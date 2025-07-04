"""
Mock completo do TensorFlow para testes
"""
import numpy as np
from typing import Any, List, Optional, Union

class MockTensor:
    """Mock Tensor class"""
    def __init__(self, data):
        self.data = np.array(data) if not isinstance(data, np.ndarray) else data
        self.shape = self.data.shape
        self.dtype = self.data.dtype
    
    def numpy(self):
        return self.data
    
    def __array__(self):
        return self.data

class MockModel:
    """Mock Model class"""
    def __init__(self, *args, **kwargs):
        self.weights = []
        self.layers = []
        self.compiled = False
    
    def predict(self, x, **kwargs):
        # Simular predição retornando valores aleatórios
        if hasattr(x, 'shape'):
            batch_size = x.shape[0] if len(x.shape) > 0 else 1
        else:
            batch_size = len(x) if hasattr(x, '__len__') else 1
        
        # Retornar probabilidades mock para classificação
        return np.random.random((batch_size, 5))  # 5 classes
    
    def fit(self, x, y, **kwargs):
        return type('History', (), {'history': {'loss': [0.5, 0.3, 0.1]}})()
    
    def evaluate(self, x, y, **kwargs):
        return [0.1, 0.95]  # loss, accuracy
    
    def save(self, filepath):
        print(f"Mock: Model saved to {filepath}")
    
    def load_weights(self, filepath):
        print(f"Mock: Weights loaded from {filepath}")
    
    def compile(self, **kwargs):
        self.compiled = True
        print("Mock: Model compiled")
    
    def summary(self):
        print("Mock Model Summary: 3 layers, 1M parameters")

class MockOptimizer:
    def __init__(self, learning_rate=0.001):
        self.learning_rate = learning_rate

class MockLoss:
    def __init__(self, *args, **kwargs):
        pass

class MockMetric:
    def __init__(self, *args, **kwargs):
        pass

# Mock keras module
class MockKeras:
    class models:
        Model = MockModel
        Sequential = MockModel
        
        @staticmethod
        def load_model(filepath):
            print(f"Mock: Loading model from {filepath}")
            return MockModel()
    
    class layers:
        @staticmethod
        def Dense(units, activation=None, **kwargs):
            return type('MockLayer', (), {'units': units, 'activation': activation})
        
        @staticmethod
        def Input(shape=None, **kwargs):
            return type('MockInput', (), {'shape': shape})
        
        @staticmethod
        def Dropout(rate, **kwargs):
            return type('MockDropout', (), {'rate': rate})
    
    class optimizers:
        Adam = MockOptimizer
        SGD = MockOptimizer
    
    class losses:
        categorical_crossentropy = MockLoss
        binary_crossentropy = MockLoss
        mse = MockLoss
    
    class metrics:
        accuracy = MockMetric
        precision = MockMetric
        recall = MockMetric

# Mock TensorFlow main module
def constant(value, dtype=None, shape=None, name=None):
    """Mock tf.constant"""
    return MockTensor(value)

def zeros(shape, dtype=None, name=None):
    """Mock tf.zeros"""
    return MockTensor(np.zeros(shape))

def ones(shape, dtype=None, name=None):
    """Mock tf.ones"""
    return MockTensor(np.ones(shape))

def convert_to_tensor(value, dtype=None, name=None):
    """Mock tf.convert_to_tensor"""
    return MockTensor(value)

# Configurar keras como atributo
keras = MockKeras()

# Mock common functions
def function(func):
    """Mock tf.function decorator"""
    return func

class dtypes:
    float32 = np.float32
    float64 = np.float64
    int32 = np.int32
    int64 = np.int64

class config:
    class experimental:
        @staticmethod
        def set_memory_growth(device, enable):
            print(f"Mock: Memory growth set to {enable} for {device}")

# Versão
__version__ = "2.13.0"
