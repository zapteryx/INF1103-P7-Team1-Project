import re
from abc import ABC, abstractmethod


class Evaluator(ABC):
    """Abstract Base Class enforcing the evaluation contract taught in Week 9 & 10."""
    
    @abstractmethod
    def evaluate(self, shelter_description: str, client_data: dict) -> tuple[int, str | None]:
        pass


class GenderEvaluator(Evaluator):
    ONLY_WOMEN_KEYWORDS = ["women", "female", "women only", "mothers"]
    ONLY_MEN_KEYWORDS = ["men", "male", "fathers"]
    BONUS_POINTS = 40

    def _has_keyword(self, sentence: str, keywords: list[str]):
        if not sentence or not keywords:
            return False
        sentence_clean = str(sentence).lower()
        patterns = [r"\b" + re.escape(str(i).lower()) + r"\b" for i in keywords]
        return bool(re.search("|".join(patterns), sentence_clean))

    def evaluate(self, shelter_description: str, client_data: dict):
        client_gender = client_data.get("gender", "").lower().strip()
        
        if client_gender == "female":
            if self._has_keyword(shelter_description, self.ONLY_MEN_KEYWORDS):
                return -999, f"REJECT: female client mismatched for male-only shelter."
            elif self._has_keyword(shelter_description, self.ONLY_WOMEN_KEYWORDS):
                return self.BONUS_POINTS, None

        elif client_gender == "male":
            if self._has_keyword(shelter_description, self.ONLY_WOMEN_KEYWORDS):
                return -999, f"REJECT: male client mismatched for female-only shelter."
            elif self._has_keyword(shelter_description, self.ONLY_MEN_KEYWORDS):
                return self.BONUS_POINTS, None

        return 0, None


class CareTypeEvaluator(Evaluator):
    LONG_TERM_KEYWORDS = ["long term", "long-term", "longterm", "supportive housing"]
    SHORT_TERM_KEYWORDS = ["short term", "short-term", "emergency", "crisis", "transitional"]
    BONUS_POINTS = 40
    PENALTY_POINTS = -50

    def _has_keyword(self, sentence: str, keywords: list[str]):
        if not sentence or not keywords:
            return False
        sentence_clean = str(sentence).lower()
        patterns = [r"\b" + re.escape(str(i).lower()) + r"\b" for i in keywords]
        return bool(re.search("|".join(patterns), sentence_clean))

    def evaluate(self, shelter_description: str, client_data: dict):
        client_care_type = client_data.get("care_type", "").lower()
        
        if client_care_type == "long term":
            if self._has_keyword(shelter_description, self.LONG_TERM_KEYWORDS):
                return self.BONUS_POINTS, None
            elif self._has_keyword(shelter_description, self.SHORT_TERM_KEYWORDS):
                return self.PENALTY_POINTS, None

        elif client_care_type == "short term":
            if self._has_keyword(shelter_description, self.SHORT_TERM_KEYWORDS):
                return self.BONUS_POINTS, None
            elif self._has_keyword(shelter_description, self.LONG_TERM_KEYWORDS):
                return self.PENALTY_POINTS, None

        return 0, None