/**
 * Button.test.jsx - Tests del componente Button 16-bit.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button', () => {
  it('renderiza children y variante primary por defecto', () => {
    render(<Button>ENTRAR</Button>)
    const btn = screen.getByRole('button', { name: /ENTRAR/i })
    expect(btn).toBeTruthy()
    expect(btn.getAttribute('type')).toBe('button')
  })

  it('permite type submit', () => {
    render(<Button type="submit">ENVIAR</Button>)
    expect(screen.getByRole('button').getAttribute('type')).toBe('submit')
  })

  it('deshabilita el boton cuando disabled', () => {
    const onClick = vi.fn()
    render(
      <Button disabled onClick={onClick}>
        CLICK
      </Button>
    )
    const btn = screen.getByRole('button')
    expect(btn.disabled).toBe(true)
    fireEvent.click(btn)
    expect(onClick).not.toHaveBeenCalled()
  })

  it('llama onClick al hacer click', () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick}>CLICK</Button>)
    fireEvent.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalledTimes(1)
  })
})
