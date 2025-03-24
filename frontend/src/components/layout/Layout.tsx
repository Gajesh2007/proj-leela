import React, { ReactNode } from 'react';
import Head from 'next/head';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gentle-gradient">
      <Head>
        <title>Leela | Meta-Creative Intelligence</title>
        <meta name="description" content="Leela - A meta-creative intelligence system designed to generate genuinely innovative, novel outputs that transcend conventional thinking." />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="relative">
        {/* Decorative blobs/gradients for subtle energy effects */}
        <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-gradient-radial from-primary/5 to-transparent opacity-70 -z-10 animate-pulse-slow"></div>
        <div className="absolute top-1/2 right-0 w-[400px] h-[400px] bg-gradient-radial from-spiritual/5 to-transparent opacity-50 -z-10 transform translate-x-1/3 animate-pulse-slow"></div>
        <div className="absolute bottom-0 left-1/3 w-[300px] h-[300px] bg-gradient-radial from-accent/5 to-transparent opacity-40 -z-10 animate-float"></div>
      </div>

      <Navbar />
      
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6 md:p-8 lg:p-10">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;