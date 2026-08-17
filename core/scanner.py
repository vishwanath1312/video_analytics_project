from pathlib import Path
import ast, json

IGNORED_DIRS = {".git",".github",".venv","venv","env","node_modules","__pycache__",".idea",".vscode","dist","build","coverage",".next",".cache"}
IGNORED_FILES = {".env",".env.local",".env.production",".env.development","id_rsa","id_dsa","id_ecdsa","id_ed25519"}
EXTENSIONS = {".py",".js",".jsx",".ts",".tsx",".java",".go",".rs",".cpp",".c",".h",".hpp",".cs",".php",".rb",".swift",".kt",".kts",".md",".txt",".yaml",".yml",".json",".toml",".ini",".cfg",".xml",".html",".css"}

def read_text(path):
    try:
        if path.stat().st_size > 300000: return "[FILE TOO LARGE - OMITTED]"
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return "[UNREADABLE FILE]"

def py_imports(source):
    try: tree = ast.parse(source)
    except SyntaxError: return []
    out=[]
    for n in ast.walk(tree):
        if isinstance(n, ast.Import): out += [a.name.split(".")[0] for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.module: out.append(n.module.split(".")[0])
    return sorted(set(out))

def js_imports(source):
    import re
    out=[]
    for p in [r'import\s+(?:.+?\s+from\s+)?["\']([^"\']+)["\']', r'require\(\s*["\']([^"\']+)["\']\s*\)', r'import\(\s*["\']([^"\']+)["\']\s*\)']:
        out += re.findall(p, source)
    return sorted(set(out))

def scan_repository(repo_path, max_files=500, max_context_chars=60000):
    files=[]; modules=[]; deps=[]; context=[]; used=0
    for path in sorted(repo_path.rglob("*")):
        if len(files) >= max_files or not path.is_file(): continue
        if any(x in IGNORED_DIRS for x in path.parts) or path.name in IGNORED_FILES or path.suffix.lower() not in EXTENSIONS: continue
        rel=path.relative_to(repo_path).as_posix()
        content=read_text(path)
        imports=[]
        if path.suffix.lower()==".py":
            imports=py_imports(content)
            try:
                tree=ast.parse(content)
                classes=[n.name for n in ast.walk(tree) if isinstance(n,ast.ClassDef)][:50]
                funcs=[n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))][:100]
            except SyntaxError: classes=[]; funcs=[]
            modules.append({"file":rel,"imports":imports,"classes":classes,"functions":funcs})
        elif path.suffix.lower() in {".js",".jsx",".ts",".tsx"}:
            imports=js_imports(content)
        files.append({"path":rel,"extension":path.suffix.lower(),"size":path.stat().st_size,"imports":imports})
        deps += [{"source":rel,"target":x} for x in imports]
        if used < max_context_chars:
            block=f"\n### FILE: {rel}\n```text\n{content[:10000]}\n```\n"
            context.append(block[:max_context_chars-used]); used += len(block)
    dirs=sorted({x["path"].split("/")[0] for x in files if "/" in x["path"]})
    ext={}
    for x in files: ext[x["extension"] or "[no extension]"]=ext.get(x["extension"] or "[no extension]",0)+1
    package_files=[x["path"] for x in files if Path(x["path"]).name.lower() in {"requirements.txt","pyproject.toml","package.json","pom.xml","build.gradle","cargo.toml","go.mod"}]
    ctx={"repository_summary":{"file_count":len(files),"top_level_directories":dirs,"extension_counts":ext,"package_files":package_files},"python_modules":modules[:200],"files":files[:500],"source_context":"".join(context)}
    result={"repository_path":str(repo_path),"file_count":len(files),"top_level_directories":dirs,"extension_counts":ext,"package_files":package_files,"python_modules":modules,"dependencies":deps[:1000],"files":files}
    result["llm_context"]=json.dumps(ctx,indent=2,ensure_ascii=False)
    return result
