import random
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from services import (
    markRead_Message, 
    listReply_Message, 
    sticker_Message, 
    get_media_id, 
    text_Message, 
    enviar_Mensaje_whatsapp, 
)

# Inicializar Firebase
cred = credentials.Certificate("datoschatbot-firebase-adminsdk-fbsvc-3192faeb5d.json")
firebase_admin.initialize_app(cred)

# Conexión a Firestore
db = firestore.client()

# Función para guardar citas en Firestore
def guardar_cita_en_firestore(numero, sucursal, dia, hora, turno, tipo, status="En espera", fecha_hora_agendada=None, movimiento=None):
    try:
        # Referencia a la colección "Citas"
        doc_ref = db.collection("Citas").document(numero)  # Usar el número como ID del documento
        # Datos a guardar
        cita = {
            "numero": numero,
            "sucursal": sucursal,
            "dia": dia,
            "hora": hora,
            "turno": turno,
            "tipo": tipo,
            "status": status,
            "fecha_hora_agendada": fecha_hora_agendada or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "movimiento": movimiento  # Guardar el movimiento seleccionado
        }
        doc_ref.set(cita, merge=True)  # merge=True para actualizar o crear si no existe
        print(f"Cita guardada para el número {numero}.")
    except Exception as e:
        print(f"Error al guardar la cita: {e}")

# Diccionario global para almacenar los datos del usuario
usuarios_data = {}

