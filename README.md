# LearningApp 📚

Веб-приложение для анализа резюме, извлечения навыков, рекомендаций вакансий и персонального профиля пользователя. Проект объединяет frontend на Next.js, несколько Python-сервисов на FastAPI и общую JWT-авторизацию через gateway.

## Основной сценарий

Пользователь:
- регистрируется и логинится в приложении;
- вставляет резюме или загружает PDF;
- сервис анализа извлекает скиллы и рекомендует связанные курсы/навыки;
- система сохраняет резюме и список навыков в базе данных пользователя;
- на странице профиля пользователь видит своё резюме и извлечённые скиллы;
- на странице вакансий можно получить рекомендации по вакансии на основе сохранённого резюме.

## Основные возможности

- регистрация и логин по JWT;
- хранение резюме пользователя в БД (`users.resume`);
- хранение извлечённых навыков в БД (`user_skills`);
- анализ резюме из текста и PDF;
- поиск и просмотр вакансий;
- рекомендации вакансий по тексту резюме;
- профиль пользователя с сохранённым резюме и навыками;
- заглушки для временно нерабочих маршрутов.

## Архитектура проекта

```text
LearningApp/
├── services/
│   ├── frontend/                    # Next.js frontend
│   │   ├── app/
│   │   │   ├── (main)/
│   │   │   │   ├── profile/
│   │   │   │   ├── skill_analyzer/
│   │   │   │   ├── vacancies/
│   │   │   │   ├── courses/
│   │   │   │   └── learning_path_generator/
│   │   │   ├── components/
│   │   │   └── lib/
│   │   ├── package.json
│   │   ├── next.config.ts
│   │   └── tsconfig.json
│   ├── auth_service/               # сервис авторизации и профиля
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── db_methods.py
│   │   ├── db.py
│   │   ├── settings.py
│   │   ├── migration/
│   │   └── requirements.txt
│   ├── skill_analyzer/             # извлечение навыков из текста/PDF
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── utils.py
│   │   ├── model_manager.py
│   │   ├── models.py
│   │   ├── settings.py
│   │   ├── extractor_model/
│   │   ├── normalize_model/
│   │   └── tests/
│   ├── job_service/                # вакансии и рекомендации
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── utils.py
│   │   ├── api_hhru.py
│   │   ├── db_methods.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── settings.py
│   │   └── tests/
│   ├── gateway_service/            # API gateway / прокси + JWT-check
│   │   ├── main.py
│   │   ├── settings.py
│   │   └── Dockerfile
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── README.md
├── README.md
└── .gitignore
```

## Технологический стек

### Frontend
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- JWT (python-jose)

### AI / ML
- spaCy
- T5 / Hugging Face models
- TF-IDF для сравнения резюме с вакансиями

### DevOps
- Docker
- Docker Compose
- Nginx

## Запуск проекта

### 1. Подготовить окружение

В корне проекта и в сервисах должны быть настроены переменные окружения. Обычно проект запускается через Docker Compose из каталога `services/`.

```bash
cd services
docker compose up -d --build
```

После запуска сервисы доступны по адресам:
- Frontend: http://localhost:3000
- Gateway: http://localhost:8000
- Auth service: http://localhost:8002
- Job service: http://localhost:8001
- Skill analyzer: внутренняя служба, доступ через gateway

## Основные HTTP endpoints

### Auth Service

- `POST /register`
- `POST /login`
- `POST /verify`
- `POST /refresh`
- `GET /profile`
- `PUT /profile` — обновление имени, email и имени пользователя
- `PUT /profile/resume`
- `GET /profile/skills`
- `PUT /profile/skills`
- `GET /health`

### Gateway

- `ANY /api/auth/*`
- `ANY /api/job_service/*`
- `ANY /api/skill_analyzer/*`
- `GET /api/health`

### Job Service

- `POST /api/job_service/recommendations_from_text`
- `POST /api/job_service/recommendations_from_pdf`
- `GET /api/job_service/vacancies`
- `GET /api/job_service/vacancies/{id}`

### Skill Analyzer

- `POST /api/skill_analyzer/extract_skills_from_text`
- `POST /api/skill_analyzer/extract_skills_from_pdf` — возвращает извлечённый текст резюме и навыки

## Схема сохранения резюме и навыков

Пользовательский профиль хранит:
- `users.full_name`, `users.email`, `users.username` — редактируемые данные аккаунта;
- `users.resume` — полный текст резюме
- `user_skills.skill` — список извлечённых навыков

Логика сохранения:
- после анализа текста/PDF приложение сохраняет извлечённый текст резюме в БД через protected endpoint `/profile/resume`;
- после извлечения навыков система сохраняет список скиллов через `/profile/skills`;
- на странице профиля данные читаются обратно из БД;
- при отсутствии токена используется localStorage как fallback.

## Frontend страницы

Основные страницы приложения:
- `/login` — авторизация
- `/registration` — регистрация
- `/profile` — профиль с сохранённым резюме и навыками
- `/skill_analyzer` — вставка текста или загрузка PDF
- `/vacancies` — базовый поиск вакансий
- `/vacancies/recommendations` — рекомендации по сохранённому резюме
- `/courses` — заглушка для раздела курсов
- `/learning_path_generator` — заглушка для генератора учебного пути

## Разработка

Запуск frontend локально:

```bash
cd services/frontend
npm install
npm run dev
```

Запуск backend-сервисов локально:

```bash
cd services/auth_service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

```bash
cd services/job_service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

```bash
cd services/skill_analyzer
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

## Примечания

- В проекте предусмотрены заглушки для ещё не реализованных разделов интерфейса.
- Текущая логика синхронизации профиля в первую очередь ориентирована на авторизованного пользователя.
- Для продакшн-окружения стоит отдельно настроить переменные окружения, миграции и безопасное хранение секретов.

## Статус проекта

Проект находится в активной разработке и реализует базовый цикл:
1. регистрация / авторизация;
2. загрузка резюме;
3. извлечение навыков;
4. хранение профиля в БД;
5. вакансий и рекомендации;
6. личный профиль пользователя.

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

