def build_documentation(a, mermaid, llm_doc):
    dirs=", ".join(a.get("top_level_directories",[])) or "None detected"
    exts=", ".join(f"{k}: {v}" for k,v in sorted(a.get("extension_counts",{}).items())) or "None"
    packages=", ".join(a.get("package_files",[])) or "None detected"
    evidence=f"""## Automated Repository Analysis

- Files analyzed: **{a.get("file_count",0)}**
- Top-level directories: **{dirs}**
- File types: **{exts}**
- Package/configuration files: **{packages}**

## Architecture Visualization

```mermaid
{mermaid}
```"""
    if llm_doc:
        return "# Project Documentation\n\n"+llm_doc+"\n\n---\n\n"+evidence+"\n"
    return "# Project Documentation\n\nLLM generation was disabled.\n\n"+evidence+"\n"
