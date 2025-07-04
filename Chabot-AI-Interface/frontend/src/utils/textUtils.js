/**
 * Utilitaires pour la gestion des textes dans l'interface
 */

/**
 * Tronque un texte à une longueur donnée en gardant les mots entiers
 * @param {string} text - Le texte à tronquer
 * @param {number} maxLength - La longueur maximale (par défaut: 40)
 * @returns {string} - Le texte tronqué avec "..." si nécessaire
 */
export const truncateText = (text, maxLength = 40) => {
  if (!text || text.length <= maxLength) {
    return text;
  }

  // Trouve le dernier espace avant la limite
  const truncated = text.substring(0, maxLength);
  const lastSpaceIndex = truncated.lastIndexOf(' ');
  
  // Si on trouve un espace et qu'il n'est pas trop proche du début
  if (lastSpaceIndex > maxLength * 0.6) {
    return truncated.substring(0, lastSpaceIndex) + '...';
  }
  
  // Sinon, tronque simplement à la limite
  return truncated + '...';
};

/**
 * Génère un titre intelligent pour une conversation basé sur le premier message
 * @param {string} firstMessage - Le premier message de la conversation
 * @param {number} maxLength - La longueur maximale du titre (par défaut: 50)
 * @returns {string} - Le titre généré
 */
export const generateChatTitle = (firstMessage, maxLength = 50) => {
  if (!firstMessage) {
    return 'Nouvelle conversation';
  }

  // Nettoie le message (supprime les espaces en trop, sauts de ligne, etc.)
  const cleanMessage = firstMessage.trim().replace(/\s+/g, ' ');
  
  // Trouve la première phrase ou question
  const sentenceEnd = /[.!?]\s/.exec(cleanMessage);
  let title = sentenceEnd ? cleanMessage.substring(0, sentenceEnd.index + 1) : cleanMessage;
  
  // Tronque si nécessaire
  if (title.length > maxLength) {
    title = truncateText(title, maxLength);
  }
  
  return title || 'Nouvelle conversation';
};

/**
 * Crée un tooltip avec le texte complet si le texte est tronqué
 * @param {string} text - Le texte original
 * @param {string} displayText - Le texte affiché (possiblement tronqué)
 * @returns {string|null} - Le texte du tooltip ou null si pas nécessaire
 */
export const getTooltipText = (text, displayText) => {
  return displayText.endsWith('...') ? text : null;
};
