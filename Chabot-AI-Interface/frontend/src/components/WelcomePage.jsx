import React from 'react';
import { MessageSquare, HelpCircle, FileText, Mail, Briefcase, Users } from 'lucide-react';

const WelcomePage = ({ onSuggestionClick }) => {
  const suggestions = [
    {
      icon: HelpCircle,
      title: "Comment pouvez-vous m'aider aujourd'hui ?",
      description: "Découvrez les capacités de l'IA",
      message: "Comment pouvez-vous m'aider aujourd'hui ?"
    },
    {
      icon: Briefcase,
      title: "Expliquez-moi les politiques RH",
      description: "Obtenez des explications détaillées",
      message: "Expliquez-moi les politiques RH de l'entreprise"
    },
    {
      icon: FileText,
      title: "Aidez-moi à planifier un projet",
      description: "Assistance pour la planification",
      message: "Aidez-moi à planifier un projet RH"
    },
    {
      icon: Mail,
      title: "Rédigez un email professionnel",
      description: "Aide à la création de contenu",
      message: "Aidez-moi à rédiger un email professionnel"
    }
  ];

  return (
    <div className="flex-1 flex items-center justify-center p-8">
      <div className="max-w-4xl w-full text-center">
        {/* Icône principale */}
        <div className="mb-8">
          <div className="w-20 h-20 bg-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <MessageSquare className="w-10 h-10 text-white" />
          </div>
          <div className="space-y-2">
            <h1 className="text-3xl font-bold text-gray-900">
              Bienvenue dans l'Assistant IA RH
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Commencez une conversation avec notre assistant IA. Posez des questions, obtenez 
              de l'aide ou explorez de nouvelles idées !
            </p>
          </div>
        </div>

        {/* Grille des suggestions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          {suggestions.map((suggestion, index) => {
            const Icon = suggestion.icon;
            return (
              <button
                key={index}
                onClick={() => onSuggestionClick(suggestion.message)}
                className="p-6 bg-white border border-gray-200 rounded-xl hover:bg-blue-50 hover:border-blue-200 transition-all duration-200 text-left group"
              >
                <div className="flex items-start space-x-4">
                  <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
                    <Icon className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">
                      {suggestion.title}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {suggestion.description}
                    </p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Informations supplémentaires */}
        <div className="text-sm text-gray-500 space-y-2">
          <p>💡 Astuce : Vous pouvez poser des questions sur les politiques RH, demander de l'aide pour rédiger des documents, ou explorer les CV disponibles.</p>
          <div className="flex items-center justify-center space-x-4 mt-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-xs text-gray-600">En ligne</span>
            </div>
            <span className="text-xs text-gray-400">•</span>
            <span className="text-xs text-gray-600">Propulsé par l'IA avancée</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;
