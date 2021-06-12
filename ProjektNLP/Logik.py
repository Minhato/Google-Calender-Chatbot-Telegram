from KalenderMethoden import kalenderAnlegen, kalenderLoeschen, kalenderAnlegen, terminAnlegen, terminBearbeiten, terminTitelBearbeiten, terminVerschiebenNeueUhrzeit, terminanzeigen, terminloeschen
import spacy
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
from spacy import displacy
from datetime import*
from re import*


#Korpus laden
nlp=spacy.load("de_core_news_sm")
matcher=Matcher(nlp.vocab)

text="Erstelle einen Termin"
#text = ""
#Doc ist text als Spacy Doc Objekt
doc =  nlp(text)
bereinigt=" ".join([token.text for token in doc if not token.is_stop and not token.is_punct])

print("bereingiter Text:")
print(bereinigt)
#Doc mit entfernten Stopwords
noStopwordDoc=nlp(bereinigt)

tokenListe=[]

def setText(eingabe):
    global text, doc, bereinigt, noStopwordDoc
    text = eingabe
    text=text+"."
    #Doc ist text als Spacy Doc Objekt
    doc =  nlp(text)
    bereinigt=" ".join([token.text for token in doc if not token.is_stop and not token.is_punct])
    noStopwordDoc = nlp(bereinigt)



def getTokenList():
    #Liste mit Tokens zum checken
    for token in noStopwordDoc:
        if(token.is_stop == False or token.pos_=="NOUN"):
            tokenListe.append(token.lemma_)
    
def checkActionKind(usereingabe):
    print("nostopword")
    print(noStopwordDoc)
    setText(usereingabe)
    # for token in noStopwordDoc:
    #     if(token.pos_=="NOUN"):
    #         print(token.text)
    #         if(token.text=="Kalender"):
    #             return "Kalender"
    #         if(token.text=="Termin"or"Meeting"or"Treffen"):
    #             print("Der TOKEN HIER IST" + token.text)
    #             return "Termin"
    #         if(token.text=="Geburtstag"):
    #             return"Geburtstag"
    for token in noStopwordDoc:
        if(token.text=="Kalender"):
            return "Kalender"
        elif(token.lemma_=="Termin"or token.lemma_ == "Meeting"or token.lemma_ =="Treffen"):
            print("Der TOKEN HIER IST" + token.text)
            return "Termin"
        elif(token.text=="Geburtstag"):
            return"Geburtstag"

def getIntend(userInput,kindOfRequest):
    matcher=Matcher(nlp.vocab)
    userInput=userInput+"."
    #List of Intends für mögliche aktionen für den matcher.
    listOfIntends=["anlegen","anzeigen","machen","löschen","ändern","verschieben","verlegen","eintragen","erstellen","lege","ändere","lösche","erstelle","verschiebe","verlege","mache","zeige","bearbeite", "bearbeiten"]
    #Pattern anlegen
    patterns=[
        [{"LOWER":"erstelle"},{"POS":"DET"},{"TEXT":kindOfRequest}],
        [{"LOWER":"mache"},{"POS":"DET"},{"TEXT":kindOfRequest}],
        [{"LOWER":"trage"},{"POS":"DET"},{"TEXT":kindOfRequest}],
        [{"LOWER":"ändere"},{"POS":"DET"},{"TEXT":kindOfRequest}],
        [{"LOWER":"bearbeite"},{"POS":"DET"},{"TEXT":kindOfRequest}],
        [{"LOWER":"lösche"},{"POS":"DET"},{"TEXT":kindOfRequest}],
        [{"LOWER":"lege"},{"POS":"DET"},{"TEXT":kindOfRequest}],
        [{"LOWER":"verschiebe"},{"POS":"DET"},{"TEXT":kindOfRequest}],
        [{"LOWER":"verlege"},{"POS":"DET"},{"TEXT":kindOfRequest}],
        [{"LOWER":"zeige"},{"POS":"PRON","OP":"?"},{"POS":"DET"},{"LEMMA":kindOfRequest}],
        [{"LEMMA":kindOfRequest},{"POS":"VERB"}],
        [{"POS":"VERB"},{"IS_PUNCT":True}]
        
    
    ]
    
    matcher.add("Intention",patterns)
    testDoc= nlp(userInput)
    matches= matcher(testDoc)

    for match_id,start, end in matches:

        string_id=nlp.vocab.strings[match_id]
        span=testDoc[start:end]
        intend=span.text.replace(kindOfRequest,"").replace(" ","").replace(".","")
    if(intend in listOfIntends or len(intend)>7):
            if "lege"in intend.lower() or "erstelle"in intend.lower() or"trage"in intend.lower() or "mache" in intend.lower():
                return "erstellen"
            elif "änder" in intend.lower() or "bearbeite" in intend.lower():
                return "bearbeiten"
            elif "lösche"in intend.lower():
                return "loeschen"
            elif "verschiebe"in intend.lower() or "verlege" in intend.lower():
                return "verschiebe"
            elif "zeige" in intend.lower():
                return "zeige an"
            else:
                return"kein pattern für Intend gefunden"
    

