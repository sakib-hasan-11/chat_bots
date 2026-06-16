import os
import time

from core.embedding_loader import embedding_model
from dotenv import load_dotenv
from pinecone import Pinecone
from utils.fact_to_text import fact_to_text

load_dotenv()


class PineconeService:
    def __init__(self):

        self.pc = Pinecone(api_key=os.getenv("PINECONE_API"))

        self.index = self.pc.index(host=os.getenv("PINECONE_HOST"))

        self.embedding_model = embedding_model

    def archive_fact_memory_to_pinecone(
        self,
        user_id: str,
        fact_memory: dict,
    ):

        fact_text = fact_to_text(fact_memory)

        embedding = self.embedding_model.embed_query(fact_text)

        vector_id = f"memory_{int(time.time())}"

        metadata = {
            "user_id": user_id,
            "fact_text": fact_text,
            "type": "fact_memory",
            "created_at": int(time.time()),
        }

        self.index.upsert(
            vectors=[{"id": vector_id, "values": embedding, "metadata": metadata}],
            namespace=user_id,
        )

    def search_memory(
        self,
        user_id: str,
        query: str,
        top_k: int = 3,
    ):
        embedding = embedding_model.embed_query(query)

        results = self.index.query(
            namespace=user_id,
            vector=embedding,
            top_k=top_k,
            include_metadata=True,
        )

        # matched= results.matches

        return [ el.metadata['fact_text'] for el in results.matches] # sent the facts medata data so that we get the txt not embedings . now we dont need to convert to text again .

    def delete_namespace(
        self,
        user_id: str,
    ):
        self.index.delete(delete_all=True, namespace=user_id)
