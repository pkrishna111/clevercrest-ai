import { useCallback, useState, type PropsWithChildren } from 'react'
import { useNavigate } from 'react-router-dom'
import { routePaths } from './router/routes'
import { useAuth } from './auth/useAuth'
import { CrestMark } from '../components/brand/CrestMark'
import { ThemeToggle } from '../components/theme/ThemeToggle'

const foundationNavigation = ['Foundation', 'Surfaces', 'Themes']

export function AppShell({ children }: PropsWithChildren) {
  const navigate = useNavigate()
  const { currentUser, logout: authLogout } = useAuth()
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  const handleLogout = useCallback(async () => {
    if (isLoggingOut) return
    setIsLoggingOut(true)
    try {
      await authLogout()
    } finally {
      navigate(routePaths.login, { replace: true })
    }
  }, [authLogout, isLoggingOut, navigate])

  return <div className="app-shell"><aside className="navigation-rail" aria-label="Foundation navigation"><a className="brand" href="#foundation" aria-label="CleverCrest foundation"><CrestMark /><span>CleverCrest</span></a><nav className="navigation-list">{foundationNavigation.map((item) => <a className={item === 'Foundation' ? 'navigation-item is-active' : 'navigation-item'} href={`#${item.toLowerCase()}`} key={item}>{item}</a>)}</nav><p className="navigation-caption">Crested Intelligence</p></aside><div className="app-frame"><header className="app-header"><div className="app-header-left"><p className="eyebrow">Product foundation</p>{currentUser && <p className="app-header-user" aria-live="polite">Signed in as <span>{currentUser.email}</span></p>}</div><div className="app-header-actions"><ThemeToggle /><button className="app-logout" type="button" onClick={handleLogout} disabled={isLoggingOut} aria-label="Sign out of CleverCrest">{isLoggingOut ? 'Signing out…' : 'Sign out'}</button></div></header><main className="main-content">{children}</main></div></div>
}
