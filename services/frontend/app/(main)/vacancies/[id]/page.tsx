'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { authFetch } from '@/app/lib/auth';

interface Vacancy {
    id: number;
    name: string;
    description: string;
    employer: string;
    salary: string | null;
    employment: string | null;
    schedule: string | null;
    experience: string | null;
    area: string | null;
}

interface VacancyShort {
    id: number;
    name: string;
    employer: string;
    salary: string | null;
    area: string | null;
}

export default function VacancyPage() {
    const params = useParams();
    const id = params?.id as string | undefined;
    const [vacancy, setVacancy] = useState<Vacancy | null>(null);
    const [similarVacancies, setSimilarVacancies] = useState<VacancyShort[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!id) {
            setError('Вакансия не найдена');
            setLoading(false);
            return;
        }

        setLoading(true);
        setError('');

        authFetch(`/api/job_service/vacancies/${id}`, {
            method: 'GET',
        })
            .then((res) => {
                if (res.status === 404) {
                    throw new Error('notfound');
                }
                if (!res.ok) {
                    throw new Error('Ошибка при загрузке вакансии');
                }
                return res.json();
            })
            .then((data: Vacancy) => {
                setVacancy(data);
                return authFetch('/api/job_service/recommendations_from_text', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ resume: data.description }),
                });
            })
            .then((res) => {
                if (!res.ok) {
                    return [];
                }
                return res.json();
            })
            .then((similar: VacancyShort[]) => {
                setSimilarVacancies(similar || []);
            })
            .catch((err) => {
                if (err.message === 'notfound') {
                    setError('Вакансия не найдена');
                } else {
                    setError('Не удалось загрузить вакансию');
                }
            })
            .finally(() => setLoading(false));
    }, [id]);

    if (loading) {
        return <div className="container mx-auto p-6">Загрузка вакансии...</div>;
    }

    if (error) {
        return <div className="container mx-auto p-6 text-red-600">{error}</div>;
    }

    if (!vacancy) {
        return <div className="container mx-auto p-6 text-red-600">Вакансия не найдена</div>;
    }

    return (
        <div>
            <div className="container mx-auto p-6 w-3/4">
                <h1 className="text-3xl font-bold mb-4">{vacancy.name}</h1>
                <div className="bg-white shadow-md rounded-lg p-6">
                    <p className="text-xl font-semibold mb-2">Работодатель: {vacancy.employer}</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-lg text-gray-900 mb-4">
                        <div>
                            <span className="font-medium">Зарплата:</span> {vacancy.salary ?? 'не указана'}
                        </div>
                        <div>
                            <span className="font-medium">Тип занятости:</span> {vacancy.employment ?? 'не указано'}
                        </div>
                        <div>
                            <span className="font-medium">График:</span> {vacancy.schedule ?? 'не указано'}
                        </div>
                        <div>
                            <span className="font-medium">Требуемый опыт:</span> {vacancy.experience ?? 'не указан'}
                        </div>
                        <div>
                            <span className="font-medium">Регион:</span> {vacancy.area ?? 'не указан'}
                        </div>
                    </div>
                    <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: vacancy.description }} />
                </div>
            </div>
            {similarVacancies.length > 0 && (
                <div className="bg-gray-50 rounded-lg p-6 w-3/4 mx-auto mt-8">
                    <h2 className="text-2xl font-bold mb-4">Похожие вакансии</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {similarVacancies.map((similar) => (
                            Number(id) !== similar.id && (
                                <Link
                                    key={similar.id}
                                    href={`/vacancies/${similar.id}`}
                                    className="block bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow border border-gray-200 hover:border-blue-300"
                                >
                                    <h3 className="font-semibold text-lg mb-1 line-clamp-2">
                                        {similar.name}
                                    </h3>
                                    <p className="text-sm text-gray-600 mb-2">{similar.employer}</p>
                                    <div className="flex justify-between items-center text-sm">
                                        {similar.salary ? (
                                            <span className="text-green-600 font-medium">
                                                {similar.salary} ₽
                                            </span>
                                        ) : (
                                            <span className="text-gray-400">з/п не указана</span>
                                        )}
                                        {similar.area && (
                                            <span className="text-gray-500">{similar.area}</span>
                                        )}
                                    </div>
                                </Link>
                            )
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
