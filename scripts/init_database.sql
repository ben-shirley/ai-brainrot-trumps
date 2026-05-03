
CREATE TABLE IF NOT EXISTS brainrot(
    name VARCHAR(100) PRIMARY KEY,
    short_name VARCHAR(100) NOT NULL,

    weight FLOAT CHECK(weight>0) NOT NULL,
    weight_units VARCHAR(3) NOT NULL,
    height FLOAT CHECK(height>0) NOT NULL,
    height_units VARCHAR(3) NOT NULL,

    hp INT CHECK(hp>=0) NOT NULL,
    attack INT CHECK(attack>=0) NOT NULL,
    defense INT CHECK(defense>=0) NOT NULL,
    special_attack INT CHECK(special_attack>=0) NOT NULL,
    special_defense INT CHECK(special_defense>=0) NOT NULL,
    speed INT CHECK(speed>=0) NOT NULL,

    rarity VARCHAR(30) CHECK(rarity IN ("MYTHIC_RARE",
                                        "RARE",
                                        "UNCOMMON",
                                        "COMMON")) NOT NULL
);

CREATE TABLE IF NOT EXISTS scraped_data(
    extension VARCHAR(100) PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    short_name VARCHAR(100),

    weight FLOAT CHECK(weight>0),
    weight_units VARCHAR(3),
    height FLOAT CHECK(height>0),
    height_units VARCHAR(3),

    hp INT CHECK(hp>=0),
    attack INT CHECK(attack>=0),
    defense INT CHECK(defense>=0),
    special_attack INT CHECK(special_attack>=0),
    special_defense INT CHECK(special_defense>=0),
    speed INT CHECK(speed>=0),
    lore TEXT
);