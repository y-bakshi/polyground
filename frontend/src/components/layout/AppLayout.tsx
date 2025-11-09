import { NavLink, Link } from 'react-router-dom'
import type { PropsWithChildren } from 'react'
import { useUnreadAlertCount } from '../../hooks/useAlerts'

const navItems = [
  { to: '/', label: 'Overview' },
  { to: '/alerts', label: 'Alerts' },
]

export const AppLayout = ({ children }: PropsWithChildren) => {
  const unreadCount = useUnreadAlertCount()

  return (
    <div className="app-shell">
      <header className="app-header">
        <Link to="/" className="brand">
          <span className="brand-mark" aria-hidden>
            PM
          </span>
          <div>
            <strong>Polymarket Scout</strong>
            <p>Pin, monitor, react faster.</p>
          </div>
        </Link>
        <nav className="app-nav">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
              {item.label}
              {item.to === '/alerts' && unreadCount > 0 && <span className="badge">{unreadCount}</span>}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="app-content">{children}</main>
    </div>
  )
}
