import re
from typing import Dict

class ParserNLP:
    def __init__(self):
        self._comma_split_re = re.compile(r',\s*')
        self.methods = {
            "nlp": self._parse_nlp_simple
        }
    async def parse(self, text, method, structure: list[str]) -> dict:
        parser_func = self.methods.get(method)
        if not parser_func:
            raise ValueError("f[ERROR] Unsuported parsing method: {method}")
        return await parser_func(text, structure)
    
    async def _parse_nlp_simple(self, text, structure: list[str]) -> dict:
        parts = self._comma_split_re.split(text.strip())
        if len(parts) != len(structure):
            return {}
        print(f"[DEBUG] parts: {parts}, structure: {structure}")
        return dict(zip(structure, parts))