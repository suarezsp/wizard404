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
        <h1 className="pixel-page-title">WIZARD404</h1>
        <div className="flex items-center gap-4">
          <span className="pixel-subtitle text-xs">{user?.name}</span>
          <Button onClick={logout} variant="secondary" className="px-3 py-1">
            SALIR
          </Button>
        </div>
      </header>

      <div className="flex flex-col gap-2 md:gap-4 max-w-4xl ml-0 md:ml-[10%] mr-auto w-full">
        {MENU_OPTIONS.map(({ to, title, subtitle }) => (
          <Link key={to} to={to} className="block w-full">
            <Card
              variant="light"
              borderWidth={4}
              className="card-menu p-3 md:p-4 cursor-pointer w-full min-h-0 flex items-center justify-between gap-4"
            >
              <h2 className="card-menu-title pixel-section-title flex-shrink-0">{title}</h2>
              <p className="hidden md:block text-right flex-1 min-w-0"><span className="pixel-subtitle text-[0.5rem]">{subtitle}</span></p>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
