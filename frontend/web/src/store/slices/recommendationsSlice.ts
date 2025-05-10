import { createSlice } from '@reduxjs/toolkit';
import { RootState } from '..';

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  domain: 'energy' | 'water' | 'waste' | 'biodiversity';
  priorityScore: number;
  estimatedCostMin: number;
  estimatedCostMax: number;
  estimatedSavingsPerYear: number;
  estimatedRoiMonths: number;
  ecologicalImpactScore: number; // 1-10
  difficulty: number; // 1-10
  applicableSubsidies: string[];
  status: 'pending' | 'accepted' | 'rejected' | 'completed';
}

interface RecommendationsState {
  loading: boolean;
  error: string | null;
  recommendations: Recommendation[];
}

const initialState: RecommendationsState = {
  loading: false,
  error: null,
  recommendations: [
    {
      id: '1',
      title: 'Installation de panneaux solaires',
      description: 'Installation de panneaux photovoltaïques sur votre toit pour produire de l\'électricité et réduire votre facture énergétique.',
      domain: 'energy',
      priorityScore: 0.85,
      estimatedCostMin: 5000,
      estimatedCostMax: 15000,
      estimatedSavingsPerYear: 1200,
      estimatedRoiMonths: 60,
      ecologicalImpactScore: 9,
      difficulty: 7,
      applicableSubsidies: ['subsidy-1', 'subsidy-2', 'subsidy-3'],
      status: 'pending'
    },
    {
      id: '2',
      title: 'Isolation du toit/combles',
      description: 'Amélioration de l\'isolation du toit pour réduire les pertes de chaleur et économiser sur le chauffage.',
      domain: 'energy',
      priorityScore: 0.78,
      estimatedCostMin: 2000,
      estimatedCostMax: 8000,
      estimatedSavingsPerYear: 800,
      estimatedRoiMonths: 48,
      ecologicalImpactScore: 7,
      difficulty: 6,
      applicableSubsidies: ['subsidy-1', 'subsidy-4'],
      status: 'accepted'
    },
    {
      id: '3',
      title: 'Installation d\'un système de récupération d\'eau de pluie',
      description: 'Mise en place d\'un système de collecte et de stockage d\'eau de pluie pour usage non potable.',
      domain: 'water',
      priorityScore: 0.72,
      estimatedCostMin: 1500,
      estimatedCostMax: 5000,
      estimatedSavingsPerYear: 350,
      estimatedRoiMonths: 60,
      ecologicalImpactScore: 8,
      difficulty: 7,
      applicableSubsidies: ['subsidy-5'],
      status: 'pending'
    },
    {
      id: '4',
      title: 'Remplacement des ampoules par LED',
      description: 'Remplacement de toutes les ampoules traditionnelles ou halogènes par des LED basse consommation.',
      domain: 'energy',
      priorityScore: 0.68,
      estimatedCostMin: 100,
      estimatedCostMax: 500,
      estimatedSavingsPerYear: 120,
      estimatedRoiMonths: 12,
      ecologicalImpactScore: 6,
      difficulty: 2,
      applicableSubsidies: [],
      status: 'completed'
    },
    {
      id: '5',
      title: 'Installation de réducteurs de débit',
      description: 'Installation de réducteurs de débit sur les robinets et douches pour diminuer la consommation d\'eau.',
      domain: 'water',
      priorityScore: 0.65,
      estimatedCostMin: 50,
      estimatedCostMax: 150,
      estimatedSavingsPerYear: 150,
      estimatedRoiMonths: 6,
      ecologicalImpactScore: 6,
      difficulty: 2,
      applicableSubsidies: [],
      status: 'pending'
    }
  ],
};

const recommendationsSlice = createSlice({
  name: 'recommendations',
  initialState,
  reducers: {},
});

export const selectRecommendations = (state: RootState) => state.recommendations.recommendations;
export const selectRecommendationsLoading = (state: RootState) => state.recommendations.loading;
export const selectRecommendationsError = (state: RootState) => state.recommendations.error;

export default recommendationsSlice.reducer;
