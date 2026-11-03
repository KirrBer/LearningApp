'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Vacancies } from '@/app/components/Vacancies';
import { getSavedResumeText } from '@/app/lib/resume';

export default function RecommendationsPage() {
    const [resume, setResume] = useState<string | null>(null);

    useEffect(() => {
        setResume(getSavedResumeText());
    }, []);

    if (!resume) {
        return (
            <div className="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-8 text-center">
                <h2 className="text-2xl font-semibold text-gray-900 mb-3">Рекомендации по вакансиям</h2>
                <p className="mb-5 text-gray-600">
                    Для подбора вакансий сначала сохраните или вставьте своё резюме в разделе анализа навыков.
                </p>
                <Link
                    href="/skill_analyzer"
                    className="inline-flex rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
                >
                    Перейти к анализу резюме
                </Link>
            </div>
        );
    }

    return <Vacancies resume={resume} file={null} />;
}