// ---------------------------------------------------------------------------
// Password-reset API integration — ISOLATED / NOT YET FINALIZED
//
// The CleverCrest backend does not currently expose finalized password-reset
// endpoints (see backend/app/api/routes/auth.py — only /auth/register,
// /auth/login and /auth/verify-email exist today). This module is the single
// integration point for the password-reset UI so the request shape and
// response handling can be replaced later WITHOUT touching
// ForgotPasswordPage / ResetPasswordPage.
//
// The endpoints and request bodies below are ASSUMED and follow the existing
// project conventions used by LoginPage / RegisterPage / VerifyEmailPage:
//   - base URL from VITE_API_BASE_URL (default http://localhost:8000)
//   - JSON request bodies with snake_case fields
//   - the /auth/* route prefix
//   - 400 signals an invalid/expired/used token (mirrors /auth/verify-email)
//
// When the backend contract is finalized, update ONLY this file.
// ---------------------------------------------------------------------------

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/+$/, '')

// --- ASSUMED endpoints (replace when the backend contract is finalized) ---
const forgotPasswordEndpoint = `${apiBaseUrl}/auth/forgot-password`
const resetPasswordEndpoint = `${apiBaseUrl}/auth/reset-password`

// Result of requesting a reset link. Deliberately does NOT distinguish whether
// an account exists — the UI must show a single generic message either way.
export type ForgotPasswordResult = 'submitted' | 'network-error'

// Result of completing a password reset with a token.
export type ResetPasswordResult = 'success' | 'invalid-token' | 'error'

/**
 * Request password-reset instructions for an email address.
 *
 * Any completed HTTP response is treated as "submitted" so the UI never
 * reveals whether the email address is registered. Only a failure to reach the
 * server surfaces a (retryable) network error.
 */
export async function requestPasswordReset(email: string): Promise<ForgotPasswordResult> {
  try {
    await fetch(forgotPasswordEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    })
    return 'submitted'
  } catch {
    return 'network-error'
  }
}

/**
 * Complete a password reset using the token from the reset link.
 *
 * The token is only forwarded to the request and is never logged, stored, or
 * returned to the caller.
 */
export async function resetPassword(token: string, password: string): Promise<ResetPasswordResult> {
  try {
    const response = await fetch(resetPasswordEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, password }),
    })

    if (response.ok) {
      return 'success'
    }

    // Mirrors the existing /auth/verify-email convention where 400 signals an
    // invalid, expired, or already-used token. Any other status is generic.
    if (response.status === 400) {
      return 'invalid-token'
    }

    return 'error'
  } catch {
    return 'error'
  }
}
