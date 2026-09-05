import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { routePaths } from '../../app/router/routes'
import { useAuth } from '../../app/auth/useAuth'
import { CrestMark } from '../../components/brand/CrestMark'
import { ThemeToggle } from '../../components/theme/ThemeToggle'

type FieldErrors = {
  email?: string
  password?: string
}

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/+$/, '')

function getForbiddenLoginMessage(message: string): string {
  const normalizedMessage = message.toLowerCase()

  if (normalizedMessage.includes('verify')) {
    return 'Please verify your email before signing in.'
  }

  if (normalizedMessage.includes('inactive')) {
    return 'This account is inactive. Please contact your organization administrator.'
  }

  if (normalizedMessage.includes('suspended')) {
    return 'This account is suspended. Please contact your organization administrator.'
  }

  return 'This account cannot sign in right now. Please contact your organization administrator.'
}

export function LoginPage() {
  const navigate = useNavigate()
  const { refreshSession } = useAuth()
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})
  const [requestError, setRequestError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (isSubmitting) return

    const form = event.currentTarget
    const formData = new FormData(form)
    const email = String(formData.get('email') ?? '').trim()
    const password = String(formData.get('password') ?? '')
    const emailInput = form.elements.namedItem('email') as HTMLInputElement
    const errors: FieldErrors = {}

    if (!email) {
      errors.email = 'Enter your email address.'
    } else if (!emailInput.validity.valid) {
      errors.email = 'Enter a valid email address.'
    }

    if (!password) {
      errors.password = 'Enter your password.'
    }

    setFieldErrors(errors)
    setRequestError(null)
    if (Object.keys(errors).length > 0) return

    setIsSubmitting(true)
    try {
      const response = await fetch(`${apiBaseUrl}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      })

      if (response.status === 200) {
        await refreshSession()
        navigate(routePaths.app)
        return
      }

      if (response.status === 401) {
        setRequestError('Invalid email or password.')
        return
      }

      if (response.status === 403) {
        let backendMessage = ''
        try {
          const payload: unknown = await response.json()
          if (typeof payload === 'object' && payload !== null && 'detail' in payload && typeof payload.detail === 'string') {
            backendMessage = payload.detail
          }
        } catch {
          // Keep the account-status response generic when no JSON message is available.
        }
        setRequestError(getForbiddenLoginMessage(backendMessage))
        return
      }

      setRequestError('Unable to sign in right now. Please try again.')
    } catch {
      setRequestError("We couldn't connect to CleverCrest. Check your connection and try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  return <main className="login-page"><header className="login-header"><Link className="brand" to={routePaths.app} aria-label="CleverCrest"><CrestMark /><span>CleverCrest</span></Link><ThemeToggle /></header><div className="login-layout"><section className="login-identity" aria-labelledby="login-identity-title"><div className="login-crest" aria-hidden="true"><span /><span /><span /></div><p className="eyebrow">CleverCrest AI</p><h1 id="login-identity-title">Welcome back to deliberate intelligence.</h1><p>Sign in to continue to your CleverCrest workspace.</p></section><section className="login-panel" aria-labelledby="login-title"><p className="eyebrow">Account access</p><h2 id="login-title">Sign in</h2><p className="login-intro">Use your verified CleverCrest account to continue.</p><form className="login-form" noValidate onSubmit={handleSubmit}><div className="login-field"><label htmlFor="login-email">Email</label><input id="login-email" name="email" type="email" autoComplete="email" maxLength={320} required aria-invalid={Boolean(fieldErrors.email)} aria-describedby={fieldErrors.email ? 'login-email-error' : undefined} />{fieldErrors.email && <p className="login-field-error" id="login-email-error">{fieldErrors.email}</p>}</div><div className="login-field"><label htmlFor="login-password">Password</label><input id="login-password" name="password" type="password" autoComplete="current-password" maxLength={128} required aria-invalid={Boolean(fieldErrors.password)} aria-describedby={fieldErrors.password ? 'login-password-error' : undefined} />{fieldErrors.password && <p className="login-field-error" id="login-password-error">{fieldErrors.password}</p>}</div>{requestError && <div className="login-error" role="alert"><span aria-hidden="true" />{requestError}</div>}<div className="login-actions"><button className="login-submit" type="submit" disabled={isSubmitting}>{isSubmitting ? 'Signing in…' : 'Sign in'}</button><Link className="login-secondary" to={routePaths.forgotPassword}>Forgot password?</Link></div>{isSubmitting && <p className="login-request-status" role="status" aria-live="polite">Signing in to CleverCrest.</p>}</form><p className="login-registration">Don&apos;t have an account? <Link to={routePaths.register}>Create an account</Link></p></section></div></main>
}
