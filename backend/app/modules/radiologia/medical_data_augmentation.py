"""
Medical-specific data augmentation techniques
Implements safe augmentations that preserve anatomical validity
"""

import logging
from typing import Any, Optional
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import random

logger = logging.getLogger(__name__)


class MedicalDataAugmentation:
    """
    Medical imaging-specific data augmentation that preserves anatomical validity
    Based on clinical guidelines and radiological best practices
    """
    
    def __init__(self):
        self.modality_params = {
            'CR': {  # Chest X-ray
                'rotation_range': (-5, 5),  # Small rotations only
                'brightness_range': (0.9, 1.1),
                'contrast_range': (0.9, 1.1),
                'noise_std': 0.01,
                'allow_horizontal_flip': False,  # Anatomically incorrect
                'allow_elastic_deform': False
            },
            'DX': {  # Digital X-ray
                'rotation_range': (-3, 3),
                'brightness_range': (0.95, 1.05),
                'contrast_range': (0.95, 1.05),
                'noise_std': 0.005,
                'allow_horizontal_flip': False,
                'allow_elastic_deform': False
            },
            'CT': {  # Computed Tomography
                'rotation_range': (-2, 2),
                'brightness_range': (0.98, 1.02),
                'contrast_range': (0.95, 1.05),
                'noise_std': 0.01,
                'allow_horizontal_flip': False,
                'allow_elastic_deform': True,
                'elastic_alpha': 50,
                'elastic_sigma': 5
            },
            'MR': {  # Magnetic Resonance
                'rotation_range': (-3, 3),
                'brightness_range': (0.95, 1.05),
                'contrast_range': (0.9, 1.1),
                'noise_std': 0.02,
                'allow_horizontal_flip': False,
                'allow_elastic_deform': True,
                'elastic_alpha': 30,
                'elastic_sigma': 3
            }
        }
        
        logger.info("Medical Data Augmentation initialized")
    
    def augment_medical_image(self, image: np.ndarray, modality: str, 
                            severity: float = 0.5) -> np.ndarray:
        """
        Apply medical-safe augmentations to an image
        
        Args:
            image: Input medical image (2D grayscale)
            modality: Medical imaging modality (CR, DX, CT, MR)
            severity: Augmentation severity (0.0 to 1.0)
            
        Returns:
            Augmented image
        """
        if modality not in self.modality_params:
            logger.warning(f"Unknown modality {modality}, using default parameters")
            modality = 'CR'
        
        params = self.modality_params[modality]
        augmented = image.copy()
        
        if random.random() < 0.7:  # 70% chance of rotation
            augmented = self._safe_rotation(augmented, params['rotation_range'], severity)
        
        if random.random() < 0.8:  # 80% chance of brightness adjustment
            augmented = self._adjust_brightness(augmented, params['brightness_range'], severity)
        
        if random.random() < 0.8:  # 80% chance of contrast adjustment
            augmented = self._adjust_contrast(augmented, params['contrast_range'], severity)
        
        if random.random() < 0.5:  # 50% chance of noise addition
            augmented = self._add_medical_noise(augmented, params['noise_std'], severity)
        
        if params.get('allow_elastic_deform', False) and random.random() < 0.3:
            augmented = self._elastic_deformation(
                augmented, 
                params.get('elastic_alpha', 50), 
                params.get('elastic_sigma', 5),
                severity
            )
        
        return augmented
    
    def _safe_rotation(self, image: np.ndarray, rotation_range: tuple[float, float], 
                      severity: float) -> np.ndarray:
        """Apply small, anatomically safe rotations"""
        min_angle, max_angle = rotation_range
        angle = random.uniform(min_angle * severity, max_angle * severity)
        
        pil_image = Image.fromarray((image * 255).astype(np.uint8))
        rotated = pil_image.rotate(angle, fillcolor=0, expand=False)
        
        return np.array(rotated).astype(np.float32) / 255.0
    
    def _adjust_brightness(self, image: np.ndarray, brightness_range: tuple[float, float],
                          severity: float) -> np.ndarray:
        """Adjust brightness while preserving medical image characteristics"""
        min_bright, max_bright = brightness_range
        factor = random.uniform(
            1 - (1 - min_bright) * severity,
            1 + (max_bright - 1) * severity
        )
        
        adjusted = image * factor
        return np.clip(adjusted, 0.0, 1.0)
    
    def _adjust_contrast(self, image: np.ndarray, contrast_range: tuple[float, float],
                        severity: float) -> np.ndarray:
        """Adjust contrast preserving diagnostic information"""
        min_contrast, max_contrast = contrast_range
        factor = random.uniform(
            1 - (1 - min_contrast) * severity,
            1 + (max_contrast - 1) * severity
        )
        
        mean = np.mean(image)
        adjusted = (image - mean) * factor + mean
        return np.clip(adjusted, 0.0, 1.0)
    
    def _add_medical_noise(self, image: np.ndarray, noise_std: float, 
                          severity: float) -> np.ndarray:
        """Add realistic medical imaging noise"""
        actual_std = noise_std * severity
        
        noise = np.random.normal(0, actual_std, image.shape)
        noisy = image + noise
        
        return np.clip(noisy, 0.0, 1.0)
    
    def _elastic_deformation(self, image: np.ndarray, alpha: float, sigma: float,
                           severity: float) -> np.ndarray:
        """Apply mild elastic deformation for soft tissue simulation"""
        try:
            from scipy.ndimage import gaussian_filter, map_coordinates
            
            alpha = alpha * severity
            
            shape = image.shape
            
            dx = gaussian_filter(np.random.randn(*shape), sigma) * alpha
            dy = gaussian_filter(np.random.randn(*shape), sigma) * alpha
            
            x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
            indices = np.reshape(y + dy, (-1, 1)), np.reshape(x + dx, (-1, 1))
            
            deformed = map_coordinates(image, indices, order=1, mode='reflect')
            return deformed.reshape(shape)
            
        except ImportError:
            logger.warning("SciPy not available, skipping elastic deformation")
            return image
        except Exception as e:
            logger.error(f"Elastic deformation failed: {e}")
            return image
    
    def create_augmentation_pipeline(self, modality: str, num_augmentations: int = 5) -> list:
        """
        Create a pipeline of augmentations for training
        
        Args:
            modality: Medical imaging modality
            num_augmentations: Number of augmented versions per image
            
        Returns:
            List of augmentation functions
        """
        pipeline = []
        
        for i in range(num_augmentations):
            severity = 0.3 + (i / num_augmentations) * 0.4  # 0.3 to 0.7
            
            pipeline.append(
                lambda img, mod=modality, sev=severity: self.augment_medical_image(img, mod, sev)
            )
        
        return pipeline
    
    def validate_augmentation(self, original: np.ndarray, augmented: np.ndarray,
                            modality: str) -> dict[str, Any]:
        """
        Validate that augmentation preserves medical image integrity
        
        Returns:
            Validation report
        """
        validation_report = {
            'valid': True,
            'warnings': [],
            'metrics': {}
        }
        
        orig_range = (np.min(original), np.max(original))
        aug_range = (np.min(augmented), np.max(augmented))
        
        if abs(orig_range[0] - aug_range[0]) > 0.1 or abs(orig_range[1] - aug_range[1]) > 0.1:
            validation_report['warnings'].append("Significant intensity range change detected")
        
        noise_level = np.std(augmented - original)
        if noise_level > 0.05:
            validation_report['warnings'].append(f"High noise level: {noise_level:.3f}")
        
        correlation = np.corrcoef(original.flatten(), augmented.flatten())[0, 1]
        validation_report['metrics']['correlation'] = correlation
        
        if correlation < 0.8:
            validation_report['valid'] = False
            validation_report['warnings'].append(f"Low structural similarity: {correlation:.3f}")
        
        return validation_report


