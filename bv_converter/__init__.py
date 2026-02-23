"""bv_converter - 将B站缓存中的.m4s文件转换为.mp4格式"""

__version__ = "0.1.0"

from .cli import main, process_bili_cache

__all__ = ["main", "process_bili_cache", "__version__"]
