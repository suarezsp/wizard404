/**
 * ToastContext.test.jsx - Tests del contexto Toast (addToast, removeToast, auto-cierre).
 */
import { describe, it, expect } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { ToastProvider, useToast } from './ToastContext'

function TestConsumer() {
  const { addToast, removeToast } = useToast()
  return (
    <div>
      <button type="button" onClick={() => addToast('Error de prueba', 'error')}>
        Add
      </button>
      <button type="button" onClick={() => addToast('Second', 'error')}>
        Add second
      </button>
    </div>
  )
}

describe('ToastContext', () => {
  it('addToast anade un toast y se muestra en ToastList', () => {
    const ToastList = () => {
      const { toasts } = useToast()
      return (
        <div data-testid="toast-list">
          {toasts.map((t) => (
            <div key={t.id} data-testid="toast">
              {t.message}
            </div>
          ))}
        </div>
      )
    }
    render(
      <ToastProvider>
        <TestConsumer />
        <ToastList />
      </ToastProvider>
    )
    expect(screen.getByTestId('toast-list').children).toHaveLength(0)
    act(() => {
      screen.getByText('Add').click()
    })
    expect(screen.getByTestId('toast-list').children).toHaveLength(1)
    expect(screen.getByText('Error de prueba')).toBeTruthy()
  })

  it('removeToast elimina el toast', () => {
    let toastId
    const ToastList = () => {
      const { toasts, removeToast } = useToast()
      return (
        <div data-testid="toast-list">
          {toasts.map((t) => (
            <div key={t.id} data-testid="toast">
              {t.message}
              <button type="button" onClick={() => removeToast(t.id)}>Cerrar</button>
            </div>
          ))}
        </div>
      )
    }
    render(
      <ToastProvider>
        <TestConsumer />
        <ToastList />
      </ToastProvider>
    )
    act(() => screen.getByText('Add').click())
    expect(screen.getByTestId('toast-list').children).toHaveLength(1)
    act(() => screen.getByText('Cerrar').click())
    expect(screen.getByTestId('toast-list').children).toHaveLength(0)
  })
})
