# Criar mock do TensorFlow para testes
import os
mock_tf_content = '''
"""Mock TensorFlow for testing"""

class MockModel:
    def predict(self, data):
        import numpy as np
        return np.random.random((len(data), 1))
    
    def save(self, path):
        pass
    
    def load_weights(self, path):
        pass

def keras():
    return type('keras', (), {
        'models': type('models', (), {
            'Model': MockModel,
            'load_model': lambda x: MockModel()
        })
    })()

def constant(value):
    import numpy as np
    return np.array(value)

# Simular módulos principais
models = keras().models
'''

# Criar diretório para mock
os.makedirs('tests/mocks', exist_ok=True)

with open('tests/mocks/tensorflow_mock.py', 'w') as f:
    f.write(mock_tf_content)

print("✅ Mock do TensorFlow criado")

