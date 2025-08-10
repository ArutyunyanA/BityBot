from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
import os
import yaml

load_dotenv()  # загружает переменные из .env
YAML_PATH = os.getenv("YAML_FILE")

class Interpreter:

    def __init__(self, yaml_path=YAML_PATH):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self._load_yaml(yaml_path)

    def _load_yaml(self, path):
        with open(path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        self.intents = config["intents"]
        self.trigger_phrases = []
        self.phrase_to_intent = []
        for intent in self.intents:
            for trig in intent.get("triggers", []):
                self.trigger_phrases.append(trig)
                self.phrase_to_intent.append(intent)
        self.embeddings = self.model.encode(self.trigger_phrases, convert_to_tensor=True)

    def get_intent(self, user_input: str):
        user_emb = self.model.encode(user_input, convert_to_tensor=True)
        sim = util.cos_sim(user_emb, self.embeddings)
        best_idx = sim.argmax().item()
        if sim[0][best_idx].item() > 0.5:
            return self.phrase_to_intent[best_idx]
        return None

    def _extract_slots(self, intent: dict) -> str:
        slots = intent.get("slots")
        if isinstance(slot, str):
            return slot
        elif isinstance(slot, list) and slot:
            return slot[0]
        return "input"

