import { createSlice } from '@reduxjs/toolkit';
import { RootState } from '..';

export interface Supplier {
  id: string;
  name: string;
  description: string;
  domains: ('energy' | 'water' | 'waste' | 'biodiversity')[];
  regionsServed: ('wallonie' | 'flandre' | 'bruxelles')[];
  address: string;
  postalCode: string;
  city: string;
  contactEmail: string;
  contactPhone: string;
  website: string | null;
  vatNumber: string;
  rating: number | null;
  verified: boolean;
  active: boolean;
}

interface SuppliersState {
  loading: boolean;
  error: string | null;
  suppliers: Supplier[];
}

const initialState: SuppliersState = {
  loading: false,
  error: null,
  suppliers: [
    {
      id: 'supplier-1',
      name: 'EcoSolar Belgique',
      description: 'Installation de panneaux solaires et solutions photovoltaïques pour particuliers et entreprises.',
      domains: ['energy'],
      regionsServed: ['wallonie', 'bruxelles'],
      address: 'Rue de l\'Innovation 45',
      postalCode: '4000',
      city: 'Liège',
      contactEmail: 'contact@ecosolar.be',
      contactPhone: '+32 4 123 45 67',
      website: 'https://www.ecosolar.be',
      vatNumber: 'BE0123456789',
      rating: 4.8,
      verified: true,
      active: true
    },
    {
      id: 'supplier-2',
      name: 'ThermoConfort',
      description: 'Spécialistes en isolation thermique, audit énergétique et pompes à chaleur.',
      domains: ['energy'],
      regionsServed: ['wallonie'],
      address: 'Avenue Thermique 23',
      postalCode: '5000',
      city: 'Namur',
      contactEmail: 'info@thermoconfort.be',
      contactPhone: '+32 81 234 567',
      website: 'https://www.thermoconfort.be',
      vatNumber: 'BE0234567891',
      rating: 4.6,
      verified: true,
      active: true
    },
    {
      id: 'supplier-3',
      name: 'AquaSave',
      description: 'Solutions pour l\'économie d\'eau: récupération d\'eau de pluie, systèmes économes et audits.',
      domains: ['water'],
      regionsServed: ['wallonie', 'bruxelles', 'flandre'],
      address: 'Waterstraat 78',
      postalCode: '6700',
      city: 'Arlon',
      contactEmail: 'contact@aquasave.be',
      contactPhone: '+32 63 345 678',
      website: 'https://www.aquasave.be',
      vatNumber: 'BE0345678912',
      rating: 4.5,
      verified: true,
      active: true
    },
    {
      id: 'supplier-4',
      name: 'ÉcoRénov',
      description: 'Entreprise spécialisée dans la rénovation durable et l\'amélioration de l\'efficacité énergétique.',
      domains: ['energy'],
      regionsServed: ['wallonie'],
      address: 'Rue de la Rénovation 56',
      postalCode: '4800',
      city: 'Verviers',
      contactEmail: 'info@ecorenov.be',
      contactPhone: '+32 87 456 789',
      website: 'https://www.ecorenov.be',
      vatNumber: 'BE0456789123',
      rating: 4.7,
      verified: true,
      active: true
    },
    {
      id: 'supplier-5',
      name: 'BioConstruct',
      description: 'Construction et rénovation écologique avec matériaux biosourcés et techniques durables.',
      domains: ['energy', 'water'],
      regionsServed: ['wallonie', 'bruxelles'],
      address: 'Rue Verte 89',
      postalCode: '1348',
      city: 'Louvain-la-Neuve',
      contactEmail: 'contact@bioconstruct.be',
      contactPhone: '+32 10 567 890',
      website: 'https://www.bioconstruct.be',
      vatNumber: 'BE0567891234',
      rating: 4.9,
      verified: true,
      active: true
    }
  ],
};

const suppliersSlice = createSlice({
  name: 'suppliers',
  initialState,
  reducers: {},
});

export const selectSuppliers = (state: RootState) => state.suppliers.suppliers;
export const selectSuppliersLoading = (state: RootState) => state.suppliers.loading;
export const selectSuppliersError = (state: RootState) => state.suppliers.error;

export default suppliersSlice.reducer;
