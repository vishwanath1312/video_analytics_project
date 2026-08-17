import requests

SYSTEM_PROMPT = """You are a senior software architect and technical documentation engineer.
Understand the repository from the supplied evidence. Do not invent modules, dependencies, APIs, databases, or deployment mechanisms.
Produce:
1. Executive summary
2. Problem solved
3. Technology stack
4. Repository structure
5. Architecture
6. Major modules and responsibilities
7. Data flow
8. Control flow
9. Important dependencies
10. Configuration and deployment
11. Strengths
12. Risks and limitations
13. Suggested improvements
14. Research opportunities
Clearly distinguish evidence from inference."""

class OllamaLLM:
    def __init__(self, model="llama3.1:8b", host="http://localhost:11434"):
        self.model=model; self.host=host.rstrip("/")
    def generate(self, context):
        r=requests.post(f"{self.host}/api/generate",json={"model":self.model,"prompt":SYSTEM_PROMPT+"\n\nREPOSITORY EVIDENCE:\n"+context,"stream":False,"options":{"temperature":0.1}},timeout=600)
        r.raise_for_status()
        return r.json().get("response","").strip()
