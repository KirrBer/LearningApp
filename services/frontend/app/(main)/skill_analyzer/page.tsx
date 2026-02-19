'use client';

import { useState } from 'react';

export default function SkillForm() {
  const [resume, setResume] = useState('');
  const [skills, setSkills] = useState<Array<string>>([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch('/api/skill_analyzer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: resume })
      });
    
      const data = await res.json();
      const jsn = JSON.parse(data)
      setSkills(jsn.message || []);
      console.log(skills)
      
    
    } catch (error) {
        console.error('Error:', error);
      }
    setLoading(false);
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={resume}
          onChange={(e) => setResume(e.target.value)}
          placeholder="Вставьте текст резюме..."
          className="w-full h-64 p-4 border rounded-lg focus:ring-2 focus:ring-blue-500"
          required
        />
        
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Извлечение...' : 'Извлечь навыки'}
        </button>
      </form>

      {skills?.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-3">Навыки:</h3>
          <div className="flex flex-wrap gap-2">
            {skills.map((skill, i) => (
              <span
                key={i}
                className="bg-gray-100 px-3 py-1 rounded-full text-sm"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}