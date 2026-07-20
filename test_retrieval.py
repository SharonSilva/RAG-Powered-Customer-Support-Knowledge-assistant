from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.services.retrieval import retrieve_similar_chunks

db = SessionLocal()
results = retrieve_similar_chunks("How long do I have to return an item?", db, top_k=3)

for r in results:
    print(f"[doc {r.document_id}] section={r.section_title!r} page={r.page_number}")
    print(r.content)
    print("---")

db.close()
