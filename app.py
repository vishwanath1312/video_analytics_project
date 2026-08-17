import json
from pathlib import Path
import streamlit as st
from core.repo_loader import clone_repository
from core.scanner import scan_repository
from core.architecture import build_mermaid
from core.llm import OllamaLLM
from core.documentation import build_documentation

st.set_page_config(page_title="GitHub AI Architect", page_icon="🧠", layout="wide")
st.title("🧠 LLM-Based GitHub Repository Understanding & Architecture System")
st.caption("Analyze a GitHub repository, visualize its architecture, and generate technical documentation.")

with st.sidebar:
    repo_url = st.text_input("GitHub repository URL", placeholder="https://github.com/owner/repository")
    model = st.text_input("Ollama model", value="llama3.1:8b")
    use_llm = st.checkbox("Use LLM", value=True)
    max_files = st.number_input("Maximum files", 10, 5000, 500)
    max_chars = st.number_input("Maximum context characters", 5000, 200000, 60000)
    analyze = st.button("Analyze Repository", type="primary", use_container_width=True)

if analyze:
    if not repo_url.strip():
        st.error("Enter a GitHub repository URL.")
        st.stop()
    try:
        with st.status("Analyzing repository...", expanded=True) as status:
            st.write("Cloning repository...")
            repo_path = clone_repository(repo_url.strip())
            st.write("Scanning files and source code...")
            analysis = scan_repository(repo_path, int(max_files), int(max_chars))
            st.write("Building architecture...")
            mermaid = build_mermaid(analysis)
            llm_doc = ""
            if use_llm:
                st.write("Generating LLM documentation...")
                llm_doc = OllamaLLM(model=model).generate(analysis["llm_context"])
            documentation = build_documentation(analysis, mermaid, llm_doc)

            out = Path("outputs")
            out.mkdir(exist_ok=True)
            (out / "architecture.mmd").write_text(mermaid, encoding="utf-8")
            (out / "repository_analysis.json").write_text(json.dumps(analysis, indent=2), encoding="utf-8")
            (out / "PROJECT_DOCUMENTATION.md").write_text(documentation, encoding="utf-8")
            status.update(label="Analysis completed", state="complete")

        tab1, tab2, tab3 = st.tabs(["Architecture", "Documentation", "Analysis"])
        with tab1:
            st.code(mermaid, language="mermaid")
        with tab2:
            st.markdown(documentation)
            st.download_button("Download Markdown", documentation, "PROJECT_DOCUMENTATION.md", "text/markdown")
        with tab3:
            st.json(analysis)
    except Exception as exc:
        st.exception(exc)
