"""
Medical-specific neural network architectures optimized for radiological AI
Based on technical analysis recommendations for medical imaging
"""

import logging
from typing import Optional, Tuple, Dict, Any

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

logger = logging.getLogger(__name__)


class MedicalFocalLoss(nn.Module):
    """Focal loss for addressing class imbalance in medical imaging"""
    
    def __init__(self, alpha: Optional[torch.Tensor] = None, gamma: float = 2.0, reduction: str = 'mean'):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
        
    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = (1 - pt) ** self.gamma * ce_loss
        
        if self.alpha is not None:
            alpha_t = self.alpha[targets]
            focal_loss = alpha_t * focal_loss
            
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss


class DiceLoss(nn.Module):
    """Dice loss for segmentation tasks"""
    
    def __init__(self, smooth: float = 1.0):
        super().__init__()
        self.smooth = smooth
        
    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        inputs = torch.sigmoid(inputs)
        
        inputs_flat = inputs.view(-1)
        targets_flat = targets.view(-1)
        
        intersection = (inputs_flat * targets_flat).sum()
        dice = (2. * intersection + self.smooth) / (inputs_flat.sum() + targets_flat.sum() + self.smooth)
        
        return 1 - dice


class CombinedMedicalLoss(nn.Module):
    """Combined loss function for medical imaging"""
    
    def __init__(self, focal_weight: float = 0.7, dice_weight: float = 0.3, 
                 class_weights: Optional[torch.Tensor] = None):
        super().__init__()
        self.focal_weight = focal_weight
        self.dice_weight = dice_weight
        self.focal_loss = MedicalFocalLoss(alpha=class_weights)
        self.dice_loss = DiceLoss()
        
    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        focal = self.focal_loss(inputs, targets)
        dice = self.dice_loss(inputs, targets)
        return self.focal_weight * focal + self.dice_weight * dice


class MedicalResNet50(nn.Module):
    """Medical imaging-specific ResNet50 with adaptations"""
    
    def __init__(self, num_classes: int, num_channels: int = 1, dropout_rate: float = 0.5):
        super().__init__()
        
        import torchvision.models as models
        self.backbone = models.resnet50(pretrained=True)
        
        self.backbone.conv1 = nn.Conv2d(
            num_channels, 64, kernel_size=7, stride=2, padding=3, bias=False
        )
        
        with torch.no_grad():
            if num_channels == 1:
                pretrained_weight = self.backbone.conv1.weight.data
                self.backbone.conv1.weight.data = pretrained_weight.mean(dim=1, keepdim=True)
        
        self.backbone.fc = nn.Identity()
        
        self.channel_attention = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(2048, 128, 1),
            nn.ReLU(),
            nn.Conv2d(128, 2048, 1),
            nn.Sigmoid()
        )
        
        self.classifier = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(2048, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(dropout_rate * 0.6),
            nn.Linear(512, num_classes)
        )
        
        self.uncertainty_head = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(2048, 256),
            nn.ReLU(),
            nn.Dropout(dropout_rate * 0.5),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x: torch.Tensor, return_uncertainty: bool = False) -> torch.Tensor:
        features = self.backbone(x)
        
        attention = self.channel_attention(features)
        features = features * attention
        
        features = F.adaptive_avg_pool2d(features, (1, 1))
        features = features.view(features.size(0), -1)
        
        logits = self.classifier(features)
        
        if return_uncertainty:
            uncertainty = self.uncertainty_head(features)
            return logits, uncertainty
        
        return logits


