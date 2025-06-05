'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { href: '/', label: 'Dashboard', icon: '📊' },
    { href: '/daily_entry', label: 'Daily Entry', icon: '✏️' },
    { href: '/patterns', label: 'Patterns', icon: '🔍' },
    { href: '/recommendations', label: 'Recommendations', icon: '💡' },
    { href: '/history', label: 'History', icon: '📚' },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <Link href="/" className="brand-link">
            <span className="brand-icon">🧠</span>
            <span className="brand-text">WellnessAI</span>
          </Link>
        </div>

        <div className="navbar-nav">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`nav-link ${pathname === item.href ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-text">{item.label}</span>
            </Link>
          ))}
        </div>

        <div className="navbar-utils">
          <div className="user-menu">
            <div className="user-avatar">U</div>
          </div>
        </div>
      </div>
    </nav>
  );
}