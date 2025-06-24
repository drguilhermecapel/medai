"""
Smart Mocks para Dados Médicos Realistas - MedAI
"""

import numpy as np
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any  # Adicionado 'Any' aqui


class SmartECGMock:
    """Smart mock for generating realistic ECG data."""
    
    @staticmethod
    def generate_normal_ecg(duration_seconds: int = 10, sampling_rate: int = 500) -> np.ndarray:
        """Generate normal ECG data with realistic morphology."""
        samples = duration_seconds * sampling_rate
        time = np.linspace(0, duration_seconds, samples)
        
        # Base rhythm
        heart_rate = random.randint(60, 90)
        heart_period = 60.0 / heart_rate
        
        ecg_signal = np.zeros((samples, 12))
        
        for lead in range(12):
            # P wave, QRS complex, T wave simulation
            signal = np.zeros(samples)
            
            for beat_time in np.arange(0, duration_seconds, heart_period):
                beat_idx = int(beat_time * sampling_rate)
                if beat_idx < samples:
                    # P wave (100ms duration, 0.15mV amplitude)
                    p_wave_samples = int(0.1 * sampling_rate)
                    if beat_idx + p_wave_samples < samples:
                        t = np.linspace(0, np.pi, p_wave_samples)
                        signal[beat_idx:beat_idx + p_wave_samples] += 0.15 * np.sin(t)
                    
                    # QRS complex (80ms duration, 1-2mV amplitude)
                    qrs_start = beat_idx + int(0.16 * sampling_rate)
                    qrs_samples = int(0.08 * sampling_rate)
                    if qrs_start + qrs_samples < samples:
                        # Q wave
                        signal[qrs_start:qrs_start + qrs_samples//4] -= 0.2
                        # R wave
                        r_peak = qrs_start + qrs_samples//4
                        signal[r_peak:r_peak + qrs_samples//2] = np.linspace(-0.2, 1.5, qrs_samples//2)
                        signal[r_peak + qrs_samples//2:qrs_start + qrs_samples] = np.linspace(1.5, -0.1, qrs_samples//4)
                    
                    # T wave (200ms duration, 0.3mV amplitude)
                    t_wave_start = qrs_start + int(0.1 * sampling_rate)
                    t_wave_samples = int(0.2 * sampling_rate)
                    if t_wave_start + t_wave_samples < samples:
                        t = np.linspace(0, np.pi, t_wave_samples)
                        signal[t_wave_start:t_wave_start + t_wave_samples] += 0.3 * np.sin(t)
            
            # Add baseline wander and noise
            baseline_wander = 0.05 * np.sin(2 * np.pi * 0.15 * time)
            noise = 0.02 * np.random.randn(samples)
            
            ecg_signal[:, lead] = signal + baseline_wander + noise
            
            # Lead-specific adjustments
            if lead in [1, 2, 3]:  # AVR, AVL, AVF
                ecg_signal[:, lead] *= 0.5
            elif lead >= 6:  # V1-V6
                ecg_signal[:, lead] *= (0.8 + 0.05 * (lead - 6))
        
        return ecg_signal

    @staticmethod
    def generate_arrhythmia_ecg(arrhythmia_type: str, duration_seconds: int = 10) -> np.ndarray:
        """Generate ECG with specific arrhythmia patterns."""
        sampling_rate = 500
        samples = duration_seconds * sampling_rate
        ecg_signal = np.zeros((samples, 12))
        
        if arrhythmia_type == "atrial_fibrillation":
            # Irregular RR intervals, absent P waves
            beat_times = []
            current_time = 0
            while current_time < duration_seconds:
                # Random RR interval between 0.4-1.2 seconds
                rr_interval = random.uniform(0.4, 1.2)
                beat_times.append(current_time)
                current_time += rr_interval
            
            for lead in range(12):
                signal = np.zeros(samples)
                
                # Fibrillatory waves
                fib_freq = random.uniform(4, 7)
                fib_amplitude = random.uniform(0.05, 0.1)
                signal += fib_amplitude * np.sin(2 * np.pi * fib_freq * np.linspace(0, duration_seconds, samples))
                
                # QRS complexes at irregular intervals
                for beat_time in beat_times:
                    beat_idx = int(beat_time * sampling_rate)
                    if beat_idx + 40 < samples:
                        # Narrow QRS
                        signal[beat_idx:beat_idx + 40] += np.concatenate([
                            np.linspace(0, 1.2, 20),
                            np.linspace(1.2, -0.2, 20)
                        ])
                
                ecg_signal[:, lead] = signal + 0.01 * np.random.randn(samples)
        
        elif arrhythmia_type == "ventricular_tachycardia":
            # Wide QRS complexes, rate >100 bpm
            heart_rate = random.randint(150, 200)
            heart_period = 60.0 / heart_rate
            
            for lead in range(12):
                signal = np.zeros(samples)
                
                for beat_time in np.arange(0, duration_seconds, heart_period):
                    beat_idx = int(beat_time * sampling_rate)
                    if beat_idx + 80 < samples:
                        # Wide QRS (>120ms)
                        signal[beat_idx:beat_idx + 80] = np.concatenate([
                            np.linspace(0, -0.5, 20),
                            np.linspace(-0.5, 1.8, 40),
                            np.linspace(1.8, 0, 20)
                        ])
                
                ecg_signal[:, lead] = signal + 0.02 * np.random.randn(samples)
        
        elif arrhythmia_type == "stemi":
            # ST elevation in specific leads
            base_ecg = SmartECGMock.generate_normal_ecg(duration_seconds)
            
            # Add ST elevation to leads II, III, aVF (inferior STEMI)
            affected_leads = [1, 2, 5]  # Lead indices
            for lead in affected_leads:
                # Find QRS end points and elevate ST segment
                ecg_signal[:, lead] = base_ecg[:, lead]
                # Simple ST elevation simulation
                ecg_signal[:, lead] += 0.3  # 3mm elevation
        
        else:
            # Default to normal ECG
            ecg_signal = SmartECGMock.generate_normal_ecg(duration_seconds)
        
        return ecg_signal

    @staticmethod
    def generate_noisy_ecg(noise_type: str = "baseline_wander", duration_seconds: int = 10) -> np.ndarray:
        """Generate ECG with specific noise patterns."""
        base_ecg = SmartECGMock.generate_normal_ecg(duration_seconds)
        sampling_rate = 500
        samples = duration_seconds * sampling_rate
        time = np.linspace(0, duration_seconds, samples)
        
        if noise_type == "baseline_wander":
            # Low frequency drift
            wander = 0.3 * np.sin(2 * np.pi * 0.1 * time) + 0.2 * np.sin(2 * np.pi * 0.05 * time)
            for lead in range(12):
                base_ecg[:, lead] += wander
        
        elif noise_type == "muscle_artifact":
            # High frequency noise
            for lead in range(12):
                muscle_noise = 0.1 * np.random.randn(samples)
                muscle_noise = np.convolve(muscle_noise, np.ones(5)/5, mode='same')  # Slight smoothing
                base_ecg[:, lead] += muscle_noise
        
        elif noise_type == "powerline":
            # 60Hz interference
            powerline = 0.05 * np.sin(2 * np.pi * 60 * time)
            for lead in range(12):
                base_ecg[:, lead] += powerline
        
        return base_ecg


class SmartPatientMock:
    """Smart mock for generating realistic patient data."""
    
    @staticmethod
    def generate_patient_data(age_range: Tuple[int, int] = (18, 90), 
                            condition: Optional[str] = None) -> Dict:
        """Generate realistic patient data based on medical statistics."""
        age = random.randint(*age_range)
        gender = random.choice(["male", "female"])
        
        # Base patient data
        patient_data = {
            "id": random.randint(10000, 99999),
            "age": age,
            "gender": gender,
            "height": random.gauss(170 if gender == "male" else 162, 10),
            "weight": random.gauss(80 if gender == "male" else 70, 15),
            "blood_pressure_systolic": random.gauss(120, 15),
            "blood_pressure_diastolic": random.gauss(80, 10),
            "heart_rate": random.gauss(70, 12),
            "created_at": datetime.now() - timedelta(days=random.randint(0, 365)),
            "medical_history": [],
            "medications": [],
            "allergies": [],
            "smoking_status": random.choice(["never", "former", "current"]),
            "diabetes": False,
            "hypertension": False
        }
        
        # Age-related conditions
        if age > 50:
            if random.random() < 0.3:
                patient_data["hypertension"] = True
                patient_data["medical_history"].append("hypertension")
                patient_data["medications"].extend(["lisinopril", "hydrochlorothiazide"])
                patient_data["blood_pressure_systolic"] += 20
                patient_data["blood_pressure_diastolic"] += 10
        
        if age > 60:
            if random.random() < 0.2:
                patient_data["diabetes"] = True
                patient_data["medical_history"].append("type 2 diabetes")
                patient_data["medications"].append("metformin")
        
        # Condition-specific modifications
        if condition == "cardiac":
            patient_data["medical_history"].extend([
                "coronary artery disease",
                "previous MI" if random.random() < 0.3 else None
            ])
            patient_data["medical_history"] = [h for h in patient_data["medical_history"] if h]
            patient_data["medications"].extend(["aspirin", "atorvastatin", "metoprolol"])
            patient_data["ejection_fraction"] = random.gauss(55, 10)
        
        elif condition == "arrhythmia":
            patient_data["medical_history"].append("atrial fibrillation")
            patient_data["medications"].extend(["warfarin", "diltiazem"])
            patient_data["inr"] = round(random.uniform(2.0, 3.0), 1)
        
        # Common allergies
        if random.random() < 0.1:
            patient_data["allergies"].append(random.choice(["penicillin", "sulfa", "aspirin"]))
        
        return patient_data

    @staticmethod
    def generate_lab_results(test_type: str = "basic", condition: Optional[str] = None) -> Dict[str, Any]:
        """Generate realistic lab results."""
        results = {}
        
        if test_type in ["basic", "comprehensive"]:
            # Basic metabolic panel
            results.update({
                "glucose": random.randint(70, 200),
                "sodium": random.randint(135, 145),
                "potassium": round(random.uniform(3.5, 5.0), 1),
                "chloride": random.randint(98, 107),
                "bun": random.randint(7, 25),
                "creatinine": round(random.uniform(0.6, 1.5), 1),
                "hemoglobin": round(random.uniform(12.0, 16.0), 1),
                "hematocrit": round(random.uniform(36.0, 48.0), 1),
                "platelets": random.randint(150, 450)
            })
        
        if test_type in ["cardiac", "comprehensive"]:
            # Cardiac markers
            results.update({
                "troponin_i": round(random.uniform(0.0, 0.1), 3),
                "ck_mb": round(random.uniform(0.0, 6.0), 1),
                "bnp": random.randint(0, 100),
                "ldl": random.randint(70, 200),
                "hdl": random.randint(30, 80),
                "total_cholesterol": random.randint(150, 300)
            })
        
        if test_type in ["inflammatory", "comprehensive"]:
            # Inflammatory markers
            results.update({
                "esr": random.randint(0, 30),
                "crp": round(random.uniform(0.0, 10.0), 1),
                "wbc": round(random.uniform(4.0, 11.0), 1)
            })
        
        # Condition-specific modifications
        if condition == "myocardial_infarction":
            results["troponin_i"] = round(random.uniform(0.5, 50.0), 2)
            results["ck_mb"] = round(random.uniform(10.0, 100.0), 1)
        
        elif condition == "heart_failure":
            results["bnp"] = random.randint(400, 2000)
            results["creatinine"] = round(random.uniform(1.2, 3.0), 1)
        
        elif condition == "infection":
            results["wbc"] = round(random.uniform(12.0, 25.0), 1)
            results["crp"] = round(random.uniform(10.0, 200.0), 1)
        
        elif condition == "diabetes":
            results["glucose"] = random.randint(200, 400)
            results["hemoglobin_a1c"] = round(random.uniform(7.0, 12.0), 1)
        
        return results


class SmartDiagnosticMock:
    """Smart mock for generating realistic diagnostic scenarios."""
    
    @staticmethod
    def generate_diagnostic_scenario(complexity: str = "moderate") -> Dict[str, Any]:
        """Generate complete diagnostic scenario."""
        # Implementation would continue here...
        pass