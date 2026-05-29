import { NavLink, Outlet } from 'react-router-dom';
import { FolderOpen, Settings } from 'lucide-react';
import logoWhite from '../../assets/logowhite.png';

const APP_VERSION = 'v0.1';

const NAV_ITEMS = [
  { to: '/', end: true, icon: FolderOpen, label: 'Casebook' },
  { to: '/settings', end: false, icon: Settings, label: 'Settings' },
];

export const AppShell = () => {
  return (
    <div
      className="flex h-screen w-full overflow-hidden"
      style={{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)', fontFamily: 'inherit' }}
    >
      {/* ── Sidebar ─────────────────────────────────────────────── */}
      <aside
        className="w-52 flex-shrink-0 flex flex-col justify-between z-10"
        style={{
          backgroundColor: 'var(--aletheia-navy)',
          borderRight: '1px solid rgba(255,255,255,0.06)',
        }}
      >
        {/* Logo / Brand */}
        <div className="flex flex-col">
          <div
            className="h-14 flex items-center px-4"
            style={{ borderBottom: '1px solid rgba(255,255,255,0.07)' }}
          >
            <img
              src={logoWhite}
              alt="Aletheia Clinical Workstation"
              className="select-none"
              style={{ height: '22px', width: 'auto', objectFit: 'contain' }}
            />
          </div>

          {/* Navigation */}
          <nav className="flex flex-col px-3 pt-4 gap-0.5">
            {NAV_ITEMS.map(({ to, end, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) => [
                  'flex items-center gap-2.5 px-3 py-2 text-xs font-medium outline-none select-none transition-all',
                  'focus-visible:ring-0',
                  isActive
                    ? 'text-white'
                    : 'text-[rgba(255,255,255,0.48)] hover:text-[rgba(255,255,255,0.80)]',
                ].join(' ')}
                style={({ isActive }) => ({
                  borderRadius: 'var(--radius-1)',
                  backgroundColor: isActive ? 'rgba(255,255,255,0.10)' : 'transparent',
                  transitionDuration: 'var(--motion-fast)',
                  transitionTimingFunction: 'var(--ease-standard)',
                  borderLeft: isActive ? '2px solid rgba(255,255,255,0.55)' : '2px solid transparent',
                  paddingLeft: isActive ? '10px' : '12px',
                })}
              >
                <Icon className="w-3.5 h-3.5 flex-shrink-0" />
                <span>{label}</span>
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Footer */}
        <div
          className="px-5 pb-[75px] pt-3"
          style={{ borderTop: '1px solid rgba(255,255,255,0.07)' }}
        >
          <div
            className="text-[10px] font-medium"
            style={{ color: 'rgba(255,255,255,0.22)', letterSpacing: '0.04em', textTransform: 'uppercase' }}
          >
            Aletheia {APP_VERSION}
          </div>
        </div>
      </aside>

      {/* ── Main Content ─────────────────────────────────────────── */}
      <main
        className="flex-1 flex flex-col overflow-auto pb-[90px]"
        style={{ backgroundColor: 'var(--bg-primary)' }}
      >
        <Outlet />
      </main>

      {/* ── Global Legal Footer ─────────────────────────────────── */}
      <div
        className="fixed bottom-0 left-0 right-0 flex flex-col items-center justify-center px-4 py-2.5 text-center select-none"
        style={{
          zIndex: 999, // Ensure it's above modals if possible, or at least above main content
          backgroundColor: 'rgba(255, 255, 255, 0.85)',
          backdropFilter: 'blur(8px)',
          WebkitBackdropFilter: 'blur(8px)',
          borderTop: '1px solid var(--border-subtle)',
          boxShadow: '0 -4px 24px rgba(22, 44, 65, 0.03)',
        }}
      >
        <div
          className="text-[9px] font-bold uppercase tracking-[0.08em] mb-0.5"
          style={{ color: 'var(--text-secondary)' }}
        >
          BIOWESS © 2026
        </div>
        <div
          className="text-[9px] leading-[1.3] max-w-5xl mx-auto"
          style={{ color: 'var(--text-muted)' }}
        >
          For educational and informational purposes only. This application does not provide medical advice, diagnosis, or treatment and must not be used as a substitute for professional clinical judgment or consultation with qualified healthcare providers.
          <br />
          All outputs are AI-generated and may contain inaccuracies. Clinical decisions must always be validated by licensed professionals and primary medical sources.
        </div>
      </div>
    </div>
  );
};
