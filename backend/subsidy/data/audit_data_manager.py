"""
Gestionnaire de données pour les audits vocaux
---------------------------------------------
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

import logging
import time
logger = logging.getLogger("subsidy.audit")

# Chemin vers le fichier de stockage des audits
AUDITS_FILE = os.path.join(os.path.dirname(__file__), "audits.json")

# S'assurer que le fichier existe
if not os.path.exists(os.path.dirname(AUDITS_FILE)):
    os.makedirs(os.path.dirname(AUDITS_FILE), exist_ok=True)

class AuditDataManager:
    """Gestionnaire de données pour les audits vocaux"""
    
    def __init__(self):
        """Initialise le gestionnaire de données d'audit"""
        self.audits = {}
        self._load_audits()
    
    def _load_audits(self):
        """Charge les audits depuis le fichier"""
        try:
            if os.path.exists(AUDITS_FILE):
                with open(AUDITS_FILE, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self.audits = json.loads(content)
                    else:
                        self.audits = {}
            else:
                # Initialiser avec un dictionnaire vide
                self.audits = {}
                # Créer le fichier vide
                with open(AUDITS_FILE, 'w', encoding='utf-8') as f:
                    f.write('{}')
        except Exception as e:
            logger.error(f"Erreur lors du chargement des audits: {e}")
            self.audits = {}
    
    def _save_audits(self):
        start_time = time.time()
        try:
            with open(AUDITS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.audits, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des audits: {e}")
        finally:
            end_time = time.time()
            logger.info(f"Audit save took {end_time - start_time:.2f} seconds")
    
    def create_audit(self, user_id: str, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un nouvel audit pour un utilisateur"""
        audit_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        audit = {
            "id": audit_id,
            "userId": user_id,
            "createdAt": now,
            "updatedAt": now,
            "auditData": audit_data
        }
        
        # Ajouter l'audit à la collection
        if user_id not in self.audits:
            self.audits[user_id] = []
        
        self.audits[user_id].append(audit)
        self._save_audits()
        
        return audit
    
    def get_audit(self, audit_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un audit par son ID"""
        for user_audits in self.audits.values():
            for audit in user_audits:
                if audit["id"] == audit_id:
                    return audit
        return None
    
    def get_user_audits(self, user_id: str) -> List[Dict[str, Any]]:
        """Récupère tous les audits d'un utilisateur"""
        return self.audits.get(user_id, [])
    
    def update_audit(self, audit_id: str, audit_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un audit existant"""
        for user_id, user_audits in self.audits.items():
            for i, audit in enumerate(user_audits):
                if audit["id"] == audit_id:
                    # Mettre à jour les données d'audit
                    self.audits[user_id][i]["auditData"] = audit_data
                    self.audits[user_id][i]["updatedAt"] = datetime.now().isoformat()
                    self._save_audits()
                    return self.audits[user_id][i]
        return None
    
    def delete_audit(self, audit_id: str) -> bool:
        """Supprime un audit"""
        for user_id, user_audits in self.audits.items():
            for i, audit in enumerate(user_audits):
                if audit["id"] == audit_id:
                    # Supprimer l'audit
                    del self.audits[user_id][i]
                    self._save_audits()
                    return True
        return False


# Singleton pour accéder au gestionnaire de données d'audit
_audit_data_manager = None

def get_audit_data_manager() -> AuditDataManager:
    """Récupère l'instance du gestionnaire de données d'audit"""
    global _audit_data_manager
    if _audit_data_manager is None:
        _audit_data_manager = AuditDataManager()
    return _audit_data_manager
