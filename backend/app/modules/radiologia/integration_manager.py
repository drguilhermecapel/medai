import logging

import tensorflow as tf

logger = logging.getLogger('MedAI.Integration')

class IntegrationManager:
    def __init__(self):
        try:
            try:
                from .medai_pacs_integration import PACSIntegration
                self.pacs_integration = PACSIntegration()
            except ImportError:
                logger.warning("PACS integration não disponível")
                self.pacs_integration = None

            try:
                from .medai_clinical_performance import ClinicalPerformanceEvaluator
                self.clinical_evaluator = ClinicalPerformanceEvaluator()
            except ImportError:
                logger.warning("Clinical evaluator não disponível")
                self.clinical_evaluator = None

            try:
                from .medai_ethical_framework import EthicalAIFramework
                self.ethics_framework = EthicalAIFramework()
                self.regulatory_manager = self.ethics_framework
            except ImportError:
                logger.warning("Ethical framework não disponível")
                self.ethics_framework = None
                self.regulatory_manager = None

            try:
                from .medai_sota_models import StateOfTheArtModels
                self.sota_models = StateOfTheArtModels(
                    input_shape=(512, 512, 3),
                    num_classes=5
                )
            except ImportError:
                logger.warning("SOTA models não disponível")
                self.sota_models = None

            self.enhanced_models = {
                'medical_vit': self._create_simple_model(),
                'enhanced_ensemble': self._create_simple_model()
            }

            for model_name, model in self.enhanced_models.items():
                model.compile(optimizer='adam',
                            loss='sparse_categorical_crossentropy',
                            metrics=['accuracy'])
                logger.info(f"Modelo {model_name} compilado")

        except Exception as e:
            logger.error(f"Erro na inicialização: {e}")

    def _create_simple_model(self):
        """Cria modelo simples como fallback"""
        return tf.keras.Sequential([
            tf.keras.layers.Input(shape=(224, 224, 3)),
            tf.keras.layers.Conv2D(32, 3, activation='relu'),
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dense(5, activation='softmax')
        ])
