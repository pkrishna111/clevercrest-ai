export interface ModulePlaceholderProps {
  eyebrow: string
  title: string
  description?: string
}

export function ModulePlaceholder({ eyebrow, title, description }: ModulePlaceholderProps) {
  return (
    <section className="module-placeholder" aria-labelledby="module-placeholder-title">
      <div className="crest-divider" aria-hidden="true"><span /><span /></div>
      <p className="eyebrow">{eyebrow}</p>
      <h1 id="module-placeholder-title">{title}</h1>
      <p className="module-placeholder-description">{description ?? 'Module interface is being prepared.'}</p>
      <p className="module-placeholder-footnote">CleverCrest — Crested Intelligence</p>
    </section>
  )
}
