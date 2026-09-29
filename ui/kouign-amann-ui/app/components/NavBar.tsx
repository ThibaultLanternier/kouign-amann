'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const LINKS = [
  { href: '/', label: 'Sauvegarde' },
  { href: '/heaps', label: 'Tas de photos' },
];

export default function NavBar() {
  const pathname = usePathname();

  const isActive = (href: string) =>
    href === '/' ? pathname === '/' : pathname.startsWith(href);

  return (
    <nav className="w-full border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-black">
      <div className="mx-auto flex max-w-6xl items-center gap-6 px-6 h-14">
        <span className="font-semibold text-black dark:text-zinc-50">Kouign-Amann</span>
        {LINKS.map(({ href, label }) => (
          <Link
            key={href}
            href={href}
            className={`text-sm transition-colors ${
              isActive(href)
                ? 'text-blue-600 dark:text-blue-400 font-medium'
                : 'text-zinc-600 hover:text-black dark:text-zinc-400 dark:hover:text-zinc-50'
            }`}
          >
            {label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
