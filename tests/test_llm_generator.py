import sqlite3
from unittest.mock import Mock, patch

from src.brainrot_tcg.database import get_all_unprocessed_scraped_data
from src.brainrot_tcg.enrichment.llm_generator import LLMGenerator
from tests.conftest import DATABASE_DIR


def test_llm(test_card):
    generator = LLMGenerator()

    connection = sqlite3.Connection(DATABASE_DIR)
    data = get_all_unprocessed_scraped_data(connection, "scraped_data", "brainrot")
    connection.close()

    mock_agent_response = Mock()
    test_card.name = "different"
    mock_agent_response.output = test_card
    with patch("pydantic_ai.Agent.run_sync", return_value=mock_agent_response):
        card = generator.generate(data[0])

    assert card.name == data[0]["name"]
