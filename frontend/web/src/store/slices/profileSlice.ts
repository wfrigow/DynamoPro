import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import { RootState } from '..';
import apiService from '../../services/api';

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

// Async thunk to fetch user audits
export const fetchUserAudits = createAsyncThunk<
  UserAuditData, // Return type on success
  string,        // Argument type (userId)
  { rejectValue: string; state: RootState } // ThunkApi config
>('profile/fetchUserAudits', async (userId, { rejectWithValue }) => {
  try {
    // 1. Fetch audit summaries for the user
    const summaries: AuditSummary[] = await apiService.get(`/audits?user_id=${userId}`);
    
    if (summaries.length === 0) {
      // No audits found for the user, this is not an error, but no data to set
      // We could potentially dispatch an action to clear existing audit data or set a specific state
      return rejectWithValue('No audits found for user.'); 
    }

    // 2. Sort summaries to find the most recent one (by createdAt)
    summaries.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    const latestAuditSummary = summaries[0];

    // 3. Fetch the full details of the most recent audit
    const fullAudit: FullAuditResponse = await apiService.get(`/audits/${latestAuditSummary.id}`);
    
    return fullAudit.auditData; // This will be the payload of the fulfilled action

  } catch (error: any) {
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
