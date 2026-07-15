import React from 'react'
import { render, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from '@mui/material/styles'
import { describe, it, expect, vi } from 'vitest'
import { theme } from '../../theme'
import DashboardPage from '../DashboardPage'

vi.mock('../../hooks/redux', () => ({
  useAppDispatch: vi.fn(() => vi.fn()),
  useAppSelector: vi.fn(selector => {
    const mockState = {
      exam: {
        exams: [
          {
            id: 1,
            patient_id: 1,
            exam_type: 'blood_test',
            status: 'completed',
            results: { glucose: 126 },
          },
        ],
        diagnostics: [
          {
            id: 1,
            patient_id: 1,
            exam_id: 1,
            diagnostic_text: 'Análise automática: 1 parâmetro fora da referência (glucose).',
            severity: 'severe',
          },
        ],
        lastDiagnostic: null,
        isLoading: false,
        isAnalyzing: false,
        error: null,
      },
      patient: {
        patients: [{ id: 1, name: 'João Silva', cpf: '12345678901' }],
        currentPatient: null,
        isLoading: false,
        error: null,
      },
    }
    return selector(mockState)
  }),
}))

import { store } from '../../store'

const renderWithProviders = (component: React.ReactElement): ReturnType<typeof render> => {
  return render(
    <Provider store={store}>
      <BrowserRouter>
        <ThemeProvider theme={theme}>{component}</ThemeProvider>
      </BrowserRouter>
    </Provider>
  )
}

describe('DashboardPage', () => {
  it('renders dashboard page', () => {
    renderWithProviders(<DashboardPage />)
    expect(screen.getByText('Dashboard')).toBeDefined()
  })

  it('displays dashboard metrics', () => {
    renderWithProviders(<DashboardPage />)
    expect(screen.getByText('Pacientes')).toBeDefined()
    expect(screen.getByText('Exames')).toBeDefined()
    expect(screen.getByText('Diagnósticos IA')).toBeDefined()
    expect(screen.getByText('Casos graves')).toBeDefined()
  })

  it('lists recent diagnostics with patient name and severity', () => {
    renderWithProviders(<DashboardPage />)
    expect(screen.getByText('João Silva')).toBeDefined()
    expect(screen.getByText('Grave')).toBeDefined()
  })
})
