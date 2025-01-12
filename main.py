import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from PIL import Image, ImageDraw, ImageFont
import pytz
from datetime import datetime

# Token del bot
TOKEN = "7699996224:AAGRK31aHgxUQwgkdtfAOXXEWArEy-0WPnA"  # Reemplaza con tu token seguro

# Lista de usuarios permitidos (IDs)
USUARIOS_PERMITIDOS = {7142146578, 733317016, 6903942837, 7200393970, 6625965336, 5238277683}  # Sustituye con los IDs permitidos

# Rutas de plantillas y fuentes
TEMPLATE_PATH = "plantilla.jpeg"  # Plantilla existente
TEMPLATE_PATH_C2 = "plantilla_c2.jpeg"  # Nueva plantilla para el comando /c2
FONT_PATH = "fuente.ttf"  # Fuente para número y valor del /c
FONT_PATH_C2 = "fuente_c2.ttf"  # Nueva fuente para el comando /c2 (cambia a la tipografía que prefieras)
FONT_PATH_CEROS = "fuente.ttf"  # Fuente específica para los ceros
DATE_FONT_PATH = "fuente_fecha.ttf"  # Fuente para la fecha en /c1 y /c2 (mantenemos la misma para ambos)

# Tamaño de la fuente para el número, valor, nombre y fecha
TAMANO_NUMERO_C1 = 23  # Tamaño de la fuente para el número en /c
TAMANO_VALOR_C1 = 27  # Tamaño de la fuente para el valor en /c
TAMANO_NUMERO_C2 = 25  # Tamaño de la fuente para el número en /c2
TAMANO_VALOR_C2 = 25  # Tamaño de la fuente para el valor en /c2
TAMANO_CEROS = 20  # Tamaño de fuente para los ceros
TAMANO_NOMBRE = 25  # Tamaño de fuente para el nombre
TAMANO_FECHA = 21  # Tamaño de fuente para la fecha

# Separación entre la parte entera y los ceros (espaciado horizontal)
SEPARACION_DECIMAL = -1  # Ajuste de separación más pequeño

# Función para formatear la fecha y hora
def obtener_fecha_hora():
    colombia_tz = pytz.timezone('America/Bogota')
    fecha_actual = datetime.now(colombia_tz)
    fecha_formateada = fecha_actual.strftime("%d %b %Y - %I:%M %p.")
    fecha_formateada = fecha_formateada.replace(fecha_formateada.split()[1], fecha_formateada.split()[1].capitalize())
    return fecha_formateada

# Función para formatear el valor
def formatear_valor(valor: str) -> str:
    entero = int(valor)
    entero_formateado = f"{entero:,}".replace(",", ".")  # Usar puntos para separar los miles
    return f"{entero_formateado},00"  # Se asegura que los valores tengan ",00"

# Función para formatear el número con guiones (para el comando /c2)
def formatear_nequi(nequi: str) -> str:
    nequi = nequi.zfill(10)  # Rellenar con ceros a la izquierda si es necesario
    return f"{nequi[:3]}-{nequi[3:9]}-{nequi[9:]}"  # Formato XXX-XXXXXX-X

# Función para verificar si el usuario está permitido
def verificar_usuario_permitido(user_id: int) -> bool:
    return user_id in USUARIOS_PERMITIDOS

# Función para generar comprobante con /c
def generar_comprobante(numero: str, valor: str) -> str:
    img = Image.open(TEMPLATE_PATH)
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(FONT_PATH, TAMANO_NUMERO_C1)
    font_valor = ImageFont.truetype(FONT_PATH, TAMANO_VALOR_C1)
    small_font = ImageFont.truetype(FONT_PATH_CEROS, TAMANO_CEROS)
    date_font = ImageFont.truetype(DATE_FONT_PATH, TAMANO_FECHA)
    color_numero_valor = (0, 0, 0)
    color_fecha = (62, 62, 62, 255)

    numero_pos = (50, 970)
    valor_pos = (70, 555)
    fecha_pos = (180, 335)

    fecha_hora = obtener_fecha_hora()
    valor_formateado = formatear_valor(valor)
    numero_formateado = formatear_nequi(numero)  # Usamos la función para formatear el nequi
    parte_entera, parte_decimal = valor_formateado.split(',')

    draw.text(numero_pos, f"{numero_formateado}", font=font, fill=color_numero_valor)
    draw.text(valor_pos, parte_entera, font=font_valor, fill=color_numero_valor)

    x_offset_ceros = valor_pos[0] + draw.textlength(parte_entera, font=font_valor) + 2
    y_offset_ceros = valor_pos[1] + 6
    draw.text((x_offset_ceros, y_offset_ceros), f",{parte_decimal}", font=small_font, fill=color_numero_valor)
    draw.text(fecha_pos, f"{fecha_hora}", font=date_font, fill=color_fecha)

    output_path = "comprobante.png"
    img.save(output_path)
    return output_path

