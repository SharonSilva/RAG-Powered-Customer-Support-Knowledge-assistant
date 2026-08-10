from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request
from fastapi.responses import JSONResponse
import os
from fastapi.middleware.cors import CORSMiddleware

from app.database import get_db
from app.models import Document, Chunk
from app.services.parsing import extract_text_from_pdf
from app.services.docx_parsing import extract_text_from_docx
from app.services.markdown_parsing import extract_text_from_markdown
from app.services.url_parsing import fetch_and_extract_text_from_url
from app.services.chunking import chunk_pages
from app.services.embedding import generate_embeddings_batch
from app.services.retrieval import retrieve_similar_chunks, retrieve_candidates_with_distance
from app.services.reranking import rerank
from app.services.generation import generate_answer
from app.services.clustering import cluster_unanswered_queries
from app.services.recommendations import generate_recommendations
from app.services.impact_analytics import get_summary, get_daily_trend
from app.models import QueryLog
from app.services.health_score import compute_health_score
from app.models import GapRecommendation

app = FastAPI(title="RAG-powered Customer Support Knowledge Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://rag-powered-customer-support-knowledge-assistant-q3yoy5x98.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("API_KEY")


@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.method == "OPTIONS" or request.url.path == "/health":
        return await call_next(request)

    if not API_KEY or request.headers.get("x-api-key") != API_KEY:
        return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})

    return await call_next(request)

@app.get("/health")
def health_check():
    return {"status": "ok"}

def _parse_by_filetype(filename: str, file_bytes: bytes) -> list[dict]:
    lower_name = filename.lower()
    
    if lower_name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif lower_name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif lower_name.endswith(".md"):
        return extract_text_from_markdown(file_bytes)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type.Please upload a PDF, DOCX , or Markdown file",
        )
        
class QueryRequest(BaseModel):
    question: str
    category: Optional[str] = None
    
@app.post("/query")
async def query(payload:QueryRequest, db:Session = Depends(get_db)):
    candidates = retrieve_candidates_with_distance(payload.question, db, top_k=10, category=payload.category)
    chunks = rerank(payload.question, candidates, top_k=5)
    
    return {
        "question": payload.question,
        "category_filter": payload.category,
        "results":[
            {
                "document_id": c.document_id,
                "section_title": c.section_title,
                "page_number": c.page_number,
                "content": c.content,
            }
            for c in chunks
        ],
    }
    
class AskRequest(BaseModel):
    question: str
    category: Optional[str] = None

@app.post("/ask")
async def ask(payload: AskRequest, db: Session = Depends(get_db)):
    result = generate_answer(payload.question, db, category=payload.category)
    return result


class UrlIngestRequest(BaseModel):
    url: str
    category: Optional[str] = None
    
