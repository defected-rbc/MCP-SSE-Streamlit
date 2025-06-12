-----

# Wikipedia Article Summarizer

This project provides a web-based tool for summarizing Wikipedia articles using the Google Gemini API (or optionally, an Ollama model). It consists of a backend server (built with Starlette and MCP) that handles the summarization logic and a frontend Streamlit application for user interaction.

-----

## Features

  * **Article Fetching:** Fetches content from any provided Wikipedia article URL.
  * **Content Extraction:** Parses the main content of the Wikipedia page.
  * **Markdown Conversion:** Converts the extracted HTML content to a cleaner Markdown format.
  * **AI Summarization:** Utilizes the Google Gemini API to generate concise summaries of the article text.
  * **Server-Sent Events (SSE):** The backend communicates with the frontend using SSE for real-time updates.
  * **Streamlit Frontend:** A simple and intuitive web interface for inputting URLs and viewing summaries.

-----

## Project Structure

  * `ollama_server.py`: The backend server that exposes the `summarize_wikipedia_article` tool. This is where the core logic for fetching, parsing, and summarizing resides.
  * `streamlit_new.py`: The Streamlit frontend application that provides the user interface and interacts with the `ollama_server.py` via an MCP client.
  * `.env`: (Recommended) A file to store your sensitive API keys and other environment-specific variables. **This file should NOT be committed to Git.**
  * `requirements.txt`: Lists all Python dependencies required for the project.
  * `.gitignore`: Specifies files and directories that Git should ignore (like virtual environments and `.env` files).

-----

## Setup and Installation

Follow these steps to get the project running on your local machine.

### 1\. Prerequisites

  * **Python 3.8+**: Make sure Python is installed.
  * **Google Gemini API Key**:
      * Go to [Google AI Studio](https://aistudio.google.com/).
      * Sign in with your Google account.
      * Generate a new API key. **Keep this key secure\!**

### 2\. Clone the Repository

First, clone this repository to your local machine:

```bash
git clone <repository_url>
cd <your-project-directory-name> # e.g., cd SSE
```

### 3\. Create and Activate a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
# Create a virtual environment (e.g., named .venv)
python -m venv .venv

# Activate the virtual environment:
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
.\.venv\Scripts\activate.bat

# On macOS/Linux (Bash/Zsh):
source ./.venv/bin/activate
```

### 4\. Install Dependencies

With your virtual environment activated, install all required Python packages:

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt` file yet, you can generate one after installing `google-generativeai`, `requests`, `beautifulsoup4`, `html2text`, `uvicorn`, `starlette`, and `mcp` (ensure `mcp` is correctly installed, possibly via a custom install or pip if available):

```bash
pip install google-generativeai requests beautifulsoup4 html2text uvicorn starlette python-dotenv
# If 'mcp' is a custom library, ensure its installation steps are followed.
# If it's a pip-installable package, add it to the above line: pip install mcp
```

Then generate `requirements.txt`:

```bash
pip freeze > requirements.txt
```

### 5\. Configure Your Gemini API Key

**This is a crucial security step.** Do NOT hardcode your API key in the code or commit it to Git.

Create a file named **`.env`** in the root directory of your project (the same directory as `ollama_server.py`).

Add your Gemini API key to this file in the following format:

```
GOOGLE_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY_HERE"
```

Replace `YOUR_ACTUAL_GEMINI_API_KEY_HERE` with the API key you obtained from Google AI Studio.

**Important:** Make sure your `.gitignore` file contains the line `.env` to prevent this file from being pushed to your remote repository.

### 6\. Start the Backend Server

Open your terminal, activate your virtual environment, and navigate to your project directory. Then, run the backend server:

```bash
python ollama_server.py
# Or, if you're using `uv` for running:
uv run ollama_server.py
```

The server should start on `http://localhost:8000`. Keep this terminal window open.

### 7\. Start the Streamlit Frontend

Open a **new terminal window**, activate your virtual environment, and navigate to your project directory. Then, run the Streamlit application:

```bash
streamlit run streamlit_new.py
```

This will open the Streamlit application in your web browser (usually at `http://localhost:8501`).

-----

## Usage

1.  **Backend Server:** Ensure `ollama_server.py` is running in one terminal.
2.  **Streamlit App:** Access the Streamlit application in your web browser (e.g., `http://localhost:8501`).
3.  **MCP Server URL:** The default value for the "MCP Server URL" input is `http://localhost:8000/sse`, which should match your running backend server.
4.  **Wikipedia Article URL:** Enter the full URL of a Wikipedia article you want to summarize (e.g., `https://en.wikipedia.org/wiki/Artificial_intelligence`).
5.  **Summarize:** Click the "Fetch and Summarize Article" button. The summary generated by the Gemini model will appear in the text area below.

-----

## Error Handling

  * **`ModuleNotFoundError`**: Ensure you have activated your virtual environment and installed all dependencies from `requirements.txt` using `pip install -r requirements.txt`.
  * **`GOOGLE_API_KEY environment variable not set`**: Double-check that you have created the `.env` file correctly with `GOOGLE_API_KEY="YOUR_KEY"` and that you've installed `python-dotenv` and added `load_dotenv()` at the top of `ollama_server.py`.
  * **`Could not find main content on Wikipedia URL`**: This typically means the HTML structure of the Wikipedia page changed, or the URL provided isn't a standard Wikipedia article page.
  * **Gemini API Errors**: Check your API key, ensure you have sufficient quota, and verify your network connection.
  * **Unexpected output in Streamlit**: If the summary output in Streamlit contains `meta=... content=[TextContent(...)]`, it means the client is receiving the structured response. The provided `streamlit_new.py` has logic to extract just the text.

-----

## Deployment

For deploying this application to a production environment, consider the following:

1.  **Cloud Provider:** Use a Virtual Machine (VM) from providers like AWS EC2, Google Cloud Compute Engine, Azure, DigitalOcean, or Linode.
2.  **VM Sizing:** Choose a VM with adequate RAM and potentially a GPU if you were to use larger, more demanding local models. For Gemini API, network latency and general VM uptime are more critical than raw processing power on the VM itself.
3.  **Environment Variables:** Set your `GOOGLE_API_KEY` directly as an environment variable on your production server.
4.  **Process Management:** Use tools like `systemd` (Linux) or `pm2` (Node.js ecosystem, but can manage Python apps) to ensure your `ollama_server.py` and `streamlit_new.py` applications run continuously in the background and restart if they crash.
5.  **Reverse Proxy (Recommended):** For a production setup, place a web server like Nginx or Caddy in front of your Streamlit application to handle SSL/TLS encryption (HTTPS), custom domain names, and potentially serve static assets.
6.  **Docker (Highly Recommended):** Containerize your applications using Docker and Docker Compose. This provides a reproducible, portable, and isolated environment for your services. You would have separate containers for your `ollama_server` and `streamlit_app`.

-----

## Contributing

Feel free to fork this repository, open issues, and submit pull requests.

-----
