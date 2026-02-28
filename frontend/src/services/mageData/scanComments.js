/**
 * services/mageData/scanComments.js - Frases del mago segun el tipo de archivos dominantes en un scan.
 * Usado en Scan tras mostrar resultados. Los componentes consumen getScanComment; no definen estas frases.
 */

const EXT_TO_CATEGORY = {
  programming: ['.java', '.c', '.h', '.py', '.js', '.ts', '.go', '.rs', '.sh', '.bat', '.cpp', '.hpp', '.cs', '.rb', '.php', '.swift', '.kt'],
  excel: ['.xlsx', '.xls', '.csv'],
  pdf: ['.pdf'],
  audio: ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma'],
  video: ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.wmv', '.flv'],
  images: ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff', '.tif', '.heic', '.heif'],
}

const PHRASE_BY_CATEGORY = {
  programming:
    'Oh, otro mago por lo que veo... quizá te subestimé. No sabía que manejabas las artes del código tan bien como yo...',
  excel:
    'Ah, la pesadilla de HHRR y Finanzas! Podría dárselo a uno de mis goblins y te lo pasaría a una BBDD en menos de lo que canta un gallo!',
  pdf:
    'Pergaminos clásicos. Si alguno está encriptado, ni mis hechizos pueden abrirlo... pero los demás los leo en un susurro.',
  audio:
    'Canciones y runas sonoras. Cuidado con los que dicen que te hipnotizan... a mí me gustan.',
  video:
    'Visiones en movimiento. Los oráculos del futuro en formato .mp4. Qué tiempos, qué tiempos.',
  images:
    'Retratos y mapas visuales. Un mago con muchos PNG es un mago que documenta bien sus experimentos.',
}

/**
 * Dado by_extension (ej. { ".java": 60, ".xml": 11 }), devuelve la categoria dominante
 * y la frase del mago, o null si no hay match.
 */
export function getScanComment(byExtension) {
  if (!byExtension || typeof byExtension !== 'object') return null
  const entries = Object.entries(byExtension).filter(([, count]) => count > 0)
  if (entries.length === 0) return null
  const sorted = entries.sort((a, b) => b[1] - a[1])
  const topExt = sorted[0][0].toLowerCase()
  const topCount = sorted[0][1]
  for (const [category, exts] of Object.entries(EXT_TO_CATEGORY)) {
    if (exts.includes(topExt)) {
      const phrase = PHRASE_BY_CATEGORY[category]
      return phrase || null
    }
  }
  return null
}

export { EXT_TO_CATEGORY, PHRASE_BY_CATEGORY }
