import json
from pathlib import Path

from src.brainrot_tcg.enrichment.llm_generator import LLMGenerator


def main():
    card_1 = generate_card("resources/characters/Rhino_Toasterino.json")
    # card_2 = generate_card("resources/characters/Aduh_9_April_Udah_Dekat.json")

    print(card_1.model_dump_json(indent=4))


def generate_card(filepath: str):
    with Path(filepath).open() as file:
        data = json.load(file)
    print(f"generating card for {data['name']}")

    generator = LLMGenerator()
    return generator.generate(data)


if __name__ == "__main__":
    main()
