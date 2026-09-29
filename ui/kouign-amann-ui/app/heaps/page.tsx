'use client';

/* eslint-disable @next/next/no-img-element */

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  HeapDescription,
  fetchHeaps,
  formatPeriod,
  heapTypeLabel,
  thumbnailUrl,
} from '@/app/lib/api';

interface YearGroup {
  year: number;
  heaps: HeapDescription[];
}

const groupHeapsByYear = (heaps: HeapDescription[]): YearGroup[] => {
  const groups = new Map<number, HeapDescription[]>();

  for (const heap of heaps) {
    const yearHeaps = groups.get(heap.heap_year) ?? [];
    yearHeaps.push(heap);
    groups.set(heap.heap_year, yearHeaps);
  }

  return Array.from(groups.entries())
    .sort(([yearA], [yearB]) => yearB - yearA)
    .map(([year, yearHeaps]) => ({
      year,
      heaps: yearHeaps.sort((a, b) => b.start_date.localeCompare(a.start_date)),
    }));
};

export default function HeapsPage() {
  const [yearGroups, setYearGroups] = useState<YearGroup[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHeaps()
      .then((heaps) => setYearGroups(groupHeapsByYear(heaps)))
      .catch((err) => setError(err instanceof Error ? err.message : 'Une erreur est survenue'))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-zinc-50 font-sans dark:bg-black">
      <main className="mx-auto w-full max-w-6xl px-6 py-10 space-y-10">
        <h1 className="text-3xl font-semibold text-black dark:text-zinc-50">
          Tas de photos
        </h1>

        {isLoading && (
          <p className="text-zinc-600 dark:text-zinc-400">Chargement...</p>
        )}

        {error && (
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-700 dark:text-red-400 text-sm">{error}</p>
          </div>
        )}

        {!isLoading && !error && yearGroups.length === 0 && (
          <p className="text-zinc-600 dark:text-zinc-400">Aucun tas de photos sauvegardé</p>
        )}

        {yearGroups.map(({ year, heaps }) => (
          <section key={year} className="space-y-4">
            <h2 className="text-2xl font-semibold text-black dark:text-zinc-50">
              {year}
              <span className="ml-3 text-sm font-normal text-zinc-500">
                {heaps.length} tas
              </span>
            </h2>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {heaps.map((heap) => (
                <HeapCard key={heap.heap_id} heap={heap} />
              ))}
            </div>
          </section>
        ))}
      </main>
    </div>
  );
}

function HeapCard({ heap }: { heap: HeapDescription }) {
  return (
    <article className="flex flex-col overflow-hidden rounded-lg border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <div className="grid grid-cols-2 gap-0.5 bg-zinc-200 dark:bg-zinc-800">
        {heap.picture_hashes.map((hash) => (
          <img
            key={hash}
            src={thumbnailUrl(hash, 300)}
            alt=""
            loading="lazy"
            className="aspect-square w-full object-cover bg-zinc-100 dark:bg-zinc-900"
          />
        ))}
      </div>

      <div className="flex flex-1 flex-col gap-2 p-4">
        <h3 className="font-medium text-black dark:text-zinc-50">
          {heap.description || 'Sans description'}
        </h3>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          {formatPeriod(heap.start_date, heap.end_date)}
        </p>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          {heap.picture_count} photo(s) · {heapTypeLabel(heap.heap_type)}
        </p>

        <Link
          href={`/heaps/${heap.heap_id}`}
          className="mt-auto inline-flex h-10 items-center justify-center rounded-lg bg-blue-600 px-4 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
        >
          Voir le détail
        </Link>
      </div>
    </article>
  );
}
