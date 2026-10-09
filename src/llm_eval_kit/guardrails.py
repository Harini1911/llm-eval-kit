import re
from pydantic import BaseModel

_PII = [(re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL]"),
        (re.compile(r"\b[6-9]\d{9}\b"), "[PHONE]"),
        (re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"), "[PAN]"),
        (re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"), "[AADHAAR]")]
def redact_pii(text: str) -> str:
    for pat, repl in _PII: text = pat.sub(repl, text)
    return text

_INJECTION = ["ignore previous instructions", "ignore all previous", "disregard the above",
              "disregard previous", "forget your instructions", "you are now",
              "developer mode", "system prompt", "reveal your prompt", "jailbreak",
              "do anything now"]
def detect_injection(text: str) -> dict:
    low = text.lower(); hits = [p for p in _INJECTION if p in low]
    return {"flagged": bool(hits), "patterns": hits}

class Policy(BaseModel):
    block_injection: bool = True
    redact_pii_input: bool = True
    redact_pii_output: bool = True
    max_input_chars: int = 8000

class Decision(BaseModel):
    allow: bool; reason: str = ""; text: str = ""

class GuardrailEngine:
    def __init__(self, policy: Policy | None = None): self.p = policy or Policy()
    def check_input(self, text: str) -> Decision:
        if len(text) > self.p.max_input_chars:
            return Decision(allow=False, reason="input_too_long")
        if self.p.block_injection and detect_injection(text)["flagged"]:
            return Decision(allow=False, reason="prompt_injection")
        return Decision(allow=True, text=redact_pii(text) if self.p.redact_pii_input else text)
    def check_output(self, text: str) -> Decision:
        return Decision(allow=True, text=redact_pii(text) if self.p.redact_pii_output else text)