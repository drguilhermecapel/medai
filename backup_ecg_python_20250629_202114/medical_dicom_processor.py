"""
Optimized DICOM Processor for Medical Imaging AI
Based on technical analysis recommendations for preserving diagnostic information
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pydicom
from pydicom.dataset import Dataset

logger = logging.getLogger(__name__)

@dataclass
class DICOMMetadata:
    """Preserved DICOM metadata for medical analysis"""
    study_instance_uid: str
    series_instance_uid: str
    sop_instance_uid: str
    patient_id: str
    acquisition_date: str
    modality: str
    pixel_spacing: Optional[Tuple[float, float]]
    slice_thickness: Optional[float]
    window_center: float
    window_width: float
    rescale_slope: float
    rescale_intercept: float
    original_shape: Tuple[int, ...]
    manufacturer: Optional[str]
    model_name: Optional[str]

class MedicalDICOMProcessor:
    """
    Optimized DICOM processor that preserves diagnostic information
    and applies medical-specific preprocessing
    """
    
    def __init__(self):
        self.modality_windows = {
            'CT': {'center': 40, 'width': 400},  # Soft tissue window
            'MR': {'center': 300, 'width': 600},
            'CR': {'center': 2048, 'width': 4096},  # Chest X-ray
            'DX': {'center': 2048, 'width': 4096},  # Digital X-ray
            'MG': {'center': 1024, 'width': 2048},  # Mammography
        }
    
    def process_dicom(self, dicom_data: Dataset) -> Tuple[np.ndarray, DICOMMetadata]:
        """
        Process DICOM data preserving medical image integrity
        
        Args:
            dicom_data: PyDICOM dataset
            
        Returns:
            Tuple of processed image array and metadata
        """
        try:
            image_array = dicom_data.pixel_array.astype(np.float32)
            
            metadata = self._extract_metadata(dicom_data)
            
            image_array = self._apply_rescale_parameters(image_array, metadata)
            
            image_array = self._apply_medical_windowing(image_array, metadata)
            
            self._validate_image_quality(image_array, metadata)
            
            return image_array, metadata
            
        except Exception as e:
            logger.error(f"DICOM processing failed: {e}")
            raise ValueError(f"DICOM processing failed: {e}")
    
    def _extract_metadata(self, ds: Dataset) -> DICOMMetadata:
        """Extract and preserve critical DICOM metadata"""
        return DICOMMetadata(
            study_instance_uid=str(ds.get('StudyInstanceUID', '')),
            series_instance_uid=str(ds.get('SeriesInstanceUID', '')),
            sop_instance_uid=str(ds.get('SOPInstanceUID', '')),
            patient_id=self._hash_patient_id(str(ds.get('PatientID', ''))),
            acquisition_date=str(ds.get('AcquisitionDate', ds.get('StudyDate', ''))),
            modality=str(ds.get('Modality', 'Unknown')),
            pixel_spacing=self._get_pixel_spacing(ds),
            slice_thickness=float(ds.get('SliceThickness', 0)) if ds.get('SliceThickness') else None,
            window_center=self._get_window_center(ds),
            window_width=self._get_window_width(ds),
            rescale_slope=float(ds.get('RescaleSlope', 1.0)),
            rescale_intercept=float(ds.get('RescaleIntercept', 0.0)),
            original_shape=ds.pixel_array.shape,
            manufacturer=str(ds.get('Manufacturer', '')),
            model_name=str(ds.get('ManufacturerModelName', ''))
        )
    
    def _get_pixel_spacing(self, ds: Dataset) -> Optional[Tuple[float, float]]:
        """Extract pixel spacing with fallback options"""
        if hasattr(ds, 'PixelSpacing') and ds.PixelSpacing:
            return (float(ds.PixelSpacing[0]), float(ds.PixelSpacing[1]))
        elif hasattr(ds, 'ImagerPixelSpacing') and ds.ImagerPixelSpacing:
            return (float(ds.ImagerPixelSpacing[0]), float(ds.ImagerPixelSpacing[1]))
        return None
    
    def _get_window_center(self, ds: Dataset) -> float:
        """Get window center with modality-specific defaults"""
        if hasattr(ds, 'WindowCenter') and ds.WindowCenter:
            if isinstance(ds.WindowCenter, (list, tuple)):
                return float(ds.WindowCenter[0])
            return float(ds.WindowCenter)
        
        modality = str(ds.get('Modality', 'Unknown'))
        return self.modality_windows.get(modality, {'center': 128})['center']
    
    def _get_window_width(self, ds: Dataset) -> float:
        """Get window width with modality-specific defaults"""
        if hasattr(ds, 'WindowWidth') and ds.WindowWidth:
            if isinstance(ds.WindowWidth, (list, tuple)):
                return float(ds.WindowWidth[0])
            return float(ds.WindowWidth)
        
        modality = str(ds.get('Modality', 'Unknown'))
        return self.modality_windows.get(modality, {'width': 256})['width']
    
    def _apply_rescale_parameters(self, image: np.ndarray, metadata: DICOMMetadata) -> np.ndarray:
        """Apply DICOM rescale parameters to preserve Hounsfield Units"""
        return image * metadata.rescale_slope + metadata.rescale_intercept
    
    def _apply_medical_windowing(self, image: np.ndarray, metadata: DICOMMetadata) -> np.ndarray:
        """Apply appropriate windowing for medical imaging"""
        img_min = metadata.window_center - metadata.window_width / 2
        img_max = metadata.window_center + metadata.window_width / 2
        
        windowed = np.clip(image, img_min, img_max)
        
        if metadata.window_width > 0:
            windowed = (windowed - img_min) / metadata.window_width
        
        return windowed
    
    def _validate_image_quality(self, image: np.ndarray, metadata: DICOMMetadata) -> None:
        """Validate image quality for medical analysis"""
        if image.size == 0:
            raise ValueError("Empty image array")
        
        if np.all(image == image.flat[0]):
            logger.warning("Image appears to be uniform - possible processing error")
        
        if metadata.pixel_spacing and (metadata.pixel_spacing[0] <= 0 or metadata.pixel_spacing[1] <= 0):
            logger.warning("Invalid pixel spacing detected")
    
    def _hash_patient_id(self, patient_id: str) -> str:
        """Hash patient ID for privacy compliance"""
        import hashlib
        return hashlib.sha256(patient_id.encode()).hexdigest()[:16]

class ModalitySpecificNormalizer:
    """Modality-specific normalization for different imaging types"""
    
    def __init__(self):
        self.normalization_params = {
            'CT': {'mean': -600, 'std': 400},  # Hounsfield Units
            'MR': {'mean': 300, 'std': 200},
            'CR': {'mean': 2048, 'std': 1024},
            'DX': {'mean': 2048, 'std': 1024},
            'MG': {'mean': 1024, 'std': 512},
        }
    
    def normalize(self, image: np.ndarray, modality: str) -> np.ndarray:
        """Apply modality-specific normalization"""
        params = self.normalization_params.get(modality, {'mean': 0, 'std': 1})
        
        normalized = (image - params['mean']) / params['std']
        
        normalized = np.clip(normalized, -3, 3)
        
        return normalized

class PatientLevelDataSplitter:
    """Ensures patient-level data splitting to prevent data leakage"""
    
    def __init__(self):
        pass
    
    def split_by_patient(self, metadata_list: list[DICOMMetadata], 
                        train_ratio: float = 0.7, 
                        val_ratio: float = 0.15,
                        test_ratio: float = 0.15) -> Dict[str, list[int]]:
        """
        Split data by patient to prevent leakage
        
        Args:
            metadata_list: List of DICOM metadata
            train_ratio: Training set ratio
            val_ratio: Validation set ratio  
            test_ratio: Test set ratio
            
        Returns:
            Dictionary with train/val/test indices
        """
        if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
            raise ValueError("Ratios must sum to 1.0")
        
        patient_groups = {}
        for idx, metadata in enumerate(metadata_list):
            patient_id = metadata.patient_id
            if patient_id not in patient_groups:
                patient_groups[patient_id] = []
            patient_groups[patient_id].append(idx)
        
        patients = list(patient_groups.keys())
        np.random.shuffle(patients)
        
        n_patients = len(patients)
        n_train = int(n_patients * train_ratio)
        n_val = int(n_patients * val_ratio)
        
        train_patients = patients[:n_train]
        val_patients = patients[n_train:n_train + n_val]
        test_patients = patients[n_train + n_val:]
        
        train_indices = []
        val_indices = []
        test_indices = []
        
        for patient in train_patients:
            train_indices.extend(patient_groups[patient])
        for patient in val_patients:
            val_indices.extend(patient_groups[patient])
        for patient in test_patients:
            test_indices.extend(patient_groups[patient])
        
        return {
            'train': train_indices,
            'val': val_indices,
            'test': test_indices
        }
