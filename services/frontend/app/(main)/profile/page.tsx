'use client';

import { useEffect, useState } from 'react';
import { authFetch } from '@/app/lib/auth';
import {
  getSavedResumeText,
  getSavedSkills,
  loadResumeFromProfile,
  loadSkillsFromProfile,
  type SavedSkill,
} from '@/app/lib/resume';

interface UserProfile {
    email: string;
    username: string;
    full_name: string | null;
}

export default function ProfilePage() {
    const [resume, setResume] = useState<string>('');
    const [skills, setSkills] = useState<SavedSkill[]>([]);
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [isEditing, setIsEditing] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [profileError, setProfileError] = useState('');
    const [profileMessage, setProfileMessage] = useState('');

    useEffect(() => {
        const hydrateProfile = async () => {
            try {
                const response = await authFetch('/api/auth/profile');
                if (response.ok) {
                    setProfile(await response.json());
                }
            } catch {
                setProfileError('Не удалось загрузить данные профиля.');
            }

            const [profileResume, profileSkills] = await Promise.all([
                loadResumeFromProfile(),
                loadSkillsFromProfile(),
            ]);

            setResume(profileResume ?? getSavedResumeText() ?? '');

            const nextSkills = profileSkills.length > 0 ? profileSkills : getSavedSkills();
            setSkills(nextSkills);
        };

        hydrateProfile();
    }, []);

    const handleProfileSave = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        if (!profile) return;

        const formData = new FormData(event.currentTarget);
        setIsSaving(true);
        setProfileError('');
        setProfileMessage('');

        try {
            const response = await authFetch('/api/auth/profile', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    full_name: String(formData.get('full_name') ?? ''),
                    email: String(formData.get('email') ?? ''),
                    username: String(formData.get('username') ?? ''),
                }),
            });

            const data = await response.json();
            if (!response.ok) {
                setProfileError(data.detail || 'Не удалось сохранить данные профиля.');
                return;
            }

            setProfile(data);
            setIsEditing(false);
            setProfileMessage('Данные профиля сохранены.');
        } catch {
            setProfileError('Ошибка соединения. Попробуйте ещё раз.');
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="mx-auto max-w-5xl space-y-6 p-6">
            <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
                <h1 className="mb-3 text-3xl font-bold text-gray-900">Профиль</h1>
                <p className="text-gray-600">Личная карточка с сохранённым резюме и извлечёнными навыками.</p>
            </div>

            <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
                <div className="mb-5 flex items-center justify-between gap-4">
                    <h2 className="text-xl font-semibold text-gray-900">Данные пользователя</h2>
                    {profile && !isEditing && (
                        <button
                            type="button"
                            onClick={() => {
                                setProfileError('');
                                setProfileMessage('');
                                setIsEditing(true);
                            }}
                            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                        >
                            Редактировать
                        </button>
                    )}
                </div>

                {profile ? isEditing ? (
                    <form onSubmit={handleProfileSave} className="grid gap-4 sm:grid-cols-2">
                        <label className="block">
                            <span className="text-sm font-medium text-gray-700">Имя</span>
                            <input
                                name="full_name"
                                defaultValue={profile.full_name ?? ''}
                                maxLength={255}
                                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
                            />
                        </label>
                        <label className="block">
                            <span className="text-sm font-medium text-gray-700">Email</span>
                            <input
                                name="email"
                                type="email"
                                required
                                defaultValue={profile.email}
                                maxLength={255}
                                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
                            />
                        </label>
                        <label className="block sm:col-span-2">
                            <span className="text-sm font-medium text-gray-700">Имя пользователя</span>
                            <input
                                name="username"
                                required
                                minLength={3}
                                maxLength={100}
                                defaultValue={profile.username}
                                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
                            />
                        </label>
                        <div className="flex gap-3 sm:col-span-2">
                            <button
                                type="submit"
                                disabled={isSaving}
                                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                {isSaving ? 'Сохранение...' : 'Сохранить'}
                            </button>
                            <button
                                type="button"
                                onClick={() => setIsEditing(false)}
                                disabled={isSaving}
                                className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                            >
                                Отмена
                            </button>
                        </div>
                    </form>
                ) : (
                    <dl className="grid gap-4 sm:grid-cols-3">
                        <div>
                            <dt className="text-sm text-gray-500">Имя</dt>
                            <dd className="mt-1 font-medium text-gray-900">{profile.full_name || 'Не указано'}</dd>
                        </div>
                        <div>
                            <dt className="text-sm text-gray-500">Email</dt>
                            <dd className="mt-1 break-all font-medium text-gray-900">{profile.email}</dd>
                        </div>
                        <div>
                            <dt className="text-sm text-gray-500">Имя пользователя</dt>
                            <dd className="mt-1 font-medium text-gray-900">{profile.username}</dd>
                        </div>
                    </dl>
                ) : (
                    <p className="text-gray-600">Войдите в аккаунт, чтобы просматривать и редактировать данные пользователя.</p>
                )}

                {profileError && <p role="alert" className="mt-4 text-sm text-red-600">{profileError}</p>}
                {profileMessage && <p role="status" className="mt-4 text-sm text-green-700">{profileMessage}</p>}
            </section>

            <div className="grid gap-6 lg:grid-cols-[1.3fr_1fr]">
                <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
                    <h2 className="mb-4 text-xl font-semibold text-gray-900">Загруженное резюме</h2>

                    {resume ? (
                        <div className="whitespace-pre-wrap rounded-xl bg-gray-50 p-4 text-sm leading-7 text-gray-800">
                            {resume}
                        </div>
                    ) : (
                        <div className="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-6 text-gray-600">
                            Резюме ещё не добавлено. Вставьте текст или загрузите PDF на странице анализа навыков.
                        </div>
                    )}
                </div>

                <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
                    <h2 className="mb-4 text-xl font-semibold text-gray-900">Извлечённые скилы</h2>

                    {skills.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                            {skills.map((skill, index) =>
                                skill.course ? (
                                    <a
                                        key={`${skill.name}-${index}`}
                                        href={skill.course}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="rounded-full bg-red-300 px-3 py-1 text-sm font-medium text-gray-900 transition hover:bg-red-400"
                                    >
                                        {skill.name}
                                    </a>
                                ) : (
                                    <span
                                        key={`${skill.name}-${index}`}
                                        className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-800"
                                    >
                                        {skill.name}
                                    </span>
                                )
                            )}
                        </div>
                    ) : (
                        <div className="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-6 text-gray-600">
                            Пока нет извлечённых навыков.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}