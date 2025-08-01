import { RiskLevel, BiopsyUrgency, MalignancyRisk, LesionType, BodyRegion } from '../types';

/**
 * Calculate ABCDE total score from individual scores
 */
export const calculateABCDEScore = (scores: {
  asymmetry_score?: number;
  border_score?: number;
  color_score?: number;
  diameter_score?: number;
  evolving_score?: number;
}): number => {
  const { asymmetry_score = 0, border_score = 0, color_score = 0, diameter_score = 0, evolving_score = 0 } = scores;
  return asymmetry_score + border_score + color_score + diameter_score + evolving_score;
};

/**
 * Determine risk level based on ABCDE total score
 */
export const determineRiskLevel = (totalScore: number): RiskLevel => {
  if (totalScore >= 8) return 'critical';
  if (totalScore >= 6) return 'high';
  if (totalScore >= 4) return 'moderate';
  return 'low';
};

/**
 * Determine biopsy urgency based on total score and risk factors
 */
export const determineBiopsyUrgency = (
  totalScore: number,
  riskLevel: RiskLevel,
  hasChanges: boolean = false
): BiopsyUrgency => {
  if (totalScore >= 8 || riskLevel === 'critical' || hasChanges) {
    return 'emergent';
  }
  if (totalScore >= 6 || riskLevel === 'high') {
    return 'urgent';
  }
  return 'routine';
};

/**
 * Determine malignancy risk based on multiple factors
 */
export const determineMalignancyRisk = (
  totalScore: number,
  lesionType: string,
  hasAsymmetry: boolean,
  isEvolving: boolean
): MalignancyRisk => {
  // High-risk lesion types
  const highRiskTypes = ['melanoma', 'basal_cell_carcinoma', 'squamous_cell_carcinoma'];
  const suspiciousTypes = ['suspicious_lesion', 'atypical_nevus'];
  
  if (highRiskTypes.includes(lesionType) || totalScore >= 8) {
    return 'very_high';
  }
  
  if (suspiciousTypes.includes(lesionType) || totalScore >= 6 || (hasAsymmetry && isEvolving)) {
    return 'high';
  }
  
  if (totalScore >= 4 || hasAsymmetry || isEvolving) {
    return 'moderate';
  }
  
  if (totalScore >= 2) {
    return 'low';
  }
  
  return 'very_low';
};

/**
 * Check if a lesion needs urgent referral
 */
export const needsUrgentReferral = (
  totalScore: number,
  riskLevel: RiskLevel,
  malignancyRisk: MalignancyRisk,
  biopsyUrgency: BiopsyUrgency
): boolean => {
  return (
    totalScore >= 8 ||
    riskLevel === 'critical' ||
    ['high', 'very_high'].includes(malignancyRisk) ||
    biopsyUrgency === 'emergent'
  );
};

/**
 * Calculate estimated lesion area (assuming elliptical shape)
 */
export const calculateLesionArea = (length: number, width: number): number => {
  if (length <= 0 || width <= 0) return 0;
  return Math.PI * (length / 2) * (width / 2);
};

/**
 * Format lesion size for display
 */
export const formatLesionSize = (length?: number, width?: number, area?: number): string => {
  if (length && width) {
    const calculatedArea = area || calculateLesionArea(length, width);
    return `${length} × ${width} mm (${calculatedArea.toFixed(1)} mm²)`;
  }
  if (length) {
    return `${length} mm`;
  }
  return 'Not measured';
};

/**
 * Get risk color for UI components
 */
export const getRiskColor = (riskLevel: RiskLevel): 'success' | 'warning' | 'error' | 'info' => {
  switch (riskLevel) {
    case 'low': return 'success';
    case 'moderate': return 'warning';
    case 'high': case 'critical': return 'error';
    default: return 'info';
  }
};

/**
 * Get human-readable lesion type
 */
export const formatLesionType = (lesionType: string): string => {
  return lesionType
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase());
};

/**
 * Get human-readable body region
 */
export const formatBodyRegion = (bodyRegion: string): string => {
  return bodyRegion
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase());
};

/**
 * Generate follow-up recommendations based on risk assessment
 */
