from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document, Chunk
from app.services.parsing import extract_text_from_pdf
from app.services.chunking import chunk_text
from app.services.embedding import generate_embeddings_batch

app = FastAPI(title="RAG-Powered Customer Support Knowledge Assistant")

@app.get("/health")
def health_check():
    return {"status":"ok"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session =
Depends(get_db)):
    file_bytes = await file.read()
    
    text = extract_text_from_pdf(file_bytes)
    chunks = chunk_text(text)
    embeddings = generate_embeddings_batch(chunks)
    
    document = Document(filename=file.filename)
    db.add(document)
    db.flush() #assign document.id without committing yet
    
    for chunk_content, embedding in zip(chunks, embeddings):
        chunk_row = Chunk(
            document_id=document.id,
            content=chunk_content,
            embedding=embedding,
        )
        db.add(chunk_row)
    db.commit()
    
    return{
        "filename": file.filename,
        "document_id": document.id,
        "num_chunks": len(chunks),
    }
    