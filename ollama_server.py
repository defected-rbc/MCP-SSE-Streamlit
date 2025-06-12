import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from html2text import html2text

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from mcp.server.sse import SseServerTransport

# Import Google Generative AI client library
import google.generativeai as genai
import os # To access environment variables

# --- IMPORTANT: Configure your Gemini API Key ---
# It's recommended to store your API key as an environment variable
# For local testing, you can uncomment and set it directly,
# but NEVER commit your API key to version control.
# os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY"
# ------------------------------------------------

# Configure the genai library with your API key
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    print("Please set the GOOGLE_API_KEY environment variable or uncomment the line above to set it directly (for testing only).")
    exit(1) # Exit if API key is not found

# Initialize the Gemini model
# You can choose a different model if needed, e.g., 'gemini-pro', 'gemini-1.5-pro-latest'
GEMINI_MODEL = genai.GenerativeModel('gemini-2.0-flash')

# Create an MCP server instance with the identifier "wiki-summary-gemini"
mcp = FastMCP("wiki-summary-gemini")

@mcp.tool()
def summarize_wikipedia_article(url: str) -> str:
    """
    Fetch a Wikipedia article at the provided URL, parse its main content,
    convert it to Markdown, and generate a summary using the Gemini model.

    Usage:
        summarize_wikipedia_article("https://en.wikipedia.org/wiki/Python_(programming_language)")
    """
    try:
        # Validate input
        if not url.startswith("http"):
            raise ValueError("URL must start with http or https.")

        # Fetch the article
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            raise McpError(
                ErrorData(
                    INTERNAL_ERROR,
                    f"Failed to retrieve the article. HTTP status code: {response.status_code}"
                )
            )

        # Parse the main content of the article
        soup = BeautifulSoup(response.text, "html.parser")
        content_div = soup.find("div", {"id": "mw-content-text"})
        if not content_div:
            raise McpError(
                ErrorData(
                    INVALID_PARAMS,
                    "Could not find the main content on the provided Wikipedia URL."
                )
            )

        # Convert the content to Markdown
        markdown_text = html2text(str(content_div))

        # Create the summarization prompt for Gemini
        # It's good practice to make prompts clear for LLMs
        prompt = f"Please summarize the following Wikipedia article text concisely and accurately. Focus on the main points and key information:\n\nArticle Text:\n{markdown_text}\n\nSummary:"

        # Call the Gemini model to generate a summary
        # The `generate_content` method is used for text generation
        # `stream=True` is good for real-time output but for a single summary, `stream=False` is fine too.
        # Here we use the non-streaming approach for simplicity.
        gemini_response = GEMINI_MODEL.generate_content(prompt)
        
        # Access the generated text
        # Check if there are parts and if the text attribute exists
        if gemini_response.parts and hasattr(gemini_response.parts[0], 'text'):
            summary = gemini_response.parts[0].text.strip()
        else:
            # Handle cases where the response might not contain text directly
            # This can happen if the model refuses or if there's an error
            print(f"Gemini response structure unexpected: {gemini_response}")
            raise McpError(ErrorData(INTERNAL_ERROR, "Gemini model did not return a valid text summary."))

        return summary

    except ValueError as e:
        raise McpError(ErrorData(INVALID_PARAMS, str(e))) from e
    except RequestException as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Request error: {str(e)}")) from e
    except genai.APIError as e: # Catch specific Gemini API errors
        raise McpError(ErrorData(INTERNAL_ERROR, f"Gemini API error: {str(e)}")) from e
    except Exception as e:
        raise McpError(ErrorData(INTERNAL_ERROR, f"Unexpected error: {str(e)}")) from e

# Set up the SSE transport for MCP communication.
sse = SseServerTransport("/messages/")

async def handle_sse(request: Request) -> None:
    _server = mcp._mcp_server
    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send,
    ) as (reader, writer):
        await _server.run(reader, writer, _server.create_initialization_options())

# Create the Starlette app with two endpoints:
app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)