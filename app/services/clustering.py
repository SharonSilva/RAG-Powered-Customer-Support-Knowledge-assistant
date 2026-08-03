from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import QueryLog

SIMILARITY_THRESHOLD = 0.50


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def cluster_unanswered_queries(db: Session, similarity_threshold: float = SIMILARITY_THRESHOLD) -> list[dict]:
    """
    Groups unanswered (fallback-triggering) queries by semantic similarity,
    using simple greedy clustering: each query either joins an existing
    cluster if it's similar enough to that cluster's first question, or
    starts a new cluster.

    Returns clusters sorted by size (most common gaps first), each with:
    - representative_question: the first question in the cluster
    - count: how many times this topic came up
    - questions: all the actual questions in the cluster
    - last_seen: most recent timestamp in the cluster
    """
    stmt = (
        select(QueryLog)
        .where(QueryLog.answered == False)  # noqa: E712
        .where(QueryLog.embedding.is_not(None))
        .order_by(QueryLog.created_at.desc())
    )
    logs = db.execute(stmt).scalars().all()

    clusters: list[dict] = []

    for log in logs:
        placed = False

        for cluster in clusters:
            similarity = _cosine_similarity(log.embedding, cluster["_representative_embedding"])
            if similarity >= similarity_threshold:
                cluster["questions"].append(log.question)
                cluster["count"] += 1
                if log.created_at > cluster["last_seen"]:
                    cluster["last_seen"] = log.created_at
                placed = True
                break

        if not placed:
            clusters.append({
                "representative_question": log.question,
                "count": 1,
                "questions": [log.question],
                "last_seen": log.created_at,
                "_representative_embedding": log.embedding,
            })

    clusters.sort(key=lambda c: c["count"], reverse=True)

    for cluster in clusters:
        del cluster["_representative_embedding"]

    return clusters
