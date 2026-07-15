import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Alert,
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { MonitorHeart as MonitorHeartIcon } from '@mui/icons-material'
import { useAuth } from '../hooks/useAuth'

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (event: React.FormEvent): Promise<void> => {
    event.preventDefault()
    if (!email || !password) {
      return
    }
    setIsLoading(true)
    setError('')
    try {
      const success = await login(email, password)
      if (success) {
        navigate('/dashboard')
      } else {
        setError('Credenciais inválidas. Verifique e-mail e senha.')
      }
    } catch {
      setError('Não foi possível conectar ao servidor. Tente novamente.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
      }}
    >
      <Card sx={{ width: '100%', maxWidth: 420 }}>
        <CardContent sx={{ p: { xs: 3, sm: 5 } }}>
          <Stack spacing={3} alignItems="center">
            <Avatar
              variant="rounded"
              sx={{
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                width: 56,
                height: 56,
              }}
            >
              <MonitorHeartIcon fontSize="large" />
            </Avatar>
            <Box textAlign="center">
              <Typography variant="h4" component="h1">
                MedAI
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                Prontuário Eletrônico Inteligente
              </Typography>
            </Box>

            {error && (
              <Alert severity="error" sx={{ width: '100%' }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
              <Stack spacing={2}>
                <TextField
                  label="E-mail"
                  type="email"
                  value={email}
                  onChange={event => setEmail(event.target.value)}
                  autoComplete="email"
                  autoFocus
                  required
                  fullWidth
                />
                <TextField
                  label="Senha"
                  type="password"
                  value={password}
                  onChange={event => setPassword(event.target.value)}
                  autoComplete="current-password"
                  required
                  fullWidth
                />
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={isLoading || !email || !password}
                  startIcon={isLoading ? <CircularProgress size={18} color="inherit" /> : undefined}
                >
                  {isLoading ? 'Entrando…' : 'Entrar'}
                </Button>
              </Stack>
            </Box>

            <Typography variant="caption" color="text.secondary" textAlign="center">
              Acesso restrito a profissionais autorizados.
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  )
}

export default LoginPage
