import { routePaths } from '../router/routes'

export type ActivityStatus =
  | 'approved'
  | 'processing'
  | 'pending'
  | 'rejected'
  | 'draft'
  | 'failed'

export interface DashboardMetric {
  id:
    | 'members'
    | 'collections'
    | 'documents'
    | 'pending_approvals'
    | 'processing_jobs'
    | 'ai_conversations'
  eyebrow: string
  cardIndex: string
  label: string
  value: number
  delta?: {
    sign: 'up' | 'down'
    value: number
    period: string
  }
  summary: string
  link?: {
    label: string
    routePath: string
  }
}

export interface DashboardActivityItem {
  id: string
  timestamp: string
  actorName: string
  actorEmail?: string
  action: string
  targetLabel: string
  status: ActivityStatus | null
  route?: string
}

export interface DashboardOperationalItem {
  id: string
  kind: 'approval' | 'job'
  title: string
  metadata: string
  status: ActivityStatus
}

export interface DashboardOverview {
  greetingName: string | null
  organizationName: string | null
  metrics: DashboardMetric[]
  recentActivity: DashboardActivityItem[]
  pendingApprovals: DashboardOperationalItem[]
  processingSummary: DashboardOperationalItem[]
  generatedAt: string
}

export type GetDashboardOverviewResult =
  | { kind: 'success'; overview: DashboardOverview }
  | { kind: 'unauthenticated' }
  | { kind: 'forbidden'; status: number }
  | { kind: 'error'; status: number }
  | { kind: 'network' }

const mockMetrics: DashboardMetric[] = [
  {
    id: 'members',
    eyebrow: 'Organization',
    cardIndex: '01',
    label: 'Members',
    value: 24,
    delta: { sign: 'up', value: 3, period: 'this week' },
    summary: 'People with access to organizational knowledge.',
    link: { label: 'Manage members', routePath: routePaths.members },
  },
  {
    id: 'collections',
    eyebrow: 'Knowledge',
    cardIndex: '02',
    label: 'Collections',
    value: 8,
    delta: { sign: 'up', value: 1, period: 'this week' },
    summary: 'Knowledge shelves organizing approved documents.',
    link: { label: 'Browse collections', routePath: routePaths.collections },
  },
  {
    id: 'documents',
    eyebrow: 'Knowledge',
    cardIndex: '03',
    label: 'Documents',
    value: 142,
    delta: { sign: 'up', value: 12, period: 'this week' },
    summary: 'Controlled knowledge assets with version and approval history.',
    link: { label: 'View documents', routePath: routePaths.documents },
  },
  {
    id: 'pending_approvals',
    eyebrow: 'Operations',
    cardIndex: '04',
    label: 'Pending approvals',
    value: 6,
    delta: { sign: 'up', value: 2, period: 'today' },
    summary: 'Documents awaiting review before becoming knowledge.',
    link: { label: 'Open approval queue', routePath: routePaths.approvalQueue },
  },
  {
    id: 'processing_jobs',
    eyebrow: 'Operations',
    cardIndex: '05',
    label: 'Processing jobs',
    value: 3,
    delta: { sign: 'down', value: 1, period: 'today' },
    summary: 'Ingestion, extraction, chunking, embedding, and indexing runs.',
    link: { label: 'Inspect jobs', routePath: routePaths.processingJobs },
  },
  {
    id: 'ai_conversations',
    eyebrow: 'Intelligence',
    cardIndex: '06',
    label: 'AI conversations',
    value: 38,
    delta: { sign: 'up', value: 7, period: 'this week' },
    summary: 'Questions asked against approved organizational knowledge.',
    link: { label: 'Ask CleverCrest', routePath: routePaths.aiAssistant },
  },
]

const mockActivity: DashboardActivityItem[] = [
  {
    id: 'act-1',
    timestamp: '2 hours ago',
    actorName: 'Sarah Chen',
    actorEmail: 'sarah.chen@acme.example',
    action: 'approved',
    targetLabel: 'Information Security Policy v3',
    status: 'approved',
    route: routePaths.approvalQueue,
  },
  {
    id: 'act-2',
    timestamp: '4 hours ago',
    actorName: 'Marcus Okafor',
    actorEmail: 'marcus.okafor@acme.example',
    action: 'uploaded a new revision of',
    targetLabel: 'Employee Handbook 2026',
    status: 'pending',
    route: routePaths.documents,
  },
  {
    id: 'act-3',
    timestamp: 'Yesterday',
    actorName: 'Priya Raman',
    actorEmail: 'priya.raman@acme.example',
    action: 'invited a new member',
    targetLabel: 'alex.torres@acme.example',
    status: 'processing',
    route: routePaths.members,
  },
  {
    id: 'act-4',
    timestamp: 'Yesterday',
    actorName: 'Processing service',
    action: 'completed indexing job for',
    targetLabel: 'Vendor Risk Assessment Q3',
    status: 'approved',
    route: routePaths.processingJobs,
  },
  {
    id: 'act-5',
    timestamp: '2 days ago',
    actorName: 'Krishna Patel',
    actorEmail: 'krishna.patel@acme.example',
    action: 'started a new AI conversation about',
    targetLabel: 'Data Retention Policy',
    status: null,
    route: routePaths.aiAssistant,
  },
  {
    id: 'act-6',
    timestamp: '2 days ago',
    actorName: 'Sarah Chen',
    actorEmail: 'sarah.chen@acme.example',
    action: 'rejected the proposed revision of',
    targetLabel: 'Onboarding Guide, draft 4',
    status: 'rejected',
    route: routePaths.approvalQueue,
  },
]

const mockApprovals: DashboardOperationalItem[] = [
  {
    id: 'apv-1',
    kind: 'approval',
    title: 'Employee Handbook 2026',
    metadata: 'Submitted 4h ago · Marcus Okafor · Policies',
    status: 'pending',
  },
  {
    id: 'apv-2',
    kind: 'approval',
    title: 'Onboarding Guide, draft 5',
    metadata: 'Resubmitted 2d ago · Alex Torres · People Operations',
    status: 'pending',
  },
]

const mockProcessing: DashboardOperationalItem[] = [
  {
    id: 'job-1',
    kind: 'job',
    title: 'Vendor Risk Assessment Q3 — Embed',
    metadata: 'Stage 4 of 6 · Started 25m ago',
    status: 'processing',
  },
  {
    id: 'job-2',
    kind: 'job',
    title: 'Procurement Playbook 2026 — Index',
    metadata: 'Failed during Chunk · 3 failed attempts',
    status: 'failed',
  },
]

export async function getDashboardOverview(): Promise<GetDashboardOverviewResult> {
  try {
    await new Promise((resolve) => setTimeout(resolve, 220))
    const overview: DashboardOverview = {
      greetingName: null,
      organizationName: 'Acme Organization',
      metrics: mockMetrics,
      recentActivity: mockActivity,
      pendingApprovals: mockApprovals,
      processingSummary: mockProcessing,
      generatedAt: new Date().toISOString(),
    }
    return { kind: 'success', overview }
  } catch {
    return { kind: 'network' }
  }
}
