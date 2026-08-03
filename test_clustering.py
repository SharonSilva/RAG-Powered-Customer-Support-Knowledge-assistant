from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.services.clustering import cluster_unanswered_queries

db = SessionLocal()

clusters = cluster_unanswered_queries(db)

for i, cluster in enumerate(clusters, start=1):
    print(f"Cluster {i}: {cluster['count']} question(s)")
    print(f"  Representative: {cluster['representative_question']}")
    for q in cluster['questions']:
        print(f"    - {q}")
    print()

db.close()