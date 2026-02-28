/**
 * Home.jsx - Menu principal tipo CLI: 6 tarjetas en bloque + Salir.
 * Mismas opciones que native_menu.py; click navega a cada ruta.
 */
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useMage } from '../context/MageContext'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { useEffect } from 'react'

const MENU_OPTIONS = [
  { to: '/scan', title: 'Scan directory', subtitle: 'Analyze types and sizes' },
  { to: '/import', title: 'Import documents', subtitle: 'Add files to the index' },
  { to: '/search', title: 'Search', subtitle: 'Search by keywords' },
  { to: '/explore', title: 'Explore documents', subtitle: 'Navigate and view content' },
  { to: '/organize', title: 'Organize files', subtitle: 'Move into folders by type/date/size' },
  { to: '/cleanup', title: 'Cleanup', subtitle: 'Find cache, logs and tiny files' },
]

export function Home() {
  const { user, logout } = useAuth()
  const { sayForScene } = useMage()

  useEffect(() => {
    sayForScene('home')
  }, [sayForScene])

  return (
    <div className="min-h-screen p-6">
      <header className="flex justify-between items-center mb-4 md:mb-8 border-b-2 border-[var(--pixel-border)] pb-4">
        <h1 className="text-[var(--pixel-accent)] text-lg font-pixel">WIZARD404</h1>
        <div className="flex items-center gap-4">
          <span className="text-xs text-[var(--pixel-muted)]">{user?.name}</span>
          <Button onClick={logout} variant="secondary" className="px-3 py-1">
            SALIR
          </Button>
        </div>
      </header>

      <div className="flex flex-col gap-2 md:gap-4 max-w-2xl ml-0 md:ml-[10%] mr-auto">
        {MENU_OPTIONS.map(({ to, title, subtitle }) => (
          <Link key={to} to={to} className="block w-full">
            <Card
              variant="light"
              borderWidth={4}
              className="card-menu p-2 md:p-4 cursor-pointer hover:border-[var(--pixel-accent)] w-full min-h-0"
            >
              <h2 className="text-xs md:text-sm text-[var(--pixel-accent)] md:mb-2">{title}</h2>
              <p className="hidden md:block text-xs text-[var(--pixel-muted)] leading-relaxed">{subtitle}</p>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
