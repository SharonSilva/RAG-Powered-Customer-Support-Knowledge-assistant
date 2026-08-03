from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.services.generation import generate_answer

db = SessionLocal()

test_questions = [
    "Do you offer international shipping to Europe?",
    "Can I ship this product to Germany?",
    "Is shipping available outside the country?",
    "What payment methods do you accept?",
    "Can I pay with PayPal?",
    "What is your CEO's favorite color?",
]

for q in test_questions:
    result = generate_answer(q, db)
    print(f"Q: {q}")
    print(f"   -> {result['answer'][:60]}")

db.close()