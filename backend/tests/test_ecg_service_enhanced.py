"""
Módulo de dados mock para testes de ECG
Conversão do código JavaScript para Python
"""
import math
import random
from datetime import datetime
from typing import List, Dict, Any


def generate_mock_ecg_signal(samples: int) -> List[float]:
    """
    Gera sinal de ECG realístico com características fisiológicas
    
    Args:
        samples: Número de amostras do sinal
        
    Returns:
        Lista com valores do sinal ECG simulado
    """
    signal = []
    heart_rate = 72  # bpm
    sample_rate = 500  # Hz
    samples_per_beat = (60 / heart_rate) * sample_rate
    
    for i in range(samples):
        beat_position = (i % samples_per_beat) / samples_per_beat
        value = 0.0
        
        # Onda P (duração de 0.08s)
        if 0.1 <= beat_position <= 0.18:
            p_wave_position = (beat_position - 0.1) / 0.08
            value = 0.15 * math.sin(math.pi * p_wave_position)
            
        # Complexo QRS (duração de 0.08s)
        elif 0.25 <= beat_position <= 0.33:
            qrs_position = (beat_position - 0.25) / 0.08
            if qrs_position < 0.2:
                # Onda Q
                value = -0.1
            elif qrs_position < 0.6:
                # Onda R
                value = 1.5 * (1 - abs(qrs_position - 0.4) / 0.2)
            else:
                # Onda S
                value = -0.2
                
        # Onda T (duração de 0.16s)
        elif 0.4 <= beat_position <= 0.56:
            t_wave_position = (beat_position - 0.4) / 0.16
            value = 0.3 * math.sin(math.pi * t_wave_position)
        
        # Adiciona oscilação basal e ruído
        value += 0.05 * math.sin(2 * math.pi * 0.15 * i / 500)
        value += (random.random() - 0.5) * 0.02
        
        signal.append(value)
    
    return signal


# Dados mock do ECG
mock_ecg_data = {
    'id': '123',
    'patient_id': '456',
    'recorded_at': '2024-06-23T10:30:00Z',
    'duration': 10,  # segundos
    'sample_rate': 500,  # Hz
    'leads': {
        'I': generate_mock_ecg_signal(5000),
        'II': generate_mock_ecg_signal(5000),
        'III': generate_mock_ecg_signal(5000),
        'aVR': generate_mock_ecg_signal(5000),
        'aVL': generate_mock_ecg_signal(5000),
        'aVF': generate_mock_ecg_signal(5000),
        'V1': generate_mock_ecg_signal(5000),
        'V2': generate_mock_ecg_signal(5000),
        'V3': generate_mock_ecg_signal(5000),
        'V4': generate_mock_ecg_signal(5000),
        'V5': generate_mock_ecg_signal(5000),
        'V6': generate_mock_ecg_signal(5000),
    },
    'analysis': {
        'heart_rate': 72,
        'rhythm': 'Sinusal',
        'pr_interval': 160,
        'qrs_duration': 90,
        'qt_interval': 400,
        'qtc_bazett': 428,
        'axis': 45,
    },
    'annotations': [],
    'validated': False,
}

# Dados mock do paciente
mock_patient_data = {
    'id': '456',
    'first_name': 'João',
    'last_name': 'Silva',
    'date_of_birth': '1958-03-15',
    'gender': 'male',
    'medical_record_number': 'MRN123456',
    'demographics': {
        'age': 66,
        'height': 175,
        'weight': 78,
        'bmi': 25.5,
    },
    'vital_signs': {
        'blood_pressure': '130/85',
        'heart_rate': 72,
        'respiratory_rate': 16,
        'temperature': 36.5,
        'oxygen_saturation': 98,
    },
    'medical_history': [
        {'condition': 'Hipertensão', 'diagnosed_at': '2015-06-10'},
        {'condition': 'Diabetes Tipo 2', 'diagnosed_at': '2018-03-22'},
    ],
    'medications': [
        {'name': 'Losartana', 'dose': '50mg', 'frequency': '1x/dia'},
        {'name': 'Metformina', 'dose': '850mg', 'frequency': '2x/dia'},
        {'name': 'AAS', 'dose': '100mg', 'frequency': '1x/dia'},
    ],
    'allergies': ['Penicilina'],
}

