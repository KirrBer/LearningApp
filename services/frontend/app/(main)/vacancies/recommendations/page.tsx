'use client';

import { Vacancies } from '@/app/components/Vacancies';

export default function SkillForm() {
    const resume = 'пишу код на python, знаю английский, умею работать с базами данных';
    return (
        <Vacancies resume={resume} file={null} />
    )
}