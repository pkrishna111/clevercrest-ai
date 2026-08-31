import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { routePaths } from '../../app/router/routes'
import { CrestMark } from '../../components/brand/CrestMark'
import { ThemeToggle } from '../../components/theme/ThemeToggle'

type FieldErrors = {
  firstName?: string
  email?: string
  organizationName?: string
  password?: string
  confirmPassword?: string
}

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/+$/, '')

export function RegisterPage() {
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})
  const [requestError, setRequestError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isRegistered, setIsRegistered] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (isSubmitting) return

    const form = event.currentTarget
    const formData = new FormData(form)
    const firstName = String(formData.get('first_name') ?? '').trim()
    const lastNameValue = String(formData.get('last_name') ?? '').trim()
    const email = String(formData.get('email') ?? '').trim()
    const organizationName = String(formData.get('organization_name') ?? '').trim()
    const password = String(formData.get('password') ?? '')
    const confirmPassword = String(formData.get('confirm_password') ?? '')
    const emailInput = form.elements.namedItem('email') as HTMLInputElement
    const errors: FieldErrors = {}

    if (!firstName) errors.firstName = 'Enter your first name.'
    if (!email) {
      errors.email = 'Enter your email address.'
    } else if (!emailInput.validity.valid) {
      errors.email = 'Enter a valid email address.'
    }
    if (!organizationName) errors.organizationName = 'Enter your organization name.'
    if (!password) {
      errors.password = 'Create a password.'
    } else if (password.length < 8) {
      errors.password = 'Password must be at least 8 characters.'
    }
    if (!confirmPassword) {
      errors.confirmPassword = 'Confirm your password.'
    } else if (confirmPassword !== password) {
      errors.confirmPassword = 'Passwords do not match.'
    }

    setFieldErrors(errors)
    setRequestError(null)
    if (Object.keys(errors).length > 0) return

    setIsSubmitting(true)
    try {
      const response = await fetch(`${apiBaseUrl}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastNameValue || null,
          email,
          password,
          organization_name: organizationName,
        }),
      })

      if (response.status === 201) {
        setIsRegistered(true)
        return
      }

      if (response.status === 409) {
        setRequestError('An account with this email already exists.')
        return
      }
      if (response.status === 422) {
        setRequestError('Please check the information you entered and try again.')
        return
      }
      if (response.status === 503) {
        setRequestError("Your account was created, but we couldn't send the verification email right now. Please try again later.")
        return
      }
      setRequestError('Unable to create your account right now. Please try again.')
    } catch {
      setRequestError("We couldn't connect to CleverCrest. Check your connection and try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  return <main className="register-page">
    <header className="register-header">
      <Link className="brand" to={routePaths.app} aria-label="CleverCrest"><CrestMark /><span>CleverCrest</span></Link>
      <ThemeToggle />
    </header>
    <div className="register-layout">
      <section className="register-identity" aria-labelledby="register-identity-title">
        <div className="register-crest" aria-hidden="true"><span /><span /><span /></div>
        <p className="eyebrow">CleverCrest AI</p>
        <h1 id="register-identity-title">Build a more deliberate workspace.</h1>
        <p>Create your CleverCrest organization and begin with a verified account.</p>
      </section>
      <section className="register-panel" aria-labelledby="register-title">
        {isRegistered ? <div className="register-success" role="status" aria-live="polite" aria-atomic="true">
          <p className="eyebrow">Registration complete</p>
          <h2 id="register-title">Check your email</h2>
          <p>Your CleverCrest account has been created. We sent a verification link to your email address. Verify your email before signing in.</p>
          <Link className="register-login" to={routePaths.login}>Go to login</Link>
          <p className="register-secondary">After verification, return here to sign in.</p>
        </div> : <>
          <p className="eyebrow">Create your account</p>
          <h2 id="register-title">Register</h2>
          <p className="register-intro">Set up your account and organization to get started.</p>
          <form className="register-form" noValidate onSubmit={handleSubmit}>
            <fieldset disabled={isSubmitting}>
              <div className="register-field"><label htmlFor="register-first-name">First name</label><input id="register-first-name" name="first_name" type="text" autoComplete="given-name" maxLength={100} required aria-invalid={Boolean(fieldErrors.firstName)} aria-describedby={fieldErrors.firstName ? 'register-first-name-error' : undefined} />{fieldErrors.firstName && <p className="register-field-error" id="register-first-name-error">{fieldErrors.firstName}</p>}</div>
              <div className="register-field"><label htmlFor="register-last-name">Last name <span>(optional)</span></label><input id="register-last-name" name="last_name" type="text" autoComplete="family-name" maxLength={100} /></div>
              <div className="register-field"><label htmlFor="register-email">Email</label><input id="register-email" name="email" type="email" autoComplete="email" maxLength={320} required aria-invalid={Boolean(fieldErrors.email)} aria-describedby={fieldErrors.email ? 'register-email-error' : undefined} />{fieldErrors.email && <p className="register-field-error" id="register-email-error">{fieldErrors.email}</p>}</div>
              <div className="register-field"><label htmlFor="register-organization-name">Organization name</label><input id="register-organization-name" name="organization_name" type="text" autoComplete="organization" maxLength={255} required aria-invalid={Boolean(fieldErrors.organizationName)} aria-describedby={fieldErrors.organizationName ? 'register-organization-name-error' : undefined} />{fieldErrors.organizationName && <p className="register-field-error" id="register-organization-name-error">{fieldErrors.organizationName}</p>}</div>
              <div className="register-field"><label htmlFor="register-password">Password</label><input id="register-password" name="password" type="password" autoComplete="new-password" maxLength={128} required aria-invalid={Boolean(fieldErrors.password)} aria-describedby={fieldErrors.password ? 'register-password-error' : undefined} />{fieldErrors.password && <p className="register-field-error" id="register-password-error">{fieldErrors.password}</p>}</div>
              <div className="register-field"><label htmlFor="register-confirm-password">Confirm password</label><input id="register-confirm-password" name="confirm_password" type="password" autoComplete="new-password" maxLength={128} required aria-invalid={Boolean(fieldErrors.confirmPassword)} aria-describedby={fieldErrors.confirmPassword ? 'register-confirm-password-error' : undefined} />{fieldErrors.confirmPassword && <p className="register-field-error" id="register-confirm-password-error">{fieldErrors.confirmPassword}</p>}</div>
              {requestError && <div className="register-error" role="alert"><span aria-hidden="true" />{requestError}</div>}
              <div className="register-actions"><button className="register-submit" type="submit" disabled={isSubmitting}>{isSubmitting ? 'Creating account…' : 'Create account'}</button></div>
            </fieldset>
            {isSubmitting && <p className="register-request-status" role="status" aria-live="polite">Creating your CleverCrest account.</p>}
          </form>
          <p className="register-login">Already have an account? <Link to={routePaths.login}>Sign in</Link></p>
        </>}
      </section>
    </div>
  </main>
}
