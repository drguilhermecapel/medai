import React from 'react'
import ReactDOM from 'react-dom/client'
import AppWithAuth from './App'
import './index.css'
import { ThemeProvider } from '@mui/material/styles'
import { theme } from './theme'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <AppWithAuth />
    </ThemeProvider>
  </React.StrictMode>
)
