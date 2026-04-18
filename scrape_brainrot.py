import sys
from logging import Logger

import requests
from bs4 import BeautifulSoup

from src.trading_card import TradingCard


def main():
    output_directory = sys.argv[1]
    logger = Logger("brainrot scraper")
    BRAINROT_URL = "https://italianbrainrotcharacters.com"
    scrape_character("https://italianbrainrotcharacters.com/frigo-camelo")


def parse_all_brainrot(url: str, logger: Logger | None = None) -> list[TradingCard]:

    res = requests.get(url)
    parser = BeautifulSoup(res.content, "html.parser")

    brainrot_extensions = [
        str(link.attrs["href"])
        for link in parser.find_all("a", class_="character-card")
    ]
    print(brainrot_extensions)
    cards = []
    for extension in brainrot_extensions:
        card = scrape_character(url + extension)
        if card:
            cards.append(card)
        else:
            logger.warning(f"Failed to parse brainrot character at {extension}")


def scrape_character(url: str) -> TradingCard | None:
    res = requests.get(url)
    parser = BeautifulSoup(res.content, "html.parser")
    print(parser.prettify())
    
    move_boxes = parser.find_all("div", class_="power-card")
    for move_box in move_boxes:
        name = move_box.find("h3").text
        power_regex = r'⚡ Power: (\d\d)'
        accuracy_regex = r'🎯 Accuracy: (\d\d)%'



if __name__ == "__main__":
    main()
