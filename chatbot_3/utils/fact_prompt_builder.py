from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from schema.fact_schema import FactMemory

parser = PydanticOutputParser(
    pydantic_object=FactMemory  # push the whole class.not any object of the class.
)


def build_fact_prompt(current_fact: list[str], recent_message: str):

    fact_prompts = PromptTemplate(
        template="""You are an AI memory manager.Your job is NOT to answer the user.Your job is to update the user's long-term memory.
        Rules:
        - Keep only information useful in future conversations.
        - Ignore greetings.
        - Ignore temporary questions.
        - Ignore one-time requests.
        - Update existing facts if they changed.
        - Remove outdated facts.
        - Return ONLY JSON.
        to make this facts we can use this user recent message {recent_message} 
        and also we can have the previous fact table {current_fact}
        and must use this format \n{fact_table_format}""",
        input_variables=["current_fact", "recent_message"],
        partial_variables={"fact_table_format": parser.get_format_instructions()},
    )

    return fact_prompts.format(current_fact=current_fact, recent_message=recent_message)
