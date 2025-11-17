# Bitácora de Decisiones y Flujo de Trabajo

Este documento registra las justificaciones detrás de ciertas decisiones y prácticas adoptadas durante la gestión de este proyecto.

## Gestión de Ramas Post-Fusión

### ¿Por qué borrar una rama después de fusionarla (merge)?

Una vez que una rama de funcionalidad (ej. `feature/password-generator`) ha sido integrada exitosamente en la rama principal (`main`), es una buena práctica eliminarla tanto localmente como en el repositorio remoto. Las razones son las siguientes:

*   **Claridad y Limpieza:** Evita la acumulación de ramas obsoletas que ya cumplieron su propósito. Un repositorio con solo ramas activas es mucho más fácil de navegar y entender para todos los colaboradores.
*   **Reducción de Confusiones:** Minimiza el riesgo de que alguien, por error, continúe trabajando sobre una rama ya fusionada o intente integrarla de nuevo, lo cual podría reintroducir bugs o cambios no deseados.
*   **Enfoque en el Trabajo Actual:** Ayuda al equipo a centrarse únicamente en las funcionalidades que están en desarrollo activo, sin el ruido de las que ya fueron completadas.

## Deshaciendo Cambios: `reset` vs. `revert`

Git ofrece dos comandos principales para deshacer cambios: `git reset` y `git revert`. Aunque ambos pueden "deshacer" commits, funcionan de maneras muy diferentes y su uso depende de si los cambios ya han sido compartidos en un repositorio remoto.

### `git reset`

*   **Qué hace:** Modifica directamente el historial de commits. Mueve el puntero de la rama actual a un commit anterior, efectivamente "borrando" los commits que le seguían.
*   **Cuándo usarlo:** Es ideal para deshacer cambios en tu **repositorio local** que **aún no has subido** a un repositorio compartido (con `git push`). Permite limpiar tu historial local antes de compartirlo, por ejemplo, para combinar varios commits pequeños en uno solo o para descartar experimentos fallidos.
*   **Peligro:** **Nunca debe usarse en ramas públicas o compartidas** (como `main` o `develop`). Si se usa en una rama que otros ya han clonado, reescribe un historial que ya es público. Esto causa inconsistencias y conflictos graves para los demás colaboradores, que tendrán una versión diferente de la historia del proyecto.

### `git revert`

*   **Qué hace:** No borra el historial. En su lugar, crea un **nuevo commit** que aplica los cambios inversos al commit que se quiere deshacer. Si un commit añadió una línea, el `revert` creará un nuevo commit que la elimina.
*   **Cuándo usarlo:** Es la forma **segura y profesional** de deshacer cambios en una **rama pública o compartida**.
*   **Ventajas:** Mantiene la integridad y la transparencia del historial. Deja un registro claro de que un cambio fue introducido y luego deshecho explícitamente, lo cual es crucial para la auditoría y el trabajo en equipo. No causa problemas a otros colaboradores porque no altera la historia pasada, solo añade un nuevo estado al proyecto.

## Análisis del Proceso de Conflicto de Fusión (Merge Conflict)

Un conflicto de fusión es una parte inevitable del trabajo con Git en un entorno colaborativo. Comprender su origen y cómo resolverlo es fundamental para mantener la integridad del código.

### Origen del Conflicto

Un conflicto ocurre cuando Git no puede decidir automáticamente cómo fusionar dos ramas. El escenario más común es cuando dos ramas diferentes han modificado **las mismas líneas en el mismo archivo**. Git no tiene forma de saber qué versión es la "correcta" o cómo combinar los cambios, por lo que detiene el proceso de fusión y le pide al desarrollador que tome una decisión.

### Proceso de Solución

La resolución de un conflicto es un proceso manual que requiere la intervención del desarrollador:

1.  **Detección:** Git detiene la fusión (`git merge` o `git pull`) y marca los archivos conflictivos.
2.  **Inspección:** El desarrollador debe abrir los archivos marcados. Dentro de ellos, Git inserta marcadores visuales (`<<<<<<< HEAD`, `=======`, `>>>>>>> nombre-rama`) para delimitar claramente qué líneas provienen de la rama actual (`HEAD`) y cuáles provienen de la rama que se está intentando fusionar.
3.  **Resolución Manual:** El desarrollador edita el archivo para eliminar los marcadores de Git y dejar el código en el estado final deseado. Esto puede implicar quedarse con una de las versiones, con la otra, o combinar ambas de una manera lógica.
4.  **Finalización:** Una vez que el archivo se ha corregido, se le informa a Git que el conflicto está resuelto usando `git add <archivo-resuelto>`. Finalmente, se completa la fusión con `git commit`, creando un nuevo "merge commit" que une las dos historias y contiene la resolución del conflicto.

### Importancia para la Integridad del Código

Manejar correctamente los conflictos es crucial porque:

*   **Previene la Pérdida de Trabajo:** Asegura que los cambios de un desarrollador no sobrescriban accidentalmente los de otro.
*   **Fuerza una Decisión Consciente:** Obliga a los desarrolladores a comunicarse y a tomar una decisión informada sobre cómo deben integrarse los cambios que compiten entre sí.
*   **Garantiza un Código Funcional:** Al resolver los conflictos manualmente, se garantiza que la versión final del código en la rama principal sea coherente, esté completa y funcione como se espera, manteniendo así la calidad y la integridad de todo el proyecto.
