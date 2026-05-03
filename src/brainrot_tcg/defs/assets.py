from sqlite3 import IntegrityError

import dagster as dg
from bs4 import BeautifulSoup

from src.brainrot_tcg.database import (
    get_all_brainrot,
    get_all_unprocessed_scraped_data,
    save_card,
    save_scraped_data,
)
from src.brainrot_tcg.defs.resources import (
    BrainrotDatabaseResource,
    BrainrotWebsiteResource,
    ImageStoreResource,
    PDFResource,
)
from src.brainrot_tcg.enrichment.image_sumariser import ImageSummarizer
from src.brainrot_tcg.enrichment.llm_generator import LLMGenerator
from src.brainrot_tcg.generate_pdf import create_pdf
from src.brainrot_tcg.scraping.character_page import scrape_character


@dg.asset
def get_brainrot_characters_from_website(
    context: dg.AssetExecutionContext, website: BrainrotWebsiteResource
) -> set[str]:
    res = website.get_page_content()
    parser = BeautifulSoup(res.content, "html.parser")

    characters = {
        str(link.attrs["href"])[1:]
        for link in parser.find_all("a", class_="character-card")
    }
    context.log.info(f"{len(characters)} pulled from website.")
    context.log.info(characters)

    return characters


@dg.asset
def get_processed_brainrot_characters(
    context: dg.AssetExecutionContext, database: BrainrotDatabaseResource
) -> set[str]:
    connection = database.connection()

    query = f"SELECT extension FROM {database.scraped_data_table_name}"
    extensions: list[tuple[str]] = connection.execute(query).fetchall()
    character_extensions = {extension[0] for extension in extensions}
    connection.close()

    context.log.info(
        f"database response: {len(character_extensions)} already processed"
    )
    context.log.info(character_extensions)
    return character_extensions


@dg.asset
def scrape_new_brainrot_characters(
    context: dg.AssetExecutionContext,
    get_processed_brainrot_characters: set[str],
    get_brainrot_characters_from_website: set[str],
    website: BrainrotWebsiteResource,
    database: BrainrotDatabaseResource,
    image_store: ImageStoreResource,
) -> None:
    characters_to_scrape = get_brainrot_characters_from_website.difference(
        get_processed_brainrot_characters
    )

    context.log.info(f"{len(characters_to_scrape)} new characters to be scraped.")
    result = [
        scrape_character(character, website) for character in characters_to_scrape
    ]

    connection = database.connection()
    for extension, card in zip(characters_to_scrape, result):
        if card is not None:
            card["extension"] = extension
            image = card.pop("image")
            save_scraped_data(card, connection, database.scraped_data_table_name)
            image_store.save(card["name"], image)
    connection.close()


@dg.asset(deps=[scrape_new_brainrot_characters])
def save_and_enrich_brainrot(
    context: dg.AssetExecutionContext,
    database: BrainrotDatabaseResource,
    image_store: ImageStoreResource,
) -> None:
    connection = database.connection()
    character_data = get_all_unprocessed_scraped_data(
        connection=connection,
        table_name=database.scraped_data_table_name,
        excluded_table=database.brainrot_table_name,
    )

    context.log.info(f"attempting to save {len(character_data)} characters.")
    image_summarizer = ImageSummarizer()
    character_creator = LLMGenerator()
    for character in character_data:
        if character is not None:
            try:
                image = image_store.get(str(character["name"]))
                image_summary = image_summarizer.summarize_image(image)
                character["lore"] = (
                    str(character.get("lore", ""))
                    + f"Summary of attached image:\n{image_summary}"
                )
                card = character_creator.generate(character)
                save_card(
                    card=card,
                    connection=connection,
                    table_name=database.brainrot_table_name,
                )
                context.log.info(
                    f"enrichment and saving of {character['name']} successful."
                )
            except (ValueError, IntegrityError):
                context.log.warning(f"failed to enrich {character['name']}")
    connection.close()


@dg.asset(deps=[save_and_enrich_brainrot])
def generate_pdf(
    context: dg.AssetExecutionContext,
    pdf_resource: PDFResource,
    database: BrainrotDatabaseResource,
    image_store: ImageStoreResource,
):
    connection = database.connection()
    characters = get_all_brainrot(
        connection=connection, table_name=database.brainrot_table_name
    )
    character_data = [
        (character, image_store.get(character.name)) for character in characters
    ]

    pdf_data = create_pdf(
        characters=character_data,
        resource_filepath=pdf_resource.pdf_resource_dir,
        logger=dg.get_dagster_logger(),
    )
    pdf_resource.save(pdf_data)
    context.log.info(
        f"PDF successfully created and saved to {pdf_resource.pdf_save_dir}"
    )
