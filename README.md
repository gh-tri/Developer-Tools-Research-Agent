# 🔍 Developer Tools Research Agent

An LLM-powered research agent that helps developers **discover, compare, and evaluate software tools** from natural-language queries — powered by LangGraph, OpenAI, and Firecrawl.

---

## What It Does

Instead of returning a generic chat response, the agent runs a structured research workflow:

1. **Search the web** for relevant articles and comparison pages
2. **Identify candidate tools** mentioned in those results
3. **Visit official websites** for each shortlisted tool
4. **Extract structured fields** including:
   - Pricing model
   - Open-source status
   - Tech stack
   - API availability
   - Language support
   - Integrations
   - Short developer-focused description
5. **Generate a concise recommendation** highlighting the best option and why

This makes it useful as a **developer research assistant**, a **tool comparison helper**, or a starting point for a larger agentic recommendation system.

---

## Two Implementations

### 1. `simple-agent/` — MCP-based Prototype

- Uses **Firecrawl MCP** as an external tool server
- Loads MCP tools dynamically into LangChain/LangGraph
- Uses a **prebuilt ReAct agent** to decide when to call tools
- Best for learning **tool calling** and **MCP integration**
```
User Query
   ↓
ChatOpenAI
   ↓
ReAct Agent (LangGraph prebuilt)
   ↓
MCP Tool Calls via Firecrawl MCP
   ↓
Answer
```

---

### 2. `advanced-agent/` — Structured LangGraph Workflow

- Uses **LangGraph `StateGraph`** for explicit step control
- Separates the process into clear nodes: `extract_tools → research → analyze`
- Uses **Pydantic models** for structured output
- Easier to extend with ranking, citations, memory, retries, or a frontend
```
User Query
   ↓
[extract_tools]
   ↓
[research]
   ↓
[analyze]
   ↓
Final Recommendation
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Workflow Orchestration | LangGraph |
| LLM Integration | LangChain |
| Model | OpenAI GPT-4o-mini |
| Web Search & Scraping | Firecrawl |
| Structured Output | Pydantic |
| Environment Management | python-dotenv |
| Dependency Management | uv |

---

## Repository Structure
```
Developer-Tools-Research-Agent/
├── advanced-agent/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── firecrawl.py      # Firecrawl wrapper for search and scraping
│   │   ├── models.py         # Pydantic state and output schemas
│   │   ├── prompts.py        # Prompt templates for extraction/analysis/recommendation
│   │   └── workflow.py       # LangGraph workflow definition
│   ├── main.py               # CLI entry point for advanced workflow
│   ├── pyproject.toml
│   └── uv.lock
│
├── simple-agent/
│   ├── main.py               # CLI entry point for MCP-based prototype
│   ├── pyproject.toml
│   └── uv.lock
│
├── .gitignore
└── README.md
```

## Example Query
```
> What are the best vector databases for a Python-based RAG application?
```

🔍 Finding articles about: What are the best vector databases for a Python-based RAG application?
Extracted tools: Pinecone, Weaviate, Milvus, Faiss, Chroma
🔬 Researching specific tools: Pinecone, Weaviate, Milvus, Faiss
Generating recommendations

1. 🏢 Pinecone
   🌐 Website: https://www.pinecone.io/
   💰 Pricing: Unknown
   📖 Open Source: False
   🛠️  Tech Stack: Vector Database, Serverless Architecture, Hybrid Search, Embeddings
   💻 Language Support: Python, JavaScript
   🔌 API: ✅ Available
   🔗 Integrations: AWS, GCP, Azure
   📝 Description: Pinecone is a purpose-built vector database designed for scalable and efficient AI applications, enabling developers to implement advanced search and recommendation systems.

2. 🏢 Weaviate
   🌐 Website: https://weaviate.io/
   💰 Pricing: Freemium
   📖 Open Source: False
   🛠️  Tech Stack: Python, Go, TypeScript, JavaScript, GraphQL
   💻 Language Support: Python, Go, TypeScript, JavaScript
   🔌 API: ✅ Available
   🔗 Integrations: ML models, embedding services
   📝 Description: Weaviate is an AI-powered search and retrieval platform that enables developers to build applications with advanced search capabilities across unstructured data.

3. 🏢 Milvus
   🌐 Website: https://milvus.io/
   💰 Pricing: Freemium
   📖 Open Source: True
   🛠️  Tech Stack: Python, Docker, Helm
   💻 Language Support: Python
   🔌 API: ✅ Available
   🔗 Integrations: Docker, Zilliz Cloud
   📝 Description: Milvus is an open-source vector database designed for high-performance searches and scalability in GenAI applications.

4. 🏢 Faiss
   🌐 Website: https://faiss.ai/index.html
   💰 Pricing: Free
   📖 Open Source: True
   🛠️  Tech Stack: C++, Python, GPU
   💻 Language Support: Python
   🔌 API: ✅ Available
   🔗 Integrations: GitHub, Anaconda
   📝 Description: Faiss is a library for efficient similarity search and clustering of dense vectors, enabling developers to perform high-performance vector searches.

For a Python-based RAG application, **Milvus** is the best choice due to its open-source nature and high-performance capabilities for scalable searches. It offers a freemium pricing model, making it cost-effective for various project sizes. Its main technical advantage is its ability to handle large-scale vector searches efficiently, which is crucial for AI applications.
