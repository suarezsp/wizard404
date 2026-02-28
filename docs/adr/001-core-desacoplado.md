# ADR 001: Núcleo desacoplado (wizard404_core)

## Contexto

Wizard404 debe ofrecer búsqueda y gestión de documentos desde múltiples interfaces: CLI (w404), API HTTP (FastAPI) y potencialmente otros clientes. La lógica de descubrimiento, extracción y búsqueda es común; duplicarla en cada capa aumentaría la deuda técnica y el riesgo de inconsistencias.

## Decisión

Toda la lógica de dominio (descubrimiento de archivos, extracción de metadatos, búsqueda por contenido, filtros, resúmenes) vive en un paquete **wizard404_core** dentro de `backend/wizard404_core/`. Este paquete:

- No depende de FastAPI, SQLAlchemy ni de la capa HTTP.
- Expone funciones puras o que reciben listas/datos en memoria (p. ej. `search_documents(documents, filters)`).
- Es consumido por la API (que orquesta persistencia en DB y llamadas al core) y por la CLI (que puede usarlo en modo local sin servidor).

La persistencia y la autenticación quedan en `app/`; el core solo opera sobre estructuras de datos (DocumentMetadata, SearchFilters, etc.).

## Consecuencias

- **Positivas**: Un solo lugar para algoritmos de búsqueda y extracción; el core se puede reutilizar como librería en otros proyectos; tests del core no requieren DB ni HTTP; la CLI puede funcionar sin backend para scan/browse en directorio.
- **Negativas**: Hay que mantener la conversión entre modelos de DB (Document) y modelos del core (DocumentMetadata) en la capa de servicios; los desarrolladores deben conocer la frontera entre `app/` y `wizard404_core/`.

Documentación de uso del core como librería: [core-as-library.md](../core-as-library.md).