def calculateWithWeekdays(requestedWeekday):
    """Gibt für einen gewünschten Wochentag das entsprechende Datum zurück"""
    #Wochentag zum iterieren über die while Schleife
    weekdayToday=date.weekday(date.today())
    calculatedDate=date.today()
    #statisches Startdatum
    startDatum=date.weekday(date.today())

    while(weekdayToday != requestedWeekday):
        
        calculatedDate=calculatedDate+timedelta(days=1)
        
        weekdayToday=date.weekday(calculatedDate)

    stringCalculatedDate=str(calculatedDate)
    formatedDate=datetime.strptime(stringCalculatedDate,'%Y' '-' '%m' '-' '%d').strftime('%d' '.' '%m' '.' '%Y')          #Format verändern auf dd.dd.dddd
    return str(formatedDate)

def getDatum(erkannterTag):
    #heutigesDatum
    heute=date.today()
    #globale Variable datumNextWeek in die Ergebis der Methode getDateNextWeek gespeichert wird,die in der for schleife der erkannten patterns aufgerufen wird
    datumNextWeek=date.today()
    #aus Parameter wird NLP objekt erstellt
    datumNlp =nlp(erkannterTag)
    #patterns
    patterns=[
        [{"LEMMA":"nächst"},{"TEXT":"Woche","OP":"?" },{"TEXT":{"REGEX":"\w*tag\b"}}],
        [{"LEMMA":"nächst"},{"TEXT":"Woche","OP":"?" },{"TEXT":"Mittwoch"}]
        
        
    ]
    #Matcher wird inizialisiert
    matcher.add("Weekdays",patterns)
    testDoc= nlp(erkannterTag)
    matches= matcher(testDoc)
    
    possibleDate={
        "heute":str(heute.strftime('%d' '.' '%m' '.' '%Y') ),
        "morgen":str((heute+timedelta(days=1)).strftime('%d' '.' '%m' '.' '%Y') ),
        "übermorgen":str((heute+timedelta(days=2)).strftime('%d' '.' '%m' '.' '%Y') ),
        "Montag":calculateWithWeekdays(0),
        "Dienstag":calculateWithWeekdays(1),
        "Mittwoch":calculateWithWeekdays(2),
        "Donnerstag":calculateWithWeekdays(3),
        "Freitag":calculateWithWeekdays(4),
        "Samstag":calculateWithWeekdays(5),
        "Sonntag":calculateWithWeekdays(6)
    }
    #Methode getDateNextWeek wird aufgerufen wenn pattern gematched wird
    def getDateNextWeek(spanText):
        WeekdayNextWeek = spanText.replace("nächsten","").replace("nächste","").replace("Woche","").replace(" ","")
        if(heute.weekday()<=possibleDate[WeekdayNextWeek].weekday()):
            return possibleDate[WeekdayNextWeek]+timedelta(days=7)
        else:
            return possibleDate[WeekdayNextWeek]
    
    #for Schleife die für Pattern match getDateNextWeek aufruft
    for match_id,start,end in matches:
        string_id=nlp.vocab.strings[match_id]            
        span=testDoc[start:end]
        datumNextWeek=getDateNextWeek(span.text)
    #return der getDatum Methode
    #deutsches Datum->return des Formatieren Datums
    #Leeres Array==Kein Pattern gefunden->normaler aufruf über dictonary
    #else->Aufruf der globalen Variable datumNextWeek in die Datum für die nächste Woche gespeichert wurde
    for token in datumNlp:
        if token.shape_=="dd.dd.dddd":
            #Platz zum formatieren des Datums zum google api Standart
            return token.text
    if(matches==[]):
        
        return possibleDate.get(erkannterTag)
    else:
        return datumNextWeek

