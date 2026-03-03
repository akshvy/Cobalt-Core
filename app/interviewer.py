from typing import List, Dict

# stub functions for AI interaction
def next_question(role: str, resume_data: dict) -> str:
    # In a real implementation we would call the AI engine
    # to generate a question based on the role and resume.
    return f"Can you describe your experience relevant to {role}?"


def evaluate_answer(answer: str, history: List[Dict]) -> dict:
    # Dummy evaluation: count words, check for keywords
    score = len(answer.split())
    feedback = "Good" if score > 5 else "Try to elaborate more"
    return {"score": score, "feedback": feedback}
