'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';

interface Vacancy {
    id: number;
    name: string;
    employer: string;
    salary: string | null;
    area: string | null;
}

interface VacanciesProps {
  resume: string | null;
  file: File | null;
}

export function Vacancies({ resume, file }: VacanciesProps) {
    const [vacancies, setVacancies] = useState<Array<Vacancy>>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        try {
            if (resume){
                fetch('/api/job_service/recommendations_from_text', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ resume: resume })
                }).then(res => res.json()).then(data => {
                    setVacancies(data);
                    setLoading(false);
                });
            } else if (file){
                const formData = new FormData();
                formData.append('file', file);
                fetch('/api/job_service/recommendations_from_pdf', {
                    method: 'POST',
                    body: formData
                }).then(res => res.json()).then(data => {
                    setVacancies(data);
                    setLoading(false);
                });
            }
        }catch (error) {
            console.error('Error:', error);
        }
    }, [resume, file]);

    if (loading) return <div className="text-center py-8">Loading...</div>;

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-6">Вакансии</h1>
            {vacancies &&
                <div className="grid gap-4">
                    {vacancies.map(vacancy => (
                    <Link href={`/vacancies/${vacancy.id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        key={vacancy.id} 
                        className="border rounded-lg p-4 hover:shadow-md"
                    >
                        <h2 className="text-xl font-semibold">{vacancy.name}</h2>
                        <p className="text-gray-600">Работодатель: {vacancy.employer}</p>
                        <div className="flex gap-4 mt-2 text-sm text-gray-500">
                            <span>Адрес: {vacancy.area}</span>
                            <span>Зарплата: {vacancy.salary}</span>
                        </div>
                    </Link>
                    ))}
                </div>
            }
        </div>
    );
}