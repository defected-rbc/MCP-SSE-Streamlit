import streamlit as st
import asyncio
import traceback
from mcp import ClientSession
from mcp.client.sse import sse_client
import httpx # Required for sse_client for async HTTP requests

# --- Configuration ---
# Your deployed Cloud Run server URL (base URL for the service)
# This has been updated with the URL you provided.
CLOUD_RUN_BASE_URL = "https://ollama-gemini-server-974800203413.us-central1.run.app"
# The SSE endpoint on your server
MCP_SERVER_SSE_URL = f"{CLOUD_RUN_BASE_URL}/sse"
# The endpoint for posting messages to the MCP server
MCP_SERVER_MESSAGES_URL = f"{CLOUD_RUN_BASE_URL}/messages/"

async def call_tool(server_sse_url: str, article_url: str) -> str:
    """
    Connects to the MCP server using SSE, initializes the session,
    calls the summarize_wikipedia_article tool, and returns only the summary text.
    """
    try:
        # Corrected sse_client usage: It typically expects the base URL as the first argument.
        # The ClientSession then handles the read/write streams internally using this base URL.
        async with sse_client(server_sse_url) as streams:
            reader, writer = streams # Unpack the reader and writer streams
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                
                st.info(f"Calling tool 'summarize_wikipedia_article' for URL: {article_url}")
                raw_result = await session.call_tool("summarize_wikipedia_article", arguments={"url": article_url})
                st.success("Tool call completed. Processing result...")

                # --- Logic to Extract Plain Text from MCP Result ---
                extracted_text = ""
                
                # Case 1: Result is a dictionary with a 'content' list (common for Gemini tool output)
                if isinstance(raw_result, dict) and 'content' in raw_result and isinstance(raw_result['content'], list):
                    for item in raw_result['content']:
                        if isinstance(item, dict) and item.get('type') == 'text' and 'text' in item:
                            extracted_text += item['text']
                # Case 2: Result is an object with a 'content' list (if mcp library wraps dicts)
                elif hasattr(raw_result, 'content') and isinstance(raw_result.content, list):
                    for item in raw_result.content:
                        if hasattr(item, 'type') and item.type == 'text' and hasattr(item, 'text'):
                            extracted_text += item.text
                # Case 3: Result is a direct string (less common for complex tool outputs)
                elif isinstance(raw_result, str):
                    extracted_text = raw_result
                # Fallback: If it's an object with a 'text' attribute
                elif hasattr(raw_result, 'text'):
                    extracted_text = str(raw_result.text)
                # Last resort: Convert the whole raw result to string
                else:
                    extracted_text = str(raw_result)

                if extracted_text:
                    return extracted_text.strip()
                else:
                    return "No discernible summary text found in the tool's response."

    except Exception as e:
        error_message = f"An error occurred during tool call: {e}"
        st.exception(e) # Display full exception in Streamlit
        return f"{error_message}\n{traceback.format_exc()}"

def main():
    st.set_page_config(page_title="Wikipedia Article Summarizer (MCP Client)", page_icon="📝")
    st.title("📚 Wikipedia Article Summarizer (MCP Client)")
    st.write("This Streamlit app connects to your deployed MCP server to summarize Wikipedia articles.")

    st.markdown("---")
    st.subheader("Server Configuration")
    # Display the fixed server URL
    st.code(f"MCP Server Base URL: {CLOUD_RUN_BASE_URL}", language="text")
    st.code(f"SSE Endpoint: {MCP_SERVER_SSE_URL}", language="text")
    st.code(f"Messages Endpoint: {MCP_SERVER_MESSAGES_URL}", language="text")
    st.markdown("---")

    st.subheader("Article Input")
    article_url = st.text_input(
        "Enter Wikipedia Article URL:",
        "https://en.wikipedia.org/wiki/India", # Default URL for convenience
        placeholder="e.g., https://en.wikipedia.org/wiki/Artificial_intelligence"
    )

    if st.button("Summarize Article"):
        if article_url:
            with st.spinner("Connecting to server and summarizing article..."):
                try:
                    # Run the async function
                    summary_result = asyncio.run(call_tool(MCP_SERVER_SSE_URL, article_url))
                    
                    st.subheader("Article Summary:")
                    st.text_area("Summary", summary_result, height=400)
                except Exception as e:
                    st.error(f"Failed to get summary: {e}")
                    st.exception(e) # Show full traceback in Streamlit
        else:
            st.warning("Please enter a URL to summarize.")

if __name__ == "__main__":
    # Ensure httpx is installed for sse_client
    try:
        import httpx
    except ImportError:
        st.error("The 'httpx' library is required. Please install it: `pip install httpx`")
        st.stop()
    main()
