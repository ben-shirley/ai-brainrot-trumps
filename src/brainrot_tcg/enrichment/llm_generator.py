import json
import os
from dataclasses import dataclass
from typing import Any

from pydantic_ai import Agent, RunContext, capture_run_messages
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydanticai_ollama.models.ollama import OllamaModel
from pydanticai_ollama.providers.ollama import OllamaProvider

from src.brainrot_tcg.objects.top_trumps_card import TopTrumpsCard

from .base_generator import BaseGenerator


@dataclass
class GeneratorDependencies:
    current_data: dict[str, Any]
    character_description: str


class LLMGenerator(BaseGenerator):
    def __init__(self):
        if "MODEL_NAME" in os.environ:
            self.model_name = os.environ["MODEL_NAME"]
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

        self.model_instructions = f"""
You are a data creation agent. Use the character description and provided fields to create a top trumps card.

Return a JSON object ONLY.
Do NOT include:
- explanations
- reasoning
- comments
- markdown
- extra text

The output MUST:
- be valid JSON
- match the schema exactly
- contain no trailing text

Rules:
- All numeric fields must be numbers (not strings)
- Do not include units inside values
- Use separate unit fields
- Whilst height and weight have no upper bound, try to keep the other stats below 100, unless you judge it necessary to exceed these bounds.

If you include ANY text outside the JSON object, the response is invalid.

The schema is as follows:

{json.dumps(TopTrumpsCard.model_json_schema(), indent=4)}
        """  # noqa: E501

        # 3. Initialize OllamaProvider with your Ollama server's base URL
        #    Default is "http://localhost:11434"
        ollama_provider = OllamaProvider(base_url=self.model_endpoint)

        # 4. Create an OllamaModel instance
        #    Replace 'llama2' with the name of the Ollama model you want to use
        ollama_model = OllamaModel(
            model_name=self.model_name,
            provider=ollama_provider,
            # settings=ollama_settings
        )
        self.agent = Agent(
            model=ollama_model,
            output_type=TopTrumpsCard,
            deps_type=GeneratorDependencies,
            instructions=self.model_instructions,
        )

        @self.agent.system_prompt
        def create_system_prompt(ctx: RunContext[GeneratorDependencies]) -> str:
            return f"""
                    Create a brainrot character from the given data.
                    The current data is: {ctx.deps.current_data}.
                    The character description is as follows:
                        {ctx.deps.character_description}.
                    """

    def generate(self, data: dict[str, Any]) -> TopTrumpsCard:
        lore = data.pop("lore")
        context = GeneratorDependencies(current_data=data, character_description=lore)

        with capture_run_messages() as messages:
            try:
                llm_card = self.agent.run_sync(deps=context).output
                if type(llm_card) is not TopTrumpsCard:
                    raise UnexpectedModelBehavior(
                        "Output should always be a top trumps card"
                    )
                # sometimes the model might hallucinate old parameters,
                # which we would of course like to override.
                # HACK currently this data depends on the way the previous steps
                # output json. this is probably bad practice.
                if llm_card.name != data["name"]:
                    llm_card.name = data["name"]
                return llm_card
            except UnexpectedModelBehavior as e:
                print("MODEL FAILURE: here is the actual model output...")
                for message in messages:
                    print("\n" * 3)
                    print(message)

                raise ValueError(e)
