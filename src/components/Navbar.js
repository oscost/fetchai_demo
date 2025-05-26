'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { href: '/', label: 'Dashboard', icon: '' },
    { href: '/agents', label: 'Agents', icon: '' },
    { href: '/daily_entry', label: 'Daily Entry', icon: '' },
    { href: '/history', label: 'History', icon: '' },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo/Brand */}
        <div className="navbar-brand">
          <Link href="/" className="brand-link">
            <span className="brand-icon">🧠</span>
            <span className="brand-text">Mood Mentor</span>
          </Link>
        </div>

        {/* Navigation Links */}
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
      </div>
    </nav>
  );
}