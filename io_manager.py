import sys
from abc import ABC, abstractmethod
import data_manager


class ShelterBase(ABC):
    """Abstract base class defining the contract for shelter data representations."""
    
    def __init__(self, data: dict):
        self.data = data

    @abstractmethod
    def format_details(self) -> str:
        """Polymorphic method to format specific shelter details."""
        pass


class CsvShelter(ShelterBase):
    """Represents a standard CSV-loaded shelter record."""
    
    def format_details(self) -> str:
        name = self.data.get("name", "N/A")
        category = self.data.get("category", "N/A")
        requirements = self.data.get("requirements", "N/A")
        capacity = int(self.data.get("capacity", 0))
        occupants = int(self.data.get("occupants", 0))
        available = max(0, capacity - occupants)
        contact = self.data.get("contact", "N/A")

        info = ""
        info += f"Name:   {name}\n"
        info += f"Category:   {category}\n"
        info += f"Requirements:   {requirements}\n"
        info += f"Available:   {available} bed left ({occupants}/{capacity} occupied)\n"
        info += f"Contact:     {contact}"
        return info

class AIShelter(ShelterBase):
    """Represents an AI-manager-generated shelter recommendation record."""
    
    def format_details(self) -> str:
        rank = self.data.get("rank", "N/A")
        name = self.data.get("shelter_name", "N/A")
        ai_score = self.data.get("ai_suitability_score", "N/A")
        ai_conf = self.data.get("ai_confidence_score", "N/A")
        min_age = self.data.get("min_age", "N/A")
        max_age = self.data.get("max_age", "N/A")
        gender = self.data.get("gender_restriction", "N/A")
        dependents_allowed = self.data.get("dependents_allowed", False)
        dependents_status = "Allowed" if dependents_allowed else "Not Allowed"

        info = ""
        info += f"Rank       : {rank}\n"
        info += f"Name       : {name}\n"
        info += f"AI Score   : {ai_score}\n"
        info += f"AI Conf.   : {ai_conf}\n"
        info += f"Age Group  : {min_age} - {max_age}\n"
        info += f"Gender     : {gender}\n"
        info += f"Dependents : {dependents_status}"
        return info

