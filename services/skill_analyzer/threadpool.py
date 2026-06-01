from concurrent.futures import ProcessPoolExecutor
import asyncio
from functools import partial
from skill_analyzer.exceptions import ProcessPoolError
import logging
import os

logger = logging.getLogger(__name__)


class ProcessPoolManager():
    """Manager for process pool executor.
    
    Uses multiprocessing instead of threading for CPU-bound ML inference tasks.
    This bypasses Python's GIL and allows true parallelism on multi-core systems.
    Workers count = min(CPU cores, 4) to balance parallelism and memory usage
    (each worker loads large ML models).
    """
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.process_pool = None
    
    def create(self):
        """Create process pool for running CPU-bound ML inference operations.
        
        Raises:
            ProcessPoolError: If process pool creation fails
        """
        try:
            # Determine number of workers: min(CPU cores, 4)
            # Each worker loads large ML models, so we limit to avoid excessive memory usage
            cpu_count = os.cpu_count() or 1
            max_workers = min(cpu_count, 4)
            
            self.process_pool = ProcessPoolExecutor(max_workers=max_workers)
            logger.info(f"✅ Process pool created with {max_workers} workers (CPU cores: {cpu_count})")
        except Exception as e:
            logger.error(f"Error creating process pool: {str(e)}")
            raise ProcessPoolError(f"Failed to create process pool: {str(e)}")

    async def run_in_process_pool(self, func, *args, **kwargs):
        """Запуск CPU-bound функции в пуле процессов.
        
        Обходит Python GIL для истинного параллелизма при ML-inference операциях.
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Result of function execution
            
        Raises:
            ProcessPoolError: If process pool operation fails
        """
        if self.process_pool is None:
            raise ProcessPoolError("Process pool is not initialized")
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.process_pool, 
                partial(func, *args, **kwargs)
            )
            return result
        except Exception as e:
            logger.error(f"Error executing function in process pool: {str(e)}")
            raise ProcessPoolError(f"Failed to execute function in process pool: {str(e)}")

    async def stop(self):
        """Stop process pool and wait for all tasks to complete.
        
        Raises:
            ProcessPoolError: If process pool shutdown fails
        """
        if self.process_pool is None:
            return
        
        try:
            self.process_pool.shutdown(wait=True)
            logger.info("✅ Process pool shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down process pool: {str(e)}")
            raise ProcessPoolError(f"Failed to shutdown process pool: {str(e)}")


process_pool_manager = ProcessPoolManager()