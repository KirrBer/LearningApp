export default function CoursesPage() {
  return (
    <div className="mx-auto max-w-4xl rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
      <h1 className="mb-4 text-3xl font-bold text-gray-900">База курсов</h1>
      <p className="mb-6 text-gray-600">
        Здесь будет каталог курсов, фильтрация по темам и рекомендации по обучению.
      </p>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl bg-gray-50 p-5">
          <p className="text-sm text-gray-500">Раздел</p>
          <p className="text-lg font-semibold text-gray-900">Python</p>
        </div>
        <div className="rounded-xl bg-gray-50 p-5">
          <p className="text-sm text-gray-500">Раздел</p>
          <p className="text-lg font-semibold text-gray-900">Frontend</p>
        </div>
      </div>
    </div>
  );
}
