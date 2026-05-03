from abc import ABC, abstractmethod
from typing import Any

from src.brainrot_tcg.objects.top_trumps_card import TopTrumpsCard


class BaseGenerator(ABC):
    @abstractmethod
    def generate(self, data: dict[str, Any]) -> TopTrumpsCard:
        pass
