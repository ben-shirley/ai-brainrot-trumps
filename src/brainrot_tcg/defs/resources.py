import sqlite3
from pathlib import Path

import dagster as dg
import requests
from PIL import Image


class BrainrotDatabaseResource(dg.ConfigurableResource):
    database_path: str
    brainrot_table_name: str
    scraped_data_table_name: str

    def connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)


class BrainrotWebsiteResource(dg.ConfigurableResource):
    website_url: str

    def get_page_content(self, extension: str = "") -> requests.Response:
        return requests.get(self.website_url + extension)


class PDFResource(dg.ConfigurableResource):
    pdf_resource_dir: str
    pdf_save_dir: str

    def save(self, pdf_data: bytes) -> None:
        with Path(self.pdf_save_dir).open("wb") as file:
            file.write(pdf_data)


class ImageStoreResource(dg.ConfigurableResource):
    image_save_dir: str

    def save(self, character_name: str, img: Image.Image):
        img = img.convert("RGB")
        img.save(f"{self.image_save_dir}/{self._format_name(character_name)}.jpg")

    def get(self, character_name: str) -> Image.Image:
        return Image.open(
            f"{self.image_save_dir}/{self._format_name(character_name)}.jpg"
        )

    def _format_name(self, name: str) -> str:
        return name.lower().replace(" ", "-")
