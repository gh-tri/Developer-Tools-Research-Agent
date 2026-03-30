from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .models import ResearchState, CompanyInfo, CompanyAnalysis
from .firecrawl import FirecrawlService
from .prompts import DeveloperToolsPrompts


class Workflow:
    def __init__(self):
        self.firecrawl = FirecrawlService()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        self.prompts = DeveloperToolsPrompts()
        self.workflow = self._build_workflow()

    def _field(self, obj, name, default=None):
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)

    def _build_workflow(self):
        graph = StateGraph(ResearchState)
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)
        graph.set_entry_point("extract_tools")
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)
        return graph.compile()

    def _extract_tools_step(self, state: ResearchState) -> Dict[str, Any]:
        print(f"🔍 Finding articles about: {state.query}")

        article_query = f"{state.query} tools comparison best alternatives"
        search_results = self.firecrawl.search_with_content(article_query, num_results=3)

        all_content = ""

        # search-with-content may come back as a list-like data payload
        results = search_results if isinstance(search_results, list) else getattr(search_results, "data",
                                                                                  search_results) or []

        for result in results:
            markdown = self._field(result, "markdown", "")
            if markdown:
                all_content += markdown[:1500] + "\n\n"

        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(state.query, all_content))
        ]

        try:
            response = self.llm.invoke(messages)
            tool_names = [x.strip() for x in response.content.split("\n") if x.strip()]
            print(f"Extracted tools: {', '.join(tool_names[:5])}")
            return {"extracted_tools": tool_names}
        except Exception as e:
            print(e)
            return {"extracted_tools": []}

    def _analyze_company_content(self, company_name: str, content: str) -> CompanyAnalysis:
        structured_llm = self.llm.with_structured_output(CompanyAnalysis)

        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_analysis_user(company_name, content))
        ]

        try:
            analysis = structured_llm.invoke(messages)
            return analysis
        except Exception as e:
            print(e)
            return CompanyAnalysis(
                pricing_model="Unknown",
                is_open_source=None,
                tech_stack=[],
                description="Failed",
                api_available=None,
                language_support=[],
                integration_capabilities=[],
            )

    def _research_step(self, state: ResearchState) -> Dict[str, Any]:
        extracted_tools = getattr(state, "extracted_tools", [])

        if not extracted_tools:
            print("⚠️ No extracted tools found, falling back to direct search")
            tool_names = [state.query]
        else:
            tool_names = extracted_tools[:4]

        print(f"🔬 Researching specific tools: {', '.join(tool_names)}")

        companies = []

        for tool_name in tool_names:
            # plain search here, not search+scrape
            tool_search_results = self.firecrawl.search_web(f"{tool_name} official site", num_results=1)

            web_results = getattr(tool_search_results, "web", []) if tool_search_results else []
            if not web_results:
                continue

            result = web_results[0]
            url = self._field(result, "url", "")
            title = self._field(result, "title", tool_name)

            company = CompanyInfo(
                name=tool_name,
                description="",
                website=url,
                tech_stack=[],
                competitors=[]
            )

            scraped = self.firecrawl.scrape_company_pages(url)
            markdown = self._field(scraped, "markdown", "") if scraped else ""

            if markdown:
                analysis = self._analyze_company_content(company.name, markdown)
                company.pricing_model = analysis.pricing_model
                company.is_open_source = analysis.is_open_source
                company.tech_stack = analysis.tech_stack
                company.description = analysis.description
                company.api_available = analysis.api_available
                company.language_support = analysis.language_support
                company.integration_capabilities = analysis.integration_capabilities
            else:
                company.description = title

            companies.append(company)

        return {"companies": companies}

    def _analyze_step(self, state: ResearchState) -> Dict[str, Any]:
        print("Generating recommendations")

        company_data = ", ".join([
            company.model_dump_json() for company in state.companies
        ])

        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(content=self.prompts.recommendations_user(state.query, company_data))
        ]

        response = self.llm.invoke(messages)
        return {"analysis": response.content}

    def run(self, query: str) -> ResearchState:
        initial_state = ResearchState(query=query)
        final_state = self.workflow.invoke(initial_state)
        return ResearchState(**final_state)