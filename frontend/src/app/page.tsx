"use client";

import { DragEvent, FormEvent, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const STAGES = [
  "Parsing Context Document...",
  "Extracting Financial Metrics & Narratives...",
  "Generating Financial Charts...",
  "Rendering Geojit-Style PDF Report...",
];

export default function Home() {
  const [companyName, setCompanyName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [stageIndex, setStageIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [generatedFileName, setGeneratedFileName] = useState<string | null>(null);

  function handleDragOver(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragging(true);
  }

  function handleDragLeave(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragging(false);
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      const ext = droppedFile.name.split(".").pop()?.toLowerCase();
      if (["pdf", "txt", "csv"].includes(ext || "")) {
        setFile(droppedFile);
        setError(null);
      } else {
        setError("Invalid file format. Please upload a PDF, TXT, or CSV document.");
      }
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (downloadUrl) {
      URL.revokeObjectURL(downloadUrl);
      setDownloadUrl(null);
    }

    if (!companyName.trim()) {
      setError("Please enter a company name.");
      return;
    }
    if (!file) {
      setError("Please upload a financial document (PDF, TXT, or CSV).");
      return;
    }

    setLoading(true);
    setStageIndex(0);

    const interval = setInterval(() => {
      setStageIndex((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev));
    }, 1200);

    try {
      let response: Response | null = null;
      let lastErrorMsg = "";

      const candidateUrls = process.env.NEXT_PUBLIC_API_URL
        ? [process.env.NEXT_PUBLIC_API_URL]
        : ["http://localhost:8001", "http://localhost:8000", "http://127.0.0.1:8001", "http://127.0.0.1:8000"];

      for (const baseUrl of candidateUrls) {
        try {
          const formData = new FormData();
          formData.append("company_name", companyName.trim());
          formData.append("document", file);

          const res = await fetch(`${baseUrl}/api/generate-report`, {
            method: "POST",
            body: formData,
          });

          if (res.ok) {
            response = res;
            break;
          } else if (res.status !== 404) {
            const errData = await res.json().catch(() => null);
            lastErrorMsg = errData?.detail || `Request failed with status ${res.status}`;
            break;
          }
        } catch (err) {
          lastErrorMsg = err instanceof Error ? err.message : "Connection failed";
        }
      }

      clearInterval(interval);

      if (!response || !response.ok) {
        throw new Error(
          lastErrorMsg || "Backend API server not found. Ensure uvicorn is running."
        );
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const filename = `${companyName.trim().replace(/\s+/g, "_")}_research_report.pdf`;

      setDownloadUrl(url);
      setGeneratedFileName(filename);

      // Auto trigger download
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
    } catch (err) {
      clearInterval(interval);
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }


  return (
    <main className="min-h-screen flex flex-col bg-slate-50 text-slate-800 font-sans">
      {/* Header */}
      <header className="bg-geojit-navy text-white py-10 px-6 shadow-md">
        <div className="max-w-4xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="bg-amber-400 text-geojit-navy text-xs font-bold px-2 py-0.5 rounded tracking-wide uppercase">
                AI Institutional Research
              </span>
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight mt-2">EquityForge</h1>
            <p className="mt-1 text-blue-100 text-sm leading-relaxed max-w-xl">
              Transform Financial Documents into Institutional-Quality Equity Research Reports with AI.
            </p>
          </div>
          <div className="hidden md:block text-right border-l border-blue-800/80 pl-6">
            <p className="text-xs text-blue-200 uppercase font-semibold tracking-wider">Format Standard</p>
            <p className="text-sm font-medium text-white mt-0.5">Geojit-Inspired 4-Page PDF</p>
          </div>
        </div>
      </header>

      {/* Main Upload & Generation Card */}
      <section className="flex-1 flex items-start justify-center px-4 py-12">
        <div className="w-full max-w-xl bg-white rounded-2xl shadow-xl border border-slate-200/80 p-8 space-y-6">
          <div>
            <h2 className="text-2xl font-bold text-geojit-navy">
              Generate Equity Research Report
            </h2>
            <p className="text-slate-500 text-sm mt-1">
              Provide company name and financial context document (PDF, TXT, CSV).
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Company Name */}
            <div>
              <label
                htmlFor="company"
                className="block text-sm font-semibold text-slate-700 mb-1.5"
              >
                Company Name <span className="text-red-500">*</span>
              </label>
              <input
                id="company"
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="e.g. ICICI Bank, JSW Energy, POCL"
                className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-geojit-navy/30 focus:border-geojit-navy transition-all"
              />
            </div>

            {/* Drag and Drop Document Upload */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                Financial Context Document <span className="text-red-500">*</span>
              </label>
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`relative border-2 border-dashed rounded-xl p-6 text-center transition-all cursor-pointer ${
                  isDragging
                    ? "border-geojit-navy bg-blue-50/50 scale-[1.01]"
                    : file
                    ? "border-emerald-500 bg-emerald-50/30"
                    : "border-slate-300 hover:border-slate-400 bg-slate-50/50"
                }`}
              >
                <input
                  id="document"
                  type="file"
                  accept=".pdf,.txt,.csv"
                  onChange={(e) => {
                    const selected = e.target.files?.[0] ?? null;
                    setFile(selected);
                    if (selected) setError(null);
                  }}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />

                {file ? (
                  <div className="flex flex-col items-center justify-center space-y-2">
                    <div className="w-10 h-10 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center font-bold text-xs uppercase">
                      {file.name.split(".").pop()}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-slate-800">{file.name}</p>
                      <p className="text-xs text-slate-500">
                        {(file.size / 1024).toFixed(1)} KB &bull; Click or drop another to replace
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center space-y-2 py-2">
                    <div className="w-12 h-12 rounded-full bg-blue-50 text-geojit-navy flex items-center justify-center text-xl font-semibold">
                      📄
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-700">
                        Drag and drop your file here, or <span className="text-geojit-navy font-semibold underline">browse</span>
                      </p>
                      <p className="text-xs text-slate-400 mt-1">
                        Supports PDF, TXT, CSV formats up to 15MB
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700 flex items-start gap-3">
                <span className="text-red-500 text-base font-bold">⚠️</span>
                <div>{error}</div>
              </div>
            )}

            {/* Stage Progress Bar when Loading */}
            {loading && (
              <div className="bg-slate-100 rounded-xl p-4 space-y-2 border border-slate-200">
                <div className="flex justify-between items-center text-xs font-semibold text-geojit-navy">
                  <span>{STAGES[stageIndex]}</span>
                  <span>{Math.round(((stageIndex + 1) / STAGES.length) * 100)}%</span>
                </div>
                <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-geojit-navy h-full transition-all duration-500 ease-out"
                    style={{ width: `${((stageIndex + 1) / STAGES.length) * 100}%` }}
                  />
                </div>
              </div>
            )}

            {/* Success Download Card */}
            {downloadUrl && !loading && (
              <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm font-bold text-emerald-900">Report Ready!</p>
                  <p className="text-xs text-emerald-700 mt-0.5 truncate max-w-xs">{generatedFileName}</p>
                </div>
                <a
                  href={downloadUrl}
                  download={generatedFileName || "equity_research_report.pdf"}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs px-4 py-2 rounded-lg transition-colors shadow-sm shrink-0 flex items-center gap-1.5"
                >
                  <span>⬇</span> Download PDF
                </a>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-geojit-navy text-white py-3 text-sm font-bold hover:bg-geojit-navy/90 disabled:opacity-60 disabled:cursor-not-allowed transition-all shadow-md active:scale-[0.99]"
            >
              {loading ? "Processing Report Pipeline…" : "Generate & Download PDF"}
            </button>
          </form>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center text-xs text-slate-500 py-6 border-t border-slate-200 bg-white">
        EquityForge &mdash; Transform Financial Documents into Institutional-Quality Equity Research Reports with AI.
      </footer>
    </main>
  );
}

