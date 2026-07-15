import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { authHeaders } from '../api'

export interface Exam {
  id: number
  patient_id: number
  exam_type: string
  exam_date?: string | null
  results?: Record<string, number> | null
  reference_values?: Record<string, { min?: number; max?: number; unit?: string }> | null
  status: string
  created_at?: string | null
}

export interface ExamInput {
  patient_id: number
  exam_type: string
  status?: string
  results?: Record<string, number>
  reference_values?: Record<string, { min?: number; max?: number; unit?: string }>
}

export interface DiagnosticFinding {
  parameter: string
  value: number
  unit?: string
  status: string
  severity: string
}

export interface Diagnostic {
  id: number
  patient_id: number
  exam_id?: number | null
  diagnostic_text: string
  severity: string
  ai_analysis?: {
    findings?: DiagnosticFinding[]
    severity?: string
    abnormal_count?: number
    analyzed_count?: number
    recommendations?: string[]
  } | null
  created_at?: string | null
}

interface ExamState {
  exams: Exam[]
  diagnostics: Diagnostic[]
  lastDiagnostic: Diagnostic | null
  isLoading: boolean
  isAnalyzing: boolean
  error: string | null
}

const initialState: ExamState = {
  exams: [],
  diagnostics: [],
  lastDiagnostic: null,
  isLoading: false,
  isAnalyzing: false,
  error: null,
}

export const fetchExams = createAsyncThunk(
  'exam/fetchExams',
  async (params: { patient_id?: number; limit?: number } = {}) => {
    const searchParams = new URLSearchParams()
    if (params.patient_id) searchParams.append('patient_id', params.patient_id.toString())
    if (params.limit) searchParams.append('limit', params.limit.toString())

    const response = await fetch(`/api/v1/exams?${searchParams}`, {
      headers: authHeaders(),
    })

    if (!response.ok) {
      throw new Error('Falha ao carregar exames')
    }

    return response.json() as Promise<Exam[]>
  }
)

export const createExam = createAsyncThunk(
  'exam/createExam',
  async (examData: ExamInput, { rejectWithValue }) => {
    const response = await fetch('/api/v1/exams', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(examData),
    })

    if (!response.ok) {
      const body = await response.json().catch(() => null)
      return rejectWithValue(body?.message ?? 'Falha ao registrar exame')
    }

    return response.json() as Promise<Exam>
  }
)

export const analyzeExam = createAsyncThunk(
  'exam/analyzeExam',
  async (examId: number, { rejectWithValue }) => {
    const response = await fetch(`/api/v1/diagnostics/analyze/${examId}`, {
      method: 'POST',
      headers: authHeaders(),
    })

    if (!response.ok) {
      const body = await response.json().catch(() => null)
      return rejectWithValue(body?.message ?? 'Falha ao analisar exame')
    }

    return response.json() as Promise<Diagnostic>
  }
)

export const fetchDiagnostics = createAsyncThunk(
  'exam/fetchDiagnostics',
  async (params: { patient_id?: number; limit?: number } = {}) => {
    const searchParams = new URLSearchParams()
    if (params.patient_id) searchParams.append('patient_id', params.patient_id.toString())
    if (params.limit) searchParams.append('limit', params.limit.toString())

    const response = await fetch(`/api/v1/diagnostics?${searchParams}`, {
      headers: authHeaders(),
    })

    if (!response.ok) {
      throw new Error('Falha ao carregar diagnósticos')
    }

    return response.json() as Promise<Diagnostic[]>
  }
)

const examSlice = createSlice({
  name: 'exam',
  initialState,
  reducers: {
    clearError: state => {
      state.error = null
    },
    clearLastDiagnostic: state => {
      state.lastDiagnostic = null
    },
  },
  extraReducers: builder => {
    builder
      .addCase(fetchExams.pending, state => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchExams.fulfilled, (state, action) => {
        state.isLoading = false
        state.exams = action.payload
      })
      .addCase(fetchExams.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.error.message ?? 'Falha ao carregar exames'
      })
      .addCase(createExam.fulfilled, (state, action) => {
        state.exams.unshift(action.payload)
      })
      .addCase(createExam.rejected, (state, action) => {
        state.error = (action.payload as string) ?? 'Falha ao registrar exame'
      })
      .addCase(analyzeExam.pending, state => {
        state.isAnalyzing = true
        state.error = null
      })
      .addCase(analyzeExam.fulfilled, (state, action) => {
        state.isAnalyzing = false
        state.lastDiagnostic = action.payload
        state.diagnostics.unshift(action.payload)
      })
      .addCase(analyzeExam.rejected, (state, action) => {
        state.isAnalyzing = false
        state.error = (action.payload as string) ?? 'Falha ao analisar exame'
      })
      .addCase(fetchDiagnostics.fulfilled, (state, action) => {
        state.diagnostics = action.payload
      })
  },
})

export const { clearError, clearLastDiagnostic } = examSlice.actions
export default examSlice.reducer
