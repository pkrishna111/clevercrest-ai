import { useTheme } from '../../app/theme/useTheme'
export function ThemeToggle() { const { theme, toggleTheme } = useTheme(); const nextTheme = theme === 'light' ? 'dark' : 'light'; return <button className="theme-toggle" type="button" onClick={toggleTheme}><span className="theme-toggle-indicator" aria-hidden="true" />Use {nextTheme} theme</button> }
