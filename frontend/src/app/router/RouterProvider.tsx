import { BrowserRouter } from 'react-router-dom'
import { AppRouter } from './AppRouter'

export function RouterProvider() {
  return <BrowserRouter><AppRouter /></BrowserRouter>
}
