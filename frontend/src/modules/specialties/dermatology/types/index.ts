// Types for Dermatology module
export interface DermatologyLesion {
  fhir_condition_id: string;
  lesion_type: string;
  anatomical_location: string;
  body_region: string;
  abcde_asymmetry?: string;
  abcde_asymmetry_score?: number;
  abcde_border?: string;
  abcde_border_score?: number;
  abcde_color?: string;
  abcde_color_score?: number;
  abcde_diameter_mm?: number;
  abcde_diameter_score?: number;
  abcde_evolving?: string;
  abcde_evolving_score?: number;
  abcde_total_score?: number;
  abcde_risk_level?: 'low' | 'moderate' | 'high' | 'critical';
  malignancy_risk?: 'very_low' | 'low' | 'moderate' | 'high' | 'very_high';
  biopsy_recommended?: boolean;
  biopsy_urgency?: 'routine' | 'urgent' | 'emergent';
  length_mm?: number;
  width_mm?: number;
  height_mm?: number;
  area_mm2?: number;
  clinical_suspicion?: string;
  differential_diagnosis?: string[];
  follow_up_interval_months?: number;
  follow_up_notes?: string;
  photography_performed?: boolean;
  dermoscopy_performed?: boolean;
  dermoscopy_features?: Record<string, any>;
  surface_characteristics?: string[];
  color_description?: string[];
  texture?: string;
  laterality?: string;
  previous_assessments?: any[];
  change_tracking?: Record<string, any>;
  needs_urgent_referral?: boolean;
  calculated_area?: number;
  created_at: string;
  updated_at: string;
}

export interface DermatologyExamination {
  fhir_observation_id: string;
  examination_type: 'full_body' | 'targeted' | 'lesion_check' | 'mole_mapping';
  examination_scope?: string[];
  fitzpatrick_skin_type?: 'I' | 'II' | 'III' | 'IV' | 'V' | 'VI';
  skin_phototype?: string;
  sun_exposure_history?: Record<string, any>;
  sunscreen_use?: 'never' | 'occasional' | 'regular' | 'always';
  family_history_skin_cancer?: boolean;
  family_history_details?: Record<string, any>;
  personal_history_skin_cancer?: boolean;
  previous_biopsies?: any[];
  total_moles_count?: number;
  atypical_moles_count?: number;
  actinic_keratoses?: any[];
  seborrheic_keratoses?: any[];
  other_lesions?: any[];
  overall_skin_condition?: string;
  risk_stratification?: 'low' | 'moderate' | 'high';
  recommendations?: string[];
  next_examination_interval?: number;
  total_photos_taken?: number;
  dermoscopy_images?: number;
  body_map_created?: boolean;
  created_at: string;
  updated_at: string;
}

export interface ABCDEAssessment {
  asymmetry: 'symmetric' | 'asymmetric' | 'unknown';
  asymmetry_score: number;
  border: 'regular' | 'irregular' | 'unknown';
  border_score: number;
  color: 'uniform' | 'varied' | 'unknown';
  color_score: number;
  diameter_mm: number;
  diameter_score: number;
  evolving: 'stable' | 'changing' | 'unknown';
  evolving_score: number;
}

export interface ABCDEAssessmentResult {
  lesion_id: string;
  abcde_total_score: number;
  risk_level: 'low' | 'moderate' | 'high' | 'critical';
  biopsy_recommended: boolean;
  biopsy_urgency?: 'routine' | 'urgent' | 'emergent';
  malignancy_risk: 'very_low' | 'low' | 'moderate' | 'high' | 'very_high';
}

export interface LesionStatistics {
  total_lesions: number;
  risk_distribution: Record<string, number>;
  biopsies_recommended: number;
  urgent_biopsies: number;
  region_distribution: Record<string, number>;
}

export interface CreateLesionRequest {
  patient_id: string;
  lesion_type: string;
  anatomical_location: string;
  body_region: string;
  length_mm?: number;
  width_mm?: number;
  height_mm?: number;
  photography_performed?: boolean;
  dermoscopy_performed?: boolean;
  clinical_suspicion?: string;
  differential_diagnosis?: string[];
}

export interface CreateExaminationRequest {
  patient_id: string;
  encounter_id?: string;
  examination_type: 'full_body' | 'targeted' | 'lesion_check' | 'mole_mapping';
  examination_scope?: string[];
  fitzpatrick_skin_type?: string;
  sunscreen_use?: string;
  family_history_skin_cancer?: boolean;
  total_moles_count?: number;
  atypical_moles_count?: number;
  overall_skin_condition?: string;
  risk_stratification?: 'low' | 'moderate' | 'high';
  recommendations?: string[];
  next_examination_interval?: number;
}

export type LesionType = 
  | 'melanocytic_nevus'
  | 'atypical_nevus'
  | 'seborrheic_keratosis'
  | 'basal_cell_carcinoma'
  | 'squamous_cell_carcinoma'
  | 'melanoma'
  | 'suspicious_lesion'
  | 'actinic_keratosis'
  | 'dermatofibroma'
  | 'lipoma'
  | 'cyst'
  | 'other';

export type BodyRegion = 
  | 'head'
  | 'neck'
  | 'trunk'
  | 'arm'
  | 'leg'
  | 'hand'
  | 'foot'
  | 'genital'
  | 'other';

export type RiskLevel = 'low' | 'moderate' | 'high' | 'critical';
export type BiopsyUrgency = 'routine' | 'urgent' | 'emergent';
export type MalignancyRisk = 'very_low' | 'low' | 'moderate' | 'high' | 'very_high';