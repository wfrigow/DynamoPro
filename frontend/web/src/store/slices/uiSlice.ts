import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '..';

interface UiState {
  darkMode: boolean;
  sidebarOpen: boolean;
  notifications: {
    id: string;
    message: string;
    type: 'info' | 'success' | 'warning' | 'error';
    read: boolean;
  }[];
}

const initialState: UiState = {
  darkMode: false,
  sidebarOpen: true,
  notifications: [
    {
      id: '1',
      message: 'Nouvelle subvention disponible',
      type: 'info',
      read: false,
    },
    {
      id: '2',
      message: 'Recommandation mise à jour',
      type: 'info',
      read: false,
    },
    {
      id: '3',
      message: 'Devis reçu du fournisseur',
      type: 'success',
      read: false,
    },
  ],
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleDarkMode(state) {
      state.darkMode = !state.darkMode;
    },
    toggleSidebar(state) {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen(state, action: PayloadAction<boolean>) {
      state.sidebarOpen = action.payload;
    },
    markNotificationAsRead(state, action: PayloadAction<string>) {
      const notification = state.notifications.find(n => n.id === action.payload);
      if (notification) {
        notification.read = true;
      }
    },
    clearNotifications(state) {
      state.notifications = [];
    },
  },
});

export const { 
  toggleDarkMode, 
  toggleSidebar, 
  setSidebarOpen, 
  markNotificationAsRead, 
  clearNotifications 
} = uiSlice.actions;

export const selectUi = (state: RootState) => state.ui;
export const selectDarkMode = (state: RootState) => state.ui.darkMode;
export const selectSidebarOpen = (state: RootState) => state.ui.sidebarOpen;
export const selectNotifications = (state: RootState) => state.ui.notifications;
export const selectUnreadNotificationsCount = (state: RootState) => 
  state.ui.notifications.filter(n => !n.read).length;

export default uiSlice.reducer;
