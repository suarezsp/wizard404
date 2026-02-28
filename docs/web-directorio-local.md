# Acceso al directorio local desde la aplicación web

La aplicación web puede operar sobre archivos y carpetas del usuario de dos maneras, según el contexto y el navegador.

## Opción 1: Elegir carpeta en el navegador (File System Access API)

En **Chrome** y **Edge** (y otros navegadores que soporten la [File System Access API](https://developer.mozilla.org/en-US/docs/Web/API/File_System_Access_API)), la web puede acceder a una carpeta **que el usuario elige explícitamente** en un diálogo del navegador:

- **Scan**: botón "Elegir carpeta local". La página itera el contenido de la carpeta en el cliente y calcula estadísticas (número de archivos, tamaño total, por extensión). No se envía la ruta al servidor.
- **Import**: botón "Elegir carpeta para importar". La página itera los archivos, filtra por extensiones soportadas (las mismas que el backend) y los sube al servidor mediante `POST /documents/upload` (multipart). Se muestra progreso "Importando X de N".

El navegador **no permite** leer rutas arbitrarias del disco (por ejemplo `C:\Users\foo\Documents`). Solo se puede acceder a archivos/carpetas que el usuario selecciona en el diálogo.

## Opción 2: Ruta en el servidor

En **cualquier navegador** (incluidos Firefox y Safari), o cuando el backend corre en la misma máquina que el usuario:

- **Scan**: campo "Ruta en el servidor" + botón "Escanear servidor". Se llama a `GET /scan?path=...`. El backend escanea ese directorio en la máquina donde corre el servidor.
- **Import**: campo "Ruta en el servidor" + botón "Importar servidor". Se llama a `POST /documents/import?path=...`. El backend importa desde esa ruta local del servidor.

Esta opción es la única disponible en Firefox y Safari para operar sobre datos; también es útil cuando el backend está en tu propio equipo y quieres indicar una ruta local del servidor.

## Resumen de compatibilidad

| Navegador | Elegir carpeta (Scan/Import) | Ruta en el servidor |
|----------|------------------------------|----------------------|
| Chrome, Edge | Sí | Sí |
| Firefox, Safari | No (solo mensaje informativo) | Sí |

En navegadores sin soporte para "Elegir carpeta", la interfaz muestra un texto aclaratorio: *"Para usar una carpeta de tu ordenador, usa Chrome o Edge, o ejecuta el backend en tu máquina e indica la ruta local del servidor."*

## Organize y Cleanup en la web

Las funciones **Organize** (mover archivos a subcarpetas por tipo/fecha/tamaño) y **Cleanup** (detectar y eliminar cache/logs) están disponibles en la **CLI** porque operan sobre rutas del sistema de archivos. En la web, con la File System Access API y permiso de escritura (`{ mode: 'readwrite' }`) sería posible implementar flujos similares (elegir carpeta y ejecutar la lógica en el cliente); de momento se dejan como "Disponible en CLI" y podrían ampliarse en una fase posterior.
