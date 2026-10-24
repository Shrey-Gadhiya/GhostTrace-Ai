const API_BASE = '/api';

export interface OverviewMetrics {
  total_requests: number;
  audited_count: number;
  complete_count: number;
  incomplete_count: number;
  not_applicable_count: number;
  pending_count: number;
  latest_run: {
    run_id: string | null;
    status: string;
    completed_at: string | null;
  };
  systems_summary: Array<{
    system_id: string;
    name: string;
    type: string;
    risks: string;
  }>;
  rules_count: number;
  evidence_count: number;
}

export interface CaseListItem {
  case_id: string;
  customer_id: string;
  requested_email: string;
  request_type: string;
  requested_at: string;
  reported_status: string;
  deletion_status: string;
  audit_at: string;
  findings_count: number;
  remediation_count: number;
  verification_count: number;
}

export interface CasesResponse {
  items: CaseListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AuditStep {
  step_no: number;
  phase: string;
  system_id: string;
  resource_id: string;
  operation: string;
  state: string;
  evidence_id: string;
}

export interface IdentityLink {
  identifier_value: string;
  identifier_type: string;
  status: string;
  source_system: string;
  confidence: string;
}

export interface CaseDetail {
  case_id: string;
  customer_id: string;
  requested_email: string;
  request_type: string;
  requested_at: string;
  reported_status: string;
  deletion_status: string;
  audit_at: string;
  summary: string;
  identities: IdentityLink[];
  findings: AuditStep[];
  remediations: AuditStep[];
  verifications: AuditStep[];
  steps: AuditStep[];
  steps_json: string;
  evidence_citations: string[];
}

export interface EvidenceItem {
  evidence_id: string;
  system_id: string;
  resource_id: string;
  file_path: string;
  file_type: string;
  collected_at: string;
  hash_sha256: string;
  is_valid_hash: boolean;
  description: string;
  snippet: string;
}

export interface CaseEvidenceResponse {
  case_id: string;
  total_evidence_files: number;
  evidence: EvidenceItem[];
}

export async function fetchOverview(): Promise<OverviewMetrics> {
  const res = await fetch(`${API_BASE}/overview`);
  if (!res.ok) throw new Error('Failed to fetch overview metrics');
  return res.json();
}

export async function fetchCases(params: {
  page?: number;
  pageSize?: number;
  search?: string;
  deletionStatus?: string;
  reportedStatus?: string;
}): Promise<CasesResponse> {
  const query = new URLSearchParams();
  if (params.page) query.set('page', params.page.toString());
  if (params.pageSize) query.set('page_size', params.pageSize.toString());
  if (params.search) query.set('search', params.search);
  if (params.deletionStatus) query.set('deletion_status', params.deletionStatus);
  if (params.reportedStatus) query.set('reported_status', params.reportedStatus);

  const res = await fetch(`${API_BASE}/cases?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch cases');
  return res.json();
}

export async function fetchCaseDetail(caseId: string): Promise<CaseDetail> {
  const res = await fetch(`${API_BASE}/cases/${caseId}`);
  if (!res.ok) throw new Error(`Failed to fetch case ${caseId}`);
  return res.json();
}

export async function fetchCaseEvidence(caseId: string): Promise<CaseEvidenceResponse> {
  const res = await fetch(`${API_BASE}/cases/${caseId}/evidence`);
  if (!res.ok) throw new Error(`Failed to fetch evidence for case ${caseId}`);
  return res.json();
}

export async function fetchSystems(): Promise<any> {
  const res = await fetch(`${API_BASE}/systems`);
  if (!res.ok) throw new Error('Failed to fetch systems topology');
  return res.json();
}

export async function fetchRuns(): Promise<any> {
  const res = await fetch(`${API_BASE}/runs`);
  if (!res.ok) throw new Error('Failed to fetch analysis runs');
  return res.json();
}

export async function fetchRunLogs(runId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/runs/${runId}/logs`);
  if (!res.ok) throw new Error('Failed to fetch run logs');
  return res.json();
}

export async function triggerRun(): Promise<any> {
  const res = await fetch(`${API_BASE}/runs`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to trigger analysis run');
  return res.json();
}

export async function fetchEvaluation(): Promise<any> {
  const res = await fetch(`${API_BASE}/evaluation`);
  if (!res.ok) throw new Error('Failed to fetch evaluation metrics');
  return res.json();
}

export async function fetchSubmissionStatus(): Promise<any> {
  const res = await fetch(`${API_BASE}/submission/status`);
  if (!res.ok) throw new Error('Failed to fetch submission status');
  return res.json();
}

export async function exportOutputCsv(): Promise<any> {
  const res = await fetch(`${API_BASE}/exports/output-csv`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to export output.csv');
  return res.json();
}

export async function createSubmissionZip(): Promise<any> {
  const res = await fetch(`${API_BASE}/exports/submission-zip`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to create submission zip');
  return res.json();
}

export interface UploadBatchResponse {
  batch_id: string;
  filename: string;
  uploaded_at: string;
  total_cases: number;
  complete_count: number;
  incomplete_count: number;
  not_applicable_count: number;
  discrepancy_count: number;
  output_file: string;
  cases: Array<{
    case_id: string;
    customer_id: string;
    requested_email: string;
    request_type: string;
    requested_at: string;
    reported_status: string;
    deletion_status: string;
    audit_at: string;
    findings_count: number;
    remediation_count: number;
    verification_count: number;
    summary: string;
    steps_json: string;
    has_discrepancy: boolean;
  }>;
}

export async function uploadAndAuditCsv(file: File): Promise<UploadBatchResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/cases/upload-csv`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to upload and audit CSV file');
  }

  return res.json();
}

export function getUploadedBatchDownloadUrl(batchId: string): string {
  return `${API_BASE}/cases/uploaded/export-csv?batch_id=${encodeURIComponent(batchId)}`;
}

export function getSampleTemplateCsvUrl(): string {
  return `${API_BASE}/cases/sample-template-csv`;
}

