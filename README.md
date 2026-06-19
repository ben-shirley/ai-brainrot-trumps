# AI Brainrot Top Trumps

A very silly Dagster pipeline which scrapes italianbrainrotcharacters.com for AI Brainrot characters,
and turns them into a card game!

!(./example.png)

## Running the pipeline
This project uses uv to manage dependencies.
- First, clone the repo, and run `uv sync`.
- Next, set up your database at a path of your choice. You can run `./scripts/init_database.sql` to set it up with the correct tables.
- To run the pipeline run `dagster dev` and go to `localhost:3000`. From there go to "matarialize an asset", and "materialize all" to run the pipeline in full.

### Environment Variables
The "stats" for many of the characters on italianbrainrotcharacters.com are incomplete or missing all together, and so we make use of llms to fill in the gaps.
Furthermore, dagster can use environment variables pretty well, so I thought it made sense to store many of the "constant" variables like table names and directory paths in environment variables. 
Just create a `.env` file and make sure all these are configured.


Two models are used, one to summarize the character image, and the other to take that, and any existing details and produce relevant character stats.
We also store all intermediate steps in an sqlite3 database, and images in a directory of our choice so that each step can be rerun independently.

The following environment variables should be set:
**Model Endpoints** (using the standard openai api):
- `MODEL_NAME`: name of the stat generation model. I used `llama3.1:8b`.
- `IMAGE_MODEL_NAME`: name of the image summarization model. I used `llava:7b`.
- `MODEL_ENDPOINT`: endpoint for the models.
- `API_KEY`: If required. I just ran my models locally, cos my machine is a BEAST.


**Storage Configuration**
- `DATABASE_PATH`: Path to sqlite3 database
- `BRAINROT_TABLE=brainrot`: Name of the table where all the brainrot characters are stored.
- `SCRAPED_DATA_TABLE=scraped_data`: Name of the table where all the raw data from the website is stored.
- `IMG_SAVE_DIR`: Path to save scraped images. In future I'd probably rather base64 encode these and just chuck them in the DB.
- `PDF_SAVE_DIR`: Path to save the pdf.
- `PDF_RESOURCE_PATH=./resources/public/tradingcards`

- `BRAINROT_URL`: url of the website. For me this was `https://italianbrainrotcharacters.com`.


