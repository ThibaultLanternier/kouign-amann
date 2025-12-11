'use client';

import { useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';

interface ListPictureJobResult {
  status: string;
  result: string[];
  count: number;
  error?: string | null;
}

export default function Home() {
  const [folderPath, setFolderPath] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [totalImages, setTotalImages] = useState(0);
  const [currentImage, setCurrentImage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [completedHashes, setCompletedHashes] = useState<string[]>([]);

  const pollPictureList = async (pictureListId: string): Promise<string[]> => {
    const maxAttempts = 60;
    const pollInterval = 1000;

    for (let i = 0; i < maxAttempts; i++) {
      const response = await fetch(`${API_BASE_URL}/picture-list/${pictureListId}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch picture list: ${response.statusText}`);
      }

      const result: ListPictureJobResult = await response.json();

      if (result.status === 'completed') {
        return result.result;
      }

      if (result.status === 'failed') {
        throw new Error(result.error || 'Job failed');
      }

      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }

    throw new Error('Timeout waiting for picture list');
  };

  const backupPicture = async (path: string): Promise<string> => {
    const response = await fetch(`${API_BASE_URL}/picture`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ path, strict_mode: false }),
    });

    if (!response.ok) {
      throw new Error(`Failed to backup picture: ${response.statusText}`);
    }

    const data = await response.json();
    return data.hash;
  };

  const handleProcessFolder = async () => {
    if (!folderPath.trim()) {
      setError('Veuillez entrer un chemin de dossier');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setProgress(0);
    setTotalImages(0);
    setCompletedHashes([]);

    try {
      // Step 1: Create picture list job
      const listResponse = await fetch(`${API_BASE_URL}/picture-list`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ path: folderPath }),
      });

      if (!listResponse.ok) {
        throw new Error(`Failed to create picture list: ${listResponse.statusText}`);
      }

      const { picture_list_id } = await listResponse.json();

      // Step 2: Poll for results
      const imagePaths = await pollPictureList(picture_list_id);

      setTotalImages(imagePaths.length);

      if (imagePaths.length === 0) {
        setError('Aucune image trouvée dans ce dossier');
        setIsProcessing(false);
        return;
      }

      // Step 3: Backup each image
      const hashes: string[] = [];
      for (let i = 0; i < imagePaths.length; i++) {
        const imagePath = imagePaths[i];
        setCurrentImage(imagePath);

        try {
          const hash = await backupPicture(imagePath);
          hashes.push(hash);
          setCompletedHashes(prev => [...prev, hash]);
          setProgress(((i + 1) / imagePaths.length) * 100);
        } catch (err) {
          console.error(`Failed to backup ${imagePath}:`, err);
        }
      }

      setCurrentImage('');
      alert(`Sauvegarde terminée! ${hashes.length}/${imagePaths.length} images sauvegardées avec succès.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-center py-32 px-16 bg-white dark:bg-black">
        <div className="w-full max-w-md space-y-6">
          <h1 className="text-3xl font-semibold text-center text-black dark:text-zinc-50">
            Kouign-Amann Backup
          </h1>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                Chemin du dossier
              </label>
              <input
                id="folder-path"
                type="text"
                value={folderPath}
                onChange={(e) => setFolderPath(e.target.value)}
                disabled={isProcessing}
                placeholder="/chemin/vers/vos/images"
                className="w-full px-4 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-zinc-900 dark:text-zinc-100"
              />
              <p className="text-xs text-zinc-500 dark:text-zinc-500 mt-1">
                Entrez le chemin absolu du dossier contenant vos images
              </p>
            </div>

            <button
              onClick={handleProcessFolder}
              disabled={isProcessing}
              className="w-full h-12 px-5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-zinc-400 disabled:cursor-not-allowed transition-colors"
            >
              {isProcessing ? 'Traitement en cours...' : 'Démarrer la sauvegarde'}
            </button>

            {error && (
              <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-red-700 dark:text-red-400 text-sm">{error}</p>
              </div>
            )}

            {isProcessing && totalImages > 0 && (
              <div className="space-y-3">
                <div className="space-y-1">
                  <div className="flex justify-between text-sm text-zinc-600 dark:text-zinc-400">
                    <span>Progression</span>
                    <span>{Math.round(progress)}%</span>
                  </div>
                  <div className="w-full h-4 bg-zinc-200 dark:bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-600 transition-all duration-300 ease-out"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <p className="text-sm text-zinc-600 dark:text-zinc-400">
                    {completedHashes.length} / {totalImages} images sauvegardées
                  </p>
                </div>

                {currentImage && (
                  <div className="p-3 bg-zinc-100 dark:bg-zinc-900 rounded-lg">
                    <p className="text-xs text-zinc-600 dark:text-zinc-400 truncate">
                      En cours: {currentImage}
                    </p>
                  </div>
                )}
              </div>
            )}

            {!isProcessing && completedHashes.length > 0 && (
              <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <p className="text-green-700 dark:text-green-400 text-sm font-medium">
                  Sauvegarde terminée avec succès!
                </p>
                <p className="text-green-600 dark:text-green-500 text-xs mt-1">
                  {completedHashes.length} image(s) sauvegardée(s)
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
