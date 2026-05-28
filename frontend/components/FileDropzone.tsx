"use client";

import clsx from "clsx";
import { UploadCloud, FileText, Loader2 } from "lucide-react";
import { useRef, useState } from "react";

export function FileDropzone({
  onFile
}: {
  onFile: (file: File) => void;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [dragging, setDragging] = useState(false);

  return (
    <div
      className={clsx(
        "rounded-3xl border border-dashed p-6 transition",
        dragging ? "border-cyan-400 bg-cyan-400/10" : "border-white/15 bg-white/5"
      )}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer.files?.[0];
        if (file) onFile(file);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".csv"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onFile(file);
        }}
      />

      <div className="flex flex-col items-center justify-center gap-4 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-cyan-400/25 bg-cyan-400/10 text-cyan-200">
          <UploadCloud size={24} />
        </div>
        <div>
          <div className="text-lg font-medium text-white">Drop the CSV here</div>
          <div className="mt-1 text-sm text-slate-400">Fast validation, preview, and submission generation in one flow.</div>
        </div>
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/8 px-4 py-2 text-sm text-white transition hover:bg-white/12"
          onClick={() => inputRef.current?.click()}
        >
          <FileText size={16} />
          Choose file
        </button>
      </div>
    </div>
  );
}

