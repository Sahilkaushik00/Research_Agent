import os
from typing import TypedDict, List, Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

# Import search tool with safety check
try:
    from langchain_tavily import TavilySearch as TavilySearchResults
    HAS_TAVILY = True
except ImportError:
    try:
        from langchain_community.tools.tavily_search import TavilySearchResults
        HAS_TAVILY = True
    except ImportError:
        HAS_TAVILY = False

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    objective: str
    report: str

class AutonomousResearchAgent:
    def __init__(self, api_key: str, tavily_api_key: str = None):
        self.api_key = api_key
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        
        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.2
        )
        
        if HAS_TAVILY and self.tavily_api_key:
            # Handle both old and new parameter names for the API key
            try:
                self.search_tool = TavilySearchResults(
                    tavily_api_key=self.tavily_api_key,
                    max_results=5
                )
            except TypeError:
                self.search_tool = TavilySearchResults(
                    api_key=self.tavily_api_key,
                    max_results=5
                )
        else:
            self.search_tool = None
        
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("researcher", self._research_node)
        workflow.add_node("writer", self._writer_node)
        
        workflow.set_entry_point("researcher")
        workflow.add_edge("researcher", "writer")
        workflow.add_edge("writer", END)
        
        return workflow.compile()

    def _research_node(self, state: AgentState):
        objective = state["objective"]
        
        if self.search_tool:
            try:
                search_results = self.search_tool.invoke({"query": objective})
                context = f"Based on these search results, synthesize the key findings:\n{search_results}"
            except Exception as e:
                context = f"Note: Search tool failed ({str(e)}). Synthesize findings based on internal knowledge for: {objective}"
        else:
            context = f"Synthesize findings based on internal knowledge for: {objective}"
        
        prompt = f"""
        You are an Autonomous Researcher. 
        Objective: {objective}
        
        {context}
        """
        # Using HumanMessage ensures compatibility with Gemini API which requires at least one content message
        response = self.model.invoke([HumanMessage(content=prompt)])
        return {"messages": [response]}

    def _writer_node(self, state: AgentState):
        objective = state["objective"]
        findings = state["messages"][-1].content
        
        prompt = f"""
        You are a Professional Technical Writer.
        Objective: {objective}
        Findings: {findings if findings else "No specific findings were gathered. Provide a general overview."}
        
        Create a well-structured Markdown report with the following sections:
        1. Key Takeaways
        2. Detailed Findings
        3. Actionable Insights
        4. Conclusion
        
        Ensure the formatting is clean and professional.
        """
        # Using HumanMessage ensures compatibility with Gemini API which requires at least one content message
        response = self.model.invoke([HumanMessage(content=prompt)])
        return {"report": response.content}

    def run(self, objective: str) -> str:
        initial_state = {
            "messages": [],
            "objective": objective,
            "report": ""
        }
        result = self.workflow.invoke(initial_state)
        return result["report"]
