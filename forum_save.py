#!/usr/bin/python
"""
Autor: Adam Ormandy
Datum: 14.5.2015
Skript na stahovanie prispevkov na fore
"""

#################IMPORT###################

#Lepsi print
from __future__ import print_function
#Kvoli utf-8
import codecs
#Kniznica na stahovanie
import urllib2
#Regularne vyrazy
import re
#Parsovanie veci z html
from bs4 import BeautifulSoup
#Kvoli datumu
import time
from datetime import date

#################CLASS###################

#Aby sa lahsie pracovalo z jednotlivymi prispevkami
class prispevok:
    def __init__(self,meno,sprava=[],thread_id=0,thread=[]):
        self.meno=meno
        self.sprava=sprava
        self.thread_id=thread_id
        self.thread=thread
        self.datum=date(2008, 1, 1)

#################FUNKCIE###################

#ziska z 1 stranky fora cisla/id threadov, z ktorich sa da poskladat adresa 1 stranky threadu
#vrati list
def ziskanie_ulr_thread_stranka(html):
    #lebo id threadov je tam v tvare id="thread_title_[nase cislo]" 
    match = re.findall("\"thread_title_[0-9]+",html) 
    #vycistime si cisla od thread_title  
    index = 0
    for i in match:
         match[index] = re.findall("[0-9]+",match[index])
         index+=1
    list(match)
    return match

#def ziskanie_pocet_prispevkov

#aka je posledna stranka v danom threade alebo na celkovom fore
def ziskanie_last_index(html):
    match = re.findall("first_last.*?page[0-9]+",html) 
    match[0] = re.findall("[0-9]+$",match[0]) 
    return int(''.join(map(str,match[0])))

#Ziskanie uzivatela ktori pridal prispevok    
def ziskanie_uzivatela(soup,zoznam):
    index=0
    #Lebo <strong>Meno</strong>   
    for login in soup.find_all('div', class_=re.compile("popupmenu") ):
        login_class=prispevok( login.strong.string )
        zoznam.append(login_class)
        index+=1
    return index 

#Ziskanie datumu
def ziskanie_datumu(soup,zoznam,index):
    for datum in soup.find_all('span', class_=re.compile("^date$")):
        medziprvok=re.findall("[^ ,]*",datum.get_text())
        #Datum ak namiesto datumu tam bolo Today
        if(medziprvok[0]=="Today"):
            zoznam[index].datum=zoznam[index].datum.today()
        #Ak tam bolo Yesterday
        elif(medziprvok[0]=="Yesterday"):
            zoznam[index].datum=zoznam[index].datum.today()
            zoznam[index].datum=zoznam[index].datum.replace(day=(date.today().day)-1)
        #Ak tam bol normalny datum
        else:
            #Zmena roku
            zoznam[index].datum=zoznam[index].datum.replace(year=int(''.join(map(str,medziprvok[4])))) 
            #Zmena mesiaca
            zoznam[index].datum=zoznam[index].datum.replace(month=time.strptime(medziprvok[2],'%B').tm_mon)
            medziprvok=re.findall("^[0-9]*",datum.get_text())
            zoznam[index].datum=zoznam[index].datum.replace(day=int(''.join(map(str,medziprvok))))
        index+=1
    return index 

#Ziskanie samotneho textu prispevku
def ziskanie_spravy(soup,zoznam,index):
    #Ziskanie spravy <blockquote>Sprava</blockquote>
    for sprava in soup.find_all('div', class_=re.compile("postrow") ):
        zoznam[index].sprava=sprava.get_text()
        index+=1
    return index

#################MAIN###################

#url zaciatku, pridava sa page1 page2 page3 potom
forum_url="http://forum.kerbalspaceprogram.com/forums/35/page"

#Ziskame si id threadov
zoznam_threadov = []
i=1
pocet_stranok=1
print("Ziskavanie url threadov zo stranok fora:")
while ( i <= 1 ): #pocet_stranok
    response = urllib2.urlopen(forum_url+str(i))
    html = response.read() 
    #Kolko stranok je treba prejst 
    if ( i==1 ):
        pocet_stranok=ziskanie_last_index(html)
    zoznam_threadov[-1:-1]=ziskanie_ulr_thread_stranka(html)
    print("%d / %d" % (i,pocet_stranok))
    i+=1
    
print("Celkovo najdenych threadov: %d" % (len(zoznam_threadov)))


#Do slovniku si budeme pocet odpovedi v danom threade, co nam potom povie ci sa nepridali nove prispevky
#Nacitame data zo suboru, kde su olozene nami uz stiahnute thready, a pocet prispevkov ktore vtedi mali
#Sluzi na stiahnutie novych prispevkov, resp. rozpoznanie ze nejake boli pridane
log_subor= codecs.open("log.txt","a+","utf-8")
thread_responses={0:0}
thread_subor= codecs.open("thread.txt","a+","utf-8")
medziprvok=thread_subor.readlines()
index=0
while (index<1):
    thread_info=re.findall("[0-9]*",medziprvok[index])
    thread_responses[thread_info[0]]=thread_info[2]
    index+=1


#K tomuto sa budu pridavat id threadov ktore sme ziskali v predchadzajucom chode skriptu
thread_url="http://forum.kerbalspaceprogram.com/threads/"
for polozka_zoznam_threadov in zoznam_threadov: 
    print("Zaciatok spracovania threadu %s" % (polozka_zoznam_threadov[0]) )
    i=1
    pocet_stranok=1
    zoznam_prispevkov=[]

    while ( i <= pocet_stranok ):
        #Stiahnutie stranky
        spracovavany_thread=thread_url+(''.join(polozka_zoznam_threadov))+"/page"
        response = urllib2.urlopen(spracovavany_thread+str(i))
        html = response.read() 
        soup = BeautifulSoup(html)
        #Ak sme zacali tak zistime kolko stranok budeme musiet stiahnut
        if ( i==1 ):
            pocet_stranok=ziskanie_last_index(html)
        #Funckia nam vrati, kolko nacitala prispevkov
        pocet_novo_nacitanych=ziskanie_uzivatela(soup,zoznam_prispevkov)
        ziskanie_datumu(soup,zoznam_prispevkov,len(zoznam_prispevkov)-pocet_novo_nacitanych)
        #ziskanie_spravy(soup,zoznam_prispevkov,len(zoznam_prispevkov)-pocet_novo_nacitanych)
        i+=1

    #Cislo threadu a meno threadu
    for zaznam in zoznam_prispevkov:
        #Cislo threadu
        zaznam.thread_id=polozka_zoznam_threadov[0]
        #Meno threadu
        medziprvok=soup.find_all("span", class_="threadtitle")
        medziprvok=medziprvok[0].string
        zaznam.thread=medziprvok

    #Zapis do suboru
    for zaznam in zoznam_prispevkov:
        print("\n<post>", file=log_subor)
        print("    <user>%s</user>"%(zaznam.meno), file=log_subor)
        print("    <date>%s<date>"%(zaznam.datum), file=log_subor)
        print("    <thread_name>%s</thread_name>\n    <thread_id>%s</thread_id>"%(str(zaznam.thread),zaznam.thread_id), file=log_subor)
        print("    <body>%s</body>"%(str(zaznam.sprava)), file=log_subor)
        print("</post>\n", file=log_subor)

    print("Dokoncenie spracovanie threadu %s" % (polozka_zoznam_threadov[0]) )
    break
 
log_subor.close()   