def getDateText(userText):
    doc=nlp(userText)
    Wochentage=["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]
    MonateValue={
        "Jannuar":"01",
        "Februar":"02",
        "März":"03",
        "April":"04",
        "Mai":"05",
        "Juni":"06",
        "Juli":"07",
        "August":"08",
        "September":"09",
        "Oktober":"10",
        "November":"11",
        "Dezember":"12"
    }
    userDatum =""
    for token in doc:
        if token.shape_=="dd."or token.shape_=="d."or token.shape_=="d" and token.head.text in MonateValue:
            tag=token.text
        if token.text=='heute' or token.text=='morgen' or token.text=='übermorgen':
            return token.text
        if token.shape_=="d.":
            tag="0"+tag
            monat=MonateValue[token.head.text]                
            jahr=datetime.now().year
            userDatum=tag+monat+"."+str(jahr)
            return str(userDatum)
        elif token.shape_=="dd.dd.dddd":
                userDatum=token.text
                return str(token.text)
        elif token.lemma_=="nächst" or token.text=="Woche":
                userDatum=" ".join([userDatum,token.text])
        elif token.text in Wochentage:
                userDatum=" ".join([userDatum,token.text])
                if(len(userDatum)<10):
                    userDatum=userDatum[1:]
                return str(userDatum)
    




def getLocation():
    #UNFINISHED Soll Location des Termins Liefern falls Vorhanden
    for ent in doc.ents:
        if(ent.label_ == "LOC"):
            return ent.text
            

def getTitel(text):
    matcher=PhraseMatcher(nlp.vocab)
    term = ["titel"]
    patterns = [nlp.make_doc(text) for text in term]
    matcher.add("titel", patterns)
    titel = None
    doc = nlp(text)
    lower_doc =  str(doc).lower()
    matches = matcher(nlp(lower_doc))

    for match_id, start, end in matches:
        titel = doc[end:len(doc)]
        return titel

    if not matches: 
        print("Keinen Titel gefunden was wollen Sie als Titel haben?")
        #input bla bla into Titel
#getTitel("erstelle einen Termin um 14 Uhr mit dem Titel Hallo was geht ab")


def getUhrzeit(index):
    uhrzeiten= []
    try:
        for token in doc:
            if token.shape_ == "dd":
                tokendd = str(token.text) + ":00"
                uhrzeiten.append(tokendd)

            elif token.shape_ == "dd:dd":
                uhrzeiten.append(token.text)
        if len(uhrzeiten) == 1:
            enduhrzeit = uhrzeiten[0]
            enduhrzeit = datetime.strptime(enduhrzeit, '%H:%M').replace(second=0) + timedelta( minutes= 30)
            enduhrzeit = enduhrzeit.time().strftime('%H:%M')
            uhrzeiten.append(str(enduhrzeit))
        return uhrzeiten[index]
    except IndexError:
        print("Keine Uhrzeiten gefunden")
        return None 

class Logik(object):
    def __init__(self,):
     pass
    def __init__(self) -> None:
        super().__init__()
    
    def ausgeben(self):
        print("ausgeben aus der Logik Klasse")
        print(self.datum)
        print("---")
        print(type(self.datum))
        print("---")
    def testest(self):
        datum= self.datum
        if self.intend == "zeige an":
            datumAlsDate = datetime.strptime(datum, "%d" "." "%m" "." "%Y")
            jahr = int (datetime.strftime(datumAlsDate,"%Y"))
            monat = int (datetime.strftime(datumAlsDate,"%m"))
            tag = int (datetime.strftime(datumAlsDate,"%d"))
        
        elif self.intend == "erstellen" and self.art == "Termin": # usw TO:DO
            startUhrzeit= datetime.strptime(self.uhrzeit, "%H" ":" "%M")
            endUhrzeit= datetime.strptime(self.enduhrzeit, "%H" ":" "%M")
            #startUhrzeit= datetime.strptime(self.uhrzeit, ) 
            print("Datum ist: " + str(datum))
            datumAlsDate = datetime.strptime(datum, "%d" "." "%m" "." "%Y")
            jahr = int (datetime.strftime(datumAlsDate,"%Y"))
            monat = int (datetime.strftime(datumAlsDate,"%m"))
            tag = int (datetime.strftime(datumAlsDate,"%d"))
            stunde = int (datetime.strftime(startUhrzeit,"%H"))
            minute = int (datetime.strftime(startUhrzeit,"%M"))
            #neueStunde, neueMinute = 5 #TO:DO
            endStunde = int (datetime.strftime(endUhrzeit,"%H"))
            endMinute = int (datetime.strftime(endUhrzeit,"%M")) 

        elif self.intend == "bearbeiten":
            startUhrzeit= datetime.strptime(self.uhrzeit, "%H" ":" "%M")
            datumAlsDate = datetime.strptime(datum, "%d" "." "%m" "." "%Y")
            jahr = int (datetime.strftime(datumAlsDate,"%Y"))
            monat = int (datetime.strftime(datumAlsDate,"%m"))
            tag = int (datetime.strftime(datumAlsDate,"%d"))
            stunde = int (datetime.strftime(startUhrzeit,"%H"))
            minute = int (datetime.strftime(startUhrzeit,"%M"))

        elif self.intend == "verschiebe":
            startUhrzeit= datetime.strptime(self.uhrzeit, "%H" ":" "%M")
            neueUhrzeit = startUhrzeit + timedelta(hours= 2)
            datumAlsDate = datetime.strptime(datum, "%d" "." "%m" "." "%Y")
            jahr = int (datetime.strftime(datumAlsDate,"%Y"))
            monat = int (datetime.strftime(datumAlsDate,"%m"))
            tag = int (datetime.strftime(datumAlsDate,"%d"))
            stunde = int (datetime.strftime(startUhrzeit,"%H"))
            minute = int (datetime.strftime(startUhrzeit,"%M"))
            neueStunde = int (datetime.strftime(neueUhrzeit,"%H"))
            neueMinute = minute
            endStunde = neueStunde + 1 
            endMinute = neueMinute

        if self.intend == "loeschen" and self.art == "Termin":
            datumAlsDate = datetime.strptime(datum, "%d" "." "%m" "." "%Y")
            startUhrzeit= datetime.strptime(self.uhrzeit, "%H" ":" "%M")
            jahr = int (datetime.strftime(datumAlsDate,"%Y"))
            monat = int (datetime.strftime(datumAlsDate,"%m"))
            tag = int (datetime.strftime(datumAlsDate,"%d"))
            stunde = int (datetime.strftime(startUhrzeit,"%H"))
            minute = int (datetime.strftime(startUhrzeit,"%M"))
            print("Daten in testetst Fehlerhaft")

        if self.intend == "erstellen" and self.art == "Termin":
            print("Termin wird angelegt")
            return terminAnlegen(jahr,monat,tag, stunde,minute,endStunde,endMinute,str(self.titel), " ")
        elif self.intend == "bearbeiten" and self.art == "Termin":
            return terminTitelBearbeiten(jahr,monat,tag,stunde,minute,str(self.titel))
        elif self.intend == "verschiebe" and self.art == "Termin":
            return terminVerschiebenNeueUhrzeit(jahr,monat,tag,stunde,minute,neueStunde,neueMinute,endStunde,endMinute )
        #      elif self.neueUhrzeit != None:
        #          terminBearbeiten(jahr,monat,tag,stunde,minute,neueStunde,neueMinute,endStunde,endMinute)
        #elif self.intend == "verschieben": # and self.art == "Termin":
        #     #alel bearbeitungsfälle
        #     terminBearbeiten(jahr,monat,tag,stunde,minute,titel)    
        elif self.intend == "loeschen" and self.art == "Termin":
            return terminloeschen(jahr,monat,tag,stunde,minute)
        elif self.intend == "zeige an" and self.art == "Termin":
            return terminanzeigen(jahr,monat,tag)
        elif self.intend == "erstellen" and self.art == "Kalender":
            return kalenderAnlegen(str(self.titel))
        elif self.intend == "loeschen" and self.art == "Kalender":
             return kalenderLoeschen(str(self.titel))
