import { Navigate, Route, Routes } from 'react-router-dom'
import { ApplicationRoute } from '../../features/application/ApplicationRoute'
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
    <Route path={routePaths.app} element={<ApplicationRoute />} />
    <Route path="*" element={<Navigate to={routePaths.app} replace />} />
  </Routes>
}
