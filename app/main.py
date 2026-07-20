from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document, Chunk
from app.services.parsing import extract_text_from_pdf
from app.services.chunking import chunk_pages
from app.services.embedding import generate_embeddings_batch
from app.services.docx_parsing import extract_text_from_docx

app = FastAPI(title="RAG-Powered Customer Support Knowledge Assistant")


@app.get("/health")
def health_check():
    return {"status": "ok"}

def _parse_by_filetype(filename: str, file_bytes: bytes) -> list[dict]:
    lower_name = filename.lower()

    if lower_name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif lower_name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF or DOCX file.",
        )


@app.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_bytes = await file.read()

    pages = _parse_by_filetype(file.filename, file_bytes)
    chunks = chunk_pages(pages)

    chunk_texts = [c["content"] for c in chunks]
    embeddings = generate_embeddings_batch(chunk_texts)

    document = Document(filename=file.filename)
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

    return {
        "filename": file.filename,
        "document_id": document.id,
        "num_chunks": len(chunks),
    }
