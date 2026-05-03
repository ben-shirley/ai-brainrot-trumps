import dagster as dg

from src.brainrot_tcg.defs.assets import (
    generate_pdf,
    get_brainrot_characters_from_website,
    get_processed_brainrot_characters,
    save_and_enrich_brainrot,
    scrape_new_brainrot_characters,
)
from src.brainrot_tcg.defs.resources import (
    BrainrotDatabaseResource,
    BrainrotWebsiteResource,
    ImageStoreResource,
    PDFResource,
)

definitions = dg.Definitions(
    assets=[
        get_processed_brainrot_characters,
        get_brainrot_characters_from_website,
        scrape_new_brainrot_characters,
        save_and_enrich_brainrot,
        generate_pdf,
    ],
    resources={
        "database": BrainrotDatabaseResource(
            database_path=dg.EnvVar("DATABASE_PATH"),
            brainrot_table_name=dg.EnvVar("BRAINROT_TABLE"),
            scraped_data_table_name=dg.EnvVar("SCRAPED_DATA_TABLE"),
        ),
        "website": BrainrotWebsiteResource(website_url=dg.EnvVar("BRAINROT_URL")),
        "image_store": ImageStoreResource(image_save_dir=dg.EnvVar("IMG_SAVE_DIR")),
        "pdf_resource": PDFResource(
            pdf_save_dir=dg.EnvVar("PDF_SAVE_PATH"),
            pdf_resource_dir=dg.EnvVar("PDF_RESOURCE_PATH"),
        ),
    },
)
