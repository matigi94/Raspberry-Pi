from lywsd02 import Lywsd02Client
import urllib.request
# ~ import base64
import time

import xml.etree.ElementTree as ET
from mijia.mijia_poller import MijiaPoller, \
    MI_HUMIDITY, MI_TEMPERATURE, MI_BATTERY

# ~ mac = 'A4:C1:38:25:67:59' #salon
# ~ mac2 = 'A4:C1:38:fd:0e:0a' #lazienka
# ~ mac3 = 'A4:C1:38:6a:a4:d0' #maly
# ~ mac4 = 'e7:2e:00:13:10:b0' #kuchnia
# ~ Devices = [mac3,mac,mac2,mac4]
# ~ client = Lywsd02Client(mac)
# ~ client2 =Lywsd02Client(mac2)
# ~ client3 =Lywsd02Client(mac3)
# ~ client4 =Lywsd02Client(mac4)

domoticzserver   = ""
domoticzport     = ""
domoticzusername = ""
domoticzpassword = ""
domoticzdelay = 0
domoticzenable = "true"



class Sensor_():
    def __init__(self):
        self.Nazwa = None
        self.Mac = None
        self.Typ = None
        self.Stan = None
        self.Temp = None
        self.Wilg = None
        self.idx = None

def Read_config():

    global domoticzserver
    global domoticzport
    global domoticzdelay
    global domoticzenable
    
    global tree
    global root
    global Czujniki
    tree = ET.parse('czujniki.xml')
    root = tree.getroot()

    for Czujnik_EL in root.iterfind("config"):
        
        domoticzserver = Czujnik_EL.findtext("ip")
        domoticzport = Czujnik_EL.findtext("port")
        domoticzdelay = Czujnik_EL.findtext("delay")
        domoticzenable = Czujnik_EL.findtext("enable")
    
     

    Czujniki = list()
def Read_Sensors():
    
    global cnt
    global tree
    global root
    global Czujniki
    tree = ET.parse('czujniki.xml')
    root = tree.getroot()

    cnt =0
    
    for Czujnik_EL in root.iterfind("Czujnik"):
        Czujnik_ = Sensor_()
        
        Czujnik_.Mac = Czujnik_EL.findtext("Mac")
        Czujnik_.Nazwa = Czujnik_EL.findtext("Nazwa")
        Czujnik_.Typ = Czujnik_EL.findtext("Typ")
        Czujnik_.Stan = Czujnik_EL.findtext("Stan")
        Czujnik_.Temp = Czujnik_EL.findtext("Temperatura")
        Czujnik_.Wilg = Czujnik_EL.findtext("Wilgotnosc")
        Czujnik_.idx = Czujnik_EL.findtext("idx")
        cnt+=1
        Czujniki.append(Czujnik_)
    return(cnt)




    




def domoticzreq(idx,temp,hum,bat):
    
  
    adr = "http://"+domoticzserver+":"+domoticzport+"/json.htm?type=command&param=udevice&idx="+str(idx)+"&nvalue=0&svalue=" + str(temp) + ";" + str(hum)+ ";0&battery="+str(bat)
    with urllib.request.urlopen(adr) as response:
        html = response.read()


def update(address,idx_temp):

    poller = MijiaPoller(address)


    loop = 0
    try:
        temp = poller.parameter_value(MI_TEMPERATURE)
    except:
        temp = "Not set"
    
    while loop < 2 and temp == "Not set":
        print("Error reading value retry after 5 seconds...\n")
        time.sleep(5)
        poller = MijiaPoller(address)
        loop += 1
        try:
            temp = poller.parameter_value(MI_TEMPERATURE)
        except:
            temp = "Not set"
    
    if temp == "Not set":
        print("Error reading value\n")
        return
    
    global domoticzserver

    print("Mi Sensor: " + address)
    print("Firmware: {}".format(poller.firmware_version()))
    print("Name: {}".format(poller.name()))
    print("Temperature: {}°C".format(poller.parameter_value(MI_TEMPERATURE)))
    print("Humidity: {}%".format(poller.parameter_value(MI_HUMIDITY)))
    print("Battery: {}%".format(poller.parameter_value(MI_BATTERY)))

    val_bat  = "{}".format(poller.parameter_value(MI_BATTERY))
    
    # Update temp
    #val_temp = "{}".format(poller.parameter_value(MI_TEMPERATURE))
    #domoticzrequest("http://" + domoticzserver + "/json.htm?type=command&param=udevice&idx=" + idx_temp + "&nvalue=0&svalue=" + val_temp + "&battery=" + val_bat)

    # Update humidity
    #val_hum = "{}".format(poller.parameter_value(MI_HUMIDITY))
    #domoticzrequest("http://" + domoticzserver + "/json.htm?type=command&param=udevice&idx=" + idx_hum + "&svalue=" + val_hum + "&battery=" + val_bat)

    #/json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=TEMP;HUM;HUM_STAT
    val_temp = "{}".format(poller.parameter_value(MI_TEMPERATURE))
    val_hum = "{}".format(poller.parameter_value(MI_HUMIDITY))
    
    val_comfort = "0"
    if float(val_hum) < 40:
        val_comfort = "2"
    elif float(val_hum) <= 70:
        val_comfort = "1"
    elif float(val_hum) > 70:
        val_comfort = "3"
    
    domoticzreq(idx_temp,val_temp,val_hum,val_bat)




try:
    Read_config()
    Read_Sensors()
except:
    raise SystemExit
print("Domoticz adres: " +domoticzserver+":"+domoticzport+"\t")


while 1>0:
    for czujnik in Czujniki:
        #print(czujnik.Mac)
        print(czujnik.Nazwa+"\t"+czujnik.Typ)

        if czujnik.Typ == "Lywsd02":
            try:
                client = Lywsd02Client(czujnik.Mac)
                
                data=client.data
                domoticzreq(czujnik.idx,data.temperature,data.humidity,client.battery)
                print("Temperatura \t: "+str(data.temperature))
                print("Wilgotnosc \t: "+str(data.humidity)+"\n")
            except:
                print("error")
        else:
            print("hello")
            try:
            #    client = Lywsd02Client(czujnik.Mac)
                update(czujnik.Mac,czujnik.idx)
            except:
                print("error")
 
 
 
    print("wait :"+str(domoticzdelay)+"s")
    time.sleep(int(domoticzdelay))
