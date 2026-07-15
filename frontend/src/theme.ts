import { createTheme, alpha } from '@mui/material/styles'

// Tema escuro profissional do MedAI: superfícies frias e sóbrias,
// primária ciano-médico para ações e destaque clínico.
const PRIMARY = '#22d3ee'
const SECONDARY = '#a78bfa'
const BG_DEFAULT = '#0b1220'
const BG_PAPER = '#111a2c'
const DIVIDER = 'rgba(148, 163, 184, 0.14)'

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: PRIMARY,
      light: '#67e8f9',
      dark: '#0891b2',
      contrastText: '#06222b',
    },
    secondary: {
      main: SECONDARY,
      light: '#c4b5fd',
      dark: '#7c3aed',
      contrastText: '#160b2e',
    },
    background: {
      default: BG_DEFAULT,
      paper: BG_PAPER,
    },
    divider: DIVIDER,
    text: {
      primary: '#e2e8f0',
      secondary: '#94a3b8',
    },
    success: { main: '#34d399' },
    warning: { main: '#fbbf24' },
    error: { main: '#f87171' },
    info: { main: '#60a5fa' },
  },
  shape: {
    borderRadius: 10,
  },
  typography: {
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    h1: { fontSize: '2.25rem', fontWeight: 700, letterSpacing: '-0.02em' },
    h2: { fontSize: '1.875rem', fontWeight: 700, letterSpacing: '-0.02em' },
    h3: { fontSize: '1.5rem', fontWeight: 600, letterSpacing: '-0.01em' },
    h4: { fontSize: '1.375rem', fontWeight: 600, letterSpacing: '-0.01em' },
    h5: { fontSize: '1.125rem', fontWeight: 600 },
    h6: { fontSize: '1rem', fontWeight: 600 },
    subtitle1: { color: '#94a3b8' },
    button: { fontWeight: 600 },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundImage:
            'radial-gradient(1200px 500px at 80% -10%, rgba(34, 211, 238, 0.07), transparent), radial-gradient(900px 420px at 0% 110%, rgba(167, 139, 250, 0.06), transparent)',
          backgroundAttachment: 'fixed',
        },
      },
    },
    MuiAppBar: {
      defaultProps: { elevation: 0, color: 'transparent' },
      styleOverrides: {
        root: {
          backgroundColor: alpha(BG_DEFAULT, 0.8),
          backdropFilter: 'blur(8px)',
          borderBottom: `1px solid ${DIVIDER}`,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: BG_DEFAULT,
          borderRight: `1px solid ${DIVIDER}`,
          backgroundImage: 'none',
        },
      },
    },
    MuiCard: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          border: `1px solid ${DIVIDER}`,
          backgroundImage: 'none',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: 'none' },
      },
    },
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { fontWeight: 600 },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          color: '#94a3b8',
          fontWeight: 600,
          fontSize: '0.75rem',
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
          borderBottom: `1px solid ${DIVIDER}`,
        },
        root: {
          borderBottom: `1px solid ${DIVIDER}`,
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          '&.Mui-selected': {
            backgroundColor: alpha(PRIMARY, 0.12),
            '&:hover': { backgroundColor: alpha(PRIMARY, 0.18) },
          },
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          border: `1px solid ${DIVIDER}`,
          backgroundImage: 'none',
        },
      },
    },
  },
})
