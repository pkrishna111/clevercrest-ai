export interface CurrentUser {
  id: string
  email: string
  first_name: string
  last_name: string | null
  is_email_verified: boolean
  status: string
}

export type GetCurrentUserResult =
  | { kind: 'success'; user: CurrentUser }
  | { kind: 'unauthenticated' }
  | { kind: 'forbidden'; status: number }
  | { kind: 'error'; status: number }
  | { kind: 'network' }

export type LogoutResult =
  | { kind: 'success' }
  | { kind: 'error'; status: number }
  | { kind: 'network' }

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/+$/, '') ?? 'http://localhost:8000'

export async function getCurrentUser(): Promise<GetCurrentUserResult> {
  try {
    const response = await fetch(`${apiBaseUrl}/auth/me`, {
      method: 'GET',
      credentials: 'include',
      headers: { Accept: 'application/json' },
    })

    if (response.ok) {
      const user = (await response.json()) as CurrentUser
      return { kind: 'success', user }
    }

    if (response.status === 401) {
      return { kind: 'unauthenticated' }
    }

    if (response.status === 403) {
      return { kind: 'forbidden', status: 403 }
    }

    return { kind: 'error', status: response.status }
  } catch {
    return { kind: 'network' }
  }
}

export async function logout(): Promise<LogoutResult> {
  try {
    const response = await fetch(`${apiBaseUrl}/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    })

    if (response.ok) {
      return { kind: 'success' }
    }

    return { kind: 'error', status: response.status }
  } catch {
    return { kind: 'network' }
  }
}
