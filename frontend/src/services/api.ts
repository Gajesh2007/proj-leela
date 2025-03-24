import { UUID } from 'crypto';

// Types based on backend models
export interface ShockProfile {
  novelty_score: number;
  contradiction_score: number;
  impossibility_score: number;
  utility_potential: number;
  expert_rejection_probability: number;
  composite_shock_value: number;
}

export interface ThinkingStep {
  id: string;
  framework: string;
  reasoning_process: string;
  insights_generated: string[];
  token_usage: number;
}

export interface CreativeIdeaRequest {
  domain: string;
  problem_statement: string;
  impossibility_constraints?: string[];
  contradiction_requirements?: string[];
  shock_threshold?: number;
  thinking_budget?: number;
  creative_framework?: string;
}

export interface CreativeIdeaResponse {
  id: string;
  idea?: string;                 // Original field from API
  description?: string;          // Field from database
  framework?: string;            // Original field from API
  generative_framework?: string; // Field from database
  domain?: string;               // Domain of the idea if provided
  shock_metrics: ShockProfile;
  thinking_steps: ThinkingStep[];
  impossibility_elements?: string[]; // Elements identified as impossible
  contradiction_elements?: string[]; // Elements identified as contradictory
}

export interface DialecticIdeaRequest {
  domain: string;
  problem_statement: string;
  perspectives: string[];
  thinking_budget?: number;
}

export interface DialecticIdeaResponse {
  id: string;
  synthesized_idea: string;
  shock_metrics: ShockProfile;
  perspective_ideas: string[];
  thinking_steps: ThinkingStep[];
}

export interface MetaIdeaRequest {
  domain: string;
  problem_statement: string;
  workflow?: string;
  contexts?: Record<string, any>;
}

export interface Framework {
  id: string;
  name: string;
  description: string;
  is_custom?: boolean;
}

export interface DomainData {
  [key: string]: string[];
}

export interface PromptTemplate {
  name: string;
  content: string;
}

// API URL Configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// API Client
export class LeelaAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
    data?: any
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
    };

    const config: RequestInit = {
      method,
      headers,
      body: data ? JSON.stringify(data) : undefined,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error (${response.status}): ${errorText}`);
      }
      
      const result = await response.json();
      return result as T;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Creative Idea Generation
  async generateCreativeIdea(request: CreativeIdeaRequest): Promise<CreativeIdeaResponse> {
    return this.request<CreativeIdeaResponse>('/api/v1/ideas', 'POST', request);
  }

  // Dialectic Idea Generation
  async generateDialecticIdea(request: DialecticIdeaRequest): Promise<DialecticIdeaResponse> {
    return this.request<DialecticIdeaResponse>('/api/v1/dialectic', 'POST', request);
  }

  // Meta-Engine Idea Generation
  async generateMetaIdea(request: MetaIdeaRequest): Promise<any> {
    return this.request<any>('/api/v1/meta/idea', 'POST', request);
  }

  // Get Available Domains
  async getDomains(): Promise<{ domains: DomainData }> {
    return this.request<{ domains: DomainData }>('/api/v1/domains');
  }

  // Get Available Frameworks
  async getFrameworks(): Promise<{ frameworks: Framework[] }> {
    return this.request<{ frameworks: Framework[] }>('/api/v1/frameworks');
  }

  // Get Available Prompts
  async getPrompts(): Promise<{ prompts: string[] }> {
    return this.request<{ prompts: string[] }>('/api/v1/prompts');
  }
  
  // Get All Ideas
  async getAllIdeas(limit: number = 50, offset: number = 0): Promise<{ ideas: CreativeIdeaResponse[] }> {
    console.log(`Frontend API: Requesting all ideas with limit=${limit}, offset=${offset}`);
    try {
      const result = await this.request<{ ideas: CreativeIdeaResponse[] }>(`/api/v1/ideas?limit=${limit}&offset=${offset}`);
      console.log(`Frontend API: Received ${result.ideas.length} ideas from backend`);
      return result;
    } catch (error) {
      console.error('Frontend API: Error fetching ideas:', error);
      throw error;
    }
  }

  // Get Specific Prompt
  async getPrompt(promptName: string): Promise<PromptTemplate> {
    return this.request<PromptTemplate>(`/api/v1/prompts/${promptName}`);
  }

  // Create or Update Prompt
  async createOrUpdatePrompt(promptName: string, content: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(
      `/api/v1/prompts/${promptName}`,
      'POST',
      { content }
    );
  }

  // Delete Prompt
  async deletePrompt(promptName: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(
      `/api/v1/prompts/${promptName}`,
      'DELETE'
    );
  }

  // Health Check
  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health');
  }
}

// Create and export default instance
const api = new LeelaAPI();
export default api;