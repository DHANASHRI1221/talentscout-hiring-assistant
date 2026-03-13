def generate_question_prompt(tech_stack):

    return f"""
You are an experienced technical interviewer.

Candidate Tech Stack:
{tech_stack}

Generate exactly 3 technical interview questions for EACH technology.

Format:

Technology: <Technology Name>
1. Question
2. Question
3. Question
"""


def evaluate_answer_prompt(question, answer):

    return f"""
You are evaluating a candidate answer.

Question:
{question}

Answer:
{answer}

Evaluate correctness, clarity and understanding.

Return format:

Score: <0-10>
Sentiment: Confident / Neutral / Uncertain
Feedback: short explanation
"""