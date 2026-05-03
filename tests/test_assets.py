import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch

import dagster as dg
from conftest import DATABASE_DIR
from PIL import Image

from brainrot_tcg.database import get_all_brainrot
from brainrot_tcg.defs.assets import (
    get_brainrot_characters_from_website,
    get_processed_brainrot_characters,
    save_and_enrich_brainrot,
    scrape_new_brainrot_characters,
)
from brainrot_tcg.defs.resources import (
    BrainrotDatabaseResource,
    BrainrotWebsiteResource,
    ImageStoreResource,
)


def test_get_brainrot_characters_from_website():
    context = dg.build_asset_context()
    website_resource = BrainrotWebsiteResource(website_url="coolpage.com")

    mock_response = Mock()
    with Path("tests/resources/sample_main_page.html").open("rb") as file:
        mock_response.content = file.read()
    with patch("requests.get", return_value=mock_response):
        characters = get_brainrot_characters_from_website(context, website_resource)

    assert isinstance(characters, set)
    assert len(characters) == 126


def test_get_processed_brainrot_characters():
    context = dg.build_asset_context()
    database_resource = BrainrotDatabaseResource(
        database_path="tests/resources/test_database.db",
        scraped_data_table_name="scraped_data",
        brainrot_table_name="not useful",
    )
    character_extensions = get_processed_brainrot_characters(context, database_resource)

    assert isinstance(character_extensions, set)
    assert len(character_extensions) == 1
    assert "test-test-test-sahur" in character_extensions


def test_scrape_new_brainrot_characters():
    context = dg.build_asset_context()
    website_resource = BrainrotWebsiteResource(website_url="coolsite.com")
    database_resource = BrainrotDatabaseResource(
        database_path="tests/resources/test_database.db",
        scraped_data_table_name="scraped_data",
        brainrot_table_name="not useful",
    )
    image_resource = ImageStoreResource(image_save_dir="tests/resources")

    mock_response = Mock()
    mock_img_response = Mock()
    with Path("tests/resources/tung_tung.html").open("rb") as file:
        mock_response.content = file.read()
    with Path("tests/resources/tung_tung.jpg").open("rb") as file:
        mock_img_response.content = file.read()

    with patch("requests.get", side_effect=[mock_response, mock_img_response]):
        scrape_new_brainrot_characters(
            context=context,
            get_processed_brainrot_characters=set(),
            get_brainrot_characters_from_website={
                "tung-tung-hurar-tung-tung-tung-sahur"
            },
            website=website_resource,
            database=database_resource,
            image_store=image_resource,
        )
    connection = sqlite3.Connection(DATABASE_DIR)
    cursor = connection.cursor()
    query = """SELECT
        extension,
        name,
        short_name,
        height,
        height_units,
        weight,
        weight_units,
        attack,
        defense,
        special_attack,
        special_defense,
        speed,
        lore
        FROM scraped_data"""
    result = cursor.execute(query)
    data = result.fetchall()
    assert len(data) == 2
    tung_tung = data[1]
    assert tung_tung[1] == "Tung Tung Hurar Tung Tung Tung Sahur"
    assert tung_tung[2] == "Tungguk"
    assert tung_tung[3] == 2.1
    assert tung_tung[4] == "m"


@patch(
    "src.brainrot_tcg.enrichment.image_sumariser.ImageSummarizer.summarize_image",
    return_value="cool summary",
)
@patch("PIL.Image.open", return_value=Image.new(mode="RGB", size=(300, 300)))
def test_save_and_enrich_brainrot(mock_summary, mock_img, test_card):
    context = dg.build_asset_context()
    database_resource = BrainrotDatabaseResource(
        database_path="tests/resources/test_database.db",
        scraped_data_table_name="scraped_data",
        brainrot_table_name="brainrot",
    )
    image_resource = ImageStoreResource(image_save_dir="tests/resources")

    with patch(
        "src.brainrot_tcg.enrichment.llm_generator.LLMGenerator.generate",
        return_value=test_card,
    ):
        save_and_enrich_brainrot(
            context=context, database=database_resource, image_store=image_resource
        )

    connection = sqlite3.Connection(DATABASE_DIR)
    brainrot = get_all_brainrot(connection, "brainrot")
    connection.close()

    assert len(brainrot) == 1
    assert brainrot[0].model_dump_json() == test_card.model_dump_json()
