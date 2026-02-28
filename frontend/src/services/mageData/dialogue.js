/**
 * services/mageData/dialogue.js - Textos por escena para el mago (unica fuente, sin logica).
 * Usado por MageContext para sayForScene(). Los componentes no deben definir estos datos.
 */
export const DIALOGUE_BY_SCENE = {
  login: [
    'Bienvenido forastero! Dime, quien eres?',
    'Quien se acerca al santuario?...',
    'Identificate, viajero. Nombre y palabra secreta.',
    'Entra, pero primero dime tu nombre.',
    'Quien osa entrar en mi santuario? Identificate, viajero!',
    'Tú de nuevo, viajero. ¿Qué necesitas?',
  ],
  register: [
    'Ah, un nuevo aprendiz. Elige bien tu nombre.',
    'Registrate y tendras acceso a los pergaminos.',
    'Bienvenido al gremio. Crea tu cuenta aqui.',
    'Un nuevo mago en la torre. Elige tu identidad.',
    'Con esto comenzarás tu viaje como mi aprendiz.',
  ],
  dashboard: [
    'Aqui veras todos los pergaminos indexados.',
    'Busca con la lupa mágica y encontraras.',
    'Estos son tus documentos. Busca o importa mas.',
    'El oráculo del Índice esta a tu servicio. Busca lo que necesites.',
    'Invoca rutas para añadir documentos al caldero.',
  ],
  documentDetail: [
    'Este es el contenido del documento.',
    'Aqui esta lo que buscabas. Lee con calma.',
    'El pergamino desplegado. Resumen arriba si hay.',
    'Detalle del documento. Vuelve atras para ver mas.',
  ],
  loading: [
    'Vale, dejame esto a mi.. Tengo un hechizo que puede servir...',
    'Un momento, que consulto los archivos...',
    'Hmm, casi listo...',
    'Buscando en el grimorio...',
    'Un segundo, estoy leyendo...',
    'Consultando los registros...',
    'Es un poco incómodo si estás mirando...',
  ],
  home: [
    'Elige el hechizo que quieres practicas hoy.',
    'Selecciona una de las runas para continuar.',
    'Bienvenido al santuario. Que deseas hacer?',
  ],
  scan: [
    'Oh! La runa del escaneo... Un clásico. Escanea un directorio de tu ordenador. Tiene el poder de mostrarte los archivos que contiene.',
    'Indica la ruta en tu ordenador para analizar.',
    'Para usar este hechizo, tienes que proporcionar la ruta de tu ordenador que deseas analizar.',
    'Este hechizo es poderoso y no es peligroso. Solo analiza el contenido de la ruta que proporcionas. Clásico entre novicios.',
  ],
  import: [
    'Importa documentos desde una ruta del servidor al indice.',
    'Anade archivos o carpetas al indice con la ruta.',
  ],
  search: [
    'Busca por palabras clave en los documentos indexados.',
    'Usa la lupa. Busqueda semantica disponible.',
  ],
  explore: [
    'Navega por los documentos del indice. Click para ver detalle.',
    'Aqui esta todo lo que has indexado.',
  ],
  organize: [
    'Organizar por tipo o fecha esta disponible en la CLI.',
    'Para mover archivos en carpetas, usa el comando w404.',
  ],
  cleanup: [
    'Limpiar cache y logs esta disponible en la CLI.',
    'Para limpieza en tu maquina, ejecuta la CLI.',
  ],
}
