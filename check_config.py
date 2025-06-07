#!/usr/bin/env python3
"""
Check configuration and models directory
"""

import sys
import os
sys.path.append('/app')

from app.core.config import settings

def check_configuration():
    """Check application configuration"""
    print("🔧 Checking Application Configuration...")
    print(f"Models directory configured as: {settings.MODELS_DIR}")
    print(f"ECG sample rate: {settings.ECG_SAMPLE_RATE}")
    print(f"ECG leads: {settings.ECG_LEADS}")
    print(f"Min validation score: {settings.MIN_VALIDATION_SCORE}")
    print(f"Upload directory: {settings.UPLOAD_DIR}")
    print(f"Max file size: {settings.MAX_FILE_SIZE}")
    print(f"Allowed file types: {settings.ALLOWED_FILE_TYPES}")

if __name__ == "__main__":
    check_configuration()
