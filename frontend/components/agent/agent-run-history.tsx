"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { AgentRunResponse } from "@/lib/types";

export function AgentRunHistory({
  selectedRunId,
  onSelect,
}: {
  selectedRunId: string | null;
  onSelect: (run: AgentRunResponse) => void;
}) {
  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ["agent-runs"],
    queryFn: () => apiClient.listAgentRuns(),
    staleTime: 10_000,
  });

  const runs = data?.agent_runs ?? [];

  return (
    <section className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
          Agent Runs
        </h2>
        <button
          type="button"
          onClick={() => refetch()}
          disabled={isFetching}
          className="text-xs font-medium text-zinc-500 underline-offset-2 hover:underline disabled:text-zinc-300 dark:text-zinc-400 dark:disabled:text-zinc-700"
        >
          {isFetching ? "Refreshing" : "Refresh"}
        </button>
      </div>

      {isLoading ? (
        <p className="text-sm text-zinc-400 dark:text-zinc-500">Loading runs...</p>
      ) : isError ? (
        <p className="text-sm text-red-500">Failed to load Agent runs.</p>
      ) : runs.length === 0 ? (
        <div className="rounded-lg border border-dashed border-zinc-300 p-4 text-center text-sm text-zinc-400 dark:border-zinc-700 dark:text-zinc-500">
          No Agent runs yet
        </div>
      ) : (
        <ul className="flex max-h-64 flex-col gap-2 overflow-auto pr-1">
          {runs.slice(0, 8).map((run) => (
            <li key={run.run_id}>
              <button
                type="button"
                onClick={() => onSelect(run)}
                className={`w-full rounded-md border p-2 text-left transition ${
                  selectedRunId === run.run_id
                    ? "border-zinc-900 bg-zinc-100 dark:border-zinc-100 dark:bg-zinc-800"
                    : "border-zinc-200 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-900"
                }`}
              >
                <div className="mb-1 flex items-center justify-between gap-2 text-xs">
                  <span className="font-medium text-zinc-700 dark:text-zinc-300">
                    {run.route}
                  </span>
                  <span className="shrink-0 text-zinc-400">
                    {run.status} | {run.total_latency_ms}ms
                  </span>
                </div>
                <p className="line-clamp-2 text-sm text-zinc-600 dark:text-zinc-400">
                  {run.question}
                </p>
                <div className="mt-1 flex items-center justify-between text-xs text-zinc-400">
                  <span>{run.agent_steps.length} steps</span>
                  <span>{run.citations.length} citations</span>
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
