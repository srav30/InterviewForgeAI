"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [jobDescription, setJobDescription] = useState("");
  const [resume, setResume] = useState("");
  const [question, setQuestion] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const canSubmit = jobDescription.trim() && resume.trim() && !loading;

  async function startInterview() {
    setLoading(true);
    setError(null);
    setQuestion(null);
    try {
      const res = await fetch(`${API_URL}/api/interview/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_description: jobDescription,
          resume,
        }),
      });
      if (!res.ok) {
        throw new Error(`Backend returned ${res.status}`);
      }
      const data: { question: string } = await res.json();
      setQuestion(data.question);
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Could not reach the backend. Is it running on port 8000?"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-1 flex-col items-center bg-zinc-50 px-6 py-12 font-sans dark:bg-zinc-950">
      <main className="w-full max-w-3xl">
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
            InterviewForge <span className="text-indigo-600">AI</span>
          </h1>
          <p className="mt-2 text-zinc-600 dark:text-zinc-400">
            Paste a job description and your resume to start a mock interview.
          </p>
        </header>

        <div className="grid gap-6 sm:grid-cols-2">
          <label className="flex flex-col gap-2">
            <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
              Job description
            </span>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={12}
              placeholder="Paste the job description here..."
              className="resize-y rounded-lg border border-zinc-300 bg-white p-3 text-sm text-zinc-900 shadow-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
            />
          </label>

          <label className="flex flex-col gap-2">
            <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
              Resume
            </span>
            <textarea
              value={resume}
              onChange={(e) => setResume(e.target.value)}
              rows={12}
              placeholder="Paste your resume here..."
              className="resize-y rounded-lg border border-zinc-300 bg-white p-3 text-sm text-zinc-900 shadow-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
            />
          </label>
        </div>

        <div className="mt-6 flex justify-center">
          <button
            onClick={startInterview}
            disabled={!canSubmit}
            className="rounded-full bg-indigo-600 px-8 py-3 text-sm font-semibold text-white shadow transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {loading ? "Preparing your interview..." : "Start interview"}
          </button>
        </div>

        {error && (
          <div className="mt-8 rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-800 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
            {error}
          </div>
        )}

        {question && (
          <div className="mt-8 rounded-xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-indigo-600">
              Interviewer
            </h2>
            <p className="text-lg leading-relaxed text-zinc-900 dark:text-zinc-100">
              {question}
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
