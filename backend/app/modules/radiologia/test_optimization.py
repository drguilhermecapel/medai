#!/usr/bin/env python3
"""
Test script for optimized radiologia system
"""

import sys
import os
sys.path.append('/home/ubuntu/repos/medai/backend')

def test_optimized_system():
    """Test the optimized radiologia system"""
    try:
        print("🧪 Testing Optimized Radiologia System...")
        
        from optimized_radiologia_service import OptimizedRadiologiaService
        service = OptimizedRadiologiaService()
        status = service.get_system_status()
        
        print("✅ Optimized Radiologia Service initialized successfully")
        print(f"   Models loaded: {status['models_loaded']}")
        print(f"   System status: {status['system_status']}")
        print(f"   DICOM processor ready: {status['dicom_processor_ready']}")
        
        from optimized_radiologia_service import RadiologiaInteligenteMedIA
        compat_service = RadiologiaInteligenteMedIA()
        print("✅ Compatibility wrapper initialized successfully")
        
        from medical_dicom_processor import MedicalDICOMProcessor
        dicom_processor = MedicalDICOMProcessor()
        print("✅ Medical DICOM Processor initialized successfully")
        
        from medical_neural_networks import MedicalModelFactory
        model = MedicalModelFactory.create_model('medical_resnet50', num_classes=4)
        print("✅ Medical Neural Networks initialized successfully")
        
        from clinical_validation_framework import ClinicalValidationFramework
        validator = ClinicalValidationFramework()
        print("✅ Clinical Validation Framework initialized successfully")
        
        from medical_data_augmentation import MedicalDataAugmentation
        augmenter = MedicalDataAugmentation()
        print("✅ Medical Data Augmentation initialized successfully")
        
        print("\n🎉 All optimization components working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_optimized_system()
    sys.exit(0 if success else 1)
