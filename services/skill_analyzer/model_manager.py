"""Менеджер ML-моделей.

Сервис загружает модели один раз (singleton) и предоставляет доступ к ним.
Это помогает избежать многократной загрузки больших моделей при каждом запросе.
"""

import logging
import spacy
from transformers import T5ForConditionalGeneration, T5Tokenizer

logger = logging.getLogger(__name__)


class ModelManager:
    # Singleton, чтобы модели загружались только один раз на процесс.
    _instance = None
    _extractor_model = None
    _normalize_model = None
    _tokenizer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_models(self):
        """Загружает spaCy + T5 модели (лениво).

        Если модели уже загружены, метод просто возвращает управление.
        """
        if self._extractor_model is None:
            self._extractor_model = spacy.load("./extractor_model/model-best")
            logger.info("✅ Extractor model loaded!")

            self._normalize_model = T5ForConditionalGeneration.from_pretrained("./normalize_model")
            self._tokenizer = T5Tokenizer.from_pretrained("./normalize_model")
            self._normalize_model.eval()
            logger.info("✅ Normalize model loaded!")

    def get_extractor_model(self):
        return self._extractor_model

    def get_normalize_model(self):
        return self._normalize_model

    def get_tokenizer(self):
        return self._tokenizer

    def unload_models(self):
        """Выгружает все модели и освобождает память.

        Вызывается при завершении работы сервиса.
        """
        if self._extractor_model:
            del self._extractor_model
            self._extractor_model = None
            del self._normalize_model
            self._normalize_model = None
            del self._tokenizer
            self._tokenizer = None
            logger.info("✅ Модель выгружена")


# Экспортируем единый экземпляр для всего приложения.
model_manager = ModelManager()