import { useMemo, useState } from "react";
import { chatStream, ingestSources, uploadPdfs } from "./api";
import type { Source } from "./types";

const defaultQuery = "Summarize the key signals across my sources.";

export default function App() {
  const [query, setQuery] = useState(defaultQuery);
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<Source[]>([]);
  const [uploadStatus, setUploadStatus] = useState("No PDFs uploaded yet.");
  const [ingestStatus, setIngestStatus] = useState("Waiting on sources.");
  const [loading, setLoading] = useState(false);
  const [gdriveFolderId, setGdriveFolderId] = useState("");
  const [mysqlEnabled, setMysqlEnabled] = useState(false);
  const [mysqlConfig, setMysqlConfig] = useState({
    host: "localhost",
    port: 3306,
    user: "root",
    password: "",
    database: "",
    query: "SELECT * FROM your_table LIMIT 100"
  });
  const [overwrite, setOverwrite] = useState(false);

  const sourceCount = useMemo(() => sources.length, [sources]);

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) {
      return;
    }
    try {
      setUploadStatus("Uploading...");
      const uploaded = await uploadPdfs(files);
      setUploadStatus(`Uploaded ${uploaded.length} PDF(s).`);
    } catch (error) {
      setUploadStatus((error as Error).message);
    }
  };

  const handleIngest = async () => {
    setLoading(true);
    setAnswer("");
    setSources([]);
    try {
      setIngestStatus("Indexing sources...");
      const payload = await ingestSources({
        gdriveFolderId: gdriveFolderId.trim() || undefined,
        mysql: mysqlEnabled ? mysqlConfig : null,
        overwrite
      });
      setIngestStatus(`Indexed ${payload.documents} documents.`);
    } catch (error) {
      setIngestStatus((error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = async () => {
    if (!query.trim()) {
      return;
    }
    setLoading(true);
    setAnswer("");
    setSources([]);

    try {
      await chatStream(
        query,
        (token) => setAnswer((prev) => prev + token),
        (streamSources) => setSources(streamSources)
      );
    } catch (error) {
      setAnswer((error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="hero">
        <div>
          <p className="eyebrow">Complex Sources, Clean Answers</p>
          <h1>LlamaIndex x OpenRouter Control Room</h1>
          <p className="subhead">
            Blend PDFs, Google Drive folders, and live MySQL data into a single
            reasoning surface. Build the index, then interrogate it in real time.
          </p>
        </div>
        <div className="hero-card">
          <h3>Index Pulse</h3>
          <div className="pulse-line">
            <span>Status</span>
            <strong>{ingestStatus}</strong>
          </div>
          <div className="pulse-line">
            <span>Uploads</span>
            <strong>{uploadStatus}</strong>
          </div>
          <div className="pulse-line">
            <span>Sources</span>
            <strong>{sourceCount} snippets</strong>
          </div>
        </div>
      </header>

      <main className="grid">
        <section className="panel sources">
          <h2>Source Pipeline</h2>
          <div className="panel-block">
            <label className="label">PDF uploads</label>
            <input
              className="input"
              type="file"
              accept="application/pdf"
              multiple
              onChange={(event) => handleUpload(event.target.files)}
            />
            <p className="hint">Upload PDFs to seed the index instantly.</p>
          </div>

          <div className="panel-block">
            <label className="label">Google Drive folder ID</label>
            <input
              className="input"
              value={gdriveFolderId}
              onChange={(event) => setGdriveFolderId(event.target.value)}
              placeholder="1AbC..."
            />
            <p className="hint">Make sure OAuth is configured in the backend.</p>
          </div>

          <div className="panel-block mysql">
            <div className="toggle">
              <input
                id="mysql-toggle"
                type="checkbox"
                checked={mysqlEnabled}
                onChange={(event) => setMysqlEnabled(event.target.checked)}
              />
              <label htmlFor="mysql-toggle">Enable MySQL ingestion</label>
            </div>
            {mysqlEnabled && (
              <div className="mysql-grid">
                <input
                  className="input"
                  placeholder="Host"
                  value={mysqlConfig.host}
                  onChange={(event) =>
                    setMysqlConfig({ ...mysqlConfig, host: event.target.value })
                  }
                />
                <input
                  className="input"
                  type="number"
                  placeholder="Port"
                  value={mysqlConfig.port}
                  onChange={(event) =>
                    setMysqlConfig({
                      ...mysqlConfig,
                      port: Number(event.target.value)
                    })
                  }
                />
                <input
                  className="input"
                  placeholder="User"
                  value={mysqlConfig.user}
                  onChange={(event) =>
                    setMysqlConfig({ ...mysqlConfig, user: event.target.value })
                  }
                />
                <input
                  className="input"
                  type="password"
                  placeholder="Password"
                  value={mysqlConfig.password}
                  onChange={(event) =>
                    setMysqlConfig({
                      ...mysqlConfig,
                      password: event.target.value
                    })
                  }
                />
                <input
                  className="input"
                  placeholder="Database"
                  value={mysqlConfig.database}
                  onChange={(event) =>
                    setMysqlConfig({
                      ...mysqlConfig,
                      database: event.target.value
                    })
                  }
                />
                <textarea
                  className="input textarea"
                  placeholder="Query"
                  value={mysqlConfig.query}
                  onChange={(event) =>
                    setMysqlConfig({ ...mysqlConfig, query: event.target.value })
                  }
                />
              </div>
            )}
          </div>

          <div className="panel-block">
            <div className="toggle">
              <input
                id="overwrite-toggle"
                type="checkbox"
                checked={overwrite}
                onChange={(event) => setOverwrite(event.target.checked)}
              />
              <label htmlFor="overwrite-toggle">Overwrite existing index</label>
            </div>
          </div>

          <button className="primary" onClick={handleIngest} disabled={loading}>
            Build Index
          </button>
        </section>

        <section className="panel chat">
          <h2>Ask the Index</h2>
          <textarea
            className="input textarea"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <div className="actions">
            <button className="ghost" onClick={() => setQuery(defaultQuery)}>
              Reset Prompt
            </button>
            <button className="primary" onClick={handleAsk} disabled={loading}>
              Stream Answer
            </button>
          </div>

          <div className="answer">
            <div className="answer-header">
              <span>Response</span>
              {loading && <span className="tag">Working...</span>}
            </div>
            <p>{answer || "No response yet."}</p>
          </div>

          <div className="sources-list">
            <div className="answer-header">
              <span>Top Sources</span>
              <span className="tag">{sourceCount} snippets</span>
            </div>
            <div className="source-grid">
              {sources.map((source) => (
                <article key={source.id} className="source-card">
                  <p className="source-text">{source.text}</p>
                  <div className="source-meta">
                    <span>Score: {source.score?.toFixed(2) ?? "-"}</span>
                    <span>{source.metadata?.source ?? "source"}</span>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
