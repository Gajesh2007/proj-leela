import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import {
  HomeIcon,
  SparklesIcon,
  MagnifyingGlassIcon,
  CubeTransparentIcon,
  UsersIcon,
  ArrowTrendingUpIcon,
  Cog6ToothIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Generate', href: '/generate', icon: SparklesIcon },
  { name: 'Explorer', href: '/explorer', icon: MagnifyingGlassIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'Thinking Explorer', href: '/quantum-canvas', icon: CubeTransparentIcon },
  { name: 'Multi-Agent', href: '/multi-agent', icon: UsersIcon },
  { name: 'Creative Spiral', href: '/creative-spiral', icon: ArrowTrendingUpIcon },
];

const Sidebar = () => {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  
  // Only show the sidebar with active state after client-side hydration
  useEffect(() => {
    setMounted(true);
  }, []);
  
  return (
    <aside className="w-64 bg-white/90 border-r border-slate-100 h-[calc(100vh-4rem)] sticky top-16 hidden md:block shadow-soft-sm">
      <div className="mt-6 px-4">
        {mounted ? (
          <nav className="space-y-1">
            {navigation.map((item) => {
              const isActive = router.pathname === item.href;
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`
                    group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200
                    ${isActive 
                      ? 'bg-primary/10 text-primary-dark shadow-soft-sm'
                      : 'text-text hover:bg-slate-50 hover:text-primary-dark'}
                  `}
                >
                  <item.icon
                    className={`
                      mr-3 h-5 w-5 transition-colors
                      ${isActive ? 'text-primary-dark' : 'text-text-light group-hover:text-primary-dark'}
                    `}
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        ) : (
          <div className="space-y-1">
            {navigation.map((item) => (
              <div
                key={item.name}
                className="group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg text-text"
              >
                <item.icon
                  className="mr-3 h-5 w-5 text-text-light"
                  aria-hidden="true"
                />
                {item.name}
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div className="px-4 mt-8">
        <div className="text-xs font-medium text-text-light uppercase tracking-wider mb-3">Utilities</div>
        {mounted ? (
          <Link
            href="/settings"
            className={`
              group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200
              ${router.pathname === '/settings'
                ? 'bg-primary/10 text-primary-dark shadow-soft-sm'
                : 'text-text hover:bg-slate-50 hover:text-primary-dark'}
            `}
          >
            <Cog6ToothIcon
              className={`
                mr-3 h-5 w-5 transition-colors
                ${router.pathname === '/settings' ? 'text-primary-dark' : 'text-text-light group-hover:text-primary-dark'}
              `}
              aria-hidden="true"
            />
            Settings
          </Link>
        ) : (
          <div className="group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg text-text">
            <Cog6ToothIcon
              className="mr-3 h-5 w-5 text-text-light"
              aria-hidden="true"
            />
            Settings
          </div>
        )}
      </div>
      
      <div className="absolute bottom-0 w-full p-4 border-t border-slate-100">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-highlight-dark rounded-full animate-pulse mr-2"></div>
            <span className="text-xs text-text-light font-medium">System Active</span>
          </div>
          <span className="text-xs text-text-light font-medium">v1.0.0</span>
        </div>
        <div className="text-xs text-text-light mt-1">
          Project Leela 2025
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;