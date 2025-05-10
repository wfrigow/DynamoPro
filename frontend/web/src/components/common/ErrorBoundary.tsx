import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button, Paper, Container } from '@mui/material';
import { ErrorOutline } from '@mui/icons-material';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Composant qui capture les erreurs JavaScript dans ses composants enfants,
 * affiche une interface de secours et enregistre les erreurs.
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Mettre à jour l'état pour afficher l'UI de secours
    return {
      hasError: true,
      error,
      errorInfo: null
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Vous pouvez également enregistrer l'erreur dans un service de rapport d'erreurs
    console.error('ErrorBoundary a capturé une erreur:', error, errorInfo);
    
    // Mettre à jour l'état avec les informations d'erreur
    this.setState({
      errorInfo
    });
    
    // Ici, vous pourriez envoyer l'erreur à un service comme Sentry
    // if (process.env.NODE_ENV === 'production') {
    //   Sentry.captureException(error);
    // }
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Vous pouvez afficher n'importe quelle UI de secours
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <Container maxWidth="md">
          <Paper 
            elevation={3} 
            sx={{ 
              p: 4, 
              mt: 4, 
              textAlign: 'center',
              borderRadius: 2,
              border: '1px solid #f0f0f0'
            }}
          >
            <ErrorOutline color="error" sx={{ fontSize: 60, mb: 2 }} />
            <Typography variant="h4" gutterBottom>
              Oups ! Une erreur s'est produite
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              Nous sommes désolés pour ce désagrément. L'équipe technique a été informée du problème.
            </Typography>
            
            {process.env.NODE_ENV !== 'production' && this.state.error && (
              <Box sx={{ mt: 2, mb: 2, textAlign: 'left', bgcolor: '#f5f5f5', p: 2, borderRadius: 1 }}>
                <Typography variant="subtitle2" color="error">
                  {this.state.error.toString()}
                </Typography>
                {this.state.errorInfo && (
                  <Typography 
                    variant="caption" 
                    component="pre" 
                    sx={{ 
                      mt: 1, 
                      p: 1, 
                      bgcolor: '#eeeeee',
                      overflowX: 'auto',
                      fontFamily: 'monospace'
                    }}
                  >
                    {this.state.errorInfo.componentStack}
                  </Typography>
                )}
              </Box>
            )}
            
            <Box sx={{ mt: 3 }}>
              <Button 
                variant="contained" 
                color="primary" 
                onClick={this.handleReset}
                sx={{ mr: 2 }}
              >
                Réessayer
              </Button>
              <Button 
                variant="outlined"
                onClick={() => window.location.href = '/'}
              >
                Retour à l'accueil
              </Button>
            </Box>
          </Paper>
        </Container>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
