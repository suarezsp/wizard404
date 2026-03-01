# Carpeta de demo para el CLI (alta entropía)

Esta carpeta está pensada para **demos en vivo** del proyecto: permite mostrar el mensaje de **alta entropía** del CLI y probar Scan, vista por tipo, vista por directorio y Organize/Cleanup.

## Cómo generar la carpeta `chaos`

La estructura desordenada se crea con el script:

```bash
./scripts/create-demo-chaos-dir.sh
```

El script crea `demo/chaos/` con muchos subdirectorios anidados y archivos vacíos de **múltiples extensiones** (txt, md, pdf, py, js, json, csv, etc.), de forma que:

- **num_extensions > 12** y **total_files / num_extensions < 8**  
  → el scan muestra: *"High entropy... lots of disorder... recommend organizing."*

- Puedes probar **View by type**, **View by directory** y **Organize/Cleanup** con estadísticas ricas.

Al finalizar, el script imprime la ruta absoluta de `demo/chaos` para usarla directamente con el CLI (por ejemplo `./w404` y luego Scan sobre esa ruta).

## Uso en la demo

1. Ejecutar una vez: `./scripts/create-demo-chaos-dir.sh` (o usar la carpeta ya generada si está commiteada).
2. En el CLI, hacer **Scan** sobre `demo/chaos` (o la ruta que haya impreso el script).
3. Revisar el resumen (alta entropía), **View by type**, **View by directory** y, si quieres, **Organize** o **Cleanup**.
