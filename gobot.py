import discord
import asyncio
import requests
import json
import time


client = discord.Client();
num_commandes = 0


async def validateCommande(message, commande_id) :
	data = {
		"request" : "validate",
		"commande_id" : commande_id
	}

	r = requests.post("https://www.graphique-one.xyz/disc/app.php", data=data)
	jResp = json.loads(r.text)
	if jResp["status"] ==  "SUCCESS" :
		await client.send_message(message.author, jResp["message"])
		await client.send_message(message.channel, "Une nouvelle commande a été validée")
	else :
		await client.send_message(message.channel, jResp["message"])

async def getCommande(message, userID, commande_id, username):
	data = {
		"request" : "reserve",
		"commande_id" : commande_id,
		"username" : username
	}
	r = requests.post("https://www.graphique-one.xyz/disc/app.php", data=data)
	jResp = json.loads(r.text)

	if jResp["status"] == "SUCCESS" :

		infos = jResp["message"]
		
		await client.send_message(message.channel, "La commande bien été réservé à votre nom")
		response = "**Informations sur la commande de {} :**\n\n".format(infos["username"]) +\
		"ADRESSE E-MAIL :  {} \n\n".format(infos["email"])  +\
		"N° Identification de la commande : **{}** ( Ne l'oubliez pas pour valider la commande) \n\n".format(commande_id)+\
		"Description : ```{}``` \n\n".format(infos["commande_desc"])
		if infos["type"] != "pack": 
			if not infos["pseudoInLogo"] is None or infos["pseudoInLogo"] == "" :
				response = "".join([response, " - Il ne veut son pseudo sur l'image\n\n"])
			else :
				response = "".join([response, " - Il ne veut pas son pseudo sur l'image\n\n"])

			if not infos["product_size"] is None or infos["product_size"] == "" :
				response = "".join([response, "Dimension de l'image : {}".format(infos["product_size"])])

		await client.send_message(message.author, response)


	else :
		await client.send_message(message.channel, jResp["message"])

async def sendList(message,userID = "") :
	data = {
		"request" : "list"
 	}		
	r = requests.post("https://www.graphique-one.xyz/disc/app.php", data = data)
	try:
		jResp = json.loads(r.text)

		if jResp["status"] == "SUCCESS" :

			commandes = jResp["message"]
			premiumList = "• ***Liste des commandes Premium*** : \n\n"
			memberList = "• ***Liste des autres commandes*** : \n\n"
			for commande in commandes :
				if commande["suscriber"] == "1": 
					partial = "- __ID de la commande :   {}__ \n\n {} a commandé :   **{}** \n\n".format(commande["commande_id"], commande["username"], commande["product_name"])+\
						' ```{}``` \n\n*le {}* \n\n'.format(commande["commande_desc"], commande["commande_date"])
					premiumList = "".join([premiumList, partial])

				else :
					partial = "- __ID de la commande :   {}__ \n\n {} a commandé :   **{}** \n\n".format(commande["commande_id"], commande["username"], commande["product_name"]) +\
						' ```{}``` \n\n*le {}* \n\n'.format(commande["commande_desc"], commande["commande_date"])
					memberList = "".join([memberList, partial])

			await client.send_message(message.channel, "".join([premiumList, memberList]))
			num_commandes = jResp["nb_commandes"]
			
		else : 
			await client.send_message(message.channel, jResp["message"])
	except json.decoder.JSONDecodeError :
		print("Error")


@client.event
async def on_ready() :
	print("Logged as : {} - {}".format(client.user.name, client.user.id))

@client.event
async def on_message(message) :
	msg = message.content.upper()
	if msg.startswith("G!") :
		cmd = msg.split("!")[1].lstrip(" ")

		if cmd == "HELP" :
			response = "Voici la liste des commandes possibles avec GOBOT :\n" + \
				"- `g!help` : Vous obtenez ce message :joy: \n\n" + \
				"- `g!liste_commandes` : Retourne la liste des commandes n'ayant pas de graphiste attitré. Les commandes premiums apparraisent en premier\n\n" + \
				"- `g!select [id_de_la_commande] [votre_nom_de_graphiste_Gone]` : Permet de réserver la commande correspondant à l'ID entré. Une fois réservé, vous ne pouvez plus retourner en arrière\n\n" +\
				"- `g!validate [id_de_la_commande] ` : Vous permet de valider la commande que vous avez terminé \n\n" + \
				"- `g!ping` : Si vous voulez vous amusez à voir votre ping :ping_pong: "
			await client.send_message(message.channel, response);

		if cmd == "PING" :
			userID = message.author.id
			timePing = time.monotonic()
			pinger = await client.send_message(message.channel, "<@{}> :ping_pong:  **Pong !**".format(userID))
			ping = '%.2f'%(1000*(time.monotonic() - timePing))

			await client.edit_message(pinger, "<@{}> :ping_pong:  **Pong !** \n\n `Latence : {} ms.`".format(userID, ping))

		if cmd == "LISTE_COMMANDES" :
			userID = message.author.id
			if message.channel.id == "448919657630531594" :

				await sendList(message,userID)
			else :
				client.send_message(message.channel, "<@{}> Ce n'est pas le bon channel !".format(userID))

		if cmd.startswith("SELECT") :
			userID = message.author.id
			if message.channel.id == "448919657630531594" :
				cmd = cmd.split(" ")
				if(len(cmd) == 3) :
					commandeID = cmd[1]
					username = cmd[2]
					await getCommande(message, userID, commandeID, username)
				else : 
					await client.send_message(message.channel, "<@{}> La syntaxe de la requête est incorrecte !".format(userID))
			else :
				client.send_message(message.channel, "<@{}> Ce n'est pas le bon channel !".format(userID))			

		if cmd.startswith("VALIDATE") :
			if message.channel.id == "448919657630531594" :
				cmd = cmd.split(" ")
				if len(cmd) == 2 :
					commandeID = cmd[1]
					await validateCommande(message, commandeID)
				else :
					await client.send_message(message.channel, "<@{}> La syntaxe de la requête est incorrecte !".format(message.author.id))
			else :
				client.send_message(message.channel, "<@{}> Ce n'est pas le bon channel !".format(message.author.id))

		if cmd == "QUIT" :
			if message.author.id == "409299770457194511" :
				await client.logout()
				await client.close()   

client.run("process.env.TOKEN")
