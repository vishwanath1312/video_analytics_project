import re
def nid(x): return re.sub(r"[^a-zA-Z0-9_]","_",x)[:60]
def build_mermaid(a):
    lines=["flowchart LR",'    USER["User / Developer"]','    REPO["GitHub Repository"]','    USER --> REPO','    REPO --> ANALYSIS["Repository Analyzer"]','    ANALYSIS --> TREE["File / Module Structure"]','    ANALYSIS --> AST["AST / Import Analysis"]']
    for d in a.get("top_level_directories",[])[:20]: lines.append(f'    ANALYSIS --> {nid("dir_"+d)}["{d}"]')
    if a.get("python_modules"):
        lines.append('    AST --> PY["Python Modules"]')
        for m in a["python_modules"][:25]:
            p=m["file"].replace('"',"'"); lines.append(f'    PY --> {nid("py_"+p)}["{p}"]')
    important={"requirements.txt","pyproject.toml","package.json","dockerfile","docker-compose.yml","docker-compose.yaml","main.py","app.py","server.py","manage.py"}
    hits=[x["path"] for x in a["files"] if x["path"].split("/")[-1].lower() in important]
    if hits:
        lines.append('    ANALYSIS --> CONFIG["Configuration / Entry Points"]')
        for p in hits[:20]: lines.append(f'    CONFIG --> {nid("cfg_"+p)}["{p}"]')
    lines += ['    ANALYSIS --> DOC["LLM Documentation Generator"]','    DOC --> OUT["Architecture + Technical Documentation"]']
    return "\n".join(lines)
