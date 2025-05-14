import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '..';
// Temporairement commenté jusqu'à ce que le service soit correctement configuré
// import authService, { LoginRequest, RegisterRequest, UserResponse } from '../services/AuthService';

// Types temporaires pour remplacer ceux importés
interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}

interface UserResponse {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
}

interface User {
  id: string;
  email: string;
  name: string;
  fullName: string;
  userType: string;
  isActive: boolean;
  isSuperuser: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Fonctions sécurisées pour accéder à localStorage
const getLocalStorageItem = (key: string): string | null => {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      return localStorage.getItem(key);
    }
    return null;
  } catch (e) {
    console.error('Error accessing localStorage:', e);
    return null;
  }
};

const setLocalStorageItem = (key: string, value: string): void => {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem(key, value);
    }
  } catch (e) {
    console.error('Error setting localStorage item:', e);
  }
};

const removeLocalStorageItem = (key: string): void => {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem(key);
    }
  } catch (e) {
    console.error('Error removing localStorage item:', e);
  }
};

const initialState: AuthState = {
  user: null,
  token: getLocalStorageItem('token'),
  isAuthenticated: !!getLocalStorageItem('token'),
  isLoading: false,
  error: null,
};

// Fonction pour convertir UserResponse en User
const mapUserResponseToUser = (userResponse: UserResponse): User => ({
  id: userResponse.id,
  email: userResponse.email,
  name: userResponse.firstName + ' ' + userResponse.lastName,
  fullName: userResponse.firstName + ' ' + userResponse.lastName,
  userType: userResponse.role,
  isActive: true,
  isSuperuser: false
});

// Async thunks for authentication
export const login = createAsyncThunk<
  { token: string; user: User },
  { username: string; password: string },
  { rejectValue: string }
>('auth/login', async (credentials, { rejectWithValue }) => {
  try {
    // Simulation de connexion réussie pour le développement
    const mockToken = 'mock-jwt-token-' + Date.now();
    const mockUser = {
      id: '1',
      email: credentials.username,
      name: 'Jean Dupont',
      fullName: 'Jean Dupont',
      userType: 'admin',
      isActive: true,
      isSuperuser: false
    };
    
    setLocalStorageItem('token', mockToken);
    
    return {
      token: mockToken,
      user: mockUser
    };
    
    // Code original commenté
    /*
    const { username, password } = credentials;
    const response = await authService.login({
      email: username,
      password
    });
    setLocalStorageItem('token', response.token);
    return {
      token: response.token,
      user: {
        id: response.user.id,
        email: response.user.email,
        fullName: response.user.full_name,
        userType: response.user.user_type,
        isActive: response.user.is_active,
        isSuperuser: response.user.is_superuser
      }
    };
    */
  } catch (error) {
    return rejectWithValue('Échec de la connexion. Veuillez vérifier vos identifiants.');
  }
});

export const register = createAsyncThunk<
  { token: string; user: User },
  { email: string; password: string; full_name: string },
  { rejectValue: string }
>('auth/register', async (userData, { rejectWithValue }) => {
  try {
    // Simulation d'inscription réussie pour le développement
    const mockToken = 'mock-jwt-token-' + Date.now();
    const mockUser = {
      id: '1',
      email: userData.email,
      name: userData.full_name,
      fullName: userData.full_name,
      userType: 'user',
      isActive: true,
      isSuperuser: false
    };
    
    setLocalStorageItem('token', mockToken);
    
    return {
      token: mockToken,
      user: mockUser
    };
    
    // Code original commenté
    /*
    const response = await authService.register({
      email: userData.email,
      password: userData.password,
      firstName: userData.full_name.split(' ')[0],
      lastName: userData.full_name.split(' ')[1] || ''
    });
    
    const loginResponse = await authService.login({
      email: userData.email,
      password: userData.password
    });
    
    setLocalStorageItem('token', loginResponse.token);
    
    return {
      token: loginResponse.token,
      user: {
        id: loginResponse.user.id,
        email: loginResponse.user.email,
        fullName: loginResponse.user.full_name,
        userType: loginResponse.user.user_type,
        isActive: loginResponse.user.is_active,
        isSuperuser: loginResponse.user.is_superuser
      }
    };
    */
  } catch (error) {
    return rejectWithValue('Échec de l\'inscription. Veuillez réessayer.');
  }
});

export const fetchCurrentUser = createAsyncThunk<
  User,
  void,
  { rejectValue: string }
>('auth/fetchCurrentUser', async (_, { rejectWithValue }) => {
  try {
    const token = getLocalStorageItem('token');
    if (!token) {
      return rejectWithValue('Token non trouvé');
    }
    
    // Simulation de récupération d'utilisateur pour le développement
    return {
      id: '1',
      email: 'jean.dupont@example.com',
      name: 'Jean Dupont',
      fullName: 'Jean Dupont',
      userType: 'admin',
      isActive: true,
      isSuperuser: false
    };
    
    // Code original commenté
    /*
    const userResponse = await authService.getCurrentUser(token);
    return mapUserResponseToUser(userResponse);
    */
  } catch (error: any) {
    removeLocalStorageItem('token');
    return rejectWithValue('Session expirée ou invalide');
  }
});

export const logout = createAsyncThunk('auth/logout', async () => {
  // Remove token from localStorage
  removeLocalStorageItem('token');
  return null;
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Login
    builder.addCase(login.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(login.fulfilled, (state, action: PayloadAction<{ user: User; token: string }>) => {
      state.isLoading = false;
      state.isAuthenticated = true;
      state.user = action.payload.user;
      state.token = action.payload.token;
    });
    builder.addCase(login.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
    
    // Register
    builder.addCase(register.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(register.fulfilled, (state, action: PayloadAction<{ user: User; token: string }>) => {
      state.isLoading = false;
      state.isAuthenticated = true;
      state.user = action.payload.user;
      state.token = action.payload.token;
    });
    builder.addCase(register.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
    
    // Fetch Current User
    builder.addCase(fetchCurrentUser.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(fetchCurrentUser.fulfilled, (state, action: PayloadAction<User>) => {
      state.isLoading = false;
      state.isAuthenticated = true;
      state.user = action.payload;
      // Le token est déjà dans le state via initialState ou login, pas besoin de le redéfinir ici
      // sauf si fetchCurrentUser devait aussi rafraîchir un token, ce qui n'est pas le cas actuellement.
    });
    builder.addCase(fetchCurrentUser.rejected, (state, action) => {
      state.isLoading = false;
      state.isAuthenticated = false;
      state.user = null;
      state.token = null; // Le token est invalide ou non trouvé, donc on le vide dans le state.
                          // localStorage est géré par le thunk fetchCurrentUser ou logout.
      
      // Afficher une erreur seulement si ce n'est pas un échec "silencieux" 
      // (comme un token non trouvé au démarrage de l'app).
      if (action.payload && action.payload !== 'Token non trouvé') {
        state.error = action.payload as string;
      } else {
        state.error = null; // Pas d'erreur visible pour un token non trouvé initialement.
      }
    });
    
    // Logout
    builder.addCase(logout.fulfilled, (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.token = null;
    });
  },
});

export const { clearError } = authSlice.actions;

export const selectAuth = (state: RootState) => state.auth;
export const selectUser = (state: RootState) => state.auth.user;
export const selectIsAuthenticated = (state: RootState) => state.auth.isAuthenticated;

export default authSlice.reducer;
