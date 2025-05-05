import os
import json
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler
)

# Configuración GitHub
REPO_OWNER = "tu-usuario-github"
REPO_NAME = "nombre-repositorio"
JSON_PATH = "data/telefonos.json"

# Estados de la conversación
KEYWORD, PHONE, SCHEDULE, ADDRESS = range(4)

# Cargar datos desde GitHub
def cargar_datos():
    url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/{JSON_PATH}"
    response = requests.get(url)
    return response.json()

# Actualizar datos en GitHub
def actualizar_github(data):
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Obtener SHA del archivo existente
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{JSON_PATH}"
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha")
    
    # Actualizar archivo
    content = json.dumps(data, indent=2).encode("utf-8")
    content_base64 = base64.b64encode(content).decode("utf-8")
    
    payload = {
        "message": "Actualización desde bot",
        "content": content_base64,
        "sha": sha
    }
    
    response = requests.put(url, headers=headers, json=payload)
    return response.status_code == 200

# Comando /agregar (solo para admins)
async def agregar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) != os.getenv("ADMIN_ID"):  # Configura ADMIN_ID en Railway
        await update.message.reply_text("❌ Solo los admins pueden usar este comando.")
        return ConversationHandler.END
    
    await update.message.reply_text("🔑 Ingresa la palabra clave (ej: 'farmacia'):")
    return KEYWORD

async def keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["keyword"] = update.message.text.lower()
    await update.message.reply_text("📞 Ingresa el teléfono:")
    return PHONE

async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("⏰ Ingresa el horario (opcional):")
    return SCHEDULE

async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["schedule"] = update.message.text
    await update.message.reply_text("📍 Ingresa la dirección (opcional):")
    return ADDRESS

async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    keyword = user_data["keyword"]
    
    # Cargar y actualizar datos
    data = cargar_datos()
    data[keyword] = {
        "telefono": user_data["phone"],
        "horario": user_data.get("schedule", ""),
        "direccion": update.message.text
    }
    
    if actualizar_github(data):
        await update.message.reply_text("✅ ¡Datos actualizados correctamente!")
    else:
        await update.message.reply_text("❌ Error al actualizar en GitHub")
    
    return ConversationHandler.END

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()
    
    # Conversation Handler para /agregar
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("agregar", agregar)],
        states={
            KEYWORD: [MessageHandler(filters.TEXT, keyword)],
            PHONE: [MessageHandler(filters.TEXT, phone)],
            SCHEDULE: [MessageHandler(filters.TEXT, schedule)],
            ADDRESS: [MessageHandler(filters.TEXT, address)]
        },
        fallbacks=[]
    )
    
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
