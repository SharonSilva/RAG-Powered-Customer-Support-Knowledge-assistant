from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.services.recommendations import generate_recommendations

db = SessionLocal()

recommendations = generate_recommendations(db)

print(f"Generated {len(recommendations)} new recommendation(s):\n")
for r in recommendations:
    print(f"Topic: {r.topic}")
    print(f"  Times asked: {r.times_asked}")
    print(f"  Suggested Q: {r.suggested_question}")
    print(f"  Suggested A: {r.suggested_answer}")
    print(f"  Status: {r.status}")
    print()

db.close()
