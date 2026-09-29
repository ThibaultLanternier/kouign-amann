export const API_BASE_URL = 'http://localhost:8000';

export interface HeapInfo {
  heap_id: string;
  description: string | null;
  start_date: string;
  end_date: string;
  picture_count: number;
  heap_year: number;
  heap_type: string;
}

export interface HeapDescription extends HeapInfo {
  picture_hashes: string[];
}

interface HeapPicturesResponse {
  heap_id: string;
  picture_hashes: string[];
}

const HEAP_TYPE_LABELS: Record<string, string> = {
  GROUPED: 'Groupé',
  NOT_GROUPED: 'Non groupé',
  OTHER: 'Autres',
};

const getJson = async <T>(path: string): Promise<T> => {
  const response = await fetch(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch ${path}: ${response.statusText}`);
  }

  return response.json();
};

export const fetchHeaps = (): Promise<HeapDescription[]> => getJson('/heaps');

export const fetchHeapInfo = (heapId: string): Promise<HeapInfo> =>
  getJson(`/heap/${encodeURIComponent(heapId)}/info`);

export const fetchHeapPictureHashes = async (heapId: string): Promise<string[]> => {
  const data = await getJson<HeapPicturesResponse>(`/heap/${encodeURIComponent(heapId)}/pictures`);
  return data.picture_hashes;
};

export const pictureUrl = (hash: string): string =>
  `${API_BASE_URL}/picture/${encodeURIComponent(hash)}`;

export const thumbnailUrl = (hash: string, size = 400): string =>
  `${API_BASE_URL}/picture/${encodeURIComponent(hash)}/thumbnail?size=${size}`;

export const heapTypeLabel = (heapType: string): string =>
  HEAP_TYPE_LABELS[heapType] ?? heapType;

const formatDate = (isoDate: string): string =>
  new Date(isoDate).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

export const formatPeriod = (startDate: string, endDate: string): string => {
  const start = formatDate(startDate);
  const end = formatDate(endDate);

  return start === end ? start : `Du ${start} au ${end}`;
};
