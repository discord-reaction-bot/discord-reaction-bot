# DiscordBotReacciones

Proyecto compuesto por dos partes:

1. **El bot de Discord** (`bot/DiscordBotReacciones/`) — reacciona automáticamente a los mensajes de usuarios específicos, con emoji configurable por usuario, probabilidad de reacción, soporte multi-servidor y persistencia en JSON.
2. **La página web** (`docs/`) — presenta el bot, explica sus comandos y funciones, y además sirve como plantilla estática reutilizable para otros proyectos similares.

---

## Índice

**Parte 1 — El bot**
1. [Crear la aplicación y el bot en Discord](#1-crear-la-aplicación-y-el-bot-en-discord)
2. [Configurar el token de forma segura (.env)](#2-configurar-el-token-de-forma-segura-env)
3. [Estructura del bot](#3-estructura-del-bot)
4. [Instalación y primer arranque](#4-instalación-y-primer-arranque)
5. [Invitar el bot a un servidor](#5-invitar-el-bot-a-un-servidor)
6. [Encender y apagar el bot](#6-encender-y-apagar-el-bot)
7. [Comandos disponibles](#7-comandos-disponibles)
8. [Ejecución local: qué significa y cómo funciona](#8-ejecución-local-qué-significa-y-cómo-funciona)
9. [Notas de seguridad](#9-notas-de-seguridad)

**Parte 2 — La página web**
10. [Qué es esta web](#10-qué-es-esta-web)
11. [Estructura de la web](#11-estructura-de-la-web)
12. [Cómo funciona la página](#12-cómo-funciona-la-página)
13. [Cómo editar el contenido](#13-cómo-editar-el-contenido)
14. [Cómo editar la apariencia](#14-cómo-editar-la-apariencia)
15. [Cómo ver la página localmente](#15-cómo-ver-la-página-localmente)
16. [Usar la web como plantilla en otro proyecto](#16-usar-la-web-como-plantilla-en-otro-proyecto)

---

# Parte 1 — El bot

## 1. Crear la aplicación y el bot en Discord

1. Ve a **https://discord.com/developers/applications** e inicia sesión con tu cuenta de Discord.
2. Pulsa **"New Application"**, ponle un nombre y acepta los términos.
3. En el menú izquierdo, entra a **"Bot"**.
   - Cambia el nombre/avatar del bot si quieres (opcional).
   - Baja hasta **"Privileged Gateway Intents"** y activa **"Message Content Intent"** (imprescindible, sin esto el bot no puede leer quién escribe cada mensaje).
   - Pulsa **"Save Changes"**.
4. En esa misma página, pulsa **"Reset Token"** para generar tu token, y cópialo. **No lo compartas ni lo subas a ningún sitio** (ver sección 2).
5. Ve a **"OAuth2" → "OAuth2 URL Generator"**:
   - En **Scopes**, marca `bot` y `applications.commands`.
   - En **Bot Permissions**, marca como mínimo: `View Channels`, `Send Messages`, `Read Message History`, `Add Reactions`.
   - Copia la URL generada al final.

Guarda esa URL, la necesitarás en la sección 5 para invitar el bot a un servidor.

---

## 2. Configurar el token de forma segura (.env)

El proyecto usa un archivo `.env` para guardar el token sin exponerlo en el código ni en GitHub.

1. Dentro de `bot/DiscordBotReacciones/`, copia el archivo de ejemplo:
   ```
   copy .env.example .env
   ```
2. Abre `.env` con un editor de texto y sustituye el valor de ejemplo por tu token real:
   ```
   DISCORD_TOKEN=tu_token_real_aqui
   ```
3. Guarda el archivo. `.env` está en `.gitignore`, así que nunca se subirá a GitHub aunque hagas `git add .`.

⚠️ Si en algún momento crees que tu token se filtró, vuelve al portal de desarrolladores y pulsa **"Reset Token"** para invalidarlo y generar uno nuevo.

---

## 3. Estructura del bot

```
bot/DiscordBotReacciones/
│
├── bot.py                  → Punto de entrada. Conecta con Discord, registra los comandos slash y escucha mensajes.
├── config_manager.py       → Funciones para leer/escribir config.json (usuarios vigilados, emojis, pausa).
├── config.example.json     → Ejemplo de la estructura de config.json (no contiene datos reales).
│
├── dat/                     → Carpeta con TODOS los archivos generados automáticamente (ignorada por Git).
│   ├── config.json             → Configuración persistente. Se crea sola al arrancar el bot por primera vez.
│   ├── watchdog.log             → Registro de eventos del watchdog (arranques, caídas, reinicios).
│   ├── watchdog.pid             → PID del proceso del watchdog mientras está activo.
│   └── bot.pid                  → PID del proceso del bot mientras está activo.
│
├── .env                    → Tu token real (NO se sube a GitHub).
├── .env.example             → Plantilla de ejemplo del .env (SÍ se sube).
│
├── watchdog.ps1             → Mantiene el bot corriendo en segundo plano y lo reinicia si se cae.
├── iniciar_bot.bat          → Doble clic para encender el bot (sin ventanas visibles).
├── detener_bot.bat          → Doble clic para apagar el bot y el watchdog por completo.
├── detener_bot.ps1          → Lógica real que usa detener_bot.bat.
│
└── venv/                     → Entorno virtual de Python (no se sube a GitHub).
```

**Nota:** ni `config.json`, ni `watchdog.log`, ni los archivos `.pid` se crean manualmente — todos se generan solos dentro de `dat/` la primera vez que arrancas el bot o el watchdog. No hace falta crear esa carpeta a mano, el propio código la genera si no existe.

El `.gitignore` del proyecto vive en la **raíz del repositorio** (no dentro de esta carpeta) y cubre tanto los archivos del bot como los de la web.

---

## 4. Instalación y primer arranque

**Requisitos:** Windows, Python 3.10+ instalado (con "Add python.exe to PATH" marcado durante la instalación).

1. Clona o descarga el proyecto y entra a la carpeta del bot:
   ```
   cd bot/DiscordBotReacciones
   ```
2. Crea el entorno virtual:
   ```
   python -m venv venv
   ```
3. Actívalo:
   ```
   venv\Scripts\activate
   ```
4. Instala las dependencias:
   ```
   pip install discord.py python-dotenv
   ```
5. Configura tu `.env` (ver sección 2).
6. Ejecuta el bot manualmente para comprobar que arranca bien:
   ```
   python bot.py
   ```
   En la consola deberías ver `✅ Bot conectado como TuBot#XXXX` y `✅ X comandos slash sincronizados.`
7. Detén la prueba con `Ctrl+C`. A partir de ahora puedes usar `iniciar_bot.bat` y `detener_bot.bat` para encenderlo/apagarlo con doble clic (ver sección 6).

---

## 5. Invitar el bot a un servidor

1. Abre la URL de invitación que generaste en la sección 1 (formato `https://discord.com/oauth2/authorize?client_id=...`).
2. Selecciona el servidor donde quieres añadirlo en el desplegable.
3. Pulsa **"Continuar"** y revisa que los permisos mostrados sean correctos (Ver canales, Enviar mensajes, Ver historial, Añadir reacciones).
4. Pulsa **"Autorizar"**.
5. El bot aparecerá en la lista de miembros del servidor (desconectado hasta que lo enciendas con `python bot.py` o `iniciar_bot.bat`).

La configuración (usuarios vigilados, emojis, pausa) es **independiente por servidor** — puedes tener el bot en varios servidores a la vez, cada uno con su propia configuración.

---

## 6. Encender y apagar el bot

- **Encender:** doble clic en `iniciar_bot.bat`. No se abre ninguna ventana visible; el bot queda corriendo en segundo plano vigilado por el watchdog.
- **Apagar:** doble clic en `detener_bot.bat`. Cierra tanto el bot como el watchdog de forma limpia.
- **Ver actividad:** revisa `dat/watchdog.log` para confirmar arranques, caídas y reinicios automáticos.
- El watchdog reinicia el bot solo si estuvo activo más de 60 segundos antes de caerse (evita bucles infinitos si hay un error de arranque real).

---

## 7. Comandos disponibles

Todos los comandos de configuración requieren permisos de **administrador** en el servidor, excepto `/rinfo`.

| Comando | Descripción |
|---|---|
| `/ruser @usuario emoji` | Añade o actualiza un usuario vigilado con su reacción. |
| `/rmulti-user @u1 @u2 ... emoji` | Asigna el mismo emoji a varios usuarios de golpe. |
| `/redit @usuario emoji` | Cambia la reacción de un usuario ya configurado. |
| `/rmulti @usuario emoji1 emoji2 ...` | Asigna hasta 5 emojis; el bot elige uno al azar cada vez. |
| `/rchance @usuario emoji porcentaje` | Define la probabilidad (1-100%) de reaccionar a ese usuario. |
| `/rremove @usuario` | Elimina un usuario de la lista vigilada. |
| `/rpause` | Pausa o reanuda las reacciones automáticas. |
| `/rlist` | Muestra los usuarios vigilados, sus emojis y probabilidad. |
| `/rinfo` | Muestra esta lista de comandos (disponible para todos). |

**Límite de usuarios:** configurable en `config_manager.py` mediante la constante `MAX_USERS` (por defecto 20).

**Emojis:** el bot acepta tanto emojis normales de Discord (👍, 🔥, 😭) como emojis personalizados del servidor (`<:nombre:id>`), validando que estos últimos pertenezcan al servidor donde se ejecuta el comando.

**Comportamiento adicional:**
- Si alguien escribe al bot por **mensaje directo**, responde una única vez indicando que solo funciona en servidores, junto con la lista de comandos.
- Si alguien **menciona solo al bot** (`@TuBot`, sin texto adicional), responde recordando el comando `/rinfo`.

---

## 8. Ejecución local: qué significa y cómo funciona

**Este bot corre en tu propio PC, no en la nube.** Es importante entenderlo antes de usarlo a diario:

- El bot solo está **en línea en Discord mientras el proceso de Python esté corriendo en tu computadora**. Si apagas, reinicias o suspendes el PC, el bot se desconecta.
- No depende de que tengas Discord (la app) abierto — es un programa aparte, independiente del cliente de Discord.
- Bloquear la pantalla (`Win + L`) o cambiar de usuario de Windows **no** apaga el bot, porque el proceso sigue corriendo en segundo plano. Cerrar sesión, suspender o apagar el equipo **sí** lo detiene.
- El consumo de recursos es mínimo (normalmente unos 40-80 MB de RAM y ~0% de CPU en reposo), similar o menor a tener una pestaña extra de navegador abierta.

Si en el futuro quieres que el bot esté disponible 24/7 sin depender de tu PC, la alternativa es desplegarlo en un servidor externo (VPS de pago, o servicios con capa gratuita como Oracle Cloud Free Tier) — eso queda fuera del alcance de este README, pero el código no necesita cambios para migrarlo, solo el entorno donde corre.

### Cómo funciona el watchdog (`watchdog.ps1`)

El watchdog es un script de PowerShell que actúa como "supervisor" del bot, para que no tengas que dejar una ventana de terminal abierta manualmente ni reiniciar el bot a mano si se cae.

Lo que hace, paso a paso, cada vez que lo enciendes (`iniciar_bot.bat`):

1. Comprueba que no haya ya otro watchdog corriendo (evita duplicados accidentales).
2. Arranca `bot.py` usando el Python del entorno virtual (`venv\Scripts\python.exe`), **sin abrir ninguna ventana visible**.
3. Guarda el PID (identificador de proceso) del watchdog y del bot en `dat/watchdog.pid` y `dat/bot.pid` — así `detener_bot.bat` sabe exactamente qué procesos cerrar después.
4. Se queda esperando en segundo plano a que el proceso del bot termine.
5. Si el bot se cierra **después** de haber estado activo más de 60 segundos, el watchdog asume que fue una caída inesperada (por ejemplo, un error temporal de conexión) y lo **reinicia automáticamente** 5 segundos después.
6. Si el bot se cierra **antes** de 60 segundos, el watchdog asume que hay un error de arranque real (por ejemplo, un fallo de sintaxis o un token inválido) y **se detiene por completo** en vez de reintentar en bucle infinito.
7. Todo lo anterior queda registrado con fecha y hora en `dat/watchdog.log`, para que puedas revisar el historial de arranques, caídas y reinicios en cualquier momento.

### Qué hace `detener_bot.bat`

Lee los PID guardados en `dat/watchdog.pid` y `dat/bot.pid`, cierra ambos procesos de forma forzada y limpia esos archivos temporales. También revisa si quedó algún proceso residual (por ejemplo, de un cierre anterior fallido) y lo cierra igualmente. Todo queda registrado en `dat/watchdog.log`.

### En resumen

| Acción | Resultado |
|---|---|
| Doble clic en `iniciar_bot.bat` | Arranca el watchdog, que a su vez arranca el bot en segundo plano (sin ventanas). |
| El bot se cae solo (tras +60s activo) | El watchdog lo reinicia automáticamente. |
| El bot falla al arrancar (antes de 60s) | El watchdog se detiene, no reintenta en bucle. |
| Doble clic en `detener_bot.bat` o Click derecho y "Ejecutar con PowerShell" | Apaga watchdog + bot de forma limpia y ordenada. |
| Apagar/reiniciar/suspender el PC | El bot y el watchdog se detienen; hay que volver a ejecutar `iniciar_bot.bat` al encender el PC. |

---

## 9. Notas de seguridad

- Nunca compartas tu `.env` ni el contenido de tu token.
- El link de invitación (`client_id` + scopes) **sí es seguro de compartir** — no expone el token.
- `config.json` no se sube a GitHub porque contiene IDs reales de usuarios de tus servidores.

---

# Parte 2 — La página web

## 10. Qué es esta web

La carpeta `docs/` contiene la página web del proyecto, y a la vez funciona como una **plantilla editable** para reutilizar el mismo diseño en otros proyectos.

La idea es simple: la estructura HTML se mantiene estática, pero el contenido visible se carga desde archivos JSON, lo que hace que el sitio sea muy fácil de personalizar sin tener que tocar el código principal cada vez.

La página sirve para:

- presentar el bot y sus funciones;
- explicar cómo usarlo;
- mostrar los comandos disponibles;
- mostrar enlaces de invitación y GitHub;
- servir como base visual reutilizable para otras páginas similares.

No depende de frameworks ni de un backend. Es una web estática, rápida de abrir, fácil de mantener y muy práctica para adaptar el contenido a distintos proyectos.

---

## 11. Estructura de la web

```
docs/
├── index.html          # Estructura principal de la página
├── style.css           # Estilos visuales, colores, layout, tipografías
├── script.js           # Lógica para cargar contenido desde JSON
├── assets/             # Imágenes, iconos, favicon y recursos visuales
│   ├── fonts/
│   └── images/
└── data/
    ├── site.json       # Texto general, navegación, hero, footer
    ├── functions.json  # Tarjetas de funcionalidades
    ├── commands.json   # Lista de comandos
    └── legal.json      # Política de privacidad y términos
```

---

## 12. Cómo funciona la página

### HTML base

El archivo `index.html` define la estructura general del sitio: navbar, hero principal, sección "¿Qué hace el bot?", sección de funciones, sección de comandos, footer y páginas legales. Cada bloque tiene un `id` específico que luego el JavaScript llena con contenido dinámico.

### Carga de contenido desde JSON

El archivo `script.js` hace peticiones `fetch()` a los archivos de `docs/data/` y arma la página en tiempo real. Eso significa que para cambiar textos, enlaces o secciones, normalmente no hace falta editar el HTML — solo se modifica el JSON correspondiente.

### Estilos visuales

`style.css` controla colores, tipografías, botones, espaciados, tarjetas, navbar, fondos animados y el soporte responsive para móvil. Si quieres cambiar la identidad visual del sitio, aquí es donde se hace.

### Assets gráficos

En `assets/images/` y `assets/fonts/` se guardan los recursos visuales: logo, mascota, íconos, favicon y fuentes. La página está pensada para que sea muy sencillo reemplazar los archivos sin romper la estructura.

---

## 13. Cómo editar el contenido

### Editar textos generales

Abre `docs/data/site.json`. Aquí se configuran: título del sitio, nombre del logo, texto del hero, botones principales, enlaces de navegación, texto del footer y el contenido de la sección "about".

```json
{
  "hero": {
    "title": "Mi Bot",
    "subtitle": "Reacciona por vos, en automático.",
    "description": "Texto descriptivo de la página."
  }
}
```

Solo cambia los valores, no hace falta reescribir el HTML.

### Editar funciones

Abre `docs/data/functions.json`. Cada elemento representa una tarjeta de función.

```json
{
  "icon": "assets/images/test.png",
  "title": "Reacciona a usuarios específicos",
  "description": "Descripción de la función."
}
```

Puedes agregar, quitar o modificar tarjetas sin tocar `script.js` ni `index.html`.

### Editar comandos

Abre `docs/data/commands.json`. Cada objeto representa un comando del bot.

```json
{
  "name": "/rinfo",
  "description": "Muestra la lista de comandos disponibles."
}
```

Si cambias el bot, solo actualiza esta lista para que la web refleje el estado real (revisa la sección 7 de este documento para la lista actual de comandos).

### Editar política legal

Abre `docs/data/legal.json`. Ahí se define la política de privacidad, los términos y condiciones y las secciones internas del texto legal. Cada bloque tiene un `heading` y un `body`, así que es muy fácil reescribir el contenido para adaptarlo a tu marca o proyecto.

---

## 14. Cómo editar la apariencia

### Cambiar colores y estilo

Se modifica en `docs/style.css`. Dentro del archivo hay una sección con variables como:

```css
:root {
  --bg-start: #008bff;
  --bg-end: #004ed9;
  --accent-start: #ff8700;
  --accent-end: #ffc300;
}
```

Cambiar esos valores cambia rápidamente la identidad visual de la web.

### Cambiar fuentes

El CSS referencia fuentes personalizadas en `assets/fonts/`:

```css
@font-face {
  font-family: "DisplayFont";
  src: url("assets/fonts/display.ttf") format("truetype");
}
```

Si agregas tus propias fuentes con esos nombres, la página las usará sin tocar el layout.

### Cambiar imágenes

En `assets/images/` puedes reemplazar logo, favicon, mascota, íconos de funciones y emoticonos de reacción. Solo tienes que mantener los nombres o actualizar la ruta en los JSON.

---

## 15. Cómo ver la página localmente

La forma más simple es abrir `index.html` directamente en el navegador.

También es recomendable servirlo con un servidor local para evitar problemas con `fetch()` al leer los archivos JSON. Desde la carpeta `docs`, ejecuta:

```bash
python -m http.server 8000
```

Luego abre en el navegador:

```
http://localhost:8000/
```

---

## 16. Usar la web como plantilla en otro proyecto

Esta página está pensada como plantilla editable: no usa un framework pesado, el contenido vive en JSON, los estilos están centralizados en CSS, los recursos visuales están separados en `assets/`, y la estructura principal es estable y reutilizable. Para adaptar la web a otro proyecto casi no hace falta tocar HTML.

Pasos para reutilizarla:

1. Cambia los textos dentro de `docs/data/site.json`.
2. Actualiza los enlaces de invitación, GitHub y redes.
3. Reemplaza los recursos gráficos en `docs/assets/images/`.
4. Ajusta paleta y tipografía en `docs/style.css`.
5. Revisa la vista final en el navegador.

Con estos pasos, la web queda completamente adaptada sin necesidad de rehacer el proyecto desde cero.

**Resumen:** `index.html` define la estructura, `style.css` el diseño, `script.js` carga el contenido dinámico, `data/*.json` mantiene textos y configuración, y `assets/` guarda los recursos visuales. Esto hace que sea fácil mantenerla, editarla y reutilizarla como plantilla profesional para distintos proyectos.
