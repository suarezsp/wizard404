/**
 * MageWizard.test.jsx - Sin mensaje: solo imagen idle; con mensaje: caja y sprite speak.
 */
import { useEffect } from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MageProvider, useMage } from '../context/MageContext'
import { MageWizard } from './MageWizard'

function TestWrapper() {
  return (
    <MageProvider>
      <MageWizard />
    </MageProvider>
  )
}

describe('MageWizard', () => {
  it('renders idle image when there is no message', () => {
    render(<TestWrapper />)
    const img = screen.getByRole('img', { name: /mage/i })
    expect(img).toBeTruthy()
    expect(img.getAttribute('src')).toBe('/mage_idle.png')
  })

  it('renders dialogue box and speak image when message is set', () => {
    function SetMessage() {
      const { say } = useMage()
      useEffect(() => {
        say('Hi')
      }, [say])
      return null
    }
    render(
      <MageProvider>
        <SetMessage />
        <MageWizard />
      </MageProvider>
    )
    const img = screen.getByRole('img', { name: /mage/i })
    expect(img.getAttribute('src')).toBe('/mage_speak.png')
    expect(screen.getByTestId('mage-dialogue')).toBeTruthy()
  })

  it('dialogue allows scroll for long content and does not cut text', () => {
    const longMessage = 'Line one. '.repeat(30)
    function SetLongMessage() {
      const { say } = useMage()
      useEffect(() => {
        say(longMessage)
      }, [say])
      return null
    }
    render(
      <MageProvider>
        <SetLongMessage />
        <MageWizard />
      </MageProvider>
    )
    const dialogue = screen.getByTestId('mage-dialogue')
    expect(dialogue).toBeTruthy()
    expect(dialogue.className).toContain('overflow-y-auto')
    expect(dialogue.className).not.toContain('overflow-hidden')
  })
})
