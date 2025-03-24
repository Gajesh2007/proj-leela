# Project Leela Frontend

A quantum-inspired visualization interface for Project Leela, a meta-creative intelligence system designed to generate shocking, novel outputs that transcend conventional thinking.

## Overview

This frontend provides an intuitive and visually engaging interface for interacting with the Leela API. It includes:

- Dashboard showing system activity and metrics
- Idea generation interface with various creative workflows
- Idea explorer for browsing and filtering generated concepts
- Quantum canvas for visualizing conceptual networks
- Multi-agent observatory to view dialectic processes
- Creative spiral visualization

## Tech Stack

- React with Next.js
- TypeScript for type safety
- Tailwind CSS for styling
- Framer Motion for animations
- D3.js and Three.js for visualizations
- React Force Graph for network visualizations

## Getting Started

### Prerequisites

- Node.js 14+ and npm/yarn
- Leela backend running (see main project README)

### Installation

1. Install dependencies:

```bash
cd frontend
npm install
# or
yarn install
```

2. Configure environment variables:

Create a `.env.local` file in the frontend directory with the following content:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Replace the URL with your backend API endpoint if different.

### Development

Run the development server:

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### Building for Production

```bash
npm run build
# or
yarn build
```

Then start the production server:

```bash
npm run start
# or
yarn start
```

## Backend Connection

The frontend connects to the backend through API services located in `src/services/api.ts`. The API service handles all API calls to the backend and provides interfaces for all API endpoints.

## State Management

Global state is managed through React Context in `src/services/LeelaContext.tsx`. This contains:

- API data (frameworks, domains)
- Generated ideas
- System metrics
- Creative state information

## Visualization Components

- **Quantum Canvas**: Visualizes concept networks using force-directed graphs
- **Multi-Agent Observatory**: Shows dialectic processes between multiple perspectives
- **Creative Spiral**: Visualizes the meta-creative spiral process

## Developer Notes

- API calls are mocked if the backend is not available (development mode)
- The quantum visualization uses WebGL and may not work in all browsers
- For best experience, use Chrome or Firefox