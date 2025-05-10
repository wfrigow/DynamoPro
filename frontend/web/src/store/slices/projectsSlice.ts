import { createSlice } from '@reduxjs/toolkit';
import { RootState } from '..';

export interface Project {
  id: string;
  userId: string;
  recommendationId: string;
  recommendationTitle: string;
  propertyId: string | null;
  supplierId: string | null;
  supplierName: string | null;
  status: 'planning' | 'in_progress' | 'completed' | 'cancelled';
  startDate: string | null;
  completionDate: string | null;
  actualCost: number | null;
  notes: string | null;
  verificationStatus: 'pending' | 'verified';
  verificationDate: string | null;
  verificationDocuments: string[];
  domain: 'energy' | 'water' | 'waste' | 'biodiversity';
  estimatedAnnualSavings: number;
  estimatedCo2Reduction: number;
  progress: number;
}

interface ProjectsState {
  loading: boolean;
  error: string | null;
  projects: Project[];
}

const initialState: ProjectsState = {
  loading: false,
  error: null,
  projects: [
    {
      id: 'project-1',
      userId: 'user-1',
      recommendationId: '1',
      recommendationTitle: 'Installation de panneaux solaires',
      propertyId: 'property-1',
      supplierId: 'supplier-1',
      supplierName: 'EcoSolar Belgique',
      status: 'completed',
      startDate: '2025-03-15',
      completionDate: '2025-04-10',
      actualCost: 12500,
      notes: 'Installation réussie de 12 panneaux solaires',
      verificationStatus: 'verified',
      verificationDate: '2025-04-15',
      verificationDocuments: ['doc-1', 'doc-2'],
      domain: 'energy',
      estimatedAnnualSavings: 1200,
      estimatedCo2Reduction: 2500,
      progress: 100
    },
    {
      id: 'project-2',
      userId: 'user-1',
      recommendationId: '2',
      recommendationTitle: 'Isolation du toit/combles',
      propertyId: 'property-1',
      supplierId: 'supplier-2',
      supplierName: 'ThermoConfort',
      status: 'in_progress',
      startDate: '2025-05-01',
      completionDate: null,
      actualCost: null,
      notes: 'Travaux d\'isolation du toit en cours',
      verificationStatus: 'pending',
      verificationDate: null,
      verificationDocuments: [],
      domain: 'energy',
      estimatedAnnualSavings: 800,
      estimatedCo2Reduction: 1500,
      progress: 60
    },
    {
      id: 'project-3',
      userId: 'user-1',
      recommendationId: '3',
      recommendationTitle: 'Installation d\'un système de récupération d\'eau de pluie',
      propertyId: 'property-1',
      supplierId: 'supplier-3',
      supplierName: 'AquaSave',
      status: 'planning',
      startDate: null,
      completionDate: null,
      actualCost: null,
      notes: 'Installation de récupération d\'eau de pluie planifiée',
      verificationStatus: 'pending',
      verificationDate: null,
      verificationDocuments: [],
      domain: 'water',
      estimatedAnnualSavings: 350,
      estimatedCo2Reduction: 800,
      progress: 10
    }
  ],
};

const projectsSlice = createSlice({
  name: 'projects',
  initialState,
  reducers: {},
});

export const selectProjects = (state: RootState) => state.projects.projects;
export const selectProjectsLoading = (state: RootState) => state.projects.loading;
export const selectProjectsError = (state: RootState) => state.projects.error;

export default projectsSlice.reducer;
