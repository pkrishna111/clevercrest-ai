import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import type { ActivityStatus, DashboardMetric, DashboardOperationalItem, DashboardOverview } from '../../app/dashboard/dashboardApi'
import { getDashboardOverview } from '../../app/dashboard/dashboardApi'
import { routePaths } from '../../app/router/routes'
import { useAuth } from '../../app/auth/useAuth'

const STATUS_LABELS: Record<ActivityStatus, string> = {
  approved: 'Approved',
  processing: 'Processing',
  pending: 'Pending',
  rejected: 'Rejected',
  draft: 'Draft',
  failed: 'Failed',
}

function statusClass(status: ActivityStatus | null | undefined): string {
  switch (status) {
    case 'approved':
      return 'dashboard-status dashboard-status-approved'
    case 'processing':
      return 'dashboard-status dashboard-status-processing'
    case 'pending':
      return 'dashboard-status dashboard-status-pending'
    case 'rejected':
      return 'dashboard-status dashboard-status-rejected'
    case 'failed':
      return 'dashboard-status dashboard-status-failed'
    case 'draft':
      return 'dashboard-status dashboard-status-draft'
    default:
      return 'dashboard-status dashboard-status-draft'
  }
}

function StatusBadge({ status }: { status: ActivityStatus | null }) {
  const label = status ? STATUS_LABELS[status] : 'Recorded'
  return <span className={statusClass(status)} aria-label={`Activity status: ${label}`}>{label}</span>
}

function MetricCard({ metric }: { metric: DashboardMetric }) {
  return (
    <article className="foundation-card dashboard-metric" aria-labelledby={`metric-${metric.id}`}>
      <div className="dashboard-metric-top">
        <span className="card-index">{metric.cardIndex}</span>
        <p className="eyebrow">{metric.eyebrow}</p>
      </div>
      <h2 className="dashboard-metric-title" id={`metric-${metric.id}`}>{metric.label}</h2>
      <p className="dashboard-metric-value" aria-label={`${metric.label}: ${metric.value.toLocaleString()}`}>{metric.value.toLocaleString()}</p>
      <p className="dashboard-metric-summary">{metric.summary}</p>
      <div className="dashboard-metric-foot">
        {metric.delta && (
          <p className={`dashboard-delta dashboard-delta-${metric.delta.sign}`}>
            {metric.delta.sign === 'up' ? '+' : '−'}{metric.delta.value}&nbsp;{metric.delta.period}
          </p>
        )}
        {metric.link && (
          <Link className="dashboard-link" to={metric.link.routePath} aria-label={`${metric.link.label} for ${metric.label}`}>
            {metric.link.label} →
          </Link>
        )}
      </div>
    </article>
  )
}

function OperationalCard({
  eyebrow,
  cardIndex,
  title,
  count,
  items,
  routePath,
  routeLabel,
}: {
  eyebrow: string
  cardIndex: string
  title: string
  count: string
  items: DashboardOperationalItem[]
  routePath: string
  routeLabel: string
}) {
  return (
    <section className="foundation-card dashboard-operational-card" aria-labelledby={`ops-${eyebrow.toLowerCase()}-title`}>
      <div className="dashboard-metric-top">
        <span className="card-index">{cardIndex}</span>
        <p className="eyebrow">{eyebrow}</p>
      </div>
      <div className="dashboard-operational-head">
        <h2 id={`ops-${eyebrow.toLowerCase()}-title`} className="dashboard-metric-title">{title}</h2>
        <p className="dashboard-operational-count">{count}</p>
      </div>
      <ul className="dashboard-operational-list" aria-label={title}>
        {items.map((item) => (
          <li key={item.id} className="dashboard-operational-item">
            <div>
              <p className="dashboard-operational-item-title">{item.title}</p>
              <p className="dashboard-operational-item-metadata">{item.metadata}</p>
            </div>
            <StatusBadge status={item.status} />
          </li>
        ))}
      </ul>
      <div className="dashboard-operational-foot">
        <Link className="dashboard-link" to={routePath}>{routeLabel} →</Link>
      </div>
    </section>
  )
}

function getGreetingFromTime(hour: number): string {
  if (hour >= 5 && hour < 12) return 'Good morning'
  if (hour >= 12 && hour < 17) return 'Good afternoon'
  return 'Good evening'
}

type DashboardRenderState =
  | { kind: 'loading' }
  | { kind: 'success'; overview: DashboardOverview }
  | { kind: 'error' }

function renderMark(status: ActivityStatus | null) {
  if (status === 'approved' || status === 'processing' || status === 'pending' || status === 'rejected' || status === 'failed') {
    return status
  }
  return undefined
}

