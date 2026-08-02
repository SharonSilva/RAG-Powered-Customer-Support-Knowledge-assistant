from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

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

app = FastAPI(title="RAG-powered Customer Support Knowledge Assistant")

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
    
    
        
        
    