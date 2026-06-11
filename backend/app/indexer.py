from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import faiss
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.schema import Document

from .config import get_settings
from .openrouter import get_embedding_model


def _index_dir() -> Path:
    settings = get_settings()
    index_dir = settings.data_dir / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    return index_dir


def _uploads_dir() -> Path:
    settings = get_settings()
    uploads_dir = settings.data_dir / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    return uploads_dir


def get_uploads_dir() -> Path:
    return _uploads_dir()


def _build_vector_store() -> FaissVectorStore:
    embed_model = get_embedding_model()
    dim = len(embed_model.get_text_embedding("dimension probe"))
    faiss_index = faiss.IndexFlatL2(dim)
    return FaissVectorStore(faiss_index=faiss_index)


def load_or_create_index() -> VectorStoreIndex:
    index_dir = _index_dir()
    vector_store_path = index_dir / "docstore.json"

    if vector_store_path.exists():
        vector_store = FaissVectorStore.from_persist_path(str(index_dir))
        storage_context = StorageContext.from_defaults(
            persist_dir=str(index_dir),
            vector_store=vector_store,
        )
        return load_index_from_storage(storage_context, embed_model=get_embedding_model())

    vector_store = _build_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex([], storage_context=storage_context,embed_model = get_embedding_model())


def persist_index(index: VectorStoreIndex) -> None:
    index_dir = _index_dir()
    index.storage_context.persist(persist_dir=str(index_dir))


def index_from_documents(documents: List[Document], overwrite: bool) -> VectorStoreIndex:
    if overwrite:
        vector_store = _build_vector_store()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            embed_model=get_embedding_model(),
        )
        persist_index(index)
        return index

    index = load_or_create_index()
    if documents:
        for doc in documents:
            index.insert(doc, embed_model=get_embedding_model())
        persist_index(index)
    return index


def read_pdf_documents(paths: Iterable[Path]) -> List[Document]:
    docs: List[Document] = []
    for path in paths:
        if path.is_dir():
            docs.extend(
                SimpleDirectoryReader(str(path), required_exts=[".pdf"]).load_data()
            )
        elif path.suffix.lower() == ".pdf":
            docs.extend(SimpleDirectoryReader(str(path.parent), required_exts=[".pdf"]).load_data())
            break

    return docs
