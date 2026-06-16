from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


def build_langchain_messages(
    history,
    recent_fact_table,
    retrieved_facts,
):

    messages = []

    # Original System Prompt
    system_prompt = " "

    for msg in history:
        if msg["role"] == "system":
            system_prompt = msg["content"]

            break

    if recent_fact_table:
        system_prompt += "\n\nCurrent User Memory:\n"

        MEMORY_FIELDS = [
            "career_goals",
            "preferences",
            "skills",
            "projects",
            "current_focus",
        ]

        for key in MEMORY_FIELDS:
            values = recent_fact_table.get(key, [])

            if not values:
                continue

            system_prompt += f"\n{key.replace('_', ' ').title()}:\n"

            for value in values:
                system_prompt += f"- {value}\n"

    # add returieved facts from vector data base .
    if retrieved_facts:
        system_prompt += "\n\nRelevant Past Memories:\n"

        for fact in retrieved_facts:
            system_prompt += f"\n{fact}\n"

    system_prompt += """

        Use the Current User Profile as the user's latest persistent profile.

        Use the Retrieved Historical Memories only when they are relevant to the user's current request.

        Do not mention these memories unless they help answer the question.

        """

    # now all the system messge_facts in one messge.
    messages.append(SystemMessage(content=system_prompt))

    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))

        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

        elif msg["role"] == "system":  # already added .
            continue

    return messages
