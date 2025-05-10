import { store } from '../store';
import { updateProfile } from '../store/slices/profileSlice';

// Type definitions
export interface ProfileData {
  userType?: string;
  region?: string;
}

export interface ConsumptionData {
  electricityUsage?: number;
  gasUsage?: boolean;
  gasConsumption?: number;
}

export interface PropertyData {
  propertyType?: string;
  area?: number;
  constructionYear?: number;
  insulationStatus?: string;
}

export interface AuditData {
  profile: ProfileData;
  consumption: ConsumptionData;
  property: PropertyData;
}

export interface SimplifiedAudit {
  timestamp: string;
  data: {
    userType?: string;
    region?: string;
    electricityUsage?: number;
    gasUsage?: boolean;
    gasConsumption?: number;
    propertyType?: string;
    area?: number;
    constructionYear?: number;
    insulationStatus?: string;
  };
}

// Constants
export const AUDIT_STORAGE_KEY = 'dynamopro_current_audit';

/**
 * Save audit data to both localStorage and Redux store
 * @param auditData The audit data to save
 * @returns Boolean indicating success
 */
export const saveAuditData = (auditData: SimplifiedAudit): boolean => {
  try {
    // 1. Save to localStorage
    localStorage.setItem(AUDIT_STORAGE_KEY, JSON.stringify(auditData));
    
    // 2. Save to Redux store
    store.dispatch(updateProfile({
      auditData: {
        lastUpdated: auditData.timestamp,
        // Profile data
        userType: auditData.data.userType,
        region: auditData.data.region,
        // Consumption data
        electricityUsage: auditData.data.electricityUsage,
        gasUsage: auditData.data.gasUsage,
        gasConsumption: auditData.data.gasConsumption,
        // Property data
        propertyType: auditData.data.propertyType,
        area: auditData.data.area,
        constructionYear: auditData.data.constructionYear,
        insulationStatus: auditData.data.insulationStatus
      }
    }));
    
    console.log('Audit data successfully saved to localStorage and Redux store');
    return true;
  } catch (error) {
    console.error('Error saving audit data:', error);
    return false;
  }
};

/**
 * Get audit data from multiple sources with fallback
 * @returns SimplifiedAudit object or null if not found
 */
export const getAuditData = (): SimplifiedAudit | null => {
  try {
    // 1. Try to get from Redux store first
    const state = store.getState();
    const profile = state.profile.profile;
    
    if (profile?.auditData && Object.keys(profile.auditData).length > 0) {
      console.log('Audit data found in Redux store');
      
      const simplifiedAudit: SimplifiedAudit = {
        timestamp: profile.auditData.lastUpdated || new Date().toISOString(),
        data: {
          userType: profile.auditData.userType,
          region: profile.auditData.region,
          electricityUsage: profile.auditData.electricityUsage,
          gasUsage: profile.auditData.gasUsage,
          gasConsumption: profile.auditData.gasConsumption,
          propertyType: profile.auditData.propertyType,
          area: profile.auditData.area,
          constructionYear: profile.auditData.constructionYear,
          insulationStatus: profile.auditData.insulationStatus
        }
      };
      
      // Ensure localStorage is in sync
      localStorage.setItem(AUDIT_STORAGE_KEY, JSON.stringify(simplifiedAudit));
      
      return simplifiedAudit;
    }
    
    // 2. Try to get from localStorage
    const auditStr = localStorage.getItem(AUDIT_STORAGE_KEY);
    if (auditStr) {
      console.log('Audit data found in localStorage');
      const simplifiedAudit: SimplifiedAudit = JSON.parse(auditStr);
      
      // Sync with Redux store
      saveAuditData(simplifiedAudit);
      
      return simplifiedAudit;
    }
    
    // 3. Try to find older format audits
    const auditKeys: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('audit_')) {
        auditKeys.push(key);
      }
    }
    
    if (auditKeys.length > 0) {
      console.log('Found older format audits');
      // Sort by date (most recent first)
      auditKeys.sort().reverse();
      
      const lastAuditStr = localStorage.getItem(auditKeys[0]);
      if (lastAuditStr) {
        const storedAudit = JSON.parse(lastAuditStr);
        
        // Convert to simplified format
        const simplifiedAudit: SimplifiedAudit = {
          timestamp: new Date().toISOString(),
          data: {
            userType: storedAudit.auditData?.profile?.userType || storedAudit.userType,
            region: storedAudit.auditData?.profile?.region || storedAudit.region,
            electricityUsage: storedAudit.auditData?.consumption?.electricityUsage || storedAudit.electricityUsage,
            gasUsage: storedAudit.auditData?.consumption?.gasUsage || storedAudit.gasUsage,
            gasConsumption: storedAudit.auditData?.consumption?.gasConsumption || storedAudit.gasConsumption,
            propertyType: storedAudit.auditData?.property?.type || storedAudit.propertyType,
            area: storedAudit.auditData?.property?.size || storedAudit.auditData?.property?.area || storedAudit.area,
            constructionYear: storedAudit.auditData?.property?.constructionYear || storedAudit.constructionYear,
            insulationStatus: storedAudit.auditData?.property?.insulation || storedAudit.auditData?.property?.insulationStatus || storedAudit.insulationStatus
          }
        };
        
        // Save in new format for future use
        saveAuditData(simplifiedAudit);
        
        return simplifiedAudit;
      }
    }
    
    console.log('No audit data found');
    return null;
  } catch (error) {
    console.error('Error retrieving audit data:', error);
    return null;
  }
};

/**
 * Clear all audit data from localStorage and Redux store
 */
export const clearAuditData = (): void => {
  try {
    // Clear from localStorage
    localStorage.removeItem(AUDIT_STORAGE_KEY);
    
    // Clear old format audits
    const auditKeys: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('audit_')) {
        auditKeys.push(key);
      }
    }
    
    auditKeys.forEach(key => localStorage.removeItem(key));
    
    // Clear from Redux store
    store.dispatch(updateProfile({
      auditData: undefined
    }));
    
    console.log('All audit data cleared');
  } catch (error) {
    console.error('Error clearing audit data:', error);
  }
};
