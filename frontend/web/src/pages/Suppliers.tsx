import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Rating,
  TextField,
  InputAdornment,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Avatar,
} from '@mui/material';
import {
  Search as SearchIcon,
  CheckCircle as VerifiedIcon,
  Star as StarIcon,
  FilterList as FilterIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Language as WebsiteIcon,
  LocationOn as LocationIcon,
} from '@mui/icons-material';
import { useSelector } from 'react-redux';
import { selectSuppliers, Supplier } from '../store/slices/suppliersSlice';

const Suppliers: React.FC = () => {
  const suppliers = useSelector(selectSuppliers);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDomain, setSelectedDomain] = useState<string>('all');
  const [selectedRegion, setSelectedRegion] = useState<string>('all');
  const [openContactDialog, setOpenContactDialog] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null);

  const handleDomainChange = (event: SelectChangeEvent) => {
    setSelectedDomain(event.target.value);
  };

  const handleRegionChange = (event: SelectChangeEvent) => {
    setSelectedRegion(event.target.value);
  };

  const handleOpenContactDialog = (supplier: Supplier) => {
    setSelectedSupplier(supplier);
    setOpenContactDialog(true);
  };

  const handleCloseContactDialog = () => {
    setOpenContactDialog(false);
  };

  // Filter suppliers based on search term, domain, and region
  const filteredSuppliers = suppliers.filter(supplier => {
    const matchesSearch = 
      supplier.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      supplier.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesDomain = 
      selectedDomain === 'all' || 
      supplier.domains.includes(selectedDomain as 'energy' | 'water' | 'waste' | 'biodiversity');
    
    const matchesRegion = 
      selectedRegion === 'all' || 
      supplier.regionsServed.includes(selectedRegion as 'wallonie' | 'flandre' | 'bruxelles');
    
    return matchesSearch && matchesDomain && matchesRegion && supplier.active;
  });

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
        <Typography variant="h5" gutterBottom>
          Fournisseurs
        </Typography>
        <Typography variant="body1" color="textSecondary" paragraph>
          Découvrez notre réseau de fournisseurs qualifiés et certifiés pour vos projets de durabilité.
        </Typography>

        {/* Search and Filter */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Rechercher un fournisseur"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel id="domain-filter-label">Domaine</InputLabel>
              <Select
                labelId="domain-filter-label"
                value={selectedDomain}
                label="Domaine"
                onChange={handleDomainChange}
                startAdornment={(
                  <InputAdornment position="start">
                    <FilterIcon />
                  </InputAdornment>
                )}
              >
                <MenuItem value="all">Tous les domaines</MenuItem>
                <MenuItem value="energy">Énergie</MenuItem>
                <MenuItem value="water">Eau</MenuItem>
                <MenuItem value="waste">Déchets</MenuItem>
                <MenuItem value="biodiversity">Biodiversité</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel id="region-filter-label">Région</InputLabel>
              <Select
                labelId="region-filter-label"
                value={selectedRegion}
                label="Région"
                onChange={handleRegionChange}
                startAdornment={(
                  <InputAdornment position="start">
                    <LocationIcon />
                  </InputAdornment>
                )}
              >
                <MenuItem value="all">Toutes les régions</MenuItem>
                <MenuItem value="wallonie">Wallonie</MenuItem>
                <MenuItem value="bruxelles">Bruxelles</MenuItem>
                <MenuItem value="flandre">Flandre</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {/* Suppliers List */}
        <Grid container spacing={3}>
          {filteredSuppliers.map((supplier) => (
            <Grid item xs={12} md={6} lg={4} key={supplier.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Avatar
                        sx={{ 
                          bgcolor: 'primary.main', 
                          width: 40, 
                          height: 40,
                          mr: 1 
                        }}
                      >
                        {supplier.name.charAt(0)}
                      </Avatar>
                      <Typography variant="h6" component="div">
                        {supplier.name}
                      </Typography>
                    </Box>
                    {supplier.verified && (
                      <Chip
                        icon={<VerifiedIcon />}
                        label="Vérifié"
                        color="success"
                        size="small"
                      />
                    )}
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    {supplier.domains.map(domain => {
                      let label, color;
                      switch(domain) {
                        case 'energy':
                          label = 'Énergie';
                          color = 'primary';
                          break;
                        case 'water':
                          label = 'Eau';
                          color = 'info';
                          break;
                        case 'waste':
                          label = 'Déchets';
                          color = 'warning';
                          break;
                        case 'biodiversity':
                          label = 'Biodiversité';
                          color = 'success';
                          break;
                      }
                      return (
                        <Chip
                          key={domain}
                          label={label}
                          color={color as any}
                          size="small"
                          sx={{ mr: 0.5, mb: 0.5 }}
                        />
                      );
                    })}
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {supplier.description}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <LocationIcon fontSize="small" color="action" sx={{ mr: 0.5 }} />
                    <Typography variant="body2" color="text.secondary">
                      {supplier.postalCode} {supplier.city}
                    </Typography>
                  </Box>
                  
                  {supplier.rating && (
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Rating
                        value={supplier.rating}
                        readOnly
                        size="small"
                        emptyIcon={<StarIcon style={{ opacity: 0.55 }} fontSize="inherit" />}
                      />
                      <Typography variant="body2" sx={{ ml: 0.5 }}>
                        ({supplier.rating.toFixed(1)})
                      </Typography>
                    </Box>
                  )}
                </CardContent>
                
                <Divider />
                
                <CardActions>
                  <Button 
                    size="small" 
                    startIcon={<EmailIcon />}
                    onClick={() => handleOpenContactDialog(supplier)}
                  >
                    Contacter
                  </Button>
                  {supplier.website && (
                    <Button 
                      size="small" 
                      startIcon={<WebsiteIcon />}
                      component="a"
                      href={supplier.website}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Site web
                    </Button>
                  )}
                </CardActions>
              </Card>
            </Grid>
          ))}
          
          {filteredSuppliers.length === 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="h6" color="textSecondary">
                  Aucun fournisseur ne correspond à vos critères de recherche.
                </Typography>
              </Paper>
            </Grid>
          )}
        </Grid>
      </Paper>
      
      {/* Contact Dialog */}
      <Dialog open={openContactDialog} onClose={handleCloseContactDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          Contacter {selectedSupplier?.name}
        </DialogTitle>
        <DialogContent>
          {selectedSupplier && (
            <>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Coordonnées:
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <EmailIcon fontSize="small" sx={{ mr: 1 }} />
                  <Typography variant="body1">
                    {selectedSupplier.contactEmail}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <PhoneIcon fontSize="small" sx={{ mr: 1 }} />
                  <Typography variant="body1">
                    {selectedSupplier.contactPhone}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <LocationIcon fontSize="small" sx={{ mr: 1 }} />
                  <Typography variant="body1">
                    {selectedSupplier.address}, {selectedSupplier.postalCode} {selectedSupplier.city}
                  </Typography>
                </Box>
              </Box>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="subtitle1" gutterBottom>
                Demande de devis:
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Votre message"
                placeholder="Décrivez votre projet et vos besoins pour obtenir un devis personnalisé..."
                sx={{ mb: 2 }}
              />
              <Typography variant="caption" color="text.secondary">
                En envoyant ce message, vous acceptez que vos coordonnées soient partagées avec ce fournisseur. Vous recevrez une copie de votre demande par email.
              </Typography>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseContactDialog}>Annuler</Button>
          <Button variant="contained" color="primary">
            Envoyer la demande
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Suppliers;
