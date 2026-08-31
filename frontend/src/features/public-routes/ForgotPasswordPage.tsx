import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { routePaths } from '../../app/router/routes'
import { CrestMark } from '../../components/brand/CrestMark'
import { ThemeToggle } from '../../components/theme/ThemeToggle'
import { requestPasswordReset } from './passwordResetApi'

type FieldErrors = {
  email?: string
}

export function ForgotPasswordPage() {
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})
  const [requestError, setRequestError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (isSubmitting) return

    const form = event.currentTarget
    const formData = new FormData(form)
    const email = String(formData.get('email') ?? '').trim()
    const emailInput = form.elements.namedItem('email') as HTMLInputElement
    const errors: FieldErrors = {}

    if (!email) {
      errors.email = 'Enter your email address.'
    } else if (!emailInput.validity.valid) {
      errors.email = 'Enter a valid email address.'
    }

    setFieldErrors(errors)
    setRequestError(null)
    if (Object.keys(errors).length > 0) return

    setIsSubmitting(true)
    const result = await requestPasswordReset(email)
    setIsSubmitting(false)

    if (result === 'submitted') {
      // Generic success — never reveals whether the email address exists.
      setIsSubmitted(true)
      return
    }

    setRequestError("We couldn't connect to CleverCrest. Check your connection and try again.")
  }

  return <main className="forgot-page"><header className="forgot-header"><Link className="brand" to={routePaths.app} aria-label="CleverCrest"><CrestMark /><span>CleverCrest</span></Link><ThemeToggle /></header><div className="forgot-layout"><section className="forgot-identity" aria-labelledby="forgot-identity-title"><div className="forgot-crest" aria-hidden="true"><span /><span /><span /></div><p className="eyebrow">CleverCrest AI</p><h1 id="forgot-identity-title">Regain access, deliberately.</h1><p>We'll help you set a new password and get back to your CleverCrest workspace.</p></section><section className="forgot-panel" aria-labelledby="forgot-title">{isSubmitted ? <div className="forgot-success" role="status" aria-live="polite" aria-atomic="true"><p className="eyebrow">Request received</p><h2 id="forgot-title">Check your email</h2><p>If an account exists for this email address, we'll send instructions to reset your password.</p><Link className="forgot-login" to={routePaths.login}>Back to login</Link><p className="forgot-secondary-note">Didn't get an email? Check your spam folder or try again in a few minutes.</p></div> : <><p className="eyebrow">Account recovery</p><h2 id="forgot-title">Reset your password</h2><p className="forgot-intro">Enter the email address for your CleverCrest account and we'll send you a link to reset your password.</p><form className="forgot-form" noValidate onSubmit={handleSubmit}><fieldset disabled={isSubmitting}><div className="forgot-field"><label htmlFor="forgot-email">Email</label><input id="forgot-email" name="email" type="email" autoComplete="email" maxLength={320} required aria-invalid={Boolean(fieldErrors.email)} aria-describedby={fieldErrors.email ? 'forgot-email-error' : undefined} />{fieldErrors.email && <p className="forgot-field-error" id="forgot-email-error">{fieldErrors.email}</p>}</div>{requestError && <div className="forgot-error" role="alert"><span aria-hidden="true" />{requestError}</div>}<div className="forgot-actions"><button className="forgot-submit" type="submit" disabled={isSubmitting}>{isSubmitting ? 'Sending…' : 'Send reset instructions'}</button><Link className="forgot-secondary" to={routePaths.login}>Back to login</Link></div></fieldset>{isSubmitting && <p className="forgot-request-status" role="status" aria-live="polite">Sending reset instructions.</p>}</form></>}</section></div></main>
}
