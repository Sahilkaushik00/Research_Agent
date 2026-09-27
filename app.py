import streamlit as st
import os
from dotenv import load_dotenv
from research_agent import AutonomousResearchAgent

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Autonomous Research Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a modern look
st.markdown("""
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
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.title("Agent Settings")
    
    gemini_key = st.text_input("Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))
    tavily_key = st.text_input("Tavily API Key", type="password", value=os.getenv("TAVILY_API_KEY", ""))
    
    st.markdown("---")
    st.markdown("### About")
    st.info("""
        This autonomous agent uses LangGraph and Gemini 1.5 Flash to:
        - Reason about research goals
        - Search multiple data sources using Tavily
        - Synthesize information
        - Generate structured reports
    """)
    
    if st.button("Clear History"):
        st.session_state.messages = []
        st.rerun()

# Main UI
st.title("🧠 Autonomous Research Agent")
st.subheader("Multi-Source Intelligence Engine")

if "agent" not in st.session_state:
    if gemini_key and tavily_key:
        st.session_state.agent = AutonomousResearchAgent(gemini_key, tavily_key)
    else:
        st.warning("Please enter both Gemini and Tavily API Keys in the sidebar to start.")
        st.stop()

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat input
user_query = st.text_input("What would you like me to research today?", placeholder="e.g., Future of quantum computing in 2025")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.spinner("🤖 Agent is thinking and researching..."):
        try:
            # Run the agent
            report = st.session_state.agent.run(user_query)
            st.session_state.messages.append({"role": "agent", "content": report})
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Display results
for msg in reversed(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(f"**👤 You:** {msg['content']}")
    else:
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.markdown(f"### 📋 Research Report")
        st.markdown(msg["content"])
        
        # Download button
        st.download_button(
            label="📥 Download Markdown Report",
            data=msg["content"],
            file_name=f"research_report.md",
            mime="text/markdown",
        )
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

# Footer
st.markdown(
    """
    <div style="text-align: center; color: #8b949e; font-size: 0.8rem; margin-top: 50px;">
        Powered by Gemini 1.5 Flash & LangGraph | Autonomous Agent Lab v2.0
    </div>
    """,
    unsafe_allow_html=True
)
