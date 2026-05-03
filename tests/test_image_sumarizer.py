from unittest.mock import Mock, patch

from PIL import Image

from src.brainrot_tcg.enrichment.image_sumariser import ImageSummarizer


def test_image_summarizer():
    summarizer = ImageSummarizer()

    image = Image.open("tests/resources/tung_tung.jpg")
    mock_llm_response = Mock()
    fake_response = "hehe I'm not an llm"
    mock_llm_response.json.return_value = {"response": fake_response}
    mock_llm_response.status_code = 200

    with patch("requests.post", return_value=mock_llm_response):
        output = summarizer.summarize_image(image)
    assert output == fake_response
