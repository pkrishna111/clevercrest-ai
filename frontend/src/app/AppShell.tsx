import { useCallback, useState, type PropsWithChildren, type ReactElement } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { authenticatedNavigation, routePaths } from './router/routes'
import { useAuth } from './auth/useAuth'
import { CrestMark } from '../components/brand/CrestMark'
import { ThemeToggle } from '../components/theme/ThemeToggle'

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

  let lastGroup: string | null = null
  const navItems: ReactElement[] = []
  for (const item of authenticatedNavigation) {
    if (item.eyebrow !== lastGroup) {
      navItems.push(
        <li className="navigation-group" key={`group-${item.eyebrow}`}>
          <span className="navigation-group-label">{item.eyebrow}</span>
        </li>
      )
      lastGroup = item.eyebrow
    }
    navItems.push(
      <li key={item.path}>
        <NavLink
          to={item.path}
          end={item.path !== routePaths.collections && item.path !== routePaths.documents}
          className={({ isActive }) => `navigation-item${isActive ? ' is-active' : ''}`}
        >
          {item.label}
        </NavLink>
      </li>
    )
  }

  return <div className="app-shell"><aside className="navigation-rail" aria-label="CleverCrest navigation"><Link className="brand" to={routePaths.app} aria-label="CleverCrest"><CrestMark /><span>CleverCrest</span></Link><nav className="navigation-list" aria-label="Product modules"><ul>{navItems}</ul></nav><p className="navigation-caption">Crested Intelligence</p></aside><div className="app-frame"><header className="app-header"><div className="app-header-left"><p className="eyebrow">Product foundation</p>{currentUser && <p className="app-header-user" aria-live="polite">Signed in as <span>{currentUser.email}</span></p>}</div><div className="app-header-actions"><ThemeToggle /><button className="app-logout" type="button" onClick={handleLogout} disabled={isLoggingOut} aria-label="Sign out of CleverCrest">{isLoggingOut ? 'Signing out…' : 'Sign out'}</button></div></header><main className="main-content">{children}</main></div></div>
}
