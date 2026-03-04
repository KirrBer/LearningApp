FROM python:3.11-slim 

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
 
WORKDIR /skill_analyzer
 
COPY ./requirements.txt . 

RUN pip install -r requirements.txt
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch
 
COPY . . 

ENV PYTHONPATH=/skill_analyzer:/skill_analyzer/..

COPY ./entrypoint.sh .
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
 
CMD ["uvicorn", "skill_analyzer.main:app", "--host", "0.0.0.0", "--port", "8000"]