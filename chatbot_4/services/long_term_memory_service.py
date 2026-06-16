from core.model_loader import llm
from langchain_core.output_parsers import PydanticOutputParser
from schema.fact_schema import FactMemory
from utils.fact_prompt_builder import build_fact_prompt

from services.pinecone_service import PineconeService
from services.redis_services import (
    load_fact_memory,
    save_fact_memory,
)


class LongTermMemoryService:
    def __init__(self, mysql):

        self.llm = llm

        # Shared MySQL instance (DO NOT create another one)
        self.mysql = mysql

        self.parser = PydanticOutputParser(pydantic_object=FactMemory)

        self.pinecone = PineconeService()

    # Trigger

    def should_update_memory(
        self,
        conversation_id: int,
        threshold: int = 20,
    ) -> bool:

        print(f"Checking conversation_id = {conversation_id}")

        total_user_messages = self.mysql.count_user_messages(conversation_id)

        print("=" * 60)
        print(f"User message count : {total_user_messages}")
        print(f"Should update     : {total_user_messages % threshold == 0}")
        print("=" * 60)

        return total_user_messages > 0 and total_user_messages % threshold == 0

    # Redis

    def _load_current_fact_memory(
        self,
        user_id: str,
    ):

        return load_fact_memory(user_id)

    def _save_fact_memory(
        self,
        user_id: str,
        fact_memory: dict,
    ):

        save_fact_memory(
            user_id=user_id,
            fact_memory=fact_memory,
        )

    # MySQL

    def _load_recent_user_messages(
        self,
        conversation_id: int,
    ):

        return self.mysql.get_recent_user_messages(conversation_id)

    # LLM

    async def _generate_fact_memory(
        self,
        current_fact,
        recent_messages,
    ):

        prompt = build_fact_prompt(
            current_fact=current_fact,
            recent_message=recent_messages,
        )

        response = await self.llm.ainvoke(prompt)

        try:
            fact_memory = self.parser.parse(response.content)

            return fact_memory.model_dump()

        except Exception as e:
            print(f"Fact parsing error: {e}")

            return current_fact

    # Pinecone

    def _should_archive_to_pinecone(
        self,
        current_fact: dict,
    ) -> bool:

        if not current_fact:
            return False

        return any(current_fact.values())

    # Main Pipeline

    async def update_memory(
        self,
        user_id: str,
        conversation_id: int,
    ):

        if not self.should_update_memory(
            conversation_id=conversation_id,
            threshold=20,  # Change to 5 while testing===============================================================
        ):
            return

        print("*" * 80)
        print("Long-Term Memory Update Triggered")
        print("*" * 80)

        current_fact = self._load_current_fact_memory(user_id)

        print(current_fact)

        if self._should_archive_to_pinecone(current_fact):
            self.pinecone.archive_fact_memory_to_pinecone(
                user_id=user_id,
                fact_memory=current_fact,
            )

            print("Archived previous fact memory.")

        recent_messages = self._load_recent_user_messages(conversation_id)

        print("Recent Messages:")
        print(recent_messages)

        new_fact = await self._generate_fact_memory(
            current_fact=current_fact,
            recent_messages=recent_messages,
        )

        print("Generated Fact Table:")
        print(new_fact)

        self._save_fact_memory(
            user_id=user_id,
            fact_memory=new_fact,
        )

        print("Fact memory saved.")
