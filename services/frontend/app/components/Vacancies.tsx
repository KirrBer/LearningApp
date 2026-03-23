'use client';

import { useState, useEffect } from 'react';

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

interface VacanciesProps {
  resume: string;
}

export function Vacancies({ resume }: VacanciesProps) {
    const [vacancies, setVacancies] = useState<Array<Vacancy>>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        try {
        fetch('/api/job_service/recommendations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resume: resume })
        }).then(res => res.json())
        .then(data => {
            setVacancies(data);
            setLoading(false);
        });
        } catch (error) {
            console.error('Error:', error);
        }
    }, [resume]);

    if (loading) return <div className="text-center py-8">Loading...</div>;

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-6">Вакансии</h1>
            {vacancies &&
                <div className="grid gap-4">
                    {vacancies.map(vacancy => (
                    <div key={vacancy.id} className="border rounded-lg p-4 hover:shadow-md">
                        <h2 className="text-xl font-semibold">{vacancy.name}</h2>
                        <p className="text-gray-600">Работодатель: {vacancy.employer}</p>
                        <div className="flex gap-4 mt-2 text-sm text-gray-500">
                            <span>Адрес: {vacancy.area}</span>
                            <span>Зарплата: {vacancy.salary}</span>
                        </div>
                    </div>
                    ))}
                </div>
            }
        </div>
    );
}