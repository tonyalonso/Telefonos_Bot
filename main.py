from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
TOKEN = os.environ.get("935f4d85-b211-48ef-adee-da96c161b36f")

# Diccionario de respuestas privadas según palabras clave
RESPUESTAS = {
    "farmacia": "Farmacia del barrio:\nDirección: Calle 23 y B\nHorario: 8:00am - 12:00m",
    "bodega": "Bodega:\nDirección: Camilo Cienfuegos #104\nHoy llegó: arroz, aceite y café.",
    "panadería": "Panadería:\nHorario: 7:00am - 3:00pm\nPan suave, duro y galletas.",
}

async def mensaje_privado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    for clave in RESPUESTAS:
        if clave in texto:
            await context.bot.send_message(chat_id=update.message.from_user.id, text=RESPUESTAS[clave])
            break

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="¡Hola! Soy el bot Teléfonos. Escribe palabras como 'farmacia', 'bodega' o 'panadería'.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), mensaje_privado))
    app.run_polling()
