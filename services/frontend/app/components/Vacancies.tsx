'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { authFetch } from '@/app/lib/auth';

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
                authFetch('/api/job_service/recommendations_from_text', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ resume: resume }),
                }).then(res => res.json()).then(data => {
                    setVacancies(data);
                    setLoading(false);
                });
            } else if (file){
                const formData = new FormData();
                formData.append('file', file);
                authFetch('/api/job_service/recommendations_from_pdf', {
                    method: 'POST',
                    body: formData,
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
            <h1 className="text-2xl text-gray-900 font-bold mb-6">Вакансии</h1>
            {vacancies &&
                <div className="grid gap-4">
                    {vacancies.map(vacancy => (
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
                        <div className="flex gap-4 text-sm text-gray-500">
                            <span>{vacancy.area}</span>
                            <span className="font-medium text-green-600">{vacancy.salary}</span>
                        </div>
                    </Link>
                    ))}
                </div>
            }
        </div>
    );
}