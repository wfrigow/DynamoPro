/**
 * Types communs pour les API du projet DynamoPro
 * Ce fichier centralise les interfaces partagées entre les différents services
 */

// Types génériques pour les réponses d'API
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ErrorResponse {
  detail: string;
  code?: string;
  errors?: Record<string, string[]>;
}

// Types pour l'authentification
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  roles: string[];
  created_at: string;
  last_login: string | null;
}

// Types pour les documents
export interface Document {
  id: string;
  name: string;
  description: string;
  type: string;
  required: boolean;
  format: string[];
}

// Types pour les applications de subventions
export interface ApplicationBase {
  id: string;
  subsidy_id: string;
  user_id: string;
  status: ApplicationStatus;
  created_at: string;
  updated_at: string;
}

export interface ApplicationCreate {
  subsidy_id: string;
  property_id?: string;
  project_id?: string;
  notes?: string;
}

export interface ApplicationResponse extends ApplicationBase {
  subsidy: {
    id: string;
    name: string;
    provider: string;
    max_amount: number | null;
    percentage: number | null;
  };
  documents: ApplicationDocument[];
  notes: ApplicationNote[];
  history: ApplicationHistory[];
  nextSteps: string[];
}

export interface ApplicationDocument {
  id: string;
  document_id: string;
  name: string;
  status: DocumentStatus;
  uploaded_at: string | null;
  file_url: string | null;
}

export interface ApplicationNote {
  id: string;
  date: string;
  author: string;
  authorType: 'user' | 'admin' | 'system';
  content: string;
}

export interface ApplicationHistory {
  id: string;
  date: string;
  status: ApplicationStatus;
  description: string;
}

// Énumérations
export enum ApplicationStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  PROCESSING = 'processing',
  ADDITIONAL_INFO = 'additional_info',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  PAID = 'paid',
  CANCELLED = 'cancelled'
}

export enum DocumentStatus {
  PENDING = 'pending',
  UPLOADED = 'uploaded',
  VALIDATED = 'validated',
  REJECTED = 'rejected'
}
