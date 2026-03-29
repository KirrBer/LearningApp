import Link from 'next/link';


interface Vacancy {
    id: number;
    name: string;
    employer: string;
    salary: string | null;
    area: string | null;
}

async function getVacancies(page: number = 1) {
  const baseUrl = 'http://nginx:80';
  const res = await fetch(
    `${baseUrl}/api/job_service/vacancies?page=${page}`,
    { cache: 'no-store' }
  );
  
  if (!res.ok) {
    throw new Error('Ошибка загрузки вакансий');
  }
  
  return res.json();
}



export default async function VacanciesPage({ searchParams }: { searchParams: Promise<{ page?: string }> }) {
  const page = parseInt((await searchParams).page || '1');
  const data = await getVacancies(page);
  
  return (
      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Вакансии</h1>
        
        <div className="grid gap-4 mb-8">
          {data.vacancies.map((vacancy: Vacancy) => (
            <Link 
                href={`/vacancies/${vacancy.id}`} 
                key={vacancy.id} 
                className="border rounded-lg p-4 hover:shadow-md"
                target="_blank"
                rel="noopener noreferrer"
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
        
        {data.totalPages > 1 && (
          <div className="flex justify-center gap-2">
            {data.currentPage > 1 && (
              <Link
                href={`/vacancies?page=${data.currentPage - 1}`}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Назад
              </Link>
            )}
            
            <span className="px-4 py-2 text-gray-600">
              Страница {data.currentPage} из {data.totalPages}
            </span>
            
            {data.currentPage < data.totalPages && (
              <Link
                href={`/vacancies?page=${data.currentPage + 1}`}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Вперёд
              </Link>
            )}
          </div>
        )}
      </div>
  );
}