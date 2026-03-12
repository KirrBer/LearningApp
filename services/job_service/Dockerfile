FROM python:3.11-slim 

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
 
WORKDIR /job_service
 
COPY ./requirements.txt . 

RUN pip install -r requirements.txt
 
COPY . . 

ENV PYTHONPATH=/job_service:/job_service/..
 
CMD ["uvicorn", "job_service.main:app", "--host", "0.0.0.0", "--port", "8000"]