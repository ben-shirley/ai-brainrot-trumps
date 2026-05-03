import os
from base64 import b64encode
from io import BytesIO

import requests
from PIL import Image


class ImageSummarizer:
    def __init__(self):
        if "IMAGE_MODEL_NAME" in os.environ:
            self.model_name = os.environ["IMAGE_MODEL_NAME"]
        else:
            raise OSError("MODEL_NAME not in environment variables")

        if "MODEL_ENDPOINT" in os.environ:
            self.model_endpoint = os.environ["MODEL_ENDPOINT"]
        else:
            raise OSError("MODEL_ENDPOINT not in environment variables")

        if "API_KEY" in os.environ:
            self.api_key = os.environ["API_KEY"]
        else:
            raise OSError("API_KEY not in environment variables")

        self.prompt = """
            You are a specialized image description agent, whose job is to describe images of characters in detail.
            It is important that you do not add detail which is not there,
            as these descriptions will be used in a critical environment and mistakes will have serious flow-on effects.
        """  # noqa: E501

    def _base64_encode(self, image: Image.Image):
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        img_encoding = b64encode(buffer.getvalue())

        return img_encoding.decode("utf-8")

    def summarize_image(self, image: Image.Image) -> str:
        image = image.convert("RGB")
        encoding = self._base64_encode(image)
        payload = {
            "model": self.model_name,
            "prompt": self.prompt,
            "images": [encoding],
            "stream": False,
        }

        response = requests.post(
            f"{self.model_endpoint}/api/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            return response.json()["response"]

        raise Exception(f"API Error: {response.status_code}")