def administrar_chatbot(text, number, messageId, name):
    text = text.lower()  # mensaje que envio el usuario
    list = []
    print("mensaje del usuario: ", text)

    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)

    # Asegurarse de que la sucursal, día y hora tengan valores predeterminados
    if number not in usuarios_data:
        usuarios_data[number] = {}

    sucursalSal = usuarios_data[number].get('sucursal', '')  # Recoger sucursal si ya existe, sino vacío
    diaSal = usuarios_data[number].get('dia', '')  # Recoger día si ya existe, sino vacío
    horaSal = usuarios_data[number].get('hora', '')  # Recoger hora si ya existe, sino vacío
    movimientoSel = usuarios_data[number].get('movimiento', '')  # Recoger movimiento si ya existe, sino vacío

    if "hola" in text:
        body = "¡Hola! 👋 Bienvenido a Banco Azteca. ¿Selecciona tu sucursal más cercana?"
        footer = "Equipo Banco Azteca"
        options = ["Sucursal uno", "Sucursal dos", "Sucursal tres"]

        listReplyData = listReply_Message(number, options, body, footer, "sed1", messageId)
        sticker = sticker_Message(number, get_media_id("perro_traje", "sticker"))

        list.append(listReplyData)
        list.append(sticker)

    elif text in ["sucursal uno", "sucursal dos", "sucursal tres"]:
        body = "Perfecto ¿Cómo podemos ayudarte hoy? 😃"
        footer = "Equipo Banco Azteca"
        options = ["✅ Generar turno", "⛔ Agendar citas"]

        sucursalSal = text  # Guardar la sucursal seleccionada
        usuarios_data[number]['sucursal'] = sucursalSal  # Almacenar en el diccionario global

        replyButtonData = listReply_Message(number, options, body, footer, "sed1", messageId)
        list.append(replyButtonData)

    elif "generar turno" in text:
        body = "¿Qué movimiento vas a realizar? 🤔"
        footer = "Equipo Banco Azteca"
        options = ["Movimiento", "Entrega de chequeras", "Apertura", "Consultas", "Mantenimiento de cuenta"]

        listReplyData = listReply_Message(number, options, body, footer, "sed1", messageId)
        list.append(listReplyData)

    elif text in ["movimiento", "entrega de chequeras", "apertura", "consultas", "mantenimiento de cuenta"]:
        sticker = sticker_Message(number, get_media_id("pelfet", "sticker"))
        textMessage = text_Message(number, "Genial, por favor espera un momento estamos generando tu turno.")

        enviar_Mensaje_whatsapp(sticker)
        enviar_Mensaje_whatsapp(textMessage)
        time.sleep(3)

        banco = "Banco Azteca"
        turno = f"T-{random.randint(100, 999)}"
        mensaje_turno = f"{banco}\n{sucursalSal}\nTu turno es: {turno}"

        turno_message = text_Message(number, mensaje_turno)
        enviar_Mensaje_whatsapp(turno_message)
        time.sleep(3)

        movimientoSel = text  # Guardar el movimiento seleccionado
        usuarios_data[number]['movimiento'] = movimientoSel  # Actualizar el diccionario global

        # Guardar los datos de la cita en Firestore con el movimiento
        guardar_cita_en_firestore(
            numero=number,
            sucursal=sucursalSal,
            dia=diaSal,
            hora=horaSal,
            turno=turno,
            tipo="turno",
            status="En espera",
            fecha_hora_agendada=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            movimiento=movimientoSel
        )

        data = text_Message(number, "Tu turno se asignó correctamente, te esperamos en sucursal 😃")
        list.append(data)

    elif "agendar citas" in text:
        body = "¿Qué movimiento vas a realizar? 🤔"
        footer = "Equipo Banco Azteca"
        options = ["Cita apertura", "Fondo de inversión", "Créditos", "Entrega de tarjetas", "Actualizar datos", "Banca digital"]

        listReplyData = listReply_Message(number, options, body, footer, "sed4", messageId)
        list.append(listReplyData)

    elif text in ["cita apertura", "fondo de inversión", "créditos", "entrega de tarjetas", "actualizar datos", "banca digital"]:
        body = "Excelente ¿Qué día quieres acudir? 📅"
        footer = "Equipo Banco Azteca"
        options = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

        movimientoSel = text  # Guardar el movimiento seleccionado
        usuarios_data[number]['movimiento'] = movimientoSel  # Actualizar el diccionario global

        listReplyData = listReply_Message(number, options, body, footer, "sed2", messageId)
        sticker = sticker_Message(number, get_media_id("perro_traje", "sticker"))

        list.append(listReplyData)
        list.append(sticker)

    elif text in ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]:
        # Guardar el día seleccionado
        diaSal = text
        usuarios_data[number]['dia'] = diaSal  # Almacenar en el diccionario global

        body = "¿En qué horario quieres acudir? 🕜"
        footer = "Equipo Banco Azteca"
        options = ["8:00 AM", "8:30 AM", "9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "12:00 PM"]

        listReplyData = listReply_Message(number, options, body, footer, "sed2", messageId)
        sticker = sticker_Message(number, get_media_id("perro_traje", "sticker"))

        list.append(listReplyData)
        list.append(sticker)

    elif text in ["8:00 am", "8:30 am", "9:00 am", "9:30 am", "10:00 am", "10:30 am", "11:00 am", "11:30 am", "12:00 pm"]:
        # Guardar la hora seleccionada
        horaSal = text
        usuarios_data[number]['hora'] = horaSal  # Almacenar en el diccionario global

        sticker = sticker_Message(number, get_media_id("pelfet", "sticker"))
        textMessage = text_Message(number, "Genial, por favor espera un momento estamos generando tu cita.")

        enviar_Mensaje_whatsapp(sticker)
        enviar_Mensaje_whatsapp(textMessage)
        time.sleep(3)

        # Datos para el mensaje de cita
        banco = "Banco Azteca"
        turno = f"C-{random.randint(100, 999)}"
        mensaje_cita = f"{banco}\n{sucursalSal}\n{diaSal}\n{horaSal}\nTu cita es: {turno}"

        cita_message = text_Message(number, mensaje_cita)
        enviar_Mensaje_whatsapp(cita_message)
        time.sleep(3)

        # Guardar los datos de la cita en Firestore
        guardar_cita_en_firestore(
            numero=number,
            sucursal=sucursalSal,
            dia=diaSal,
            hora=horaSal,
            turno=turno,
            tipo="cita",
            status="En espera", 
            fecha_hora_agendada=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            movimiento=movimientoSel
        )

        data = text_Message(number, "Tu cita se asignó correctamente, te esperamos en sucursal 😃")
        list.append(data)

    else:
        data = text_Message(number, "Lo siento, no entendí lo que dijiste. ¿Quieres que te ayude con alguna de estas opciones?")
        list.append(data)

    for item in list:
        enviar_Mensaje_whatsapp(item)
