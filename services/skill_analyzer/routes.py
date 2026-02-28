from fastapi import APIRouter, Body, File, UploadFile
from utils import extract_skills_from_text, extract_skills_from_pdf, find_courses
from schemas import TextRequest


router = APIRouter()

@router.post("/extract_skills_from_text", summary="Получить список навыков из полученного текста")
async def get_skills(data: TextRequest=Body()):
    skills = extract_skills_from_text(data.text)
    response = await find_courses(skills)
    return response

@router.post("/extract_skills_from_pdf", summary="Получить список навыков из полученного pdf")
async def get_skills_from_pdf(file: UploadFile = File(...)):
    skills = await extract_skills_from_pdf(file)
    response = await find_courses(skills)
    return response