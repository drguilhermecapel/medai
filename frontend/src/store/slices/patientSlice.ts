import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { authHeaders } from '../api'

export interface Patient {
  id: number
  name: string
  cpf: string
  birth_date?: string | null
  gender?: string | null
  phone?: string | null
  email?: string | null
  city?: string | null
  state?: string | null
}

export interface PatientInput {
  name: string
  cpf: string
  birth_date?: string
  gender?: string
  phone?: string
  email?: string
  city?: string
  state?: string
}

interface PatientState {
  patients: Patient[]
  currentPatient: Patient | null
  isLoading: boolean
  error: string | null
}

const initialState: PatientState = {
  patients: [],
  currentPatient: null,
  isLoading: false,
  error: null,
}

export const fetchPatients = createAsyncThunk(
  'patient/fetchPatients',
  async (params: { limit?: number; skip?: number; search?: string } = {}) => {
    const searchParams = new URLSearchParams()
    if (params.limit) searchParams.append('limit', params.limit.toString())
    if (params.skip) searchParams.append('skip', params.skip.toString())
    if (params.search) searchParams.append('search', params.search)

    const response = await fetch(`/api/v1/patients?${searchParams}`, {
      headers: authHeaders(),
    })

    if (!response.ok) {
      throw new Error('Falha ao carregar pacientes')
    }

    return response.json() as Promise<Patient[]>
  }
)

export const createPatient = createAsyncThunk(
  'patient/createPatient',
  async (patientData: PatientInput, { rejectWithValue }) => {
    const response = await fetch('/api/v1/patients', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(patientData),
    })

    if (!response.ok) {
      const body = await response.json().catch(() => null)
      return rejectWithValue(body?.message ?? 'Falha ao cadastrar paciente')
    }

    return response.json() as Promise<Patient>
  }
)

const patientSlice = createSlice({
  name: 'patient',
  initialState,
  reducers: {
    clearError: state => {
      state.error = null
    },
    setCurrentPatient: (state, action) => {
      state.currentPatient = action.payload
    },
  },
  extraReducers: builder => {
    builder
      .addCase(fetchPatients.pending, state => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchPatients.fulfilled, (state, action) => {
        state.isLoading = false
        state.patients = action.payload
      })
      .addCase(fetchPatients.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.error.message ?? 'Falha ao carregar pacientes'
      })
      .addCase(createPatient.pending, state => {
        state.isLoading = true
        state.error = null
      })
      .addCase(createPatient.fulfilled, (state, action) => {
        state.isLoading = false
        state.patients.push(action.payload)
      })
      .addCase(createPatient.rejected, (state, action) => {
        state.isLoading = false
        state.error = (action.payload as string) ?? 'Falha ao cadastrar paciente'
      })
  },
})

export const { clearError, setCurrentPatient } = patientSlice.actions
export default patientSlice.reducer
