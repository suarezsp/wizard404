/**
 * ToastList.test.jsx - Tests del componente ToastList (render, cerrar).
 */
import { describe, it, expect } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { ToastProvider, useToast } from '../context/ToastContext'
import { ToastList } from './ToastList'

function AddToastAndList() {
  const { addToast } = useToast()
  return (
    <>
      <button type="button" onClick={() => addToast('Test message', 'error')}>
        Add
      </button>
      <ToastList />
    </>
  )
}

describe('ToastList', () => {
  it('no renderiza nada cuando no hay toasts', () => {
    const { container } = render(
      <ToastProvider>
        <ToastList />
      </ToastProvider>
    )
    expect(container.querySelector('[role="region"]')).toBeFalsy()
  })

  it('renderiza un toast con mensaje y boton cerrar', () => {
    render(
      <ToastProvider>
        <AddToastAndList />
      </ToastProvider>
    )
    act(() => screen.getByText('Add').click())
    expect(screen.getByTestId('toast')).toBeTruthy()
    expect(screen.getByText('Test message')).toBeTruthy()
    expect(screen.getByLabelText('Cerrar')).toBeTruthy()
  })
})