@app.post("/ingest-url")
async def ingest_url(payload: UrlIngestRequest, db: Session = Depends(get_db)):
    try:
        pages = fetch_and_extract_text_from_url(payload.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch URL:{str(e)}")
    
    chunks = chunk_pages(pages)
    chunk_texts = [c["content"] for c in chunks]
    embeddings = generate_embeddings_batch(chunk_texts)
    
    document = Document(filename=payload.url, category=payload.category)
    db.add(document)
    db.flush()
    
    for chunk_data, embedding in zip(chunks, embeddings):
        chunk_row = Chunk(
            document_id = document.id,
            content=chunk_data["content"],
            embedding=embedding,
            page_number=chunk_data["page_number"],
            section_title=chunk_data["section_title"],
        )
        db.add(chunk_row)
        
    db.commit()
    
    return{
        "source_url": payload.url,
        "document_id": document.id,
        "category": document.category,
        "num_chunks": len(chunks),
    }
    
class FeedbackRequest(BaseModel):
    feedback: str


@app.patch("/query-logs/{query_log_id}/feedback")
async def submit_feedback(query_log_id: int, payload: FeedbackRequest, db: Session = Depends(get_db)):
    if payload.feedback not in {"up", "down"}:
        raise HTTPException(status_code=400, detail="feedback must be 'up' or 'down'")

    log = db.query(QueryLog).filter(QueryLog.id == query_log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Query log not found")

    log.feedback = payload.feedback
    if payload.feedback == "down":
        log.flagged = True

    db.commit()

    return {"id": log.id, "feedback": log.feedback, "flagged": log.flagged}


@app.get("/analytics/flagged")
async def list_flagged_queries(db: Session = Depends(get_db)):
    logs = (
        db.query(QueryLog)
        .filter(QueryLog.flagged == True)
        .order_by(QueryLog.created_at.desc())
        .all()
    )

    return {
        "flagged_queries": [
            {
                "id": log.id,
                "question": log.question,
                "answered": log.answered,
                "top_score": log.top_score,
                "feedback": log.feedback,
                "created_at": log.created_at,
            }
            for log in logs
        ],
    }


@app.get("/analytics/summary")
async def get_analytics_summary(db: Session = Depends(get_db)):
    summary = get_summary(db)
    trend = get_daily_trend(db)
    health = compute_health_score(db)

    return {
        "overall": summary,
        "daily_trend": trend,
        "health_score": health,
    }


@app.get("/analytics/gaps")
async def get_knowledge_gaps(db: Session = Depends(get_db)):
    clusters = cluster_unanswered_queries(db)

    return {
        "total_gap_clusters": len(clusters),
        "gaps": [
            {
                "topic": cluster["representative_question"],
                "times_asked": cluster["count"],
                "example_questions": cluster["questions"],
                "last_seen": cluster["last_seen"],
            }
            for cluster in clusters
        ],
    }


@app.post("/analytics/recommendations/generate")
async def generate_gap_recommendations(db: Session = Depends(get_db)):
    new_recs = generate_recommendations(db)

    return {
        "new_recommendations": len(new_recs),
        "recommendations": [
            {
                "id": r.id,
                "topic": r.topic,
                "times_asked": r.times_asked,
                "suggested_question": r.suggested_question,
                "suggested_answer": r.suggested_answer,
                "status": r.status,
            }
            for r in new_recs
        ],
    }


@app.get("/analytics/recommendations")
async def list_gap_recommendations(status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(GapRecommendation)
    if status:
        query = query.filter(GapRecommendation.status == status)

    recs = query.order_by(GapRecommendation.times_asked.desc()).all()

    return {
        "recommendations": [
            {
                "id": r.id,
                "topic": r.topic,
                "times_asked": r.times_asked,
                "suggested_question": r.suggested_question,
                "suggested_answer": r.suggested_answer,
                "status": r.status,
                "created_at": r.created_at,
            }
            for r in recs
        ],
    }


class RecommendationStatusUpdate(BaseModel):
    status: str


@app.patch("/analytics/recommendations/{recommendation_id}")
async def update_recommendation_status(
    recommendation_id: int, payload: RecommendationStatusUpdate, db: Session = Depends(get_db)
):
    if payload.status not in {"approved", "rejected"}:
        raise HTTPException(status_code=400, detail="status must be 'approved' or 'rejected'")

    rec = db.query(GapRecommendation).filter(GapRecommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.status = payload.status
    db.commit()

    return {"id": rec.id, "status": rec.status}


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()
    
    pages = _parse_by_filetype(file.filename, file_bytes)
    chunks = chunk_pages(pages)
    
    chunk_texts = [c["content"] for c in chunks]
    embeddings = generate_embeddings_batch(chunk_texts)
    
    document = Document(filename=file.filename, category=category)
    db.add(document)
    db.flush()
    
    for chunk_data, embedding in zip(chunks, embeddings):
        chunk_row = Chunk(
            document_id=document.id,
            content=chunk_data["content"],
            embedding=embedding,
            page_number=chunk_data["page_number"],
            section_title=chunk_data["section_title"],
        )
        db.add(chunk_row)
        
    db.commit()
    
    return{
        "filename":file.filename,
        "document_id": document.id,
        "category": document.category,
        "num_chunks" : len(chunks),
    }