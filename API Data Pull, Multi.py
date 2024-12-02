
import requests
from requests.auth import HTTPBasicAuth
import time
import datetime
import json, os
import pyodbc
import re
import sys
from tkinter import messagebox
import multiprocessing
from multiprocessing import Manager
from icecream import ic
import urllib3
urllib3.disable_warnings()
#Attmepted
#os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
#os.environ['SSL_CERT_FILE'] = certifi.where()
dataPullTime = 1
email = 'omops@narenco.com'
with open(r"G:\Shared drives\O&M\NCC Automations\Credentials\app credentials.json", 'r') as credsfile:
    creds = json.load(credsfile)
password = creds['credentials']['AlsoEnergy']
base_url = "https://api.alsoenergy.com"
token_endpoint = "/Auth/token"

sites_endpoint = "/Sites"
#Sites and Hardware Devices
hw_sites_mapping = {
"Cherry": {
        "breakers":{
        "208909": "SEL-651R Recloser Relay"
    },
    "meters":{
        "208321": "SEL 735 Meter",
    },
    "inverters": {
        "208322": "SMA SC 2500EV-US Inverter - 1",
        "208323": "SMA SC 2500EV-US Inverter - 2",
        "208912": "SMA SC 2500EV-US Inverter - 3",
        "208913": "SMA SC 2500EV-US Inverter - 4"
    },
    "weather_stations": {
        "208332": "Weather Station 3 (Dual Mod Temp)"
    },
},
"Cougar": {
    "meters":{
        "526547": "Revenue Meter",
    },
    "inverters": {
        "526548": "Inverter 1-1",
        "526549": "Inverter 1-2",
        "526550": "Inverter 1-3",
        "526551": "Inverter 1-4",
        "526552": "Inverter 1-5",
        "526553": "Inverter 2-1",
        "526554": "Inverter 2-2",
        "526555": "Inverter 2-3",
        "526556": "Inverter 2-4",
        "526557": "Inverter 2-5",
        "526558": "Inverter 3-1",
        "526559": "Inverter 3-2",
        "526560": "Inverter 3-3",
        "526561": "Inverter 3-4",
        "526562": "Inverter 3-5",
        "526563": "Inverter 4-1",
        "526564": "Inverter 4-2",
        "526565": "Inverter 4-3",
        "526566": "Inverter 4-4",
        "526567": "Inverter 4-5",
        "526568": "Inverter 5-1",
        "526569": "Inverter 5-2",
        "526570": "Inverter 5-3",
        "526571": "Inverter 5-4",
        "526572": "Inverter 5-5",
        "526573": "Inverter 6-1",
        "526574": "Inverter 6-2",
        "526575": "Inverter 6-3",
        "526576": "Inverter 6-4",
        "526577": "Inverter 6-5"
    },
    "weather_stations": {
        "526579": "KZPOA"
    },
},
"CDIA": {
    "inverters": {
        "526644": "SatCon Inverter",
    },
    "weather_stations": {
        "526645": "Weather Station"
    },
},
"Wellons": {
    "meters":{
        "64337": "SEL 735 Meter",
    },
    "inverters": {
        "63751": "Inverter 1-1 - SMA 800CP-US",
        "63752": "Inverter 1-2 - SMA 800CP-US",
        "63971": "Inverter 2-1 - SMA 800CP-US",
        "63972": "Inverter 2-2 - SMA 800CP-US",
        "63973": "Inverter 3-1 - SMA 800CP-US",
        "63974": "Inverter 3-2 - SMA 800CP-US"
    },
    "weather_stations": {
        "59644": "Weather Station GHI & POA"
    }
},
"Wayne 2": {
    "meters":{
        "94184": "SEL 735 Meter",
    },
    "inverters": {
        "94194": "PowerOne Ultra 1500 TL - 1",
        "94196": "PowerOne Ultra 1500 TL - 2",
        "94198": "PowerOne Ultra 1000 TL - 3",
        "94202": "PowerOne Ultra 1000 TL - 4"
    },
    "weather_stations": {
        "93621": "Weather Station (POA GHI)"
    }
},
"Wayne 1": { 
    "meters":{
        "94094": "SEL 735 Meter",
    },
    "inverters": {
        "94089": "PowerOne Ultra 1000TL 1",
        "94090": "PowerOne Ultra 1000TL 2",
        "94091": "PowerOne Ultra 1500TL 3",
        "94092": "PowerOne Ultra 1500TL 4"
    },
    "weather_stations": {
        "93627": "Weather Station (POA GHI)"
    }
},
"Wayne 3": {
    "meters":{
        "94284": "SEL 735 Meter",
    },
    "inverters": {
        "94297": "PowerOne Aurora Ultra 1000TL 1",
        "94298": "PowerOne Aurora Ultra 1500TL 2",
        "94299": "PowerOne Aurora Ultra 1500TL 3",
        "94300": "PowerOne Aurora Ultra 1000TL 4"
    },
    "weather_stations": {
        "93624": "Weather Station (POA GHI)"
    }
},
"Duplin": {
    "meters":{
        "94074": "SEL 735 Meter",
    },
    "inverters": {
        "94053": "ABB Ultra 1500TL 1 - Central Inverter",
        "94055": "ABB Ultra 1500TL 2 - Central Inverter",
        "94054": "ABB Ultra 1500TL 3 - Central Inverter",
        "94056": "ABB Trio 24TL 1 - String Inverter",
        "94057": "ABB Trio 24TL 2 - String Inverter",
        "94058": "ABB Trio 24TL 3 - String Inverter",
        "94059": "ABB Trio 24TL 4 - String Inverter",
        "94060": "ABB Trio 24TL 5 - String Inverter",
        "94061": "ABB Trio 24TL 6 - String Inverter",
        "94062": "ABB Trio 24TL 7 - String Inverter",
        "94063": "ABB Trio 24TL 8 - String Inverter",
        "94064": "ABB Trio 24TL 9 - String Inverter",
        "94065": "ABB Trio 24TL 10 - String Inverter",
        "94066": "ABB Trio 24TL 11 - String Inverter",
        "94067": "ABB Trio 24TL 12 - String Inverter",
        "94068": "ABB Trio 24TL 13 - String Inverter",
        "94069": "ABB Trio 24TL 14 - String Inverter",
        "94070": "ABB Trio 24TL 15 - String Inverter",
        "94071": "ABB Trio 24TL 16 - String Inverter",
        "94072": "ABB Trio 24TL 17 - String Inverter",
        "94073": "ABB Trio 24TL 18 - String Inverter"
    },
    "weather_stations": {
        "93630": "Weather Station (POA GHI)"
    }
},
"Conetoe": {
    "meters":{
        "156535": "SEL 735 Meter",
    },
    "inverters": {
        "156547": "Inverter INV 01",
        "156548": "Inverter INV 02",
        "156549": "Inverter INV 03",
        "156550": "Inverter INV 04"
    },
    "weather_stations": {
        "156561": "POA Pyranometer SE 01",
    },
},
"Violet": {
    "breakers":{
        "390117": "651 R-1",
        "390118": "651 R-2"
    },
    "meters":{
        "390113": "SEL 735 Meter",
    },
    "inverters": {
        "390119": "Inverter 01",
        "390120": "Inverter 02"
    },
    "weather_stations": {
        "390114": "KZ POA"
    },
},
"Hickory": {
    "breakers":{
        "207199": "651R Recloser",
    },
    "meters":{
        "207198": "SEL 735 Meter",
    },
    "inverters": {
        "207201": "SMA SC 2500-EV-US Inverter 1",
        "207202": "SMA SC 2500 EV-US Inverter 2",
    },
    "weather_stations": {
        "207194": "Weather Station Modbus 16 (Standard w/ Hukseflux POA)"
    },
},
"Bluebird": {
    "meters":{
        "245183": "SEL 735 Meter"
    },
        "inverters": {
            "245187": "Inverter A1",
            "245188": "Inverter A2",
            "245189": "Inverter A3",
            "245190": "Inverter A4",
            "245191": "Inverter A5",
            "245192": "Inverter A6",
            "245193": "Inverter A7",
            "245194": "Inverter A8",
            "245195": "Inverter A9",
            "245196": "Inverter A10",
            "245197": "Inverter A11",
            "245198": "Inverter A12",
            "245199": "Inverter B13",
            "245200": "Inverter B14",
            "245202": "Inverter B15",
            "245203": "Inverter B16",
            "245204": "Inverter B17",
            "245205": "Inverter B18",
            "245206": "Inverter B19",
            "245207": "Inverter B20",
            "245208": "Inverter B21",
            "245209": "Inverter B22",
            "245210": "Inverter B23",
            "245211": "Inverter B24",
        },
        "weather_stations": {
            "245217": "Kipp & Zonen SMP-6 (POA)",
        }
},
"Freight Line": {
    "meters":{
        "245219": "SEL 735 Meter"
    },
    "inverters": {
        "245225": "Sungrow SG125HV - Inverter - 1 at 100%",
        "245226": "Sungrow SG125HV - Inverter - 2 at 66.4%",
        "245227": "Sungrow SG125HV - Inverter - 3 at 100%",
        "245228": "Sungrow SG125HV - Inverter - 4 at 100%",
        "245229": "Sungrow SG125HV - Inverter - 5 at 100%",
        "245230": "Sungrow SG125HV - Inverter - 6 at 67.2%",
        "245231": "Sungrow SG125HV - Inverter - 7 at 66.40%",
        "245232": "Sungrow SG125HV - Inverter - 8 at 100%",
        "245233": "Sungrow SG125HV - Inverter - 9 at 100%",
        "245234": "Sungrow SG125HV - Inverter - 10 at 100%",
        "245235": "Sungrow SG125HV - Inverter - 11 at 100%",
        "245236": "Sungrow SG125HV - Inverter - 12 at 100%",
        "245237": "Sungrow SG125HV - Inverter - 13 at 66.40%",
        "245238": "Sungrow SG125HV - Inverter - 14 at 66.40%",
        "245239": "Sungrow SG125HV - Inverter - 15 at 100%",
        "245240": "Sungrow SG125HV - Inverter - 16 at 100%",
        "245241": "Sungrow SG125HV - Inverter - 17 at 100%",
        "245242": "Sungrow SG125HV - Inverter - 18 at 100%"
    },
    "weather_stations": {
        "245224": "Kipp & Zonen SMP6 - POA"
    },
},
"Holly Swamp": {
    "meters":{
        "243744": "SEL 735 Meter"
    },
    "inverters": {
        "243750": "Sungrow SG 125HV - Inverter - 1 at 100%",
        "243751": "Sungrow SG 125HV - Inverter - 2 at 100%",
        "243752": "Sungrow SG 125HV - Inverter - 3 at 100%",
        "243753": "Sungrow SG 125HV - Inverter - 4 at 100%",
        "243754": "Sungrow SG 125HV - Inverter - 5 at 100%",
        "243755": "Sungrow SG 125HV - Inverter - 6 at 100%",
        "243756": "Sungrow SG 125HV - Inverter - 7 at 100%",
        "243757": "Sungrow SG 125HV - Inverter - 8 at 100%",
        "243758": "Sungrow SG 125HV - Inverter - 9 at 100%",
        "243759": "Sungrow SG 125HV - Inverter - 10 at 100%",
        "243760": "Sungrow SG 125HV - Inverter - 11 at 100%",
        "243761": "Sungrow SG 125HV - Inverter - 12 at 100%",
        "243762": "Sungrow SG 125HV - Inverter - 13 at 100%",
        "243763": "Sungrow SG 125HV - Inverter - 14 at 100%",
        "243764": "Sungrow SG 125HV - Inverter - 15 at 100%",
        "243765": "Sungrow SG 125HV - Inverter - 16 at 99.2%"
    },
    "weather_stations": {
        "243749": "Kipp & Zonen SMP6 - POA"
    },
},
"PG": {
    "meters":{
        "244717": "SEL 735 Meter",
    },
    "inverters": {
        "244726": "Sungrow SG125HV - Inverter - 1 at 66.4%",
        "244727": "Sungrow SG125HV - Inverter - 2 at 66.4%",
        "244728": "Sungrow SG125HV - Inverter - 3 at 66.4%",
        "244729": "Sungrow SG125HV - Inverter - 4 at 66.4%",
        "244730": "Sungrow SG125HV - Inverter - 5 at 66.4%",
        "244731": "Sungrow SG125HV - Inverter - 6 at 67.2%",
        "244732": "Sungrow SG125HV - Inverter - 7 at 100%",
        "244733": "Sungrow SG125HV - Inverter - 8 at 100%",
        "244734": "Sungrow SG125HV - Inverter - 9 at 100%",
        "244735": "Sungrow SG125HV - Inverter - 10 at 100%",
        "244736": "Sungrow SG125HV - Inverter - 11 at 100%",
        "244737": "Sungrow SG125HV - Inverter - 12 at 100%",
        "244738": "Sungrow SG125HV - Inverter - 13 at 100%",
        "244739": "Sungrow SG125HV - Inverter - 14 at 100%",
        "244740": "Sungrow SG125HV - Inverter - 15 at 100%",
        "244741": "Sungrow SG125HV - Inverter - 16 at 100%",
        "244742": "Sungrow SG125HV - Inverter - 17 at 100%",
        "244743": "Sungrow SG125HV - Inverter - 18 at 100%"
    },
    "weather_stations": {
        "300014": "Kipp & Zonen SMP6 - POA"
    },
},
"Harrison": {
    "breakers":{
        "298804": "SEL 751",
    },
    "meters":{
        "264620": "SEL 735 Meter",
    },
    "inverters": {
        "264649": "Sungrow SG125HV Inverter - 1 at 91.2%",
        "264650": "Sungrow SG125HV Inverter - 2 at 93.6%",
        "264651": "Sungrow SG125HV Inverter - 3 at 93.6%",
        "264652": "Sungrow SG125HV Inverter - 4 at 93.6%",
        "264654": "Sungrow SG125HV Inverter - 5 at 93.6%",
        "264655": "Sungrow SG125HV Inverter - 6 at 93.6%",
        "264656": "Sungrow SG125HV Inverter - 7 at 93.6%",
        "264657": "Sungrow SG125HV Inverter - 8 at 91.2%",
        "264658": "Sungrow SG125HV Inverter - 9 at 93.6%",
        "264659": "Sungrow SG125HV Inverter - 10 at 91.2%",
        "264660": "Sungrow SG125HV Inverter - 11 at 93.6%",
        "264661": "Sungrow SG125HV Inverter - 12 at 93.6%",
        "264662": "Sungrow SG125HV Inverter - 13 at 93.6%",
        "264663": "Sungrow SG125HV Inverter - 14 at 93.6%",
        "264664": "Sungrow SG125HV Inverter - 15 at 93.6%",
        "264665": "Sungrow SG125HV Inverter - 16 at 93.6%",
        "264666": "Sungrow SG125HV Inverter - 17 at 91.2%",
        "264667": "Sungrow SG125HV Inverter - 18 at 93.6%",
        "264668": "Sungrow SG125HV Inverter - 19 at 92.0%",
        "264669": "Sungrow SG125HV Inverter - 20 at 93.6%",
        "264670": "Sungrow SG125HV Inverter - 21 at 91.2%",
        "264671": "Sungrow SG125HV Inverter - 22 at 93.6%",
        "264672": "Sungrow SG125HV Inverter - 23 at 93.6%",
        "264673": "Sungrow SG125HV Inverter - 24 at 93.6%",
        "264674": "Sungrow SG125HV Inverter - 25 at 93.6%",
        "264675": "Sungrow SG125HV Inverter - 26 at 93.6%",
        "264676": "Sungrow SG125HV Inverter - 27 at 93.6%",
        "264677": "Sungrow SG125HV Inverter - 28 at 93.6%",
        "264678": "Sungrow SG125HV Inverter - 29 at 91.2%",
        "264679": "Sungrow SG125HV Inverter - 30 at 91.2%",
        "264680": "Sungrow SG125HV Inverter - 31 at 93.6%",
        "264682": "Sungrow SG125HV Inverter - 32 at 93.6%",
        "264683": "Sungrow SG125HV Inverter - 33 at 93.6%",
        "264684": "Sungrow SG125HV Inverter - 34 at 93.6%",
        "264685": "Sungrow SG125HV Inverter - 35 at 93.6%",
        "264686": "Sungrow SG125HV Inverter - 36 at 93.6%",
        "264687": "Sungrow SG125HV Inverter - 37 at 93.6%",
        "264688": "Sungrow SG125HV Inverter - 38 at 93.6%",
        "264689": "Sungrow SG125HV Inverter - 39 at 93.6%",
        "264690": "Sungrow SG125HV Inverter - 40 at 91.2%",
        "264691": "Sungrow SG125HV Inverter - 41 at 91.2%",
        "264692": "Sungrow SG125HV Inverter - 42 at 92.0%",
        "264693": "Sungrow SG125HV Inverter - 43 at 93.6%"
    },
    "weather_stations": {
        "264737": "Huksaflux SR-30 POA UP"
    }
},
"Hayes": {
    "breakers":{
        "298707": "SEL 751",
    },
    "meters":{
        "264628": "SEL 735 Meter",
    },
    "inverters": {
        "264696": "SunGrow SG125HV Inv - 1 at 92.0%",
        "264699": "SunGrow SG125HV Inv - 2 at 92.0%",
        "264700": "SunGrow SG125HV Inv - 3 at 92.0%",
        "264701": "SunGrow SG125HV Inv - 4 at 92.0%",
        "264702": "SunGrow SG125HV Inv - 5 at 92.0%",
        "264703": "SunGrow SG125HV Inv - 6 at 92.0%",
        "264704": "SunGrow SG125HV Inv - 7 at 92.0%",
        "264705": "SunGrow SG125HV Inv - 8 at 92.0%",
        "264706": "SunGrow SG125HV Inv - 9 at 92.0%",
        "264707": "SunGrow SG125HV Inv - 10 at 92.0%",
        "264708": "SunGrow SG125HV Inv - 11 at 92.0%",
        "264709": "SunGrow SG125HV Inv - 12 at 92.0%",
        "264710": "SunGrow SG125HV Inv - 13 at 92.0%",
        "264711": "SunGrow SG125HV Inv - 14 at 92.0%",
        "264712": "SunGrow SG125HV Inv - 15 at 92.0%",
        "264713": "SunGrow SG125HV Inv - 16 at 92.0%",
        "264714": "SunGrow SG125HV Inv - 17 at 92.0%",
        "264715": "SunGrow SG125HV Inv - 18 at 96.0%",
        "264716": "SunGrow SG125HV Inv - 19 at 92.0%",
        "264717": "SunGrow SG125HV Inv - 20 at 92.0%",
        "264718": "SunGrow SG125HV Inv - 21 at 92.0%",
        "264719": "SunGrow SG125HV Inv - 22 at 96.0%",
        "264720": "SunGrow SG125HV Inv - 23 at 92.0%",
        "264721": "SunGrow SG125HV Inv - 24 at 92.0%",
        "264723": "SunGrow SG125HV Inv - 25 at 92.0%",
        "264724": "SunGrow SG125HV Inv - 26 at 92.0%"
    },
    "weather_stations": {
        "264736": "Albedometer POA",
    },
},
"Van Buren": {
    "meters":{
        "263696": "SEL 735 Meter",
    },
    "inverters": {
    "263705": "Sungrow SG125kW Inverter - 1 at 93.6%",
    "263706": "Sungrow SG125kW Inverter - 2 at 93.6%",
    "263707": "Sungrow SG125kW Inverter - 3 at 93.6%",
    "263708": "Sungrow SG125kW Inverter - 4 at 93.6%",
    "263709": "Sungrow SG125kW Inverter - 5 at 93.6%",
    "263710": "Sungrow SG125kW Inverter - 6 at 93.6%",
    "263711": "Sungrow SG125kW Inverter - 7 at 94.4%",
    "263712": "Sungrow SG125kW Inverter - 8 at 94.4%",
    "263713": "Sungrow SG125kW Inverter - 9 at 94.4%",
    "263714": "Sungrow SG125kW Inverter - 10 at 94.4%",
    "263715": "Sungrow SG125kW Inverter - 11 at 94.4%",
    "263716": "Sungrow SG125kW Inverter - 12 at 94.4%",
    "263717": "Sungrow SG125kW Inverter - 13 at 94.4%",
    "263718": "Sungrow SG125kW Inverter - 14 at 94.4%",
    "263719": "Sungrow SG125kW Inverter - 15 at 94.4%",
    "263720": "Sungrow SG125kW Inverter - 16 at 94.4%",
    "263721": "Sungrow SG125kW Inverter - 17 at 94.4%"
    },
    "weather_stations": {
    "288847": "POA"
    },
},
"Warbler": {
    "breakers":{
        "298800": "SEL 751",
    },
    "meters":{
        "263553": "SEL 735 Meter",
    },
    "inverters": {
    "263557": "Sungrow SG125 Inverter A1 at 100%",
    "263558": "Sungrow SG125 Inverter A2 at 100%",
    "263559": "Sungrow SG125 Inverter A3 at 100%",
    "263560": "Sungrow SG125 Inverter A4 at 100%",
    "263561": "Sungrow SG125 Inverter A5 at 100%",
    "263562": "Sungrow SG125 Inverter A6 at 100%",
    "263563": "Sungrow SG125 Inverter A7 at 100%",
    "263564": "Sungrow SG125 Inverter A8 at 100%",
    "263565": "Sungrow SG125 Inverter A9 at 100%",
    "263566": "Sungrow SG125 Inverter A10 at 100%",
    "263567": "Sungrow SG125 Inverter A11 at 100%",
    "263568": "Sungrow SG125 Inverter A12 at 100%",
    "263569": "Sungrow SG125 Inverter A13 at 100%",
    "263570": "Sungrow SG125 Inverter A14 at 100%",
    "263571": "Sungrow SG125 Inverter A15 at 100%",
    "263572": "Sungrow SG125 Inverter A16 at 100%",
    "263573": "Sungrow SG125 Inverter B17 at 100%",
    "263574": "Sungrow SG125 Inverter B18 at 100%",
    "263575": "Sungrow SG125 Inverter B19 at 100%",
    "263576": "Sungrow SG125 Inverter B20 at 100%",
    "263577": "Sungrow SG125 Inverter B21 at 100%",
    "263578": "Sungrow SG125 Inverter B22 at 100%",
    "263579": "Sungrow SG125 Inverter B23 at 100%",
    "263580": "Sungrow SG125 Inverter B24 at 100%",
    "263581": "Sungrow SG125 Inverter B25 at 100%",
    "263582": "Sungrow SG125 Inverter B26 at 100%",
    "263583": "Sungrow SG125 Inverter B27 at 100%",
    "263584": "Sungrow SG125 Inverter B28 at 100%",
    "263585": "Sungrow SG125 Inverter B29 at 100%",
    "263586": "Sungrow SG125 Inverter B30 at 100%",
    "263587": "Sungrow SG125 Inverter B31 at 100%",
    "263588": "Sungrow SG125 Inverter B32 at 100%"
    },
    "weather_stations": {
    "263595": "Hukseflux SR30 POA"
    },
},
"Cardinal": {
    "breakers":{
        "298803": "SEL 751",
    },
    "meters":{
        "265438": "SEL 735 Meter",
    },
        "inverters": {
            "265452": "Sungrow SG 125kW - Inverter - 1 at 96%",
            "265453": "Sungrow SG 125kW - Inverter - 2 at 96%",
            "265454": "Sungrow SG 125kW - Inverter - 3 at 96%",
            "265455": "Sungrow SG 125kW - Inverter - 4 at 96%",
            "265456": "Sungrow SG 125kW - Inverter - 5 at 96%",
            "265457": "Sungrow SG 125kW - Inverter - 6 at 96%",
            "265458": "Sungrow SG 125kW - Inverter - 7 at 96%",
            "265459": "Sungrow SG 125kW - Inverter - 8 at 95.2%",
            "265460": "Sungrow SG 125kW - Inverter - 9 at 95.2%",
            "265461": "Sungrow SG 125kW - Inverter - 10 at 95.2%",
            "265462": "Sungrow SG 125kW - Inverter - 11 at 95.2%",
            "265463": "Sungrow SG 125kW - Inverter - 12 at 95.2%",
            "265464": "Sungrow SG 125kW - Inverter - 13 at 95.2%",
            "265465": "Sungrow SG 125kW - Inverter - 14 at 95.2%",
            "265466": "Sungrow SG 125kW - Inverter - 15 at 94.4%",
            "265467": "Sungrow SG 125kW - Inverter - 16 at 94.4%",
            "265468": "Sungrow SG 125kW - Inverter - 17 at 94.4%",
            "265469": "Sungrow SG 125kW - Inverter - 18 at 94.4%",
            "265470": "Sungrow SG 125kW - Inverter - 19 at 94.4%",
            "265471": "Sungrow SG 125kW - Inverter - 20 at 94.4%",
            "265472": "Sungrow SG 125kW - Inverter - 21 at 94.4%",
            "265476": "Sungrow SG 125kW - Inverter - 22 at 96%",
            "265477": "Sungrow SG 125kW - Inverter - 23 at 96%",
            "265478": "Sungrow SG 125kW - Inverter - 24 at 96%",
            "265479": "Sungrow SG 125kW - Inverter - 25 at 96%",
            "265480": "Sungrow SG 125kW - Inverter - 26 at 96%",
            "265481": "Sungrow SG 125kW - Inverter - 27 at 96%",
            "265482": "Sungrow SG 125kW - Inverter - 28 at 96%",
            "265483": "Sungrow SG 125kW - Inverter - 29 at 95.2%",
            "265484": "Sungrow SG 125kW - Inverter - 30 at 95.2%",
            "265485": "Sungrow SG 125kW - Inverter - 31 at 95.2%",
            "265486": "Sungrow SG 125kW - Inverter - 32 at 95.2%",
            "265487": "Sungrow SG 125kW - Inverter - 33 at 95.2%",
            "265488": "Sungrow SG 125kW - Inverter - 34 at 95.2%",
            "265489": "Sungrow SG 125kW - Inverter - 35 at 95.2%",
            "265490": "Sungrow SG 125kW - Inverter - 36 at 94.4%",
            "265491": "Sungrow SG 125kW - Inverter - 37 at 94.4%",
            "265492": "Sungrow SG 125kW - Inverter - 38 at 94.4%",
            "265493": "Sungrow SG 125kW - Inverter - 39 at 94.4%",
            "265494": "Sungrow SG 125kW - Inverter - 40 at 94.4%",
            "265495": "Sungrow SG 125kW - Inverter - 41 at 94.4%",
            "265496": "Sungrow SG 125kW - Inverter - 42 at 94.4%",
            "265497": "Sungrow SG 125kW - Inverter - 43 at 96%",
            "265498": "Sungrow SG 125kW - Inverter - 44 at 96%",
            "265499": "Sungrow SG 125kW - Inverter - 45 at 96%",
            "265500": "Sungrow SG 125kW - Inverter - 46 at 96%",
            "265501": "Sungrow SG 125kW - Inverter - 47 at 96%",
            "265502": "Sungrow SG 125kW - Inverter - 48 at 95.2%",
            "265503": "Sungrow SG 125kW - Inverter - 49 at 95.2%",
            "265504": "Sungrow SG 125kW - Inverter - 50 at 95.2%",
            "265505": "Sungrow SG 125kW - Inverter - 51 at 95.2%",
            "265506": "Sungrow SG 125kW - Inverter - 52 at 95.2%",
            "265507": "Sungrow SG 125kW - Inverter - 53 at 95.2%",
            "265508": "Sungrow SG 125kW - Inverter - 54 at 94.4%",
            "265509": "Sungrow SG 125kW - Inverter - 55 at 94.4%",
            "265510": "Sungrow SG 125kW - Inverter - 56 at 94.4%",
            "265511": "Sungrow SG 125kW - Inverter - 57 at 94.4%",
            "265512": "Sungrow SG 125kW - Inverter - 58 at 94.4%",
            "265513": "Sungrow SG 125kW - Inverter - 59 at 94.4%"
        },
        "weather_stations": {
            "265518": "Hukesflux SR30 POA",
        },
},
"Whitetail": {
    "breakers":{
        "312387": "SEL-751 Relay",
    },
    "meters":{
        "312384": "SEL 735 Meter",
    },
    "inverters": {
        "312388": "SunGrow SG125HV - Inverter 1",
        "312389": "SunGrow SG125HV - Inverter 2",
        "312390": "SunGrow SG125HV - Inverter 3",
        "312391": "SunGrow SG125HV - Inverter 4",
        "312392": "SunGrow SG125HV - Inverter 5",
        "312393": "SunGrow SG125HV - Inverter 6",
        "312394": "SunGrow SG125HV - Inverter 7",
        "312395": "SunGrow SG125HV - Inverter 8",
        "312396": "SunGrow SG125HV - Inverter 9",
        "312397": "SunGrow SG125HV - Inverter 10",
        "312398": "SunGrow SG125HV - Inverter 11",
        "312399": "SunGrow SG125HV - Inverter 12",
        "312400": "SunGrow SG125HV - Inverter 13",
        "312401": "SunGrow SG125HV - Inverter 14",
        "312402": "SunGrow SG125HV - Inverter 15",
        "312403": "SunGrow SG125HV - Inverter 16",
        "312404": "SunGrow SG125HV - Inverter 17",
        "312405": "SunGrow SG125HV - Inverter 18",
        "312406": "SunGrow SG125HV - Inverter 19",
        "312407": "SunGrow SG125HV - Inverter 20",
        "312408": "SunGrow SG125HV - Inverter 21",
        "312409": "SunGrow SG125HV - Inverter 22",
        "312410": "SunGrow SG125HV - Inverter 23",
        "312411": "SunGrow SG125HV - Inverter 24",
        "312412": "SunGrow SG125HV - Inverter 25",
        "312413": "SunGrow SG125HV - Inverter 26",
        "312414": "SunGrow SG125HV - Inverter 27",
        "312415": "SunGrow SG125HV - Inverter 28",
        "312416": "SunGrow SG125HV - Inverter 29",
        "312417": "SunGrow SG125HV - Inverter 30",
        "312418": "SunGrow SG125HV - Inverter 31",
        "312419": "SunGrow SG125HV - Inverter 32",
        "312420": "SunGrow SG125HV - Inverter 33",
        "312421": "SunGrow SG125HV - Inverter 34",
        "312422": "SunGrow SG125HV - Inverter 35",
        "312423": "SunGrow SG125HV - Inverter 36",
        "312424": "SunGrow SG125HV - Inverter 37",
        "312425": "SunGrow SG125HV - Inverter 38",
        "312426": "SunGrow SG125HV - Inverter 39",
        "312427": "SunGrow SG125HV - Inverter 40",
        "312428": "SunGrow SG125HV - Inverter 41",
        "312429": "SunGrow SG125HV - Inverter 42",
        "312430": "SunGrow SG125HV - Inverter 43",
        "312431": "SunGrow SG125HV - Inverter 44",
        "312432": "SunGrow SG125HV - Inverter 45",
        "312433": "SunGrow SG125HV - Inverter 46",
        "312434": "SunGrow SG125HV - Inverter 47",
        "312436": "SunGrow SG125HV - Inverter 48",
        "312437": "SunGrow SG125HV - Inverter 49",
        "312438": "SunGrow SG125HV - Inverter 50",
        "312439": "SunGrow SG125HV - Inverter 51",
        "312440": "SunGrow SG125HV - Inverter 52",
        "312441": "SunGrow SG125HV - Inverter 53",
        "312442": "SunGrow SG125HV - Inverter 54",
        "312443": "SunGrow SG125HV - Inverter 55",
        "312444": "SunGrow SG125HV - Inverter 56",
        "312445": "SunGrow SG125HV - Inverter 57",
        "312446": "SunGrow SG125HV - Inverter 58",
        "312447": "SunGrow SG125HV - Inverter 59",
        "312448": "SunGrow SG125HV - Inverter 60",
        "312449": "SunGrow SG125HV - Inverter 61",
        "312450": "SunGrow SG125HV - Inverter 62",
        "312451": "SunGrow SG125HV - Inverter 63",
        "312452": "SunGrow SG125HV - Inverter 64",
        "312453": "SunGrow SG125HV - Inverter 65",
        "312454": "SunGrow SG125HV - Inverter 66",
        "312455": "SunGrow SG125HV - Inverter 67",
        "312456": "SunGrow SG125HV - Inverter 68",
        "312457": "SunGrow SG125HV - Inverter 69",
        "312458": "SunGrow SG125HV - Inverter 70",
        "312459": "SunGrow SG125HV - Inverter 71",
        "312460": "SunGrow SG125HV - Inverter 72",
        "312461": "SunGrow SG125HV - Inverter 73",
        "312462": "SunGrow SG125HV - Inverter 74",
        "312463": "SunGrow SG125HV - Inverter 75",
        "312464": "SunGrow SG125HV - Inverter 76",
        "312465": "SunGrow SG125HV - Inverter 77",
        "312466": "SunGrow SG125HV - Inverter 78",
        "312467": "SunGrow SG125HV - Inverter 79",
        "312468": "SunGrow SG125HV - Inverter 80"
    },
    "weather_stations": {
        "312487": "Hukseflux SR-30 - POA",
    },
},
"Marshall":{
    "breakers":{
        "331551": "SEL 751 Recloser",
    },
    "meters":{
        "331544": "SEL 735 Meter",
    },
        "inverters": {
        "331515": "A1.1",
        "331516": "A1.2",
        "331517": "A1.3",
        "331518": "A1.4",
        "331519": "A1.5",
        "331520": "A1.6",
        "331521": "A1.7",
        "331522": "A1.8",
        "331523": "A1.9",
        "331524": "A1.10",
        "331525": "A1.11",
        "331526": "A1.12",
        "331527": "A1.13",
        "331528": "A1.14",
        "331529": "A1.15",
        "331530": "A1.16"
    },
    "weather_stations": {
        "331604": "Hukseflux SR05 POA"
    },
},
"Tedder": {
    "breakers":{
        "332251": "SEL-751 Recloser",
    },
    "meters":{
        "332249": "SEL 735 Meter",
    },
    "inverters": {
        "332252": "Sungrow SG125HV Inverter - 1",
        "332253": "Sungrow SG125HV Inverter - 2",
        "332254": "Sungrow SG125HV Inverter - 3",
        "332255": "Sungrow SG125HV Inverter - 4",
        "332256": "Sungrow SG125HV Inverter - 5",
        "332257": "Sungrow SG125HV Inverter - 6",
        "332258": "Sungrow SG125HV Inverter - 7",
        "332259": "Sungrow SG125HV Inverter - 8",
        "332260": "Sungrow SG125HV Inverter - 9",
        "332261": "Sungrow SG125HV Inverter - 10",
        "332262": "Sungrow SG125HV Inverter - 11",
        "332263": "Sungrow SG125HV Inverter - 12",
        "332264": "Sungrow SG125HV Inverter - 13",
        "332265": "Sungrow SG125HV Inverter - 14",
        "332266": "Sungrow SG125HV Inverter - 15",
        "332267": "Sungrow SG125HV Inverter - 16"
    },
    "weather_stations": {
        "332296": "Hukseflux SR05 - POA",
    },
},
"Thunderhead": {
    "breakers":{
        "331793": "SEL-751 Recloser",
    },
    "meters":{
        "331784": "SEL 735 Meter",
    },
    "inverters": {
        "331811": "SUNGROW SG125HV Inverter-1",
        "331812": "SUNGROW SG125HV Inverter-2",
        "331813": "SUNGROW SG125HV Inverter-3",
        "331814": "SUNGROW SG125HV Inverter-4",
        "331815": "SUNGROW SG125HV Inverter-5",
        "331816": "SUNGROW SG125HV Inverter-6",
        "331817": "SUNGROW SG125HV Inverter-7",
        "331818": "SUNGROW SG125HV Inverter-8",
        "331819": "SUNGROW SG125HV Inverter-9",
        "331820": "SUNGROW SG125HV Inverter-10",
        "331821": "SUNGROW SG125HV Inverter-11",
        "331822": "SUNGROW SG125HV Inverter-12",
        "331823": "SUNGROW SG125HV Inverter-13",
        "331824": "SUNGROW SG125HV Inverter-14",
        "331825": "SUNGROW SG125HV Inverter-15",
        "331826": "SUNGROW SG125HV Inverter-16"
    },
    "weather_stations": {
        "331840": "Hukseflux SR05 (POA)",
    },
},
"Ogburn": {
    "breakers":{
        "379034": "SEL 851 Relay",
    },
    "meters":{
        "379033": "SEL 735 Meter",
    },
    "inverters": {
        "379044": "Inverter 1-1",
        "379045": "Inverter 1-2",
        "379046": "Inverter 1-3",
        "379047": "Inverter 1-4",
        "379048": "Inverter 1-5",
        "379049": "Inverter 1-6",
        "379050": "Inverter 1-7",
        "379051": "Inverter 1-8",
        "379052": "Inverter 1-9",
        "379053": "Inverter 1-10",
        "379054": "Inverter 1-11",
        "379055": "Inverter 1-12",
        "379056": "Inverter 1-13",
        "379057": "Inverter 1-14",
        "379058": "Inverter 1-15",
        "379059": "Inverter 1-16"
    },
    "weather_stations": {
        "379061": "Hukseflux SR05 (POA)",
    },
},
"Jefferson": {
    "breakers":{
        "381772": "SEL-851 Relay",
    },
    "meters":{
        "381281": "SEL 735 Meter",
    },
    "inverters": {
        "381284": "Inverter A1.1",
        "381285": "Inverter A1.2",
        "381286": "Inverter A1.3",
        "381287": "Inverter A1.4",
        "381288": "Inverter A1.5",
        "381289": "Inverter A1.6",
        "381290": "Inverter A1.7",
        "381291": "Inverter A1.8",
        "381292": "Inverter A1.9",
        "381293": "Inverter A1.10",
        "381294": "Inverter A1.11",
        "381295": "Inverter A1.12",
        "381296": "Inverter A1.13",
        "381297": "Inverter A1.14",
        "381298": "Inverter A1.15",
        "381299": "Inverter A1.16",
        "381300": "Inverter A2.1",
        "381301": "Inverter A2.2",
        "381302": "Inverter A2.3",
        "381303": "Inverter A2.4",
        "381304": "Inverter A2.5",
        "381305": "Inverter A2.6",
        "381306": "Inverter A2.7",
        "381307": "Inverter A2.8",
        "381308": "Inverter A2.9",
        "381309": "Inverter A2.10",
        "381310": "Inverter A2.11",
        "381311": "Inverter A2.12",
        "381312": "Inverter A2.13",
        "381313": "Inverter A2.14",
        "381314": "Inverter A2.15",
        "381315": "Inverter A2.16",
        "381316": "Inverter A3.1",
        "381317": "Inverter A3.2",
        "381318": "Inverter A3.3",
        "381319": "Inverter A3.4",
        "381320": "Inverter A3.5",
        "381321": "Inverter A3.6",
        "381322": "Inverter A3.7",
        "381323": "Inverter A3.8",
        "381324": "Inverter A3.9",
        "381325": "Inverter A3.10",
        "381326": "Inverter A3.11",
        "381327": "Inverter A3.12",
        "381328": "Inverter A3.13",
        "381329": "Inverter A3.14",
        "381330": "Inverter A3.15",
        "381331": "Inverter A3.16",
        "381332": "Inverter A4.1",
        "381333": "Inverter A4.2",
        "381334": "Inverter A4.3",
        "381335": "Inverter A4.4",
        "381336": "Inverter A4.5",
        "381337": "Inverter A4.6",
        "381338": "Inverter A4.7",
        "381339": "Inverter A4.8",
        "381340": "Inverter A4.9",
        "381341": "Inverter A4.10",
        "381342": "Inverter A4.11",
        "381343": "Inverter A4.12",
        "381344": "Inverter A4.13",
        "381345": "Inverter A4.14",
        "381346": "Inverter A4.15",
        "381347": "Inverter A4.16"
    },
    "weather_stations": {
        "381352": "Hukseflux SR05 - POA"
    },
},
"Bishopville II": {
    "breakers":{
        "383455": "SEL 851 Relay",
    },
    "meters":{
        "383452": "SEL 735 Meter",
    },
    "inverters": {
        "383456": "Inverter 1-1",
        "383457": "Inverter 1-2",
        "383458": "Inverter 1-3",
        "383459": "Inverter 1-4",
        "383460": "Inverter 1-5",
        "383461": "Inverter 1-6",
        "383462": "Inverter 1-7",
        "383463": "Inverter 1-8",
        "383464": "Inverter 1-9",
        "383465": "Inverter 2-1",
        "383466": "Inverter 2-2",
        "383467": "Inverter 2-3",
        "383468": "Inverter 2-4",
        "383469": "Inverter 2-5",
        "383470": "Inverter 2-6",
        "383471": "Inverter 2-7",
        "383472": "Inverter 2-8",
        "383473": "Inverter 2-9",
        "383474": "Inverter 3-1",
        "383475": "Inverter 3-2",
        "383476": "Inverter 3-3",
        "383477": "Inverter 3-4",
        "383478": "Inverter 3-5",
        "383479": "Inverter 3-6",
        "383480": "Inverter 3-7",
        "383481": "Inverter 3-8",
        "383482": "Inverter 3-9",
        "383483": "Inverter 4-1",
        "383484": "Inverter 4-2",
        "383485": "Inverter 4-3",
        "383486": "Inverter 4-4",
        "383487": "Inverter 4-5",
        "383488": "Inverter 4-6",
        "383489": "Inverter 4-7",
        "383490": "Inverter 4-8",
        "383491": "Inverter 4-9",
    },
    "weather_stations": {
        "508125": "Hukseflux SR30 - POA (PY0)",
    }
},
"Bulloch 1B": {
    "meters":{
        "399336": "SEL 735 Meter",
    },
        "inverters": {
            "399338": "Inverter 1",
            "399339": "Inverter 2",
            "399340": "Inverter 3",
            "399341": "Inverter 4",
            "399342": "Inverter 5",
            "399343": "Inverter 6",
            "399344": "Inverter 7",
            "399345": "Inverter 8",
            "399346": "Inverter 9",
            "399347": "Inverter 10",
            "399348": "Inverter 11",
            "399349": "Inverter 12",
            "399350": "Inverter 13",
            "399351": "Inverter 14",
            "399352": "Inverter 15",
            "399353": "Inverter 16",
            "399354": "Inverter 17",
            "399355": "Inverter 18",
            "399356": "Inverter 19",
            "399357": "Inverter 20",
            "399358": "Inverter 21",
            "399359": "Inverter 22",
            "399360": "Inverter 23",
            "399361": "Inverter 24"
        },
        "weather_stations": {
            "399363": "Kipp & Zonen SMP-12 (POA) - PY0"
        },
},
"Bulloch 1A": {
    "meters":{
        "400652": "SEL 735 Meter",
    },
        "inverters": {
            "400665": "Inverter 1",
            "400666": "Inverter 2",
            "400667": "Inverter 3",
            "400668": "Inverter 4",
            "400669": "Inverter 5",
            "400670": "Inverter 6",
            "400671": "Inverter 7",
            "400672": "Inverter 8",
            "400673": "Inverter 9",
            "400674": "Inverter 10",
            "400675": "Inverter 11",
            "400676": "Inverter 12",
            "400653": "Inverter 13",
            "400654": "Inverter 14",
            "400655": "Inverter 15",
            "400656": "Inverter 16",
            "400657": "Inverter 17",
            "400658": "Inverter 18",
            "400659": "Inverter 19",
            "400660": "Inverter 20",
            "400661": "Inverter 21",
            "400662": "Inverter 22",
            "400663": "Inverter 23",
            "400664": "Inverter 24"
        },
        "weather_stations": {
            "400677": "Kipp & Zonen SMP-12 (POA) - PY0 (RMA14237)"
        },
},
"Richmond": {
    "meters":{
        "400977": "SEL 735 Meter",
    },
    "inverters": {
        "400978": "Inverter 1",
        "400979": "Inverter 2",
        "400980": "Inverter 3",
        "400981": "Inverter 4",
        "400982": "Inverter 5",
        "400983": "Inverter 6",
        "400984": "Inverter 7",
        "400985": "Inverter 8",
        "400986": "Inverter 9",
        "400987": "Inverter 10",
        "400988": "Inverter 11",
        "400989": "Inverter 12",
        "400990": "Inverter 13",
        "400991": "Inverter 14",
        "400992": "Inverter 15",
        "400993": "Inverter 16",
        "400994": "Inverter 17",
        "400995": "Inverter 18",
        "400996": "Inverter 19",
        "400997": "Inverter 20",
        "400998": "Inverter 21",
        "400999": "Inverter 22",
        "401000": "Inverter 23",
        "401001": "Inverter 24"
    },
    "weather_stations": {
        "401004": "Kipp & Zonen SMP-12 (POA) - PY0"
    },
},
"Upson": {
    "meters":{
        "401051": "SEL 735 Meter",
    },
    "inverters": {
        "401052": "Inverter 1 - 11 String Inverter",
        "401053": "Inverter 2 - 11 String Inverter",
        "401054": "Inverter 3 - 11 String Inverter",
        "401055": "Inverter 4 - 11 String Inverter",
        "401056": "Inverter 5 - 11 String Inverter",
        "401057": "Inverter 6 - 10 String Inverter",
        "401058": "Inverter 7 - 10 String Inverter",
        "401059": "Inverter 8 - 10 String Inverter",
        "401060": "Inverter 9 - 11 String Inverter",
        "401061": "Inverter 10 - 11 String Inverter",
        "401062": "Inverter 11 - 11 String Inverter",
        "401063": "Inverter 12 - 11 String Inverter",
        "401064": "Inverter 13 - 11 String Inverter",
        "401065": "Inverter 14 - 11 String Inverter",
        "401066": "Inverter 15 - 11 String Inverter",
        "401067": "Inverter 16 - 11 String Inverter",
        "401068": "Inverter 17 - 11 String Inverter",
        "401069": "Inverter 18 - 10 String Inverter",
        "401070": "Inverter 19 - 10 String Inverter",
        "401071": "Inverter 20 - 10 String Inverter",
        "401072": "Inverter 21 - 11 String Inverter",
        "401073": "Inverter 22 - 11 String Inverter",
        "401074": "Inverter 23 - 11 String Inverter",
        "401075": "Inverter 24 - 11 String Inverter"
    },
    "weather_stations": {
        "401080": "Kipp & Zonen SMP-12 (POA) - PY0"
    },
},
"McLean": {
    "breakers":{
        "421812": "RELAY",
    },
    "meters":{
        "421811": "SEL 735 Meter",
    },
    "inverters": {
        "421813": "INVERTER 1",
        "421814": "INVERTER 2",
        "421815": "INVERTER 3",
        "421816": "INVERTER 4",
        "421817": "INVERTER 5",
        "421818": "INVERTER 6",
        "421819": "INVERTER 7",
        "421820": "INVERTER 8",
        "421821": "INVERTER 9",
        "421822": "INVERTER 10",
        "421823": "INVERTER 11",
        "421824": "INVERTER 12",
        "421825": "INVERTER 13",
        "421826": "INVERTER 14",
        "421827": "INVERTER 15",
        "421828": "INVERTER 16",
        "421829": "INVERTER 17",
        "421830": "INVERTER 18",
        "421831": "INVERTER 19",
        "421832": "INVERTER 20",
        "421833": "INVERTER 21",
        "421834": "INVERTER 22",
        "421835": "INVERTER 23",
        "421836": "INVERTER 24",
        "421837": "INVERTER 25",
        "421838": "INVERTER 26",
        "421839": "INVERTER 27",
        "421840": "INVERTER 28",
        "421841": "INVERTER 29",
        "421842": "INVERTER 30",
        "421843": "INVERTER 31",
        "421844": "INVERTER 32",
        "421845": "INVERTER 33",
        "421846": "INVERTER 34",
        "421847": "INVERTER 35",
        "421848": "INVERTER 36",
        "421849": "INVERTER 37",
        "421850": "INVERTER 38",
        "421851": "INVERTER 39",
        "421852": "INVERTER 40"
    },
    "weather_stations": {
        "421854": "PYRANOMETER - POA (PY1) (SO84054)"
    },
},
"Shorthorn": {
    "breakers":{
        "422065": "RELAY",
    },
    "meters":{
        "422064": "SEL 735 Meter",
    },
    "inverters": {
        "422066": "INVERTER 1",
        "422067": "INVERTER 2",
        "422068": "INVERTER 3",
        "422069": "INVERTER 4",
        "422070": "INVERTER 5",
        "422071": "INVERTER 6",
        "422072": "INVERTER 7",
        "422073": "INVERTER 8",
        "422074": "INVERTER 9",
        "422075": "INVERTER 10",
        "422076": "INVERTER 11",
        "422077": "INVERTER 12",
        "422078": "INVERTER 13",
        "422079": "INVERTER 14",
        "422080": "INVERTER 15",
        "422081": "INVERTER 16",
        "422082": "INVERTER 17",
        "422083": "INVERTER 18",
        "422084": "INVERTER 19",
        "422085": "INVERTER 20",
        "422086": "INVERTER 21",
        "422087": "INVERTER 22",
        "422088": "INVERTER 23",
        "422089": "INVERTER 24",
        "422090": "INVERTER 25",
        "422091": "INVERTER 26",
        "422092": "INVERTER 27",
        "422093": "INVERTER 28",
        "422094": "INVERTER 29",
        "422095": "INVERTER 30",
        "422096": "INVERTER 31",
        "422097": "INVERTER 32",
        "422098": "INVERTER 33",
        "422099": "INVERTER 34",
        "422100": "INVERTER 35",
        "422101": "INVERTER 36",
        "422102": "INVERTER 37",
        "422103": "INVERTER 38",
        "422104": "INVERTER 39",
        "422105": "INVERTER 40",
        "422106": "INVERTER 41",
        "422107": "INVERTER 42",
        "422108": "INVERTER 43",
        "422109": "INVERTER 44",
        "422110": "INVERTER 45",
        "422111": "INVERTER 46",
        "422112": "INVERTER 47",
        "422113": "INVERTER 48",
        "422114": "INVERTER 49",
        "422115": "INVERTER 50",
        "422116": "INVERTER 51",
        "422117": "INVERTER 52",
        "422118": "INVERTER 53",
        "422119": "INVERTER 54",
        "422120": "INVERTER 55",
        "422121": "INVERTER 56",
        "422122": "INVERTER 57",
        "422123": "INVERTER 58",
        "422124": "INVERTER 59",
        "422125": "INVERTER 60",
        "422126": "INVERTER 61",
        "422127": "INVERTER 62",
        "422128": "INVERTER 63",
        "422129": "INVERTER 64",
        "422130": "INVERTER 65",
        "422131": "INVERTER 66",
        "422132": "INVERTER 67",
        "422133": "INVERTER 68",
        "422134": "INVERTER 69",
        "422135": "INVERTER 70",
        "422136": "INVERTER 71",
        "422137": "INVERTER 72"
    },
    "weather_stations": {
        "422139": "PYRANOMETER - POA"
    },
},
"Washington": {
    "breakers":{
        "457101": "RELAY",
    },
    "meters":{
        "457100": "SEL 735 Meter",
    },
    "inverters": {
        "457102": "INVERTER 1",
        "457103": "INVERTER 2",
        "457104": "INVERTER 3",
        "457105": "INVERTER 4",
        "457106": "INVERTER 5",
        "457107": "INVERTER 6",
        "457108": "INVERTER 7",
        "457109": "INVERTER 8",
        "457110": "INVERTER 9",
        "457111": "INVERTER 10",
        "457112": "INVERTER 11",
        "457113": "INVERTER 12",
        "457114": "INVERTER 13",
        "457115": "INVERTER 14",
        "457116": "INVERTER 15",
        "457117": "INVERTER 16",
        "457118": "INVERTER 17",
        "457119": "INVERTER 18",
        "457120": "INVERTER 19",
        "457121": "INVERTER 20",
        "457122": "INVERTER 21",
        "457123": "INVERTER 22",
        "457124": "INVERTER 23",
        "457125": "INVERTER 24",
        "457126": "INVERTER 25",
        "457127": "INVERTER 26",
        "457128": "INVERTER 27",
        "457129": "INVERTER 28",
        "457130": "INVERTER 29",
        "457131": "INVERTER 30",
        "457132": "INVERTER 31",
        "457133": "INVERTER 32",
        "457134": "INVERTER 33",
        "457135": "INVERTER 34",
        "457136": "INVERTER 35",
        "457137": "INVERTER 36",
        "457138": "INVERTER 37",
        "457139": "INVERTER 38",
        "457140": "INVERTER 39",
        "457141": "INVERTER 40"
    },
    "weather_stations": {
        "457144": "PYRANOMETER - POA"
    },

},
"Harding": {
    "breakers":{
        "462598": "RELAY",
    },
    "meters":{
        "462597": "SEL 735 Meter",
    },
    "inverters": {
        "462599": "INVERTER 1",
        "462600": "INVERTER 2",
        "462601": "INVERTER 3",
        "462602": "INVERTER 4",
        "462603": "INVERTER 5",
        "462604": "INVERTER 6",
        "462605": "INVERTER 7",
        "462606": "INVERTER 8",
        "462607": "INVERTER 9",
        "462608": "INVERTER 10",
        "462609": "INVERTER 11",
        "462610": "INVERTER 12",
        "462611": "INVERTER 13",
        "462612": "INVERTER 14",
        "462613": "INVERTER 15",
        "462614": "INVERTER 16",
        "462615": "INVERTER 17",
        "462616": "INVERTER 18",
        "462617": "INVERTER 19",
        "462618": "INVERTER 20",
        "462619": "INVERTER 21",
        "462620": "INVERTER 22",
        "462621": "INVERTER 23",
        "462622": "INVERTER 24"
    },
    "weather_stations": {
        "462625": "PYRANOMETER - POA"
    },
},
"Whitehall": {
    "breakers":{
        "463298": "RELAY",
    },
    "meters":{
        "463297": "SEL 735 Meter",
    },
    "inverters": {
        "463299": "INVERTER 1",
        "463300": "INVERTER 2",
        "463301": "INVERTER 3",
        "463302": "INVERTER 4",
        "463303": "INVERTER 5",
        "463304": "INVERTER 6",
        "463305": "INVERTER 7",
        "463306": "INVERTER 8",
        "463307": "INVERTER 9",
        "463308": "INVERTER 10",
        "463309": "INVERTER 11",
        "463310": "INVERTER 12",
        "463311": "INVERTER 13",
        "463312": "INVERTER 14",
        "463313": "INVERTER 15",
        "463314": "INVERTER 16"
    },
    "weather_stations": {
        "463317": "PYRANOMETER - POA"
    },
},
"Sunflower": {
    "breakers":{
        "458506": "RELAY",
    },
    "meters":{
        "458505": "SEL 735 Meter",
    },
    "inverters": {
        "458507": "INVERTER 1",
        "458508": "INVERTER 2",
        "458509": "INVERTER 3",
        "458510": "INVERTER 4",
        "458511": "INVERTER 5",
        "458512": "INVERTER 6",
        "458513": "INVERTER 7",
        "458514": "INVERTER 8",
        "458515": "INVERTER 9",
        "458516": "INVERTER 10",
        "458517": "INVERTER 11",
        "458518": "INVERTER 12",
        "458519": "INVERTER 13",
        "458520": "INVERTER 14",
        "458521": "INVERTER 15",
        "458522": "INVERTER 16",
        "458523": "INVERTER 17",
        "458524": "INVERTER 18",
        "458525": "INVERTER 19",
        "458526": "INVERTER 20",
        "458527": "INVERTER 21",
        "458528": "INVERTER 22",
        "458529": "INVERTER 23",
        "458530": "INVERTER 24",
        "458531": "INVERTER 25",
        "458532": "INVERTER 26",
        "458533": "INVERTER 27",
        "458534": "INVERTER 28",
        "458535": "INVERTER 29",
        "458536": "INVERTER 30",
        "458537": "INVERTER 31",
        "458538": "INVERTER 32",
        "458539": "INVERTER 33",
        "458540": "INVERTER 34",
        "458541": "INVERTER 35",
        "458542": "INVERTER 36",
        "458543": "INVERTER 37",
        "458544": "INVERTER 38",
        "458545": "INVERTER 39",
        "458546": "INVERTER 40",
        "458547": "INVERTER 41",
        "458548": "INVERTER 42",
        "458549": "INVERTER 43",
        "458550": "INVERTER 44",
        "458551": "INVERTER 45",
        "458552": "INVERTER 46",
        "458553": "INVERTER 47",
        "458554": "INVERTER 48",
        "458555": "INVERTER 49",
        "458556": "INVERTER 50",
        "458557": "INVERTER 51",
        "458558": "INVERTER 52",
        "458559": "INVERTER 53",
        "458560": "INVERTER 54",
        "458561": "INVERTER 55",
        "458562": "INVERTER 56",
        "458563": "INVERTER 57",
        "458564": "INVERTER 58",
        "458565": "INVERTER 59",
        "458566": "INVERTER 60",
        "458567": "INVERTER 61",
        "458568": "INVERTER 62",
        "458569": "INVERTER 63",
        "458570": "INVERTER 64",
        "458571": "INVERTER 65",
        "458572": "INVERTER 66",
        "458573": "INVERTER 67",
        "458574": "INVERTER 68",
        "458575": "INVERTER 69",
        "458576": "INVERTER 70",
        "458577": "INVERTER 71",
        "458578": "INVERTER 72",
        "458579": "INVERTER 73",
        "458580": "INVERTER 74",
        "458581": "INVERTER 75",
        "458582": "INVERTER 76",
        "458583": "INVERTER 77",
        "458584": "INVERTER 78",
        "458585": "INVERTER 79",
        "458586": "INVERTER 80"
    },
    "weather_stations": {
        "458588": "PYRANOMETER - POA (PY1)"
    },
},
"Gray Fox": {
    "breakers":{
        "458187": "RELAY",
    },
    "meters":{
        "458186": "SEL 735 Meter",
    },
    "inverters": {
        "458188": "INVERTER 1.1",
        "458189": "INVERTER 1.2",
        "458190": "INVERTER 1.3",
        "458191": "INVERTER 1.4",
        "458192": "INVERTER 1.5",
        "458193": "INVERTER 1.6",
        "458194": "INVERTER 1.7",
        "458195": "INVERTER 1.8",
        "458196": "INVERTER 1.9",
        "458197": "INVERTER 1.10",
        "458198": "INVERTER 1.11",
        "458199": "INVERTER 1.12",
        "458200": "INVERTER 1.13",
        "458201": "INVERTER 1.14",
        "458202": "INVERTER 1.15",
        "458203": "INVERTER 1.16",
        "458204": "INVERTER 1.17",
        "458205": "INVERTER 1.18",
        "458206": "INVERTER 1.19",
        "458207": "INVERTER 1.20",
        "458208": "INVERTER 2.1",
        "458209": "INVERTER 2.2",
        "458210": "INVERTER 2.3",
        "458211": "INVERTER 2.4",
        "458212": "INVERTER 2.5",
        "458213": "INVERTER 2.6",
        "458214": "INVERTER 2.7",
        "458215": "INVERTER 2.8",
        "458216": "INVERTER 2.9",
        "458217": "INVERTER 2.10",
        "458218": "INVERTER 2.11",
        "458219": "INVERTER 2.12",
        "458220": "INVERTER 2.13",
        "458221": "INVERTER 2.14",
        "458222": "INVERTER 2.15",
        "458223": "INVERTER 2.16",
        "458224": "INVERTER 2.17",
        "458225": "INVERTER 2.18",
        "458226": "INVERTER 2.19",
        "458227": "INVERTER 2.20"
    },
    "weather_stations": {
        "458230": "PYRANOMETER - POA"
    },
},
"Hickson": {
    "breakers":{
        "380570": "Sel 851 Relay",
    },
    "meters":{
        "380569": "SEL 735 Meter",
    },
        "inverters": {
            "380571": "Inverter 1-1",
            "380572": "Inverter 1-2",
            "380573": "Inverter 1-3",
            "380574": "Inverter 1-4",
            "380575": "Inverter 1-5",
            "380576": "Inverter 1-6",
            "380577": "Inverter 1-7",
            "380578": "Inverter 1-8",
            "380579": "Inverter 1-9",
            "380580": "Inverter 1-10",
            "380581": "Inverter 1-11",
            "380582": "Inverter 1-12",
            "380583": "Inverter 1-13",
            "380584": "Inverter 1-14",
            "380585": "Inverter 1-15",
            "380586": "Inverter 1-16"
        },
        "weather_stations": {
            "380588": "Hukseflux SR05 (POA)"
        },
    },
"Elk": {
    "breakers":{
        "498893": "Sel 751 Relay",
    },
    "meters":{
        "498894": "SEL 735 Meter",
    },
        "inverters": {
            "499734": "Inverter - 1",
            "499735": "Inverter - 2",
            "499736": "Inverter - 3",
            "499737": "Inverter - 4",
            "499738": "Inverter - 5",
            "499739": "Inverter - 6",
            "499740": "Inverter - 7",
            "499741": "Inverter - 8",
            "499742": "Inverter - 9",
            "499743": "Inverter - 10",
            "499744": "Inverter - 11",
            "499745": "Inverter - 12",
            "499746": "Inverter - 13",
            "499747": "Inverter - 14",
            "499748": "Inverter - 15",
            "499749": "Inverter - 16",
            "499750": "Inverter - 17",
            "499751": "Inverter - 18",
            "499752": "Inverter - 19",
            "499753": "Inverter - 20",
            "499754": "Inverter - 21",
            "499755": "Inverter - 22",
            "499756": "Inverter - 23",
            "499757": "Inverter - 24",
            "499758": "Inverter - 25",
            "499759": "Inverter - 26",
            "499760": "Inverter - 27",
            "499761": "Inverter - 28",
            "499762": "Inverter - 29",
            "499763": "Inverter - 30",
            "499764": "Inverter - 31",
            "499765": "Inverter - 32",
            "499766": "Inverter - 33",
            "499767": "Inverter - 34",
            "499768": "Inverter - 35",
            "499769": "Inverter - 36",
            "499770": "Inverter - 37",
            "499771": "Inverter - 38",
            "499772": "Inverter - 39",
            "499773": "Inverter - 40",
            "499774": "Inverter - 41",
            "499775": "Inverter - 42",
            "499776": "Inverter - 43"
        },
        "weather_stations": {
            "498892": "Weather Station"
        },
    },
}




