import React, { useEffect, useState } from 'react';
import { Alert, AlertTitle, Snackbar, Stack } from '@mui/material';
import { notificationService, Notification } from '../../services/NotificationService';

/**
 * Composant global de notification qui affiche les notifications à l'utilisateur
 * Ce composant doit être placé une seule fois dans l'application, généralement dans App.tsx
 */
const NotificationCenter: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    // S'abonner aux nouvelles notifications
    const notificationSubscription = notificationService.notifications$.subscribe((notification: Notification) => {
      setNotifications(prev => [...prev, notification]);
      
      // Si la notification doit se fermer automatiquement, configurer un timer
      if (notification.autoClose && notification.duration) {
        setTimeout(() => {
          handleClose(notification.id);
        }, notification.duration);
      }
    });
    
    // S'abonner aux demandes de fermeture de notifications
    const dismissSubscription = notificationService.dismiss$.subscribe((id: string) => {
      handleClose(id);
    });
    
    // Nettoyer les abonnements lors du démontage du composant
    return () => {
      notificationSubscription.unsubscribe();
      dismissSubscription.unsubscribe();
    };
  }, []);
  
  // Gérer la fermeture d'une notification
  const handleClose = (id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  };
  
  return (
    <Stack spacing={2} sx={{ 
      position: 'fixed', 
      bottom: 24, 
      right: 24, 
      zIndex: 2000,
      maxWidth: '100%',
      width: { xs: 'calc(100% - 48px)', sm: 400 }
    }}>
      {notifications.map((notification) => (
        <Snackbar
          key={notification.id}
          open={true}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          sx={{ position: 'static', mb: 1 }}
        >
          <Alert
            severity={notification.type}
            variant="filled"
            onClose={() => handleClose(notification.id)}
            sx={{ width: '100%' }}
          >
            {notification.title && (
              <AlertTitle>{notification.title}</AlertTitle>
            )}
            {notification.message}
          </Alert>
        </Snackbar>
      ))}
    </Stack>
  );
};

export default NotificationCenter;