class MedicalAugmentationValidator:
    """Validates medical augmentations for clinical appropriateness"""
    
    def __init__(self):
        self.anatomical_constraints = {
            'chest_xray': {
                'preserve_laterality': True,
                'preserve_cardiac_position': True,
                'max_rotation': 5.0,
                'preserve_diaphragm_contour': True
            },
            'brain_mri': {
                'preserve_symmetry': True,
                'max_rotation': 3.0,
                'preserve_midline': True
            }
        }
    
    def validate_clinical_appropriateness(self, original: np.ndarray, 
                                        augmented: np.ndarray,
                                        anatomy_type: str) -> bool:
        """
        Validate that augmentation maintains clinical appropriateness
        
        Args:
            original: Original medical image
            augmented: Augmented medical image  
            anatomy_type: Type of anatomy (chest_xray, brain_mri, etc.)
            
        Returns:
            True if augmentation is clinically appropriate
        """
        if anatomy_type not in self.anatomical_constraints:
            return True  # Default to valid if no constraints defined
        
        constraints = self.anatomical_constraints[anatomy_type]
        
        if constraints.get('preserve_symmetry', False):
            if not self._check_symmetry_preservation(original, augmented):
                return False
        
        if constraints.get('preserve_laterality', False):
            if not self._check_laterality_preservation(original, augmented):
                return False
        
        return True
    
    def _check_symmetry_preservation(self, original: np.ndarray, 
                                   augmented: np.ndarray) -> bool:
        """Check if brain symmetry is preserved"""
        height, width = original.shape
        mid = width // 2
        
        orig_left = original[:, :mid]
        orig_right = np.fliplr(original[:, mid:])
        orig_symmetry = np.corrcoef(orig_left.flatten(), orig_right.flatten())[0, 1]
        
        aug_left = augmented[:, :mid]
        aug_right = np.fliplr(augmented[:, mid:])
        aug_symmetry = np.corrcoef(aug_left.flatten(), aug_right.flatten())[0, 1]
        
        return abs(orig_symmetry - aug_symmetry) < 0.1
    
    def _check_laterality_preservation(self, original: np.ndarray,
                                     augmented: np.ndarray) -> bool:
        """Check if chest X-ray laterality is preserved (no horizontal flips)"""
        correlation_normal = np.corrcoef(original.flatten(), augmented.flatten())[0, 1]
        correlation_flipped = np.corrcoef(original.flatten(), np.fliplr(augmented).flatten())[0, 1]
        
        return correlation_normal > correlation_flipped
