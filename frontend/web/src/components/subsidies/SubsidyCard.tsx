import React from 'react';
import { Card, CardContent, Typography, Chip, Button, Box, Divider, Tooltip } from '@mui/material';
import { Euro, CheckCircle, Info, LocationOn, Business, CategoryOutlined } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

export interface SubsidyType {
  id: string;
  name: string;
  description: string;
  provider: string;
  regions: string[];
  maxAmount: number | null;
  percentage: number | null;
  keywords: string[];
  eligibility: string[];
  documentationUrl?: string;
}

interface SubsidyCardProps {
  subsidy: SubsidyType;
  expanded?: boolean;
  onApply?: (id: string) => void;
}

export const SubsidyCard: React.FC<SubsidyCardProps> = ({ 
  subsidy, 
  expanded = false,
  onApply 
}) => {
  const navigate = useNavigate();
  
  const handleApply = () => {
    if (onApply) {
      onApply(subsidy.id);
    } else {
      navigate(`/subsidies/apply/${subsidy.id}`);
    }
  };

  const handleDetails = () => {
    navigate(`/subsidies/details/${subsidy.id}`);
  };

  // Traduire les régions
  const getRegionName = (region: string): string => {
    const regionMap: {[key: string]: string} = {
      'wallonie': 'Wallonie',
      'bruxelles': 'Bruxelles',
      'flandre': 'Flandre',
    };
    return regionMap[region.toLowerCase()] || region;
  };

  return (
    <Card sx={{ 
      mb: 2, 
      border: '1px solid #e0e0e0',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
      '&:hover': {
        transform: 'translateY(-2px)',
        boxShadow: '0 6px 12px rgba(0, 0, 0, 0.15)',
      }
    }}>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ color: 'primary.main', fontWeight: 600 }}>
          {subsidy.name}
        </Typography>
        
        <Typography variant="body2" color="text.secondary" paragraph>
          {expanded 
            ? subsidy.description 
            : subsidy.description.length > 180 
              ? `${subsidy.description.substring(0, 180)}...` 
              : subsidy.description
          }
        </Typography>
        
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box display="flex" alignItems="center">
            <Business fontSize="small" color="action" sx={{ mr: 0.5 }} />
            <Typography variant="subtitle2" color="text.secondary">
              {subsidy.provider}
            </Typography>
          </Box>
          
          <Box>
            {subsidy.maxAmount && (
              <Tooltip title="Montant maximum de la subvention">
                <Chip 
                  icon={<Euro />} 
                  label={`Jusqu'à ${subsidy.maxAmount.toLocaleString()}€`} 
                  color="primary" 
                  sx={{ mr: 1 }} 
                  size="small"
                />
              </Tooltip>
            )}
            {subsidy.percentage && (
              <Tooltip title="Pourcentage des coûts éligibles">
                <Chip 
                  icon={<CheckCircle />} 
                  label={`${subsidy.percentage}%`} 
                  color="secondary"
                  size="small"
                />
              </Tooltip>
            )}
          </Box>
        </Box>

        <Divider sx={{ my: 1.5 }} />
        
        <Box display="flex" alignItems="center" mb={1.5}>
          <LocationOn fontSize="small" color="action" sx={{ mr: 0.5 }} />
          <Typography variant="body2" color="text.secondary">
            Régions: {subsidy.regions.map(getRegionName).join(', ')}
          </Typography>
        </Box>
        
        <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
          <CategoryOutlined fontSize="small" color="action" sx={{ mr: 0.5 }} />
          {subsidy.keywords.map(keyword => (
            <Chip 
              key={keyword} 
              label={keyword} 
              size="small" 
              variant="outlined" 
              sx={{ fontSize: '0.7rem' }}
            />
          ))}
        </Box>
        
        {expanded && (
          <>
            <Divider sx={{ my: 1.5 }} />
            <Typography variant="subtitle2" color="text.primary" gutterBottom>
              Conditions d'éligibilité:
            </Typography>
            <ul style={{ paddingLeft: '20px', margin: '8px 0' }}>
              {subsidy.eligibility.map((item, index) => (
                <li key={index}>
                  <Typography variant="body2" color="text.secondary">
                    {item}
                  </Typography>
                </li>
              ))}
            </ul>
          </>
        )}
        
        <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
          <Button 
            variant="outlined" 
            color="primary" 
            size="small"
            startIcon={<Info />}
            onClick={handleDetails}
          >
            Détails
          </Button>
          <Button 
            variant="contained" 
            color="primary" 
            size="small"
            onClick={handleApply}
          >
            Demander
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default SubsidyCard;
