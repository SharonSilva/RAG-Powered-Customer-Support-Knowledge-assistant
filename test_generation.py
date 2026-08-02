from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.services.generation import generate_answer

db = SessionLocal()

result = generate_answer("How long do I have to return an item?", db)
print("ANSWER:")
print(result["answer"])
print("\nSOURCES:")
for s in result["sources"]:
    print(s)
db.close() 