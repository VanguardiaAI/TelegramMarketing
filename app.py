import asyncio
import logging
import os
import time
import json
import argparse
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from telegram import Bot, InputMediaPhoto
from telegram.constants import ParseMode
from telegram.error import Forbidden, BadRequest, TelegramError
from telegram.ext import Application

# Cargar variables de entorno
load_dotenv()

# --- CONFIGURACIÓN ---
# ¡IMPORTANTE! Usa variables de entorno o un método seguro para tus credenciales.
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "TU_BOT_TOKEN_AQUI")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://usuario:contraseña@tu_cluster.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = os.getenv("DB_NAME", "Bote")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "BoteCol")
ID_FIELD = os.getenv("ID_FIELD", "id")
JSON_PATH = os.getenv("JSON_PATH", "users.json")

# --- CONFIGURACIÓN MODO TEST ---
# ¡¡¡IMPORTANTE!!! Reemplaza None con TU PROPIO ID de usuario de Telegram para pruebas.
# Puedes obtener tu ID hablando con @userinfobot en Telegram. Debe ser un número entero.
TEST_USER_ID_STR = os.getenv("TELEGRAM_TEST_USER_ID", None) # Puedes usar variable de entorno
TEST_USER_ID = int(TEST_USER_ID_STR) if TEST_USER_ID_STR and TEST_USER_ID_STR.isdigit() else None
# Ejemplo: TEST_USER_ID = 123456789

# Rutas o URLs de las imágenes
IMAGE_1_PATH = os.getenv("IMAGE_1_PATH", "imagen1.jpg")
IMAGE_2_PATH = os.getenv("IMAGE_2_PATH", "imagen2.jpg")
IMAGE_3_PATH = os.getenv("IMAGE_3_PATH", "imagen3.jpg")

# Número de imágenes a enviar (0-3)
NUM_IMAGES = int(os.getenv("NUM_IMAGES", "3"))

# Delay entre mensajes para evitar rate limits (en segundos)
MESSAGE_DELAY = float(os.getenv("MESSAGE_DELAY", "1.5"))

# Configuración de Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- TEXTO POR DEFECTO ---
DEFAULT_CAPTION_TEXT = """
🚨 <b>¡OFERTA ESPECIAL!</b> 🚨

¡No te pierdas esta increíble oportunidad!
"""

DEFAULT_DETAILED_TEXT = """
✅ Beneficio 1
✅ Beneficio 2
✅ Beneficio 3

👉 <a href='https://t.me/tubot'>¡Únete ahora!</a>
"""

# --- FUNCIONES ---

def load_message_text():
    """Carga el texto del mensaje desde el archivo JSON o usa el texto por defecto."""
    try:
        with open('message_text.json', 'r', encoding='utf-8') as f:
            text_data = json.load(f)
            return text_data.get('caption_text', DEFAULT_CAPTION_TEXT), text_data.get('detailed_text', DEFAULT_DETAILED_TEXT)
    except FileNotFoundError:
        logger.warning("No se encontró message_text.json, usando texto por defecto")
        return DEFAULT_CAPTION_TEXT, DEFAULT_DETAILED_TEXT
    except json.JSONDecodeError:
        logger.error("Error al decodificar message_text.json, usando texto por defecto")
        return DEFAULT_CAPTION_TEXT, DEFAULT_DETAILED_TEXT

# Cargar el texto del mensaje
CAPTION_TEXT, DETAILED_TEXT = load_message_text()

async def get_user_ids_from_json() -> list:
    """Obtiene IDs de usuario desde un archivo JSON."""
    try:
        with open(JSON_PATH, 'r') as f:
            data = json.load(f)
            user_ids = []
            for user_id in data.get('user_ids', []):
                try:
                    user_ids.append(int(user_id))
                except (ValueError, TypeError):
                    logger.warning(f"ID inválido encontrado y omitido: {user_id}")
            return user_ids
    except FileNotFoundError:
        logger.error(f"No se encontró el archivo {JSON_PATH}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Error al decodificar el archivo {JSON_PATH}")
        return []

async def get_user_ids_from_db() -> list:
    """Conecta a MongoDB y obtiene la lista de IDs de usuario."""
    user_ids = []
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        for doc in collection.find({}, {ID_FIELD: 1, "_id": 0}):
            user_id_str = doc.get(ID_FIELD)
            if user_id_str:
                try:
                    user_ids.append(int(user_id_str))
                except (ValueError, TypeError):
                    logger.warning(f"ID inválido encontrado y omitido: {user_id_str}")
        client.close()
        logger.info(f"Se encontraron {len(user_ids)} IDs de usuario en la base de datos.")
    except ConnectionFailure:
        logger.error("No se pudo conectar a MongoDB. Verifica tu URI de conexión y la red.")
    except Exception as e:
        logger.error(f"Error al obtener IDs de MongoDB: {e}")
    return user_ids

