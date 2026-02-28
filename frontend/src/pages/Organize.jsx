/**
 * Organize.jsx - Mensaje "Disponible en CLI"; sin endpoint en backend.
 */
import { Link } from 'react-router-dom'
import { useMage } from '../context/MageContext'
import { Card } from '../components/ui/Card'
import { AnimatedView } from '../components/AnimatedView'
import { useEffect } from 'react'

export function Organize() {
  const { sayForScene } = useMage()

  useEffect(() => {
    sayForScene('organize')
  }, [sayForScene])

  return (
    <AnimatedView className="min-h-screen p-6">
      <header className="flex justify-between items-center mb-6 border-b-2 border-[var(--pixel-border)] pb-4">
        <Link to="/" className="link-back-menu">
          ← Volver al menú
        </Link>
      </header>
      <h1 className="text-lg text-[var(--pixel-accent)] mb-4">Organize files</h1>
      <Card className="p-4 max-w-xl">
        <p className="text-xs text-[var(--pixel-muted)] mb-2">
          Mover archivos a carpetas por tipo, fecha o tamaño esta disponible en la CLI.
        </p>
        <p className="text-xs">
          Ejecuta <code className="bg-[var(--pixel-border)] px-1">w404</code> en tu terminal y elige
          &quot;Organize files&quot; para usar esta funcion en tu maquina.
        </p>
      </Card>
    </AnimatedView>
  )
}
