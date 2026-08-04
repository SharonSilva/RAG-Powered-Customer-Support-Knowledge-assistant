import { useState, useRef } from "react";
import { uploadDocument } from "../api";
import "./UploadPanel.css";

const CATEGORIES = ["billing", "shipping", "account", "general"];

export default function UploadPanel() {
  const [category, setCategory] = useState("general");
  const [uploading, setUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [statusIsError, setStatusIsError] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setStatusMessage(null);

    try {
      const result = await uploadDocument(file, category);
      setStatusMessage(`Added "${result.filename}" — ${result.num_chunks} sections indexed.`);
      setStatusIsError(false);
    } catch (err) {
      setStatusMessage("Upload failed. Please try a PDF, DOCX, or Markdown file.");
      setStatusIsError(true);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  return (
    <div className="upload-panel">
      <p className="upload-panel-title">Knowledge base</p>

      <label className="upload-dropzone">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.md"
          onChange={handleFileChange}
          disabled={uploading}
          hidden
        />
        <span>{uploading ? "Uploading…" : "Drop a file or click to upload"}</span>
      </label>

      <div className="category-select">
        <label htmlFor="category">Category</label>
        <select id="category" value={category} onChange={(e) => setCategory(e.target.value)}>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      {statusMessage && (
        <div className={statusIsError ? "upload-status upload-status--error" : "upload-status"}>
          {statusMessage}
        </div>
      )}
    </div>
  );
}