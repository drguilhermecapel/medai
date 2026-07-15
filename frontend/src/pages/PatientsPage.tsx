import React, { useEffect, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  Grid,
  InputAdornment,
  InputLabel,
  LinearProgress,
  MenuItem,
  Select,
  SelectChangeEvent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import { Add, Search } from '@mui/icons-material'
import { useAppDispatch, useAppSelector } from '../hooks/redux'
import { fetchPatients, createPatient, clearError } from '../store/slices/patientSlice'

interface PatientFormData {
  name: string
  cpf: string
  birth_date: string
  gender: string
  phone: string
  email: string
  city: string
  state: string
}

const EMPTY_FORM: PatientFormData = {
  name: '',
  cpf: '',
  birth_date: '',
  gender: '',
  phone: '',
  email: '',
  city: '',
  state: '',
}

const GENDER_LABELS: Record<string, string> = {
  M: 'Masculino',
  F: 'Feminino',
  other: 'Outro',
}

const formatDate = (value?: string | null): string => {
  if (!value) return '—'
  const date = new Date(`${value}T00:00:00`)
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleDateString('pt-BR')
}

const PatientsPage: React.FC = () => {
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [formData, setFormData] = useState<PatientFormData>(EMPTY_FORM)

  const dispatch = useAppDispatch()
  const { patients, isLoading, error } = useAppSelector(state => state.patient)

  useEffect(() => {
    dispatch(fetchPatients({}))
  }, [dispatch])

  useEffect(() => {
    const handle = setTimeout(() => {
      dispatch(fetchPatients(search ? { search } : {}))
    }, 300)
    return () => clearTimeout(handle)
  }, [dispatch, search])

  const handleInputChange =
    (field: keyof PatientFormData) =>
    (event: React.ChangeEvent<HTMLInputElement>): void => {
      setFormData(prev => ({ ...prev, [field]: event.target.value }))
    }

  const handleGenderChange = (event: SelectChangeEvent<string>): void => {
    setFormData(prev => ({ ...prev, gender: event.target.value }))
  }

  const handleCreatePatient = async (): Promise<void> => {
    dispatch(clearError())
    const payload = Object.fromEntries(
      Object.entries(formData).filter(([, value]) => value !== '')
    ) as unknown as Parameters<typeof createPatient>[0]
    const result = await dispatch(createPatient(payload))
    if (createPatient.fulfilled.match(result)) {
      setCreateDialogOpen(false)
      setFormData(EMPTY_FORM)
    }
  }

  const isFormValid = formData.name.length > 0 && formData.cpf.length >= 11

  return (
    <Box>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: 2,
          flexWrap: 'wrap',
          mb: 3,
        }}
      >
        <Box>
          <Typography variant="h4">Pacientes</Typography>
          <Typography variant="body2" color="text.secondary">
            {patients.length} paciente(s) cadastrados
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<Add />} onClick={() => setCreateDialogOpen(true)}>
          Novo paciente
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => dispatch(clearError())}>
          {error}
        </Alert>
      )}

      <Card>
        <CardContent>
          <TextField
            placeholder="Buscar por nome…"
            value={search}
            onChange={event => setSearch(event.target.value)}
            size="small"
            fullWidth
            sx={{ mb: 2, maxWidth: 360 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search fontSize="small" />
                </InputAdornment>
              ),
            }}
          />

          {isLoading && <LinearProgress sx={{ mb: 2 }} />}

          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Nome</TableCell>
                  <TableCell>CPF</TableCell>
                  <TableCell>Nascimento</TableCell>
                  <TableCell>Sexo</TableCell>
                  <TableCell>Telefone</TableCell>
                  <TableCell>Cidade/UF</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {patients.map(patient => (
                  <TableRow key={patient.id} hover>
                    <TableCell sx={{ fontWeight: 600 }}>{patient.name}</TableCell>
                    <TableCell>{patient.cpf}</TableCell>
                    <TableCell>{formatDate(patient.birth_date)}</TableCell>
                    <TableCell>
                      {patient.gender ? (
                        <Chip
                          size="small"
                          variant="outlined"
                          label={GENDER_LABELS[patient.gender] ?? patient.gender}
                        />
                      ) : (
                        '—'
                      )}
                    </TableCell>
                    <TableCell>{patient.phone ?? '—'}</TableCell>
                    <TableCell>
                      {patient.city ? `${patient.city}${patient.state ? `/${patient.state}` : ''}` : '—'}
                    </TableCell>
                  </TableRow>
                ))}
                {!isLoading && patients.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} align="center" sx={{ py: 6, color: 'text.secondary' }}>
                      Nenhum paciente encontrado. Cadastre o primeiro paciente.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Cadastrar paciente</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0 }}>
            <Grid item xs={12}>
              <TextField
                label="Nome completo"
                value={formData.name}
                onChange={handleInputChange('name')}
                required
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="CPF"
                value={formData.cpf}
                onChange={handleInputChange('cpf')}
                required
                fullWidth
                inputProps={{ maxLength: 14 }}
                helperText="Somente números"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Data de nascimento"
                type="date"
                value={formData.birth_date}
                onChange={handleInputChange('birth_date')}
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Sexo</InputLabel>
                <Select value={formData.gender} onChange={handleGenderChange} label="Sexo">
                  <MenuItem value="M">Masculino</MenuItem>
                  <MenuItem value="F">Feminino</MenuItem>
                  <MenuItem value="other">Outro</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Telefone"
                value={formData.phone}
                onChange={handleInputChange('phone')}
                fullWidth
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="E-mail"
                type="email"
                value={formData.email}
                onChange={handleInputChange('email')}
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={8}>
              <TextField
                label="Cidade"
                value={formData.city}
                onChange={handleInputChange('city')}
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                label="UF"
                value={formData.state}
                onChange={handleInputChange('state')}
                fullWidth
                inputProps={{ maxLength: 2 }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancelar</Button>
          <Button variant="contained" onClick={handleCreatePatient} disabled={!isFormValid}>
            Cadastrar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default PatientsPage
