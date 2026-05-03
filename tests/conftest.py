import sqlite3

import pytest

from src.brainrot_tcg.objects.rarity import Rarity
from src.brainrot_tcg.objects.top_trumps_card import TopTrumpsCard

DATABASE_DIR = "tests/resources/test_database.db"


@pytest.fixture(autouse=True)
def reset_database():
    connection = sqlite3.Connection(DATABASE_DIR)
    cursor = connection.cursor()
    cursor.execute("""
        DELETE FROM scraped_data;
    """)
    cursor.execute("""
        DELETE FROM brainrot;
    """)
    cursor.execute("""
        INSERT INTO scraped_data VALUES(
            \"test-test-test-sahur\",
            \"test test test sahur\",
            \"tesahur\",
            30, \"tonnes\",
            100, \"cm\",
            null, null, null, null, null, null,
            "test man has no lore..."
        );
    """)
    connection.commit()
    connection.close()


@pytest.fixture
def test_card() -> TopTrumpsCard:
    return TopTrumpsCard(
        name="test test test sahur",
        short_name="tesahur",
        weight=30,
        weight_units="tonnes",
        height=100,
        height_units="cm",
        hp=100,
        attack=100,
        defense=100,
        special_attack=100,
        special_defense=100,
        speed=100,
        rarity=Rarity.MYTHIC_RARE,
    )
