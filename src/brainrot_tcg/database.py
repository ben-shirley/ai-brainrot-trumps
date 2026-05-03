import sqlite3

from src.brainrot_tcg.objects.top_trumps_card import TopTrumpsCard


def save_scraped_data(
    data: dict[str, str | int | None], connection: sqlite3.Connection, table_name: str
) -> None:
    cursor = connection.cursor()
    query = f"""INSERT INTO {table_name}(
        name, short_name, weight, weight_units, height, height_units,
        hp, attack, defense, special_attack, special_defense, speed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    cursor.execute(
        query,
        (
            data.get("extension"),
            data.get("name"),
            data.get("short_name"),
            data.get("weight"),
            data.get("weight_units"),
            data.get("height"),
            data.get("height_units"),
            data.get("hp"),
            data.get("attack"),
            data.get("defense"),
            data.get("special_attack"),
            data.get("special_defense"),
            data.get("speed"),
        ),
    )
    connection.commit()


def get_all_unprocessed_scraped_data(
    connection: sqlite3.Connection, table_name: str, excluded_table: str
) -> list[dict[str, str | int | None]]:
    query = f"""
        SELECT
            name, short_name, weight, weight_units, height, height_units,
            hp, attack, defense, special_attack, special_defense, speed,
        FROM {table_name} scraped_data
        WHERE NOT EXISTS (
            SELECT 1
            FROM {excluded_table} processed_data
            WHERE scraped_data.name = processed_data.name
        );
    """

    cursor = connection.cursor()
    result = cursor.execute(query)
    characters = []
    for character in result.fetchall():
        characters.append(
            {
                "name": character[0],
                "short_name": character[1],
                "height": character[2],
                "height_units": character[3],
                "weight": character[4],
                "weight_units": character[5],
                "hp": character[6],
                "attack": character[7],
                "defense": character[8],
                "special_attack": character[9],
                "special_defense": character[10],
                "speed": character[11],
                "rarity": character[12],
            }
        )
    return characters


def save_card(
    card: TopTrumpsCard, connection: sqlite3.Connection, table_name: str
) -> None:
    cursor = connection.cursor()
    query = f"""INSERT INTO {table_name}(
        name, short_name, weight, weight_units, height, height_units,
        hp, attack, defense, special_attack, special_defense, speed, rarity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    cursor.execute(
        query,
        (
            card.name,
            card.short_name,
            card.weight,
            card.weight_units,
            card.height,
            card.height_units,
            card.hp,
            card.attack,
            card.defense,
            card.special_attack,
            card.special_defense,
            card.speed,
            card.rarity,
        ),
    )
    connection.commit()


def get_all_brainrot(
    connection: sqlite3.Connection, table_name: str
) -> list[TopTrumpsCard]:
    query = f"""SELECT
        name, short_name, weight, weight_units, height, height_units,
        hp, attack, defense, special_attack, special_defense, speed,
        rarity FROM {table_name};"""

    cursor = connection.cursor()
    result = cursor.execute(query)
    characters = []
    for character in result.fetchall():
        characters.append(
            TopTrumpsCard(
                name=character[0],
                short_name=character[1],
                height=character[2],
                height_units=character[3],
                weight=character[4],
                weight_units=character[5],
                hp=character[6],
                attack=character[7],
                defense=character[8],
                special_attack=character[9],
                special_defense=character[10],
                speed=character[11],
                rarity=character[12],
            )
        )
    return characters
