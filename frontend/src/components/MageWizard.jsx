/**
 * MageWizard.jsx - Mago fijo en esquina: sprite idle/speak y caja de dialogo 16-bit con typewriter.
 * Tamano del mago y del dialogo se ajustan con variables CSS en :root (--mage-size, --mage-dialogue-width, etc.).
 */
import { useMage } from '../context/MageContext'
import { useTypewriter } from '../hooks/useTypewriter'

const TYPEWRITER_SPEED_MS = 45

export function MageWizard() {
  const { message, isSpeaking, onTypewriterComplete } = useMage()
  const displayText = useTypewriter(
    message ?? '',
    TYPEWRITER_SPEED_MS,
    onTypewriterComplete
  )

  return (
    <div
      className="fixed bottom-0 right-0 flex flex-col items-end pointer-events-none"
      style={{ zIndex: 50, gap: 'var(--mage-gap, 8px)' }}
    >
      {message != null && (
        <div
          data-testid="mage-dialogue"
          className="border-4 font-pixel leading-relaxed p-3 overflow-y-auto overflow-x-hidden min-h-0"
          style={{
            width: 'var(--mage-dialogue-width, 300px)',
            fontSize: 'var(--mage-dialogue-font-size, 10px)',
            maxHeight: 'var(--mage-dialogue-max-height, 40vh)',
            backgroundColor: 'var(--pixel-dialogue-bg)',
            borderColor: 'var(--pixel-border)',
            color: 'var(--pixel-text)',
            transition: 'max-height 0.2s ease-out',
          }}
        >
          <span style={{ display: 'block' }}>
            {displayText}
          </span>
        </div>
      )}
      <img
        src={isSpeaking ? '/mage_speak.png' : '/mage_idle.png'}
        alt="Mage"
        className="flex-shrink-0"
        style={{ width: 'var(--mage-size, 428px)', height: 'var(--mage-size, 428px)' }}
      />
    </div>
  )
}
