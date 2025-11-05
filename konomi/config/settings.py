"""
⚙️ KONOMI System Configuration
"""
import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class eVGPUConfig:
    """eVGPU configuration"""
    cores: int = 4
    use_simd: bool = True
    enable_cache: bool = True


@dataclass
class FemtoLLMConfig:
    """FemtoLLM configuration"""
    hidden_size: int = 16
    vocab_size: int = 256
    target_latency: float = 0.1  # seconds
    target_memory: float = 4.0  # MB


@dataclass
class BlockArrayConfig:
    """BlockArray configuration"""
    default_dimensions: tuple = (10, 10, 10)
    max_dimensions: tuple = (1000, 1000, 1000)
    sparse_storage: bool = True
    compression_enabled: bool = True


@dataclass
class AnalyticsConfig:
    """Analytics configuration"""
    window_size: int = 100
    enable_cognitive_analysis: bool = True
    enable_prediction: bool = True
    learning_enabled: bool = True


@dataclass
class APIConfig:
    """API configuration"""
    rest_host: str = "0.0.0.0"
    rest_port: int = 3001
    ws_host: str = "0.0.0.0"
    ws_port: int = 3002
    enable_cors: bool = True


@dataclass
class KonomiConfig:
    """Main KONOMI system configuration"""
    evgpu: eVGPUConfig = eVGPUConfig()
    femtollm: FemtoLLMConfig = FemtoLLMConfig()
    blockarray: BlockArrayConfig = BlockArrayConfig()
    analytics: AnalyticsConfig = AnalyticsConfig()
    api: APIConfig = APIConfig()

    debug: bool = False
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> 'KonomiConfig':
        """Load configuration from environment variables"""
        config = cls()

        # eVGPU
        if cores := os.getenv('EVGPU_CORES'):
            config.evgpu.cores = int(cores)

        # API
        if rest_port := os.getenv('REST_PORT'):
            config.api.rest_port = int(rest_port)
        if ws_port := os.getenv('WS_PORT'):
            config.api.ws_port = int(ws_port)

        # Debug
        if debug := os.getenv('DEBUG'):
            config.debug = debug.lower() in ('true', '1', 'yes')

        if log_level := os.getenv('LOG_LEVEL'):
            config.log_level = log_level.upper()

        return config

    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return {
            'evgpu': {
                'cores': self.evgpu.cores,
                'use_simd': self.evgpu.use_simd,
                'enable_cache': self.evgpu.enable_cache,
            },
            'femtollm': {
                'hidden_size': self.femtollm.hidden_size,
                'vocab_size': self.femtollm.vocab_size,
                'target_latency': self.femtollm.target_latency,
                'target_memory': self.femtollm.target_memory,
            },
            'blockarray': {
                'default_dimensions': self.blockarray.default_dimensions,
                'max_dimensions': self.blockarray.max_dimensions,
                'sparse_storage': self.blockarray.sparse_storage,
                'compression_enabled': self.blockarray.compression_enabled,
            },
            'analytics': {
                'window_size': self.analytics.window_size,
                'enable_cognitive_analysis': self.analytics.enable_cognitive_analysis,
                'enable_prediction': self.analytics.enable_prediction,
                'learning_enabled': self.analytics.learning_enabled,
            },
            'api': {
                'rest_host': self.api.rest_host,
                'rest_port': self.api.rest_port,
                'ws_host': self.api.ws_host,
                'ws_port': self.api.ws_port,
                'enable_cors': self.api.enable_cors,
            },
            'debug': self.debug,
            'log_level': self.log_level,
        }


# Global configuration instance
_config: Optional[KonomiConfig] = None


def get_config() -> KonomiConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = KonomiConfig.from_env()
    return _config


def set_config(config: KonomiConfig):
    """Set global configuration instance"""
    global _config
    _config = config


if __name__ == "__main__":
    # Test configuration
    print("⚙️ KONOMI Configuration Test\n")

    config = KonomiConfig.from_env()
    print("Configuration:")
    import json
    print(json.dumps(config.to_dict(), indent=2))

    print("\n✓ Configuration test complete!")
