import { createSlice } from '@reduxjs/toolkit';
import { RootState } from '..';

interface EnergyState {
  loading: boolean;
  error: string | null;
  consumptionData: {
    id: string;
    type: 'electricity' | 'gas';
    startDate: string;
    endDate: string;
    consumptionKwh: number;
    cost: number;
    provider: string;
  }[];
}

const initialState: EnergyState = {
  loading: false,
  error: null,
  consumptionData: [
    {
      id: 'energy-1',
      type: 'electricity',
      startDate: '2025-01-01',
      endDate: '2025-03-31',
      consumptionKwh: 1250,
      cost: 350,
      provider: 'Engie',
    },
    {
      id: 'energy-2',
      type: 'gas',
      startDate: '2025-01-01',
      endDate: '2025-03-31',
      consumptionKwh: 5500,
      cost: 550,
      provider: 'Luminus',
    },
    {
      id: 'energy-3',
      type: 'electricity',
      startDate: '2024-10-01',
      endDate: '2024-12-31',
      consumptionKwh: 1300,
      cost: 380,
      provider: 'Engie',
    },
    {
      id: 'energy-4',
      type: 'gas',
      startDate: '2024-10-01',
      endDate: '2024-12-31',
      consumptionKwh: 6200,
      cost: 640,
      provider: 'Luminus',
    },
  ],
};

const energySlice = createSlice({
  name: 'energy',
  initialState,
  reducers: {},
});

export const selectEnergyData = (state: RootState) => state.energy.consumptionData;
export const selectEnergyLoading = (state: RootState) => state.energy.loading;
export const selectEnergyError = (state: RootState) => state.energy.error;

export default energySlice.reducer;
