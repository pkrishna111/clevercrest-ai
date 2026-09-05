import { Navigate, useLocation } from 'react-router-dom'
import type { PropsWithChildren } from 'react'
import { useAuth } from './useAuth'
import { routePaths } from '../router/routes'

export function RequireAuth({ children }: PropsWithChildren) {
  const { status } = useAuth()
  const location = useLocation()

  if (status === 'initializing' || status === 'unavailable') {
    return (
      <div className="auth-loading-shell" aria-live="polite" role="status">
        <div className="auth-loading-indicator" aria-hidden="true" />
        <p>Loading CleverCrest.</p>
      </div>
    )
  }

  if (status === 'unauthenticated' || status === 'forbidden') {
    return <Navigate to={routePaths.login} replace state={{ from: location.pathname }} />
  }

  return <>{children}</>
}
