import '../styles/globals.css'
import type { AppProps } from 'next/app'
import { Inter, Orbitron, JetBrains_Mono } from 'next/font/google'
import { QueryClient, QueryClientProvider } from 'react-query'
import Layout from '../components/layout/Layout'
import { LeelaProvider } from '../services/LeelaContext'
import { useEffect } from 'react'

// Properly initialize A-Frame for force-graph components
if (typeof window !== 'undefined') {
  // Import A-Frame only on client-side
  require('aframe');
}

// Initialize fonts
const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
})

const orbitron = Orbitron({ 
  subsets: ['latin'],
  variable: '--font-orbitron',
})

const jetbrainsMono = JetBrains_Mono({ 
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
})

// Create a client
const queryClient = new QueryClient()

export default function App({ Component, pageProps }: AppProps) {
  return (
    <main className={`${inter.variable} ${orbitron.variable} ${jetbrainsMono.variable}`}>
      <QueryClientProvider client={queryClient}>
        <LeelaProvider>
          <Layout>
            <Component {...pageProps} />
          </Layout>
        </LeelaProvider>
      </QueryClientProvider>
    </main>
  )
}