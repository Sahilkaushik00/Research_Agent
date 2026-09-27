import os
from typing import TypedDict, List, Annotated

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
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

    def __init__(self, api_key: str = None, tavily_api_key: str = None):

        # Get API keys from arguments or environment variables
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. "
                "Set OPENAI_API_KEY as an environment variable "
                "or pass api_key when creating the agent."
            )

        # OpenAI model
        self.model = ChatOpenAI(
            model="gpt-5.6",
            api_key=self.api_key,
            temperature=0.2
        )

        # Tavily search
        if HAS_TAVILY and self.tavily_api_key:
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

        # Build LangGraph workflow
        self.workflow = self._build_workflow()

    def _build_workflow(self):

        workflow = StateGraph(AgentState)

        workflow.add_node(
            "researcher",
            self._research_node
        )

        workflow.add_node(
            "writer",
            self._writer_node
        )

        workflow.set_entry_point("researcher")

        workflow.add_edge(
            "researcher",
            "writer"
        )

        workflow.add_edge(
            "writer",
            END
        )

        return workflow.compile()

    def _research_node(self, state: AgentState):

        objective = state["objective"]

        # Perform web search
        if self.search_tool:

            try:
                search_results = self.search_tool.invoke(
                    {"query": objective}
                )

                context = (
                    "Based on these search results, "
                    "synthesize the key findings:\n"
                    f"{search_results}"
                )

            except Exception as e:

                context = (
                    f"Note: Search tool failed ({str(e)}).\n"
                    f"Synthesize findings using your internal knowledge "
                    f"for the following objective:\n{objective}"
                )

        else:

            context = (
                "No web search tool is available. "
                f"Synthesize findings using your internal knowledge "
                f"for: {objective}"
            )

        prompt = f"""
You are an Autonomous Researcher.

Your objective is:

{objective}

{context}

Analyze the available information carefully.

Provide:
- Important facts
- Key findings
- Relevant details
- Potential limitations or uncertainties

Do not invent information that is not supported by the
available search results or your knowledge.
"""

        response = self.model.invoke(
            [HumanMessage(content=prompt)]
        )

        return {
            "messages": [response]
        }

    def _writer_node(self, state: AgentState):

        objective = state["objective"]

        findings = state["messages"][-1].content

        prompt = f"""
You are a Professional Technical Writer.

Research Objective:
{objective}

Research Findings:
{findings if findings else "No specific findings were gathered."}

Create a well-structured Markdown report.

Use exactly these sections:

# Key Takeaways

# Detailed Findings

# Actionable Insights

# Conclusion

Requirements:
- Keep the report factual and clear.
- Do not invent sources or facts.
- Organize information logically.
- Use bullet points where appropriate.
- Make the report easy to read.
"""

        response = self.model.invoke(
            [HumanMessage(content=prompt)]
        )

        return {
            "report": response.content
        }

    def run(self, objective: str) -> str:

        initial_state = {
            "messages": [],
            "objective": objective,
            "report": ""
        }

        result = self.workflow.invoke(
            initial_state
        )

        return result["report"]


# Example usage
if __name__ == "__main__":

    agent = AutonomousResearchAgent()

    report = agent.run(
        "Research the current state of AI agent frameworks "
        "and compare LangGraph, CrewAI, and AutoGen."
    )

    print(report)
