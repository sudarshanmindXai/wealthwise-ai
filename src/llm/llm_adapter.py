def generate_user_explanation(explanation_lines):
    """
    Converts deterministic explanation points into a single or in pointers as
    user-friendly paragraph using an LLM later.
    For now, we keep it simple and deterministic.
    """

    return " ".join(explanation_lines)


def generate_followup_questions(missing_info):
    """
    Converts missing information into user-friendly questions.
    """

    questions = []

    for r in missing_info.get("required", []):
        questions.append(f"Please provide details for {r}.")

    for o in missing_info.get("optional", []):
        questions.append(
            f"If available, you may also share details about {o} to optimise your tax."
        )

    return questions

