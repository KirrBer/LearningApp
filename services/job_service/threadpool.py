from concurrent.futures import ThreadPoolExecutor
import asyncio
from functools import partial
import asyncio

class ThreadpoolManager():
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def create(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=10)

    async def run_in_custom_threadpool(self, func, *args, **kwargs):
        """Запуск функции в выделенном пуле потоков."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.thread_pool, 
            partial(func, *args, **kwargs)
        )
    async def stop(self):
        self.thread_pool.shutdown(wait=True)

threadpool_manager = ThreadpoolManager()