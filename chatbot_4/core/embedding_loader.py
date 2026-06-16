import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()


embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY")
)
