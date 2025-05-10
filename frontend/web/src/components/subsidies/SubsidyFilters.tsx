import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  TextField, 
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Button,
  Grid,
  Divider,
  Autocomplete,
  SelectChangeEvent,
  IconButton,
  Collapse,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { 
  FilterList, 
  Clear, 
  ExpandMore, 
  ExpandLess,
  EuroSymbol,
  AccessTime,
  Category,
  LocationOn
} from '@mui/icons-material';

// Types pour les filtres
export interface ISubsidyFilters {
  searchTerm: string;
  categories: string[];
  regions: string[];
  minAmount: number | null;
  maxAmount: number | null;
  deadlineRange: number; // en jours
  targetAudiences: string[];
  sortBy: 'relevance' | 'amount' | 'deadline' | 'popularity';
  sortOrder: 'asc' | 'desc';
}

interface SubsidyFiltersProps {
  onFiltersChange: (filters: ISubsidyFilters) => void;
  initialFilters?: Partial<ISubsidyFilters>;
}

// Valeurs par défaut
const DEFAULT_FILTERS: ISubsidyFilters = {
  searchTerm: '',
  categories: [],
  regions: [],
  minAmount: null,
  maxAmount: null,
  deadlineRange: 365, // 1 an par défaut
  targetAudiences: [],
  sortBy: 'relevance',
  sortOrder: 'desc'
};

// Options pour les filtres
const CATEGORIES = [
  'Énergie renouvelable',
  'Efficacité énergétique',
  'Isolation',
  'Chauffage',
  'Eau',
  'Biodiversité',
  'Mobilité durable',
  'Économie circulaire',
  'Rénovation'
];

const REGIONS = [
  'Bruxelles-Capitale',
  'Wallonie',
  'Flandre',
  'Toute la Belgique'
];

const TARGET_AUDIENCES = [
  'Particuliers',
  'Indépendants',
  'PME',
  'Grandes entreprises',
  'Associations',
  'Secteur public'
];

