"""Kafka manager for Skill Analyzer.

Обрабатывает входящие сообщения из топиков:
- extract_skills_from_text
- extract_skills_from_pdf

Публикует результаты в топик `extraction_results`.
"""

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json
from skill_analyzer.settings import settings
from skill_analyzer.utils import extract_skills_from_text, extract_text_from_pdf

class KafkaManager:
    """Управляет Kafka producer/consumer и обрабатывает входящие сообщения."""

    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self):
        self.producer = None
        self.consumer = None
        self.tasks = []
        
    async def start(self):
        """Инициализация Kafka producer/consumer и запуск цикла обработки сообщений."""

        # Producer отправляет результаты извлечения навыков.
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id='skill-analyzer-producer',
            value_serializer=lambda v: json.dumps(v).encode()
        )
        await self.producer.start()
        
        # Запускаем consumer
        self.consumer = AIOKafkaConsumer(
            'extract_skills_from_text','extract_skills_from_pdf',
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id='skill-analyzer-consumer',
            value_deserializer=lambda m: json.loads(m.decode())
        )
        await self.consumer.start()
        
        print("✅ Сервис запущен: и producer, и consumer готовы")
        
        # Запускаем обработку в фоне
        asyncio.create_task(self.consume_loop())
        
    async def consume_loop(self):
        """Фоновый цикл, читающий сообщения из Kafka и обрабатывающий их."""

        async for msg in self.consumer:
            task = asyncio.create_task(self.process_message(msg))
            self.tasks.append(task)

            # Очищаем завершенные задачи
            self.tasks = [t for t in self.tasks if not t.done()]

    async def process_message(self, msg):
        """Обрабатывает одно сообщение из Kafka и отправляет результат в топик extraction_results."""
        if msg.topic == 'extract_skills_from_text':
            result = extract_skills_from_text(msg.value)
        elif msg.topic == 'extract_skills_from_pdf':
            text = await extract_text_from_pdf(msg.value)
            result = extract_skills_from_text(text)
        
        # Можно отправить результат
        await self.producer.send('extraction_results', value=result)
    


kafka_manager = KafkaManager()