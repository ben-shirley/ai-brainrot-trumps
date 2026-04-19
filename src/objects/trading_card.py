from typing import Self

from pydantic import BaseModel, model_validator

from src.move import Move


class TradingCard(BaseModel):
    name: str
    short_name: str
    height: str
    weight: str

    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int

    moves: list[Move] | None

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.moves is not None and len(self.moves) != 4:
            raise ValueError("Exactly 4 moves required.")
        return self
