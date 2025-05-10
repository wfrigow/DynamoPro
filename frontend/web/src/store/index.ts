import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import profileReducer from './slices/profileSlice';
import energyReducer from './slices/energySlice';
import waterReducer from './slices/waterSlice';
import recommendationsReducer from './slices/recommendationsSlice';
import subsidiesReducer from './slices/subsidiesSlice';
import suppliersReducer from './slices/suppliersSlice';
import projectsReducer from './slices/projectsSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    profile: profileReducer,
    energy: energyReducer,
    water: waterReducer,
    recommendations: recommendationsReducer,
    subsidies: subsidiesReducer,
    suppliers: suppliersReducer,
    projects: projectsReducer,
    ui: uiReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
