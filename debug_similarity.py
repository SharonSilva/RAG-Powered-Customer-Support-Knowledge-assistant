from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.models import QueryLog
from app.services.clustering import _cosine_similarity

db = SessionLocal()

logs = db.query(QueryLog).filter(QueryLog.answered == False).order_by(QueryLog.id).all()

for i in range(len(logs)):
    for j in range(i + 1, len(logs)):
        sim = _cosine_similarity(logs[i].embedding, logs[j].embedding)
        if sim > 0.5:
            print(f"{sim:.3f}  |  {logs[i].question!r}  <->  {logs[j].question!r}")

db.close()