export const generateFollowUpRecommendations = (
  riskLevel: RiskLevel,
  totalScore: number,
  biopsyRecommended: boolean,
  hasPhotography: boolean = false
): string[] => {
  const recommendations: string[] = [];
  
  if (biopsyRecommended) {
    if (totalScore >= 8) {
      recommendations.push('Immediate biopsy required - refer urgently');
    } else if (totalScore >= 6) {
      recommendations.push('Biopsy recommended within 2 weeks');
    } else {
      recommendations.push('Consider biopsy - routine referral');
    }
  }
  
  switch (riskLevel) {
    case 'critical':
      recommendations.push('Follow-up in 1-3 months');
      recommendations.push('Dermoscopy imaging recommended');
      break;
    case 'high':
      recommendations.push('Follow-up in 3-6 months');
      if (!hasPhotography) {
        recommendations.push('Photography for monitoring recommended');
      }
      break;
    case 'moderate':
      recommendations.push('Follow-up in 6-12 months');
      break;
    case 'low':
      recommendations.push('Routine annual skin check');
      break;
  }
  
  recommendations.push('Patient education on self-examination');
  recommendations.push('Sun protection counseling');
  
  return recommendations;
};

/**
 * Validate ABCDE scores
 */
export const validateABCDEScores = (scores: {
  asymmetry_score?: number;
  border_score?: number;
  color_score?: number;
  diameter_score?: number;
  evolving_score?: number;
}): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  Object.entries(scores).forEach(([key, value]) => {
    if (value !== undefined) {
      if (typeof value !== 'number' || value < 0 || value > 2) {
        errors.push(`${key.replace('_score', '')} score must be between 0 and 2`);
      }
    }
  });
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Get suggested lesion types based on characteristics
 */
export const getSuggestedLesionTypes = (characteristics: {
  isAsymmetric?: boolean;
  hasIrregularBorder?: boolean;
  hasVariedColor?: boolean;
  isLarge?: boolean;
  isEvolving?: boolean;
}): LesionType[] => {
  const suggestions: LesionType[] = [];
  const { isAsymmetric, hasIrregularBorder, hasVariedColor, isLarge, isEvolving } = characteristics;
  
  // High suspicion characteristics
  if (isAsymmetric && hasIrregularBorder && hasVariedColor && isEvolving) {
    suggestions.push('melanoma', 'suspicious_lesion');
  } else if (hasIrregularBorder && isEvolving) {
    suggestions.push('basal_cell_carcinoma', 'squamous_cell_carcinoma');
  } else if (isAsymmetric || hasVariedColor) {
    suggestions.push('atypical_nevus', 'suspicious_lesion');
  } else {
    suggestions.push('melanocytic_nevus', 'seborrheic_keratosis');
  }
  
  return suggestions;
};

/**
 * Generate body map coordinates for lesion placement
 */
export const getBodyMapCoordinates = (anatomicalLocation: string, bodyRegion: BodyRegion): { x: number; y: number } => {
  // This would be implemented based on a body diagram coordinate system
  // For now, return default coordinates
  const regionCoordinates: Record<BodyRegion, { x: number; y: number }> = {
    head: { x: 200, y: 50 },
    neck: { x: 200, y: 100 },
    trunk: { x: 200, y: 200 },
    arm: { x: 150, y: 180 },
    leg: { x: 180, y: 350 },
    hand: { x: 100, y: 220 },
    foot: { x: 180, y: 450 },
    genital: { x: 200, y: 280 },
    other: { x: 200, y: 200 }
  };
  
  return regionCoordinates[bodyRegion] || { x: 200, y: 200 };
};

/**
 * Calculate next examination date based on risk level
 */
export const calculateNextExaminationDate = (
  riskLevel: RiskLevel,
  baseDate: Date = new Date()
): Date => {
  const nextDate = new Date(baseDate);
  
  switch (riskLevel) {
    case 'critical':
      nextDate.setMonth(nextDate.getMonth() + 3); // 3 months
      break;
    case 'high':
      nextDate.setMonth(nextDate.getMonth() + 6); // 6 months
      break;
    case 'moderate':
      nextDate.setFullYear(nextDate.getFullYear() + 1); // 1 year
      break;
    case 'low':
    default:
      nextDate.setFullYear(nextDate.getFullYear() + 1); // 1 year
      break;
  }
  
  return nextDate;
};