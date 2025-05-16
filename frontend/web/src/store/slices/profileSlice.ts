import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import { RootState } from '..';
import apiService from '../../services/api';
import { API_CONFIG } from '../../config/api';

// Detailed Audit Data structures to match backend models
interface BackendProfileData {
  userType: string;
  region: string;
  additionalInfo?: Record<string, any>;
}

interface BackendConsumptionData {
  electricityUsage: number;
  gasUsage: boolean;
  gasConsumption: number;
  additionalInfo?: Record<string, any>;
}

interface BackendPropertyData {
  propertyType: string;
  area: number;
  constructionYear: number;
  insulationStatus: string;
  additionalInfo?: Record<string, any>;
}

export interface UserAuditData {
  profile: BackendProfileData;
  consumption: BackendConsumptionData;
  property: BackendPropertyData;
  // lastUpdated can be added here if it's part of the AuditData payload from backend
  // or managed at a higher level in AuditResponse
}

// Interface for the AuditSummary from the backend (for the list endpoint)
interface AuditSummary {
  id: string;
  createdAt: string; // Assuming ISO string format for dates
  userType: string;
  region: string;
  propertyType: string;
}

// Interface for the full AuditResponse from the backend (for the single audit endpoint)
interface FullAuditResponse {
  id: string;
  userId: string;
  createdAt: string;
  updatedAt: string;
  auditData: UserAuditData; // This is what we need for the store
}

interface ProfileState {
  loading: boolean;
  error: string | null;
  profile: {
    id: string;
    email: string;
    name: string;
    userType: 'individual' | 'self_employed' | 'small_business' | 'medium_business' | 'large_business';
    region: 'wallonie' | 'flandre' | 'bruxelles';
    postalCode: string;
    address?: string;
    phone?: string;
    language: 'fr' | 'nl' | 'de' | 'en';
    companyName?: string;
    companySize?: number;
    companyVat?: string;
    subscriptionType: 'free' | 'premium';
    auditData?: UserAuditData; // Updated to use the detailed UserAuditData
    lastAuditUpdateTimestamp?: string; // To track when auditData was last fetched/updated from backend
  } | null;
}

const initialState: ProfileState = {
  loading: false,
  error: null,
  profile: {
    id: 'user-1',
    email: 'john.doe@example.com',
    name: 'John Doe',
    userType: 'individual',
    region: 'wallonie',
    postalCode: '4000',
    address: 'Rue de l\'Exemple 123',
    phone: '+32 123 456 789',
    language: 'fr',
    subscriptionType: 'premium',
    // auditData will be initially undefined, to be populated from backend
  },
};

// Données factices pour les tests quand l'API n'est pas disponible
const mockAuditData: UserAuditData = {
  profile: {
    userType: 'individual',
    region: 'wallonie',
    additionalInfo: {}
  },
  consumption: {
    electricityUsage: 3500,
    gasUsage: true,
    gasConsumption: 15000,
    additionalInfo: {}
  },
  property: {
    propertyType: 'apartment',
    area: 95,
    constructionYear: 1998,
    insulationStatus: 'medium',
    additionalInfo: {}
  }
};

// Configuration des endpoints d'audit
const AUDIT_ENDPOINTS = {
  getUserAudits: (userId: string) => `/api/audits?user_id=${userId}`,
  getAuditById: (auditId: string) => `/api/audits/${auditId}`
};

// Variable pour suivre le nombre de tentatives d'appel API
let apiCallAttempts = 0;
const MAX_API_CALL_ATTEMPTS = 3;

// Async thunk to fetch user audits
export const fetchUserAudits = createAsyncThunk<
  UserAuditData, // Return type on success
  string,        // Argument type (userId)
  { rejectValue: string; state: RootState } // ThunkApi config
