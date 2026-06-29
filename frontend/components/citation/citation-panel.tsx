"use client";

import { useState } from "react";
import type { CitationResponse, RetrievalTraceResponse } from "@/lib/types";

/**
 * Citation / evidence panel: shows the source chunks supporting the latest
 * answer, with page numbers, scores, quoted original text, and a minimal
 * retrieval trace summary for Phase 2 Hybrid RAG.
 */
export function CitationPanel({
  citations,
  trace,
}: {
  citations: CitationResponse[];
  trace: RetrievalTraceResponse | null;
}) {
  const [showTrace, setShowTrace] = useState(false);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
          Citations &amp; Evidence
        </h2>
        <button
          type="button"
          onClick={() => setShowTrace((prev) => !prev)}
          className="text-xs font-medium text-zinc-500 underline-offset-2 hover:underline dark:text-zinc-400"
        >
          {showTrace ? "Hide trace" : "Show trace"}
        </button>
      </div>

      {citations.length === 0 ? (
        <div className="rounded-lg border border-dashed border-zinc-300 p-6 text-center text-sm text-zinc-400 dark:border-zinc-700 dark:text-zinc-500">
          Answer sources will appear here
        </div>
      ) : (
        <ul className="flex flex-col gap-2">
          {citations.map((cite, i) => (
            <li
              key={cite.chunk_id}
              className="rounded-md border border-zinc-200 p-3 dark:border-zinc-800"
            >
              <div className="mb-1 flex items-center justify-between text-xs">
                <span className="font-medium text-zinc-700 dark:text-zinc-300">
                  [{i + 1}] Page {cite.page}
                </span>
                <span className="text-zinc-400">
                  score {cite.score.toFixed(3)}
                </span>
              </div>
              {cite.section && (
                <p className="mb-1 text-xs text-zinc-500">{cite.section}</p>
              )}
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                “{cite.quote}”
              </p>
            </li>
          ))}
        </ul>
      )}

      {showTrace && (
        <div className="rounded-lg border border-zinc-200 p-3 dark:border-zinc-800">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
            Retrieval Trace
          </h3>
          {!trace ? (
            <p className="text-sm text-zinc-400 dark:text-zinc-500">
              No retrieval trace available for this answer yet.
            </p>
          ) : (
            <div className="flex flex-col gap-3 text-sm text-zinc-600 dark:text-zinc-400">
              <div>
                <p className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Query</p>
                <p className="whitespace-pre-wrap">{trace.query}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Rewritten query</p>
                <p className="whitespace-pre-wrap">{trace.rewritten_query}</p>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="rounded border border-zinc-200 p-2 dark:border-zinc-800">
                  Dense results: {trace.dense_results.length}
                </div>
                <div className="rounded border border-zinc-200 p-2 dark:border-zinc-800">
                  Sparse results: {trace.sparse_results.length}
                </div>
                <div className="rounded border border-zinc-200 p-2 dark:border-zinc-800">
                  Fused results: {trace.fused_results.length}
                </div>
                <div className="rounded border border-zinc-200 p-2 dark:border-zinc-800">
                  Reranked: {trace.reranked_results.length}
                </div>
              </div>
              <div>
                <p className="mb-2 text-xs font-medium text-zinc-500 dark:text-zinc-400">
                  Evidence Pack
                </p>
                {trace.evidence_pack.length === 0 ? (
                  <p className="text-xs text-zinc-400 dark:text-zinc-500">
                    No evidence pack items.
                  </p>
                ) : (
                  <ul className="flex flex-col gap-2">
                    {trace.evidence_pack.map((item, index) => (
                      <li
                        key={`${item.chunk_id}-${index}`}
                        className="rounded border border-zinc-200 p-2 dark:border-zinc-800"
                      >
                        <div className="mb-1 flex items-center justify-between text-xs">
                          <span>
                            [{index + 1}] p.{item.page_start}
                            {item.page_end > item.page_start ? `-${item.page_end}` : ""}
                          </span>
                          <span>{item.retrieval_source}</span>
                        </div>
                        {item.section && (
                          <p className="mb-1 text-xs text-zinc-500">{item.section}</p>
                        )}
                        <p className="line-clamp-4 whitespace-pre-wrap text-sm">
                          {item.text}
                        </p>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