# Resultados mock de análise
mock_analysis_results = {
    'normal': {
        'id': '001',
        'diagnosis': 'Ritmo Sinusal Normal',
        'confidence': 0.95,
        'urgency': 'low',
        'findings': [
            'Ritmo sinusal regular',
            'Frequência cardíaca normal',
            'Intervalos dentro dos limites normais',
            'Sem alterações ST-T significativas',
        ],
        'recommendations': [
            'Manter acompanhamento de rotina',
            'Repetir ECG em 1 ano',
        ],
    },
    'atrial_fibrillation': {
        'id': '002',
        'diagnosis': 'Fibrilação Atrial',
        'confidence': 0.92,
        'urgency': 'high',
        'findings': [
            'Ritmo irregularmente irregular',
            'Ausência de ondas P',
            'Frequência ventricular variável',
            'QRS estreito',
        ],
        'recommendations': [
            'Avaliar necessidade de anticoagulação',
            'Considerar controle de frequência',
            'Encaminhar para cardiologista',
            'Calcular escore CHA2DS2-VASc',
        ],
        'risk_scores': {
            'cha2ds2_vasc': 3,
            'hasbled': 1,
        },
    },
    'stemi': {
        'id': '003',
        'diagnosis': 'Infarto Agudo do Miocárdio com Supra de ST',
        'confidence': 0.98,
        'urgency': 'critical',
        'findings': [
            'Elevação do segmento ST em DII, DIII, aVF',
            'Depressão recíproca em DI, aVL',
            'Ondas Q patológicas em desenvolvimento',
            'Localização: parede inferior',
        ],
        'recommendations': [
            'ATIVAR PROTOCOLO DE IAM',
            'Tempo porta-balão < 90 minutos',
            'Administrar AAS 300mg',
            'Preparar para cateterismo',
        ],
        'critical_alerts': [
            'EMERGÊNCIA MÉDICA',
            'Ativar hemodinâmica',
            'Notificar cardiologista de plantão',
        ],
    },
}

# Dados mock de validação
mock_validation_data = {
    'pending_validation': {
        'id': '123',
        'analysis_id': '123',
        'status': 'pending',
        'requested_at': '2024-06-23T10:35:00Z',
        'requested_by': 'Sistema IA',
        'priority': 'high',
        'reason': 'Baixa confiança do modelo ML',
    },
    'completed_validation': {
        'id': '124',
        'analysis_id': '124',
        'status': 'completed',
        'requested_at': '2024-06-23T09:00:00Z',
        'validated_at': '2024-06-23T09:15:00Z',
        'validated_by': {
            'id': '789',
            'name': 'Dr. Carlos Mendes',
            'specialty': 'Cardiologia',
            'crm': '12345-SP',
        },
        'original_diagnosis': 'Fibrilação Atrial',
        'validated_diagnosis': 'Flutter Atrial',
        'notes': 'Padrão de serra dentada visível em DII, DIII, aVF. Condução AV variável.',
        'agreement': False,
    },
}

# Dados mock de notificações
mock_notifications = [
    {
        'id': 'notif-001',
        'type': 'critical_ecg',
        'title': 'ECG Crítico Detectado',
        'message': 'IAMCSST detectado no paciente João Silva (MRN123456)',
        'timestamp': '2024-06-23T10:32:00Z',
        'read': False,
        'priority': 'critical',
        'action_required': True,
        'actions': [
            {'label': 'Visualizar ECG', 'action': 'view_ecg', 'data': {'analysis_id': '123'}},
            {'label': 'Ativar Protocolo', 'action': 'activate_protocol', 'data': {'protocol': 'stemi'}},
        ],
    },
    {
        'id': 'notif-002',
        'type': 'validation_request',
        'title': 'Validação Solicitada',
        'message': 'ECG requer validação médica - Paciente Maria Santos',
        'timestamp': '2024-06-23T09:45:00Z',
        'read': True,
        'priority': 'high',
        'action_required': True,
        'actions': [
            {'label': 'Revisar', 'action': 'review_ecg', 'data': {'analysis_id': '456'}},
        ],
    },
]

