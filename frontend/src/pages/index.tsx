import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Image from 'next/image';
import { motion } from 'framer-motion';
import { ArrowRightIcon, ArrowPathIcon, BoltIcon, BeakerIcon, SparklesIcon, LightBulbIcon, SunIcon, MoonIcon } from '@heroicons/react/24/outline';
import ActivityFeed from '../components/dashboard/ActivityFeed';
import MetricsPanel from '../components/dashboard/MetricsPanel';
import RecentIdeasPanel from '../components/dashboard/RecentIdeasPanel';
import CreativeStatePanel from '../components/dashboard/CreativeStatePanel';

export default function Home() {
  return (
    <>
      <Head>
        <title>Project Leela | Creative Intelligence</title>
        <meta name="description" content="Project Leela - A meta-creative intelligence system" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="gradient-card"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
              <div>
                <h2 className="text-3xl font-heading font-semibold bg-gradient-to-r from-primary to-spiritual text-transparent bg-clip-text mb-1">Creative Dashboard</h2>
                <p className="text-text-light">Explore innovative <span className="font-script text-accent-dark">creativity</span></p>
              </div>
              <span className="badge-highlight flex items-center self-start">
                <span className="animate-pulse mr-1.5 h-2 w-2 rounded-full bg-highlight-dark"></span>
                System Active
              </span>
            </div>
            
            <p className="text-text mb-8 max-w-3xl">
              Welcome to Leela, a meta-creative intelligence system designed to generate truly innovative outputs that transcend conventional thinking through structured exploration of improbable ideas.
            </p>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <Link href="/generate" className="feature-card flex items-center justify-between p-5 group">
                <div className="flex">
                  <div className="mr-4 icon-container">
                    <SparklesIcon className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-heading text-lg text-text-dark mb-1 group-hover:text-primary transition-colors">Generate Ideas</h3>
                    <p className="text-sm text-text-light">Create innovative, novel outputs</p>
                  </div>
                </div>
                <ArrowRightIcon className="w-5 h-5 text-primary opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
              </Link>
              
              <Link href="/explorer" className="feature-card flex items-center justify-between p-5 group">
                <div className="flex">
                  <div className="mr-4 icon-container">
                    <LightBulbIcon className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-heading text-lg text-text-dark mb-1 group-hover:text-primary transition-colors">Explore Concepts</h3>
                    <p className="text-sm text-text-light">Browse generated ideas</p>
                  </div>
                </div>
                <ArrowRightIcon className="w-5 h-5 text-primary opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
              </Link>
            </div>
          </motion.div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <MetricsPanel />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <CreativeStatePanel />
            </motion.div>
          </div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <RecentIdeasPanel />
          </motion.div>
        </div>
        
        <div className="space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <ActivityFeed />
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="card"
          >
            <h3 className="text-xl font-heading mb-6 flex items-center">
              <span className="p-1.5 rounded-full bg-accent/10 text-accent-dark mr-3">
                <ArrowPathIcon className="w-5 h-5" />
              </span>
              Creative Workflows
            </h3>
            
            <div className="space-y-4">
              {[
                { name: 'Disruptor', description: 'Challenge assumptions', icon: BoltIcon, color: 'bg-primary/10 text-primary-dark' },
                { name: 'Connector', description: 'Link distant domains', icon: ArrowPathIcon, color: 'bg-secondary/10 text-secondary-dark' },
                { name: 'Dialectic', description: 'Multi-perspective synthesis', icon: SunIcon, color: 'bg-accent/10 text-accent-dark' },
                { name: 'Meta-Synthesis', description: 'Combined approaches', icon: MoonIcon, color: 'bg-spiritual/10 text-spiritual-dark' },
              ].map((workflow) => (
                <div key={workflow.name} className="flex items-center p-3 rounded-xl border border-slate-100 hover:bg-slate-50 hover:border-slate-200 transition-all cursor-pointer">
                  <span className={`p-2 rounded-full ${workflow.color} mr-3`}>
                    <workflow.icon className="w-4 h-4" />
                  </span>
                  <div>
                    <h4 className="font-heading text-sm font-medium text-text-dark">{workflow.name}</h4>
                    <p className="text-xs text-text-light">{workflow.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </>
  );
}