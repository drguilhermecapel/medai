"""
Memory monitoring utilities.
"""

import logging
from typing import Any

import psutil

logger = logging.getLogger(__name__)


class MemoryMonitor:
    """Monitor memory usage for ML models and processing."""

    def get_memory_usage(self) -> dict[str, Any]:
        """Get current memory usage statistics."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()

            system_memory = psutil.virtual_memory()

            return {
                "process_memory_mb": memory_info.rss / 1024 / 1024,
                "process_memory_percent": process.memory_percent(),
                "system_memory_total_gb": system_memory.total / 1024 / 1024 / 1024,
                "system_memory_available_gb": system_memory.available / 1024 / 1024 / 1024,
                "system_memory_percent": system_memory.percent,
            }

        except Exception as e:
            logger.error("Failed to get memory usage: %s", str(e))
            return {
                "process_memory_mb": 0,
                "process_memory_percent": 0,
                "system_memory_total_gb": 0,
                "system_memory_available_gb": 0,
                "system_memory_percent": 0,
            }

    def check_memory_threshold(self, threshold_percent: float = 80.0) -> bool:
        """Check if memory usage exceeds threshold."""
        try:
            memory_info = self.get_memory_usage()
            system_percent = memory_info["system_memory_percent"]
            if isinstance(system_percent, int | float):
                return system_percent > threshold_percent
            return False
        except Exception:
            return False

    def log_memory_usage(self, context: str = "") -> None:
        """Log current memory usage."""
        try:
            memory_info = self.get_memory_usage()
            logger.info(
                "Memory usage %s - Process: %.1f MB, System: %.1f%%",
                context,
                memory_info["process_memory_mb"],
                memory_info["system_memory_percent"],
            )
        except Exception as e:
            logger.error("Failed to log memory usage: %s", str(e))
