'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { authFetch } from '@/app/lib/auth';
import { getSavedResumeText } from '@/app/lib/resume';

interface Vacancy {
    id: number;
    name: string;
    employer: string;
    salary: string | null;
    area: string | null;
}

interface VacanciesProps {
  resume?: string | null;
  file?: File | null;
}

export function Vacancies({ resume, file }: VacanciesProps) {
    const [vacancies, setVacancies] = useState<Array<Vacancy>>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');

    useEffect(() => {
        const effectiveResume = resume ?? getSavedResumeText();

        const loadRecommendations = async () => {
            try {
                setLoading(true);

                if (effectiveResume) {
                    const response = await authFetch('/api/job_service/recommendations_from_text', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ resume: effectiveResume }),
                    });

                    if (!response.ok) {
                        setVacancies([]);
                        return;
                    }

                    const data = await response.json();
                    setVacancies(Array.isArray(data) ? data : []);
                    return;
                }

                if (file) {
                    const formData = new FormData();
                    formData.append('file', file);

                    const response = await authFetch('/api/job_service/recommendations_from_pdf', {
                        method: 'POST',
                        body: formData,
                    });

                    if (!response.ok) {
                        setVacancies([]);
                        return;
                    }

                    const data = await response.json();
                    setVacancies(Array.isArray(data) ? data : []);
                    return;
                }

                setVacancies([]);
            } catch (error) {
                console.error('Error:', error);
                setVacancies([]);
            } finally {
                setLoading(false);
            }
        };

        loadRecommendations();
    }, [resume, file]);

    const visibleVacancies = vacancies.filter((vacancy) => {
        const query = search.trim().toLowerCase();
        if (!query) return true;

        const haystack = `${vacancy.name} ${vacancy.employer} ${vacancy.area ?? ''}`.toLowerCase();
        return haystack.includes(query);
    });

    if (loading) return <div className="text-center py-8">Загрузка рекомендаций...</div>;

    return (
        <div className="container mx-auto p-4">
            <div className="mb-6 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <h1 className="text-2xl text-gray-900 font-bold">Рекомендации вакансий</h1>
                {vacancies.length > 0 && (
                    <input
                        value={search}
                        onChange={(event) => setSearch(event.target.value)}
                        placeholder="Поиск по вакансии или компании"
                        className="w-full max-w-md rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-blue-500"
                    />
                )}
            </div>

            {!resume && !file && !getSavedResumeText() ? (
                <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-6 text-gray-600">
                    Вставьте или сохраните резюме в разделе анализа навыков, чтобы получить персональные рекомендации.
                </div>
            ) : visibleVacancies.length === 0 ? (
                <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-6 text-gray-600">
                    По вашему резюме не найдено подходящих вакансий.
                </div>
            ) : (
                <div className="grid gap-4">
                    {visibleVacancies.map(vacancy => (
                        <Link href={`/vacancies/${vacancy.id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            key={vacancy.id}
                            className="border rounded-lg p-4 hover:shadow-md"
                        >
                            <h2 className="text-xl font-semibold text-gray-900 mb-2">
                                {vacancy.name}
                            </h2>
                            <p className="text-gray-600 mb-2">{vacancy.employer}</p>
                            <div className="flex gap-4 text-sm text-gray-500 flex-wrap">
                                <span>{vacancy.area ?? 'Регион не указан'}</span>
                                <span className="font-medium text-green-600">{vacancy.salary ?? 'Зарплата не указана'}</span>
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}