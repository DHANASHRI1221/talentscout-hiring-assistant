import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_questions(text):

    questions = []

    for line in text.split("\n"):
        line = line.strip()

        if line.startswith(("1.","2.","3.","4.","5.")):
            questions.append(line)

    return questions


def parse_evaluation(text):

    score_match = re.search(r"Score[: ]+(\d+)", text)
    sentiment_match = re.search(r"Sentiment[: ]+(Confident|Neutral|Uncertain)", text)
    feedback_match = re.search(r"Feedback[: ]+(.*)", text)

    score = score_match.group(1) if score_match else "0"
    sentiment = sentiment_match.group(1) if sentiment_match else "Unknown"
    feedback = feedback_match.group(1) if feedback_match else text

    return score, sentiment, feedback


# ---------- Originality / Similarity Check ----------

def check_similarity(answer, reference_text):

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform([answer, reference_text])

    similarity = cosine_similarity(vectors)[0][1]

    similarity_percentage = round(similarity * 100, 2)

    originality_score = round(100 - similarity_percentage, 2)

    return originality_score