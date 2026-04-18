from pydantic import BaseModel, field_validator


class Move(BaseModel):
    """Class representing a move that can be made by an italian brainrot character."""

    name: str
    power: int
    accuracy: float
    description: str

    @field_validator("power")
    @classmethod
    def _check_power(cls, power: int) -> int:
        if power < 0:
            raise ValueError("power must be non-negative.")
        return power

    @field_validator("accuracy")
    @classmethod
    def _check_accuracy(cls, accuracy: float) -> float:
        if accuracy < 0 or accuracy > 1:
            raise ValueError("accuracy must be between 0 and 1.")
        return accuracy