# Dados mock de estatísticas
mock_statistics = {
    'dashboard': {
        'total_analyses': 1543,
        'analyses_today': 48,
        'pending_validations': 7,
        'critical_findings': 3,
        'average_processing_time': 2.3,  # segundos
        'system_uptime': 99.8,  # porcentagem
    },
    'performance_metrics': {
        'model_accuracy': 0.96,
        'sensitivity': 0.98,
        'specificity': 0.95,
        'f1_score': 0.97,
        'average_confidence': 0.91,
    },
    'diagnose_distribution': {
        'Normal': 65,
        'Fibrilação Atrial': 15,
        'Flutter Atrial': 5,
        'Taquicardia Sinusal': 8,
        'Bradicardia Sinusal': 4,
        'Outros': 3,
    },
}

# Dados mock do usuário
mock_user_data = {
    'current_user': {
        'id': '999',
        'email': 'dr.silva@hospital.com',
        'name': 'Dr. Ana Silva',
        'role': 'physician',
        'specialty': 'Cardiologia',
        'permissions': [
            'view_ecg',
            'validate_diagnosis',
            'export_reports',
            'view_patient_history',
        ],
        'preferences': {
            'default_view': '12-lead',
            'grid_enabled': True,
            'measurement_units': 'metric',
            'notifications': {
                'critical': True,
                'validation_requests': True,
                'system_updates': False,
            },
        },
    },
}

# Mensagens mock WebSocket
mock_websocket_messages = {
    'ecg_update': {
        'type': 'ecg_update',
        'data': {
            'analysis_id': '123',
            'timestamp': datetime.now().timestamp() * 1000,
            'lead': 'II',
            'values': generate_mock_ecg_signal(50),  # 100ms de dados a 500Hz
        },
    },
    'analysis_complete': {
        'type': 'analysis_complete',
        'data': {
            'analysis_id': '123',
            'diagnosis': 'Ritmo Sinusal Normal',
            'confidence': 0.94,
            'processing_time': 2.1,
        },
    },
    'critical_alert': {
        'type': 'critical_alert',
        'data': {
            'analysis_id': '789',
            'patient_id': '111',
            'diagnosis': 'IAMCSST',
            'urgency': 'critical',
            'message': 'Atenção imediata necessária',
        },
    },
}


def generate_mock_ecg_file(format: str = 'xml') -> bytes:
    """
    Gera arquivo ECG mock em diferentes formatos
    
    Args:
        format: Formato do arquivo ('xml', 'pdf', 'dicom')
        
    Returns:
        Conteúdo do arquivo em bytes
    """
    if format == 'xml':
        content = f"""<?xml version="1.0"?>
<RestingECG>
  <PatientDemographics>
    <PatientID>123456</PatientID>
  </PatientDemographics>
  <Waveforms>
    <WaveformData lead="I">{','.join(map(str, generate_mock_ecg_signal(100)))}</WaveformData>
  </Waveforms>
</RestingECG>"""
        return content.encode('utf-8')
    
    elif format == 'pdf':
        # Em um caso real, você usaria uma biblioteca como reportlab
        return b'Mock PDF content'
    
    elif format == 'dicom':
        # Em um caso real, você usaria pydicom
        return b'Mock DICOM content'
    
    else:
        raise ValueError(f"Formato não suportado: {format}")


# Exemplo de uso em testes
if __name__ == "__main__":
    # Teste da geração de sinal ECG
    signal = generate_mock_ecg_signal(500)
    print(f"Sinal ECG gerado com {len(signal)} amostras")
    print(f"Valor mínimo: {min(signal):.3f}, Valor máximo: {max(signal):.3f}")
    
    # Teste da geração de arquivo
    xml_file = generate_mock_ecg_file('xml')
    print(f"\nArquivo XML gerado com {len(xml_file)} bytes")
    
    # Exemplo de acesso aos dados mock
    print(f"\nPaciente: {mock_patient_data['first_name']} {mock_patient_data['last_name']}")
    print(f"Frequência cardíaca: {mock_ecg_data['analysis']['heart_rate']} bpm")
    print(f"Ritmo: {mock_ecg_data['analysis']['rhythm']}")