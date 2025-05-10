import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  AppBar,
  Box,
  CssBaseline,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Avatar,
  Menu,
  MenuItem,
  Tooltip,
  Badge,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Person as PersonIcon,
  BoltOutlined as EnergyIcon,
  WaterDrop as WaterIcon,
  Recommend as RecommendIcon,
  Euro as SubsidyIcon,
  Business as SupplierIcon,
  Assignment as ProjectsIcon,
  EmojiEvents as GreenPassportIcon,
  Notifications as NotificationsIcon,
  Logout as LogoutIcon,
  RecordVoiceOver as AuditIcon,
} from '@mui/icons-material';
import { selectAuth, logout } from '../store/slices/authSlice';

const drawerWidth = 260;

interface NavItem {
  text: string;
  path: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  { text: 'Tableau de bord', path: '/', icon: <DashboardIcon /> },
  { text: 'Mon profil', path: '/profile', icon: <PersonIcon /> },
  { text: 'Audit vocal', path: '/audit', icon: <AuditIcon /> },
  { text: 'Énergie', path: '/energy', icon: <EnergyIcon /> },
  { text: 'Eau', path: '/water', icon: <WaterIcon /> },
  { text: 'Recommandations', path: '/recommendations', icon: <RecommendIcon /> },
  { text: 'Subventions', path: '/subsidies', icon: <SubsidyIcon /> },
  { text: 'Fournisseurs', path: '/suppliers', icon: <SupplierIcon /> },
  { text: 'Mes projets', path: '/projects', icon: <ProjectsIcon /> },
  { text: 'Passeport Vert', path: '/green-passport', icon: <GreenPassportIcon /> },
];

const MainLayout: React.FC = () => {
  const { user } = useSelector(selectAuth);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorElUser, setAnchorElUser] = useState<null | HTMLElement>(null);
  const [anchorElNotifications, setAnchorElNotifications] = useState<null | HTMLElement>(null);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleOpenUserMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorElUser(event.currentTarget);
  };

  const handleCloseUserMenu = () => {
    setAnchorElUser(null);
  };

  const handleOpenNotificationsMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorElNotifications(event.currentTarget);
  };

  const handleCloseNotificationsMenu = () => {
    setAnchorElNotifications(null);
  };

  const handleLogout = () => {
    dispatch(logout() as any);
    navigate('/login');
  };

  const getActiveNavItem = () => {
    const activeItem = navItems.find((item) => {
      if (item.path === '/' && location.pathname === '/') {
        return true;
      }
      return location.pathname.startsWith(item.path) && item.path !== '/';
    });
    return activeItem?.text || 'DynamoPro';
  };

  const drawer = (
    <div>
      <Toolbar sx={{ justifyContent: 'center', py: 2 }}>
        <Typography variant="h6" component="div" color="primary" fontWeight="bold">
          DynamoPro
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {navItems.map((item) => {
          const isActive = item.path === '/' 
            ? location.pathname === '/'
            : location.pathname.startsWith(item.path);
            
          return (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                selected={isActive}
                onClick={() => {
                  navigate(item.path);
                  setMobileOpen(false);
                }}
                sx={{
                  borderRight: isActive ? '4px solid' : 'none',
                  borderColor: 'primary.main',
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(46, 125, 50, 0.08)',
                  },
                  '&.Mui-selected:hover': {
                    backgroundColor: 'rgba(46, 125, 50, 0.12)',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isActive ? 'primary.main' : 'inherit',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text} 
                  primaryTypographyProps={{
                    fontWeight: isActive ? 'medium' : 'regular',
                    color: isActive ? 'primary.main' : 'inherit',
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          boxShadow: 'none',
          borderBottom: '1px solid',
          borderColor: 'divider',
          backgroundColor: 'background.paper',
          color: 'text.primary',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {getActiveNavItem()}
          </Typography>

          {/* Notifications */}
          <Box sx={{ flexGrow: 0, mr: 2 }}>
            <Tooltip title="Notifications">
              <IconButton onClick={handleOpenNotificationsMenu}>
                <Badge badgeContent={3} color="error">
                  <NotificationsIcon />
                </Badge>
              </IconButton>
            </Tooltip>
            <Menu
              sx={{ mt: '45px' }}
              anchorEl={anchorElNotifications}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorElNotifications)}
              onClose={handleCloseNotificationsMenu}
            >
              <MenuItem>
                <Typography variant="body2">Nouvelle subvention disponible</Typography>
              </MenuItem>
              <MenuItem>
                <Typography variant="body2">Recommandation mise à jour</Typography>
              </MenuItem>
              <MenuItem>
                <Typography variant="body2">Devis reçu du fournisseur</Typography>
              </MenuItem>
            </Menu>
          </Box>

          {/* User Menu */}
          <Box sx={{ flexGrow: 0 }}>
            <Tooltip title="Options du compte">
              <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
                <Avatar alt={user?.name || 'User'} src="/static/images/avatar/1.jpg" />
              </IconButton>
            </Tooltip>
            <Menu
              sx={{ mt: '45px' }}
              anchorEl={anchorElUser}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorElUser)}
              onClose={handleCloseUserMenu}
            >
              <MenuItem onClick={() => navigate('/profile')}>
                <ListItemIcon>
                  <PersonIcon fontSize="small" />
                </ListItemIcon>
                <Typography textAlign="center">Mon profil</Typography>
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleLogout}>
                <ListItemIcon>
                  <LogoutIcon fontSize="small" />
                </ListItemIcon>
                <Typography textAlign="center">Déconnexion</Typography>
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>
      
      {/* Drawer for Mobile/Desktop */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="navigation menu"
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      
      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          backgroundColor: 'background.default',
          minHeight: '100vh',
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
};

export default MainLayout;
