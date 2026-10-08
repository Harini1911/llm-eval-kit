import json
from pydantic import BaseModel

class GoldenItem(BaseModel):
    question: str
    answer: str | None = None          # None => absent (should abstain)
    relevant_ids: list[str] = []

class GoldenSet(BaseModel):
    items: list[GoldenItem]
    @property
    def answerable(self): return [i for i in self.items if i.answer is not None]
    @property
    def absent(self): return [i for i in self.items if i.answer is None]

def load_goldens(path: str) -> GoldenSet:
    return GoldenSet(items=[GoldenItem(**json.loads(l))
                            for l in open(path, encoding="utf-8") if l.strip()])