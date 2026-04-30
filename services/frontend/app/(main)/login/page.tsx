"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Ошибка входа. Проверьте данные.");
        return;
      }

      localStorage.setItem("accessToken", data.access_token);
      localStorage.setItem("refreshToken", data.refresh_token);
      router.push("/");
    } catch (err) {
      setError("Серверная ошибка. Повторите попытку позже.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md bg-white shadow-md rounded-xl p-8">
        <h1 className="text-2xl font-semibold mb-4 text-center">Вход</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Имя пользователя</span>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              type="text"
              required
              className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">Пароль</span>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              required
              className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </label>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-blue-600 px-4 py-3 text-white font-semibold hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {loading ? "Вход..." : "Войти"}
          </button>
        </form>

        <div className="mt-6 text-sm text-slate-600 text-center">
          <span>Нет аккаунта? </span>
          <Link href="/registration" className="text-blue-600 hover:underline">
            Зарегистрируйтесь
          </Link>
        </div>
      </div>
    </main>
  );
}
