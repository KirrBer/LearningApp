from concurrent.futures import ThreadPoolExecutor
import asyncio
from functools import partial
from skill_analyzer.exceptions import ThreadPoolError
import logging

logger = logging.getLogger(__name__)


class ThreadpoolManager():
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.thread_pool = None
    
    def create(self):
        """Create threadpool for running blocking operations.
        
        Raises:
            ThreadPoolError: If threadpool creation fails
        """
        try:
            self.thread_pool = ThreadPoolExecutor(max_workers=10)
            logger.info("✅ Threadpool created with 10 workers")
        except Exception as e:
            logger.error(f"Error creating threadpool: {str(e)}")
            raise ThreadPoolError(f"Failed to create threadpool: {str(e)}")

    async def run_in_custom_threadpool(self, func, *args, **kwargs):
        """Запуск функции в выделенном пуле потоков.
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Result of function execution
            
        Raises:
            ThreadPoolError: If threadpool operation fails
        """
        if self.thread_pool is None:
            raise ThreadPoolError("Threadpool is not initialized")
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.thread_pool, 
                partial(func, *args, **kwargs)
            )
            return result
        except Exception as e:
            logger.error(f"Error executing function in threadpool: {str(e)}")
            raise ThreadPoolError(f"Failed to execute function in threadpool: {str(e)}")

    async def stop(self):
        """Stop threadpool and wait for all tasks to complete.
        
        Raises:
            ThreadPoolError: If threadpool shutdown fails
        """
        if self.thread_pool is None:
            return
        
        try:
            self.thread_pool.shutdown(wait=True)
            logger.info("✅ Threadpool shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down threadpool: {str(e)}")
            raise ThreadPoolError(f"Failed to shutdown threadpool: {str(e)}")


threadpool_manager = ThreadpoolManager()