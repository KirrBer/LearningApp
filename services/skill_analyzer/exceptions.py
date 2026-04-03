"""Custom exceptions for Skill Analyzer service."""


class SkillAnalyzerException(Exception):
    """Base exception for all Skill Analyzer errors."""
    pass


class ModelLoadingError(SkillAnalyzerException):
    """Raised when ML model loading fails."""
    pass


class ModelInferenceError(SkillAnalyzerException):
    """Raised when model inference fails."""
    pass


class PDFExtractionError(SkillAnalyzerException):
    """Raised when PDF text extraction fails."""
    pass


class KafkaError(SkillAnalyzerException):
    """Base exception for Kafka-related errors."""
    pass


class KafkaConnectionError(KafkaError):
    """Raised when Kafka connection fails."""
    pass


class KafkaMessageError(KafkaError):
    """Raised when Kafka message processing fails."""
    pass


class DatabaseError(SkillAnalyzerException):
    """Base exception for database-related errors."""
    pass


class DatabaseQueryError(DatabaseError):
    """Raised when database query fails."""
    pass


class ThreadPoolError(SkillAnalyzerException):
    """Raised when threadpool operations fail."""
    pass
