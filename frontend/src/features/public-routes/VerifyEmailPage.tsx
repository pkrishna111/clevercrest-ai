import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { routePaths } from '../../app/router/routes'
import { CrestMark } from '../../components/brand/CrestMark'
import { ThemeToggle } from '../../components/theme/ThemeToggle'

type VerificationStatus = 'loading' | 'success' | 'rejected' | 'unavailable' | 'missing'

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/+$/, '')

const statusCopy: Record<VerificationStatus, { label: string; title: string; message: string }> = {
  loading: {
    label: 'Verification in progress',
    title: 'Verifying your email',
    message: "We're confirming your email address. This should only take a moment.",
  },
  success: {
    label: 'Verification complete',
    title: 'Email verified',
    message: 'Your email address has been successfully verified. Your CleverCrest account is ready for the next step.',
  },
  rejected: {
    label: 'Verification failed',
    title: 'Verification failed',
    message: 'This verification link is invalid, expired, or has already been used. You can request a new verification email later.',
  },
  unavailable: {
    label: 'Verification unavailable',
    title: 'Unable to verify right now',
    message: "We couldn't verify your email right now. Please check your connection and try again.",
  },
  missing: {
    label: 'Invalid verification link',
    title: 'Invalid verification link',
    message: 'This verification link is missing the information needed to confirm your email address.',
  },
}

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const [status, setStatus] = useState<VerificationStatus>(token ? 'loading' : 'missing')
  const requestedToken = useRef<string | null>(null)

  const verifyEmail = useCallback(async () => {
    if (!token) {
      setStatus('missing')
      return
    }

    setStatus('loading')
    const verificationUrl = new URL(`${apiBaseUrl}/auth/verify-email`)
    verificationUrl.searchParams.set('token', token)

    try {
      const response = await fetch(verificationUrl, { method: 'GET' })
      setStatus(response.status === 200 ? 'success' : response.status === 400 ? 'rejected' : 'unavailable')
    } catch {
      setStatus('unavailable')
    }
  }, [token])

  useEffect(() => {
    if (!token) {
      return
    }

    if (requestedToken.current === token) {
      return
    }

    requestedToken.current = token
    void verifyEmail()
  }, [token, verifyEmail])

  const content = statusCopy[status]

  return <main className="verify-email-page"><header className="verify-email-header"><Link className="brand" to={routePaths.app} aria-label="CleverCrest"><CrestMark /><span>CleverCrest</span></Link><ThemeToggle /></header><div className="verify-email-layout"><section className="verify-email-identity" aria-labelledby="verify-identity-title"><div className="verify-email-crest" aria-hidden="true"><span /><span /><span /></div><p className="eyebrow">CleverCrest AI</p><h1 id="verify-identity-title">Secure organizational knowledge, thoughtfully connected.</h1><p>Verification keeps your access to CleverCrest deliberate and dependable.</p></section><section className="verify-email-panel" aria-labelledby="verification-title"><div className={`verification-status verification-status--${status}`} role="status" aria-live="polite" aria-atomic="true"><span className="verification-status-mark" aria-hidden="true" /><span>{content.label}</span></div><h2 id="verification-title">{content.title}</h2><p>{content.message}</p>{status === 'loading' && <span className="verification-loading" aria-hidden="true" />}{status === 'success' && <Link className="verification-action verification-action--primary" to={routePaths.login}>Continue to login</Link>}{(status === 'rejected' || status === 'missing') && <Link className="verification-action verification-action--secondary" to={routePaths.login}>Back to login</Link>}{status === 'unavailable' && <div className="verification-actions"><button className="verification-action verification-action--primary" type="button" onClick={() => void verifyEmail()}>Try again</button><Link className="verification-action verification-action--secondary" to={routePaths.login}>Back to login</Link></div>}</section></div></main>
}