class MedicalVisionTransformer(nn.Module):
    """Vision Transformer adapted for medical imaging"""
    
    def __init__(self, img_size: int = 224, patch_size: int = 16, num_classes: int = 1000,
                 embed_dim: int = 768, depth: int = 12, num_heads: int = 12,
                 mlp_ratio: float = 4.0, dropout_rate: float = 0.1):
        super().__init__()
        
        self.img_size = img_size
        self.patch_size = patch_size
        self.num_patches = (img_size // patch_size) ** 2
        
        self.patch_embed = nn.Conv2d(1, embed_dim, kernel_size=patch_size, stride=patch_size)
        
        self.pos_embed = nn.Parameter(torch.zeros(1, self.num_patches + 1, embed_dim))
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        
        self.blocks = nn.ModuleList([
            TransformerBlock(embed_dim, num_heads, mlp_ratio, dropout_rate)
            for _ in range(depth)
        ])
        
        self.norm = nn.LayerNorm(embed_dim)
        self.head = nn.Linear(embed_dim, num_classes)
        
        self.attention_pool = nn.MultiheadAttention(embed_dim, num_heads, dropout=dropout_rate)
        
        self._init_weights()
        
    def _init_weights(self):
        """Initialize weights with medical imaging considerations"""
        nn.init.trunc_normal_(self.pos_embed, std=0.02)
        nn.init.trunc_normal_(self.cls_token, std=0.02)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B = x.shape[0]
        
        x = self.patch_embed(x)  # (B, embed_dim, H/P, W/P)
        x = x.flatten(2).transpose(1, 2)  # (B, num_patches, embed_dim)
        
        cls_tokens = self.cls_token.expand(B, -1, -1)
        x = torch.cat((cls_tokens, x), dim=1)
        
        x = x + self.pos_embed
        
        for block in self.blocks:
            x = block(x)
        
        x = self.norm(x)
        
        return self.head(x[:, 0])


class TransformerBlock(nn.Module):
    """Transformer block with medical-specific modifications"""
    
    def __init__(self, embed_dim: int, num_heads: int, mlp_ratio: float = 4.0, dropout_rate: float = 0.1):
        super().__init__()
        
        self.norm1 = nn.LayerNorm(embed_dim)
        self.attn = nn.MultiheadAttention(embed_dim, num_heads, dropout=dropout_rate)
        
        self.norm2 = nn.LayerNorm(embed_dim)
        mlp_hidden_dim = int(embed_dim * mlp_ratio)
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim, mlp_hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout_rate),
            nn.Linear(mlp_hidden_dim, embed_dim),
            nn.Dropout(dropout_rate)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x_norm = self.norm1(x)
        attn_out, _ = self.attn(x_norm, x_norm, x_norm)
        x = x + attn_out
        
        x = x + self.mlp(self.norm2(x))
        
        return x


class MedicalEnsembleModel(nn.Module):
    """Ensemble of medical imaging models for robust predictions"""
    
    def __init__(self, models: list[nn.Module], weights: Optional[list[float]] = None):
        super().__init__()
        self.models = nn.ModuleList(models)
        
        if weights is None:
            weights = [1.0 / len(models)] * len(models)
        self.weights = torch.tensor(weights)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        outputs = []
        
        for model in self.models:
            with torch.no_grad():
                output = model(x)
                outputs.append(F.softmax(output, dim=1))
        
        ensemble_output = torch.zeros_like(outputs[0])
        for i, output in enumerate(outputs):
            ensemble_output += self.weights[i] * output
            
        return torch.log(ensemble_output + 1e-8)  # Convert back to logits


class UncertaintyQuantifier:
    """Monte Carlo Dropout for uncertainty quantification"""
    
    def __init__(self, model: nn.Module, num_samples: int = 100):
        self.model = model
        self.num_samples = num_samples
        
    def predict_with_uncertainty(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Predict with uncertainty estimation using Monte Carlo Dropout
        
        Returns:
            Tuple of (mean_prediction, uncertainty)
        """
        self.model.train()  # Enable dropout
        
        predictions = []
        for _ in range(self.num_samples):
            with torch.no_grad():
                pred = F.softmax(self.model(x), dim=1)
                predictions.append(pred)
        
        predictions = torch.stack(predictions)
        
        mean_pred = predictions.mean(dim=0)
        uncertainty = predictions.var(dim=0).mean(dim=1)  # Average variance across classes
        
        self.model.eval()  # Disable dropout
        
        return mean_pred, uncertainty


class MedicalModelFactory:
    """Factory for creating medical imaging models"""
    
    @staticmethod
    def create_model(model_type: str, num_classes: int, **kwargs) -> nn.Module:
        """Create medical imaging model based on type"""
        
        if model_type == 'medical_resnet50':
            return MedicalResNet50(num_classes=num_classes, **kwargs)
        elif model_type == 'medical_vit':
            return MedicalVisionTransformer(num_classes=num_classes, **kwargs)
        elif model_type == 'ensemble':
            models = kwargs.get('models', [])
            weights = kwargs.get('weights', None)
            return MedicalEnsembleModel(models, weights)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    @staticmethod
    def create_loss_function(loss_type: str, **kwargs) -> nn.Module:
        """Create medical-specific loss function"""
        
        if loss_type == 'focal':
            return MedicalFocalLoss(**kwargs)
        elif loss_type == 'dice':
            return DiceLoss(**kwargs)
        elif loss_type == 'combined':
            return CombinedMedicalLoss(**kwargs)
        else:
            raise ValueError(f"Unknown loss type: {loss_type}")