const SubsidyFilters: React.FC<SubsidyFiltersProps> = ({ onFiltersChange, initialFilters }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [expanded, setExpanded] = useState(!isMobile);
  const [filters, setFilters] = useState<ISubsidyFilters>({
    ...DEFAULT_FILTERS,
    ...initialFilters
  });
  
  // Mettre à jour les filtres parents lorsque les filtres locaux changent
  useEffect(() => {
    onFiltersChange(filters);
  }, [filters, onFiltersChange]);
  
  // Gérer les changements de filtres
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFilters(prev => ({ ...prev, searchTerm: event.target.value }));
  };
  
  const handleCategoriesChange = (_event: React.SyntheticEvent, newValue: string[]) => {
    setFilters(prev => ({ ...prev, categories: newValue }));
  };
  
  const handleRegionsChange = (_event: React.SyntheticEvent, newValue: string[]) => {
    setFilters(prev => ({ ...prev, regions: newValue }));
  };
  
  const handleAmountChange = (_event: Event, newValue: number | number[]) => {
    if (Array.isArray(newValue)) {
      setFilters(prev => ({ 
        ...prev, 
        minAmount: newValue[0] > 0 ? newValue[0] : null,
        maxAmount: newValue[1] < 100000 ? newValue[1] : null
      }));
    }
  };
  
  const handleDeadlineChange = (_event: Event, newValue: number | number[]) => {
    if (!Array.isArray(newValue)) {
      setFilters(prev => ({ ...prev, deadlineRange: newValue }));
    }
  };
  
  const handleTargetAudiencesChange = (_event: React.SyntheticEvent, newValue: string[]) => {
    setFilters(prev => ({ ...prev, targetAudiences: newValue }));
  };
  
  const handleSortByChange = (event: SelectChangeEvent) => {
    setFilters(prev => ({ 
      ...prev, 
      sortBy: event.target.value as 'relevance' | 'amount' | 'deadline' | 'popularity' 
    }));
  };
  
  const handleSortOrderChange = (event: SelectChangeEvent) => {
    setFilters(prev => ({ 
      ...prev, 
      sortOrder: event.target.value as 'asc' | 'desc' 
    }));
  };
  
  const handleReset = () => {
    setFilters(DEFAULT_FILTERS);
  };
  
  const toggleExpanded = () => {
    setExpanded(!expanded);
  };
  
  return (
    <Paper 
      elevation={2} 
      sx={{ 
        p: 3, 
        mb: 3, 
        borderRadius: 2,
        border: '1px solid #f0f0f0'
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <FilterList sx={{ mr: 1 }} />
          <Typography variant="h6">Filtres de recherche</Typography>
        </Box>
        
        <Box>
          <Button 
            size="small" 
            startIcon={<Clear />} 
            onClick={handleReset}
            sx={{ mr: 1 }}
          >
            Réinitialiser
          </Button>
          
          {isMobile && (
            <IconButton onClick={toggleExpanded} size="small">
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          )}
        </Box>
      </Box>
      
      <Collapse in={expanded}>
        <Grid container spacing={3}>
          {/* Barre de recherche */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Rechercher des subventions"
              variant="outlined"
              value={filters.searchTerm}
              onChange={handleSearchChange}
              placeholder="Ex: panneaux solaires, isolation toiture..."
              InputProps={{
                endAdornment: filters.searchTerm ? (
                  <IconButton 
                    size="small" 
                    onClick={() => setFilters(prev => ({ ...prev, searchTerm: '' }))}
                  >
                    <Clear fontSize="small" />
                  </IconButton>
                ) : null
              }}
            />
          </Grid>
          
          {/* Catégories */}
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
              <Category fontSize="small" sx={{ mr: 1, mt: 0.5 }} color="action" />
              <Typography variant="subtitle2">Catégories</Typography>
            </Box>
            <Autocomplete
              multiple
              options={CATEGORIES}
              value={filters.categories}
              onChange={handleCategoriesChange}
              renderInput={(params) => (
                <TextField {...params} variant="outlined" placeholder="Sélectionner des catégories" />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    label={option}
                    {...getTagProps({ index })}
                    size="small"
                    sx={{ m: 0.5 }}
                  />
                ))
              }
            />
          </Grid>
          
          {/* Régions */}
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
              <LocationOn fontSize="small" sx={{ mr: 1, mt: 0.5 }} color="action" />
              <Typography variant="subtitle2">Régions</Typography>
            </Box>
            <Autocomplete
              multiple
              options={REGIONS}
              value={filters.regions}
              onChange={handleRegionsChange}
              renderInput={(params) => (
                <TextField {...params} variant="outlined" placeholder="Sélectionner des régions" />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    label={option}
                    {...getTagProps({ index })}
                    size="small"
                    sx={{ m: 0.5 }}
                  />
                ))
              }
            />
          </Grid>
          
          {/* Montant */}
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
              <EuroSymbol fontSize="small" sx={{ mr: 1, mt: 0.5 }} color="action" />
              <Typography variant="subtitle2">Montant (€)</Typography>
            </Box>
            <Box sx={{ px: 2, pt: 1 }}>
              <Slider
                value={[filters.minAmount || 0, filters.maxAmount || 100000]}
                onChange={handleAmountChange}
                valueLabelDisplay="auto"
                min={0}
                max={100000}
                step={1000}
                marks={[
                  { value: 0, label: '0 €' },
                  { value: 25000, label: '25k €' },
                  { value: 50000, label: '50k €' },
                  { value: 75000, label: '75k €' },
                  { value: 100000, label: '100k+ €' }
                ]}
              />
            </Box>
          </Grid>
          
          {/* Délai */}
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
              <AccessTime fontSize="small" sx={{ mr: 1, mt: 0.5 }} color="action" />
              <Typography variant="subtitle2">Délai maximum (jours)</Typography>
            </Box>
            <Box sx={{ px: 2, pt: 1 }}>
              <Slider
                value={filters.deadlineRange}
                onChange={handleDeadlineChange}
                valueLabelDisplay="auto"
                min={7}
                max={365}
                marks={[
                  { value: 7, label: '7j' },
                  { value: 30, label: '30j' },
                  { value: 90, label: '3m' },
                  { value: 180, label: '6m' },
                  { value: 365, label: '1a' }
                ]}
              />
            </Box>
          </Grid>
          
          {/* Public cible */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
              <Typography variant="subtitle2">Public cible</Typography>
            </Box>
            <Autocomplete
              multiple
              options={TARGET_AUDIENCES}
              value={filters.targetAudiences}
              onChange={handleTargetAudiencesChange}
              renderInput={(params) => (
                <TextField {...params} variant="outlined" placeholder="Sélectionner des publics cibles" />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    label={option}
                    {...getTagProps({ index })}
                    size="small"
                    sx={{ m: 0.5 }}
                  />
                ))
              }
            />
          </Grid>
          
          <Grid item xs={12}>
            <Divider sx={{ my: 1 }} />
          </Grid>
          
          {/* Tri */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel id="sort-by-label">Trier par</InputLabel>
              <Select
                labelId="sort-by-label"
                value={filters.sortBy}
                label="Trier par"
                onChange={handleSortByChange}
              >
                <MenuItem value="relevance">Pertinence</MenuItem>
                <MenuItem value="amount">Montant</MenuItem>
                <MenuItem value="deadline">Date limite</MenuItem>
                <MenuItem value="popularity">Popularité</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel id="sort-order-label">Ordre</InputLabel>
              <Select
                labelId="sort-order-label"
                value={filters.sortOrder}
                label="Ordre"
                onChange={handleSortOrderChange}
              >
                <MenuItem value="desc">Décroissant</MenuItem>
                <MenuItem value="asc">Croissant</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Collapse>
    </Paper>
  );
};

export default SubsidyFilters;
