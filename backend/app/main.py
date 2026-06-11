from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from llama_index.core.query_engine import CitationQueryEngine

from .config import get_settings
from .gdrive import download_pdfs
from .indexer import get_uploads_dir, index_from_documents, load_or_create_index
from .models import ChatRequest, IngestRequest
from .mysql_reader import mysql_documents
from .openrouter import get_embedding_model, get_llm

from llama_index.core import Settings

app = FastAPI(title="LlamaIndex OpenRouter API")
settings = get_settings()

# Set global settings
Settings.llm = get_llm()
Settings.embed_model = get_embedding_model()

cors_origins_str = settings.cors_origins
if cors_origins_str == "*":
    allow_origins = ["*"]
    allow_credentials = False
else:
    allow_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/index/upload")
async def upload_files(files: List[UploadFile] = File(...)) -> dict:
    uploads_dir = get_uploads_dir()
    saved = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        out_path = uploads_dir / Path(file.filename).name
        content = await file.read()
        out_path.write_bytes(content)
        saved.append(out_path.name)

    return {"uploaded": saved}


@app.post("/api/index/ingest")
def ingest_sources(payload: IngestRequest) -> dict:
    documents = []

    uploads_dir = get_uploads_dir()
    if list(uploads_dir.glob("*.pdf")):
        documents.extend(_pdf_documents([uploads_dir]))

    if payload.gdrive_folder_id:
        gdrive_dir = settings.data_dir / "gdrive"
        pdfs = download_pdfs(payload.gdrive_folder_id, gdrive_dir)
        if pdfs:
            documents.extend(_pdf_documents(pdfs))

    if payload.mysql:
        mysql_docs = mysql_documents(
            host=payload.mysql.host,
            port=payload.mysql.port,
            user=payload.mysql.user,
            password=payload.mysql.password,
            database=payload.mysql.database,
            query=payload.mysql.query,
        )
        documents.extend(mysql_docs)

    if not documents:
        raise HTTPException(status_code=400, detail="No documents found to ingest")

    index_from_documents(documents, overwrite=payload.overwrite)
    return {"status": "indexed", "documents": len(documents)}


@app.post("/api/chat")
def chat(payload: ChatRequest) -> dict:
    index = load_or_create_index()
    query_engine = CitationQueryEngine.from_args(
        index,
        llm=get_llm(),
        embed_model=get_embedding_model(),
        similarity_top_k=4,
        citation_chunk_size=512,
    )

    response = query_engine.query(payload.query)
    sources = [
        {
            "id": node.node.node_id,
            "score": node.score,
            "text": node.node.get_content(),
            "metadata": node.node.metadata,
        }
        for node in response.source_nodes
    ]

    return {"answer": str(response), "sources": sources}


@app.post("/api/chat/stream")
def chat_stream(payload: ChatRequest):
    index = load_or_create_index()
    query_engine = CitationQueryEngine.from_args(
        index,
        llm=get_llm(),
        embed_model=get_embedding_model(),
        similarity_top_k=4,
        citation_chunk_size=512,
        streaming=True,
    )

    response = query_engine.query(payload.query)

    def event_stream():
        try:
            tokens_sent = False
            if response.response_gen:
                for token in response.response_gen:
                    escape_token = token.replace("\n", "\\n").replace("\r", "\\r")
                    yield f"data: {escape_token}\n\n"
                    tokens_sent = True
            if not tokens_sent:
                full_response = str(response)
                if full_response:
                    escape_response = full_response.replace("\n", "\\n").replace("\r", "\\r")
                    yield f"data: {escape_response}\n\n"
                    else:
                        yield f"data: no rev \n\n"
        except Exception as e:
            error_message = f"Error during streaming: {str(e)}"
            yield f"data: {error_message}\n\n"
        
        sources = [
            {
                "id": node.node.node_id,
                "score": node.score,
                "text": node.node.get_content(),
                "metadata": node.node.metadata,
            }
            for node in response.source_nodes
        ]
        yield "event: sources\n"
        yield f"data: {json.dumps(sources, ensure_ascii=True)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _pdf_documents(paths: Iterable[Path]):
    from .indexer import read_pdf_documents

    return read_pdf_documents(paths)
