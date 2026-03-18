# LearningApp 📚

Веб-приложение для анализа навыков и подбора актуальных курсов обучения. Приложение автоматически извлекает навыки из текста или PDF-документов и предлагает релевантные курсы для их развития.

## 🎯 Основные возможности

- **Извлечение навыков из текста** - анализ текстовой информации и идентификация профессиональных навыков
- **Извлечение навыков из PDF** - обработка PDF-документов для автоматической идентификации навыков
- **Web-интерфейс** - удобный пользовательский интерфейс с использованием Next.js и React
- **ML-модели** - использование продвинутых моделей для NER (Named Entity Recognition) и нормализации текста

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
│   ├── job_service/          # Сервис вакансий
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
- **Apache kafka** - брокер сообщений

### ML
- **spaCy** - NER модель для извлечения сущностей
- **T5** - Дообученная rut5-small модель

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
PGDATA=/var/lib/postgresql/data
DB_PORT=5432

POSTGRES_DB_SA=skills
DB_HOST_SA=skill_analyzer_db
POSTGRES_DB_JS=vacancies
DB_HOST_JS=job_service_db
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
    "course": "ссылка"
  },
  {
    "skill": "JavaScript",
    "course": None
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

