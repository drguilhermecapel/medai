import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  IconButton,
  Alert,
  LinearProgress,
  Tabs,
  Tab,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction
} from '@mui/material';
import {
  Add as AddIcon,
  PhotoCamera as PhotoIcon,
  Assessment as AssessmentIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

// Types
interface DermatologyLesion {
  fhir_condition_id: string;
  lesion_type: string;
  anatomical_location: string;
  body_region: string;
  abcde_total_score?: number;
  abcde_risk_level?: string;
  biopsy_recommended?: boolean;
  biopsy_urgency?: string;
  malignancy_risk?: string;
  length_mm?: number;
  width_mm?: number;
  photography_performed?: boolean;
  dermoscopy_performed?: boolean;
  created_at: string;
  updated_at: string;
}

interface ABCDEAssessment {
  asymmetry: string;
  asymmetry_score: number;
  border: string;
  border_score: number;
  color: string;
  color_score: number;
  diameter_mm: number;
  diameter_score: number;
  evolving: string;
  evolving_score: number;
}

// Validation schemas
const lesionSchema = z.object({
  lesion_type: z.string().min(1, 'Lesion type is required'),
  anatomical_location: z.string().min(1, 'Anatomical location is required'),
  body_region: z.string().min(1, 'Body region is required'),
  length_mm: z.number().min(0).optional(),
  width_mm: z.number().min(0).optional(),
  photography_performed: z.boolean().optional(),
  dermoscopy_performed: z.boolean().optional(),
});

const abcdeSchema = z.object({
  asymmetry: z.enum(['symmetric', 'asymmetric', 'unknown']),
  asymmetry_score: z.number().min(0).max(2),
  border: z.enum(['regular', 'irregular', 'unknown']),
  border_score: z.number().min(0).max(2),
  color: z.enum(['uniform', 'varied', 'unknown']),
  color_score: z.number().min(0).max(2),
  diameter_mm: z.number().min(0),
  diameter_score: z.number().min(0).max(2),
  evolving: z.enum(['stable', 'changing', 'unknown']),
  evolving_score: z.number().min(0).max(2),
});

type LesionFormData = z.infer<typeof lesionSchema>;
type ABCDEFormData = z.infer<typeof abcdeSchema>;

const DermatologyModule: React.FC<{ patientId: string }> = ({ patientId }) => {
  // State
  const [lesions, setLesions] = useState<DermatologyLesion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);
  const [openLesionDialog, setOpenLesionDialog] = useState(false);
  const [openABCDEDialog, setOpenABCDEDialog] = useState(false);
  const [selectedLesion, setSelectedLesion] = useState<DermatologyLesion | null>(null);
  
  // Forms
  const {
    control: lesionControl,
    handleSubmit: handleLesionSubmit,
    reset: resetLesionForm,
    formState: { errors: lesionErrors }
  } = useForm<LesionFormData>({
    resolver: zodResolver(lesionSchema),
  });

  const {
    control: abcdeControl,
    handleSubmit: handleABCDESubmit,
    reset: resetABCDEForm,
    watch: watchABCDE,
    formState: { errors: abcdeErrors }
  } = useForm<ABCDEFormData>({
    resolver: zodResolver(abcdeSchema),
  });

  // Watch ABCDE scores for real-time calculation
  const abcdeScores = watchABCDE();
  const totalABCDEScore = Object.values(abcdeScores || {})
    .filter(value => typeof value === 'number')
    .reduce((sum: number, score) => sum + (score || 0), 0);

  // Effects
  useEffect(() => {
    loadLesions();
  }, [patientId]);

  // API calls
  const loadLesions = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/specialties/dermatology/lesions?patient_id=${patientId}`);
      if (!response.ok) throw new Error('Failed to load lesions');
      const data = await response.json();
      setLesions(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const createLesion = async (data: LesionFormData) => {
    try {
      const response = await fetch('/api/v1/specialties/dermatology/lesions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...data,
          patient_id: patientId,
        }),
      });

      if (!response.ok) throw new Error('Failed to create lesion');
      
      await loadLesions();
      setOpenLesionDialog(false);
      resetLesionForm();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create lesion');
    }
  };

  const performABCDEAssessment = async (data: ABCDEFormData) => {
    if (!selectedLesion) return;

    try {
      const response = await fetch(`/api/v1/specialties/dermatology/lesions/${selectedLesion.fhir_condition_id}/abcde`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) throw new Error('Failed to perform ABCDE assessment');
      
      await loadLesions();
      setOpenABCDEDialog(false);
      resetABCDEForm();
      setSelectedLesion(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to perform assessment');
    }
  };

  // Helper functions
  const getRiskColor = (riskLevel?: string) => {
    switch (riskLevel) {
      case 'low': return 'success';
      case 'moderate': return 'warning';
      case 'high': return 'error';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getRiskIcon = (riskLevel?: string) => {
    switch (riskLevel) {
      case 'low': return <CheckCircleIcon />;
      case 'moderate': return <WarningIcon />;
      case 'high': case 'critical': return <CancelIcon />;
      default: return null;
    }
  };

  // Render functions
  const renderLesionCard = (lesion: DermatologyLesion) => (
    <Card key={lesion.fhir_condition_id} sx={{ mb: 2 }}>
      <CardContent>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6}>
            <Typography variant="h6" gutterBottom>
              {lesion.lesion_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Location: {lesion.anatomical_location} ({lesion.body_region})
            </Typography>
            {lesion.length_mm && lesion.width_mm && (
              <Typography variant="body2" color="text.secondary">
                Size: {lesion.length_mm} × {lesion.width_mm} mm
              </Typography>
            )}
          </Grid>
          
          <Grid item xs={12} sm={3}>
            {lesion.abcde_risk_level && (
              <Box display="flex" alignItems="center" gap={1}>
                <Chip
                  icon={getRiskIcon(lesion.abcde_risk_level)}
                  label={`${lesion.abcde_risk_level.toUpperCase()} RISK`}
                  color={getRiskColor(lesion.abcde_risk_level) as any}
                  size="small"
                />
                {lesion.abcde_total_score && (
                  <Typography variant="body2">
                    Score: {lesion.abcde_total_score}/10
                  </Typography>
                )}
              </Box>
            )}
            
            {lesion.biopsy_recommended && (
              <Alert severity={lesion.biopsy_urgency === 'emergent' ? 'error' : 'warning'} sx={{ mt: 1 }}>
                Biopsy recommended ({lesion.biopsy_urgency})
              </Alert>
            )}
          </Grid>
          
          <Grid item xs={12} sm={3}>
            <Box display="flex" gap={1}>
              <IconButton
                size="small"
                onClick={() => {
                  setSelectedLesion(lesion);
                  setOpenABCDEDialog(true);
                }}
              >
                <AssessmentIcon />
              </IconButton>
              
              <IconButton size="small">
                <EditIcon />
              </IconButton>
              
              {lesion.photography_performed && (
                <IconButton size="small">
                  <PhotoIcon color="primary" />
                </IconButton>
              )}
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const renderLesionDialog = () => (
    <Dialog open={openLesionDialog} onClose={() => setOpenLesionDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle>Add New Lesion</DialogTitle>
      <form onSubmit={handleLesionSubmit(createLesion)}>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Controller
                name="lesion_type"
                control={lesionControl}
                render={({ field }) => (
                  <FormControl fullWidth error={!!lesionErrors.lesion_type}>
                    <InputLabel>Lesion Type</InputLabel>
                    <Select {...field} label="Lesion Type">
                      <MenuItem value="melanocytic_nevus">Melanocytic Nevus</MenuItem>
                      <MenuItem value="atypical_nevus">Atypical Nevus</MenuItem>
                      <MenuItem value="seborrheic_keratosis">Seborrheic Keratosis</MenuItem>
                      <MenuItem value="basal_cell_carcinoma">Basal Cell Carcinoma</MenuItem>
                      <MenuItem value="squamous_cell_carcinoma">Squamous Cell Carcinoma</MenuItem>
                      <MenuItem value="melanoma">Melanoma</MenuItem>
                      <MenuItem value="suspicious_lesion">Suspicious Lesion</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <Controller
                name="body_region"
                control={lesionControl}
                render={({ field }) => (
                  <FormControl fullWidth error={!!lesionErrors.body_region}>
                    <InputLabel>Body Region</InputLabel>
                    <Select {...field} label="Body Region">
                      <MenuItem value="head">Head</MenuItem>
                      <MenuItem value="neck">Neck</MenuItem>
                      <MenuItem value="trunk">Trunk</MenuItem>
                      <MenuItem value="arm">Arm</MenuItem>
                      <MenuItem value="leg">Leg</MenuItem>
                      <MenuItem value="hand">Hand</MenuItem>
                      <MenuItem value="foot">Foot</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Controller
                name="anatomical_location"
                control={lesionControl}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Anatomical Location"
                    error={!!lesionErrors.anatomical_location}
                    helperText={lesionErrors.anatomical_location?.message}
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={6}>
              <Controller
                name="length_mm"
                control={lesionControl}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Length (mm)"
                    type="number"
                    inputProps={{ step: 0.1, min: 0 }}
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={6}>
              <Controller
                name="width_mm"
                control={lesionControl}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Width (mm)"
                    type="number"
                    inputProps={{ step: 0.1, min: 0 }}
                  />
                )}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenLesionDialog(false)}>Cancel</Button>
          <Button type="submit" variant="contained">Add Lesion</Button>
        </DialogActions>
      </form>
    </Dialog>
  );

  const renderABCDEDialog = () => (
    <Dialog open={openABCDEDialog} onClose={() => setOpenABCDEDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        ABCDE Assessment - {selectedLesion?.lesion_type.replace(/_/g, ' ')}
      </DialogTitle>
      <form onSubmit={handleABCDESubmit(performABCDEAssessment)}>
        <DialogContent>
          <Grid container spacing={3}>
            {/* Asymmetry */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>A - Asymmetry</Typography>
              <Grid container spacing={2}>
                <Grid item xs={8}>
                  <Controller
                    name="asymmetry"
                    control={abcdeControl}
                    render={({ field }) => (
                      <FormControl fullWidth>
                        <InputLabel>Asymmetry</InputLabel>
                        <Select {...field} label="Asymmetry">
                          <MenuItem value="symmetric">Symmetric</MenuItem>
                          <MenuItem value="asymmetric">Asymmetric</MenuItem>
                          <MenuItem value="unknown">Unknown</MenuItem>
                        </Select>
                      </FormControl>
                    )}
                  />
                </Grid>
                <Grid item xs={4}>
                  <Controller
                    name="asymmetry_score"
                    control={abcdeControl}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Score (0-2)"
                        type="number"
                        inputProps={{ min: 0, max: 2 }}
                      />
                    )}
                  />
                </Grid>
              </Grid>
            </Grid>

            {/* Border */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>B - Border</Typography>
              <Grid container spacing={2}>
                <Grid item xs={8}>
                  <Controller
                    name="border"
                    control={abcdeControl}
                    render={({ field }) => (
                      <FormControl fullWidth>
                        <InputLabel>Border</InputLabel>
                        <Select {...field} label="Border">
                          <MenuItem value="regular">Regular</MenuItem>
                          <MenuItem value="irregular">Irregular</MenuItem>
                          <MenuItem value="unknown">Unknown</MenuItem>
                        </Select>
                      </FormControl>
                    )}
                  />
                </Grid>
                <Grid item xs={4}>
                  <Controller
                    name="border_score"
                    control={abcdeControl}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Score (0-2)"
                        type="number"
                        inputProps={{ min: 0, max: 2 }}
                      />
                    )}
                  />
                </Grid>
              </Grid>
            </Grid>

            {/* Color */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>C - Color</Typography>
              <Grid container spacing={2}>
                <Grid item xs={8}>
                  <Controller
                    name="color"
                    control={abcdeControl}
                    render={({ field }) => (
                      <FormControl fullWidth>
                        <InputLabel>Color</InputLabel>
                        <Select {...field} label="Color">
                          <MenuItem value="uniform">Uniform</MenuItem>
                          <MenuItem value="varied">Varied</MenuItem>
                          <MenuItem value="unknown">Unknown</MenuItem>
                        </Select>
                      </FormControl>
                    )}
                  />
                </Grid>
                <Grid item xs={4}>
                  <Controller
                    name="color_score"
                    control={abcdeControl}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Score (0-2)"
                        type="number"
                        inputProps={{ min: 0, max: 2 }}
                      />
                    )}
                  />
                </Grid>
              </Grid>
            </Grid>

            {/* Diameter */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>D - Diameter</Typography>
              <Grid container spacing={2}>
                <Grid item xs={8}>
                  <Controller
                    name="diameter_mm"
                    control={abcdeControl}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Diameter (mm)"
                        type="number"
                        inputProps={{ step: 0.1, min: 0 }}
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={4}>
                  <Controller
                    name="diameter_score"
                    control={abcdeControl}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Score (0-2)"
                        type="number"
                        inputProps={{ min: 0, max: 2 }}
                      />
                    )}
                  />
                </Grid>
              </Grid>
            </Grid>

            {/* Evolving */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>E - Evolving</Typography>
              <Grid container spacing={2}>
                <Grid item xs={8}>
                  <Controller
                    name="evolving"
                    control={abcdeControl}
                    render={({ field }) => (
                      <FormControl fullWidth>
                        <InputLabel>Evolving</InputLabel>
                        <Select {...field} label="Evolving">
                          <MenuItem value="stable">Stable</MenuItem>
                          <MenuItem value="changing">Changing</MenuItem>
                          <MenuItem value="unknown">Unknown</MenuItem>
                        </Select>
                      </FormControl>
                    )}
                  />
                </Grid>
                <Grid item xs={4}>
                  <Controller
                    name="evolving_score"
                    control={abcdeControl}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Score (0-2)"
                        type="number"
                        inputProps={{ min: 0, max: 2 }}
                      />
                    )}
                  />
                </Grid>
              </Grid>
            </Grid>

            {/* Total Score */}
            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Total ABCDE Score: {totalABCDEScore}/10
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={(totalABCDEScore / 10) * 100}
                    color={totalABCDEScore >= 8 ? 'error' : totalABCDEScore >= 6 ? 'warning' : 'success'}
                  />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Risk Level: {
                      totalABCDEScore >= 8 ? 'CRITICAL' :
                      totalABCDEScore >= 6 ? 'HIGH' :
                      totalABCDEScore >= 4 ? 'MODERATE' : 'LOW'
                    }
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenABCDEDialog(false)}>Cancel</Button>
          <Button 
            type="submit" 
            variant="contained"
            color={totalABCDEScore >= 6 ? 'error' : 'primary'}
          >
            Save Assessment
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );

  const renderQuickAssessment = () => (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Quick Assessment
        </Typography>
        
        <List dense>
          <ListItem>
            <ListItemAvatar>
              <Avatar sx={{ bgcolor: 'primary.main' }}>
                {lesions.length}
              </Avatar>
            </ListItemAvatar>
            <ListItemText
              primary="Total Lesions"
              secondary="Documented lesions"
            />
          </ListItem>
          
          <ListItem>
            <ListItemAvatar>
              <Avatar sx={{ bgcolor: 'error.main' }}>
                {lesions.filter(l => l.biopsy_recommended).length}
              </Avatar>
            </ListItemAvatar>
            <ListItemText
              primary="Biopsies Recommended"
              secondary="Lesions requiring biopsy"
            />
          </ListItem>
          
          <ListItem>
            <ListItemAvatar>
              <Avatar sx={{ bgcolor: 'warning.main' }}>
                {lesions.filter(l => l.abcde_risk_level === 'high' || l.abcde_risk_level === 'critical').length}
              </Avatar>
            </ListItemAvatar>
            <ListItemText
              primary="High Risk Lesions"
              secondary="Require urgent attention"
            />
          </ListItem>
        </List>
        
        <Box sx={{ mt: 2 }}>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setOpenLesionDialog(true)}
            fullWidth
          >
            Add New Lesion
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  // Main render
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <LinearProgress sx={{ width: '100%' }} />
      </Box>
    );
  }

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Main Content */}
        <Grid item xs={12} md={8}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h5">Dermatology Assessment</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpenLesionDialog(true)}
            >
              Add Lesion
            </Button>
          </Box>

          <Tabs value={selectedTab} onChange={(_, newValue) => setSelectedTab(newValue)} sx={{ mb: 2 }}>
            <Tab label="Lesions" />
            <Tab label="Examinations" />
            <Tab label="History" />
          </Tabs>

          {selectedTab === 0 && (
            <Box>
              {lesions.length === 0 ? (
                <Card>
                  <CardContent>
                    <Typography variant="body1" color="text.secondary" textAlign="center">
                      No lesions documented yet. Click "Add Lesion" to start.
                    </Typography>
                  </CardContent>
                </Card>
              ) : (
                lesions.map(renderLesionCard)
              )}
            </Box>
          )}

          {selectedTab === 1 && (
            <Card>
              <CardContent>
                <Typography variant="body1" color="text.secondary">
                  Examination history will be displayed here.
                </Typography>
              </CardContent>
            </Card>
          )}

          {selectedTab === 2 && (
            <Card>
              <CardContent>
                <Typography variant="body1" color="text.secondary">
                  Patient history and follow-up information.
                </Typography>
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          {renderQuickAssessment()}
        </Grid>
      </Grid>

      {/* Dialogs */}
      {renderLesionDialog()}
      {renderABCDEDialog()}
    </Box>
  );
};

export default DermatologyModule;