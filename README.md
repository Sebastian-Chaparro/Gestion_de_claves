# Gestor de Contraseñas Local

Este es un gestor de contraseñas de escritorio diseñado para Windows, que permite almacenar y gestionar tus credenciales de forma segura y completamente local. La aplicación se enfoca en la privacidad y la facilidad de uso, ofreciendo funcionalidades CRUD (Crear, Leer, Actualizar, Eliminar) y un generador de contraseñas robusto, todo ello con una interfaz de usuario inspirada en el estilo de Windows 11.

## Características

*   **Almacenamiento 100% Local:** Todas tus contraseñas se guardan en un archivo cifrado en tu máquina local. No hay conexión a internet ni almacenamiento en la nube, garantizando la máxima privacidad.
*   **Cifrado Robusto:** Utiliza cifrado AES-256 a través de la biblioteca `cryptography` de Python. La clave de cifrado se deriva de una contraseña maestra que solo tú conoces, usando PBKDF2 para mayor seguridad.
*   **Interfaz de Usuario Estilo Windows 11:**
    *   Diseño limpio y moderno inspirado en Fluent Design.
    *   Controles y elementos visuales que buscan replicar la estética de Windows 11.
    *   **Barra de Búsqueda:** Filtra rápidamente tus entradas de contraseña por nombre de servicio.
    *   **Botones de Copia Rápida:** Copia el nombre de usuario y la contraseña al portapapeles con un solo clic desde la vista de detalles.
    *   **Nota sobre Transparencias (Mica/Acrylic) e Iconos:** Aunque se ha intentado replicar el estilo de Windows 11, la implementación de efectos de transparencia avanzados como Mica o Acrylic puede ser limitada por la biblioteca `customtkinter` y las APIs de Python para GUI. Es posible que estos efectos no se visualicen de forma idéntica a las aplicaciones nativas de Windows 11 sin un desarrollo más profundo a nivel de sistema operativo. Actualmente, los botones utilizan texto. La integración de iconos Fluent UI requeriría la inclusión de archivos de iconos externos o fuentes específicas, lo cual se considera una mejora futura para mantener la simplicidad del proyecto.
*   **Funcionalidades CRUD Completas:**
    *   **Crear:** Añade nuevas entradas de servicio, usuario, contraseña y notas.
    *   **Leer:** Visualiza los detalles de tus entradas de contraseña.
    *   **Actualizar:** Edita la información de las entradas existentes.
    *   **Eliminar:** Borra entradas de forma segura con confirmación.
*   **Generador de Contraseñas Seguras:** Crea contraseñas aleatorias y robustas, personalizables en longitud y tipos de caracteres (mayúsculas, minúsculas, números, símbolos). Incluye opción para copiar al portapapeles.
*   **Documentación:** Código bien comentado con docstrings y un `README.md` detallado.

## Requisitos

*   Python 3.x
*   pip (gestor de paquetes de Python)

## Instalación

Sigue estos pasos para configurar y ejecutar la aplicación en tu sistema:

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/tu_usuario/Gestion_de_claves.git
    cd Gestion_de_claves
    ```
    *(Reemplaza `https://github.com/tu_usuario/Gestion_de_claves.git` con la URL real de tu repositorio si lo has subido a GitHub)*

2.  **Crear un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Uso

1.  **Iniciar la aplicación:**
    ```bash
    python main.py
    ```

2.  **Establecer/Ingresar Contraseña Maestra:**
    *   La primera vez que ejecutes la aplicación, se te pedirá que establezcas una contraseña maestra. Esta contraseña es crucial, ya que se utiliza para cifrar y descifrar todas tus credenciales. **¡Guárdala en un lugar seguro y no la olvides!**
    *   **Importante:** La "contraseña maestra" es la clave real para acceder y proteger tus datos. `MainAppFrame` es el componente principal de la interfaz de usuario de la aplicación y *no* es la contraseña maestra.
    *   En ejecuciones posteriores, deberás ingresar esta misma contraseña maestra para acceder a tus datos.

3.  **Navegación y Funcionalidades:**
    *   **Panel Izquierdo:** Contiene botones para "Añadir Nueva" entrada, "Generar Clave", "Editar Entrada" y "Eliminar Entrada".
    *   **Barra de Búsqueda:** Utiliza la barra de búsqueda en la parte superior de la lista de contraseñas para filtrar las entradas por nombre de servicio.
    *   **Lista de Contraseñas:** En el centro, verás una lista de tus servicios guardados. Haz clic en uno para ver sus detalles.
    *   **Panel Derecho:** Muestra los detalles de la entrada seleccionada (Servicio, Usuario, Contraseña, Notas). Junto al usuario y la contraseña, encontrarás botones para copiarlos rápidamente al portapapeles.
    *   **Añadir Nueva:** Abre un diálogo para ingresar los datos de una nueva credencial.
    *   **Editar Entrada:** Edita la entrada actualmente seleccionada. El nombre del servicio no se puede cambiar.
    *   **Eliminar Entrada:** Elimina la entrada seleccionada previa confirmación.
    *   **Generar Clave:** Abre un generador de contraseñas donde puedes configurar la longitud y los tipos de caracteres. La contraseña generada se puede copiar al portapapeles.

## Estructura del Proyecto

*   `main.py`: Archivo principal de la aplicación que contiene la lógica de la UI, gestión de datos y las clases de los diálogos.
*   `requirements.txt`: Lista de dependencias de Python necesarias para el proyecto.
*   `passwords.json.enc`: Archivo cifrado donde se almacenan tus contraseñas.
*   `salt.bin`: Archivo que contiene el "salt" criptográfico utilizado para la derivación de la clave maestra.

## Consideraciones de Seguridad

*   **Contraseña Maestra:** La seguridad de tus contraseñas depende directamente de la fortaleza de tu contraseña maestra. Usa una contraseña larga, compleja y única.
*   **Almacenamiento Local:** Al ser una aplicación local, tus datos están tan seguros como tu sistema operativo. Asegúrate de que tu ordenador esté protegido con un buen antivirus y un firewall.
*   **No Compartir:** Nunca compartas tu contraseña maestra ni el archivo `passwords.json.enc` con nadie.

---
Desarrollado con Python y `customtkinter`.
## Característica: Generador de Contraseñas
## Liena modificada localmente.
## Liena modificada en linea.

