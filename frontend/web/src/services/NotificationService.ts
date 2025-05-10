import { Subject } from 'rxjs';

export type NotificationType = 'success' | 'error' | 'info' | 'warning';

export interface Notification {
  id: string;
  type: NotificationType;
  message: string;
  title?: string;
  duration?: number; // en millisecondes
  autoClose?: boolean;
}

/**
 * Service de notification global pour l'application
 * Permet d'afficher des notifications à l'utilisateur depuis n'importe quel composant
 */
class NotificationService {
  private notificationSubject = new Subject<Notification>();
  private dismissSubject = new Subject<string>();
  
  // Observable pour les nouvelles notifications
  public notifications$ = this.notificationSubject.asObservable();
  
  // Observable pour les notifications à fermer
  public dismiss$ = this.dismissSubject.asObservable();
  
  /**
   * Affiche une notification de succès
   * @param message Message à afficher
   * @param title Titre optionnel
   * @param duration Durée d'affichage en millisecondes (par défaut 5000ms)
   */
  success(message: string, title?: string, duration = 5000): string {
    return this.notify({
      id: this.generateId(),
      type: 'success',
      message,
      title,
      duration,
      autoClose: true
    });
  }
  
  /**
   * Affiche une notification d'erreur
   * @param message Message à afficher
   * @param title Titre optionnel
   * @param duration Durée d'affichage en millisecondes (par défaut 0 = pas de fermeture automatique)
   */
  error(message: string, title?: string, duration = 0): string {
    return this.notify({
      id: this.generateId(),
      type: 'error',
      message,
      title,
      duration,
      autoClose: duration > 0
    });
  }
  
  /**
   * Affiche une notification d'information
   * @param message Message à afficher
   * @param title Titre optionnel
   * @param duration Durée d'affichage en millisecondes (par défaut 5000ms)
   */
  info(message: string, title?: string, duration = 5000): string {
    return this.notify({
      id: this.generateId(),
      type: 'info',
      message,
      title,
      duration,
      autoClose: true
    });
  }
  
  /**
   * Affiche une notification d'avertissement
   * @param message Message à afficher
   * @param title Titre optionnel
   * @param duration Durée d'affichage en millisecondes (par défaut 7000ms)
   */
  warning(message: string, title?: string, duration = 7000): string {
    return this.notify({
      id: this.generateId(),
      type: 'warning',
      message,
      title,
      duration,
      autoClose: true
    });
  }
  
  /**
   * Ferme une notification spécifique
   * @param id Identifiant de la notification à fermer
   */
  dismiss(id: string): void {
    this.dismissSubject.next(id);
  }
  
  /**
   * Méthode interne pour envoyer une notification
   * @param notification Objet de notification
   * @returns Identifiant de la notification
   */
  private notify(notification: Notification): string {
    this.notificationSubject.next(notification);
    return notification.id;
  }
  
  /**
   * Génère un identifiant unique pour une notification
   * @returns Identifiant unique
   */
  private generateId(): string {
    return 'notification-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
  }
}

// Exporter une instance singleton du service
export const notificationService = new NotificationService();
export default notificationService;
