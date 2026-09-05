import { useCallback, useEffect, useRef, useState, type PropsWithChildren } from 'react'
import { AuthContext, type AuthSessionStatus } from './AuthContext'
import { getCurrentUser, logout as apiLogout, type CurrentUser } from './authApi'

export function AuthProvider({ children }: PropsWithChildren) {
  const [status, setStatus] = useState<AuthSessionStatus>('initializing')
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null)
  const inflightRef = useRef<Promise<void> | null>(null)

  const clearSession = useCallback(() => {
    setCurrentUser(null)
    setStatus('unauthenticated')
  }, [])

  const refreshSession = useCallback(async () => {
    if (inflightRef.current) {
      await inflightRef.current
      return
    }

    let inflight: Promise<void> = Promise.resolve()
    inflight = (async () => {
      const result = await getCurrentUser()
      try {
        switch (result.kind) {
          case 'success':
            setCurrentUser(result.user)
            setStatus('authenticated')
            break
          case 'unauthenticated':
            setCurrentUser(null)
            setStatus('unauthenticated')
            break
          case 'forbidden':
            setCurrentUser(null)
            setStatus('forbidden')
            break
          case 'error':
          case 'network':
            setCurrentUser(null)
            setStatus('unavailable')
            break
        }
      } finally {
        if (inflightRef.current === inflight) {
          inflightRef.current = null
        }
      }
    })()

    inflightRef.current = inflight
    await inflight
  }, [])

  const logout = useCallback(async () => {
    const result = await apiLogout()
    clearSession()
    if (result.kind === 'success') return
    if (result.kind === 'error') return
    void result
  }, [clearSession])

  useEffect(() => {
    void refreshSession()
  }, [refreshSession])

  return (
    <AuthContext value={{ status, currentUser, refreshSession, clearSession, logout }}>
      {children}
    </AuthContext>
  )
}
