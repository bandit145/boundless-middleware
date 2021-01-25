import discord
import os
import aio_pika
import json
import hashlib

AMQP_CON = "amqp://guest:guest@127.0.0.1/"
ROUTING_KEY = "wiretap"

client = discord.Client()
api_key = os.getenv("WIRETAP_API_KEY")
conn = None


@client.event
async def on_ready():
	global conn
	conn = await aio_pika.connect_robust(AMQP_CON)
	chan = await conn.channel()
	print(f'I am logged in as {client.user}')

@client.event
async def on_message(message):
	hash_str = f"{message.id}{message.author.id}{str(message.created_at)}"
	msg_hash = hashlib.sha256(hash_str.encode()).hexdigest()
	chan = await conn.channel()
	dsc_msg = {
		"hash": msg_hash,
		"author_name": message.author.name,
		"author_id": message.author.id,
		"message": message.clean_content,
		"created_at": str(message.created_at),
		"channel": message.channel.id,
		"mentions": [{"name": x.name, "display_name": x.display_name, "mention": x.mention} for x in message.mentions]
	}
	print("Message sending to rabbitmq", json.dumps(dsc_msg, indent=4))
	await chan.default_exchange.publish(aio_pika.Message(body=json.dumps(dsc_msg).encode()), routing_key=ROUTING_KEY)





client.run(api_key)