import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def main():
    base_dir = Path(__file__).resolve().parents[1]
    data_dir = base_dir / ".." / "data"
    secret = data_dir / "google" / "client_secret.json"
    token = data_dir / "google" / "token.json"

    if not secret.exists():
        raise FileNotFoundError(f"Missing {secret}")

    flow = InstalledAppFlow.from_client_secrets_file(str(secret), SCOPES)
    creds = flow.run_local_server(port=0)

    token.parent.mkdir(parents=True, exist_ok=True)
    token.write_text(creds.to_json())
    print(f"Saved token to {token}")


if __name__ == "__main__":
    main()
