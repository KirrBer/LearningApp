"""Менеджер ML-моделей.

Сервис загружает модели один раз (singleton) и предоставляет доступ к ним.
Это помогает избежать многократной загрузки больших моделей при каждом запросе.
"""

import logging
import spacy
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
from skill_analyzer.exceptions import ModelLoadingError

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
        
        Raises:
            ModelLoadingError: If model loading fails
        """
        if self._extractor_model is None:
            try:
                logger.info("Loading extractor model...")
                self._extractor_model = spacy.load("./extractor_model/model-best")
                logger.info("✅ Extractor model loaded!")
            except FileNotFoundError as e:
                logger.error(f"Extractor model files not found: {str(e)}")
                raise ModelLoadingError(f"Failed to load extractor model: {str(e)}")
            except Exception as e:
                logger.error(f"Error loading extractor model: {str(e)}")
                raise ModelLoadingError(f"Failed to load extractor model: {str(e)}")

            try:
                logger.info("Loading normalize model...")
                self._normalize_model = torch.compile(
                    T5ForConditionalGeneration.from_pretrained("./normalize_model")
                )
                self._tokenizer = T5Tokenizer.from_pretrained("./normalize_model")
                self._normalize_model.eval()
                logger.info("✅ Normalize model loaded!")
            except FileNotFoundError as e:
                logger.error(f"Normalize model files not found: {str(e)}")
                # Clean up extractor model if normalize model fails
                self._extractor_model = None
                raise ModelLoadingError(f"Failed to load normalize model: {str(e)}")
            except Exception as e:
                logger.error(f"Error loading normalize model: {str(e)}")
                # Clean up extractor model if normalize model fails
                self._extractor_model = None
                raise ModelLoadingError(f"Failed to load normalize model: {str(e)}")

    def get_extractor_model(self):
        """Returns the extractor model.
        
        Returns:
            spacy model or None
            
        Raises:
            ModelLoadingError: If model is not loaded
        """
        if self._extractor_model is None:
            raise ModelLoadingError("Extractor model is not loaded")
        return self._extractor_model

    def get_normalize_model(self):
        """Returns the normalize model.
        
        Returns:
            T5ForConditionalGeneration model or None
            
        Raises:
            ModelLoadingError: If model is not loaded
        """
        if self._normalize_model is None:
            raise ModelLoadingError("Normalize model is not loaded")
        return self._normalize_model

    def get_tokenizer(self):
        """Returns the tokenizer.
        
        Returns:
            T5Tokenizer or None
            
        Raises:
            ModelLoadingError: If tokenizer is not loaded
        """
        if self._tokenizer is None:
            raise ModelLoadingError("Tokenizer is not loaded")
        return self._tokenizer

    def unload_models(self):
        """Выгружает все модели и освобождает память.

        Вызывается при завершении работы сервиса.
        """
        try:
            if self._extractor_model:
                del self._extractor_model
                self._extractor_model = None
            if self._normalize_model:
                del self._normalize_model
                self._normalize_model = None
            if self._tokenizer:
                del self._tokenizer
                self._tokenizer = None
            logger.info("✅ Models unloaded successfully")
        except Exception as e:
            logger.error(f"Error unloading models: {str(e)}")


# Экспортируем единый экземпляр для всего приложения.
model_manager = ModelManager()