def check_fail_loop(auth_file):
        auth_file.seek(0)
        txt = auth_file.read().strip()
        print(txt)  # Read once and store the content
        count = int(txt) - 1
        return count
def reset_count(auth_file):
        auth_file.seek(0)
        auth_file.write("1")
        auth_file.truncate()
def counting_fails(auth_file):
        auth_file.seek(0)
        content = auth_file.read().strip()  # Read once and store the content
        current_value = int(content)
        new_value = current_value + 1

        # Write incremented value back to file
        auth_file.seek(0)
        auth_file.write(str(new_value))
        auth_file.truncate()
        return new_value

# Make the POST request to obtain an access token
def get_access_token():
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'password',
        'username': email,
        'password': password,
    }
    access_token_url = base_url + token_endpoint
    response = requests.post(access_token_url, headers=headers, data=data, verify=False) #I know that I shouldn't set verify to false for security reasons. But the Code worked flawlessly for over a year being set to True by Default and this was the only thing out of 10 things I tried that worked. 🤷‍♂️ Adivce is welcomed to joseph.lang@narenco.com. If you message me, please include 'Found on GitHub, looking to help', so that I know it's not spam.
    return response

# Function to make API request with authentication
def make_api_request(get_hardware_url, access_token):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    headers['Authorization'] = f"Bearer {access_token}"
    return requests.get(get_hardware_url, headers=headers, verify=False) #I know that I shouldn't set verify to false for security reasons. But the Code worked flawlessly for over a year being set to True by Default and this was the only thing out of 10 things I tried that worked. 🤷‍♂️ Adivce is welcomed to joseph.lang@narenco.com. If you message me, please include 'Found on GitHub, looking to help', so that I know it's not spam.

