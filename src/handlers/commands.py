import logging
from telethon import events


def register_command_handler(client, allowed_user_ids):
    async def handle_send_message_command(event):
        if event.sender_id not in allowed_user_ids:
            return

        if not event.message.message.startswith("@jonnyyy envia mensagem para"):
            return

        try:
            command_parts = event.message.message.split(" ")
            target_group_id = int(command_parts[4])
            message_content_index = event.message.message.index("com a mensagem") + len("com a mensagem ")
            message_content = event.message.message[message_content_index:]

            await client.send_message(target_group_id, message_content)
            await event.respond(f"Mensagem enviada para o grupo {target_group_id}")
        except Exception as exc:
            logging.error("Erro ao processar comando de envio de mensagem: %s", exc)
            await event.respond("Erro ao tentar enviar a mensagem. Verifique o comando e tente novamente.")

    client.add_event_handler(handle_send_message_command, events.NewMessage())

