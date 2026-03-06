# LearningApp 📚

Веб-приложение для анализа навыков и подбора актуальных курсов обучения. Приложение автоматически извлекает навыки из текста или PDF-документов и предлагает релевантные курсы для их развития.

## 🎯 Основные возможности

- **Извлечение навыков из текста** - анализ текстовой информации и идентификация профессиональных навыков
- **Извлечение навыков из PDF** - обработка PDF-документов для автоматической идентификации навыков
- **Подбор курсов** - рекомендация курсов на основе выявленных навыков
- **Web-интерфейс** - удобный пользовательский интерфейс с использованием Next.js и React
- **ML-модели** - использование продвинутых моделей для NER (Named Entity Recognition) и нормализации текста

## 🏗️ Архитектура проекта

```
LearningApp/
├── services/
│   ├── frontend/              # Next.js приложение
│   │   ├── app/              # Application layout и страницы
│   │   └── components/       # React компоненты
│   ├── skill_analyzer/       # FastAPI бэкенд
│   │   ├── models/           # ML-модели
│   │   ├── routes.py         # API endpoints
│   │   ├── db_methods.py     # Методы работы с БД
│   │   └── migration/        # Миграции БД (Alembic)
│   ├── docker-compose.yml    # Docker Compose конфигурация
│   └── nginx.conf            # Nginx конфигурация
└── README.md                  # Этот файл
```

## 🛠️ Технический стек

### Backend
- **FastAPI** - современный веб-фреймворк для Python
- **PostgreSQL** - реляционная база данных
- **SQLAlchemy** - ORM для работы с БД
- **Alembic** - управление миграциями БД
- **spaCy** - NER модель для извлечения сущностей

### Frontend
- **Next.js 14+** - React фреймворк
- **TypeScript** - типизированный JavaScript
- **Tailwind CSS** - утилита-первый CSS фреймворк
- **React** - библиотека для UI

### DevOps
- **Docker** - контейнеризация
- **Docker Compose** - оркестрация контейнеров
- **Nginx** - веб-сервер и reverse proxy



## 🚀 Быстрый старт

### 1. Подготовка окружения

Создайте файл `.env` в директории `services/` с переменными окружения:

```env
POSTGRES_USER=learningapp_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=learningapp_db
PGDATA=/var/lib/postgresql/data
DB_PORT=5432
DB_HOST=skill_analyzer_db
```

### 2. Запуск приложения

Перейдите в директорию `services/` и запустите Docker Compose:

```bash
cd services
docker-compose up -d
```


## 📡 API Endpoints

### POST /extract_skills_from_text
Извлечение навыков из текста

**Request:**
```json
{
  "text": "Я работаю с Python, JavaScript и машинным обучением"
}
```

**Response:**
```json
[
  {
    "skill": "Python",
    "courses": [...]
  }
]
```

### POST /extract_skills_from_pdf
Извлечение навыков из PDF-документа

**Request:** Multipart form-data с файлом

**Response:** Список навыков с рекомендованными курсами

## 🗄️ База данных

Проект использует PostgreSQL. Миграции управляются через Alembic и находятся в `skill_analyzer/migration/versions/`.

### Запуск миграций

```bash
docker-compose exec skill_analyzer alembic upgrade head
```

### Создание новой миграции

```bash
docker-compose exec skill_analyzer alembic revision --autogenerate -m "Описание изменений"
```

## 📁 Структура папок

- **frontend/** - Next.js приложение с компонентами и страницами
- **skill_analyzer/** - FastAPI приложение с моделями и API
  - `extractor_model/` - spaCy модель для NER
  - `normalize_model/` - модель для нормализации текста
  - `models.py` - SQLAlchemy модели
  - `routes.py` - API endpoints
  - `db_methods.py` - методы для работы с БД
  - `tests/` - юнит-тесты

## 🧪 Тестирование

Запуск тестов backend'а:

```bash
docker-compose exec skill_analyzer python -m pytest
```

## 🛑 Остановка приложения

```bash
docker-compose down
```

Для удаления объема БД:
```bash
docker-compose down -v
```

## 🔧 Разработка

### Локальная разработка Frontend

```bash
cd services/frontend
npm install
npm run dev
```

### Локальная разработка Backend

```bash
cd services/skill_analyzer
pip install -r requirements.txt
python main.py
```

## 📝 Логирование

Приложение генерирует логи в консоль с уровнем INFO. Для изменении уровня отредактируйте `skill_analyzer/main.py`.

