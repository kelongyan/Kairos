"use client";

import { useState } from "react";
import type { CitationResponse, DocumentResponse, RetrievalTraceResponse } from "@/lib/types";
import { DocumentList } from "@/components/document/document-list";
import { ChatPanel } from "@/components/chat/chat-panel";
import { CitationPanel } from "@/components/citation/citation-panel";

/**
 * Kairos home page: three-column knowledge workspace.
 *
 * Left   - source library with upload and live status
 * Center - evidence-grounded Q&A
 * Right  - citations, evidence, and retrieval trace for the latest answer
 */
export default function Home() {
  const [selectedDoc, setSelectedDoc] = useState<DocumentResponse | null>(null);
  const [citations, setCitations] = useState<CitationResponse[]>([]);
  const [trace, setTrace] = useState<RetrievalTraceResponse | null>(null);

  return (
    <div className="flex flex-col flex-1 bg-zinc-50 font-sans dark:bg-black">
      <header className="flex items-center justify-between border-b border-zinc-200 bg-white px-6 py-3 dark:border-zinc-800 dark:bg-zinc-950">
        <div className="flex items-center gap-3">
          <span className="text-lg font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            Kairos
          </span>
          <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-medium text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
            Phase 2 | Evidence RAG
          </span>
        </div>
        <div className="text-sm text-zinc-500 dark:text-zinc-400">
          {selectedDoc ? (
            <span>
              {selectedDoc.title} | <span className="text-zinc-400">{selectedDoc.status}</span>
            </span>
          ) : (
            <span>No source selected</span>
          )}
        </div>
      </header>

      <div className="grid flex-1 grid-cols-1 md:grid-cols-[280px_1fr_360px]">
        <aside className="border-r border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950">
          <DocumentList
            selectedDocId={selectedDoc?.doc_id ?? null}
            onSelect={(doc) => {
              setSelectedDoc(doc);
              setCitations([]);
              setTrace(null);
            }}
          />
        </aside>

        <main className="flex flex-col border-r border-zinc-200 dark:border-zinc-800">
          {selectedDoc ? (
            <ChatPanel
              document={selectedDoc}
              onAnswerArtifacts={({ citations: nextCitations, trace: nextTrace }) => {
                setCitations(nextCitations);
                setTrace(nextTrace);
              }}
            />
          ) : (
            <div className="flex flex-1 items-center justify-center p-6 text-center text-sm text-zinc-400">
              Select or upload a source to start asking questions.
            </div>
          )}
        </main>

        <aside className="bg-white p-4 dark:bg-zinc-950">
          <CitationPanel citations={citations} trace={trace} />
        </aside>
      </div>
    </div>
  );
}
