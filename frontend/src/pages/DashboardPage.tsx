import React, { useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Typography,
} from '@mui/material'
import {
  People as PeopleIcon,
  Science as ScienceIcon,
  Psychology as PsychologyIcon,
  WarningAmber as WarningIcon,
} from '@mui/icons-material'
import { useAppDispatch, useAppSelector } from '../hooks/redux'
import { fetchExams, fetchDiagnostics } from '../store/slices/examSlice'
import { fetchPatients } from '../store/slices/patientSlice'

const SEVERITY_LABELS: Record<string, { label: string; color: 'success' | 'info' | 'warning' | 'error' }> = {
  normal: { label: 'Normal', color: 'success' },
  mild: { label: 'Leve', color: 'info' },
  moderate: { label: 'Moderada', color: 'warning' },
  severe: { label: 'Grave', color: 'error' },
}

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  accent: string
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, accent }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
      <Box
        sx={{
          width: 48,
          height: 48,
          borderRadius: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: `${accent}22`,
          color: accent,
          flexShrink: 0,
        }}
      >
        {icon}
      </Box>
      <Box sx={{ minWidth: 0 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
          {value}
        </Typography>
        <Typography variant="body2" color="text.secondary" noWrap>
          {title}
        </Typography>
      </Box>
    </CardContent>
  </Card>
)

const DashboardPage: React.FC = () => {
  const dispatch = useAppDispatch()
  const { exams, diagnostics, isLoading } = useAppSelector(state => state.exam)
  const { patients } = useAppSelector(state => state.patient)

  useEffect(() => {
    dispatch(fetchPatients({}))
    dispatch(fetchExams({}))
    dispatch(fetchDiagnostics({ limit: 10 }))
  }, [dispatch])

  const pendingExams = exams.filter(exam => exam.status === 'pending').length
  const severeCases = diagnostics.filter(diagnostic => diagnostic.severity === 'severe').length

  const patientName = (id: number): string =>
    patients.find(patient => patient.id === id)?.name ?? `Paciente #${id}`

  if (isLoading && exams.length === 0) {
    return (
      <Box sx={{ width: '100%' }}>
        <LinearProgress />
        <Typography sx={{ mt: 2 }}>Carregando dashboard…</Typography>
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Visão geral dos pacientes, exames e diagnósticos gerados por IA
      </Typography>

      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Pacientes"
            value={patients.length}
            icon={<PeopleIcon />}
            accent="#22d3ee"
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard title="Exames" value={exams.length} icon={<ScienceIcon />} accent="#a78bfa" />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Diagnósticos IA"
            value={diagnostics.length}
            icon={<PsychologyIcon />}
            accent="#34d399"
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Casos graves"
            value={severeCases}
            icon={<WarningIcon />}
            accent="#f87171"
          />
        </Grid>
      </Grid>

      <Grid container spacing={2.5}>
        <Grid item xs={12} md={7}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Diagnósticos recentes
              </Typography>
              {diagnostics.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ py: 4 }} align="center">
                  Nenhum diagnóstico gerado ainda. Registre um exame e use a análise por IA.
                </Typography>
              ) : (
                <List disablePadding>
                  {diagnostics.slice(0, 6).map(diagnostic => (
                    <ListItem key={diagnostic.id} disableGutters divider>
                      <ListItemText
                        primary={patientName(diagnostic.patient_id)}
                        secondary={diagnostic.diagnostic_text}
                        secondaryTypographyProps={{
                          sx: {
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          },
                        }}
                      />
                      <Chip
                        size="small"
                        label={SEVERITY_LABELS[diagnostic.severity]?.label ?? diagnostic.severity}
                        color={SEVERITY_LABELS[diagnostic.severity]?.color ?? 'default'}
                        sx={{ ml: 2 }}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={5}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Fila de exames
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, mb: 1 }}>
                <Typography variant="h3" sx={{ fontWeight: 700 }}>
                  {pendingExams}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  exame(s) pendente(s)
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={exams.length === 0 ? 0 : ((exams.length - pendingExams) / exams.length) * 100}
                sx={{ height: 8, borderRadius: 4, mb: 2 }}
              />
              <Typography variant="body2" color="text.secondary">
                {exams.length === 0
                  ? 'Nenhum exame registrado.'
                  : `${exams.length - pendingExams} de ${exams.length} exames concluídos.`}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default DashboardPage
