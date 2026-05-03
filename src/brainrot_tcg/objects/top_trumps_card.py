from pydantic import BaseModel, Field

from src.brainrot_tcg.objects.rarity import Rarity


class TopTrumpsCard(BaseModel):
    name: str = Field(description="Name of the brainrot character.")
    short_name: str = Field(
        description="Short name for the character. Sometimes longer than the actual name, because it's brainrot."  # noqa: E501
    )
    height: float = Field(description="Height of the character.", ge=0)
    height_units: str = Field(description="Units to interpret the height in, eg: cm.")
    weight: float = Field(description="Weight of the character.")
    weight_units: str = Field(description="Units to interpret the weight in, eg: kg.")

    hp: int = Field(description="Health Points of the character", ge=0)
    attack: int = Field(description="Attack Points of the character", ge=0)
    defense: int = Field(description="Defense Points of the character", ge=0)
    special_attack: int = Field(
        description="Special Attack Points of the character", ge=0
    )
    special_defense: int = Field(
        description="Special Defense Points of the character", ge=0
    )
    speed: int = Field(description="Speed of the character", ge=0)

    rarity: Rarity = Field(
        description="Rarity of the card. This is a metadata field and will not be used in the game."  # noqa: E501
    )
