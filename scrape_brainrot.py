
from PIL import Image
from typing import Any
import json
from os import name
import sys
from logging import Logger

import requests
from bs4 import BeautifulSoup

from src.trading_card import TradingCard

LOGGER = Logger("brainrot scraper")


def main():
    output_directory = sys.argv[1]
    BRAINROT_URL = "https://italianbrainrotcharacters.com"
    # scrape_character(BRAINROT_URL, "/nooo-my-hotspot")
    cards = parse_all_brainrot(BRAINROT_URL)
    for card in cards:
        output_file = f"{output_directory}/{card["name"].replace(" ", "_")}.json"  # ty:ignore[unresolved-attribute]
        with open(output_file, "w") as file:
            file.write(json.dumps(card, indent=4))
            print(f"wrote {card["name"]} to file")


def parse_all_brainrot(url: str) -> list[dict[str, Any]]:

    res = requests.get(url)
    parser = BeautifulSoup(res.content, "html.parser")

    brainrot_extensions = [
        str(link.attrs["href"])
        for link in parser.find_all("a", class_="character-card")
    ]
    print(brainrot_extensions)
    cards = []
    for extension in brainrot_extensions:
        card = scrape_character(url, extension)
        if card:
            cards.append(card)
        else:
            LOGGER.warning(f"Failed to parse brainrot character at {extension}")
    return cards


def scrape_character(base_url: str, extension: str) -> dict[str, Any] | None:
    res = requests.get(base_url + extension)
    parser = BeautifulSoup(res.content, "html.parser")
    parser.prettify()

    meta_dict: dict[str, str] = {}
    character_meta = parser.find(name="div", class_="character-meta")
    if character_meta is not None:
        metadata = character_meta.find_all("li")
        for metadatum in metadata:
            key = metadatum.find("strong")
            val = metadatum.find("div", class_="text-end")
            if key is not None and val is not None:
                meta_dict[key.text.strip()] = val.text.strip()

    stat_dict: dict[str, int] = {}
    character_stats = parser.find(name="section", class_="character-stat")
    if character_stats is not None:
        stats = character_stats.find_all("li")
        for stat in stats:
            key = stat.find("strong")
            val = stat.find("span")
            if key is not None and val is not None:
                stat_dict[key.text.strip()] = int(val.text.strip())
    lore_tag = parser.find("section", class_="character-post")
    lore = None
    if lore_tag is not None:
        lore = lore_tag.text

    character_img = parser.find("div", class_="character-img")
    image = None
    if character_img is not None:
        img_elem = character_img.find("img")
        if img_elem is not None:
            image_ext = str(img_elem.attrs["src"])
            image = get_brainrot_image(base_url, image_ext)



    return {
        "name":meta_dict.get("Name", "error"),
        "short_name":meta_dict.get("Short Name", None),
        "height":meta_dict.get("Height", None),
        "weight":meta_dict.get("Weight", None),
        "hp":stat_dict.get("HP", None),
        "attack":stat_dict.get("Attack", None),
        "defense":stat_dict.get("Defense", None),
        "special_attack":stat_dict.get("Special Attack", None),
        "special_defense":stat_dict.get("Special Defense", None),
        "speed":stat_dict.get("Speed", None),
        "lore": lore
    }

def get_brainrot_image(base_url: str, extension: str) -> bool:
    res = requests.get(base_url + extension).content
    filename = extension.split("/")[-1]
    with open(f"resources/images/{filename}.jpg", "wb") as file:
        file.write(res)
    return True

if __name__ == "__main__":
    main()
