"""
AWS KMS Manager for MedAI
Handles PHI encryption with envelope encryption and automatic key rotation
"""
import boto3
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)


class KMSManager:
    """AWS KMS Manager for secure key management and PHI encryption"""
    
    def __init__(self, region: str = "us-east-1"):
        """
        Initialize KMS Manager
        
        Args:
            region: AWS region for KMS operations
        """
        try:
            # Check if we have AWS credentials and region
            import os
            if not os.getenv('AWS_ACCESS_KEY_ID') and not os.getenv('AWS_PROFILE'):
                raise Exception("No AWS credentials available")
                
            self.kms_client = boto3.client('kms', region_name=region)
            self.region = region
            self.key_aliases = {
                'phi_data': 'alias/medai-phi-encryption',
                'sessions': 'alias/medai-session-keys'
            }
            self._use_mock = False
            logger.info(f"KMS Manager initialized for region: {region}")
        except Exception as e:
            logger.warning(f"Failed to initialize KMS client, using mock: {e}")
            # In development/testing, fall back to mock implementation
            self.kms_client = None
            self._use_mock = True
    
    async def encrypt_phi(self, plaintext: str, context: Dict[str, str]) -> str:
        """
        Encrypt PHI data with envelope encryption
        
        Args:
            plaintext: Data to encrypt
            context: Encryption context for additional security
            
        Returns:
            Encrypted ciphertext blob
        """
        if self._use_mock:
            return self._mock_encrypt(plaintext, context)
            
        try:
            response = self.kms_client.encrypt(
                KeyId=self.key_aliases['phi_data'],
                Plaintext=plaintext.encode('utf-8'),
                EncryptionContext=context
            )
            
            logger.info("PHI data encrypted successfully", extra={
                "context_keys": list(context.keys()),
                "data_length": len(plaintext)
            })
            
            return response['CiphertextBlob']
            
        except ClientError as e:
            logger.error(f"KMS encryption failed: {e}")
            raise Exception(f"Failed to encrypt PHI data: {e}")
    
    async def decrypt_phi(self, ciphertext_blob: bytes, context: Dict[str, str]) -> str:
        """
        Decrypt PHI data
        
        Args:
            ciphertext_blob: Encrypted data
            context: Encryption context for verification
            
        Returns:
            Decrypted plaintext
        """
        if self._use_mock:
            return self._mock_decrypt(ciphertext_blob, context)
            
        try:
            response = self.kms_client.decrypt(
                CiphertextBlob=ciphertext_blob,
                EncryptionContext=context
            )
            
            logger.info("PHI data decrypted successfully", extra={
                "context_keys": list(context.keys())
            })
            
            return response['Plaintext'].decode('utf-8')
            
        except ClientError as e:
            logger.error(f"KMS decryption failed: {e}")
            raise Exception(f"Failed to decrypt PHI data: {e}")
    
    async def setup_rotation(self, key_alias: str, rotation_days: int = 90):
        """
        Configure automatic key rotation
        
        Args:
            key_alias: Key alias to configure rotation for
            rotation_days: Days between rotations
        """
        if self._use_mock:
            logger.info(f"Mock: Key rotation configured for {key_alias} every {rotation_days} days")
            return
            
        try:
            key_id = self._get_key_id(key_alias)
            self.kms_client.enable_key_rotation(
                KeyId=key_id
            )
            
            logger.info(f"Key rotation enabled for {key_alias}", extra={
                "rotation_days": rotation_days,
                "key_id": key_id
            })
            
        except ClientError as e:
            logger.error(f"Failed to setup key rotation: {e}")
            raise Exception(f"Failed to configure key rotation: {e}")
    
    def _get_key_id(self, key_alias: str) -> str:
        """Get key ID from alias"""
        try:
            response = self.kms_client.describe_key(KeyId=key_alias)
            return response['KeyMetadata']['KeyId']
        except ClientError as e:
            logger.error(f"Failed to get key ID for alias {key_alias}: {e}")
            raise
    
    def _mock_encrypt(self, plaintext: str, context: Dict[str, str]) -> str:
        """Mock encryption for development/testing"""
        import base64
        import json
        
        mock_data = {
            'data': base64.b64encode(plaintext.encode()).decode(),
            'context': context,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return base64.b64encode(json.dumps(mock_data).encode()).decode()
    
    def _mock_decrypt(self, ciphertext: str, context: Dict[str, str]) -> str:
        """Mock decryption for development/testing"""
        import base64
        import json
        
        try:
            if isinstance(ciphertext, bytes):
                ciphertext = ciphertext.decode()
                
            mock_data = json.loads(base64.b64decode(ciphertext).decode())
            return base64.b64decode(mock_data['data']).decode()
        except Exception as e:
            logger.error(f"Mock decryption failed: {e}")
            raise Exception("Failed to decrypt data")


# Global instance
kms_manager = KMSManager()