export function DashboardPage() {
  const { currentUser } = useAuth()
  const [state, setState] = useState<DashboardRenderState>({ kind: 'loading' })

  const greeting = useMemo(() => {
    const base = getGreetingFromTime(new Date().getHours())
    const name = (currentUser?.first_name?.trim()) || null
    return name ? `${base}, ${name}.` : `${base}.`
  }, [currentUser])

  useEffect(() => {
    let cancelled = false
    void (async () => {
      const result = await getDashboardOverview()
      if (cancelled) return
      if (result.kind === 'success') setState({ kind: 'success', overview: result.overview })
      else setState({ kind: 'error' })
    })()
    return () => {
      cancelled = true
    }
  }, [])

  if (state.kind === 'loading') {
    return (
      <section className="dashboard-page dashboard-page-loading" aria-live="polite">
        <div className="crest-divider" aria-hidden="true"><span /><span /></div>
        <p className="eyebrow">Overview</p>
        <h1 className="dashboard-greeting">Preparing your organization overview…</h1>
      </section>
    )
  }

  if (state.kind === 'error') {
    return (
      <section className="dashboard-page dashboard-page-error" aria-live="assertive">
        <div className="crest-divider" aria-hidden="true"><span /><span /></div>
        <p className="eyebrow">Overview</p>
        <h1 className="dashboard-greeting">Dashboard data could not be loaded.</h1>
        <p className="dashboard-subheading">
          The organizational overview is temporarily unavailable. Return later or sign out if the issue continues.
        </p>
      </section>
    )
  }

  const { overview } = state
  const orgLine = overview.organizationName
    ? `Here's what is happening across ${overview.organizationName}.`
    : 'Here\'s what is happening across your organization.'

  return (
    <section className="dashboard-page" aria-labelledby="dashboard-greeting-title">
      <header className="dashboard-header">
        <div className="crest-divider" aria-hidden="true"><span /><span /></div>
        <p className="eyebrow">Overview</p>
        <h1 id="dashboard-greeting-title" className="dashboard-greeting">{greeting}</h1>
        <p className="dashboard-subheading">{orgLine}</p>
      </header>

      <section className="dashboard-section" aria-labelledby="metrics-heading">
        <div className="dashboard-section-header">
          <h2 id="metrics-heading" className="dashboard-section-title">At a glance</h2>
        </div>
        <div className="foundation-grid dashboard-metrics-grid" aria-label="Key metrics">
          {overview.metrics.map((metric) => <MetricCard key={metric.id} metric={metric} />)}
        </div>
      </section>

      <section className="dashboard-section" aria-labelledby="activity-heading">
        <div className="dashboard-section-header">
          <h2 id="activity-heading" className="dashboard-section-title">Recent activity</h2>
          <p className="eyebrow">Updated {new Date(overview.generatedAt).toLocaleString()}</p>
        </div>
        <ul className="dashboard-activity-list" aria-label="Recent activity items">
          {overview.recentActivity.map((item) => (
            <li key={item.id} className="dashboard-activity-item" data-status={renderMark(item.status)}>
              <div className="dashboard-activity-head">
                <p className="eyebrow dashboard-activity-timestamp">{item.timestamp}</p>
                {item.status !== undefined && item.status !== null && <StatusBadge status={item.status} />}
              </div>
              <p className="dashboard-activity-line">
                <strong>{item.actorName}</strong>
                {' '}{item.action}{' '}
                {item.route
                  ? <Link className="dashboard-activity-target" to={item.route}>{item.targetLabel}</Link>
                  : <span className="dashboard-activity-target">{item.targetLabel}</span>}
              </p>
              {item.actorEmail && (
                <p className="dashboard-activity-metadata">{item.actorEmail}</p>
              )}
            </li>
          ))}
        </ul>
      </section>

      <section className="dashboard-section" aria-labelledby="operations-heading">
        <div className="dashboard-section-header">
          <h2 id="operations-heading" className="dashboard-section-title">Operations</h2>
        </div>
        <div className="dashboard-operational-grid">
          <OperationalCard
            eyebrow="Approvals"
            cardIndex="A"
            title="Pending approvals"
            count={`${overview.pendingApprovals.length.toString()} pending`}
            items={overview.pendingApprovals}
            routePath={routePaths.approvalQueue}
            routeLabel="Go to Approval Queue"
          />
          <OperationalCard
            eyebrow="Processing"
            cardIndex="B"
            title="Processing jobs"
            count={`${overview.processingSummary.length.toString()} active or failed`}
            items={overview.processingSummary}
            routePath={routePaths.processingJobs}
            routeLabel="Go to Processing Jobs"
          />
        </div>
      </section>
    </section>
  )
}

export default DashboardPage
