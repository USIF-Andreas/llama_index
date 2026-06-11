from typing import Iterable, List
import json

from sqlalchemy import create_engine, text
from llama_index.core import Document


def mysql_documents(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    query: str,
) -> List[Document]:
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(url)

    docs: List[Document] = []
    with engine.connect() as connection:
        result = connection.execute(text(query))
        for row in result.mappings():
            row_dict = dict(row)
            docs.append(
                Document(
                    text=json.dumps(row_dict, ensure_ascii=True),
                    metadata={"source": "mysql", "database": database},
                )
            )

    return docs
