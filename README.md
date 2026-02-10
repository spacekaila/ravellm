# Ravellm

Not sure what to knit next? Ravellm has you covered.

Intelligent knitting pattern recommender system using retrieval-augmented generation (RAG) to suggest patterns based on queries like "I want to knit lightweight summer socks" (using natural language processing, NLP). The system retrieves similar patterns from a vector database and uses an LLM to generate personalized recommendations with explanations.

## Features

- Data validation: checks for missing fields, ensures that patterns in multiple categories are only fetched and saved once.
- Incremental updates: checks new pattern IDs against database pattern IDs before saving, ensures no duplicate patterns saved.

**To Add**
- Conversational memory: allow user to refine searches with followup queries like "I want something easier" or "but in worsted weight".
- Recommendation guardrails: filters to recommend patterns of appropriate skill level or attributes.
- Dynamic prompting: detect skill level from query (beginner to advanced) and adjust LLM prompt to give appropriate complexity.
- Difficulty predictor: train a classifier on pattern metadata to predict difficulty level.
- Evaluation metrics: calculate precision and recall for queries.

## Tech stack
- SentenceTransformers
- ChromaDB
- LangChain
- mistral:7b model

## To use

0. Clone repo and set up Ravelry pro credentials (free)

```bash
git clone git@github.com:spacekaila/ravellm.git
```

Read about how to set up Rav API access [here](https://www.ravelry.com/api). You'll also need a free Ravelry account.

1. Install and test Ollama

```bash
brew install ollama

ollama serve. # run in separate terminal window

ollama pull mistral:7b

ollama run mistral:7b "Hello, how are you?"
```

2. Install tech stack

```bash
pip install chromadb sentence-transformers langchain-ollama langchain-core requests python-dotenv jupyterlab ipykernel
```

3. Download and transform data

Open [download_data.py](download_data.py) and check to see if you want to change the categories.

Download and vectorize the data with

```bash
python download_data.py
python extract_transform_load.py
```

Note: every time you run [download_data.py](download_data.py), it writes a new file `data/raw/patterns_{i}.json`. You have to update the [extract_transform_load.py](extract_transform_load.py) file to have the correct filename.

4. Query the model

Open [ravellm_tutorial.ipynb](ravellm_tutorial.ipynb) and change the query as you wish. Run the cells.

On my M1 Macbook with 16GB RAM it takes ~30-60 seconds to answer a query.