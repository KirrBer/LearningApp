# LearningApp 📚

Веб-приложение для анализа навыков и подбора актуальных курсов обучения. Приложение автоматически извлекает навыки из текста или PDF-документов и предлагает релевантные курсы для их развития.

## 🎯 Основные возможности

- **Извлечение навыков из текста** - анализ текстовой информации и идентификация профессиональных навыков
- **Извлечение навыков из PDF** - обработка PDF-документов для автоматической идентификации навыков
- **Web-интерфейс** - удобный пользовательский интерфейс с использованием Next.js и React
- **ML-модели** - использование продвинутых моделей для NER (Named Entity Recognition) и нормализации текста
- **Рекомендации** - система подбора на основе tf-idf векторизации текста

## 🏗️ Архитектура проекта

```
LearningApp/
├── services/
│   ├── frontend/              # Next.js приложение
│   │   ├── app/              # Application layout и страницы
│   │   └── components/       # React компоненты
│   ├── skill_analyzer/       # Сервис анализа скиллов
│   │   ├── extractor_model/  # NER модель для извлечения навыков из текста
│   │   ├── normalize_model/  # T5 модель для преобразования найденных навыков к стандартному виду
│   │   ├── model_manager.py  # Провайдер моделей(модели подгружаются при запуске сервиса)
│   │   ├── routes.py         # API endpoints
│   │   ├── db_methods.py     # Методы работы с БД
│   │   ├── kafka.py          # kafka producer and consumer
│   │   ├── utils.py          # Методы обработки данных
│   │   ├── seed_data.py      # Заполняет БД данными при запуске сервиса
│   │   ├── tests/            # Unit-тесты с покрытием 74%
│   │   └── migration/        # Миграции БД (Alembic)
│   ├── job_service/          # Сервис вакансий: поиск и рекомендации вакансий на основе текста резюме
│   │   ├── routes.py         # API endpoints (recommendations и вакансии)
│   │   ├── db_methods.py     # Методы доступа к БД
│   │   ├── db.py             # ORM, сессии, настройки БД
│   │   ├── models.py         # SQLAlchemy модель Vacancy
│   │   ├── schemas.py        # Pydantic схемы для запросов/ответов
│   │   ├── settings.py       # Настройки PostgreSQL (env)
│   │   ├── api_hhru.py       # Хелпер для загрузки вакансий из hh.ru
│   │   ├── threadpool.py     # Менеджер фоновых задач
│   │   ├── seed_data.py      # Заполняет БД данными при запуске сервиса
│   │   └── tests/            # Unit-тесты
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
- **Pytest** - тестирование

### ML
- **spaCy** - NER модель для извлечения сущностей
- **T5** - Дообученная rut5-small модель
- **tf-idf** - для рекомендаций

### Frontend
- **Next.js** - React фреймворк
- **TypeScript** - типизированный JavaScript
- **Tailwind CSS** - CSS фреймворк

### DevOps
- **Docker** - контейнеризация
- **Docker Compose** - оркестрация контейнеров
- **Nginx** - веб-сервер и reverse proxy
- **GitHub Actions** - CI/CD



## 🚀 Быстрый старт

### 1. Подготовка окружения

Создайте файл `.env` в директории `services/` с переменными окружения:

```env
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
PGDATA=pgdata:/var/lib/postgresql/data
DB_PORT=5432
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

DB_HOST_SA=skill_analyzer_db
POSTGRES_DB_SA=skills
DB_HOST_JS=job_service_db
POSTGRES_DB_JS=vacancies
```

### 2. Запуск приложения

Перейдите в директорию `services/` и запустите Docker Compose:

```bash
cd services
docker-compose up -d
```




## 🧩 Job Service (vacancies)

Job service предоставляет API для поиска и рекомендаций вакансий на основе резюме (текст/PDF) и для работы с базой вакансий.

- Backend: FastAPI
- БД: PostgreSQL
- ORM: SQLAlchemy (async)
- Модели: `job_service/models.py`, `job_service/schemas.py`
- Настройки: `job_service/settings.py` (env через `.env`)

### Endpoints Job Service

- `POST /recommendations_from_text` - рекомендация вакансий по тексту резюме.
  - тело: `{ "resume": "..." }`
  - ответ: список `ShortVacancyResponse` (id, name, employer, salary, area)
- `POST /recommendations_from_pdf` - рекомендации по резюме в PDF (content_type `application/pdf`)
- `GET /vacancies?page={page}` - пагинация вакансий (10 на страницу)
- `GET /vacancies/{id}` - детальная вакансия
- `GET /health` - статус сервиса

### Запуск Job Service локально

```bash
cd services/job_service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

Если вы используете `docker-compose`, то запускается вместе со всеми сервисами из `services/docker-compose.yml`.

## 🧩 Skill Analyzer (skills)

Skill analyzer отвечает за извлечение навыков из текста и PDF, нормализацию скиллов и предоставление рекомендаций.

- Backend: FastAPI
- ML: spaCy NER, T5 (normalize)
- БД: PostgreSQL
- ORM: SQLAlchemy (async)
- Миграции: Alembic
- Модели: `skill_analyzer/models.py`, `skill_analyzer/schemas.py`
- Настройки: `skill_analyzer/settings.py` (env через `.env`)

### Endpoints Skill Analyzer

- `POST /extract_skills_from_text` - извлечь навыки из текста.
  - тело: `{ "text": "..." }`
  - ответ: список объектов с полями `skill`, `course`.
- `POST /extract_skills_from_pdf` - извлечь навыки из PDF (multipart form-data).
- `GET /health` - статус сервиса

### Запуск Skill Analyzer локально

```bash
cd services/skill_analyzer
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

Если используете `docker-compose`, сервис поднимается вместе со всеми сервисами (см. `services/docker-compose.yml`).

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

