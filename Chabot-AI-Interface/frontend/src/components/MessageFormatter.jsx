import React from 'react';

const MessageFormatter = ({ content }) => {
  // Fonction pour détecter et formater les tableaux markdown
  const formatMarkdownTable = (text) => {
    const lines = text.split('\n');
    let inTable = false;
    let tableRows = [];
    let otherContent = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Détecter le début d'un tableau (ligne avec |)
      if (line.includes('|') && !inTable) {
        inTable = true;
        tableRows = [line];
      }
      // Continuer le tableau
      else if (line.includes('|') && inTable) {
        tableRows.push(line);
      }
      // Fin du tableau
      else if (inTable && !line.includes('|')) {
        inTable = false;
        // Traiter le tableau
        otherContent.push(renderTable(tableRows));
        tableRows = [];
        if (line.trim()) {
          otherContent.push(<p key={i} className="my-2">{line}</p>);
        }
      }
      // Contenu normal
      else if (!inTable && line.trim()) {
        otherContent.push(<p key={i} className="my-2">{formatText(line)}</p>);
      }
    }
    
    // Si le texte se termine par un tableau
    if (inTable && tableRows.length > 0) {
      otherContent.push(renderTable(tableRows));
    }
    
    return otherContent;
  };

  // Fonction pour rendre un tableau HTML
  const renderTable = (rows) => {
    if (rows.length < 2) return null;
    
    const headerRow = rows[0];
    const separatorRow = rows[1];
    const dataRows = rows.slice(2);
    
    // Parser les en-têtes
    const headers = headerRow.split('|')
      .map(h => h.trim())
      .filter(h => h);
    
    // Parser les données
    const data = dataRows.map((row, index) => {
      const cells = row.split('|')
        .map(cell => cell.trim())
        .filter(cell => cell);
      return { id: index, cells };
    });
    
    return (
      <div key={`table-${Math.random()}`} className="my-4 overflow-x-auto">
        <table className="min-w-full bg-white border border-gray-200 rounded-lg shadow-sm">
          <thead className="bg-gray-50">
            <tr>
              {headers.map((header, index) => (
                <th 
                  key={index}
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b"
                >
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.map((row) => (
              <tr key={row.id} className="hover:bg-gray-50">
                {row.cells.map((cell, cellIndex) => (
                  <td 
                    key={cellIndex}
                    className="px-4 py-3 text-sm text-gray-900 border-b"
                  >
                    {formatCellContent(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  // Fonction pour formater le contenu des cellules
  const formatCellContent = (cell) => {
    // Gérer les liens HTML d'abord
    const htmlLinkRegex = /<a\s+href="([^"]+)"[^>]*>([^<]+)<\/a>/g;
    let processedCell = cell;
    const htmlLinks = [];
    
    // Extraire les liens HTML et les remplacer par des placeholders
    let htmlMatch;
    let htmlIndex = 0;
    while ((htmlMatch = htmlLinkRegex.exec(cell)) !== null) {
      const placeholder = `__HTML_LINK_${htmlIndex}__`;
      const url = htmlMatch[1].replace('./app/static/cvs/', 'http://localhost:8000/static/cvs/');
      const linkText = htmlMatch[2];
      htmlLinks.push({ placeholder, url, linkText });
      processedCell = processedCell.replace(htmlMatch[0], placeholder);
      htmlIndex++;
    }
    
    // Gérer les liens markdown
    const markdownLinkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    
    if (markdownLinkRegex.test(processedCell) || htmlLinks.length > 0) {
      // Traiter les liens markdown
      const parts = processedCell.split(markdownLinkRegex);
      const elements = [];
      
      for (let i = 0; i < parts.length; i += 3) {
        if (parts[i]) {
          let textPart = parts[i];
          
          // Remplacer les placeholders HTML par des liens
          htmlLinks.forEach(({ placeholder, url, linkText }) => {
            if (textPart.includes(placeholder)) {
              const textParts = textPart.split(placeholder);
              const finalElements = [];
              
              textParts.forEach((part, idx) => {
                if (part) finalElements.push(part);
                if (idx < textParts.length - 1) {
                  finalElements.push(
                    <a 
                      key={`html-cell-${placeholder}-${idx}`}
                      href={url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 underline"
                    >
                      {linkText}
                    </a>
                  );
                }
              });
              
              textPart = finalElements;
            }
          });
          
          elements.push(textPart);
        }
        
        // Gérer les liens markdown
        if (parts[i + 1] && parts[i + 2]) {
          const correctedUrl = parts[i + 2].replace('./app/static/cvs/', 'http://localhost:8000/static/cvs/');
          elements.push(
            <a 
              key={`md-cell-${i}`}
              href={correctedUrl} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              {parts[i + 1]}
            </a>
          );
        }
      }
      
      return elements;
    }
    
    // Si pas de liens markdown mais des liens HTML
    if (htmlLinks.length > 0) {
      let result = processedCell;
      const elements = [];
      
      htmlLinks.forEach(({ placeholder, url, linkText }) => {
        const parts = result.split(placeholder);
        const newResult = [];
        
        parts.forEach((part, idx) => {
          if (part) newResult.push(part);
          if (idx < parts.length - 1) {
            newResult.push(
              <a 
                key={`html-cell-final-${placeholder}-${idx}`}
                href={url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 underline"
              >
                {linkText}
              </a>
            );
          }
        });
        
        result = newResult;
      });
      
      return result;
    }
    
    return cell;
  };

  // Fonction pour formater le texte normal
  const formatText = (text) => {
    // Gérer les liens HTML d'abord
    const htmlLinkRegex = /<a\s+href="([^"]+)"[^>]*>([^<]+)<\/a>/g;
    let processedText = text;
    const htmlLinks = [];
    
    // Extraire les liens HTML et les remplacer par des placeholders
    let htmlMatch;
    let htmlIndex = 0;
    while ((htmlMatch = htmlLinkRegex.exec(text)) !== null) {
      const placeholder = `__HTML_LINK_${htmlIndex}__`;
      const url = htmlMatch[1].replace('./app/static/cvs/', 'http://localhost:8000/static/cvs/');
      const linkText = htmlMatch[2];
      htmlLinks.push({ placeholder, url, linkText });
      processedText = processedText.replace(htmlMatch[0], placeholder);
      htmlIndex++;
    }
    
    // Gérer les liens markdown
    const markdownLinkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    
    if (markdownLinkRegex.test(processedText) || htmlLinks.length > 0) {
      // Traiter les liens markdown
      const parts = processedText.split(markdownLinkRegex);
      const elements = [];
      
      for (let i = 0; i < parts.length; i += 3) {
        if (parts[i]) {
          let textPart = parts[i];
          
          // Remplacer les placeholders HTML par des liens
          htmlLinks.forEach(({ placeholder, url, linkText }) => {
            if (textPart.includes(placeholder)) {
              const textParts = textPart.split(placeholder);
              const finalElements = [];
              
              textParts.forEach((part, idx) => {
                if (part) finalElements.push(part);
                if (idx < textParts.length - 1) {
                  finalElements.push(
                    <a 
                      key={`html-${placeholder}-${idx}`}
                      href={url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 underline"
                    >
                      {linkText}
                    </a>
                  );
                }
              });
              
              textPart = finalElements;
            }
          });
          
          elements.push(textPart);
        }
        
        // Gérer les liens markdown
        if (parts[i + 1] && parts[i + 2]) {
          const correctedUrl = parts[i + 2].replace('./app/static/cvs/', 'http://localhost:8000/static/cvs/');
          elements.push(
            <a 
              key={`md-${i}`}
              href={correctedUrl} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              {parts[i + 1]}
            </a>
          );
        }
      }
      
      return elements;
    }
    
    // Si pas de liens markdown mais des liens HTML
    if (htmlLinks.length > 0) {
      let result = processedText;
      const elements = [];
      
      htmlLinks.forEach(({ placeholder, url, linkText }) => {
        const parts = result.split(placeholder);
        const newResult = [];
        
        parts.forEach((part, idx) => {
          if (part) newResult.push(part);
          if (idx < parts.length - 1) {
            newResult.push(
              <a 
                key={`html-final-${placeholder}-${idx}`}
                href={url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 underline"
              >
                {linkText}
              </a>
            );
          }
        });
        
        result = newResult;
      });
      
      return result;
    }
    
    return text;
  };

  // Traitement principal
  const formattedContent = formatMarkdownTable(content);
  
  return (
    <div className="message-content-formatted">
      {formattedContent.length > 0 ? formattedContent : (
        <p className="whitespace-pre-wrap">{content}</p>
      )}
    </div>
  );
};

export default MessageFormatter;
