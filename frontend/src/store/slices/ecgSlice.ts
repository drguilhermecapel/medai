import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'

export interface ECGAnalysis {
  id: number
  analysisId: string
  patientId: number
  status: string
  diagnosis?: string
  clinicalUrgency: string
  confidence?: number
  createdAt: string
}

interface ECGState {
  analyses: ECGAnalysis[]
  currentAnalysis: ECGAnalysis | null
  isLoading: boolean
  error: string | null
  uploadProgress: number
}

const initialState: ECGState = {
  analyses: [],
  currentAnalysis: null,
  isLoading: false,
  error: null,
  uploadProgress: 0,
}

export const fetchAnalyses = createAsyncThunk(
  'ecg/fetchAnalyses',
  async (params: { limit?: number; offset?: number } = {}) => {
    const searchParams = new URLSearchParams()
    if (params.limit) searchParams.append('limit', params.limit.toString())
    if (params.offset) searchParams.append('offset', params.offset.toString())

    const response = await fetch(`/api/v1/ecg/analyses?${searchParams}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to fetch ECG analyses')
    }

    return response.json()
  }
)

export const uploadECG = createAsyncThunk(
  'ecg/uploadECG',
  async (params: { patientId: number; file: File }) => {
    const formData = new FormData()
    formData.append('patient_id', params.patientId.toString())
    formData.append('file', params.file)

    const response = await fetch('/api/v1/ecg/upload', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: formData,
    })

    if (!response.ok) {
      throw new Error('Failed to upload ECG')
    }

    return response.json()
  }
)

const ecgSlice = createSlice({
  name: 'ecg',
  initialState,
  reducers: {
    clearError: state => {
      state.error = null
    },
    setUploadProgress: (state, action) => {
      state.uploadProgress = action.payload
    },
  },
  extraReducers: builder => {
    builder
      .addCase(fetchAnalyses.pending, state => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchAnalyses.fulfilled, (state, action) => {
        state.isLoading = false
        state.analyses = Array.isArray(action.payload)
          ? action.payload
          : (action.payload.items ?? [])
      })
      .addCase(fetchAnalyses.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.error.message ?? 'Failed to fetch ECG analyses'
      })
      .addCase(uploadECG.pending, state => {
        state.error = null
        state.uploadProgress = 0
      })
      .addCase(uploadECG.fulfilled, (state, action) => {
        state.uploadProgress = 100
        if (action.payload && action.payload.id) {
          state.analyses.unshift(action.payload)
        }
      })
      .addCase(uploadECG.rejected, (state, action) => {
        state.uploadProgress = 0
        state.error = action.error.message ?? 'Failed to upload ECG'
      })
  },
})

export const { clearError, setUploadProgress } = ecgSlice.actions
export default ecgSlice.reducer