#Testing Status Code if statements
class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code

    def json(self):
        # Return a dummy JSON response if needed
        return {}

def get_data_for_site(site, site_data, api_data, hw_sites_mapping, start, base_url, access_token):
    troubleshooting_file = r"C:\Users\omops\Documents\Automations\Troubleshooting.txt"

    global category, hardware_data, hardware_id, hdname
    
    current = time.perf_counter()
    #print("Start Processing:", site, round(current-start, 2))
    for category, hardware_data in site_data.items():
        for hardware_id, hdname in hardware_data.items():
            get_hardware_url = f"{base_url}/Hardware/{hardware_id}"
            hardware_response = make_api_request(get_hardware_url, access_token)

            if hardware_response.status_code == 200:
                register_values = {}
                hardware_data_response = hardware_response.json()
                #with open(troubleshooting_file, "a") as tbfile: 
                #    json.dump(hardware_data_response, tbfile, indent=2)

                hdtimestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


                # AE Register Names
                breaker_register_names = ['Status', 'Breaker Open/Closed', 'Status Closed']
                inverterKW_register_names = ['Grid power', 'Line kW', 'AC Real Power', '3phase Power', 'Active Power', 'Total Active Power', 'Pac', 'AC Power']
                inverterDC_register_names = ['DC Power Total', 'DC Voltage1', 'DC Input Voltage', 'DC voltage (average)', 'DC Voltage Average', 'Bus Voltage', 'Total DC Power', 'DC Voltage', 'Input Voltage', 'Vpv']
                amps_a_register_names = ['Phase current, A', 'AC Current A', 'Current A', 'Amps A', 'AC Phase A Current']
                amps_b_register_names = ['Phase current, B', 'AC Current B', 'Current B', 'Amps B', 'AC Phase B Current']
                amps_c_register_names = ['Phase current, C', 'AC Current C', 'Current C', 'Amps C', 'AC Phase C Current']

                volts_a_register_names = ['Volts A-N', 'Volts A', 'AC Voltage A', 'Voltage AN', 'AC Voltage A (Line-Neutral)', 'Voltage, A-N', 'AC Phase A Voltage', 'AC Voltage AN']
                volts_b_register_names = ['Volts B-N', 'Volts B', 'AC Voltage B', 'Voltage BN', 'AC Voltage B (Line-Neutral)', 'Voltage, B-N', 'AC Phase B Voltage', 'AC Voltage BN']
                volts_c_register_names = ['Volts C-N', 'Volts C', 'AC Voltage C', 'Voltage CN', 'AC Voltage C (Line-Neutral)', 'Voltage, C-N', 'AC Phase C Voltage', 'AC Voltage CN']
                meterkw_register_names = ['Active Power', 'Real power', 'Real Power', 'Total power']    #Real Power is probably not used but lowercase power is.            
                
                weather_station_register_names = ['POA Irradiance', 'Plane of Array Irradiance',  'GHI Irradiance', 'Sun (GHI)', 'Sun (POA Temp comp)', 'Sun (POA raw)', 'GHI', 'POA', 'POA irradiance', 'Sun (POA)']

                # Iterate over register groups for the current hardware
                for register_group in hardware_data_response.get('registerGroups', []):
                    for register in register_group.get('registers', []):
                        # Check if the register name is in the list of register names for the category
                        if register['name'] in breaker_register_names:
                            register_values['Status'] = register['value']
                        elif register['name'] in weather_station_register_names:
                            register_values['POA'] = register['value']
                        elif register['name'] in inverterKW_register_names:
                            register_values['KW'] = register['value']
                        elif register['name'] in inverterDC_register_names:
                            register_values['DC V'] = register['value']
                        elif register['name'] in volts_a_register_names:
                            register_values['Volts A'] = register['value']
                        elif register['name'] in volts_b_register_names:
                            register_values['Volts B'] = register['value']
                        elif register['name'] in volts_c_register_names:
                            register_values['Volts C'] = register['value']
                        elif register['name'] in amps_a_register_names:
                            register_values['Amps A'] = register['value']
                        elif register['name'] in amps_b_register_names:
                            register_values['Amps B'] = register['value']
                        elif register['name'] in amps_c_register_names:
                            register_values['Amps C'] = register['value']
                        elif register['name'] in meterkw_register_names:
                            register_values['KW'] = register['value']
                        



                register_values['pytimestamp'] = hdtimestamp
                try:
                    # Save to Dictionary
                    dvtimestamp = hardware_data_response.get('lastUpload')
                    datetime_obj = datetime.datetime.strptime(dvtimestamp, "%Y-%m-%dT%H:%M:%S%z")
                    aetimestamp = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
                    register_values['aetimestamp'] = aetimestamp
                except Exception as e:
                    print("Error parsing timestamp:", e)
                    print("Timestamp value:", dvtimestamp)

                api_data[hardware_id] = register_values

                #with open(troubleshooting_file, 'a') as tfile:
                #    json.dump(register_values, tfile, indent=2)

            elif 400 <= hardware_response.status_code < 500: # Unauthorized or Forbidden
                print(f"Failed to retrieve hardware data for {hardware_id}. Status Code: {hardware_response.status_code}")
            else:
                print(f"Failed to retrieve hardware data for {hardware_id} at {site} in {category}. Status code: {hardware_response.status_code}")
 
    end = time.perf_counter()
    print(f"Pulled Data: {site}\nTime Taken: {round(end-current, 2)}")

