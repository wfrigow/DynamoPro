import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '..';

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
    // Audit data fields
    auditData?: {
      lastUpdated: string;
      // Profile data
      userType?: string;
      region?: string;
      // Consumption data
      electricityUsage?: number;
      gasUsage?: boolean;
      gasConsumption?: number;
      // Property data
      propertyType?: string;
      area?: number;
      constructionYear?: number;
      insulationStatus?: string;
    };
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
  },
};

const profileSlice = createSlice({
  name: 'profile',
  initialState,
  reducers: {
    updateProfile(state, action: PayloadAction<Partial<ProfileState['profile']>>) {
      if (state.profile) {
        state.profile = {
          ...state.profile,
          ...action.payload,
        };
      }
    },
  },
});

export const { updateProfile } = profileSlice.actions;

export const selectProfile = (state: RootState) => state.profile.profile;
export const selectProfileLoading = (state: RootState) => state.profile.loading;
export const selectProfileError = (state: RootState) => state.profile.error;

export default profileSlice.reducer;
