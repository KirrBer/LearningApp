from concurrent.futures import ProcessPoolExecutor
import asyncio
from functools import partial
import os


class ProcessPoolManager():
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.process_pool = None

    def create(self):
        # ограничиваем количество процессов, т.к. каждый процесс может потреблять много памяти
        cpu_count = os.cpu_count() or 1
        max_workers = min(cpu_count, 4)
        self.process_pool = ProcessPoolExecutor(max_workers=max_workers)

    async def run_in_process_pool(self, func, *args, **kwargs):
        """Run CPU-bound function in a separate process to bypass GIL."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.process_pool,
            partial(func, *args, **kwargs)
        )

    async def stop(self):
        if self.process_pool:
            self.process_pool.shutdown(wait=True)


process_pool_manager = ProcessPoolManager()