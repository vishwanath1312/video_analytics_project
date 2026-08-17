from pathlib import Path
import hashlib, re, shutil, tempfile
from urllib.parse import urlparse
from git import Repo

def validate_github_url(url: str) -> bool:
    p = urlparse(url)
    return p.scheme in {"https", "http"} and p.netloc.lower() in {"github.com", "www.github.com"} and bool(re.match(r"^/[^/]+/[^/]+/?$", p.path))

def clone_repository(url: str) -> Path:
    if not validate_github_url(url):
        raise ValueError("Only standard GitHub repository URLs are supported.")
    base = Path(tempfile.gettempdir()) / "github_repo_ai_architect"
    base.mkdir(parents=True, exist_ok=True)
    target = base / hashlib.sha256(url.encode()).hexdigest()[:16]
    if target.exists():
        shutil.rmtree(target, ignore_errors=True)
    Repo.clone_from(url, target, depth=1)
    return target
