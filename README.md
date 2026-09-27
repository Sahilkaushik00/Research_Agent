# Autonomous Research Agent(https://researchagent-jp8bzucvdqyorqqpoubhv9.streamlit.app/)

A high-fidelity autonomous AI agent built with **Streamlit**, **LangGraph**, and **Gemini 1.5 Flash**. 

## Features

- **Autonomous Reasoning**: Uses LangGraph state machines to manage research and writing phases.
- **Modern UI**: Dark-themed, responsive dashboard built with Streamlit.
- **Markdown Export**: Generate and download structured research reports instantly.
- **Gemini Powered**: Leverages Google's latest models for high-quality synthesis.

## Quick Start (Local)

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd <repo-name>
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables**:
   Create a `.env` file or export your key:
   ```bash
   export GEMINI_API_KEY="your_api_key"
   TAVILY_API_KEY="your_api_key"
   ```

4. **Run the app**:
   ```bash
   streamlit run app.py
   ```


## Project Structure

- `app.py`: The Streamlit frontend and UI logic.
- `research_agent.py`: Core agent logic using LangGraph and LangChain.
- `requirements.txt`: Python dependencies.
- `.streamlit/config.toml`: Custom theme and server configuration.
