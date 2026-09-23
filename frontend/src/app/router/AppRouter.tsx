import { Navigate, Route, Routes } from 'react-router-dom'
import { RequireAuth } from '../auth/RequireAuth'
import {
  AccessRequestsPlaceholder,
  AiAssistantPlaceholder,
  ApprovalQueuePlaceholder,
  AuditLogsPlaceholder,
  AuthenticatedLayout,
  AuthenticatedRootRedirect,
  CollectionDetailPlaceholder,
  CollectionsPlaceholder,
  DocumentUploadPlaceholder,
  DocumentsPlaceholder,
  MembersPlaceholder,
  NotificationsPlaceholder,
  ProcessingJobsPlaceholder,
  RolesPermissionsPlaceholder,
  SettingsPlaceholder,
} from '../../features/application/ApplicationRoute'
import { DashboardPage } from '../../features/dashboard/DashboardPage'
import { ForgotPasswordPage } from '../../features/public-routes/ForgotPasswordPage'
import { LoginPage } from '../../features/public-routes/LoginPage'
import { PublicRoutePlaceholder } from '../../features/public-routes/PublicRoutePlaceholder'
import { RegisterPage } from '../../features/public-routes/RegisterPage'
import { ResetPasswordPage } from '../../features/public-routes/ResetPasswordPage'
import { VerifyEmailPage } from '../../features/public-routes/VerifyEmailPage'
import { publicRouteDefinitions, routePaths } from './routes'

export function AppRouter() {
  return <Routes>
    <Route path="/" element={<Navigate to={routePaths.app} replace />} />
    <Route path={routePaths.login} element={<LoginPage />} />
    <Route path={routePaths.register} element={<RegisterPage />} />
    {publicRouteDefinitions.map(({ path, title }) => <Route key={path} path={path} element={<PublicRoutePlaceholder title={title} />} />)}
    <Route path={routePaths.verifyEmail} element={<VerifyEmailPage />} />
    <Route path={routePaths.forgotPassword} element={<ForgotPasswordPage />} />
    <Route path={routePaths.resetPassword} element={<ResetPasswordPage />} />
    <Route path={routePaths.app} element={<RequireAuth><AuthenticatedLayout /></RequireAuth>}>
      <Route index element={<AuthenticatedRootRedirect />} />
      <Route path={routePaths.dashboard.replace(`${routePaths.app}/`, '')} element={<DashboardPage />} />
      <Route path={routePaths.aiAssistant.replace(`${routePaths.app}/`, '')} element={<AiAssistantPlaceholder />} />
      <Route path={routePaths.collections.replace(`${routePaths.app}/`, '')} element={<CollectionsPlaceholder />} />
      <Route path={routePaths.collectionDetail.replace(`${routePaths.app}/`, '')} element={<CollectionDetailPlaceholder />} />
      <Route path={routePaths.documents.replace(`${routePaths.app}/`, '')} element={<DocumentsPlaceholder />} />
      <Route path={routePaths.documentUpload.replace(`${routePaths.app}/`, '')} element={<DocumentUploadPlaceholder />} />
      <Route path={routePaths.approvalQueue.replace(`${routePaths.app}/`, '')} element={<ApprovalQueuePlaceholder />} />
      <Route path={routePaths.processingJobs.replace(`${routePaths.app}/`, '')} element={<ProcessingJobsPlaceholder />} />
      <Route path={routePaths.members.replace(`${routePaths.app}/`, '')} element={<MembersPlaceholder />} />
      <Route path={routePaths.rolesPermissions.replace(`${routePaths.app}/`, '')} element={<RolesPermissionsPlaceholder />} />
      <Route path={routePaths.accessRequests.replace(`${routePaths.app}/`, '')} element={<AccessRequestsPlaceholder />} />
      <Route path={routePaths.notifications.replace(`${routePaths.app}/`, '')} element={<NotificationsPlaceholder />} />
      <Route path={routePaths.auditLogs.replace(`${routePaths.app}/`, '')} element={<AuditLogsPlaceholder />} />
      <Route path={routePaths.settings.replace(`${routePaths.app}/`, '')} element={<SettingsPlaceholder />} />
    </Route>
    <Route path="*" element={<Navigate to={routePaths.app} replace />} />
  </Routes>
}
