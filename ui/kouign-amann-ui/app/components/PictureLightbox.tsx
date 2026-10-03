'use client';

/* eslint-disable @next/next/no-img-element */

import { useEffect } from 'react';
import { pictureUrl } from '@/app/lib/api';

interface PictureLightboxProps {
  hashes: string[];
  index: number;
  onClose: () => void;
  onNavigate: (index: number) => void;
}

export default function PictureLightbox({ hashes, index, onClose, onNavigate }: PictureLightboxProps) {
  const hasPrevious = index > 0;
  const hasNext = index < hashes.length - 1;

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      } else if (event.key === 'ArrowLeft' && hasPrevious) {
        onNavigate(index - 1);
      } else if (event.key === 'ArrowRight' && hasNext) {
        onNavigate(index + 1);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [index, hasPrevious, hasNext, onClose, onNavigate]);

  const navButtonClass =
    'absolute top-1/2 -translate-y-1/2 h-12 w-12 rounded-full bg-white/10 text-2xl text-white hover:bg-white/20 transition-colors';

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/90"
      onClick={onClose}
    >
      <img
        src={pictureUrl(hashes[index])}
        alt={`Photo ${index + 1} sur ${hashes.length}`}
        className="max-h-screen max-w-full object-contain p-4"
        onClick={(event) => event.stopPropagation()}
      />

      <button
        aria-label="Fermer"
        onClick={onClose}
        className="absolute top-4 right-4 h-10 w-10 rounded-full bg-white/10 text-xl text-white hover:bg-white/20 transition-colors"
      >
        ×
      </button>

      {hasPrevious && (
        <button
          aria-label="Photo précédente"
          onClick={(event) => {
            event.stopPropagation();
            onNavigate(index - 1);
          }}
          className={`${navButtonClass} left-4`}
        >
          ‹
        </button>
      )}

      {hasNext && (
        <button
          aria-label="Photo suivante"
          onClick={(event) => {
            event.stopPropagation();
            onNavigate(index + 1);
          }}
          className={`${navButtonClass} right-4`}
        >
          ›
        </button>
      )}

      <p className="absolute bottom-4 left-1/2 -translate-x-1/2 text-sm text-zinc-300">
        {index + 1} / {hashes.length}
      </p>
    </div>
  );
}
