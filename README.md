# LLM-Based GitHub Repository Understanding, Architecture Visualization and Documentation System

A local-first system that accepts a GitHub repository URL, clones it, analyzes repository structure/source code, extracts dependencies, generates a Mermaid architecture diagram, and uses a local Ollama LLM to create technical documentation.

## Features
- GitHub repository cloning
- File tree and technology-stack analysis
- Python AST analysis
- JavaScript/TypeScript import analysis
- Dependency/module graph extraction
- Secret-file exclusion
- Mermaid architecture generation
- LLM-generated project overview, architecture, module descriptions, data flow, deployment guidance and research opportunities
- Streamlit UI
- Downloadable Markdown and JSON
- Local Ollama by default

## Windows setup

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

Install Ollama and a model:

```powershell
ollama pull llama3.1:8b
```

Run:

```powershell
streamlit run app.py
```

The system can also run without an LLM by unchecking **Use LLM**.

Do not analyze repositories containing confidential source code without authorization.
