"use client";

import { useRef, useState } from "react";
import { API_BASE_URL } from "@/lib/api";

interface BatchJob {
  job_id: string;
  status: string;
  total: number;
  processed: number;
  failed: number;
  skipped: number;
  estimated_cost_usd: number;
}

export default function DatasetBuilderPage() {
  const folderInputRef = useRef<HTMLInputElement>(null);
  const [browserFiles, setBrowserFiles] = useState<File[]>([]);
  const [serverPath, setServerPath] = useState("");
  const [job, setJob] = useState<BatchJob | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleFolderSelect(files: FileList | null) {
    if (!files) return;
    setBrowserFiles(Array.from(files).filter((f) => f.type.startsWith("image/")));
  }

  async function startServerDirectoryImport() {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/dataset/import-directory`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ directory_path: serverPath }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setJob({
        job_id: data.job_id,
        status: "pending",
        total: data.total_images,
        processed: 0,
        failed: 0,
        skipped: 0,
        estimated_cost_usd: data.estimated_cost_usd,
      });
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function processBatch(action: "start" | "pause" | "resume") {
    if (!job) return;
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/dataset/process-batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_id: job.job_id, action }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setJob(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function exportDataset(format: "jsonl" | "csv") {
    const res = await fetch(`${API_BASE_URL}/api/dataset/export`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ format }),
    });
    const data = await res.json();
    alert(`Exported to ${data.path}`);
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Dataset Builder</h1>
        <p className="mt-1 text-slate-600">
          Batch-process food images into training candidates for the internal model.
        </p>
      </div>

      <div className="rounded-lg border bg-white p-6 shadow-sm">
        <h2 className="font-semibold">Option A — Upload a folder (browser mode)</h2>
        <p className="mt-1 text-sm text-slate-500">
          Select a local folder. The browser cannot read directories without your explicit selection.
        </p>
        <input
          ref={folderInputRef}
          type="file"
          // @ts-expect-error non-standard browser attribute
          webkitdirectory="true"
          directory="true"
          multiple
          onChange={(e) => handleFolderSelect(e.target.files)}
          className="mt-3 block text-sm"
        />
        {browserFiles.length > 0 && (
          <p className="mt-2 text-sm text-slate-600">{browserFiles.length} images found in folder.</p>
        )}
      </div>

      <div className="rounded-lg border bg-white p-6 shadow-sm">
        <h2 className="font-semibold">Option B — Server-side directory path (local/admin mode)</h2>
        <p className="mt-1 text-sm text-slate-500">
          Only available when the backend runs on the same machine you're administering.
        </p>
        <div className="mt-3 flex gap-2">
          <input
            value={serverPath}
            onChange={(e) => setServerPath(e.target.value)}
            placeholder="C:\path\to\images"
            className="flex-1 rounded-md border px-3 py-2 text-sm"
          />
          <button
            onClick={startServerDirectoryImport}
            disabled={!serverPath || busy}
            className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
          >
            Scan directory
          </button>
        </div>
      </div>

      {job && (
        <div className="rounded-lg border bg-white p-6 shadow-sm">
          <h2 className="font-semibold">Batch job {job.job_id.slice(0, 8)}</h2>
          <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-5">
            <Stat label="Total" value={job.total} />
            <Stat label="Processed" value={job.processed} />
            <Stat label="Failed" value={job.failed} />
            <Stat label="Skipped" value={job.skipped} />
            <Stat label="Est. cost" value={`$${job.estimated_cost_usd}`} />
          </div>
          <p className="mt-2 text-sm text-slate-500">Status: {job.status}</p>
          <div className="mt-4 flex gap-2">
            <button onClick={() => processBatch("start")} disabled={busy}
              className="rounded-md bg-brand-600 px-3 py-1.5 text-sm text-white hover:bg-brand-700 disabled:opacity-50">
              Start
            </button>
            <button onClick={() => processBatch("pause")} disabled={busy}
              className="rounded-md border px-3 py-1.5 text-sm hover:bg-slate-50 disabled:opacity-50">
              Pause
            </button>
            <button onClick={() => processBatch("resume")} disabled={busy}
              className="rounded-md border px-3 py-1.5 text-sm hover:bg-slate-50 disabled:opacity-50">
              Resume
            </button>
          </div>
        </div>
      )}

      <div className="rounded-lg border bg-white p-6 shadow-sm">
        <h2 className="font-semibold">Export dataset</h2>
        <div className="mt-3 flex gap-2">
          <button onClick={() => exportDataset("jsonl")} className="rounded-md border px-3 py-1.5 text-sm hover:bg-slate-50">
            Export JSONL
          </button>
          <button onClick={() => exportDataset("csv")} className="rounded-md border px-3 py-1.5 text-sm hover:bg-slate-50">
            Export CSV
          </button>
        </div>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-md bg-slate-50 p-3 text-center">
      <div className="text-xs uppercase text-slate-500">{label}</div>
      <div className="text-lg font-semibold">{value}</div>
    </div>
  );
}
