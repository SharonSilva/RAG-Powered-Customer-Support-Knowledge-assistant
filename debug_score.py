from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.services.retrieval import retrieve_candidates_with_distance
from app.services.reranking import rerank_with_scores

db = SessionLocal()

candidates = retrieve_candidates_with_distance("How long do I have to return an item?", db, top_k=10)
scored = rerank_with_scores("How long do I have to return an item?", candidates, top_k=5)

for chunk, score in scored:
    print(f"score={score:.3f} section={chunk.section_title!r}")
    
db.close()