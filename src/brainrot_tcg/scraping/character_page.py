from io import BytesIO
from typing import Any

from bs4 import BeautifulSoup
from PIL import Image

from src.brainrot_tcg.defs.resources import BrainrotWebsiteResource


def scrape_character(
    character: str, website: BrainrotWebsiteResource
) -> dict[str, Any] | None:
    res = website.get_page_content(extension=f"/{character}")
    parser = BeautifulSoup(res.content, "html.parser")

    # parse metadata block, for things like height, name
    meta_dict: dict[str, str] = {}
    character_meta = parser.find(name="div", class_="character-meta")
    if character_meta is not None:
        metadata = character_meta.find_all("li")
        for metadatum in metadata:
            key = metadatum.find("strong")
            val = metadatum.find("div", class_="text-end")
            if key is not None and val is not None:
                meta_dict[key.text.strip()] = val.text.strip()

    # parse stat block for attack, hp, etc
    stat_dict: dict[str, int] = {}
    character_stats = parser.find(name="section", class_="character-stat")
    if character_stats is not None:
        stats = character_stats.find_all("li")
        for stat in stats:
            key = stat.find("strong")
            val = stat.find("span")
            if key is not None and val is not None:
                stat_dict[key.text.strip()] = int(val.text.strip())

    # parse lore section
    lore_tag = parser.find("section", class_="character-post")
    lore = None
    if lore_tag is not None:
        lore = lore_tag.text

    # get character image
    character_img = parser.find("div", class_="character-img")
    image = None
    if character_img is not None:
        img_elem = character_img.find("img")
        if img_elem is not None:
            image_ext = str(img_elem.attrs["src"])
            image = scrape_brainrot_image(image_ext, website)

    try:
        height_str = meta_dict.get("Height", "")
        height, height_units = height_str.split()
        weight_str = meta_dict.get("Weight", "")
        weight, weight_units = weight_str.split()
    except ValueError:
        height = None
        weight = None
        weight_units = None
        height_units = None

    if image is None:
        return None

    return {
        "name": meta_dict.get("Name", "error"),
        "short_name": meta_dict.get("Short Name"),
        "height": float(height) if height is not None else None,
        "height_units": height_units,
        "weight": float(weight) if weight is not None else None,
        "weight_units": weight_units,
        "hp": stat_dict.get("HP"),
        "attack": stat_dict.get("Attack"),
        "defense": stat_dict.get("Defense"),
        "special_attack": stat_dict.get("Special Attack"),
        "special_defense": stat_dict.get("Special Defense"),
        "speed": stat_dict.get("Speed"),
        "lore": lore,
        "image": image,
    }


def scrape_brainrot_image(
    extension: str,
    website: BrainrotWebsiteResource,
) -> Image.Image:
    res = website.get_page_content(extension=extension)
    return Image.open(BytesIO(res.content))
