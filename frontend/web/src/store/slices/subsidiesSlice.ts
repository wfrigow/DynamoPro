import { createSlice } from '@reduxjs/toolkit';
import { RootState } from '..';

export interface Subsidy {
  id: string;
  name: string;
  provider: string;
  description: string;
  domains: ('energy' | 'water' | 'waste' | 'biodiversity')[];
  maxAmount: number | null;
  percentage: number | null;
  conditions: string;
  documentationUrl: string;
  applicationProcess: string;
  expirationDate: string | null;
  active: boolean;
}

export interface SubsidyApplication {
  id: string;
  subsidyId: string;
  subsidyName: string;
  status: 'draft' | 'submitted' | 'pending' | 'approved' | 'rejected';
  submissionDate: string | null;
  responseDate: string | null;
  amountRequested: number;
  amountApproved: number | null;
}

interface SubsidiesState {
  loading: boolean;
  error: string | null;
  subsidies: Subsidy[];
  applications: SubsidyApplication[];
}

const initialState: SubsidiesState = {
  loading: false,
  error: null,
  subsidies: [
    {
      id: 'subsidy-1',
      name: 'Prime Energie - Isolation Toiture',
      provider: 'Région Wallonne',
      description: 'Prime pour l\'isolation thermique du toit ou des combles dans une habitation existante.',
      domains: ['energy'],
      maxAmount: 2000,
      percentage: 35,
      conditions: 'Le coefficient de résistance thermique R doit être ≥ 4,5 m²K/W. Les travaux doivent être réalisés par un entrepreneur enregistré.',
      documentationUrl: 'https://energie.wallonie.be/fr/prime-isolation-du-toit.html',
      applicationProcess: 'Demande en ligne via le portail Energie de la Région Wallonne.',
      expirationDate: null,
      active: true
    },
    {
      id: 'subsidy-2',
      name: 'Prime Energie - Pompe à Chaleur',
      provider: 'Région Wallonne',
      description: 'Prime pour l\'installation d\'une pompe à chaleur pour le chauffage ou combiné eau chaude sanitaire.',
      domains: ['energy'],
      maxAmount: 4000,
      percentage: 30,
      conditions: 'La pompe à chaleur doit respecter des exigences minimales de performance. L\'installation doit être réalisée par un installateur certifié.',
      documentationUrl: 'https://energie.wallonie.be/fr/prime-pompe-a-chaleur.html',
      applicationProcess: 'Demande en ligne via le portail Energie de la Région Wallonne.',
      expirationDate: null,
      active: true
    },
    {
      id: 'subsidy-3',
      name: 'Prime Energie - Panneaux Photovoltaïques',
      provider: 'Région Wallonne',
      description: 'Prime pour l\'installation de panneaux photovoltaïques pour la production d\'électricité.',
      domains: ['energy'],
      maxAmount: 1500,
      percentage: 20,
      conditions: 'L\'installation doit être réalisée par un installateur certifié. Les panneaux doivent avoir un rendement minimal.',
      documentationUrl: 'https://energie.wallonie.be/fr/prime-photovoltaique.html',
      applicationProcess: 'Demande en ligne via le portail Energie de la Région Wallonne.',
      expirationDate: null,
      active: true
    },
    {
      id: 'subsidy-4',
      name: 'Primes Rénovation - Audit Énergétique',
      provider: 'Région Wallonne',
      description: 'Prime pour la réalisation d\'un audit énergétique par un auditeur agréé.',
      domains: ['energy'],
      maxAmount: 900,
      percentage: 70,
      conditions: 'L\'audit doit être réalisé par un auditeur agréé PAE (Procédure d\'Avis Énergétique).',
      documentationUrl: 'https://energie.wallonie.be/fr/audit-energetique.html',
      applicationProcess: 'Demande en ligne via le portail Energie de la Région Wallonne.',
      expirationDate: null,
      active: true
    },
    {
      id: 'subsidy-5',
      name: 'Prime Eau - Récupération Eau de Pluie',
      provider: 'Région Wallonne',
      description: 'Prime pour l\'installation d\'un système de récupération et d\'utilisation de l\'eau de pluie.',
      domains: ['water'],
      maxAmount: 1000,
      percentage: 25,
      conditions: 'La citerne doit avoir une capacité minimale de 5000 litres et être raccordée à au moins un WC ou un lave-linge.',
      documentationUrl: 'https://environnement.wallonie.be/eau/prime-eau-pluie.html',
      applicationProcess: 'Demande auprès de la commune ou de l\'intercommunale compétente.',
      expirationDate: null,
      active: true
    }
  ],
  applications: [
    {
      id: 'app-1',
      subsidyId: 'subsidy-1',
      subsidyName: 'Prime Energie - Isolation Toiture',
      status: 'approved',
      submissionDate: '2025-03-15',
      responseDate: '2025-04-02',
      amountRequested: 1800,
      amountApproved: 1650
    },
    {
      id: 'app-2',
      subsidyId: 'subsidy-3',
      subsidyName: 'Prime Energie - Panneaux Photovoltaïques',
      status: 'pending',
      submissionDate: '2025-04-28',
      responseDate: null,
      amountRequested: 1200,
      amountApproved: null
    },
    {
      id: 'app-3',
      subsidyId: 'subsidy-5',
      subsidyName: 'Prime Eau - Récupération Eau de Pluie',
      status: 'draft',
      submissionDate: null,
      responseDate: null,
      amountRequested: 800,
      amountApproved: null
    }
  ],
};

const subsidiesSlice = createSlice({
  name: 'subsidies',
  initialState,
  reducers: {},
});

export const selectSubsidies = (state: RootState) => state.subsidies.subsidies;
export const selectSubsidyApplications = (state: RootState) => state.subsidies.applications;
export const selectSubsidiesLoading = (state: RootState) => state.subsidies.loading;
export const selectSubsidiesError = (state: RootState) => state.subsidies.error;

export default subsidiesSlice.reducer;
