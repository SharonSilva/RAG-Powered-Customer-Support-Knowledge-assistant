import os
from openai import OpenAI

from sqlalchemy.orm import Session

from app.models import GapRecommendation
from app.services.clustering import cluster_unanswered_queries

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_MODEL="gpt-4o-mini"

def _draft_faq_entry(example_questions: list[str]) -> dict:
    questions_block = "\n".join(f"- {q}" for q in example_questions)
    
    system_prompt = (
         "You help businesses turn customer questions they couldn't answer "
        "into FAQ entries. You will be given several similar customer "
        "questions. Draft ONE clear, general FAQ question that captures "
        "what customers are really asking, and a short placeholder answer "
        "template showing what information the business needs to fill in. "
        "Do NOT invent specific facts, policies, or numbers — you don't "
        "know the real answer. Mark exactly where the business needs to "
        "add real details using [BRACKETS]."
    )
    
    user_prompt = (
        f"Customer questions that couldn't be answered:\n{questions_block}\n\n"
        "Respond in exactly this format:\n"
        "QUESTION: <the FAQ question>\n"
        "ANSWER: <placeholder answer with [BRACKETS] for missing details>"
    )

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0.3,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    
    text = response.choices[0].message.content
    
    question_line = ""
    answer_line = ""
    for line in text.split("\n"):
        if line.startswith("QUESTION:"):
            question_line = line.replace("QUESTION:", "").strip()
        elif line.startswith("ANSWER:"):
            answer_line = line.replace("ANSWER:", "").strip()
            
    return {"suggested_question": question_line, "suggested_answer": answer_line}

def generate_recommendations(db: Session) -> list[GapRecommendation]:
    clusters = cluster_unanswered_queries(db)
    
    existing_topics ={
        row.topic for row in db.query(GapRecommendation.topic).all()
    }
    
    new_recommendation = []
    
    for cluster in clusters:
        if cluster["representative_question"] in existing_topics:
            continue
        
        draft = _draft_faq_entry(cluster["questions"])
        
        recommendation = GapRecommendation(
            topic=cluster["representative_question"],
            example_questions="\n".join(cluster["questions"]),
            times_asked=cluster["count"],
            suggested_question=draft["suggested_question"],
            suggested_answer=draft["suggested_answer"],
            status="pending",
        )
        db.add(recommendation)
        new_recommendation.append(recommendation)
        
    db.commit()
    
    return new_recommendation