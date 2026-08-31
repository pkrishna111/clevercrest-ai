import { ThemeProvider } from './app/theme/ThemeProvider'
import { RouterProvider } from './app/router/RouterProvider'

function App() {
  return <ThemeProvider><RouterProvider /></ThemeProvider>
}

export default App
