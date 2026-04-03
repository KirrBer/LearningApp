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
from skill_analyzer.exceptions import KafkaConnectionError, KafkaMessageError
import logging

logger = logging.getLogger(__name__)

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
        self._consume_task = None
        
    async def start(self):
        """Инициализация Kafka producer/consumer и запуск цикла обработки сообщений.
        
        Raises:
            KafkaConnectionError: If connection to Kafka fails
        """
        try:
            # Producer отправляет результаты извлечения навыков.
            logger.info("Connecting to Kafka producer...")
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id='skill-analyzer-producer',
                value_serializer=lambda v: json.dumps(v).encode()
            )
            await self.producer.start()
            logger.info("✅ Kafka producer started")
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {str(e)}")
            raise KafkaConnectionError(f"Failed to initialize Kafka producer: {str(e)}")
        
        try:
            # Запускаем consumer
            logger.info("Connecting to Kafka consumer...")
            self.consumer = AIOKafkaConsumer(
                'extract_skills_from_text', 'extract_skills_from_pdf',
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id='skill-analyzer-consumer',
                value_deserializer=lambda m: json.loads(m.decode()),
                auto_offset_reset='earliest',
                group_id='skill-analyzer-group'
            )
            await self.consumer.start()
            logger.info("✅ Kafka consumer started")
        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {str(e)}")
            try:
                if self.producer:
                    await self.producer.stop()
            except Exception as stop_error:
                logger.error(f"Error stopping producer during cleanup: {str(stop_error)}")
            raise KafkaConnectionError(f"Failed to initialize Kafka consumer: {str(e)}")
        
        logger.info("✅ Kafka started successfully")
        
        # Запускаем обработку в фоне
        self._consume_task = asyncio.create_task(self.consume_loop())
    
    async def stop(self):
        """Stop Kafka producer and consumer."""
        try:
            if self._consume_task:
                self._consume_task.cancel()
                try:
                    await self._consume_task
                except asyncio.CancelledError:
                    logger.info("Consume task cancelled")
        except Exception as e:
            logger.error(f"Error cancelling consume task: {str(e)}")

        try:
            # Wait for all pending tasks to complete or timeout
            if self.tasks:
                await asyncio.wait(self.tasks, timeout=5.0)
        except Exception as e:
            logger.error(f"Error waiting for pending tasks: {str(e)}")

        try:
            if self.producer:
                await self.producer.stop()
                logger.info("✅ Kafka producer stopped")
        except Exception as e:
            logger.error(f"Error stopping producer: {str(e)}")

        try:
            if self.consumer:
                await self.consumer.stop()
                logger.info("✅ Kafka consumer stopped")
        except Exception as e:
            logger.error(f"Error stopping consumer: {str(e)}")
        
    async def consume_loop(self):
        """Фоновый цикл, читающий сообщения из Kafka и обрабатывающий их."""
        try:
            async for msg in self.consumer:
                try:
                    task = asyncio.create_task(self.process_message(msg))
                    self.tasks.append(task)

                    # Очищаем завершенные задачи
                    self.tasks = [t for t in self.tasks if not t.done()]
                except Exception as e:
                    logger.error(f"Error creating task for message: {str(e)}")
        except asyncio.CancelledError:
            logger.info("Consume loop cancelled")
        except Exception as e:
            logger.error(f"Error in consume loop: {str(e)}")

    async def process_message(self, msg):
        """Обрабатывает одно сообщение из Kafka и отправляет результат в топик extraction_results.
        
        Args:
            msg: Kafka message
        """
        try:
            result = None
            
            if msg.topic == 'extract_skills_from_text':
                try:
                    text = msg.value.get('text', '')
                    if not text:
                        logger.warning("Received empty text in extract_skills_from_text message")
                        return
                    result = extract_skills_from_text(text)
                except Exception as e:
                    logger.error(f"Error processing text extraction message: {str(e)}")
                    return
                    
            elif msg.topic == 'extract_skills_from_pdf':
                try:
                    pdf_data = msg.value.get('pdf_data', '')
                    if not pdf_data:
                        logger.warning("Received empty PDF data in extract_skills_from_pdf message")
                        return
                    # Note: This would need proper PDF data handling
                    # For now, we'll skip this or handle appropriately
                    logger.info(f"Processing PDF message: {msg.value.get('filename', 'unknown')}")
                    return
                except Exception as e:
                    logger.error(f"Error processing PDF extraction message: {str(e)}")
                    return
            
            if result:
                try:
                    await self.producer.send(
                        'extraction_results',
                        value={
                            'topic': msg.topic,
                            'skills': result,
                            'timestamp': msg.timestamp
                        }
                    )
                    logger.info(f"✅ Result published to extraction_results")
                except Exception as e:
                    logger.error(f"Error publishing message to Kafka: {str(e)}")
                    raise KafkaMessageError(f"Failed to publish extraction result: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Unhandled error in process_message: {str(e)}")


kafka_manager = KafkaManager()