"""
Smart Mocks for Medical Data Testing
"""

import numpy as np
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json


class SmartECGMock:
    """Smart mock for generating realistic ECG data."""
    
    @staticmethod
    def generate_normal_ecg(duration_seconds: int = 10, sample_rate: int = 500) -> np.ndarray:
        """Generate normal ECG with physiological characteristics."""
        samples = duration_seconds * sample_rate
        leads = 12
        
        # Heart rate between 60-100 bpm (normal range)
        heart_rate = random.randint(60, 100)
        rr_interval = 60.0 / heart_rate
        
        ecg_data = np.zeros((samples, leads))
        t = np.linspace(0, duration_seconds, samples)
        
        # Lead-specific amplitude factors
        lead_amplitudes = {
            0: 0.5,   # Lead I
            1: 1.0,   # Lead II (reference)
            2: 0.5,   # Lead III
            3: -0.5,  # aVR
            4: 0.3,   # aVL
            5: 0.8,   # aVF
            6: 0.2,   # V1
            7: 0.4,   # V2
            8: 0.8,   # V3
            9: 1.2,   # V4
            10: 1.0,  # V5
            11: 0.8   # V6
        }
        
        for lead in range(leads):
            signal = np.zeros(samples)
            amplitude_factor = lead_amplitudes[lead]
            
            # Generate QRS complexes
            current_time = 0
            while current_time < duration_seconds:
                qrs_sample = int(current_time * sample_rate)
                
                if qrs_sample < samples - 100:
                    # P wave (if not aVR)
                    if lead != 3:  # aVR typically has inverted P
                        p_start = qrs_sample - int(0.16 * sample_rate)  # 160ms before QRS
                        p_duration = int(0.08 * sample_rate)  # 80ms duration
                        if p_start >= 0:
                            p_wave = 0.1 * amplitude_factor * np.exp(
                                -((np.arange(p_duration) - p_duration/2) ** 2) / (p_duration/6) ** 2
                            )
                            signal[p_start:p_start + p_duration] += p_wave
                    
                    # QRS complex
                    qrs_duration = int(0.08 * sample_rate)  # 80ms
                    qrs_start = max(0, qrs_sample - qrs_duration // 2)
                    qrs_end = min(samples, qrs_sample + qrs_duration // 2)
                    
                    qrs_wave = amplitude_factor * np.exp(
                        -((np.arange(qrs_end - qrs_start) - qrs_duration // 2) ** 2) / (qrs_duration / 8) ** 2
                    )
                    signal[qrs_start:qrs_end] += qrs_wave
                    
                    # T wave
                    t_start = qrs_sample + int(0.32 * sample_rate)  # 320ms after QRS
                    t_duration = int(0.16 * sample_rate)  # 160ms duration
                    if t_start + t_duration < samples:
                        t_wave = 0.3 * amplitude_factor * np.exp(
                            -((np.arange(t_duration) - t_duration/2) ** 2) / (t_duration/4) ** 2
                        )
                        signal[t_start:t_start + t_duration] += t_wave
                
                current_time += rr_interval
            
            # Add physiological noise
            noise = np.random.normal(0, 0.02, samples)
            ecg_data[:, lead] = signal + noise
        
        return ecg_data.astype(np.float32)
    
    @staticmethod
    def generate_arrhythmia_ecg(arrhythmia_type: str, duration_seconds: int = 10, sample_rate: int = 500) -> np.ndarray:
        """Generate ECG with specific arrhythmia patterns."""
        samples = duration_seconds * sample_rate
        leads = 12
        ecg_data = np.zeros((samples, leads))
        
        if arrhythmia_type == "atrial_fibrillation":
            # Irregular RR intervals
            rr_intervals = np.random.normal(0.8, 0.3, 20)
            rr_intervals = np.clip(rr_intervals, 0.3, 1.5)
            
            # Add fibrillation waves
            fib_freq = random.uniform(300, 600)  # Hz
            t = np.linspace(0, duration_seconds, samples)
            
            for lead in range(leads):
                signal = np.zeros(samples)
                
                # Irregular QRS complexes
                current_time = 0
                for rr_interval in rr_intervals:
                    if current_time >= duration_seconds:
                        break
                    
                    qrs_sample = int(current_time * sample_rate)
                    if qrs_sample < samples - 50:
                        qrs_duration = int(0.08 * sample_rate)
                        qrs_start = max(0, qrs_sample - qrs_duration // 2)
                        qrs_end = min(samples, qrs_sample + qrs_duration // 2)
                        
                        amplitude = 0.8 + 0.4 * random.random()
                        qrs_wave = amplitude * np.exp(
                            -((np.arange(qrs_end - qrs_start) - qrs_duration // 2) ** 2) / (qrs_duration / 8) ** 2
                        )
                        signal[qrs_start:qrs_end] += qrs_wave
                    
                    current_time += rr_interval
                
                # Add fibrillation waves
                fib_amplitude = 0.05 + 0.05 * random.random()
                fib_signal = fib_amplitude * np.sin(2 * np.pi * fib_freq * t)
                
                noise = np.random.normal(0, 0.03, samples)
                ecg_data[:, lead] = signal + fib_signal + noise
        
        elif arrhythmia_type == "ventricular_tachycardia":
            # Fast, regular, wide QRS complexes
            heart_rate = random.randint(150, 250)
            rr_interval = 60.0 / heart_rate
            
            for lead in range(leads):
                signal = np.zeros(samples)
                current_time = 0
                
                while current_time < duration_seconds:
                    qrs_sample = int(current_time * sample_rate)
                    
                    if qrs_sample < samples - 100:
                        # Wide QRS (>120ms)
                        qrs_duration = int(0.15 * sample_rate)  # 150ms
                        qrs_start = max(0, qrs_sample - qrs_duration // 2)
                        qrs_end = min(samples, qrs_sample + qrs_duration // 2)
                        
                        # Bizarre morphology
                        amplitude = 1.5 + 0.5 * random.random()
                        qrs_wave = amplitude * np.sin(np.linspace(0, 2*np.pi, qrs_end - qrs_start))
                        signal[qrs_start:qrs_end] += qrs_wave
                    
                    current_time += rr_interval
                
                noise = np.random.normal(0, 0.05, samples)
                ecg_data[:, lead] = signal + noise
        
        elif arrhythmia_type == "bradycardia":
            # Slow heart rate
            heart_rate = random.randint(35, 50)
            rr_interval = 60.0 / heart_rate
            
            ecg_data = SmartECGMock.generate_normal_ecg(duration_seconds, sample_rate)
            # The normal generation with slow heart rate will create bradycardia
        
        return ecg_data.astype(np.float32)
    
    @staticmethod
    def generate_noisy_ecg(duration_seconds: int = 10, sample_rate: int = 500, noise_level: float = 0.5) -> np.ndarray:
        """Generate ECG with various types of noise and artifacts."""
        ecg_data = SmartECGMock.generate_normal_ecg(duration_seconds, sample_rate)
        samples = duration_seconds * sample_rate
        
        # Add different types of noise
        if noise_level > 0.3:
            # Baseline wander (0.5 Hz)
            t = np.linspace(0, duration_seconds, samples)
            baseline_wander = 0.3 * noise_level * np.sin(2 * np.pi * 0.5 * t)
            ecg_data += baseline_wander[:, np.newaxis]
        
        if noise_level > 0.4:
            # Power line interference (50/60 Hz)
            power_freq = random.choice([50, 60])
            t = np.linspace(0, duration_seconds, samples)
            power_noise = 0.1 * noise_level * np.sin(2 * np.pi * power_freq * t)
            ecg_data += power_noise[:, np.newaxis]
        
        if noise_level > 0.5:
            # Muscle artifacts (high frequency)
            muscle_noise = np.random.normal(0, 0.2 * noise_level, ecg_data.shape)
            ecg_data += muscle_noise
        
        # Random spikes (electrode artifacts)
        if noise_level > 0.6:
            num_spikes = int(noise_level * 10)
            for _ in range(num_spikes):
                spike_time = random.randint(0, samples - 1)
                spike_lead = random.randint(0, 11)
                spike_amplitude = random.uniform(-2, 2) * noise_level
                ecg_data[spike_time, spike_lead] += spike_amplitude
        
        return ecg_data.astype(np.float32)


class SmartPatientMock:
    """Smart mock for generating realistic patient data."""
    
    @staticmethod
    def generate_patient_data(age_range: tuple = (18, 90), condition: Optional[str] = None) -> Dict[str, Any]:
        """Generate realistic patient data."""
        age = random.randint(*age_range)
        gender = random.choice(["male", "female"])
        
        # Base patient data
        patient_data = {
            "age": age,
            "gender": gender,
            "height_cm": random.randint(150, 200) if gender == "male" else random.randint(145, 180),
            "weight_kg": random.randint(50, 120),
            "blood_type": random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]),
            "allergies": [],
            "medications": [],
            "medical_history": [],
            "family_history": [],
            "vital_signs": {
                "blood_pressure_systolic": random.randint(90, 180),
                "blood_pressure_diastolic": random.randint(60, 110),
                "heart_rate": random.randint(60, 100),
                "temperature": round(random.uniform(97.0, 99.5), 1),
                "oxygen_saturation": random.randint(95, 100)
            }
        }
        
        # Age-related conditions
        if age > 65:
            patient_data["medical_history"].extend(
                random.sample(["hypertension", "diabetes", "arthritis", "osteoporosis"], 
                             random.randint(0, 2))
            )
        
        if age > 50:
            patient_data["medications"].extend(
                random.sample(["lisinopril", "metformin", "atorvastatin", "aspirin"], 
                             random.randint(0, 2))
            )
        
        # Condition-specific modifications
        if condition == "cardiac":
            patient_data["medical_history"].extend(["hypertension", "hyperlipidemia"])
            patient_data["medications"].extend(["beta_blocker", "ace_inhibitor"])
            patient_data["family_history"].append("coronary_artery_disease")
            patient_data["vital_signs"]["heart_rate"] = random.randint(80, 120)
        
        elif condition == "diabetic":
            patient_data["medical_history"].append("diabetes_type_2")
            patient_data["medications"].extend(["metformin", "insulin"])
            patient_data["vital_signs"]["blood_pressure_systolic"] = random.randint(130, 160)
        
        elif condition == "respiratory":
            patient_data["medical_history"].extend(["asthma", "copd"])
            patient_data["medications"].extend(["albuterol", "prednisone"])
            patient_data["vital_signs"]["oxygen_saturation"] = random.randint(88, 96)
        
        return patient_data
    
    @staticmethod
    def generate_symptoms(severity: str = "moderate") -> Dict[str, Any]:
        """Generate realistic symptom data."""
        severity_map = {
            "mild": (1, 4),
            "moderate": (4, 7),
            "severe": (7, 10)
        }
        
        severity_range = severity_map.get(severity, (4, 7))
        
        common_symptoms = [
            "chest_pain", "shortness_of_breath", "fatigue", "dizziness",
            "nausea", "headache", "abdominal_pain", "back_pain"
        ]
        
        num_symptoms = random.randint(1, 4)
        selected_symptoms = random.sample(common_symptoms, num_symptoms)
        
        symptoms = {}
        for symptom in selected_symptoms:
            symptoms[symptom] = {
                "severity": random.randint(*severity_range),
                "duration": random.choice(["minutes", "hours", "days", "weeks"]),
                "onset": random.choice(["sudden", "gradual", "intermittent"])
            }
            
            # Symptom-specific details
            if symptom == "chest_pain":
                symptoms[symptom].update({
                    "type": random.choice(["crushing", "stabbing", "burning", "pressure"]),
                    "radiation": random.choice(["none", "left_arm", "jaw", "back"])
                })
            elif symptom == "shortness_of_breath":
                symptoms[symptom].update({
                    "triggers": random.choice(["exertion", "rest", "lying_down"]),
                    "associated_symptoms": random.choice(["none", "wheezing", "cough"])
                })
        
        return symptoms


class SmartLabMock:
    """Smart mock for generating realistic laboratory results."""
    
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
        scenarios = {
            "simple": {
                "primary_diagnosis": "upper_respiratory_infection",
                "confidence": random.uniform(0.8, 0.95),
                "differential_diagnoses": ["viral_syndrome", "allergic_rhinitis"]
            },
            "moderate": {
                "primary_diagnosis": "acute_coronary_syndrome",
                "confidence": random.uniform(0.6, 0.8),
                "differential_diagnoses": ["unstable_angina", "myocardial_infarction", "gastroesophageal_reflux"]
            },
            "complex": {
                "primary_diagnosis": "systemic_lupus_erythematosus",
                "confidence": random.uniform(0.4, 0.7),
                "differential_diagnoses": ["rheumatoid_arthritis", "fibromyalgia", "multiple_sclerosis", "drug_reaction"]
            }
        }
        
        base_scenario = scenarios.get(complexity, scenarios["moderate"])
        
        scenario = {
            "patient_data": SmartPatientMock.generate_patient_data(),
            "symptoms": SmartPatientMock.generate_symptoms(),
            "lab_results": SmartLabMock.generate_lab_results(),
            "ecg_data": SmartECGMock.generate_normal_ecg(),
            **base_scenario
        }
        
        return scenario
    
    @staticmethod
    def generate_treatment_plan(diagnosis: str) -> Dict[str, Any]:
        """Generate realistic treatment plan."""
        treatment_plans = {
            "acute_myocardial_infarction": {
                "immediate_actions": ["oxygen", "aspirin", "nitroglycerin", "morphine"],
                "medications": ["clopidogrel", "atorvastatin", "metoprolol"],
                "procedures": ["cardiac_catheterization", "pci"],
                "monitoring": ["continuous_ecg", "cardiac_enzymes", "vital_signs"],
                "follow_up": ["cardiology_consult", "echo_in_24h"]
            },
            "pneumonia": {
                "immediate_actions": ["oxygen", "iv_fluids"],
                "medications": ["azithromycin", "ceftriaxone"],
                "procedures": ["chest_xray", "blood_cultures"],
                "monitoring": ["oxygen_saturation", "temperature", "respiratory_rate"],
                "follow_up": ["repeat_xray_in_48h", "primary_care_in_1_week"]
            }
        }
        
        return treatment_plans.get(diagnosis, {
            "immediate_actions": ["supportive_care"],
            "medications": ["as_needed"],
            "procedures": ["further_evaluation"],
            "monitoring": ["clinical_assessment"],
            "follow_up": ["primary_care"]
        })

