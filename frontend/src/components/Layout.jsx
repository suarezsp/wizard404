/**
 * Layout.jsx - Envuelve el contenido y reserva la esquina inferior derecha para el mago y sus dialogos.
 * Zona reservada definida por variables CSS (--mage-zone-width, --mage-zone-height) en :root.
 */
import { MageWizard } from './MageWizard'

export function Layout({ children }) {
  return (
    <div className="min-h-screen relative" style={{ position: 'relative', zIndex: 1 }}>
      <main
        className="min-h-screen"
        style={{
          paddingRight: 'var(--mage-zone-width, 320px)',
          paddingBottom: 'var(--mage-zone-height, 220px)',
        }}
      >
        {children}
      </main>
      <MageWizard />
    </div>
  )
}
