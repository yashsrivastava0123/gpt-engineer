import logging
import os

from pathlib import Path

import openai
import typer

from dotenv import load_dotenv

from gpt_engineer.ai import AI
from gpt_engineer.collect import collect_learnings
from gpt_engineer.db import DB, DBs, archive
from gpt_engineer.learning import collect_consent
from gpt_engineer.steps import STEPS, Config as StepsConfig

app = typer.Typer()  # creates a CLI app


def load_env_if_needed():
    if os.getenv("OPENAI_API_KEY") is None:
        load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")


@app.command()
def main(
    project_path: str = typer.Argument("projects/example", help="path"),
    model: str = typer.Argument("gpt-4", help="model id string"),
    temperature: float = 0.1,
    steps_config: StepsConfig = StepsConfig.DEFAULT,
    # steps_config: StepsConfig = typer.Option(
    #     StepsConfig.DEFAULT, "--steps", "-s", help="decide which steps to run"
    # ),
    improve_option: bool = typer.Option(
        False,
        "--improve",
        "-i",
        help="Improve code from existing project.",
    ),
    azure_endpoint: str = typer.Option(
        "",
        "--azure",
        "-a",
        help="""Endpoint for your Azure OpenAI Service (https://xx.openai.azure.com).
            In that case, the given model is the deployment name chosen in the Azure AI Studio.""",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    body: dict = typer.Option({}, "--body", "-b"),
):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    # For the improve option take current project as path and add .gpteng folder
    if improve_option:
        # The default option for the --improve is the IMPROVE_CODE, not DEFAULT
        if steps_config == StepsConfig.DEFAULT:
            steps_config = StepsConfig.IMPROVE_CODE

    load_env_if_needed()

    azure_endpoint = os.getenv("OPENAI_API_BASE")
    ai = AI(
        model_name=os.getenv("OPENAI_API_DEPLOYMENT"),
        temperature=temperature,
        azure_endpoint=azure_endpoint,
    )

    dbs = DBs(
        memory=DB(data=body, identifier='memory'),
        logs=DB(data=body, identifier='logs'),
        preprompts=DB(data=body, identifier='preprompts'),
        input=DB(data=body, identifier='input_prompt'),
        workspace=DB(data=body, identifier='workspace'),
        archive=DB(data=body, identifier='archive')
    )

    if steps_config not in [
        StepsConfig.EXECUTE_ONLY,
        StepsConfig.USE_FEEDBACK,
        StepsConfig.EVALUATE,
        # StepsConfig.IMPROVE_CODE,
    ]:
        archive(dbs)

        if not dbs.input.get("prompt"):
            dbs.input["prompt"] = input(
                "\nWhat application do you want gpt-engineer to generate?\n"
            )

    steps = STEPS[steps_config]
    for step in steps:
        messages = step(ai, dbs)
        dbs.logs[step.__name__] = AI.serialize_messages(messages)

    dbs.logs["token_usage"] = ai.format_token_usage_log()


if __name__ == "__main__":
    app()
