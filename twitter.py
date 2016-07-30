#!/usr/bin/python
# -*- coding: utf-8 -*
"""
Autor: Adam Ormandy
Datum: 14.5.2015
Skript na stahovanie tweetov
"""



#################IMPORT###################

import sys
#Regex
import re
import os
#TWITTER API
import tweepy
#Stahovanie
import requests
requests.packages.urllib3.disable_warnings()
#Kvoli utf-8
import codecs

reload(sys)
sys.setdefaultencoding("UTF-8")

#################FUNKCIE###################

#Funkcia, ktora stahuje stranky do priecinka 
def stahovanie_stranok(url):
    #Ziskame meno suboru	
    meno_suboru = url.split("/")[2]+".html"

    #Vytvorime subor
    subor = codecs.open(meno_priecinka+meno_suboru,"w","utf-8-sig")
    
    if "http://t.co/" in url and len(url) == 22: 
		if url[len(url)-1] != ".":
			print url
			try:	    	
				response = requests.get(url)
				subor.write(response.content )
			except requests.exceptions.SSLError:

				print "Nespravna stranka"	    	
			
    subor.close()

def spracovanie_tweetov(zoznam,tweety,end_id):
    for tweet in tweety:
        if(int(end_id)==tweet.id):
             return 0
        zoznam.append(tweet)
    try:
        return tweet.id
    except UnboundLocalError:
       return 0
   

#################MAIN###################

#Textac do ktoreho zapisujeme tweety
meno_data_subor="./tweet_subor.txt"

#Limit kolko tweetom mozme stiahnut
limit=800		

#Meno twitter uctu z ktoreho stahuje
#+mnozstvo tweetow ktore ma stiahnut
meno_twitter_ucet="SpaceX"
pocet_twitter_ucet=200


#Bezpecnostne kluce Twitteru
consumer_key = 'XXXX'
consumer_secret =  'XXXX'
access_token = 'XXXX'
access_token_secret = 'XXXX'

#Prihlasenie
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

#Skontroluje ci sme uz niekedy stahovaly tweety
if os.path.isfile(meno_data_subor) == 1:	
    data_subor = codecs.open(meno_data_subor, "r", "utf-8-sig")	
    data_subor_obsah = data_subor.readlines()
    try:
         posledny_riadok = data_subor_obsah[len(data_subor_obsah)-1]
         end_id = posledny_riadok.split("\t")[0]			
         data_subor.close()
    except IndexError:
         end_id=0
else:
    end_id=0;

print end_id

#Id prveho tweetu nech mame kde zacat
try:
    posledny_tweet = api.user_timeline(meno_twitter_ucet, count = 1, since_id = 1)
    start_id=posledny_tweet[0].id
except "tweepy.error.TweepError":
    print "Twitter docasne zablokoval ucet, skript sa peto ukonci, skuste sa vratit o 20 minut"
    quit()

zastavovac=0
stiahnute_tweety=[]

print "Faza prechadzanie twitterom"
while(zastavovac==0):
    #Nacitanie tweetow
    try:
        public_tweets = api.user_timeline(meno_twitter_ucet, count = pocet_twitter_ucet, max_id=start_id)
    except "tweepy.error.TweepError":
        print "Twitter docasne zablokoval ucet, skript sa peto ukonci, skuste sa vratit o 20 minut"
        quit()
    start_id=spracovanie_tweetov(stiahnute_tweety,public_tweets,end_id)
    if ( len(stiahnute_tweety)>limit):
        zastavovac=1
    if (start_id==0):
        zastavovac=1

#Meno priecinka kam budeme ukladat stranky
meno_priecinka="./odkaz_stranky/"
#Ci existuje priecinok kam to chceme ukaladat
#Ak nie tak ho vytvorime
if not os.path.exists(meno_priecinka):
    os.makedirs(meno_priecinka)

#Ulozenie tweetow
print "Faza zapisovania novych tweetow do suboru"
data_subor = codecs.open(meno_data_subor, "a+", "utf-8-sig" ) 
#Aby na konci bol najnovsi tweet
for tweet in reversed(stiahnute_tweety):
   	#Zapisem id tweetu
   	id = str(tweet.id)
   	data_subor.write(id)   
   	data_subor.write("\t")
        
        #A spravu v tweete
   	text = tweet.text.replace('\n', ' ')
   	data_subor.write(text)
        data_subor.write("\n")

	#Keby tam boli dajake url
        """
        print "Faza stahovania stranok" 
   	urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        for url in urls:
            stahovanie_stranok(url)
        """
   	
data_subor.close()

