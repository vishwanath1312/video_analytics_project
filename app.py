import json
from pathlib import Path

import streamlit as st

from core.repo_loader import clone_repository
from core.scanner import scan_repository
from core.architecture import build_mermaid
from core.llm import OllamaLLM
from core.documentation import build_documentation


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="GitHub AI Architect",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #777;
        margin-bottom: 25px;
    }

    .metric-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        text-align: center;
    }

    .success-box {
        padding: 15px;
        border-radius: 10px;
        background-color: rgba(0, 180, 100, 0.10);
        border: 1px solid rgba(0, 180, 100, 0.3);
    }

    .warning-box {
        padding: 15px;
        border-radius: 10px;
        background-color: rgba(255, 170, 0, 0.10);
        border: 1px solid rgba(255, 170, 0, 0.3);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🧠 GitHub AI Architect</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    LLM-Based GitHub Repository Understanding, Architecture
    Visualization and Documentation System
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "mermaid" not in st.session_state:
    st.session_state.mermaid = None

if "documentation" not in st.session_state:
    st.session_state.documentation = None

if "repo_path" not in st.session_state:
    st.session_state.repo_path = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Configuration")

    st.markdown("### GitHub Repository")

    repo_url = st.text_input(
        "Repository URL",
        placeholder="https://github.com/owner/repository",
        help=(
            "Enter a public GitHub repository URL. "
            "Example: https://github.com/AI4Bharat/IndicVoices"
        )
    )

    st.markdown("---")

    st.markdown("### 🔍 Repository Analysis")

    max_files = st.number_input(
        "Maximum files to analyze",
        min_value=10,
        max_value=5000,
        value=500,
        step=50
    )

    max_chars = st.number_input(
        "Maximum LLM context characters",
        min_value=5000,
        max_value=200000,
        value=60000,
        step=5000
    )

    st.markdown("---")

    st.markdown("### 🤖 LLM Configuration")

    use_llm = st.checkbox(
        "Use LLM",
        value=False,
        help=(
            "Disable this when using Streamlit Cloud without "
            "a cloud LLM provider. Local Ollama is not available "
            "from Streamlit Cloud."
        )
    )

    model = st.text_input(
        "Ollama Model",
        value="llama3.1:8b",
        disabled=not use_llm
    )

    ollama_host = st.text_input(
        "Ollama URL",
        value="http://localhost:11434",
        disabled=not use_llm,
        help=(
            "For local execution use http://localhost:11434. "
            "This does not work from Streamlit Cloud unless "
            "you provide a reachable Ollama server."
        )
    )

    st.markdown("---")

    analyze_button = st.button(
        "🚀 Analyze Repository",
        type="primary",
        use_container_width=True
    )

    clear_button = st.button(
        "🗑️ Clear Results",
        use_container_width=True
    )


# ============================================================
# CLEAR RESULTS
# ============================================================

if clear_button:

    st.session_state.analysis = None
    st.session_state.mermaid = None
    st.session_state.documentation = None
    st.session_state.repo_path = None

    st.rerun()


# ============================================================
# HELPER FUNCTION
# ============================================================

def save_outputs(analysis, mermaid, documentation):

    output_dir = Path("outputs")

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # JSON
    json_path = output_dir / "repository_analysis.json"

    with open(
        json_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            analysis,
            f,
            indent=2,
            ensure_ascii=False
        )

    # Mermaid
    mermaid_path = output_dir / "architecture.mmd"

    mermaid_path.write_text(
        mermaid,
        encoding="utf-8"
    )

    # Documentation
    documentation_path = (
        output_dir /
        "PROJECT_DOCUMENTATION.md"
    )

    documentation_path.write_text(
        documentation,
        encoding="utf-8"
    )

    return (
        json_path,
        mermaid_path,
        documentation_path
    )


# ============================================================
# MAIN ANALYSIS
# ============================================================

if analyze_button:

    if not repo_url.strip():

        st.error(
            "❌ Please enter a GitHub repository URL."
        )

        st.stop()


    try:

        # ----------------------------------------------------
        # STEP 1 — CLONE REPOSITORY
        # ----------------------------------------------------

        with st.status(
            "🔄 Analyzing repository...",
            expanded=True
        ) as status:

            st.write(
                "📥 Cloning GitHub repository..."
            )

            repo_path = clone_repository(
                repo_url.strip()
            )

            st.session_state.repo_path = str(
                repo_path
            )

            st.write(
                f"✅ Repository cloned successfully."
            )


            # ------------------------------------------------
            # STEP 2 — SCAN REPOSITORY
            # ------------------------------------------------

            st.write(
                "🔍 Scanning repository structure..."
            )

            analysis = scan_repository(
                repo_path,
                int(max_files),
                int(max_chars)
            )

            st.session_state.analysis = analysis

            st.write(
                "✅ Repository analysis completed."
            )


            # ------------------------------------------------
            # STEP 3 — ARCHITECTURE
            # ------------------------------------------------

            st.write(
                "🏗️ Building architecture model..."
            )

            mermaid = build_mermaid(
                analysis
            )

            st.session_state.mermaid = mermaid

            st.write(
                "✅ Architecture generated."
            )


            # ------------------------------------------------
            # STEP 4 — LLM
            # ------------------------------------------------

            llm_doc = ""

            if use_llm:

                st.write(
                    "🤖 Connecting to LLM..."
                )

                try:

                    llm = OllamaLLM(
                        model=model,
                        host=ollama_host
                    )

                    llm_doc = llm.generate(
                        analysis["llm_context"]
                    )

                    if llm_doc:

                        st.write(
                            "✅ LLM documentation generated."
                        )

                    else:

                        st.warning(
                            "⚠️ LLM returned an empty response."
                        )

                except Exception as llm_error:

                    st.warning(
                        "⚠️ LLM service is unavailable."
                    )

                    st.info(
                        """
                        The repository analysis will continue
                        without LLM-generated documentation.

                        If you are using Streamlit Cloud,
                        `localhost:11434` refers to the cloud server,
                        not your personal computer.

                        Disable **Use LLM** or configure a
                        cloud-accessible LLM provider.
                        """
                    )

                    with st.expander(
                        "Show LLM connection error"
                    ):

                        st.code(
                            str(llm_error)
                        )

                    llm_doc = ""


            # ------------------------------------------------
            # STEP 5 — DOCUMENTATION
            # ------------------------------------------------

            st.write(
                "📝 Generating project documentation..."
            )

            documentation = build_documentation(
                analysis,
                mermaid,
                llm_doc
            )

            st.session_state.documentation = (
                documentation
            )


            # ------------------------------------------------
            # STEP 6 — SAVE OUTPUTS
            # ------------------------------------------------

            save_outputs(
                analysis,
                mermaid,
                documentation
            )

            status.update(
                label="✅ Repository analysis completed",
                state="complete"
            )


    except Exception as error:

        st.error(
            "❌ Repository analysis failed."
        )

        with st.expander(
            "Show technical error"
        ):

            st.exception(error)

        st.stop()


# ============================================================
# DISPLAY RESULTS
# ============================================================

if st.session_state.analysis:

    analysis = st.session_state.analysis
    mermaid = st.session_state.mermaid
    documentation = st.session_state.documentation


    # ========================================================
    # METRICS
    # ========================================================

    st.markdown("## 📊 Repository Overview")

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Files Analyzed",
            analysis.get(
                "file_count",
                0
            )
        )


    with col2:

        st.metric(
            "Directories",
            len(
                analysis.get(
                    "top_level_directories",
                    []
                )
            )
        )


    with col3:

        st.metric(
            "Dependencies",
            len(
                analysis.get(
                    "dependencies",
                    []
                )
            )
        )


    with col4:

        st.metric(
            "Python Modules",
            len(
                analysis.get(
                    "python_modules",
                    []
                )
            )
        )


    st.markdown("---")


    # ========================================================
    # TABS
    # ========================================================

    (
        tab_architecture,
        tab_documentation,
        tab_structure,
        tab_dependencies,
        tab_python,
        tab_raw
    ) = st.tabs(
        [
            "🏗️ Architecture",
            "📚 Documentation",
            "📁 Structure",
            "🔗 Dependencies",
            "🐍 Python Analysis",
            "🔎 Raw Analysis"
        ]
    )


    # ========================================================
    # ARCHITECTURE TAB
    # ========================================================

    with tab_architecture:

        st.subheader(
            "System Architecture"
        )

        st.markdown(
            """
            The generated architecture represents the
            repository structure and major analysis components.
            """
        )

        if mermaid:

            st.code(
                mermaid,
                language="text"
            )

            st.download_button(
                label="⬇️ Download Mermaid Diagram",
                data=mermaid,
                file_name="architecture.mmd",
                mime="text/plain"
            )

        else:

            st.warning(
                "No architecture diagram was generated."
            )


    # ========================================================
    # DOCUMENTATION TAB
    # ========================================================

    with tab_documentation:

        st.subheader(
            "📚 Project Documentation"
        )

        if documentation:

            st.markdown(
                documentation
            )

            st.download_button(
                label="⬇️ Download Documentation",
                data=documentation,
                file_name="PROJECT_DOCUMENTATION.md",
                mime="text/markdown"
            )

        else:

            st.warning(
                "Documentation is not available."
            )


    # ========================================================
    # STRUCTURE TAB
    # ========================================================

    with tab_structure:

        st.subheader(
            "📁 Repository Structure"
        )

        directories = analysis.get(
            "top_level_directories",
            []
        )

        if directories:

            for directory in directories:

                st.markdown(
                    f"📂 `{directory}`"
                )

        else:

            st.info(
                "No top-level directories detected."
            )


        st.markdown(
            "### File Types"
        )

        extension_counts = analysis.get(
            "extension_counts",
            {}
        )

        if extension_counts:

            for extension, count in sorted(
                extension_counts.items(),
                key=lambda x: x[1],
                reverse=True
            ):

                st.write(
                    f"`{extension}` — {count} files"
                )


    # ========================================================
    # DEPENDENCY TAB
    # ========================================================

    with tab_dependencies:

        st.subheader(
            "🔗 Dependencies and Imports"
        )

        dependencies = analysis.get(
            "dependencies",
            []
        )

        if dependencies:

            for dependency in dependencies[:500]:

                source = dependency.get(
                    "source",
                    ""
                )

                target = dependency.get(
                    "target",
                    ""
                )

                st.write(
                    f"`{source}` → `{target}`"
                )

        else:

            st.info(
                "No dependencies were detected."
            )


        package_files = analysis.get(
            "package_files",
            []
        )

        st.markdown(
            "### Package / Configuration Files"
        )

        if package_files:

            for file in package_files:

                st.write(
                    f"📦 `{file}`"
                )

        else:

            st.info(
                "No standard package files detected."
            )


    # ========================================================
    # PYTHON ANALYSIS TAB
    # ========================================================

    with tab_python:

        st.subheader(
            "🐍 Python Module Analysis"
        )

        python_modules = analysis.get(
            "python_modules",
            []
        )

        if python_modules:

            for module in python_modules:

                with st.expander(
                    module.get(
                        "file",
                        "Unknown"
                    )
                ):

                    classes = module.get(
                        "classes",
                        []
                    )

                    functions = module.get(
                        "functions",
                        []
                    )

                    imports = module.get(
                        "imports",
                        []
                    )


                    st.markdown(
                        "#### Classes"
                    )

                    if classes:

                        for cls in classes:

                            st.write(
                                f"🔹 `{cls}`"
                            )

                    else:

                        st.write(
                            "No classes detected."
                        )


                    st.markdown(
                        "#### Functions"
                    )

                    if functions:

                        for function in functions:

                            st.write(
                                f"🔹 `{function}()`"
                            )

                    else:

                        st.write(
                            "No functions detected."
                        )


                    st.markdown(
                        "#### Imports"
                    )

                    if imports:

                        st.write(
                            ", ".join(
                                f"`{x}`"
                                for x in imports
                            )
                        )

                    else:

                        st.write(
                            "No imports detected."
                        )

        else:

            st.info(
                "No Python modules were detected."
            )


    # ========================================================
    # RAW ANALYSIS TAB
    # ========================================================

    with tab_raw:

        st.subheader(
            "🔎 Complete Analysis Data"
        )

        st.json(
            analysis
        )


    # ========================================================
    # DOWNLOAD JSON
    # ========================================================

    st.markdown("---")

    analysis_json = json.dumps(
        analysis,
        indent=2,
        ensure_ascii=False
    )

    st.download_button(
        label="⬇️ Download Repository Analysis JSON",
        data=analysis_json,
        file_name="repository_analysis.json",
        mime="application/json"
    )


    # ========================================================
    # REPOSITORY LOCATION
    # ========================================================

    if st.session_state.repo_path:

        st.markdown("---")

        st.caption(
            "Repository working directory:"
        )

        st.code(
            st.session_state.repo_path
        )


