import os
from openai import OpenAI

from sqlalchemy.orm import Session

from app.models import QueryLog
from app.services.retrieval import retrieve_candidates_with_distance
from app.services.reranking import rerank_with_scores
from app.services.embedding import generate_embedding

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_MODEL = "gpt-4o-mini"

CONFIDENCE_THRESHOLD = 0.35

FALLBACK_MESSAGE = "I don't have information on that in the knowledge base."


def _build_context(scored_chunks: list[tuple]) -> str:
    lines = []
    for i, (chunk, score) in enumerate(scored_chunks, start=1):
        section = chunk.section_title or "Untitled section"
        lines.append(f"[{i}] ({section})\n{chunk.content}")

    return "\n\n".join(lines)


def _log_query(
    db: Session,
    query: str,
    query_embedding: list[float],
    category: str | None,
    top_score: float | None,
    answered: bool,
    session_id: str | None = None,
) -> int:
    log_row = QueryLog(
        question=query,
        embedding=query_embedding,
        category=category,
        top_score=top_score,
        answered=answered,
        session_id=session_id,
    )
    db.add(log_row)
    db.commit()
    db.refresh(log_row)
    return log_row.id


def generate_answer(
    query: str, db: Session, category: str | None = None, session_id: str | None = None
) -> dict:
    query_embedding = generate_embedding(query)
    candidates = retrieve_candidates_with_distance(
        query, db, top_k=10, category=category, query_embedding=query_embedding
    )

    if not candidates:
        log_id = _log_query(db, query, query_embedding, category, None, answered=False, session_id=session_id)
        return {"answer": FALLBACK_MESSAGE, "sources": [], "query_log_id": log_id, "confidence": None}

    scored_chunks = rerank_with_scores(query, candidates, top_k=5)
    top_score = scored_chunks[0][1]

    if top_score < CONFIDENCE_THRESHOLD:
        log_id = _log_query(db, query, query_embedding, category, top_score, answered=False, session_id=session_id)
        return {"answer": FALLBACK_MESSAGE, "sources": [], "query_log_id": log_id, "confidence": round(top_score, 2)}

    context = _build_context(scored_chunks)

    system_prompt = (
        "You are a customer support assistant. Answer the user's question "
        "using ONLY the information in the provided context. "
        "Cite the source of every claim using its bracketed number, e.g. [1]. "
        "If the context does not contain enough information to answer, say "
        "you don't have information on that  do not guess or use outside knowledge."
    )

    user_prompt = f"Context:\n{context}\n\nQuestion: {query}"

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    answer_text = response.choices[0].message.content

    sources = [
        {
            "ref": i,
            "document_id": chunk.document_id,
            "section_title": chunk.section_title,
            "page_number": chunk.page_number,
        }
        for i, (chunk, score) in enumerate(scored_chunks, start=1)
    ]

    log_id = _log_query(db, query, query_embedding, category, top_score, answered=True, session_id=session_id)

    return {
        "answer": answer_text,
        "sources": sources,
        "query_log_id": log_id,
        "confidence": round(top_score, 2),
    }
