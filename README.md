# Bot de Telegram para Envío de Mensajes Promocionales

Este bot de Telegram está diseñado para enviar mensajes promocionales a múltiples usuarios, con soporte para imágenes y texto formateado. Incluye un modo de prueba y un modo de producción que puede obtener los IDs de usuario desde un archivo JSON o una base de datos MongoDB.

## 🚀 Características

- Envío de mensajes promocionales con imágenes opcionales (0-3 imágenes)
- Formato de texto HTML para mensajes atractivos
- Modo de prueba para verificar el funcionamiento
- Soporte para múltiples fuentes de datos (JSON y MongoDB)
- Sistema de logging para seguimiento de operaciones
- Manejo seguro de credenciales mediante variables de entorno
- Texto personalizable mediante archivo JSON
- Rutas de imágenes configurables
- Número de imágenes configurable desde .env o argumento de línea de comandos

## ⚠️ Requisitos Importantes

- Los usuarios deben haber iniciado una conversación con el bot previamente
- El bot debe tener permisos para enviar mensajes a los usuarios
- Las imágenes deben estar en formato JPG/JPEG (si decides enviarlas)
- El texto debe estar formateado en HTML válido

## 📋 Prerrequisitos

- Python 3.7 o superior
- Token de Bot de Telegram (obtenido de @BotFather)
- Base de datos MongoDB (opcional, si se usa como fuente de datos)
- ID de usuario de Telegram para pruebas

## 🔧 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/telegram-messages.git
cd telegram-messages
```

2. Crea un entorno virtual (recomendado):
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Configura las variables de entorno:
   - Crea un archivo `.env` en la raíz del proyecto
   - Copia el siguiente contenido y reemplaza los valores:
```env
# Credenciales de Telegram
TELEGRAM_BOT_TOKEN=TU_BOT_TOKEN_AQUI
TELEGRAM_TEST_USER_ID=TU_ID_AQUI

# Credenciales de MongoDB (opcional)
MONGO_URI=mongodb+srv://usuario:contraseña@tu_cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=NombreBD
COLLECTION_NAME=NombreColeccion
ID_FIELD=id

# Configuración de archivos
JSON_PATH=users.json
IMAGE_1_PATH=imagen1.jpg
IMAGE_2_PATH=imagen2.jpg
IMAGE_3_PATH=imagen3.jpg

# Número de imágenes a enviar (0-3)
NUM_IMAGES=3

# Configuración de envío
MESSAGE_DELAY=1.5
```

## 📝 Archivos de Configuración

### 1. Archivo de Usuarios (users.json)
```json
{
    "user_ids": [
        123456789,
        987654321,
        456789123
    ]
}
```

### 2. Archivo de Texto (message_text.json)
```json
{
    "caption_text": "🚨 <b>¡OFERTA ESPECIAL!</b> 🚨\n\n¡No te pierdas esta increíble oportunidad!",
    "detailed_text": "✅ Beneficio 1\n✅ Beneficio 2\n✅ Beneficio 3\n\n👉 <a href='https://t.me/tubot'>¡Únete ahora!</a>"
}
```

## 🖼️ Configuración de Imágenes

El bot puede enviar entre 0 y 3 imágenes:

- **0 imágenes**: Envia solamente mensajes de texto
- **1 imagen**: Envía una sola imagen con el texto de caption
- **2 o 3 imágenes**: Envía un grupo de 2 o 3 imágenes (la primera con caption)

Puedes configurar esto de dos maneras:

1. En el archivo `.env` mediante la variable `NUM_IMAGES`
2. Mediante el argumento `--images` al ejecutar el script

El bot verificará automáticamente si las imágenes existen antes de intentar enviarlas. Si una imagen no existe, simplemente la omitirá y enviará las disponibles.

## 🎯 Uso

### Modo de Prueba
Para enviar mensajes solo a tu ID de usuario configurado:
```bash
python app.py --mode test
```

### Modo de Producción
Para enviar mensajes a todos los usuarios desde JSON:
```bash
python app.py --mode production --source json
```

Para enviar mensajes a todos los usuarios desde MongoDB:
```bash
python app.py --mode production --source mongodb
```

### Configurar Número de Imágenes
Para enviar un mensaje sin imágenes:
```bash
python app.py --mode test --images 0
```

Para enviar un mensaje con una sola imagen:
```bash
python app.py --mode test --images 1
```

## 📊 Estructura de la Base de Datos (MongoDB)

Si usas MongoDB, la base de datos debe tener la siguiente estructura:
- Base de datos: `Bote` (configurable en .env)
- Colección: `BoteCol` (configurable en .env)
- Campo de ID: `id` (configurable en .env)

## ⚠️ Consideraciones de Seguridad

- Nunca compartas tu archivo `.env`
- Mantén tu token de bot seguro
- No subas imágenes sensibles al repositorio
- Usa el modo de prueba antes de ejecutar en producción
- Asegúrate de que los usuarios hayan iniciado una conversación con el bot

## 📝 Logs

El bot genera logs detallados que incluyen:
- Éxitos y fallos en el envío de mensajes
- Errores de conexión
- Estadísticas de envío
- Tiempo total de ejecución

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios que te gustaría hacer.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Contacto

Si tienes preguntas o sugerencias, no dudes en abrir un issue en el repositorio. 