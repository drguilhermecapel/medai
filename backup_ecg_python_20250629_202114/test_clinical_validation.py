#!/usr/bin/env python3
"""
Test script for clinical validation framework
"""

import sys
import os
sys.path.append('/app')

import numpy as np
from app.validation.clinical_validation import ClinicalValidationFramework, PathologyType

def test_clinical_validation():
    """Test the clinical validation framework"""
    print("🔬 Testing Clinical Validation Framework...")
    
    validator = ClinicalValidationFramework()
    
    np.random.seed(42)
    predictions = np.random.random(10000)  # 10k samples as required
    ground_truth = np.random.choice([0, 1], 10000, p=[0.9, 0.1])  # 10% positive cases
    detection_times = np.random.uniform(5000, 15000, 10000)  # Detection times in ms
    
    try:
        metrics = validator.validate_pathology_detection(
            PathologyType.STEMI, 
            predictions, 
            ground_truth, 
            detection_times
        )
        print(f"✅ STEMI validation completed:")
        print(f"  Sensitivity: {metrics.sensitivity:.2f}%")
        print(f"  Specificity: {metrics.specificity:.2f}%")
        print(f"  NPV: {metrics.npv:.2f}%")
        print(f"  Detection time: {metrics.detection_time_ms:.0f}ms")
        print(f"  Sample size: {metrics.sample_size}")
        
        report = validator.generate_validation_report()
        print(f"\n✅ Validation report generated: {report['compliance_level']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Clinical validation failed: {e}")
        return False

def test_ml_model_service():
    """Test ML model service functionality"""
    print("\n🤖 Testing ML Model Service...")
    
    try:
        from app.services.ml_model_service import MLModelService
        
        ml_service = MLModelService()
        
        model_info = ml_service.get_model_info()
        print(f"✅ ML Model Service initialized")
        print(f"  Loaded models: {model_info['loaded_models']}")
        print(f"  Memory usage: {model_info['memory_usage']}")
        
        return True
        
    except Exception as e:
        print(f"❌ ML Model Service test failed: {e}")
        return False

if __name__ == "__main__":
    print("🏥 SPEI Medical Image Analysis Testing")
    print("=" * 50)
    
    success = True
    
    success &= test_clinical_validation()
    
    success &= test_ml_model_service()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All medical analysis tests PASSED")
        sys.exit(0)
    else:
        print("❌ Some medical analysis tests FAILED")
        sys.exit(1)
