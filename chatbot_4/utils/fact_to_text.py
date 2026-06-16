# def fact_to_text(fact: dict) -> str:

#     lines = []

#     for category, values in fact.items():

#         if not values:
#             continue

#         lines.append(f"{category.replace('_', ' ').title()}:")

#         for value in values:
#             lines.append(f"- {value}")

#         lines.append("")

#     return "\n".join(lines)


def fact_to_text(fact_memory: dict) -> str:

    MEMORY_FIELDS = [
        "career_goals",
        "preferences",
        "skills",
        "projects",
        "current_focus",
    ]

    text = ""

    for key in MEMORY_FIELDS:

        values = fact_memory.get(key, [])

        if not values:
            continue

        text += f"{key.replace('_', ' ').title()}:\n"

        for value in values:
            text += f"- {value}\n"

        text += "\n"

    return text