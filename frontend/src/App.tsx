import { ThemeProvider } from './app/theme/ThemeProvider'
import { AuthProvider } from './app/auth/AuthProvider'
import { RouterProvider } from './app/router/RouterProvider'

function App() {
  return <ThemeProvider><AuthProvider><RouterProvider /></AuthProvider></ThemeProvider>
}

export default App