if __name__ == '__main__': #This is absolutely necessary due to running the async pool.
    def my_main():
        global hw_sites_mapping, sites_endpoint, dataPullTime
        global today_date
        global start
        # Get today's date
        today_date = datetime.date.today()

        # Your existing code for obtaining the access token and initializing dictionaries
        start = time.perf_counter()

        global api_data
        api_data = multiprocessing.Manager().dict()

        response = get_access_token()
        # Check if the token request was successful (status code 200)
        if response.status_code == 200:
            # Extract the access token from the response
            access_token = response.json().get('access_token')

            pool = multiprocessing.Pool()

            for site, site_data in hw_sites_mapping.items():
                pool.apply_async(get_data_for_site, args=(site, site_data, api_data, hw_sites_mapping, start, base_url, access_token))
            pool.close()
            pool.join()

            api_data_dict = dict(api_data)
            # This was temporary just so I could visualize the output
            json_loop_exit_file = r"G:\Shared drives\O&M\NCC Automations\Notification System\api_data_visualized.json"
            # Convert and write JSON object to file
            with open(json_loop_exit_file, "w+") as outfile: 
                json.dump(api_data_dict, outfile, indent=2)
            
            #print(api_data_dict)

            # Create a connection to the Access database
            global dbconn_str, dbconnection, cursor
            dbconn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\OMOPS\OneDrive - Narenco\Documents\AE API DB.accdb;'
            dbconnection = pyodbc.connect(dbconn_str)
            cursor = dbconnection.cursor()

            data_start = time.perf_counter()
            #Variables Defined for the right now Data

            for site, site_data in hw_sites_mapping.items():
                inv_num = 1   
                for device_category, devices in site_data.items():
                    for hardwareid, device_name in devices.items():
                        if device_category == "breakers":
                            if hardwareid == "390118":
                                violet_Exception = " 2"
                            elif hardwareid == "390117":
                                violet_Exception = " 1"
                            else:
                                violet_Exception = ""
                            try:
                                hdtimestamp_Relay = api_data_dict[f'{hardwareid}']['pytimestamp']
                                aetimestamp_Relay = api_data_dict[f'{hardwareid}']['aetimestamp']
                                relay_stat = api_data_dict[f'{hardwareid}']['Status']
                                valid_values = ['1', '240', 'closed']
                                openClose = True if relay_stat.lower().strip() in valid_values else False
                                cursor.execute(f"""INSERT INTO [{site} Breaker Data{violet_Exception}]
                                            ([Date & Time], Status, HardwareId, lastUpload)
                                                VALUES (?,?,?,?)""", hdtimestamp_Relay, openClose, hardwareid, aetimestamp_Relay)
                                dbconnection.commit()
                            except KeyError:
                                print(f"No Comms with {site} Relay") 
                        if device_category == "meters":
                            try:
                                voltsA = float(re.search(r'\d+', api_data_dict[f'{hardwareid}']['Volts A']).group()) if re.search(r'\d+', api_data_dict[f'{hardwareid}']['Volts A']) else 0
                                voltsB = float(re.search(r'\d+', api_data_dict[f'{hardwareid}']['Volts B']).group()) if re.search(r'\d+', api_data_dict[f'{hardwareid}']['Volts B']) else 0
                                voltsC = float(re.search(r'\d+', api_data_dict[f'{hardwareid}']['Volts C']).group()) if re.search(r'\d+', api_data_dict[f'{hardwareid}']['Volts C']) else 0
                                ampsA = float(re.search(r'\d+', api_data_dict[f'{hardwareid}']['Amps A']).group()) if re.search(r'\d+', api_data_dict[f'{hardwareid}']['Amps A']) else 0
                                ampsB = float(re.search(r'\d+', api_data_dict[f'{hardwareid}']['Amps B']).group()) if re.search(r'\d+', api_data_dict[f'{hardwareid}']['Amps B']) else 0
                                ampsC = float(re.search(r'\d+', api_data_dict[f'{hardwareid}']['Amps C']).group()) if re.search(r'\d+', api_data_dict[f'{hardwareid}']['Amps C']) else 0
                                if api_data_dict[f'{hardwareid}']['KW'].startswith('-'):
                                    meterkw = 0
                                else:
                                    meterkw = float(re.search(r'\d+', api_data_dict[f'{hardwareid}']['KW']).group()) if re.search(r'\d+', api_data_dict[f'{hardwareid}']['KW']) else 0

                                hdtimestamp_Meter = api_data_dict[f'{hardwareid}']['pytimestamp']
                                aetimestamp_Meter = api_data_dict[f'{hardwareid}']['aetimestamp']
                                cursor.execute(f""" INSERT INTO [{site} Meter Data] ([Date & Time], [Volts A], [Volts B], [Volts C], [Amps A], [Amps B], [Amps C], HardwareId, lastUpload, kW) VALUES (?,?,?,?,?,?,?,?,?,?)"""
                                            , hdtimestamp_Meter, voltsA, voltsB, voltsC, ampsA, ampsB, ampsC, hardwareid, aetimestamp_Meter, meterkw)
                                dbconnection.commit()
                            except KeyError as e:
                                print(f"No Comms with {site} Meter", e)
                            except AttributeError:
                                print(f"{site} Meter Volt or Amp value is Null")
                        if device_category == "weather_stations":
                            #POA
                            try:
                                hdtimestamp_POA = api_data_dict[f'{hardwareid}']['pytimestamp']
                                aetimestamp_POA = api_data_dict[f'{hardwareid}']['aetimestamp']
                                poa = float(re.search(r'\d+', api_data_dict[f'{hardwareid}']['POA']).group())
                                cursor.execute(f"""INSERT INTO [{site} POA Data] ([Date & Time], [W/M²], HardwareId, lastUpload) VALUES (?,?,?,?)""", hdtimestamp_POA, poa, hardwareid, aetimestamp_POA)
                                dbconnection.commit()
                            except KeyError:
                                print(f"No Comms with {site} POA")
                            except AttributeError:
                                print(f"{site} POA 0 W/M²")
                                poa = 0
                                hdtimestamp_POA = api_data_dict[f'{hardwareid}']['pytimestamp']
                                aetimestamp_POA = api_data_dict[f'{hardwareid}']['aetimestamp']
                                cursor.execute(f"""INSERT INTO [{site} POA Data] ([Date & Time], [W/M²], HardwareId, lastUpload) VALUES (?,?,?,?)""", hdtimestamp_POA, poa, hardwareid, aetimestamp_POA)
                                dbconnection.commit()
                        if device_category == "inverters":
                            # Duplin String/Central Inv Work Around
                            str_invs = ["94056", "94057", "94058", "94059", "94060", "94061", "94062", "94063", "94064", "94065", "94066", "94067", "94068", "94069", "94070", "94071", "94072", "94073"]
                            cent_invs = ["94053", "94055", "94054"]
                            if hardwareid in str_invs:
                                duplin_exception = " String"
                            elif hardwareid in cent_invs:
                                duplin_exception = " Central"
                            else:
                                duplin_exception = ""

                            #Inverters
                            try:
                                if api_data_dict[f'{hardwareid}']['KW'].startswith('-'):
                                    invkw = 0
                                else:
                                    invkW = float(re.search(r'\d+', api_data_dict[f'{hardwareid}']['KW']).group())
                                if site == 'Cougar':
                                    invkW = (invkW/1000)
                            except KeyError:
                                print(f"No Comms with {site}{duplin_exception} Inv {inv_num} kW")
                            except AttributeError:
                                print(f"{site}{duplin_exception} Inv {inv_num} kW not reporting to AE")
                                invkW = 0
                            try:
                                hdtimestamp_inv = api_data_dict[f'{hardwareid}']['pytimestamp']
                                aetimestamp_inv = api_data_dict[f'{hardwareid}']['aetimestamp']
                            except:
                                print("I Never thought this would happen, Inv timestamp error")
                            try:
                                invDCV = float(re.search(r'\d+', api_data_dict[f'{hardwareid}']['DC V']).group())
                            except KeyError:
                                print(f"No Comms with {site}{duplin_exception} Inv {inv_num}")
                            except AttributeError:
                                print(f"{site}{duplin_exception} Inv {inv_num} DC V not reporting to AE")
                                invDCV = 0
                            if duplin_exception == " String":    
                                cursor.execute(f""" INSERT INTO [{site}{duplin_exception} INV {inv_num - 3} Data] (HardwareId, [Date & Time], kW, [DC V], lastUpload) VALUES (?,?,?,?,?)""",
                                            (hardwareid, hdtimestamp_inv, invkW, invDCV, aetimestamp_inv))
                                dbconnection.commit()
                            else:
                                cursor.execute(f""" INSERT INTO [{site}{duplin_exception} INV {inv_num} Data] (HardwareId, [Date & Time], kW, [DC V], lastUpload) VALUES (?,?,?,?,?)""",
                                            (hardwareid, hdtimestamp_inv, invkW, invDCV, aetimestamp_inv))
                                dbconnection.commit()
                            inv_num += 1


            finish = time.perf_counter()
            print("Data Injection Time:", round(finish - data_start, 5))
            # Close the connection after all data is inserted
            dbconnection.close()

            end = time.perf_counter()
            dataPullTime = round((end - start)/60, 3)
            print("Total Time:", round((end - start)/60, 3), "Minutes")
            reset_count(auth_file)
        else:
            print(f"Token request failed. Status code: {response.status_code}")
            print("Why did it Fail?", response.text)
            new_value = counting_fails(auth_file)
            print(f"Failed Attempts: {new_value}")


    loop_exit_file = "C:\\Users\\OMOPS\\OneDrive - Narenco\\Documents\\APISiteStat\\Exiting Loop due to Failed Authentications.txt"
    auth_file = open(loop_exit_file, "r+")

    my_main()
    wait_time = datetime.datetime.now().replace(hour=8, minute=30, second=0, microsecond=0)
    auth_file.close()
    while True:
        auth_file = open(loop_exit_file, "r+")
        current_time = datetime.datetime.now()
        count = check_fail_loop(auth_file)
        if count > 20:
            #Failed too many times
            reset_count(auth_file)
            os._exit(0)
            break
        #winsound.Beep(250, 500)
        if count > 4 and count < 10:
            #Failed lots, so wait longer
            print("Waiting 120 Seconds then pulling data again")
            time.sleep(120)
        elif count > 10:
            #Failed lots, so wait longer
            print("Waiting 180 Seconds then pulling data again")
            time.sleep(180)     
        else:
            wait = (2 - dataPullTime) * 60
            if wait <= 0:
                wait = 10  
            print(f"Waiting {round(wait, 2)} Seconds then pulling data again")
            time.sleep(wait)

        print("Looping")
        my_main()
        auth_file.close()
