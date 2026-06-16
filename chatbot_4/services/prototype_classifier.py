import numpy as np
from core.embedding_loader import embedding_model
from utils.memory_prototypes import MEMORY_PROTOTYPES

from services.redis_services import (
    load_prototype_embeddings,
    save_prototype_embeddings,
)


class PrototypeClassifier:
    def __init__(self):
        self.embedding_model = embedding_model

        prototype_embeddings = load_prototype_embeddings()

        if (
            prototype_embeddings is None
        ):  # if prototype is not made then create them and save them to redis.
            print("creating prototype embeddings")

            prototype_embeddings = self.embedding_model.embed_documents(
                MEMORY_PROTOTYPES
            )

            save_prototype_embeddings(prototype_embeddings=prototype_embeddings)

        else:
            print("load prototype embeddings into RAM from redis")

            self.prototype_embeddings = np.array(
                object=prototype_embeddings, dtype=np.float32
            )

    # public module
    def needs_memory(
        self,
        user_query: str,
        threshold:int=0.8
    ) -> bool:
        query_embedding = np.array(
            self.embedding_model.embed_query(user_query),
            dtype=np.float32,
        )

        score = self._highest_similarity(query_embedding)

        return ( # ONLY RETURN IF SCORE IS GRETER THEN THRESHOLD . OTHERWISE NONE/FAlse
            score >= threshold,
            float(score),
        )

    # private modules

    # def _embed_query(): ...

    def _cosine_similarity(self, vector1: np.array, vector2: np.array):
        return np.dot(vector1, vector2) / (
            np.linalg.norm(vector1) * np.linalg.norm(vector2)
        )

    def _highest_similarity(
        self,
        query_embedding: np.ndarray,
    ):

        scores = [
            self._cosine_similarity(
                query_embedding,
                prototype,
            )
            for prototype in self.prototype_embeddings
        ]

        return max(scores)