async def send_promotional_message(bot: Bot, user_id: int):
    """Envía el mensaje promocional (imágenes + texto) a un usuario específico."""
    try:
        # Si el número de imágenes es mayor a 0, enviar imágenes
        if NUM_IMAGES > 0:
            # Verificar que las imágenes existen antes de intentar enviarlas
            image_paths = []
            if NUM_IMAGES >= 1 and os.path.exists(IMAGE_1_PATH):
                image_paths.append(IMAGE_1_PATH)
            if NUM_IMAGES >= 2 and os.path.exists(IMAGE_2_PATH):
                image_paths.append(IMAGE_2_PATH)
            if NUM_IMAGES >= 3 and os.path.exists(IMAGE_3_PATH):
                image_paths.append(IMAGE_3_PATH)
            
            if image_paths:
                # Crear grupo de medios con las imágenes disponibles
                media_group = []
                # Primera imagen con caption
                media_group.append(InputMediaPhoto(
                    media=open(image_paths[0], 'rb'), 
                    caption=CAPTION_TEXT, 
                    parse_mode=ParseMode.HTML
                ))
                # Resto de imágenes sin caption
                for path in image_paths[1:]:
                    media_group.append(InputMediaPhoto(media=open(path, 'rb')))
                
                # Enviar grupo de medios
                await bot.send_media_group(chat_id=user_id, media=media_group)
                logger.info(f"Grupo de medios enviado a {user_id} con {len(media_group)} imagen(es)")
            else:
                # Si no hay imágenes disponibles pero NUM_IMAGES > 0, enviar solo texto con el caption
                await bot.send_message(
                    chat_id=user_id,
                    text=CAPTION_TEXT,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=False
                )
                logger.info(f"Mensaje con caption enviado a {user_id} (sin imágenes)")
        else:
            # Si NUM_IMAGES = 0, enviar solo texto con el caption
            await bot.send_message(
                chat_id=user_id,
                text=CAPTION_TEXT,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False
            )
            logger.info(f"Mensaje con caption enviado a {user_id} (modo sin imágenes)")

        # Pequeña pausa antes del siguiente mensaje
        await asyncio.sleep(0.5)

        # Enviar mensaje detallado
        await bot.send_message(
            chat_id=user_id,
            text=DETAILED_TEXT,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False
        )
        logger.info(f"Mensaje de texto detallado enviado a {user_id}")
        return True

    except FileNotFoundError as e:
        logger.error(f"Error: Problema con archivos de imagen: {e}")
        return False
    except Forbidden:
        logger.warning(f"No se pudo enviar mensaje a {user_id}: El usuario ha bloqueado al bot o no ha iniciado una conversación con él.")
        return False
    except BadRequest as e:
        logger.warning(f"Error de solicitud incorrecta para {user_id}: {e}")
        return False
    except TelegramError as e:
        logger.error(f"Error de Telegram al enviar a {user_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado al enviar a {user_id}: {e}")
        return False

async def main():
    """Función principal para coordinar la obtención de IDs y el envío de mensajes."""
    parser = argparse.ArgumentParser(description="Envía mensajes promocionales de Telegram a usuarios.")
    parser.add_argument(
        "--mode",
        choices=['test', 'production'],
        default='test',
        help="Modo de ejecución: 'test' (envía solo a TEST_USER_ID) o 'production' (envía a todos desde DB o JSON)."
    )
    parser.add_argument(
        "--source",
        choices=['json', 'mongodb'],
        default='json',
        help="Fuente de IDs de usuario: 'json' (archivo JSON) o 'mongodb' (base de datos)."
    )
    parser.add_argument(
        "--images",
        type=int,
        choices=[0, 1, 2, 3],
        help="Número de imágenes a enviar (0-3). Anula el valor de NUM_IMAGES del .env"
    )
    args = parser.parse_args()

    # Si se especifica --images, actualizar NUM_IMAGES
    global NUM_IMAGES
    if args.images is not None:
        NUM_IMAGES = args.images
        logger.info(f"Número de imágenes configurado a: {NUM_IMAGES}")

    # Verificación de credenciales
    if not BOT_TOKEN:
        logger.error("Por favor, configura TELEGRAM_BOT_TOKEN en el archivo .env")
        return

    # Selección de IDs según el modo y fuente
    user_ids = []
    if args.mode == 'test':
        test_id = os.getenv("TELEGRAM_TEST_USER_ID")
        if test_id and test_id.isdigit():
            user_ids = [int(test_id)]
            logger.info(f"Modo test: Se enviará el mensaje únicamente a: {test_id}")
        else:
            logger.error("Error: El modo 'test' está activado pero TELEGRAM_TEST_USER_ID no está configurado correctamente.")
            return
    else:  # modo production
        if args.source == 'json':
            user_ids = await get_user_ids_from_json()
        else:
            if not MONGO_URI:
                logger.error("Por favor, configura MONGO_URI en el archivo .env")
                return
            user_ids = await get_user_ids_from_db()

    if not user_ids:
        logger.error("No se encontraron IDs de usuario para enviar mensajes.")
        return

    # Inicialización del Bot y Envío
    application = Application.builder().token(BOT_TOKEN).build()
    bot = application.bot

    logger.info(f"Iniciando envío a {len(user_ids)} usuario(s) con {NUM_IMAGES} imagen(es)...")

    success_count = 0
    failure_count = 0
    start_time = time.time()

    for i, user_id in enumerate(user_ids):
        logger.info(f"Enviando a usuario {i+1}/{len(user_ids)} (ID: {user_id})...")
        if await send_promotional_message(bot, user_id):
            success_count += 1
        else:
            failure_count += 1

        if len(user_ids) > 1 and i < len(user_ids) - 1:
            await asyncio.sleep(MESSAGE_DELAY)

    end_time = time.time()
    total_time = end_time - start_time

    logger.info(f"--- Proceso de envío ({args.mode.upper()}) completado ---")
    logger.info(f"Mensajes enviados con éxito: {success_count}")
    logger.info(f"Fallos al enviar: {failure_count}")
    logger.info(f"Tiempo total: {total_time:.2f} segundos")

if __name__ == "__main__":
    asyncio.run(main())