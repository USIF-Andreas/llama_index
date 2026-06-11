from __future__ import annotations

import io
from pathlib import Path
from typing import List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from .config import get_settings

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_credentials() -> Credentials:
    settings = get_settings()
    settings.google_token.parent.mkdir(parents=True, exist_ok=True)

    creds = None
    if settings.google_token.exists():
        creds = Credentials.from_authorized_user_file(str(settings.google_token), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not settings.google_client_secret.exists():
                raise FileNotFoundError(
                    f"Missing Google client secret at {settings.google_client_secret}. "
                    "Run scripts/gdrive_oauth.py to create token.json."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(settings.google_client_secret),
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        settings.google_token.write_text(creds.to_json())

    return creds


def download_pdfs(folder_id: str, target_dir: Path) -> List[Path]:
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)
    target_dir.mkdir(parents=True, exist_ok=True)

    query = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    files = results.get("files", [])

    downloaded: List[Path] = []
    for file_info in files:
        file_id = file_info["id"]
        name = file_info["name"]
        out_path = target_dir / name

        request = service.files().get_media(fileId=file_id)
        with io.FileIO(out_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        downloaded.append(out_path)

    return downloaded
