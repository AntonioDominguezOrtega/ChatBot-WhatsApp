import requests
import sett
import json
import time
import random

def obtener_Mensaje_whatsapp(message):
    if 'type' not in message :
        text = 'mensaje no reconocido'
        return text

    typeMessage = message['type']
    if typeMessage == 'text':
        text = message['text']['body']
    elif typeMessage == 'button':
        text = message['button']['text']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
        text = message['interactive']['list_reply']['title']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
        text = message['interactive']['button_reply']['title']
    else:
        text = 'mensaje no procesado'
    
    
    return text

def enviar_Mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}
        print("se envia ", data)
        response = requests.post(whatsapp_url, 
                                 headers=headers, 
                                 data=data)
        
        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return e,403
    
def text_Message(number,text):
    data = json.dumps(
            {
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "body": text
                }
            }
    )
    return data

def buttonReply_Message(number, options, body, footer, sedd, messageId):
    buttons = []
    for i, option in enumerate(options):
        buttons.append(
            {
                "type": "reply",
                "reply": {
                    "id": sedd + "_btn_" + str(i+1),
                    "title": option
                }
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data

def listReply_Message(number, options, body, footer, sedd,messageId):
    rows = []
    for i, option in enumerate(options):
        rows.append(
            {
                "id": sedd + "_row_" + str(i+1),
                "title": option,
                "description": ""
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": [
                        {
                            "title": "Secciones",
                            "rows": rows
                        }
                    ]
                }
            }
        }
    )
    return data

def document_Message(number, url, caption, filename):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": url,
                "caption": caption,
                "filename": filename
            }
        }
    )
    return data

def sticker_Message(number, sticker_id):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "sticker",
            "sticker": {
                "id": sticker_id
            }
        }
    )
    return data

def get_media_id(media_name , media_type):
    media_id = ""
    if media_type == "sticker":
        media_id = sett.stickers.get(media_name, None)
    #elif media_type == "image":
    #    media_id = sett.images.get(media_name, None)
    #elif media_type == "video":
    #    media_id = sett.videos.get(media_name, None)
    #elif media_type == "audio":
    #    media_id = sett.audio.get(media_name, None)
    return media_id

def replyReaction_Message(number, messageId, emoji):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "reaction",
            "reaction": {
                "message_id": messageId,
                "emoji": emoji
            }
        }
    )
    return data

def replyText_Message(number, messageId, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "context": { "message_id": messageId },
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data

def markRead_Message(messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  messageId
        }
    )
    return data

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

    if "hola" in text:
        body = "¡Hola! 👋 Bienvenido a Banco Azteca. ¿Selecciona tu sucursal mas cercana?"
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
        print("La opción seleccionada es ---------  " + sucursalSal)

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1", messageId)
        list.append(replyButtonData)

    elif "generar turno" in text:
        body = "¿Que movimiento vas a realizar? 🤔"
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

        # Datos para el mensaje de turno
        banco = "Banco Azteca"
        turno = f"T-{random.randint(100, 999)}"
        mensaje_turno = f"{banco}\n{sucursalSal}\nTu turno es: {turno}"

        turno_message = text_Message(number, mensaje_turno)
        enviar_Mensaje_whatsapp(turno_message)
        time.sleep(3)

        data = text_Message(number, "Tu turno se asignó correctamente, te esperamos en sucursal 😃")
        list.append(data)

    elif "agendar citas" in text:
        body = "¿Que movimiento vas a realizar? 🤔"
        footer = "Equipo Banco Azteca"
        options = ["Cita apertura", "Fondo de inversiòn", "Creditos", "Entrega de tarjetas", "Actualizar datos", "Banca digital"]

        listReplyData = listReply_Message(number, options, body, footer, "sed4", messageId)
        list.append(listReplyData)
        
    elif text in ["cita apertura", "fondo de inversiòn", "creditos", "entrega de tarjetas", "actualizar datos", "banca digital"]:
        body = "Excelente ¿Que dia quieres acudir? 📅"
        footer = "Equipo Banco Azteca"
        options = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

        listReplyData = listReply_Message(number, options, body, footer, "sed2", messageId)
        sticker = sticker_Message(number, get_media_id("perro_traje", "sticker"))

        list.append(listReplyData)
        list.append(sticker)
        
    elif text in ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]:
        # Guardar el día seleccionado
        diaSal = text
        usuarios_data[number]['dia'] = diaSal  # Almacenar en el diccionario global

        body = "¿En que horario quieres acudir? 🕜"
        footer = "Equipo Banco Azteca"
        options = ["8:00 AM", "8:30 AM", "9:00 AM", "9:30 AM", "    ", "10:30 AM", "11:00 AM", "11.30 AM", "12:00 PM"]

        listReplyData = listReply_Message(number, options, body, footer, "sed2", messageId)
        sticker = sticker_Message(number, get_media_id("perro_traje", "sticker"))

        list.append(listReplyData)
        list.append(sticker)
        
    elif text in ["8:00 am", "8:30 am", "9:00 am", "9:30 am", "10:00 am", "10:30 am", "11:00 am", "11.30 am", "12:00 pm"]:
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

        data = text_Message(number, "Tu cita se asignó correctamente, te esperamos en sucursal 😃")
        list.append(data)
        time.sleep(30)
        
        data = text_Message(number, "Te encuentras a 5 turnos antes depasar")
        list.append(data)
        time.sleep(10)
        
        data = text_Message(number, "Te encutras a 2 turnos antes de pasar")
        list.append(data)
        list.append(5)
        
        data = text_Message(number, "Es tu turno por favor acercate a la caja 1")
        list.append(data)
        
        body = "¿Que calificacion le das a nuestra atencion?"
        footer = "Equipo Banco Azteca"
        options = ["1 ⭐", "2 ⭐⭐", "3 ⭐⭐⭐", "4 ⭐⭐⭐⭐", "5 ⭐⭐⭐⭐⭐"]

        listReplyData = listReply_Message(number, options, body, footer, "sed2", messageId)
        sticker = sticker_Message(number, get_media_id("perro_traje", "sticker"))

        list.append(listReplyData)
        list.append(sticker)
        
    else:
        data = text_Message(number, "Lo siento, no entendí lo que dijiste. ¿Quieres que te ayude con alguna de estas opciones?")
        list.append(data)

    for item in list:
        enviar_Mensaje_whatsapp(item)


#al parecer para mexico, whatsapp agrega 521 como prefijo en lugar de 52,
# este codigo soluciona ese inconveniente.
def replace_start(s):
    number = s[3:]
    if s.startswith("521"):
        return "52" + number
    elif s.startswith("549"):
        return "54" + number
    else:
        return s
        
