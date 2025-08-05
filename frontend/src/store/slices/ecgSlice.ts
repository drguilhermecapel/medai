import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'

export interface ECGData {
  id: string
  patientId: string
  data: number[]
  timestamp: string
  analysisResult?: ECGAnalysisResult
  status: 'pending' | 'analyzing' | 'completed' | 'error'
}

export interface ECGAnalysisResult {
  id: string
  heartRate: number
  rhythm: string
  abnormalities: string[]
  confidence: number
  recommendations: string[]
}

interface ECGState {
  recordings: ECGData[]
  currentRecording: ECGData | null
  analysisResults: ECGAnalysisResult[]
  isLoading: boolean
  error: string | null
  uploadProgress: number
}

const initialState: ECGState = {
  recordings: [],
  currentRecording: null,
  analysisResults: [],
  isLoading: false,
  error: null,
  uploadProgress: 0,
}

// Async thunks
export const uploadECG = createAsyncThunk(
  'ecg/uploadECG',
  async (file: File, { rejectWithValue }) => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await fetch('/api/v1/ecg/upload', {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        throw new Error('Failed to upload ECG')
      }
      
      return await response.json()
    } catch (error) {
      return rejectWithValue(error.message)
    }
  }
)

export const analyzeECG = createAsyncThunk(
  'ecg/analyzeECG',
  async (ecgId: string, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/v1/ecg/${ecgId}/analyze`, {
        method: 'POST',
      })
      
      if (!response.ok) {
        throw new Error('Failed to analyze ECG')
      }
      
      return await response.json()
    } catch (error) {
      return rejectWithValue(error.message)
    }
  }
)

export const fetchECGRecordings = createAsyncThunk(
  'ecg/fetchRecordings',
  async (patientId?: string, { rejectWithValue }) => {
    try {
      const url = patientId 
        ? `/api/v1/ecg/recordings?patientId=${patientId}`
        : '/api/v1/ecg/recordings'
        
      const response = await fetch(url)
      
      if (!response.ok) {
        throw new Error('Failed to fetch ECG recordings')
      }
      
      return await response.json()
    } catch (error) {
      return rejectWithValue(error.message)
    }
  }
)

const ecgSlice = createSlice({
  name: 'ecg',
  initialState,
  reducers: {
    setCurrentRecording: (state, action: PayloadAction<ECGData>) => {
      state.currentRecording = action.payload
    },
    clearCurrentRecording: (state) => {
      state.currentRecording = null
    },
    clearError: (state) => {
      state.error = null
    },
    updateUploadProgress: (state, action: PayloadAction<number>) => {
      state.uploadProgress = action.payload
    },
    resetUploadProgress: (state) => {
      state.uploadProgress = 0
    },
  },
  extraReducers: (builder) => {
    builder
      // Upload ECG
      .addCase(uploadECG.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(uploadECG.fulfilled, (state, action) => {
        state.isLoading = false
        state.recordings.push(action.payload)
        state.uploadProgress = 100
      })
      .addCase(uploadECG.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
        state.uploadProgress = 0
      })
      
      // Analyze ECG
      .addCase(analyzeECG.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(analyzeECG.fulfilled, (state, action) => {
        state.isLoading = false
        const analysis = action.payload
        state.analysisResults.push(analysis)
        
        // Update the corresponding recording
        const recordingIndex = state.recordings.findIndex(
          r => r.id === analysis.ecgId
        )
        if (recordingIndex !== -1) {
          state.recordings[recordingIndex].analysisResult = analysis
          state.recordings[recordingIndex].status = 'completed'
        }
      })
      .addCase(analyzeECG.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
      
      // Fetch recordings
      .addCase(fetchECGRecordings.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchECGRecordings.fulfilled, (state, action) => {
        state.isLoading = false
        state.recordings = action.payload
      })
      .addCase(fetchECGRecordings.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
  },
})

export const {
  setCurrentRecording,
  clearCurrentRecording,
  clearError,
  updateUploadProgress,
  resetUploadProgress,
} = ecgSlice.actions

export default ecgSlice.reducer