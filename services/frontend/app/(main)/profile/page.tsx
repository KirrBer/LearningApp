export default function ProfilePage() {
    return (
        <div className="mx-auto max-w-3xl rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
            <h1 className="mb-4 text-3xl font-bold text-gray-900">Профиль</h1>
            <p className="mb-6 text-gray-600">
                Здесь будет отображаться информация о пользователе, сохранённые данные и персональные рекомендации.
            </p>

            <div className="space-y-4 rounded-xl bg-gray-50 p-5">
                <div>
                    <p className="text-sm text-gray-500">Статус</p>
                    <p className="text-lg font-medium text-gray-900">В разработке</p>
                </div>
                <div>
                    <p className="text-sm text-gray-500">Следующий шаг</p>
                    <p className="text-lg font-medium text-gray-900">Подключить данные пользователя и редактирование профиля</p>
                </div>
            </div>
        </div>
    );
}