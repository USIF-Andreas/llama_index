from typing import List, Optional
from pydantic import BaseModel, Field


class MySQLConfig(BaseModel):
    host: str
    port: int = 3306
    user: str
    password: str
    database: str
    query: str = Field(default="SELECT * FROM your_table LIMIT 100")


class IngestRequest(BaseModel):
    gdrive_folder_id: Optional[str] = None
    mysql: Optional[MySQLConfig] = None
    overwrite: bool = False


class ChatRequest(BaseModel):
    query: str
