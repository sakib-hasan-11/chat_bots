from core.model_loader import llm
from core.mysql_loader import MySQLService as mysql
from langchain_core.output_parsers import PydanticOutputParser
from schema.fact_schema import FactMemory
from utils.fact_prompt_builder import build_fact_prompt

from services.redis_services import load_fact_memory, save_fact_memory


class LongTermMemoryService:
    def __init__(self):
        self.llm = llm
        self.mysql = mysql()
        self.parser = PydanticOutputParser(  # validate llm output .
            pydantic_object=FactMemory
        )

    # public modules
    def should_update_memory(
        self,
        conversation_id: int,
    ) -> bool:

        total_user_messages = self.mysql.count_user_messages(conversation_id)

        return total_user_messages > 0 and total_user_messages % 20 == 0

    # private modules
    def _load_current_fact_memory(
        self,
        user_id: str,
    ):

        return load_fact_memory(user_id)

    def _load_recent_user_messages(
        self,
        conversation_id: int,
    ):

        return self.mysql.get_recent_user_messages(conversation_id)

    def _save_fact_memory(
        self,
        user_id: str,
        fact_memory: dict,
    ):

        save_fact_memory(
            user_id=user_id,
            fact_memory=fact_memory,
        )

    async def _generate_fact_memory(
        self,
        current_fact,
        recent_messages,
    ):

        prompt = build_fact_prompt(
            current_fact=current_fact,
            recent_message=recent_messages,
        )

        response = await self.llm.ainvoke(
            prompt
        )  # this return the pydantic validate output
        try:
            fact_memory = (
                self.parser.parse(  # here we again validate to ensure more consistancy.
                    response.content
                )
            )
        except Exception as e:
            print(f"fact memory parsing error : {e}")

        return fact_memory.model_dump()

    # public mosule
    async def update_memory(
        self,
        user_id: str,
        conversation_id: int,
    ):
        if not self.should_update_memory(
            conversation_id=conversation_id
        ):  # should update fucntion true return na korle just return do nothing.
            return
        print("*" * 100)
        print("long term memory update triggered")
        print("*" * 100)
        current_fact = self._load_current_fact_memory(user_id)
        print(f"current_fact:{current_fact}")
        print("*" * 100)
        recent_messages = self._load_recent_user_messages(conversation_id)

        new_fact = await self._generate_fact_memory(
            current_fact=current_fact,
            recent_messages=recent_messages,
        )

        print("*" * 100)
        print(new_fact)

        self._save_fact_memory(
            user_id=user_id,
            fact_memory=new_fact,
        )

        print("fact memory saved")
