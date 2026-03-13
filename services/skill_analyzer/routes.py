from fastapi import APIRouter, Body, File, UploadFile
from skill_analyzer.utils import extract_skills_from_text, extract_text_from_pdf, find_courses
from skill_analyzer.schemas import TextRequest, SkillResponse
from skill_analyzer.kafka import kafka_manager
from typing import List
from fastapi.concurrency import run_in_threadpool


router = APIRouter()

@router.post("/extract_skills_from_text", summary="Получить список навыков из полученного текста")
async def get_skills(data: TextRequest=Body(...)) -> List[SkillResponse]:
    skills = await run_in_threadpool(extract_skills_from_text, data.text)
    response = await find_courses(skills)
    kafka_manager.producer.send('extraction_results', value=skills)
    return response

@router.post("/extract_skills_from_pdf", summary="Получить список навыков из полученного pdf")
async def get_skills_from_pdf(file: UploadFile = File(...)) -> List[SkillResponse]:
    text = await extract_text_from_pdf(file)
    skills = await run_in_threadpool(extract_skills_from_text, text)
    response = await find_courses(skills)
    kafka_manager.producer.send('extraction_results', value=skills)
    return response