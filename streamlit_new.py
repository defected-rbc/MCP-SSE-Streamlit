import streamlit as st
import asyncio
import traceback
from mcp import ClientSession
from mcp.client.sse import sse_client

async def call_tool(server_url: str, article_url: str) -> str:
    """
    Connects to the MCP server using SSE, initializes the session,
    calls the summarize_wikipedia_article tool, and returns only the summary text.
    """
    try:
        async with sse_client(server_url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                # The 'result' here will be the structured object from MCP
                raw_result = await session.call_tool("summarize_wikipedia_article", arguments={"url": article_url})
                
                # --- NEW LOGIC TO EXTRACT PLAIN TEXT ---
                # Check if the result is a dict and has 'content' (typical MCP structure for text)
                if isinstance(raw_result, dict) and 'content' in raw_result and isinstance(raw_result['content'], list):
                    # Iterate through content parts to find the text
                    extracted_text = ""
                    for item in raw_result['content']:
                        if isinstance(item, dict) and item.get('type') == 'text' and 'text' in item:
                            extracted_text += item['text']
                    if extracted_text:
                        return extracted_text.strip()
                # If it's a direct string (unlikely but possible), return it
                elif isinstance(raw_result, str):
                    return raw_result.strip()
                # If it's a wrapper object like what was shown in the error, try to access its .text or .content directly
                # This part is more speculative and depends on the exact 'mcp' library object structure
                elif hasattr(raw_result, 'content') and isinstance(raw_result.content, list):
                     extracted_text = ""
                     for item in raw_result.content:
                         if hasattr(item, 'type') and item.type == 'text' and hasattr(item, 'text'):
                             extracted_text += item.text
                     if extracted_text:
                         return extracted_text.strip()
                elif hasattr(raw_result, 'text'): # Fallback for simpler objects
                    return str(raw_result.text).strip()
                
                # If none of the above, return the string representation of the raw result
                return str(raw_result).strip()

    except Exception as e:
        return f"Error: {e}\n{traceback.format_exc()}"

def main():
    st.title("Streamlit as an MCP Host")
    st.write("Enter the MCP Server SSE URL and a Wikipedia Article URL to fetch and summarize the article.")

    server_url = st.text_input("MCP Server URL", "http://localhost:8000/sse")
    article_url = st.text_input("Wikipedia Article URL", "https://en.wikipedia.org/wiki/India")

    if st.button("Fetch and Summarize Article"):
        st.info("Fetching and summarizing article...")
        try:
            result = asyncio.run(call_tool(server_url, article_url))
            st.subheader("Article Summary")
            st.text_area("Summary", result, height=400)
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()