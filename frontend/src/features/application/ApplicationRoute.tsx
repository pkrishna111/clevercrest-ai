import { Navigate, Outlet } from 'react-router-dom'
import { routePaths } from '../../app/router/routes'
import { AppShell } from '../../app/AppShell'
import { ModulePlaceholder } from '../foundation/ModulePlaceholder'

export function AuthenticatedLayout() {
  return <AppShell><Outlet /></AppShell>
}

export function AuthenticatedRootRedirect() {
  return <Navigate to={routePaths.dashboard} replace />
}

export function DashboardPlaceholder() {
  return <ModulePlaceholder eyebrow="Overview" title="Dashboard" description="An editorial summary of activity across your organization." />
}

export function AiAssistantPlaceholder() {
  return <ModulePlaceholder eyebrow="Knowledge" title="AI Assistant" description="Ask questions about your organization's approved knowledge." />
}

export function CollectionsPlaceholder() {
  return <ModulePlaceholder eyebrow="Knowledge" title="Collections" description="Knowledge shelves for organizing approved documents." />
}

export function CollectionDetailPlaceholder() {
  return <ModulePlaceholder eyebrow="Knowledge" title="Collection details" description="Documents and metadata for a knowledge shelf." />
}

export function DocumentsPlaceholder() {
  return <ModulePlaceholder eyebrow="Knowledge" title="Documents" description="Controlled knowledge assets with version, status, and approval history." />
}

export function DocumentUploadPlaceholder() {
  return <ModulePlaceholder eyebrow="Knowledge" title="Upload document" description="Add new controlled knowledge for processing and optional approval." />
}

export function ApprovalQueuePlaceholder() {
  return <ModulePlaceholder eyebrow="Operations" title="Approval queue" description="Review documents submitted for organizational knowledge approval." />
}

export function ProcessingJobsPlaceholder() {
  return <ModulePlaceholder eyebrow="Operations" title="Processing jobs" description="Ingestion, extraction, chunking, embedding, and indexing progress." />
}

export function MembersPlaceholder() {
  return <ModulePlaceholder eyebrow="Organization" title="Members" description="People with access to this organization and their role." />
}

export function RolesPermissionsPlaceholder() {
  return <ModulePlaceholder eyebrow="Organization" title="Roles &amp; Permissions" description="Role catalog and permission assignments for this organization." />
}

export function AccessRequestsPlaceholder() {
  return <ModulePlaceholder eyebrow="Organization" title="Access requests" description="Pending and resolved access requests for knowledge and roles." />
}

export function NotificationsPlaceholder() {
  return <ModulePlaceholder eyebrow="Account" title="Notifications" description="Activity and updates relevant to you." />
}

export function AuditLogsPlaceholder() {
  return <ModulePlaceholder eyebrow="Account" title="Audit logs" description="Record of administrative and knowledge management activity." />
}

export function SettingsPlaceholder() {
  return <ModulePlaceholder eyebrow="Account" title="Settings" description="Organization profile, preferences, and security configuration." />
}
