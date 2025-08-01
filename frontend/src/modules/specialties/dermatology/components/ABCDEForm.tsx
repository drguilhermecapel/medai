import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  LinearProgress,
  Box,
  Alert,
} from '@mui/material';
import { Controller, Control, FieldErrors } from 'react-hook-form';
import { ABCDEAssessment } from '../types';
import { calculateABCDEScore, determineRiskLevel, getRiskColor } from '../utils';

interface ABCDEFormProps {
  control: Control<ABCDEAssessment>;
  errors: FieldErrors<ABCDEAssessment>;
  watchedValues: Partial<ABCDEAssessment>;
}

const ABCDEForm: React.FC<ABCDEFormProps> = ({ control, errors, watchedValues }) => {
  const totalScore = calculateABCDEScore({
    asymmetry_score: watchedValues.asymmetry_score,
    border_score: watchedValues.border_score,
    color_score: watchedValues.color_score,
    diameter_score: watchedValues.diameter_score,
    evolving_score: watchedValues.evolving_score,
  });

  const riskLevel = determineRiskLevel(totalScore);
  const riskColor = getRiskColor(riskLevel);

  const renderCriterion = (
    letter: string,
    title: string,
    description: string,
    assessmentName: keyof ABCDEAssessment,
    scoreName: keyof ABCDEAssessment,
    options: { value: string; label: string }[]
  ) => (
    <Grid item xs={12}>
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom color="primary">
            {letter} - {title}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {description}
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} sm={8}>
              <Controller
                name={assessmentName}
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors[assessmentName]}>
                    <InputLabel>{title}</InputLabel>
                    <Select {...field} label={title}>
                      {options.map(option => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <Controller
                name={scoreName}
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Score (0-2)"
                    type="number"
                    inputProps={{ min: 0, max: 2, step: 0.1 }}
                    error={!!errors[scoreName]}
                    helperText={errors[scoreName]?.message}
                  />
                )}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Grid>
  );

  return (
    <Grid container spacing={2}>
      {/* Asymmetry */}
      {renderCriterion(
        'A',
        'Asymmetry',
        'Is the lesion asymmetric when divided through the center?',
        'asymmetry',
        'asymmetry_score',
        [
          { value: 'symmetric', label: 'Symmetric (0 points)' },
          { value: 'asymmetric', label: 'Asymmetric (1-2 points)' },
          { value: 'unknown', label: 'Unknown' },
        ]
      )}

      {/* Border */}
      {renderCriterion(
        'B',
        'Border',
        'Are the borders irregular, notched, or blurred?',
        'border',
        'border_score',
        [
          { value: 'regular', label: 'Regular/Well-defined (0 points)' },
          { value: 'irregular', label: 'Irregular/Poorly defined (1-2 points)' },
          { value: 'unknown', label: 'Unknown' },
        ]
      )}

      {/* Color */}
      {renderCriterion(
        'C',
        'Color',
        'Does the lesion have varied colors or shades?',
        'color',
        'color_score',
        [
          { value: 'uniform', label: 'Uniform color (0 points)' },
          { value: 'varied', label: 'Multiple colors/shades (1-2 points)' },
          { value: 'unknown', label: 'Unknown' },
        ]
      )}

      {/* Diameter */}
      <Grid item xs={12}>
        <Card variant="outlined" sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom color="primary">
              D - Diameter
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Measure the largest diameter of the lesion (≥6mm is concerning)
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={8}>
                <Controller
                  name="diameter_mm"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Diameter (mm)"
                      type="number"
                      inputProps={{ step: 0.1, min: 0 }}
                      error={!!errors.diameter_mm}
                      helperText={errors.diameter_mm?.message || 'Enter largest diameter in millimeters'}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <Controller
                  name="diameter_score"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Score (0-2)"
                      type="number"
                      inputProps={{ min: 0, max: 2, step: 0.1 }}
                      error={!!errors.diameter_score}
                      helperText={
                        errors.diameter_score?.message || 
                        (watchedValues.diameter_mm && watchedValues.diameter_mm >= 6 ? 
                          'Diameter ≥6mm suggests higher score' : '')
                      }
                    />
                  )}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Evolving */}
      {renderCriterion(
        'E',
        'Evolving',
        'Has the lesion changed in size, shape, or color over time?',
        'evolving',
        'evolving_score',
        [
          { value: 'stable', label: 'Stable/No changes (0 points)' },
          { value: 'changing', label: 'Changing/Evolving (1-2 points)' },
          { value: 'unknown', label: 'Unknown' },
        ]
      )}

      {/* Total Score Summary */}
      <Grid item xs={12}>
        <Card sx={{ bgcolor: riskColor === 'error' ? 'error.light' : riskColor === 'warning' ? 'warning.light' : 'success.light' }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Total ABCDE Score: {totalScore.toFixed(1)}/10
            </Typography>
            
            <LinearProgress
              variant="determinate"
              value={(totalScore / 10) * 100}
              color={riskColor as any}
              sx={{ height: 8, borderRadius: 4, mb: 2 }}
            />
            
            <Typography variant="h6" gutterBottom>
              Risk Level: {riskLevel.toUpperCase()}
            </Typography>
            
            <Box sx={{ mt: 2 }}>
              {totalScore >= 8 && (
                <Alert severity="error" sx={{ mb: 1 }}>
                  <strong>CRITICAL RISK:</strong> Immediate biopsy and urgent referral recommended
                </Alert>
              )}
              
              {totalScore >= 6 && totalScore < 8 && (
                <Alert severity="warning" sx={{ mb: 1 }}>
                  <strong>HIGH RISK:</strong> Biopsy recommended within 2 weeks
                </Alert>
              )}
              
              {totalScore >= 4 && totalScore < 6 && (
                <Alert severity="info" sx={{ mb: 1 }}>
                  <strong>MODERATE RISK:</strong> Consider biopsy and close monitoring
                </Alert>
              )}
              
              {totalScore < 4 && (
                <Alert severity="success" sx={{ mb: 1 }}>
                  <strong>LOW RISK:</strong> Routine monitoring and annual skin checks
                </Alert>
              )}
            </Box>
            
            <Typography variant="body2" sx={{ mt: 2 }}>
              <strong>Guidelines:</strong>
              <br />
              • Score 0-3: Low risk - routine monitoring
              <br />
              • Score 4-5: Moderate risk - consider biopsy
              <br />
              • Score 6-7: High risk - biopsy recommended
              <br />
              • Score 8-10: Critical risk - immediate biopsy required
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default ABCDEForm;