# ============================================================
# INITIAL SCREEN
# ============================================================

else:

    st.info(
        """
        👈 Enter a public GitHub repository URL in the sidebar
        and click **Analyze Repository**.
        """
    )


    st.markdown(
        "## 🔬 How the System Works"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.markdown(
            """
            ### 1️⃣ Repository Understanding

            • Clone GitHub repository

            • Analyze file structure

            • Detect programming languages

            • Analyze Python AST

            • Extract imports

            • Detect dependencies
            """
        )


    with col2:

        st.markdown(
            """
            ### 2️⃣ Architecture Analysis

            • Module identification

            • Dependency relationships

            • Entry-point detection

            • Architecture generation

            • Mermaid visualization
            """
        )


    with col3:

        st.markdown(
            """
            ### 3️⃣ Documentation

            • Project overview

            • Technology stack

            • Module descriptions

            • Data flow

            • Deployment information

            • Research opportunities
            """
        )


    st.markdown("---")

    st.markdown(
        """
        ### ⚠️ Streamlit Cloud + Ollama

        If this application is deployed on Streamlit Cloud,
        do **not** expect:

        `http://localhost:11434`

        to connect to Ollama running on your personal computer.

        For cloud deployment, use a cloud LLM provider or disable
        **Use LLM**. For local deployment, Ollama can be used.
        """
    )
