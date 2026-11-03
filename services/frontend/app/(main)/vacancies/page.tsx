'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { authFetch } from '@/app/lib/auth';

interface Vacancy {
    id: number;
    name: string;
    employer: string;
    salary: string | null;
    area: string | null;
}

interface VacancyResponse {
    vacancies?: Vacancy[];
    currentPage?: number;
    totalPages?: number;
}

export default function VacancyListPage() {
    const [vacancies, setVacancies] = useState<Vacancy[]>([]);
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const loadVacancies = async () => {
            try {
                setLoading(true);
                setError('');

                const response = await authFetch('/api/job_service/vacancies?page=1', {
                    method: 'GET',
                });

                if (!response.ok) {
                    throw new Error('Ошибка загрузки вакансий');
                }

                const data = (await response.json()) as VacancyResponse;
                const items = Array.isArray(data.vacancies) ? data.vacancies : [];
                setVacancies(items);
            } catch (err) {
                console.error(err);
                setError('Не удалось загрузить список вакансий. Попробуйте позже.');
            } finally {
                setLoading(false);
            }
        };

        loadVacancies();
    }, []);

    const filteredVacancies = useMemo(() => {
        const query = search.trim().toLowerCase();
        if (!query) return vacancies;

        return vacancies.filter((vacancy) => {
            const text = `${vacancy.name} ${vacancy.employer} ${vacancy.area ?? ''}`.toLowerCase();
            return text.includes(query);
        });
    }, [vacancies, search]);

    if (loading) {
        return <div className="container mx-auto p-6">Загрузка вакансий...</div>;
    }

    if (error) {
        return <div className="container mx-auto p-6 text-red-600">{error}</div>;
    }

    return (
        <div className="container mx-auto p-6">
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Поиск вакансий</h1>
                <input
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="Введите вакансию, компанию или город"
                    className="w-full rounded-lg border border-gray-300 px-4 py-3 text-base outline-none focus:border-blue-500"
                />
            </div>

            {filteredVacancies.length === 0 ? (
                <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-8 text-center text-gray-600">
                    По вашему запросу вакансии не найдены.
                </div>
            ) : (
                <div className="grid gap-4">
                    {filteredVacancies.map((vacancy) => (
                        <Link
                            key={vacancy.id}
                            href={`/vacancies/${vacancy.id}`}
                            className="block rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition hover:shadow-md"
                        >
                            <div className="mb-2 flex items-start justify-between gap-4">
                                <h2 className="text-xl font-semibold text-gray-900">{vacancy.name}</h2>
                                {vacancy.salary && (
                                    <span className="whitespace-nowrap font-medium text-green-600">{vacancy.salary}</span>
                                )}
                            </div>
                            <p className="mb-2 text-gray-700">{vacancy.employer}</p>
                            <div className="text-sm text-gray-500">
                                <span>{vacancy.area ?? 'Регион не указан'}</span>
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}