# Función para generar comprobante con /c2
def generar_comprobante_c2(nombre: str, nequi: str, valor: str) -> str:
    img = Image.open(TEMPLATE_PATH_C2)
    draw = ImageDraw.Draw(img)

    font_nombre = ImageFont.truetype(FONT_PATH_C2, TAMANO_NOMBRE)  # Nueva fuente para el nombre
    font = ImageFont.truetype(FONT_PATH_C2, TAMANO_NUMERO_C2)  # Fuente para número y valor en /c2
    font_valor = ImageFont.truetype(FONT_PATH_C2, TAMANO_VALOR_C2)  # Fuente para el valor en /c2
    color = (0, 0, 0)

    # Posiciones ajustadas para la plantilla de /c2
    nombre_pos = (50, 447) 
    nequi_pos = (50, 605)
    valor_pos = (50, 700)
    fecha_pos = (170, 285)

    fecha_hora = obtener_fecha_hora()

    draw.text(nombre_pos, f"{nombre.upper()}", font=font_nombre, fill=color)
    nequi_formateado = formatear_nequi(nequi)  # Formateamos el número de nequi
    draw.text(nequi_pos, f"{nequi_formateado}", font=font, fill=color)

    # Formatear el valor con separadores
    valor_formateado = formatear_valor(valor)
    draw.text(valor_pos, f"$ {valor_formateado}", font=font_valor, fill=color)

    # Cambiar color de la fecha a rojo, por ejemplo
    color_fecha = (59, 59, 59, 255)  # Rojo
    date_font = ImageFont.truetype(DATE_FONT_PATH, TAMANO_FECHA)
    draw.text(fecha_pos, f"{fecha_hora}", font=date_font, fill=color_fecha)

    output_path = "comprobante_c2.png"
    img.save(output_path)
    return output_path

# Comando /start
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if not verificar_usuario_permitido(user_id):
        await update.message.reply_text("No tienes permiso para usar este bot.")
        return
    await update.message.reply_text("¡Hola! Usa los comandos /c o /c2 para generar un comprobante.")

# Comando /c
async def comando_c(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if not verificar_usuario_permitido(user_id):
        await update.message.reply_text("No tienes permiso para usar este bot.")
        return

    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Formato incorrecto. Usa: /c [número] [valor]")
            return

        numero, valor = args

        if not valor.isdigit():
            await update.message.reply_text("El valor debe ser un número.")
            return

        comprobante_path = generar_comprobante(numero, valor)

        with open(comprobante_path, "rb") as img:
            await update.message.reply_photo(img, caption="Aquí está tu comprobante.")

    except Exception as e:
        await update.message.reply_text(f"Hubo un error: {e}")

# Comando /c2
async def comando_c2(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if not verificar_usuario_permitido(user_id):
        await update.message.reply_text("No tienes permiso para usar este bot.")
        return

    try:
        args = context.args
        if len(args) < 3:  # Aseguramos que haya al menos un nombre
            await update.message.reply_text("Formato incorrecto. Usa: /c2 [nombre(s)] [nequi] [valor]")
            return

        # El nombre puede ser más de una palabra, así que unimos todo lo que viene antes del "nequi"
        nombre = " ".join(args[:-2])
        nequi = args[-2]
        valor = args[-1]

        if not valor.isdigit():
            await update.message.reply_text("El valor debe ser un número.")
            return

        comprobante_path = generar_comprobante_c2(nombre, nequi, valor)

        with open(comprobante_path, "rb") as img:
            await update.message.reply_photo(img, caption="Aquí está tu comprobante.")

    except Exception as e:
        await update.message.reply_text(f"Hubo un error: {e}")

# Función principal
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("c", comando_c))
    application.add_handler(CommandHandler("c2", comando_c2))
    application.run_polling()

if __name__ == "__main__":
    main()
