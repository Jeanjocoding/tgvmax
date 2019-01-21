import requests
import json
import time
import smtplib
from email.message import EmailMessage

#a faire: finaliser main - trier resultats par heure(a priori ok) - meilleure presentaition des resultats - fourchette de dates(indice de tri pret. maintenant il faut faire une fonction qui permette de lancer une requete par jour dans la fourchette)   - mail(globalement bon, mais imparfait, voire mail recu) - recurrence(ok transitoire) - dire quand il y a du nouveau(ok) - et peut etre suggestion/modification des resultats - boss final: recréer correspondance


#probleme: il ne met qu'un train dans la liste

date = "2019-02-02" #str(input("date:"))
origine = "PARIS (intramuros)" #str(input("origine:"))
destination = "MARSEILLE ST CHARLES" #str(input("destination"))

# construire url en fonction des parametres
def urlbuilder(date, origine, destination):
	url = "https://data.sncf.com/api/records/1.0/search/?dataset=tgvmax&rows=100&sort=-date&facet=date&facet=origine&facet=destination&facet=od_happy_card&refine.origine={}&refine.destination={}&refine.od_happy_card=OUI&refine.date={}".format(origine, destination, date)
	return(url)

#recupere texte de reponse
def requester(url):
	req = requests.get(url)
	reqtext = req.text
	return (reqtext)

#transformer date et heure depart(string) en un indice en int permettant de classer les trains par ordre croissant d'heure de depart
def indicetemps(datzi, depstr):
	print(depstr)
	dateconcat = datzi[5] + datzi[6] + datzi[8] + datzi[9]
	if depstr[1] == ":":
		depstr = "0" + depstr
	depconcat = depstr[0] + depstr[1] + depstr[3] + depstr[4]
	indice = dateconcat + depconcat
	indice_int = int(indice)
	return (indice_int)


#modification pour test
def sortups(liste, indice_tri):
	i = 0
	temp = 0
	while i < (len(liste) - 1):
		if liste[i][indice_tri] > liste[i + 1][indice_tri]:
			temp = liste[i]
			liste[i] = liste[i + 1]
			liste[i + 1] = temp
			i = -1
		i += 1
	return(liste)
	

#recupere une liste des trains dispos avec leurs infos importantes
def dataextractor(reqtext):
	data = json.loads(reqtext)
	totalstr = ""
	liste = []
	print("nb_train : ", len(data['records']))
	for t, train in enumerate(data['records']):
		print(train['fields']['train_no'])
		num = train['fields']['train_no']
		print(train['fields']['date'])
		datz = train['fields']['date']
		print(train['fields']['date'])
		print(train['fields']['heure_depart'])
		dep = train['fields']['heure_depart']
		depindice = indicetemps(datz, dep)
		print(depindice)
		print(train['fields']['heure_arrivee'])
		arr = train['fields']['heure_arrivee']
		print(train['fields']['origine'])
		ori = train['fields']['origine']
		print(train['fields']['destination'])
		dest = train['fields']['destination']
		print("######")
		liste.append([num, datz, dep, depindice, arr, ori, dest])
	print("nb_train : ", len(data['records']))
	return (liste)

#compare deux listes et retourne liste de nouveaux trains  si de nouveaux trains ont ete ajoutes
def listcompare(l1, l2):
	bol = 0
	new_trains = []
	for x, value in enumerate(l2):
		for b, valuz in enumerate(l1):
			if valuz[0] == value[0]:
				bol = 1
		if bol == 0:
			new_trains.append(value)
		bol = 0
	return(new_trains)

#transforme listes en string pretes a etre envoyees
def mailwriter(liste):
	mailstr = ""
	for x, value in enumerate(liste):
		mailstr = mailstr + "numero du train : " + str(value[0]) + "\n"
		mailstr = mailstr + "date : " + value[1] + "\n"
		mailstr = mailstr + "depart : " + value[2] + "\n"
		mailstr = mailstr + "arrivee : " + value[4] + "\n"
		mailstr = mailstr + "origine : " + value[5] + "\n"
		mailstr = mailstr + "destination : " + value[6] + "\n"
		mailstr = mailstr + "\n"
		mailstr = mailstr + "-------------------------"
		mailstr = mailstr + "\n"
	return(mailstr)

#envoie mail a adresse 'toaddr'
def mailsender(toaddr, mailtotal):
	fromaddr = "theoto.dev@gmail.com"
	passwd = #complete

	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.starttls()
	server.login(fromaddr, passwd)
	msg = EmailMessage()
	msg.set_content(mailtotal)
	msg['Subject'] = "de nouvelles places tgvmax sont disponibles"
	msg['From'] = fromaddr
	msg['To'] = toaddr
	server.sendmail(fromaddr, toaddr, msg.as_string())
	server.quit()

def main():

	#indice car il faut envoyer un premier mail avec tout et apres on envoie un mail uniquement quand il y a de nouveaux trains
	g = 0
	while 1:
		#premiere extraction
		h = sortups(dataextractor(requester(urlbuilder(date, origine, destination))), 3)
		time.sleep(3)
		#deuxieme apres attente
		i = sortups(dataextractor(requester(urlbuilder(date, origine, destination))), 3)
		mailintro = "Bonjour, voici les nouveaux trains disponibles pour les dates demandees : \n\n"
		#comparaison entre les 2 pour voir si nouveaux trains
		new_list = listcompare(h, i)
		print(len(new_list))
		#premier mail:
		if g == 0:
			mail_ready = "Bonjour, voici les trains disponibles pour la date demandee:\n\n" +  mailwriter(i)
			mailsender("theophile.lucille@gmail.com", mail_ready)
		#mail que si nouveaux trains
		else:
			if len(new_list) > 0:
				print("nouveaux trains dispos")
				mail_ready = mailintro + mailwriter(listcompare(h, i)) + "\n\n" + mailwriter(i)
				mailsender("theophile.lucille@gmail.com", mail_ready)
		g += 1
main()

