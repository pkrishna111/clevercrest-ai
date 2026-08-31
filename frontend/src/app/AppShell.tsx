import type { PropsWithChildren } from 'react'
import { CrestMark } from '../components/brand/CrestMark'
import { ThemeToggle } from '../components/theme/ThemeToggle'

const foundationNavigation = ['Foundation', 'Surfaces', 'Themes']

export function AppShell({ children }: PropsWithChildren) {
  return <div className="app-shell"><aside className="navigation-rail" aria-label="Foundation navigation"><a className="brand" href="#foundation" aria-label="CleverCrest foundation"><CrestMark /><span>CleverCrest</span></a><nav className="navigation-list">{foundationNavigation.map((item) => <a className={item === 'Foundation' ? 'navigation-item is-active' : 'navigation-item'} href={`#${item.toLowerCase()}`} key={item}>{item}</a>)}</nav><p className="navigation-caption">Crested Intelligence</p></aside><div className="app-frame"><header className="app-header"><p className="eyebrow">Product foundation</p><ThemeToggle /></header><main className="main-content">{children}</main></div></div>
}
