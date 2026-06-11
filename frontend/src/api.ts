import type { Source } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export async function uploadPdfs(files: FileList): Promise<string[]> {
  const data = new FormData();
  Array.from(files).forEach((file) => data.append("files", file));

  const response = await fetch(`${API_BASE}/api/index/upload`, {
    method: "POST",
    body: data
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  const payload = await response.json();
  return payload.uploaded ?? [];
}

export async function ingestSources(payload: {
  gdriveFolderId?: string;
  mysql?: {
    host: string;
    port: number;
    user: string;
    password: string;
    database: string;
    query: string;
  } | null;
  overwrite: boolean;
}): Promise<{ documents: number }>
{
  const response = await fetch(`${API_BASE}/api/index/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      gdrive_folder_id: payload.gdriveFolderId || null,
      mysql: payload.mysql || null,
      overwrite: payload.overwrite
    })
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json();
}

export async function chatOnce(query: string): Promise<{ answer: string; sources: Source[] }> {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query })
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json();
}

export async function chatStream(
  query: string,
  onToken: (token: string) => void,
  onSources: (sources: Source[]) => void
): Promise<void> {
  const response = await fetch(`${API_BASE}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query })
  });

  if (!response.ok || !response.body) {
    throw new Error(await response.text());
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let currentEvent: string | null = null;

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("event:")) {
        currentEvent = line.replace("event:", "").trim();
        continue;
      }
      if (line.startsWith("data:")) {
        const data = line.replace("data:", "");
        if (currentEvent === "sources") {
          onSources(JSON.parse(data));
          currentEvent = null;
        } else {
          onToken(data);
        }
      }
    }
  }
}
