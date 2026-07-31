#!/usr/bin/env python3
"""
gpu_config.py
=============

GPU and concurrency configuration management for the document processing pipeline.
Handles automatic GPU detection, VRAM optimization, and CPU fallback.
"""

import os
import platform
from typing import Dict, Any, Callable, Optional


class GPUManager:
    """
    Manages GPU availability, VRAM allocation, and automatic CPU fallback.
    """
    
    def __init__(self):
        self.gpu_available = self._detect_gpu()
        self.mode = "GPU" if self.gpu_available else "CPU"
        self.vram_usage = {}
        
    def _detect_gpu(self) -> bool:
        """
        Detect if GPU is available for acceleration.
        Checks for CUDA, ROCm, or other GPU frameworks.
        """
        # Check CUDA availability (NVIDIA)
        try:
            import torch
            if torch.cuda.is_available():
                return True
        except ImportError:
            pass
        
        # Check for environment variable override
        gpu_disabled = os.getenv("DISABLE_GPU", "false").lower() == "true"
        if gpu_disabled:
            return False
        
        # Check CUDA_VISIBLE_DEVICES
        cuda_devices = os.getenv("CUDA_VISIBLE_DEVICES", "")
        if cuda_devices and cuda_devices != "-1":
            return True
        
        return False
    
    def execute_with_rostaing(self, pdf_path: str, extraction_func: Callable) -> str:
        """
        Execute rostaing-ocr extraction with automatic GPU VRAM optimization
        and CPU fallback protection.
        
        Args:
            pdf_path: Path to PDF file
            extraction_func: Function that performs the actual extraction
            
        Returns:
            Extracted text
        """
        if self.gpu_available:
            try:
                # Try GPU execution first
                return extraction_func(pdf_path)
            except RuntimeError as e:
                if "out of memory" in str(e).lower() or "cuda" in str(e).lower():
                    print(f"   ⚠️ GPU memory error: {e}")
                    print("   ⏩ Falling back to CPU mode...")
                    self.mode = "CPU"
                    self.gpu_available = False
                    return extraction_func(pdf_path)
                else:
                    raise
        else:
            # CPU-only execution
            return extraction_func(pdf_path)
    
    def get_optimal_workers(self, task_type: str = "default") -> int:
        """
        Get optimal number of worker threads based on hardware and task type.
        
        Args:
            task_type: Type of task (pdf_rendering, ocr, extraction)
            
        Returns:
            Optimal number of workers
        """
        cpu_count = os.cpu_count() or 4
        
        if task_type == "pdf_rendering":
            # PDF rendering is I/O bound, can use more workers
            return min(cpu_count * 2, 16)
        elif task_type == "ocr":
            # OCR is CPU/GPU intensive, use fewer workers
            if self.gpu_available:
                return min(cpu_count, 4)  # Limit to avoid GPU contention
            else:
                return min(cpu_count, 8)
        else:
            # Default: balanced approach
            return min(cpu_count, 8)


# Global GPU manager instance
gpu_manager = GPUManager()


# Concurrency configuration for different processing stages
gpu_concurrency_config: Dict[str, Any] = {
    "mode": gpu_manager.mode,
    "gpu_available": gpu_manager.gpu_available,
    
    # PDF rendering to images (I/O bound)
    "pdf_rendering": {
        "max_workers": gpu_manager.get_optimal_workers("pdf_rendering"),
        "use_threading": True,
        "description": "PDF page rendering is I/O bound, can use more workers"
    },
    
    # OCR processing (CPU/GPU intensive)
    "ocr": {
        "max_workers": gpu_manager.get_optimal_workers("ocr"),
        "use_threading": True,
        "batch_size": 4 if gpu_manager.gpu_available else 1,
        "description": "OCR is intensive, limit workers to avoid resource contention"
    },
    
    # Text extraction (mixed workload)
    "extraction": {
        "max_workers": gpu_manager.get_optimal_workers("extraction"),
        "use_threading": True,
        "description": "Balanced configuration for text extraction"
    },
    
    # System information
    "system": {
        "cpu_count": os.cpu_count() or 4,
        "platform": platform.system(),
        "python_version": platform.python_version()
    }
}


def print_config():
    """Print current GPU and concurrency configuration."""
    print("\n" + "="*80)
    print("GPU & CONCURRENCY CONFIGURATION")
    print("="*80)
    print(f"Mode: {gpu_concurrency_config['mode']}")
    print(f"GPU Available: {gpu_concurrency_config['gpu_available']}")
    print(f"CPU Count: {gpu_concurrency_config['system']['cpu_count']}")
    print(f"Platform: {gpu_concurrency_config['system']['platform']}")
    print()
    print("Worker Configuration:")
    print(f"  - PDF Rendering: {gpu_concurrency_config['pdf_rendering']['max_workers']} workers")
    print(f"  - OCR Processing: {gpu_concurrency_config['ocr']['max_workers']} workers")
    print(f"  - Text Extraction: {gpu_concurrency_config['extraction']['max_workers']} workers")
    print("="*80 + "\n")


def update_config(task_type: str, max_workers: Optional[int] = None):
    """
    Update concurrency configuration for a specific task type.
    
    Args:
        task_type: Type of task to update (pdf_rendering, ocr, extraction)
        max_workers: New maximum number of workers (None = auto-detect)
    """
    if task_type not in gpu_concurrency_config:
        raise ValueError(f"Unknown task type: {task_type}")
    
    if max_workers is not None:
        gpu_concurrency_config[task_type]["max_workers"] = max_workers
    else:
        gpu_concurrency_config[task_type]["max_workers"] = gpu_manager.get_optimal_workers(task_type)


def get_worker_count(task_type: str) -> int:
    """
    Get the configured worker count for a specific task type.
    
    Args:
        task_type: Type of task (pdf_rendering, ocr, extraction)
        
    Returns:
        Number of workers to use
    """
    config = gpu_concurrency_config.get(task_type, {})
    return config.get("max_workers", os.cpu_count() or 4)


# Auto-detect and configure on import
if __name__ == "__main__":
    print_config()
else:
    # Silent mode when imported
    pass


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
#
# Example 1: Check GPU availability
#   from gpu_config import gpu_manager
#   if gpu_manager.gpu_available:
#       print("GPU acceleration enabled")
#
# Example 2: Get optimal worker count
#   from gpu_config import get_worker_count
#   workers = get_worker_count("pdf_rendering")
#   with ThreadPoolExecutor(max_workers=workers) as executor:
#       # ... parallel processing
#
# Example 3: Execute with automatic GPU fallback
#   from gpu_config import gpu_manager
#   result = gpu_manager.execute_with_rostaing(pdf_path, extraction_function)
#
# Example 4: Print configuration
#   from gpu_config import print_config
#   print_config()
#
# Example 5: Update configuration
#   from gpu_config import update_config
#   update_config("ocr", max_workers=4)
#
# ============================================================================
