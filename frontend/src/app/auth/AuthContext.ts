import { createContext } from 'react'
import type { CurrentUser } from './authApi'

export type AuthSessionStatus =
  | 'initializing'
  | 'authenticated'
  | 'unauthenticated'
  | 'forbidden'
  | 'unavailable'

export interface AuthContextValue {
  status: AuthSessionStatus
  currentUser: CurrentUser | null
  refreshSession: () => Promise<void>
  clearSession: () => void
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)
