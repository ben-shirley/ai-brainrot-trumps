from io import BytesIO
from logging import Logger

from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from src.brainrot_tcg.objects.top_trumps_card import TopTrumpsCard

CARD_WIDTH = 61
CARD_HEIGHT = 86
IMAGE_SIZE = 38
CARD_MARGIN = 10


def create_pdf(
    characters: list[tuple[TopTrumpsCard, Image.Image]],
    resource_filepath: str,
    logger: Logger | None = None,
) -> bytes:
    x_index = 0
    y_index = 0
    max_x_index = 3
    max_y_index = 0
    margin = 20 * mm
    x_spacing = (CARD_WIDTH + 4) * mm
    y_spacing = (CARD_HEIGHT * 2 + 5) * mm

    pdf_io = BytesIO()
    pdf = canvas.Canvas(pdf_io, pagesize=landscape(A4))
    if logger:
        logger.info("creating pdf")
    for i, (character, image) in enumerate(characters):
        if logger and i % 10 == 0:
            logger.info(f"drawing {i}th character, {character.name}")
        draw_card(
            pdf=pdf,
            x=margin + x_index * x_spacing,
            y=margin + y_index * y_spacing,
            character=character,
            resource_filepath=resource_filepath,
            character_img=image,
        )
        x_index += 1
        if x_index > max_x_index:
            x_index = 0
            y_index += 1
        if y_index > max_y_index:
            y_index = 0
            pdf.showPage()

    pdf.save()
    return pdf_io.getvalue()


def draw_card(
    pdf: canvas.Canvas,
    resource_filepath: str,
    x: float,
    y: float,
    character: TopTrumpsCard,
    character_img: Image.Image,
) -> None:

    pdf.drawImage(
        f"{resource_filepath}/card_front_{character.rarity}.png",
        x,
        y,
        width=CARD_WIDTH * mm,
        height=CARD_HEIGHT * mm,
    )
    pdf.drawImage(
        f"{resource_filepath}/card_back.png",
        x,
        y + CARD_HEIGHT * mm,
        width=CARD_WIDTH * mm,
        height=CARD_HEIGHT * mm,
    )

    pdf.drawImage(
        ImageReader(character_img),
        x=x + ((CARD_WIDTH - IMAGE_SIZE) / 2) * mm,
        y=y + 44 * mm,
        height=IMAGE_SIZE * mm,
        width=IMAGE_SIZE * mm,
    )

    pdf.setFontSize(4 * mm)
    pdf.drawString(x=x + CARD_MARGIN, y=y + 37 * mm, text=character.name[:28])
    pdf.setFontSize(3 * mm)
    pdf.drawString(x=x + CARD_MARGIN, y=y + 33.5 * mm, text=character.short_name[:35])

    pdf.drawString(
        x=x + CARD_MARGIN,
        y=y + 29 * mm,
        text=f"- Weight: {character.weight} {character.weight_units}",
    )
    pdf.drawString(
        x=x + CARD_MARGIN,
        y=y + 25.5 * mm,
        text=f"- Height: {character.height} {character.height_units}",
    )
    pdf.drawString(x=x + CARD_MARGIN, y=y + 22 * mm, text=f"- HP: {character.hp}")
    pdf.drawString(
        x=x + CARD_MARGIN, y=y + 18.5 * mm, text=f"- Attack: {character.attack}"
    )
    pdf.drawString(
        x=x + CARD_MARGIN, y=y + 15 * mm, text=f"- Defense: {character.defense}"
    )
    pdf.drawString(
        x=x + CARD_MARGIN, y=y + 11.5 * mm, text=f"- Speed: {character.speed}"
    )
