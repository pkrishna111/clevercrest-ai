import { useEffect, useState, type PropsWithChildren } from 'react'
import { ThemeContext, type Theme } from './ThemeContext'

function getInitialTheme(): Theme {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function ThemeProvider({ children }: PropsWithChildren) {
  const [theme, setTheme] = useState<Theme>(getInitialTheme)
  useEffect(() => { document.documentElement.dataset.theme = theme }, [theme])
  const toggleTheme = () => { setTheme((currentTheme) => currentTheme === 'light' ? 'dark' : 'light') }
  return <ThemeContext value={{ theme, toggleTheme }}>{children}</ThemeContext>
}
