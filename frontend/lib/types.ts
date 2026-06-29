/**
 * Shared frontend type definitions mirroring backend schemas.
 */

export type DocumentStatus =
  | "uploaded"
  | "parsing"
  | "parsed"
  | "indexing"
  | "indexed"
  | "failed";

export interface DocumentResponse {
  doc_id: string;
  title: string;
  source: string;
  status: DocumentStatus;
  page_count: number;
  error_message: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  documents: DocumentResponse[];
}

export interface CitationResponse {
  doc_id: string;
  chunk_id: string;
  section: string;
  page: number;
  quote: string;
  score: number;
}

export interface RetrievalHitResponse {
  doc_id: string;
  chunk_id: string;
  section: string;
  page_start: number;
  page_end: number;
  chunk_type: string;
  chunk_index: number;
  score: number;
  retrieval_source: string;
  text: string;
}

export type EvidenceItemResponse = RetrievalHitResponse;

export interface RetrievalTraceResponse {
  query: string;
  rewritten_query: string;
  dense_results: RetrievalHitResponse[];
  sparse_results: RetrievalHitResponse[];
  fused_results: RetrievalHitResponse[];
  reranked_results: RetrievalHitResponse[];
  evidence_pack: EvidenceItemResponse[];
}

export interface ChatResponse {
  answer: string;
  citations: CitationResponse[];
  trace?: RetrievalTraceResponse | null;
}

export interface ChatRequest {
  doc_id: string;
  question: string;
}
