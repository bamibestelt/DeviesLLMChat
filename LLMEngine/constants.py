import os

from chromadb.config import Settings
from dotenv import load_dotenv

if not load_dotenv():
    print("Could not load .env file or it is empty. Please check if it exists and is readable.")
    exit(1)

LLM_HOST_ADDRESS = os.environ.get('LLM_HOST_ADDRESS')
LLM_PORT_ADDRESS = int(os.environ.get('LLM_PORT_ADDRESS'))

MODEL_TYPE = os.environ.get('MODEL_TYPE')
MODEL_PATH = os.environ.get('MODEL_PATH')
MODEL_N_CTX = os.environ.get('MODEL_N_CTX')
MODEL_N_BATCH = int(os.environ.get('MODEL_N_BATCH', 8))
TARGET_SOURCE_CHUNKS = int(os.environ.get('TARGET_SOURCE_CHUNKS', 4))

BLOG_RSS = os.environ.get('BLOG_RSS')
EMBEDDINGS_MODEL_NAME = os.environ.get('EMBEDDINGS_MODEL_NAME')

# Define the folder for storing database
PERSIST_DIRECTORY = os.environ.get('PERSIST_DIRECTORY')
if PERSIST_DIRECTORY is None:
    raise Exception("Please set the PERSIST_DIRECTORY environment variable")

# Define the Chroma settings
CHROMA_SETTINGS = Settings(
    persist_directory=PERSIST_DIRECTORY,
    anonymized_telemetry=False
)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
