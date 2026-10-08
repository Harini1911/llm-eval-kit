def resolve_pairwise(choice1: str, choice2: str) -> dict:
    """choice1 from (A,B) order, choice2 from swapped (B,A); each '1' or '2'."""
    w1 = "A" if choice1 == "1" else "B"
    w2 = "B" if choice2 == "1" else "A"
    if w1 == w2:
        return {"winner": w1, "consistent": True, "position_bias": False}
    return {"winner": "tie", "consistent": False, "position_bias": (choice1 == choice2)}

class LLMJudge:
    """Needs the [judge] extra (openai). Scores answers against a rubric, and
    does pairwise comparisons twice with options swapped to detect position bias."""
    def __init__(self, llm):   # pass any LLMProvider (template's adapter works)
        self.llm = llm
    def pairwise(self, question, answer_a, answer_b) -> dict:
        c1 = self._ask(question, answer_a, answer_b)   # (A,B)
        c2 = self._ask(question, answer_b, answer_a)   # (B,A) swapped
        return resolve_pairwise(c1, c2)
    def _ask(self, q, first, second) -> str:
        prompt = (f"Question:{q}\n[1]:{first}\n[2]:{second}\n"
                  "Which answer is better? Reply with only '1' or '2'.")
        out = self.llm.complete([{"role": "user", "content": prompt}]).strip()
        return "1" if out.startswith("1") else "2"