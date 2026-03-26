import { notFound } from 'next/navigation';

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

interface VacancyPageProps {
    params: {
        id: string;
    };
}

async function getVacancy(id: string): Promise<Vacancy> { 
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://nginx:80';
    const res = await fetch(`${baseUrl}/api/job_service/vacancies/${id}`, {
        method: 'GET',
        cache: 'no-store',
    });

    if (res.status === 404) {
        notFound();
    }

    if (!res.ok) {
        throw new Error(`Ошибка при загрузке вакансии: ${res.status}`);
    }

    const data = await res.json();
    return data as Vacancy;
}

export default async function VacancyPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = await params;
    const vacancy = await getVacancy(id);

    return (
        <div className="container mx-auto p-6">
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
                <div dangerouslySetInnerHTML={{ __html: vacancy.description }} />

                
            </div>
        </div>
    );
}