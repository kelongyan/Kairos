"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type {
  KnowledgeOperationItemResponse,
  KnowledgeOperationStatus,
} from "@/lib/types";

const SEVERITY_STYLES: Record<string, string> = {
  high: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  medium: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  low: "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300",
};

const STATUS_OPTIONS = [
  { label: "Pending", value: "pending" },
  { label: "All", value: "" },
  { label: "Resolved", value: "resolved" },
  { label: "Ignored", value: "ignored" },
  { label: "Reindexed", value: "reindexed" },
  { label: "Document added", value: "document_added" },
];

const SOURCE_TYPE_OPTIONS = [
  { label: "All sources", value: "" },
  { label: "Question logs", value: "question_log" },
  { label: "Answer feedback", value: "answer_feedback" },
  { label: "Documents", value: "document" },
  { label: "Agent runs", value: "agent_run" },
];

const ACTIONS: Array<{
  label: string;
  status: KnowledgeOperationStatus;
  note: string;
}> = [
  { label: "Resolve", status: "resolved", note: "Marked resolved from operations UI." },
  { label: "Ignore", status: "ignored", note: "Marked ignored from operations UI." },
  { label: "Reindexed", status: "reindexed", note: "Document reindex handled." },
  { label: "Doc added", status: "document_added", note: "Supporting document added." },
];

export function KnowledgeOperationsPanel({
  knowledgeBaseId,
  selectedRunId,
  onClearRunFilter,
}: {
  knowledgeBaseId: string | null;
  selectedRunId?: string | null;
  onClearRunFilter?: () => void;
}) {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState("pending");
  const [sourceTypeFilter, setSourceTypeFilter] = useState("");

  const visibleSourceType = selectedRunId ? "agent_run" : sourceTypeFilter;

  const queryKey = [
    "knowledge-operation-items",
    knowledgeBaseId,
    statusFilter,
    visibleSourceType,
    selectedRunId ?? "",
  ];
  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey,
    queryFn: () =>
      apiClient.listKnowledgeOperationItems(
        knowledgeBaseId,
        statusFilter || null,
        visibleSourceType || null,
        selectedRunId ?? null
      ),
    staleTime: 10_000,
    enabled: Boolean(knowledgeBaseId),
  });

  const mutation = useMutation({
    mutationFn: ({
      itemId,
      status,
      resolutionNote,
    }: {
      itemId: string;
      status: KnowledgeOperationStatus;
      resolutionNote: string;
    }) =>
      apiClient.updateKnowledgeOperationItem(itemId, {
        status,
        resolution_note: resolutionNote,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-operation-items"] });
    },
  });

  const items = data?.items ?? [];

  return (
    <section className="flex flex-col gap-3">
      <div className="flex items-center justify-between gap-2">
        <div>
          <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
            Operations
          </h2>
          <p className="text-[11px] text-zinc-400">
            {items.length} item(s)
          </p>
        </div>
        <button
          type="button"
          onClick={() => refetch()}
          disabled={!knowledgeBaseId || isFetching}
          className="text-xs font-medium text-zinc-500 underline-offset-2 hover:underline disabled:text-zinc-300 dark:text-zinc-400 dark:disabled:text-zinc-700"
        >
          {isFetching ? "Refreshing" : "Refresh"}
        </button>
      </div>

      {selectedRunId && onClearRunFilter && (
        <button
          type="button"
          onClick={onClearRunFilter}
          className="self-start text-[10px] font-medium text-zinc-500 underline-offset-2 hover:underline dark:text-zinc-400"
        >
          Showing Agent run {selectedRunId}
        </button>
      )}

      <select
        value={statusFilter}
        onChange={(event) => setStatusFilter(event.target.value)}
        disabled={!knowledgeBaseId}
        className="rounded-md border border-zinc-300 bg-white px-2 py-1.5 text-xs text-zinc-600 disabled:bg-zinc-50 disabled:text-zinc-300 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:disabled:bg-zinc-900/50"
      >
        {STATUS_OPTIONS.map((option) => (
          <option key={option.label} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      <select
        value={visibleSourceType}
        onChange={(event) => setSourceTypeFilter(event.target.value)}
        disabled={!knowledgeBaseId || Boolean(selectedRunId)}
        className="rounded-md border border-zinc-300 bg-white px-2 py-1.5 text-xs text-zinc-600 disabled:bg-zinc-50 disabled:text-zinc-300 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:disabled:bg-zinc-900/50"
      >
        {SOURCE_TYPE_OPTIONS.map((option) => (
          <option key={option.label} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      {!knowledgeBaseId ? (
        <EmptyState text="Select a knowledge base to view operations." />
      ) : isLoading ? (
        <p className="text-sm text-zinc-400 dark:text-zinc-500">Loading...</p>
      ) : isError ? (
        <p className="text-sm text-red-500">Failed to load operation items.</p>
      ) : items.length === 0 ? (
        <EmptyState text="No operation items" />
      ) : (
        <ul className="flex max-h-72 flex-col gap-2 overflow-auto pr-1">
          {items.slice(0, 8).map((item) => (
            <li key={item.item_id}>
              <OperationItemCard
                item={item}
                isUpdating={mutation.isPending}
                onUpdate={(status, note) =>
                  mutation.mutate({
                    itemId: item.item_id,
                    status,
                    resolutionNote: note,
                  })
                }
              />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function OperationItemCard({
  item,
  isUpdating,
  onUpdate,
}: {
  item: KnowledgeOperationItemResponse;
  isUpdating: boolean;
  onUpdate: (status: KnowledgeOperationStatus, note: string) => void;
}) {
  return (
    <div className="rounded-md border border-zinc-200 p-2 text-sm dark:border-zinc-800">
      <div className="mb-1 flex items-center justify-between gap-2">
        <span className="line-clamp-1 font-medium text-zinc-800 dark:text-zinc-100">
          {item.title}
        </span>
        <span
          className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium ${
            SEVERITY_STYLES[item.severity] ?? SEVERITY_STYLES.low
          }`}
        >
          {item.severity}
        </span>
      </div>
      <p className="line-clamp-2 text-xs text-zinc-500 dark:text-zinc-400">
        {item.description}
      </p>
      <p className="mt-1 line-clamp-2 text-xs text-zinc-600 dark:text-zinc-300">
        {item.suggested_action}
      </p>
      <div className="mt-2 flex items-center justify-between gap-2 text-[10px] text-zinc-400">
        <span>{formatLabel(item.source_type)}</span>
        <span>{formatLabel(item.status)}</span>
      </div>
      {item.status === "pending" && (
        <div className="mt-2 grid grid-cols-2 gap-1">
          {ACTIONS.map((action) => (
            <button
              key={action.status}
              type="button"
              disabled={isUpdating}
              onClick={() => onUpdate(action.status, action.note)}
              className="rounded border border-zinc-300 px-2 py-1 text-[10px] font-medium text-zinc-600 hover:bg-zinc-50 disabled:opacity-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900"
            >
              {action.label}
            </button>
          ))}
        </div>
      )}
      {item.resolution_note && (
        <p className="mt-2 line-clamp-2 text-[10px] text-zinc-400">
          {item.resolution_note}
        </p>
      )}
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return (
    <div className="rounded-lg border border-dashed border-zinc-300 p-4 text-center text-sm text-zinc-400 dark:border-zinc-700 dark:text-zinc-500">
      {text}
    </div>
  );
}

function formatLabel(value: string): string {
  return value.replaceAll("_", " ");
}
