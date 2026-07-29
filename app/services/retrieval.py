from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import Chunk
from app.services.embedding import generate_embedding

def retrieve_similar_chunks(query: str, db: Session, top_k: int = 5) -> list[Chunk]:
    """
    Embeds the query and finds the top_k most similar chunks in pgvector
    using cosine distance. Returns Chunk model instances (not raw text),
    so callers have access to document_id, page_number, and section_title
    for citations.
    """
    query_embedding = generate_embedding(query)

    stmt = (
        select(Chunk)
        .order_by(Chunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )

    results = db.execute(stmt).scalars().all()
    return list(results)

def retrieve_candidates_with_distance(query: str, db: Session, top_k: int= 10) -> list[tuple[Chunk, float]]:
    """
    Same as retrieve_similar_chunks, but also returns each chunk's raw
    cosine distance score (lower=more similar). Used by the re-ranking step ,
    which needs the actual distance value , not just chunk order
    """
    
    query_embedding = generate_embedding(query)
    distance_expr = Chunk.embedding.cosine_distance(query_embedding)
    
    stmt =(
        select(Chunk, distance_expr.label("distance"))
        .order_by(distance_expr)
        .limit(top_k)
    )
    
    rows = db.execute(stmt).all()
    return [(row[0], row[1]) for row in rows]
    