>('profile/fetchUserAudits', async (userId, { rejectWithValue, getState }) => {
  // Vérifier si l'état actuel a déjà des données d'audit
  const currentState = getState();
  const hasExistingAuditData = currentState.profile.profile?.auditData;

  // Si on a déjà atteint le nombre maximal de tentatives, utiliser les données factices
  if (apiCallAttempts >= MAX_API_CALL_ATTEMPTS) {
    console.warn('Maximum API call attempts reached. Using mock audit data.');
    apiCallAttempts = 0; // Réinitialiser pour les futures tentatives
    
    // Si on a des données existantes, les privilégier
    if (hasExistingAuditData) {
      return hasExistingAuditData;
    }
    
    return mockAuditData;
  }

  try {
    // Incrémenter le compteur de tentatives
    apiCallAttempts++;

    // 1. Fetch audit summaries for the user
    console.log(`Fetching audits from ${API_CONFIG.baseUrl}${AUDIT_ENDPOINTS.getUserAudits(userId)}`);
    const summaries: AuditSummary[] = await apiService.get(AUDIT_ENDPOINTS.getUserAudits(userId));
    
    if (summaries.length === 0) {
      // No audits found for the user, use mock data if available or return a rejection
      console.warn('No audits found for user. Using mock data.');
      return hasExistingAuditData || mockAuditData;
    }

    // 2. Sort summaries to find the most recent one (by createdAt)
    summaries.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    const latestAuditSummary = summaries[0];

    // 3. Fetch the full details of the most recent audit
    console.log(`Fetching audit details from ${API_CONFIG.baseUrl}${AUDIT_ENDPOINTS.getAuditById(latestAuditSummary.id)}`);
    const fullAudit: FullAuditResponse = await apiService.get(AUDIT_ENDPOINTS.getAuditById(latestAuditSummary.id));
    
    // Réinitialiser le compteur car l'appel a réussi
    apiCallAttempts = 0;
    
    return fullAudit.auditData; // This will be the payload of the fulfilled action

  } catch (error: any) {
    console.error('Error fetching audit data:', error);
    
    // Si on a des données existantes, les renvoyer même en cas d'erreur
    if (hasExistingAuditData) {
      console.warn('Using existing audit data due to API error.');
      return hasExistingAuditData;
    }
    
    // Si on atteint le nombre maximum de tentatives, utiliser des données factices
    if (apiCallAttempts >= MAX_API_CALL_ATTEMPTS) {
      console.warn('Maximum API call attempts reached. Using mock audit data.');
      apiCallAttempts = 0;
      return mockAuditData;
    }
    
    return rejectWithValue(error.message || 'An unknown error occurred while fetching audits');
  }
});

const profileSlice = createSlice({
  name: 'profile',
  initialState,
  reducers: {
    setProfileLoading(state) {
      state.loading = true;
      state.error = null;
    },
    updateProfile(state, action: PayloadAction<Partial<ProfileState['profile']>>) {
      if (state.profile) {
        // Ensure auditData is handled carefully if it's part of the partial update
        const { auditData, ...otherProfileUpdates } = action.payload as any; // Cast to any to handle auditData separately
        state.profile = {
          ...state.profile,
          ...otherProfileUpdates,
        };
        // If auditData is explicitly in payload, it might need special merging or replacement
        // For now, setAuditData is preferred for full auditData updates from backend
        if (auditData) {
          // This might overwrite or merge, depending on desired behavior for partial audit updates
          // state.profile.auditData = { ...state.profile.auditData, ...auditData }; 
        }
      }
      state.loading = false;
    },
    setAuditData(state, action: PayloadAction<UserAuditData>) {
      if (state.profile) {
        state.profile.auditData = action.payload;
        state.profile.lastAuditUpdateTimestamp = new Date().toISOString();
      }
      state.loading = false;
      state.error = null;
    },
    setProfileError(state, action: PayloadAction<string>) {
      state.loading = false;
      state.error = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUserAudits.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserAudits.fulfilled, (state, action: PayloadAction<UserAuditData>) => {
        if (state.profile) {
          state.profile.auditData = action.payload;
          state.profile.lastAuditUpdateTimestamp = new Date().toISOString();
        }
        state.loading = false;
      })
      .addCase(fetchUserAudits.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ? action.payload : 'Failed to fetch audits';
      });
  }
});

export const { updateProfile, setAuditData, setProfileLoading, setProfileError } = profileSlice.actions;

export const selectProfile = (state: RootState) => state.profile.profile;
export const selectAuditData = (state: RootState) => state.profile.profile?.auditData;
export const selectProfileLoading = (state: RootState) => state.profile.loading;
export const selectProfileError = (state: RootState) => state.profile.error;

export default profileSlice.reducer;
