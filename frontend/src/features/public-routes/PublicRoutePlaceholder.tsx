import { CrestMark } from '../../components/brand/CrestMark'
import { ThemeToggle } from '../../components/theme/ThemeToggle'

interface PublicRoutePlaceholderProps {
  title: string
}

export function PublicRoutePlaceholder({ title }: PublicRoutePlaceholderProps) {
  return <main className="public-route-placeholder"><header className="public-route-header"><div className="brand"><CrestMark /><span>CleverCrest</span></div><ThemeToggle /></header><section className="public-route-content" aria-labelledby="public-route-title"><p className="eyebrow">Route placeholder</p><h1 id="public-route-title">{title}</h1><p>This route is reserved for the future CleverCrest experience.</p></section></main>
}
