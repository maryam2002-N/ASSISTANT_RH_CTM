import React from 'react';
import { CheckCircle, Database, MessageSquare, Trash2, Edit2, BarChart3 } from 'lucide-react';

const ChatHistoryInfo = () => {
  return (
    <div className="p-6 bg-gradient-to-br from-blue-50 to-green-50 rounded-lg border border-blue-200 m-4">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
          <Database className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-gray-800">
            🎉 Historique Persistant Activé !
          </h3>
          <p className="text-sm text-gray-600">
            Vos conversations sont maintenant sauvegardées automatiquement
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div className="space-y-3">
          <h4 className="font-semibold text-gray-700 flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-600" />
            Nouvelles Fonctionnalités
          </h4>
          <div className="space-y-2 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-blue-500" />
              <span>Récupération automatique de l'historique</span>
            </div>
            <div className="flex items-center gap-2">
              <Edit2 className="w-4 h-4 text-orange-500" />
              <span>Renommage des conversations</span>
            </div>
            <div className="flex items-center gap-2">
              <Trash2 className="w-4 h-4 text-red-500" />
              <span>Suppression sécurisée</span>
            </div>
            <div className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-purple-500" />
              <span>Statistiques des conversations</span>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <h4 className="font-semibold text-gray-700">Avantages</h4>
          <div className="space-y-2 text-sm text-gray-600">
            <div>• Plus de perte d'historique après fermeture</div>
            <div>• Accès rapide aux conversations précédentes</div>
            <div>• Synchronisation automatique</div>
            <div>• Interface améliorée avec métadonnées</div>
          </div>
        </div>
      </div>

      <div className="p-3 bg-white rounded border border-blue-200">
        <h5 className="font-medium text-gray-700 mb-2">💡 Comment utiliser :</h5>
        <div className="text-sm text-gray-600 space-y-1">
          <div>1. Vos conversations sont automatiquement sauvegardées</div>
          <div>2. Cliquez sur une conversation dans la sidebar pour la reprendre</div>
          <div>3. Utilisez les boutons ✏️ et 🗑️ pour gérer vos conversations</div>
          <div>4. Le bouton 🔄 actualise la liste si nécessaire</div>
        </div>
      </div>
    </div>
  );
};

export default ChatHistoryInfo;
