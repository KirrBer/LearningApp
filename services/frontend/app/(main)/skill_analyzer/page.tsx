'use client';

import { useState } from 'react';

export default function SkillForm() {
  interface Skill { name: string; course: string; }
  const [resume, setResume] = useState<string>('');
  const [skills, setSkills] = useState<Array<Skill>>([]);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    if (resume){
      try {
      const response = await fetch('/api/skill_analyzer/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: resume })
      });
    
      const data = await response.json();
      setSkills(data || []);
      
    
      } catch (error) {
        console.error('Error:', error);
      }
    } else if (file){
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('/api/skill_analyzer/file', {
          method: 'POST',
          body: formData,
        });
        const data = await response.json();
        setSkills(data || []);
        setFile(null);
        // Очищаем input
        const fileInput = document.getElementById('pdf-upload') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      } catch (error) {
        console.error('Error:', error);
      }
    } 
    setLoading(false);
  }
  
    

  return (
    <div className="max-w-2xl mx-auto p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={resume}
          onChange={(e) => setResume(e.target.value)}
          placeholder="Вставьте текст резюме..."
          className="w-full h-64 p-4 border rounded-lg focus:ring-2 focus:ring-blue-500"
        />
        <input
        id="pdf-upload"
        accept=".pdf"
        type="file"
        onChange={handleFileChange}
        className="block w-full mb-4 text-sm text-gray-500
          file:mr-4 file:py-2 file:px-4
          file:rounded-full file:border-0
          file:text-sm file:font-semibold
          file:bg-blue-50 file:text-blue-700
          hover:file:bg-blue-100"
        />
        {file && (
        <p className="mt-4 text-sm text-gray-600">
          Выбран: {file.name}
        </p>
        )}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Извлечение...' : 'Извлечь навыки'}
        </button>
      </form>
      {!file && !resume && (
        <p className="mb-4 text-sm text-gray-600">
          Пожалуйста прикрепите файл или введите текст резюме
        </p>
      )}

      {skills?.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-3">Навыки:</h3>
          <div className="flex flex-wrap gap-2">
            {skills.map((skill, i) => 
            skill.course ? (
              <a
                key={i}
                className="bg-red-300 px-3 py-1 rounded-full text-sm"
                href={skill.course}
              >
                {skill.name}
              </a>
            ) : (
            <span
              key={i}
              className="bg-gray-100 px-3 py-1 rounded-full text-sm"
            >
              {skill.name}
            </span>
            )
          )}
          </div>
        </div>
      )}
    </div>
  );
}