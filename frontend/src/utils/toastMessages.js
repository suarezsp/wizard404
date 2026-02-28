/**
 * toastMessages.js - Mapeo de mensajes del backend a textos amigables para toasts.
 */
const MAP = {
  'path is required': 'Indica una ruta.',
  'Path must be a directory': 'Ese directorio no existe o no es válido.',
  'Path invalid or too long': 'Ruta inválida o demasiado larga.',
  'Only local filesystem paths are allowed': 'Solo se permiten rutas locales del sistema de archivos.',
  'Scan failed': 'Error al escanear el directorio.',
  'Document not found': 'Documento no encontrado.',
  'Invalid path': 'Ruta inválida.',
}

export function friendlyMessage(backendMessage) {
  if (!backendMessage || typeof backendMessage !== 'string') return backendMessage
  const trimmed = backendMessage.trim()
  for (const [key, value] of Object.entries(MAP)) {
    if (trimmed.includes(key)) return value
  }
  return trimmed
}
