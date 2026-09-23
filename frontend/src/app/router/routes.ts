export const routePaths = {
  app: '/app',
  dashboard: '/app/dashboard',
  aiAssistant: '/app/ai-assistant',
  collections: '/app/collections',
  collectionDetail: '/app/collections/:collectionId',
  documents: '/app/documents',
  documentUpload: '/app/documents/upload',
  approvalQueue: '/app/approval-queue',
  processingJobs: '/app/processing-jobs',
  members: '/app/members',
  rolesPermissions: '/app/roles-permissions',
  accessRequests: '/app/access-requests',
  notifications: '/app/notifications',
  auditLogs: '/app/audit-logs',
  settings: '/app/settings',
  login: '/login',
  register: '/register',
  verifyEmail: '/verify-email',
  forgotPassword: '/forgot-password',
  resetPassword: '/reset-password',
} as const

// Placeholder scaffold for routes that are reserved but not yet implemented.
// /forgot-password and /reset-password have graduated to dedicated pages
// (ForgotPasswordPage / ResetPasswordPage) and are wired up explicitly in
// AppRouter, so they are no longer listed here.
export const publicRouteDefinitions: readonly { path: string; title: string }[] = []

export const authenticatedNavigation: readonly { label: string; path: string; eyebrow: string }[] = [
  { label: 'Dashboard', path: routePaths.dashboard, eyebrow: 'Overview' },
  { label: 'AI Assistant', path: routePaths.aiAssistant, eyebrow: 'Knowledge' },
  { label: 'Collections', path: routePaths.collections, eyebrow: 'Knowledge' },
  { label: 'Documents', path: routePaths.documents, eyebrow: 'Knowledge' },
  { label: 'Approval Queue', path: routePaths.approvalQueue, eyebrow: 'Operations' },
  { label: 'Processing Jobs', path: routePaths.processingJobs, eyebrow: 'Operations' },
  { label: 'Members', path: routePaths.members, eyebrow: 'Organization' },
  { label: 'Roles & Permissions', path: routePaths.rolesPermissions, eyebrow: 'Organization' },
  { label: 'Access Requests', path: routePaths.accessRequests, eyebrow: 'Organization' },
  { label: 'Notifications', path: routePaths.notifications, eyebrow: 'Account' },
  { label: 'Audit Logs', path: routePaths.auditLogs, eyebrow: 'Account' },
  { label: 'Settings', path: routePaths.settings, eyebrow: 'Account' },
] as const
