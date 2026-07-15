import React, { useEffect, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  MenuItem,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import { Add, Delete, Psychology } from '@mui/icons-material'
import { useAppDispatch, useAppSelector } from '../hooks/redux'
import {
  fetchExams,
  createExam,
  analyzeExam,
  clearError,
  clearLastDiagnostic,
} from '../store/slices/examSlice'
import { fetchPatients } from '../store/slices/patientSlice'

const EXAM_TYPES = [
  { value: 'blood_test', label: 'Exame de sangue' },
  { value: 'urine_test', label: 'Exame de urina' },
  { value: 'xray', label: 'Raio-X' },
  { value: 'ultrasound', label: 'Ultrassom' },
  { value: 'mri', label: 'Ressonância magnética' },
  { value: 'ct_scan', label: 'Tomografia' },
]

const STATUS_LABELS: Record<string, { label: string; color: 'default' | 'info' | 'success' | 'warning' }> = {
  pending: { label: 'Pendente', color: 'warning' },
  in_progress: { label: 'Em andamento', color: 'info' },
  completed: { label: 'Concluído', color: 'success' },
}

const SEVERITY_LABELS: Record<string, { label: string; color: 'success' | 'info' | 'warning' | 'error' }> = {
  normal: { label: 'Normal', color: 'success' },
  mild: { label: 'Leve', color: 'info' },
  moderate: { label: 'Moderada', color: 'warning' },
  severe: { label: 'Grave', color: 'error' },
}

interface ResultRow {
  name: string
  value: string
  min: string
  max: string
  unit: string
}

const EMPTY_ROW: ResultRow = { name: '', value: '', min: '', max: '', unit: '' }

const examTypeLabel = (value: string): string =>
  EXAM_TYPES.find(type => type.value === value)?.label ?? value

const ExamsPage: React.FC = () => {
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [patientId, setPatientId] = useState<number | ''>('')
  const [examType, setExamType] = useState('blood_test')
  const [rows, setRows] = useState<ResultRow[]>([{ ...EMPTY_ROW }])

  const dispatch = useAppDispatch()
  const { exams, lastDiagnostic, isLoading, isAnalyzing, error } = useAppSelector(
    state => state.exam
  )
  const { patients } = useAppSelector(state => state.patient)

  useEffect(() => {
    dispatch(fetchExams({}))
    dispatch(fetchPatients({ limit: 200 }))
  }, [dispatch])

  const patientName = (id: number): string =>
    patients.find(patient => patient.id === id)?.name ?? `Paciente #${id}`

  const updateRow =
    (index: number, field: keyof ResultRow) =>
    (event: React.ChangeEvent<HTMLInputElement>): void => {
      setRows(prev =>
        prev.map((row, i) => (i === index ? { ...row, [field]: event.target.value } : row))
      )
    }

  const validRows = rows.filter(row => row.name && row.value !== '')

  const handleCreateExam = async (): Promise<void> => {
    if (patientId === '') return
    dispatch(clearError())

    const results: Record<string, number> = {}
    const references: Record<string, { min?: number; max?: number; unit?: string }> = {}
    for (const row of validRows) {
      results[row.name] = Number(row.value)
      const reference: { min?: number; max?: number; unit?: string } = {}
      if (row.min !== '') reference.min = Number(row.min)
      if (row.max !== '') reference.max = Number(row.max)
      if (row.unit !== '') reference.unit = row.unit
      if (Object.keys(reference).length > 0) references[row.name] = reference
    }

    const result = await dispatch(
      createExam({
        patient_id: patientId,
        exam_type: examType,
        status: 'completed',
        results,
        reference_values: references,
      })
    )
    if (createExam.fulfilled.match(result)) {
      setCreateDialogOpen(false)
      setPatientId('')
      setExamType('blood_test')
      setRows([{ ...EMPTY_ROW }])
    }
  }

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
          <Typography variant="h4">Exames</Typography>
          <Typography variant="body2" color="text.secondary">
            Registre exames e gere diagnósticos automáticos com IA
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<Add />} onClick={() => setCreateDialogOpen(true)}>
          Novo exame
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => dispatch(clearError())}>
          {error}
        </Alert>
      )}

      <Card>
        <CardContent>
          {isLoading && <LinearProgress sx={{ mb: 2 }} />}
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Paciente</TableCell>
                  <TableCell>Tipo</TableCell>
                  <TableCell>Parâmetros</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Data</TableCell>
                  <TableCell align="right">Análise IA</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {exams.map(exam => {
                  const status = STATUS_LABELS[exam.status] ?? {
                    label: exam.status,
                    color: 'default' as const,
                  }
                  return (
                    <TableRow key={exam.id} hover>
                      <TableCell sx={{ fontWeight: 600 }}>{patientName(exam.patient_id)}</TableCell>
                      <TableCell>{examTypeLabel(exam.exam_type)}</TableCell>
                      <TableCell>{Object.keys(exam.results ?? {}).length}</TableCell>
                      <TableCell>
                        <Chip size="small" label={status.label} color={status.color} />
                      </TableCell>
                      <TableCell>
                        {exam.exam_date
                          ? new Date(exam.exam_date).toLocaleDateString('pt-BR')
                          : '—'}
                      </TableCell>
                      <TableCell align="right">
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={
                            isAnalyzing ? <CircularProgress size={14} /> : <Psychology />
                          }
                          disabled={isAnalyzing || !exam.results}
                          onClick={() => dispatch(analyzeExam(exam.id))}
                        >
                          Analisar
                        </Button>
                      </TableCell>
                    </TableRow>
                  )
                })}
                {!isLoading && exams.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} align="center" sx={{ py: 6, color: 'text.secondary' }}>
                      Nenhum exame registrado ainda.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Dialog: resultado da análise IA */}
      <Dialog
        open={Boolean(lastDiagnostic)}
        onClose={() => dispatch(clearLastDiagnostic())}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Psychology color="primary" /> Diagnóstico automático
        </DialogTitle>
        <DialogContent>
          {lastDiagnostic && (
            <Stack spacing={2}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="subtitle2">Severidade:</Typography>
                <Chip
                  size="small"
                  label={SEVERITY_LABELS[lastDiagnostic.severity]?.label ?? lastDiagnostic.severity}
                  color={SEVERITY_LABELS[lastDiagnostic.severity]?.color ?? 'default'}
                />
              </Box>
              <Typography variant="body2">{lastDiagnostic.diagnostic_text}</Typography>

              {(lastDiagnostic.ai_analysis?.findings?.length ?? 0) > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Parâmetros alterados
                  </Typography>
                  <List dense disablePadding>
                    {lastDiagnostic.ai_analysis?.findings?.map(finding => (
                      <ListItem key={finding.parameter} disableGutters>
                        <ListItemText
                          primary={`${finding.parameter}: ${finding.value} ${finding.unit ?? ''}`}
                          secondary={
                            finding.status === 'above_reference'
                              ? 'Acima da referência'
                              : 'Abaixo da referência'
                          }
                        />
                        <Chip
                          size="small"
                          variant="outlined"
                          label={SEVERITY_LABELS[
                            finding.severity === 'high'
                              ? 'severe'
                              : finding.severity === 'medium'
                                ? 'moderate'
                                : 'mild'
                          ]?.label}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {(lastDiagnostic.ai_analysis?.recommendations?.length ?? 0) > 0 && (
                <Alert severity="info">
                  <Typography variant="subtitle2" gutterBottom>
                    Recomendações
                  </Typography>
                  {lastDiagnostic.ai_analysis?.recommendations?.map(recommendation => (
                    <Typography key={recommendation} variant="body2">
                      • {recommendation}
                    </Typography>
                  ))}
                </Alert>
              )}
            </Stack>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button variant="contained" onClick={() => dispatch(clearLastDiagnostic())}>
            Fechar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog: novo exame */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Registrar exame</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0 }}>
            <Grid item xs={12} sm={7}>
              <FormControl fullWidth required>
                <InputLabel>Paciente</InputLabel>
                <Select
                  value={patientId}
                  label="Paciente"
                  onChange={event => setPatientId(event.target.value as number)}
                >
                  {patients.map(patient => (
                    <MenuItem key={patient.id} value={patient.id}>
                      {patient.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={5}>
              <FormControl fullWidth>
                <InputLabel>Tipo de exame</InputLabel>
                <Select
                  value={examType}
                  label="Tipo de exame"
                  onChange={event => setExamType(event.target.value)}
                >
                  {EXAM_TYPES.map(type => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Resultados e valores de referência
              </Typography>
              <Stack spacing={1.5}>
                {rows.map((row, index) => (
                  <Stack key={index} direction="row" spacing={1} alignItems="center">
                    <TextField
                      label="Parâmetro"
                      size="small"
                      value={row.name}
                      onChange={updateRow(index, 'name')}
                      sx={{ flex: 2 }}
                    />
                    <TextField
                      label="Valor"
                      size="small"
                      type="number"
                      value={row.value}
                      onChange={updateRow(index, 'value')}
                      sx={{ flex: 1 }}
                    />
                    <TextField
                      label="Mín."
                      size="small"
                      type="number"
                      value={row.min}
                      onChange={updateRow(index, 'min')}
                      sx={{ flex: 1 }}
                    />
                    <TextField
                      label="Máx."
                      size="small"
                      type="number"
                      value={row.max}
                      onChange={updateRow(index, 'max')}
                      sx={{ flex: 1 }}
                    />
                    <TextField
                      label="Unidade"
                      size="small"
                      value={row.unit}
                      onChange={updateRow(index, 'unit')}
                      sx={{ flex: 1 }}
                    />
                    <IconButton
                      size="small"
                      onClick={() => setRows(prev => prev.filter((_, i) => i !== index))}
                      disabled={rows.length === 1}
                      aria-label="remover parâmetro"
                    >
                      <Delete fontSize="small" />
                    </IconButton>
                  </Stack>
                ))}
              </Stack>
              <Button
                size="small"
                startIcon={<Add />}
                onClick={() => setRows(prev => [...prev, { ...EMPTY_ROW }])}
                sx={{ mt: 1.5 }}
              >
                Adicionar parâmetro
              </Button>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancelar</Button>
          <Button
            variant="contained"
            onClick={handleCreateExam}
            disabled={patientId === '' || validRows.length === 0}
          >
            Registrar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default ExamsPage
