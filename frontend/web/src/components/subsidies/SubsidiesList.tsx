import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  MenuItem, 
  Grid, 
  Pagination, 
  FormControl, 
  InputLabel, 
  Select, 
  SelectChangeEvent,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  InputAdornment
} from '@mui/material';
import { Search, FilterList, Clear } from '@mui/icons-material';
import SubsidyCard, { SubsidyType } from './SubsidyCard';

interface SubsidiesListProps {
  subsidies: SubsidyType[];
  loading?: boolean;
  error?: string | null;
  onApply?: (id: string) => void;
}

const SubsidiesList: React.FC<SubsidiesListProps> = ({ 
  subsidies, 
  loading = false, 
  error = null,
  onApply
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [regionFilter, setRegionFilter] = useState<string>('');
  const [keywordFilter, setKeywordFilter] = useState<string>('');
  const [page, setPage] = useState(1);
  const [filtersVisible, setFiltersVisible] = useState(false);
  
  const itemsPerPage = 5;

  // Extraire toutes les régions uniques
  const allRegions = Array.from(
    new Set(subsidies.flatMap(subsidy => subsidy.regions))
  );
  
  // Extraire tous les mots-clés uniques
  const allKeywords = Array.from(
    new Set(subsidies.flatMap(subsidy => subsidy.keywords))
  );

  // Filtrer les subventions
  const filteredSubsidies = subsidies.filter(subsidy => {
    const matchesSearch = searchTerm === '' || 
      subsidy.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      subsidy.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      subsidy.provider.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesRegion = regionFilter === '' || 
      subsidy.regions.some(r => r.toLowerCase() === regionFilter.toLowerCase());
    
    const matchesKeyword = keywordFilter === '' ||
      subsidy.keywords.some(k => k.toLowerCase() === keywordFilter.toLowerCase());
    
    return matchesSearch && matchesRegion && matchesKeyword;
  });

  // Pagination
  const totalPages = Math.ceil(filteredSubsidies.length / itemsPerPage);
  const paginatedSubsidies = filteredSubsidies.slice(
    (page - 1) * itemsPerPage,
    page * itemsPerPage
  );

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    setPage(1); // Reset to first page on search change
  };

  const handleRegionChange = (event: SelectChangeEvent) => {
    setRegionFilter(event.target.value);
    setPage(1);
  };

  const handleKeywordChange = (event: SelectChangeEvent) => {
    setKeywordFilter(event.target.value);
    setPage(1);
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const clearFilters = () => {
    setSearchTerm('');
    setRegionFilter('');
    setKeywordFilter('');
    setPage(1);
  };

  const toggleFilters = () => {
    setFiltersVisible(!filtersVisible);
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

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Box mb={3}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={8}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Rechercher des subventions..."
              value={searchTerm}
              onChange={handleSearchChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search color="action" />
                  </InputAdornment>
                ),
                endAdornment: searchTerm && (
                  <InputAdornment position="end">
                    <IconButton size="small" onClick={() => setSearchTerm('')}>
                      <Clear fontSize="small" />
                    </IconButton>
                  </InputAdornment>
                )
              }}
              size="small"
            />
          </Grid>
          <Grid item xs={6} sm={3} md={2}>
            <Box display="flex" justifyContent="flex-end">
              <IconButton 
                onClick={toggleFilters} 
                color={filtersVisible ? "primary" : "default"}
                sx={{ border: filtersVisible ? '1px solid' : 'none' }}
              >
                <FilterList />
              </IconButton>
            </Box>
          </Grid>
          <Grid item xs={6} sm={3} md={2}>
            {(searchTerm || regionFilter || keywordFilter) && (
              <Box display="flex" justifyContent="flex-end">
                <Chip 
                  label="Effacer les filtres" 
                  variant="outlined" 
                  size="small" 
                  onDelete={clearFilters} 
                />
              </Box>
            )}
          </Grid>
        </Grid>
      </Box>

      {filtersVisible && (
        <Box mb={3}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small">
                <InputLabel>Région</InputLabel>
                <Select
                  value={regionFilter}
                  label="Région"
                  onChange={handleRegionChange}
                >
                  <MenuItem value="">Toutes les régions</MenuItem>
                  {allRegions.map(region => (
                    <MenuItem key={region} value={region}>
                      {getRegionName(region)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small">
                <InputLabel>Mot-clé</InputLabel>
                <Select
                  value={keywordFilter}
                  label="Mot-clé"
                  onChange={handleKeywordChange}
                >
                  <MenuItem value="">Tous les mots-clés</MenuItem>
                  {allKeywords.map(keyword => (
                    <MenuItem key={keyword} value={keyword}>
                      {keyword}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Box>
      )}

      {filteredSubsidies.length > 0 ? (
        <>
          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary">
              {filteredSubsidies.length} subvention{filteredSubsidies.length > 1 ? 's' : ''} trouvée{filteredSubsidies.length > 1 ? 's' : ''}
            </Typography>
          </Box>

          {paginatedSubsidies.map(subsidy => (
            <SubsidyCard 
              key={subsidy.id} 
              subsidy={subsidy} 
              onApply={onApply}
            />
          ))}

          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" mt={4}>
              <Pagination 
                count={totalPages} 
                page={page} 
                onChange={handlePageChange} 
                color="primary" 
              />
            </Box>
          )}
        </>
      ) : (
        <Alert severity="info">
          Aucune subvention ne correspond à vos critères. Essayez de modifier vos filtres.
        </Alert>
      )}
    </Box>
  );
};

export default SubsidiesList;
