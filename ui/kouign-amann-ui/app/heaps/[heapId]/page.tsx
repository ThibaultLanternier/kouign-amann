'use client';

/* eslint-disable @next/next/no-img-element */

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import PictureLightbox from '@/app/components/PictureLightbox';
import {
  HeapInfo,
  fetchHeapInfo,
  fetchHeapPictureHashes,
  formatPeriod,
  heapTypeLabel,
  thumbnailUrl,
} from '@/app/lib/api';

export default function HeapDetailPage() {
  const { heapId } = useParams<{ heapId: string }>();
  const [heapInfo, setHeapInfo] = useState<HeapInfo | null>(null);
  const [pictureHashes, setPictureHashes] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  useEffect(() => {
    Promise.all([fetchHeapInfo(heapId), fetchHeapPictureHashes(heapId)])
      .then(([info, hashes]) => {
        setHeapInfo(info);
        setPictureHashes(hashes);
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Une erreur est survenue'))
      .finally(() => setIsLoading(false));
  }, [heapId]);

  return (
    <div className="min-h-screen bg-zinc-50 font-sans dark:bg-black">
      <main className="mx-auto w-full max-w-6xl px-6 py-10 space-y-6">
        <Link
          href="/heaps"
          className="text-sm text-blue-600 hover:underline dark:text-blue-400"
        >
          ← Retour aux tas de photos
        </Link>

        {isLoading && (
          <p className="text-zinc-600 dark:text-zinc-400">Chargement...</p>
        )}

        {error && (
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-700 dark:text-red-400 text-sm">{error}</p>
          </div>
        )}

        {heapInfo && (
          <header className="space-y-1">
            <h1 className="text-3xl font-semibold text-black dark:text-zinc-50">
              {heapInfo.description || 'Sans description'}
            </h1>
            <p className="text-zinc-600 dark:text-zinc-400">
              {formatPeriod(heapInfo.start_date, heapInfo.end_date)}
            </p>
            <p className="text-sm text-zinc-500">
              {heapInfo.picture_count} photo(s) · {heapTypeLabel(heapInfo.heap_type)}
            </p>
          </header>
        )}

        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-6">
          {pictureHashes.map((hash, index) => (
            <button
              key={hash}
              onClick={() => setSelectedIndex(index)}
              className="overflow-hidden rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <img
                src={thumbnailUrl(hash, 300)}
                alt={`Photo ${index + 1}`}
                loading="lazy"
                className="aspect-square w-full object-cover bg-zinc-200 dark:bg-zinc-800 hover:opacity-80 transition-opacity"
              />
            </button>
          ))}
        </div>
      </main>

      {selectedIndex !== null && (
        <PictureLightbox
          hashes={pictureHashes}
          index={selectedIndex}
          onClose={() => setSelectedIndex(null)}
          onNavigate={setSelectedIndex}
        />
      )}
    </div>
  );
}
