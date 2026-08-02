from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.services.generation import generate_answer

db = SessionLocal()

result = generate_answer("What is your company's stock price?", db)
print("ANSWER:")
print(result["answer"])
print("SOURCES:", result["sources"])

db.close()
