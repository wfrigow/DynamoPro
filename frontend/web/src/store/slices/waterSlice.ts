import { createSlice } from '@reduxjs/toolkit';
import { RootState } from '..';

interface WaterState {
  loading: boolean;
  error: string | null;
  consumptionData: {
    id: string;
    startDate: string;
    endDate: string;
    consumptionM3: number;
    cost: number;
    provider: string;
  }[];
}

const initialState: WaterState = {
  loading: false,
  error: null,
  consumptionData: [
    {
      id: 'water-1',
      startDate: '2025-01-01',
      endDate: '2025-03-31',
      consumptionM3: 45,
      cost: 150,
      provider: 'CILE',
    },
    {
      id: 'water-2',
      startDate: '2024-10-01',
      endDate: '2024-12-31',
      consumptionM3: 42,
      cost: 140,
      provider: 'CILE',
    },
    {
      id: 'water-3',
      startDate: '2024-07-01',
      endDate: '2024-09-30',
      consumptionM3: 48,
      cost: 160,
      provider: 'CILE',
    },
  ],
};

const waterSlice = createSlice({
  name: 'water',
  initialState,
  reducers: {},
});

export const selectWaterData = (state: RootState) => state.water.consumptionData;
export const selectWaterLoading = (state: RootState) => state.water.loading;
export const selectWaterError = (state: RootState) => state.water.error;

export default waterSlice.reducer;
