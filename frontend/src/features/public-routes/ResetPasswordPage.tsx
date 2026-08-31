import { useState, type FormEvent } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { routePaths } from '../../app/router/routes'
import { CrestMark } from '../../components/brand/CrestMark'
import { ThemeToggle } from '../../components/theme/ThemeToggle'
import { resetPassword } from './passwordResetApi'

type FieldErrors = {
  password?: string
  confirmPassword?: string
}

type Outcome = 'pending' | 'success' | 'invalid'

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  // The reset token lives only here (component memory) and is forwarded to the
  // reset request. It is never logged, persisted, decoded, or displayed.
  const token = searchParams.get('token')

  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})
  const [requestError, setRequestError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [outcome, setOutcome] = useState<Outcome>('pending')

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (isSubmitting || !token) return

    const form = event.currentTarget
    const formData = new FormData(form)
    const password = String(formData.get('password') ?? '')
    const confirmPassword = String(formData.get('confirm_password') ?? '')
    const errors: FieldErrors = {}

    if (!password) {
      errors.password = 'Enter a new password.'
    } else if (password.length < 8) {
      errors.password = 'Password must be at least 8 characters.'
    }
    if (!confirmPassword) {
      errors.confirmPassword = 'Confirm your new password.'
    } else if (confirmPassword !== password) {
      errors.confirmPassword = 'Passwords do not match.'
    }

    setFieldErrors(errors)
    setRequestError(null)
    if (Object.keys(errors).length > 0) return

    setIsSubmitting(true)
    const result = await resetPassword(token, password)
    setIsSubmitting(false)

    if (result === 'success') {
      setOutcome('success')
    } else if (result === 'invalid-token') {
      setOutcome('invalid')
    } else {
      setRequestError("We couldn't reset your password right now. Please try again.")
    }
  }

  const hasToken = Boolean(token)
  const showInvalid = !hasToken || outcome === 'invalid'
  const invalidCopy = hasToken
    ? {
        label: 'Reset link expired',
        title: 'Reset link no longer valid',
        message: 'This password reset link is invalid, expired, or has already been used. Request a new link to continue.',
      }
    : {
        label: 'Invalid reset link',
        title: 'Invalid reset link',
        message: 'This password reset link is missing or incomplete. Request a new link to continue.',
      }

  const panelBody = showInvalid ? (
    <div className="reset-state" role="status" aria-live="polite" aria-atomic="true">
      <div className="reset-status reset-status--invalid"><span className="reset-status-mark" aria-hidden="true" /><span>{invalidCopy.label}</span></div>
      <h2 id="reset-title">{invalidCopy.title}</h2>
      <p>{invalidCopy.message}</p>
      <div className="reset-state-actions"><Link className="reset-action reset-action--primary" to={routePaths.login}>Back to login</Link><Link className="reset-action reset-action--secondary" to={routePaths.forgotPassword}>Request a new link</Link></div>
    </div>
  ) : outcome === 'success' ? (
    <div className="reset-state" role="status" aria-live="polite" aria-atomic="true">
      <div className="reset-status reset-status--success"><span className="reset-status-mark" aria-hidden="true" /><span>Password updated</span></div>
      <h2 id="reset-title">Password reset complete</h2>
      <p>Your password has been updated. You can now sign in with your new password.</p>
      <Link className="reset-action reset-action--primary" to={routePaths.login}>Continue to login</Link>
    </div>
  ) : (
    <>
      <p className="eyebrow">Account recovery</p>
      <h2 id="reset-title">Set a new password</h2>
      <p className="reset-intro">Choose a new password for your CleverCrest account.</p>
      <form className="reset-form" noValidate onSubmit={handleSubmit}>
        <fieldset disabled={isSubmitting}>
          <div className="reset-field"><label htmlFor="reset-password">New password</label><input id="reset-password" name="password" type="password" autoComplete="new-password" maxLength={128} required aria-invalid={Boolean(fieldErrors.password)} aria-describedby={fieldErrors.password ? 'reset-password-error' : undefined} />{fieldErrors.password && <p className="reset-field-error" id="reset-password-error">{fieldErrors.password}</p>}</div>
          <div className="reset-field"><label htmlFor="reset-confirm-password">Confirm new password</label><input id="reset-confirm-password" name="confirm_password" type="password" autoComplete="new-password" maxLength={128} required aria-invalid={Boolean(fieldErrors.confirmPassword)} aria-describedby={fieldErrors.confirmPassword ? 'reset-confirm-password-error' : undefined} />{fieldErrors.confirmPassword && <p className="reset-field-error" id="reset-confirm-password-error">{fieldErrors.confirmPassword}</p>}</div>
          {requestError && <div className="reset-error" role="alert"><span aria-hidden="true" />{requestError}</div>}
          <div className="reset-actions"><button className="reset-submit" type="submit" disabled={isSubmitting}>{isSubmitting ? 'Updating…' : 'Reset password'}</button><Link className="reset-secondary" to={routePaths.login}>Back to login</Link></div>
        </fieldset>
        {isSubmitting && <p className="reset-request-status" role="status" aria-live="polite">Updating your password.</p>}
      </form>
    </>
  )

  return <main className="reset-page"><header className="reset-header"><Link className="brand" to={routePaths.app} aria-label="CleverCrest"><CrestMark /><span>CleverCrest</span></Link><ThemeToggle /></header><div className="reset-layout"><section className="reset-identity" aria-labelledby="reset-identity-title"><div className="reset-crest" aria-hidden="true"><span /><span /><span /></div><p className="eyebrow">CleverCrest AI</p><h1 id="reset-identity-title">Set a new password, securely.</h1><p>Create a strong password to keep your CleverCrest workspace protected.</p></section><section className="reset-panel" aria-labelledby="reset-title">{panelBody}</section></div></main>
}
