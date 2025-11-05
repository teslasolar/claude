"""
🧬 KONOMI System - Main Package
"""
__version__ = "1.0.0"
__author__ = "Based on Thomas Frumkin's specification"

from .core import (
    eVGPU,
    FemtoLLM,
    BlockArray,
    Cube,
    MachineState,
    VertexPosition,
    KonomiSystem,
)

__all__ = [
    'eVGPU',
    'FemtoLLM',
    'BlockArray',
    'Cube',
    'MachineState',
    'VertexPosition',
    'KonomiSystem',
]
