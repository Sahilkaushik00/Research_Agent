import streamlit as st
import os
from dotenv import load_dotenv
from research_agent import AutonomousResearchAgent

# Load environment variables
load_dotenv()


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Autonomous Research Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# Custom CSS
# ============================================================

st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }

    .stTextInput > div > div > input {
        background-color: #1a1c23;
        color: #ffffff;
        border-radius: 10px;
        border: 1px solid #30363d;
    }

    .stButton > button {
        background-color: #238636;
        color: white;
        border-radius: 10px;
        width: 100%;
        font-weight: bold;
        border: none;
    }

    .stButton > button:hover {
        background-color: #2ea043;
        border: none;
    }

    .report-container {
        background-color: #161b22;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #30363d;
        margin-top: 20px;
    }

    h1, h2, h3 {
        color: #58a6ff !important;
    }

    .stMarkdown {
        color: #c9d1d9;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# API Keys
# ============================================================

# Streamlit Cloud Secrets first, environment variables second

try:
    openai_key = st.secrets.get("OPENAI_API_KEY", "")
    tavily_key = st.secrets.get("TAVILY_API_KEY", "")
except Exception:
    openai_key = ""
    tavily_key = ""

# Fallback for local development
openai_key = openai_key or os.getenv("OPENAI_API_KEY", "")
tavily_key = tavily_key or os.getenv("TAVILY_API_KEY", "")


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.image(
        "https://cdn-icons-png.flaticon.com/512/2103/2103633.png",
        width=80
    )

    st.title("Agent Settings")

    st.markdown("---")

    st.markdown("### 🔑 API Status")

    if openai_key:
        st.success("✅ OpenAI API Key configured")
    else:
        st.error("❌ OpenAI API Key missing")

    if tavily_key:
        st.success("✅ Tavily API Key configured")
    else:
        st.error("❌ Tavily API Key missing")

    st.markdown("---")

    st.markdown("### About")

    st.info(
        """
        This autonomous research agent uses:

        **🧠 OpenAI**
        - Reasoning
        - Research synthesis
        - Report generation

        **🔗 LangGraph**
        - Agent workflow orchestration

        **🔎 Tavily**
        - Web research
        - Multi-source information retrieval

        The agent researches your objective,
        synthesizes the findings, and generates
        a structured Markdown report.
        """
    )

    if st.button("Clear History"):
        st.session_state.messages = []
        st.rerun()


# ============================================================
# Main UI
# ============================================================

st.title("🧠 Autonomous Research Agent")

st.subheader("Multi-Source Intelligence Engine")


# ============================================================
# Initialize Agent
# ============================================================

if "agent" not in st.session_state:

    if openai_key and tavily_key:

        try:
            st.session_state.agent = AutonomousResearchAgent(
                api_key=openai_key,
                tavily_api_key=tavily_key
            )

        except Exception as e:
            st.error(f"Failed to initialize agent: {str(e)}")
            st.stop()

    else:

        st.warning(
            "Please configure both your OpenAI and Tavily API keys "
            "before using the research agent."
        )

        st.info(
            """
            ### Streamlit Cloud

            Add these to your app's Secrets:

            ```
            OPENAI_API_KEY = "your-openai-api-key"
            TAVILY_API_KEY = "your-tavily-api-key"
            ```

            Do not commit API keys to GitHub.
            """
        )

        st.stop()


# ============================================================
# Initialize Chat History
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# Research Input
# ============================================================

user_query = st.text_input(
    "What would you like me to research today?",
    placeholder="e.g., Future of quantum computing in 2026"
)


# ============================================================
# Run Agent
# ============================================================

if user_query:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query
        }
    )

    with st.spinner(
        "🤖 Agent is thinking and researching..."
    ):

        try:

            # Run the autonomous research agent
            report = st.session_state.agent.run(
                user_query
            )

            st.session_state.messages.append(
                {
                    "role": "agent",
                    "content": report
                }
            )

        except Exception as e:

            st.error(
                f"Error while running the agent: {str(e)}"
            )


# ============================================================
# Display Results
# ============================================================

for msg in reversed(st.session_state.messages):

    if msg["role"] == "user":

        st.markdown(
            f"**👤 You:** {msg['content']}"
        )

    else:

        st.markdown(
            '<div class="report-container">',
            unsafe_allow_html=True
        )

        st.markdown(
            "### 📋 Research Report"
        )

        st.markdown(
            msg["content"]
        )

        # Download report
        st.download_button(
            label="📥 Download Markdown Report",
            data=msg["content"],
            file_name="research_report.md",
            mime="text/markdown",
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    st.markdown("---")


# ============================================================
# Footer
# ============================================================

st.markdown(
    """
    <div style="
        text-align: center;
        color: #8b949e;
        font-size: 0.8rem;
        margin-top: 50px;
    ">
        Powered by OpenAI + LangGraph + Tavily |
        Autonomous Agent Lab v2.0
    </div>
    """,
    unsafe_allow_html=True
)

