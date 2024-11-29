#AE API GUI
import pyodbc
from datetime import datetime, date, time, timedelta
from tkinter import *
from tkinter import messagebox
import atexit
import time as ty
import threading
import numpy as np
from tkinter import simpledialog
import ctypes
from icecream import ic
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import subprocess
import os
import json

breaker_pulls = 6
meter_pulls = 6


start = ty.perf_counter()
myappid = 'AE.API.Data.GUI'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

root = Tk()
root.title("Site Data")
try:
    root.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
root.wm_attributes("-topmost", True)
root.configure(bg="yellow") 

checkIns= Toplevel(root)
try:
    checkIns.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
checkIns.title("Personnel On-Site")

checkIns.wm_attributes("-topmost", True)


timeW= Toplevel(root)
try:
    timeW.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
timeW.title("Timestamps")
timeW.wm_attributes("-topmost", True)
timeW_notes= Label(timeW, text= "Data Pull Timestamps", font= ("Calibiri", 16))
timeW_notes.grid(row=0, column= 0, columnspan= 4)

# Fit in another 2 columns and make them sticky to eeach other like these below.
time1= Label(timeW, text= "First:", font= ("Calibiri", 14))
time2= Label(timeW, text= "Second:", font= ("Calibiri", 14))
time3= Label(timeW, text= "Third:", font= ("Calibiri", 14))
time4= Label(timeW, text= "Fourth:", font= ("Calibiri", 14))
time5= Label(timeW, text= "Tenth:", font= ("Calibiri", 14))
timeL= Label(timeW, text= "Fifteenth:", font= ("Calibiri", 14))
time1.grid(row=1, column= 0, sticky=E)
time2.grid(row=2, column= 0, sticky=E)
time3.grid(row=3, column = 0, sticky=E)
time4.grid(row=4, column = 0, sticky=E)
time5.grid(row=5, column = 0, sticky=E)
timeL.grid(row=6, column = 0, sticky=E)
time1v= Label(timeW, text= "Time")
time2v= Label(timeW, text= "Time")
time3v= Label(timeW, text= "Time")
time4v= Label(timeW, text= "Time")
time10v= Label(timeW, text= "Time")
timeLv= Label(timeW, text= "Time")
time1v.grid(row=1, column= 1, sticky=W)
time2v.grid(row=2, column= 1, sticky=W)
time3v.grid(row=3, column = 1, sticky=W)
time4v.grid(row=4, column = 1, sticky=W)
time10v.grid(row=5, column = 1, sticky=W)
timeLv.grid(row=6, column = 1, sticky=W)



datalbl= Label(timeW, text= "MsgBox Data:", font= ("Calibiri", 16))
datalbl.grid(row=1, column=2)
inverterT = Label(timeW, text= "Inverters:", font= ("Calibiri", 14))
inverterT.grid(row=2, column=2)
spread15 = Label(timeW, text= "Time")
spread15.grid(row=3, column=2)
breakermeter = Label(timeW, text= """Breakers &
Meters:""", font= ("Calibiri", 14))
breakermeter.grid(row=4, column=2)
spread10 = Label(timeW, text= "Time")
spread10.grid(row=5, column=2)



alertW = Toplevel(root)
alertW.title("Alert Windows Info")
alertW.wm_attributes("-topmost", True)
try:
    alertW.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")




#Top Labels Main Window
siteLabel = Label(root, bg="yellow", text= "Sites")
siteLabel.grid(row=0, column= 0, sticky=W)
breakerstatusLabel= Label(root, bg="yellow", text= "Breaker Status")
breakerstatusLabel.grid(row=0, column=1)
meterVLabel = Label(root, bg="yellow", text= "Utility V")
meterVLabel.grid(row= 0, column=2)
meterkWLabel = Label(root, bg="yellow", text="Meter kW")
meterkWLabel.grid(row=0, column=4)
POALabel = Label(root, bg="yellow", text= "POA")
POALabel.grid(row=0, column= 5, columnspan=2)


#Inv Windows
inv = Toplevel(root)
inv.title("Harrison Street")
try:
    inv.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
narenco = Toplevel(root)
narenco.title("NARENCO")
try:
    narenco.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
solrvr = Toplevel(root)
solrvr.title("SOL River")
try:
    solrvr.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
soltage = Toplevel(root)
soltage.title("Soltage")
try:
    soltage.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
ncemc = Toplevel(root)
ncemc.title("NCEMC")
try:
    ncemc.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
#Inverter Windows created


master_List_Sites = [('Bishopville II', 36, 'bishopvilleII', inv), ('Bluebird', 24, 'bluebird', narenco), ('Bulloch 1A', 24, 'bulloch1a', solrvr), ('Bulloch 1B', 24, 'bulloch1b', solrvr), ('Cardinal', 59, 'cardinal', narenco), ('CDIA', 1, 'cdia', narenco),
                     ('Cherry', 4, 'cherry', narenco), ('Cougar', 30, 'cougar', narenco), ('Conetoe', 4, 'conetoe', soltage), ('Duplin', 21, 'duplin', soltage), ('Elk', 43, 'elk', solrvr), ('Freight Line', 18, 'freightline', ncemc), ('Gray Fox', 40, 'grayfox', solrvr),
                      ('Harding', 24, 'harding', solrvr), ('Harrison', 43, 'harrison', narenco), ('Hayes', 26, 'hayes', narenco), ('Hickory', 2, 'hickory', narenco), ('Hickson', 16, 'hickson', inv), ('Holly Swamp', 16, 'hollyswamp', ncemc),
                       ('Jefferson', 64, 'jefferson', inv), ('Marshall', 16, 'marshall', inv), ('McLean', 40, 'mcLean', solrvr), ('Ogburn', 16, 'ogburn', inv), ('PG', 18, 'pg', ncemc), ('Richmond', 24, 'richmond', solrvr),
                        ('Shorthorn', 72, 'shorthorn', solrvr), ('Sunflower', 80, 'sunflower', solrvr), ('Tedder', 16, 'tedder', inv), ('Thunderhead', 16, 'thunderhead', inv), ('Upson', 24, 'upson', solrvr), 
                        ('Van Buren', 17, 'vanburen', inv), ('Warbler', 32, 'warbler', solrvr), ('Washington', 40, 'washington', solrvr), ('Wayne 1', 4, 'wayne1', soltage), ('Wayne 2', 4, 'wayne2', soltage), 
                        ('Wayne 3', 4, 'wayne3', soltage), ('Wellons', 6, 'wellons', narenco), ('Whitehall', 16, 'whitehall', solrvr), ('Whitetail', 80, 'whitetail', solrvr), ('Violet', 2, 'violet', narenco)]

has_breaker = ['Bishopville II', 'Cardinal', 'Cherry', 'Elk', 'Gray Fox', 'Harding', 'Harrison', 'Hayes', 'Hickory', 'Hickson', 'Jefferson', 'Marshall', 'McLean', 'Ogburn', 
               'Shorthorn', 'Sunflower', 'Tedder', 'Thunderhead', 'Warbler', 'Washington', 'Whitehall', 'Whitetail', 'Violet']

all_CBs = []


#Start looping through the dictionary at the top to create what is Below. 
#This one shall create the Sites Breaker/Meter/POA window
for ro, (name, invnum, varname, custid) in enumerate(master_List_Sites, start=1):
    #Site Info
    globals()[f'{varname}Label'] = Label(root, bg="yellow", text=f'{name}', fg= 'black')
    globals()[f'{varname}Label'].grid(row=ro, column= 0, sticky=W)
    if name in has_breaker:
        if name == 'Violet':
            vio_excep = 1
        else:
            vio_excep = ''
        globals()[f'{varname}{vio_excep}statusLabel'] = Label(root, bg="yellow", text='❌', fg= 'black')
        globals()[f'{varname}{vio_excep}statusLabel'].grid(row=ro, column= 1)
        if name == 'Violet':
            violet2statusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
            violet2statusLabel.grid(row=ro+1, column= 1)

    if name != 'CDIA':
        globals()[f'{varname}meterVLabel'] = Label(root, bg="yellow", text='V', fg= 'black')
        globals()[f'{varname}meterVLabel'].grid(row=ro, column= 2)

    globals()[f'{varname}metercbval'] = IntVar()
    all_CBs.append(globals()[f'{varname}metercbval'])
    globals()[f'{varname}metercb'] = Checkbutton(root, bg="yellow", variable=globals()[f'{varname}metercbval'], fg= 'black')
    globals()[f'{varname}metercb'].grid(row=ro, column= 3)

    globals()[f'{varname}meterkWLabel'] = Label(root, bg="yellow", text='kW', fg= 'black')
    globals()[f'{varname}meterkWLabel'].grid(row=ro, column= 4)

    globals()[f'{varname}POAcbval'] = IntVar()
    all_CBs.append(globals()[f'{varname}POAcbval'])
    globals()[f'{varname}POAcb'] = Checkbutton(root, bg="yellow", text='X', variable=globals()[f'{varname}POAcbval'], fg= 'black')
    globals()[f'{varname}POAcb'].grid(row=ro, column= 5)
    #End
    #INVERTER INFO
    if name != 'CDIA':
        globals()[f'{varname}invsLabel'] = Label(custid, text=name)
        globals()[f'{varname}invsLabel'].grid(row= 0, column= ro*2, columnspan= 2)
    for num in range(1, invnum+1):
        if name != 'CDIA':
            globals()[f'{varname}inv{num}cbval'] = IntVar()
            all_CBs.append(globals()[f'{varname}inv{num}cbval'])
            globals()[f'{varname}inv{num}cb'] = Checkbutton(custid, text=str(num), variable=globals()[f'{varname}inv{num}cbval'])
            globals()[f'{varname}inv{num}cb'].grid(row= num, column= ro*2)
            
            globals()[f'{varname}invup{num}cbval'] = IntVar()
            all_CBs.append(globals()[f'{varname}invup{num}cbval'])
            globals()[f'{varname}invup{num}cb'] = Checkbutton(custid, variable=globals()[f'{varname}invup{num}cbval'])
            globals()[f'{varname}invup{num}cb'].grid(row= num, column= (ro*2)+1)

class PausableTimer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback 
        self._pause_event = threading.Event()
        self._stop_event = threading.Event()
        self._timer_thread = threading.Thread(target=self._run)
        self._pause_event.set()
        self._elapsed = 0

    def _run(self):
        start = ty.time()
        while not self._stop_event.is_set() and self._elapsed < self._timeout:
            if self._pause_event.is_set():
                ty.sleep(0.1)
                self._elapsed += ty.time() - start
                start = ty.time()
            else:
                start = ty.time()
                self._pause_event.wait()
        if not self._stop_event.is_set():
            self._callback()
    
    def start(self):
        self._timer_thread.start()

    def pause(self):
        self._pause_event.clear()

    def resume(self):
        self._pause_event.set()

    def stop(self):
        self._stop_event.set()

    def time_remaining(self):
        time_left = self._timeout - self._elapsed
        if time_left < 0:
            time_left = 0
        return time_left



def connect_Logbook():
    global cur, lbconnection

    lbconn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=G:\Shared drives\Narenco Projects\O&M Projects\NCC\NCC\NCC 039.accdb;'
    lbconnection = pyodbc.connect(lbconn_str)
    cur = lbconnection.cursor()


def connect_db():
    # Create a connection to the Access database
    globals()['dbconn_str'] = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\OMOPS\OneDrive - Narenco\Documents\AE API DB.accdb;'
    globals()['dbconnection'] = pyodbc.connect(dbconn_str)
    globals()['c'] = dbconnection.cursor()
    globals()['db'] = r"C:\Users\OMOPS\OneDrive - Narenco\Documents\AE API DB.accdb"

def launch_check():
    tday = datetime.now()
    format_date = tday.strftime('%m/%d/%Y')
    query = """
    SELECT TOP 16 [Date & Time] FROM [Whitetail Meter Data]
    WHERE FORMAT([Date & Time], 'MM/DD/YYYY') = ?
    """
    c.execute(query, (format_date,))
    data = c.fetchall()
    if len(data) == 16:
        #ic(data)
        return True
    else:
        #ic(data)
        return False
    
def duplinC_last_online(site, inv_num):
    query = f"""
    SELECT TOP 1 [Date & Time] 
    FROM [{site} String INV {inv_num} Data]
    WHERE [kW] > 2
    ORDER BY [Date & Time] DESC
    """
    c.execute(query)
    data = c.fetchone()
    if data:
        last_producing = f"Last Online: {data[0]}"
        return last_producing
    else:
        return None
    
def duplinS_last_online(site, inv_num):
    query = f"""
    SELECT TOP 1 [Date & Time] 
    FROM [{site} String INV {inv_num} Data]
    WHERE [kW] > 2
    ORDER BY [Date & Time] DESC
    """
    c.execute(query)
    data = c.fetchone()
    if data:
        last_producing = f"Last Online: {data[0]}"
        return last_producing
    else:
        return None

def last_online(site, inv_num):
    query = f"""
    SELECT TOP 1 [Date & Time] 
    FROM [{site} INV {inv_num} Data]
    WHERE [kW] > 2
    ORDER BY [Date & Time] DESC
    """
    c.execute(query)
    data = c.fetchone()
    if data:
        last_producing = f"Last Online: {data[0]}"
        return last_producing
    else:
        return None

def meter_last_online(site):
    query = f"""
    SELECT TOP 1 [Date & Time] 
    FROM [{site} Meter Data]
    WHERE [kW] > 2
    ORDER BY [Date & Time] DESC
    """
    c.execute(query)
    data = c.fetchone()
    if data:
        last_producing = f"Last Online: {data[0]}"
        return last_producing
    else:
        return None
        
def last_closed(site):
    if site == "Violet":
        query1 = f"""
        SELECT TOP 1 [Date & Time] 
        FROM [{site} Breaker Data 1]
        WHERE [Status] = True
        ORDER BY [Date & Time] DESC
        """
        c.execute(query1)
        data1 = c.fetchone()
        query2 = f"""
        SELECT TOP 1 [Date & Time] 
        FROM [{site} Breaker Data 2]
        WHERE [Status] = True
        ORDER BY [Date & Time] DESC
        """
        c.execute(query2)
        data2 = c.fetchone()

        if data1 and data2:
            data = f"Last Closed Breaker 1: {data1[0]} | Breaker 2: {data2[0]}"
            return data
        else:
            return None
    elif site in ['Cardinal', 'Harrison', 'Hayes', 'Warbler']:
        query = f"""
        SELECT TOP 1 [Date & Time]
        FROM [{site} Meter Data]
        WHERE [Amps A] <> 0 AND [Amps B] <> 0 AND [Amps C] <> 0
        ORDER BY [Date & Time] DESC 
        """
        c.execute(query)
        data = c.fetchone()
        if data:
            last_breaker = f"Last Closed: {data[0]}"
            return last_breaker
        else:
            return None
    else:
        query = f"""
        SELECT TOP 1 [Date & Time] 
        FROM [{site} Breaker Data]
        WHERE [Status] = True
        ORDER BY [Date & Time] DESC
        """
        c.execute(query)
        data = c.fetchone()
        if data:
            last_breaker = f"Last Closed: {data[0]}"
            return last_breaker
        else:
            return None

def check_inv_consecutively_online(alist):
    consecutive_count = 0
    
    for num in alist:
        if num > 0:
            consecutive_count += 1
            if consecutive_count == 2:
                return True
        else:
            consecutive_count = 0
    
    return False

def update_data():
    save_cb_state()
    update_data_start = ty.perf_counter()

    status_all = {}
    #Retireve Current INV status's and store in lists
    for site_info in master_List_Sites:
        name, inverters, var_name, custid = site_info
        l = []
        if name != "CDIA":
            for i in range(1, inverters + 1):
                checkbox_var = globals()[f'{var_name}inv{i}cbval']
                if not checkbox_var.get():
                    config_color = globals()[f'{var_name}inv{i}cb'].cget("bg")
                    l.append(config_color)
            status_all[f'{var_name}'] = l



    tm_now = datetime.now()
    str_tm_now = tm_now.strftime('%H')
    h_tm_now = int(str_tm_now)

    for site_info in master_List_Sites:
        name, inverters, var_name, custid = site_info
        if name == "Violet":
            time_date_compare = (timecurrent - timedelta(hours=4))
        else:
            time_date_compare = (timecurrent - timedelta(hours=2))


        #POA data Update
        if globals()[f'{var_name}POAcbval'].get() == 1:
            poa_noti = False
            poa = 9999
        else:
            poa = POA_data[f'{name} POA Data'][0]
            poa_noti = True
        #POA Comms check
        poa_data = max(comm_data[f'{name} POA Data'])[0]
        strtime_poa = poa_data.strftime('%m/%d/%y | %H:%M')

        if poa_data < time_date_compare:
            poalbl = globals()[f'{var_name}POAcb'].cget('bg')
            if poalbl != 'pink' and poa_noti:
                messagebox.showwarning(parent= alertW, title=f"{name}, POA Comms Error", message=f"{name} lost comms with POA sensor at {strtime_poa}")
            globals()[f'{var_name}POAcb'].config(bg='pink', text=poa)
        else:
            globals()[f'{var_name}POAcb'].config(bg='yellow', text=poa)

        if name != "CDIA":
            #Meter Update
            master_cb_skips_INV_check = True if globals()[f'{var_name}metercbval'].get() == 0 else False
            #print(name, master_cb_skips_INV_check)
            metercomms = max(comm_data[f'{name} Meter Data'])[0]
            meter_Ltime = metercomms.strftime('%m/%d/%y | %H:%M')
            if metercomms > time_date_compare:
                meterdata = meter_data[f'{name} Meter Data']
                meterdataVA= None
                meterdataVB= None
                meterdataVC= None 
                meterdataKW= None 
                meterdataAA= None 
                meterdataAB= None 
                meterdataAC= None

                # Iterate over fetched rows to find the maximum value for each column
                for row in meterdata:
                    # Update maximum values for each column
                    meterdataVA = max(meterdataVA, row[2]) if meterdataVA is not None else row[2]
                    meterdataVB = max(meterdataVB, row[3]) if meterdataVB is not None else row[3]
                    meterdataVC = max(meterdataVC, row[4]) if meterdataVC is not None else row[4]

                if meterdataVA != 0 and meterdataVB != 0 and meterdataVC !=0:
                    _percent_difference_AB = abs(meterdataVA - meterdataVB) / max(meterdataVA, meterdataVB) * 100
                    _percent_difference_AC = abs(meterdataVA - meterdataVC) / max(meterdataVA, meterdataVC) * 100
                    _percent_difference_BC = abs(meterdataVB - meterdataVC) / max(meterdataVB, meterdataVC) * 100
                else:
                    _percent_difference_AB = 0
                    _percent_difference_AC = 0
                    _percent_difference_BC = 0

                meterVconfig = globals()[f'{var_name}meterVLabel'].cget("text")

                if meterVconfig == "❌❌":
                    meterVstat = 0    
                else:
                    meterVstat = 1

                meterdataavgAA = np.mean([row[5] for row in meterdata if row[5] is not None])
                meterdataavgAB = np.mean([row[6] for row in meterdata if row[6] is not None])
                meterdataavgAC = np.mean([row[7] for row in meterdata if row[7] is not None])
                meterdataAA = all(row[5] < 1 for row in meterdata if row[5] is not None)
                meterdataAB = all(row[6] < 1 for row in meterdata if row[6] is not None)
                meterdataAC = all(row[7] < 1 for row in meterdata if row[7] is not None)
                meterdataKW = np.mean([row[10] for row in meterdata if row[10] is not None])

                #print(f'{name} |  A: {meterdataAA}, B: {meterdataAB}, C: {meterdataAC}')
                #Accounting for Sites reporting Votlage differently
                if name == "Hickory":
                    val = 5
                else:
                    val = 5000

                if (meterdataVA or meterdataVB or meterdataVC) < val and meterVstat == 1:
                    meterVstatus= '❌❌'
                    meterVstatuscolor= 'red'
                    online = meter_last_online(name)
                    messagebox.showerror(parent=alertW, title= f"{name} Meter", message= f"Loss of Utility Voltage or Lost Comms with Meter. {online}")
                elif _percent_difference_AB <= 5 and _percent_difference_AC <= 5 and _percent_difference_BC <= 5 and meterdataVA or meterdataVB or meterdataVC > 5000:
                    meterVstatus= '✓✓✓'
                    meterVstatuscolor= 'green'
                    if meterVstat == 0:
                        messagebox.showinfo(parent=alertW, title=f"{name} Meter", message= "Utility Voltage Restored!!! Close the Breaker")
                else:
                    meterVstatus= '❌❌'
                    meterVstatuscolor= 'red'

                if (meterdataKW < 2 or meterdataAA or meterdataAB or meterdataAC) and begin:
                    if name != 'Van Buren': # This if statement and elif pair juke around the VanBuren being down a phase. 
                        meterkWstatus= '❌❌'
                        meterkWstatuscolor= 'red'
                        meterlbl = globals()[f'{var_name}meterkWLabel'].cget('bg')
                        if meterlbl != 'red' and master_cb_skips_INV_check:
                            online = meter_last_online(name)
                            messagebox.showerror(parent= alertW, title=f"{name}, Power Loss", message=f"Site: {name}\nMeter Production: {round(meterdataKW, 2)}\nMeter Amps:\nA: {round(meterdataavgAA, 2)}\nB: {round(meterdataavgAB, 2)}\nC: {round(meterdataavgAC, 2)}\n{online}")
                
                    elif meterdataAC or meterdataAB or meterdataKW < 2:
                        meterkWstatus= '❌❌'
                        meterkWstatuscolor= 'red'
                        meterlbl = globals()[f'{var_name}meterkWLabel'].cget('bg')
                        if meterlbl != 'red' and master_cb_skips_INV_check:
                            online = meter_last_online(name)
                            messagebox.showerror(parent= alertW, title=f"{name}, Meter Power Loss", message=f"Site: {name}\nMeter Production: {round(meterdataKW, 2)}\nMeter Amps:\nA: {round(meterdataavgAA, 2)}\nB: {round(meterdataavgAB, 2)}\nC: {round(meterdataavgAC, 2)}\n{online}")
                
                    

                else:
                    meterkWstatus= '✓✓✓'
                    meterkWstatuscolor= 'green'
                globals()[f'{var_name}meterVLabel'].config(text= meterVstatus, bg= meterVstatuscolor)
                globals()[f'{var_name}meterkWLabel'].config(text= meterkWstatus, bg= meterkWstatuscolor)

            else:
                meterlbl = globals()[f'{var_name}meterkWLabel'].cget('bg')
                if meterlbl != 'pink' and master_cb_skips_INV_check:
                    messagebox.showerror(parent= alertW, title=f"{name}, Meter Comms Loss", message=f"Meter Comms lost {meter_Ltime} with the Meter at {name}! Please Investigate!")
                globals()[f'{var_name}meterkWLabel'].config(bg='pink')
                globals()[f'{var_name}meterVLabel'].config(bg='pink')

        #Breaker Update
        sites_WObreakers = ['Bluebird', 'Bulloch 1A', 'Bulloch 1B', 'Conetoe', 'CDIA', 'Cougar', 'Duplin', 'Freight Line', 'Holly Swamp', 'PG', 'Richmond', 'Upson', 'Van Buren', 'Wayne 1', 'Wayne 2', 'Wayne 3', 'Wellons']
        if name not in sites_WObreakers:
            if name == "Violet":
                for two in range(1, 3):
                    breakercomm = max(comm_data[f'{name} Breaker Data {two}'])[0]
                    bk_Ltime = breakercomm.strftime('%m/%d/%y | %H:%M')
                    if breakercomm > time_date_compare:
                        breakerconfig = globals()[f'{var_name}{two}statusLabel'].cget("text")
                        if any(breaker_data[f'{name} Breaker Data {two}'][i][0] == True for i in range(breaker_pulls)):
                            breakerstatus = "✓✓✓"
                            breakerstatuscolor = 'green'
                        else:         
                            if breakerconfig != "❌❌" and master_cb_skips_INV_check:
                                last_operational = last_closed(name)
                                messagebox.showerror(parent= alertW, title= f"{name}", message= f"{name} Breaker Tripped Open, Please Investigate! {last_operational}")
                            breakerstatus = "❌❌"
                            breakerstatuscolor = 'red'
                        globals()[f'{var_name}{two}statusLabel'].config(text= breakerstatus, bg=breakerstatuscolor)
                    else:
                        bklbl = globals()[f'{var_name}{two}statusLabel'].cget('bg')
                        globals()[f'{var_name}{two}statusLabel'].config(bg='pink')
                        if bklbl != 'pink' and master_cb_skips_INV_check:
                            messagebox.showerror(parent= alertW, title=f"{name}, Breaker Comms Loss", message=f"Breaker Comms lost {bk_Ltime} with the Breaker at {name}! Please Investigate!")
            elif name in ['Cardinal', 'Harrison', 'Hayes', 'Warbler', 'Hickory']:
                if metercomms > time_date_compare:
                    if any(meter_data[f'{name} Meter Data'][i][j] == 0 for i in range(meter_pulls) for j in range(5, 8)):
                        breakerconfig = globals()[f'{var_name}statusLabel'].cget("text")
                        if breakerconfig != "❌❌" and master_cb_skips_INV_check:
                            last_operational = last_closed(name)
                            messagebox.showerror(parent= alertW, title= f"{name}", message= f"{name} Breaker Tripped Open, Please Investigate! {last_operational}")
                        breakerstatus = "❌❌"
                        breakerstatuscolor = 'red'     
                    else:
                            breakerstatus = "✓✓✓"
                            breakerstatuscolor = 'green'
                    globals()[f'{var_name}statusLabel'].config(text= breakerstatus, bg=breakerstatuscolor)
                else:
                    metercomms_time = metercomms.strftime('%m/%d/%y | %H:%M')
                    bklbl = globals()[f'{var_name}statusLabel'].cget('bg')
                    globals()[f'{var_name}statusLabel'].config(bg='pink')
                    if bklbl != 'pink' and master_cb_skips_INV_check:
                        messagebox.showerror(parent= alertW, title=f"{name}, Meter Comms Loss", message=f"Meter Comms lost {metercomms_time} with the Meter at {name}! Please Investigate!")   
            else:
                breakercomm = max(comm_data[f'{name} Breaker Data'])[0]
                bk_Ltime = breakercomm.strftime('%m/%d/%y | %H:%M')

                if breakercomm > time_date_compare:
                    breakerconfig = globals()[f'{var_name}statusLabel'].cget("text")

                    if any(breaker_data[f'{name} Breaker Data'][i][0] == True for i in range(breaker_pulls)):
                        breakerstatus = "✓✓✓"
                        breakerstatuscolor = 'green'
                    else:         
                        if breakerconfig != "❌❌" and master_cb_skips_INV_check:
                            last_operational = last_closed(name)
                            messagebox.showerror(parent= alertW, title= f"{name}", message= f"{name} Breaker Tripped Open, Please Investigate! {last_operational}")
                        breakerstatus = "❌❌"
                        breakerstatuscolor = 'red'
                    globals()[f'{var_name}statusLabel'].config(text= breakerstatus, bg=breakerstatuscolor)
                else:
                    bklbl = globals()[f'{var_name}statusLabel'].cget('bg')
                    globals()[f'{var_name}statusLabel'].config(bg='pink')
                    if bklbl != 'pink' and master_cb_skips_INV_check:
                        messagebox.showerror(parent= alertW, title=f"{name}, Breaker Comms Loss", message=f"Breaker Comms lost {bk_Ltime} with the Breaker at {name}! Please Investigate!")
        if name == "Duplin":
            for r in range(1, 4):
                data = inv_data[f'{name} Central INV {r} Data']
                current_config = globals()[f'{var_name}inv{r}cb'].cget("bg")
                cbval = globals()[f'{var_name}inv{r}cbval'].get()
                total_dcv = sum(row[4] for row in data)
                avg_dcv = total_dcv / len(data)
                inv_comm = max(comm_data[f'{name} Central INV {r} Data'])[0]
                inv_Ltime = inv_comm.strftime('%m/%d/%y | %H:%M')
                if inv_comm > time_date_compare:
                    if all(point[3] < 1 for point in data):
                        if avg_dcv > 100:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 75)) and cbval == 0 and master_cb_skips_INV_check:
                                online_last = duplinC_last_online(name, r)
                                messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Central Inverter {r} Offline, Good DC Voltage | {online_last}")
                            globals()[f'{var_name}inv{r}cb'].config(bg='orange')
                        else:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 75)) and cbval == 0 and master_cb_skips_INV_check:
                                online_last = duplinC_last_online(name, r)
                                messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Central Inverter {r} Offline | {online_last}")
                            globals()[f'{var_name}inv{r}cb'].config(bg='red')
                    else:
                        if check_inv_consecutively_online(point[3] for point in data):
                            globals()[f'{var_name}inv{r}cb'].config(bg='green')
                else:
                    invlbl = globals()[f'{var_name}inv{r}cb'].cget('bg')
                    globals()[f'{var_name}inv{r}cb'].config(bg='pink')
                    if invlbl != 'pink' and cbval == 0 and master_cb_skips_INV_check:
                        messagebox.showerror(parent= alertW, title=f"{name}, Inverter Comms Loss", message=f"INV Comms lost {inv_Ltime} with Central Inverter {r} at {name}! Please Investigate!")

            stringinv = 4
            for r in range(1, 19):
                data = inv_data[f'{name} String INV {r} Data']
                current_config = globals()[f'{var_name}inv{stringinv}cb'].cget("bg")
                cbval = globals()[f'{var_name}inv{r}cbval'].get()
                total_dcv = sum(row[4] for row in data)
                avg_dcv = total_dcv / len(data)
                inv_comm = max(comm_data[f'{name} String INV {r} Data'])[0]
                inv_Ltime = inv_comm.strftime('%m/%d/%y | %H:%M')
                if inv_comm > time_date_compare:
                    if all(point[3] < 1 for point in data):
                        if avg_dcv > 100:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 75)) and cbval == 0 and master_cb_skips_INV_check:
                                online_last = duplinS_last_online(name, r)
                                messagebox.showwarning(title=f"{name}", parent= alertW, message= f"String Inverter {r} Offline, Good DC Voltage | {online_last}")
                            globals()[f'{var_name}inv{stringinv}cb'].config(bg='orange')
                            stringinv += 1  
                        else:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 75)) and cbval == 0 and master_cb_skips_INV_check:
                                online_last = duplinS_last_online(name, r)
                                messagebox.showwarning(title=f"{name}", parent= alertW, message= f"String Inverter {r} Offline | {online_last}")
                            globals()[f'{var_name}inv{stringinv}cb'].config(bg='red')
                            stringinv += 1  
                    else:
                        if check_inv_consecutively_online(point[3] for point in data):
                            globals()[f'{var_name}inv{stringinv}cb'].config(bg='green')
                        stringinv += 1  
                else:
                    invlbl = globals()[f'{var_name}inv{r}cb'].cget('bg')
                    globals()[f'{var_name}inv{stringinv}cb'].config(bg='pink')
                    if invlbl != 'pink' and cbval == 0 and master_cb_skips_INV_check:
                        messagebox.showerror(parent= alertW, title=f"{name}, Inverter Comms Loss", message=f"INV Comms lost {inv_Ltime} with String Inverter {r} at {name}! Please Investigate!")
                    stringinv += 1               
        elif name == "CDIA":
                data = inv_data[f'{name} INV 1 Data']
                current_config = globals()[f'{var_name}meterkWLabel'].cget("bg")
                cbval = globals()[f'{var_name}metercbval'].get()
                total_dcv = sum(row[4] for row in data)
                avg_dcv = total_dcv / len(data)
                inv_comm = max(comm_data[f'{name} INV 1 Data'])[0]
                inv_Ltime = inv_comm.strftime('%m/%d/%y | %H:%M')
                if inv_comm > time_date_compare:
                    if all(point[3] <= 1 for point in data):
                        if avg_dcv > 100:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 75)) and cbval == 0 and master_cb_skips_INV_check:
                                var_key = f'{var_name}statusLabel'
                                if var_key in globals():
                                    if globals()[var_key].cget("bg") == 'green':
                                        online_last = last_online(name, r)
                                        messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Inverter Offline, Good DC Voltage | {online_last}")
                                else:
                                    online_last = last_online(name, r)
                                    messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Inverter Offline, Good DC Voltage | {online_last}")

                            globals()[f'{var_name}meterkWLabel'].config(text="X✓", bg='orange')
                        else:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 75)) and cbval == 0 and master_cb_skips_INV_check:
                                var_key = f'{var_name}statusLabel'
                                if var_key in globals():
                                    if globals()[var_key].cget("bg") == 'green':
                                        online_last = last_online(name, r)
                                        messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Inverter Offline, Bad DC Voltage | {online_last}")
                                else:
                                    online_last = last_online(name, r)
                                    messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Inverter Offline, Bad DC Voltage | {online_last}")

                            globals()[f'{var_name}meterkWLabel'].config(text="❌❌", bg='red')
                    else:
                        if check_inv_consecutively_online(point[3] for point in data):
                            globals()[f'{var_name}meterkWLabel'].config(text="✓✓✓", bg='green')
                else:
                    invlbl = globals()[f'{var_name}meterkWLabel'].cget('bg')
                    globals()[f'{var_name}meterkWLabel'].config(bg='pink')
                    if invlbl != 'pink' and cbval == 0 and master_cb_skips_INV_check:
                        var_key = f'{var_name}statusLabel'
                        if var_key in globals():
                            if globals()[var_key].cget("bg") == 'green':
                                messagebox.showerror(parent= alertW, title=f"{name}, Inverter Comms Loss", message=f"INV Comms lost {inv_Ltime} with Inverter {r} at {name}! Please Investigate!")
                        else:
                            messagebox.showerror(parent= alertW, title=f"{name}, Inverter Comms Loss", message=f"INV Comms lost {inv_Ltime} with Inverter {r} at {name}! Please Investigate!")

        else:
            for r in range(1, inverters + 1):
                data = inv_data[f'{name} INV {r} Data']
                current_config = globals()[f'{var_name}inv{r}cb'].cget("bg")
                cbval = globals()[f'{var_name}inv{r}cbval'].get()
                total_dcv = sum(row[4] for row in data)
                avg_dcv = total_dcv / len(data)
                inv_comm = max(comm_data[f'{name} INV {r} Data'])[0]
                inv_Ltime = inv_comm.strftime('%m/%d/%y | %H:%M')
                if inv_comm > time_date_compare:
                    if all(point[3] < 1 for point in data):
                        if avg_dcv > 100:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 75)) and cbval == 0 and master_cb_skips_INV_check:
                                var_key = f'{var_name}statusLabel'
                                if var_key in globals():
                                    if globals()[var_key].cget("bg") == 'green':
                                        online_last = last_online(name, r)
                                        messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Inverter {r} Offline, Good DC Voltage | {online_last}")
                                else:
                                    online_last = last_online(name, r)
                                    messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Inverter {r} Offline, Good DC Voltage | {online_last}")

                            globals()[f'{var_name}inv{r}cb'].config(bg='orange')
                        else:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 75)) and cbval == 0 and master_cb_skips_INV_check:
                                var_key = f'{var_name}statusLabel'
                                if var_key in globals():
                                    if globals()[var_key].cget("bg") == 'green':
                                        online_last = last_online(name, r)
                                        messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Inverter {r} Offline, Bad DC Voltage | {online_last}")
                                else:
                                    online_last = last_online(name, r)
                                    messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Inverter {r} Offline, Bad DC Voltage | {online_last}")

                            globals()[f'{var_name}inv{r}cb'].config(bg='red')
                    else:
                        if check_inv_consecutively_online(point[3] for point in data):
                            globals()[f'{var_name}inv{r}cb'].config(bg='green')
                else:
                    invlbl = globals()[f'{var_name}inv{r}cb'].cget('bg')
                    globals()[f'{var_name}inv{r}cb'].config(bg='pink')
                    if invlbl != 'pink' and cbval == 0 and master_cb_skips_INV_check:
                        var_key = f'{var_name}statusLabel'
                        if var_key in globals():
                            if globals()[var_key].cget("bg") == 'green':
                                messagebox.showerror(parent= alertW, title=f"{name}, Inverter Comms Loss", message=f"INV Comms lost {inv_Ltime} with Inverter {r} at {name}! Please Investigate!")
                        else:
                            messagebox.showerror(parent= alertW, title=f"{name}, Inverter Comms Loss", message=f"INV Comms lost {inv_Ltime} with Inverter {r} at {name}! Please Investigate!")

    dbconnection.close()


    def allinv_message_update(num, state):
        with open(f"C:\\Users\\OMOPS\\OneDrive - Narenco\\Documents\\APISiteStat\\Site {num} All INV Msg Stat.txt", "w+") as outfile:
                outfile.write(str(state))

    def allinv_message_check(num):
        try:
            with open(f"C:\\Users\\OMOPS\\OneDrive - Narenco\\Documents\\APISiteStat\\Site {num} All INV Msg Stat.txt", "r+") as rad:
                allinvstat = rad.read()
                return allinvstat
        except Exception as errorr:
            messagebox.showerror(parent= alertW, message= errorr, title= f"Error Reading Site {num} txt file")
            return '1'


    # Post Update Status of Inverters
    poststatus_all = {}
    #Retireve Current INV status's and store in lists

    for site_info in master_List_Sites:
        name, inverters, var_name, custid = site_info
        l = []
        if name != "CDIA":
            for i in range(1, inverters + 1):
                checkbox_var = globals()[f'{var_name}inv{i}cbval']
                if not checkbox_var.get():
                    config_color = globals()[f'{var_name}inv{i}cb'].cget("bg")
                    l.append(config_color)
            poststatus_all[f'{var_name}'] = l
    #ic(poststatus_all['vanburen'])
    for index, site_info in enumerate(master_List_Sites):
        name, inverters, var_name, custid = site_info
        if name != "CDIA":
            master_cb_skips_INV_checks = True if globals()[f'{var_name}metercbval'].get() == 0 else False
            if poststatus_all[f'{var_name}']:
                if master_cb_skips_INV_checks and all(status in ['red', 'orange', 'pink'] for status in poststatus_all[f'{var_name}']):
                    #Reasons we want to ignore all the Inverters showing offline
                    if allinv_message_check(index + 1) == '1':
                        if ((POA_data[f'{name} POA Data'][0] > 250 and begin) or (h_tm_now >= 10 and POA_data[f'{name} POA Data'][0] > 75)):
                            print(f'{name} Past', status_all[f'{var_name}'])
                            messagebox.showerror(parent= alertW, title= f"{name}", message= f"All Inverters Offline, Please Investigate!")
                            stat = 0
                            allinv_message_update(index + 1, stat)
                else:
                    stat = 1
                    if allinv_message_check(index + 1) == "0":
                        print(f'{name} Trigger Error', poststatus_all[f'{var_name}'])
                        allinv_message_update(index + 1, stat)  



    def compare_lists(site, before, after):
        #Comapres 2 lists of sites inverters to see what remains online
        changed_indices = []  # List to store indices of changed items
        
        # First, identify any change from not "✓" to "✓"
        changes_detected = any(before_item != "green" and after_item == "green" for before_item, after_item in zip(before, after))
        
        if changes_detected:
            # If changes detected, then identify all items that remain "not ✓"
            changed_indices = [i + 1 for i, item in enumerate(after) if item != "green"]
        
        if changed_indices:
            late_starts = ', '.join(str(x) for x in changed_indices)
            messagebox.showinfo(parent=alertW, title=site, message=f"Some Inverters just came Online. Inverters: {late_starts} remain Offline.")
    
    
    
    #Comapres all lists of sites inverters to see what remains online
    for site_info in master_List_Sites:
        name, inverters, var_name, custid = site_info
        if int(globals()[f'{var_name}POAcb'].cget("text")) > 100:
            if name != "CDIA":
                compare_lists(name, status_all[f'{var_name}'], poststatus_all[f'{var_name}'])

    update_data_finish = ty.perf_counter()
    print("Update Data Time (secs):", round(update_data_finish - update_data_start, 2))
    global gui_update_timer
    target_time = time(8, 30)
    if timecurrent.time() < target_time:
        gui_update_timer = PausableTimer(300, db_to_dict)
        gui_update_timer.start()
    else:
        gui_update_timer = PausableTimer(60, db_to_dict)
        gui_update_timer.start()

    underperformance_check_button.config(state=NORMAL)
    notes_button.config(state=NORMAL)





def underperformance_data():
    gui_update_timer.pause()
    connect_db()

    
    timecheck = datetime.now()
    # Prompt user for the number of days ago
    selected_days_ago = simpledialog.askinteger("Input", "Enter number of days ago for Data analysis, 0 = today:", parent=alertW)

    # Calculate the date based on the selected days ago
    date_to_query = datetime.now() - timedelta(days=selected_days_ago)

    # Format the date for SQL query
    formatted_date = date_to_query.strftime('%m/%d/%Y')

    if timecheck.hour <= 14 and selected_days_ago == 0:
        messagebox.showinfo(parent= alertW, message= "Must be after 3pm to select today", title= "Exiting Performance Analysis")
        return
    else: 
        underperformance_data = {}
        for table in tables:
            table_name = table.table_name
            if "INV" in table_name:
                c.execute(f"""
                SELECT [kW] 
                FROM [{table_name}] 
                WHERE [kW] NOT IN (0, 1) AND [Date & Time] >= DATEADD('h', 11, ?) AND [Date & Time] <= DATEADD('h', 15, ?)""", (formatted_date, formatted_date))
                invkw_rows = c.fetchall()
                underperformance_data[table_name] = invkw_rows

        
        for site, inv, var, custid in master_List_Sites:
            if site != "Duplin":
                for i in range(1, inv + 1):
                    globals()[f'{var}inv{i}daykw'] = underperformance_data[f'{site} INV {i} Data']
                    globals()[f'{var}inv{i}daykwavg'] = np.mean(globals()[f'{var}inv{i}daykw'])
            else:
                for i in range(1, 4):
                    globals()[f'duplininv{i}daykw'] = underperformance_data[f'Duplin Central INV {i} Data']
                    globals()[f'duplininv{i}daykwavg'] = np.mean(globals()[f'duplininv{i}daykw'])
                for i in range(1, 19):
                    globals()[f'duplinsinv{i}daykw'] = underperformance_data[f'Duplin String INV {i} Data']
                    globals()[f'duplinsinv{i}daykwavg'] = np.mean(globals()[f'duplinsinv{i}daykw'])


        bluebirddaykwList = [(bluebirdinv1daykwavg, "1"), (bluebirdinv2daykwavg, "2"), (bluebirdinv3daykwavg, "3"), (bluebirdinv4daykwavg, "4"), (bluebirdinv5daykwavg, "5"), (bluebirdinv6daykwavg, "6"), (bluebirdinv7daykwavg, "7"), (bluebirdinv8daykwavg, "8"), (bluebirdinv9daykwavg, "9"), (bluebirdinv10daykwavg, "10"), (bluebirdinv11daykwavg, "11"), (bluebirdinv12daykwavg, "12"), (bluebirdinv13daykwavg, "13"), (bluebirdinv14daykwavg, "14"), (bluebirdinv15daykwavg, "15"), (bluebirdinv16daykwavg, "16"), (bluebirdinv17daykwavg, "17"), (bluebirdinv18daykwavg, "18"), (bluebirdinv19daykwavg, "19"), (bluebirdinv20daykwavg, "20"), (bluebirdinv21daykwavg, "21"), (bluebirdinv22daykwavg, "22"), (bluebirdinv23daykwavg, "23"), (bluebirdinv24daykwavg, "24")]
        cardinal96daykwList = [(cardinalinv1daykwavg, "1"), (cardinalinv2daykwavg, "2"), (cardinalinv3daykwavg, "3"), (cardinalinv4daykwavg, "4"), (cardinalinv5daykwavg, "5"), (cardinalinv6daykwavg, "6"), (cardinalinv7daykwavg, "7"), (cardinalinv22daykwavg, "22"), (cardinalinv23daykwavg, "23"), (cardinalinv24daykwavg, "24"), (cardinalinv25daykwavg, "25"), (cardinalinv26daykwavg, "26"), (cardinalinv27daykwavg, "27"), (cardinalinv28daykwavg, "28"), (cardinalinv43daykwavg, "43"), (cardinalinv44daykwavg, "44"), (cardinalinv45daykwavg, "45"), (cardinalinv46daykwavg, "46"), (cardinalinv47daykwavg, "47")]
        cardinal952daykwList = [(cardinalinv8daykwavg, "8"), (cardinalinv9daykwavg, "9"), (cardinalinv10daykwavg, "10"), (cardinalinv11daykwavg, "11"), (cardinalinv12daykwavg, "12"), (cardinalinv13daykwavg, "13"), (cardinalinv14daykwavg, "14"), (cardinalinv29daykwavg, "29"), (cardinalinv30daykwavg, "30"), (cardinalinv31daykwavg, "31"), (cardinalinv32daykwavg, "32"), (cardinalinv33daykwavg, "33"), (cardinalinv34daykwavg, "34"), (cardinalinv35daykwavg, "35"), (cardinalinv48daykwavg, "48"), (cardinalinv49daykwavg, "49"), (cardinalinv50daykwavg, "50"), (cardinalinv51daykwavg, "51"), (cardinalinv52daykwavg, "52"), (cardinalinv53daykwavg, "53")]
        cardinal944daykwList = [(cardinalinv15daykwavg, "15"), (cardinalinv16daykwavg, "16"), (cardinalinv17daykwavg, "17"), (cardinalinv18daykwavg, "18"), (cardinalinv19daykwavg, "19"), (cardinalinv20daykwavg, "20"), (cardinalinv21daykwavg, "21"), (cardinalinv36daykwavg, "36"), (cardinalinv37daykwavg, "37"), (cardinalinv38daykwavg, "38"), (cardinalinv39daykwavg, "39"), (cardinalinv40daykwavg, "40"), (cardinalinv41daykwavg, "41"), (cardinalinv42daykwavg, "42"), (cardinalinv54daykwavg, "54"), (cardinalinv55daykwavg, "55"), (cardinalinv56daykwavg, "56"), (cardinalinv57daykwavg, "57"), (cardinalinv58daykwavg, "58"), (cardinalinv59daykwavg, "59")]
        cherrydaykwList = [(cherryinv1daykwavg, "1"), (cherryinv2daykwavg, "2"), (cherryinv3daykwavg, "3"), (cherryinv4daykwavg, "4")]
        harrisondaykwList = [(harrisoninv2daykwavg, "2"), (harrisoninv3daykwavg, "3"), (harrisoninv4daykwavg, "4"), (harrisoninv5daykwavg, "5"), (harrisoninv6daykwavg, "6"), (harrisoninv7daykwavg, "7"), (harrisoninv9daykwavg, "9"), (harrisoninv11daykwavg, "11"), (harrisoninv12daykwavg, "12"), (harrisoninv13daykwavg, "13"), (harrisoninv14daykwavg, "14"), (harrisoninv15daykwavg, "15"), (harrisoninv16daykwavg, "16"), (harrisoninv18daykwavg, "18"), (harrisoninv19daykwavg, "19"), (harrisoninv20daykwavg, "20"), (harrisoninv22daykwavg, "22"), (harrisoninv23daykwavg, "23"), (harrisoninv24daykwavg, "24"), (harrisoninv25daykwavg, "25"), (harrisoninv26daykwavg, "26"), (harrisoninv27daykwavg, "27"), (harrisoninv28daykwavg, "28"), (harrisoninv31daykwavg, "31"), (harrisoninv32daykwavg, "32"), (harrisoninv33daykwavg, "33"), (harrisoninv34daykwavg, "34"), (harrisoninv35daykwavg, "35"), (harrisoninv36daykwavg, "36"), (harrisoninv37daykwavg, "37"), (harrisoninv38daykwavg, "38"), (harrisoninv39daykwavg, "39"), (harrisoninv42daykwavg, "42"), (harrisoninv43daykwavg, "43")]
        harrison92daykwList = [(harrisoninv1daykwavg, "1"), (harrisoninv8daykwavg, "8"), (harrisoninv10daykwavg, "10"), (harrisoninv17daykwavg, "17"), (harrisoninv21daykwavg, "21"), (harrisoninv29daykwavg, "29"), (harrisoninv30daykwavg, "30"), (harrisoninv40daykwavg, "40"), (harrisoninv41daykwavg, "41")]
        hayesdaykwList = [(hayesinv1daykwavg, "1"), (hayesinv2daykwavg, "2"), (hayesinv3daykwavg, "3"), (hayesinv4daykwavg, "4"), (hayesinv5daykwavg, "5"), (hayesinv6daykwavg, "6"), (hayesinv7daykwavg, "7"), (hayesinv8daykwavg, "8"), (hayesinv9daykwavg, "9"), (hayesinv10daykwavg, "10"), (hayesinv11daykwavg, "11"), (hayesinv12daykwavg, "12"), (hayesinv13daykwavg, "13"), (hayesinv14daykwavg, "14"), (hayesinv15daykwavg, "15"), (hayesinv16daykwavg, "16"), (hayesinv17daykwavg, "17"), (hayesinv19daykwavg, "19"), (hayesinv20daykwavg, "20"), (hayesinv21daykwavg, "21"), (hayesinv23daykwavg, "23"), (hayesinv24daykwavg, "24"), (hayesinv25daykwavg, "25"), (hayesinv26daykwavg, "26")]
        hayes96daykwList = [(hayesinv22daykwavg, "22"), (hayesinv18daykwavg, "18")]
        hickorydaykwList = [(hickoryinv1daykwavg, "1"), (hickoryinv2daykwavg, "2")]
        vanburendaykwList = [(vanbureninv7daykwavg, "7"), (vanbureninv8daykwavg, "8"), (vanbureninv9daykwavg, "9"), (vanbureninv10daykwavg, "10"), (vanbureninv11daykwavg, "11"), (vanbureninv12daykwavg, "12"), (vanbureninv13daykwavg, "13"), (vanbureninv14daykwavg, "14"), (vanbureninv15daykwavg, "15"), (vanbureninv16daykwavg, "16"), (vanbureninv17daykwavg, "17")]
        vanburen93daykwList = [(vanbureninv1daykwavg, "1"), (vanbureninv2daykwavg, "2"), (vanbureninv3daykwavg, "3"), (vanbureninv4daykwavg, "4"), (vanbureninv5daykwavg, "5"), (vanbureninv6daykwavg, "6")]
        violetdaykwList = [(violetinv1daykwavg, "1"), (violetinv2daykwavg, "2")]
        wellonsdaykwList = [(wellonsinv1daykwavg, "1-1"), (wellonsinv2daykwavg, "1-2"), (wellonsinv3daykwavg, "2-1"), (wellonsinv4daykwavg, "2-2"), (wellonsinv5daykwavg, "3-1"), (wellonsinv6daykwavg, "3-2")]
        bishopvilleIIdaykwList = [(bishopvilleIIinv6daykwavg, "1-6"), (bishopvilleIIinv7daykwavg, "1-7"), (bishopvilleIIinv8daykwavg, "1-8"), (bishopvilleIIinv9daykwavg, "1-9"), (bishopvilleIIinv10daykwavg, "2-1"), (bishopvilleIIinv13daykwavg, "2-4"),  (bishopvilleIIinv15daykwavg, "2-6"),  (bishopvilleIIinv19daykwavg, "3-1"), (bishopvilleIIinv20daykwavg, "3-2"), (bishopvilleIIinv21daykwavg, "3-3"), (bishopvilleIIinv22daykwavg, "3-4"), (bishopvilleIIinv23daykwavg, "3-5"),  (bishopvilleIIinv26daykwavg, "3-8"), (bishopvilleIIinv27daykwavg, "3-9"), (bishopvilleIIinv28daykwavg, "4-1"), (bishopvilleIIinv29daykwavg, "4-2"), (bishopvilleIIinv30daykwavg, "4-3"), (bishopvilleIIinv32daykwavg, "4-5"),  (bishopvilleIIinv34daykwavg, "4-7")]
        bishopvilleII34strdaykwList = [(bishopvilleIIinv1daykwavg, "1-1"), (bishopvilleIIinv2daykwavg, "1-2"), (bishopvilleIIinv3daykwavg, "1-3"), (bishopvilleIIinv4daykwavg, "1-4"), (bishopvilleIIinv5daykwavg, "1-5"), (bishopvilleIIinv11daykwavg, "2-2"), (bishopvilleIIinv12daykwavg, "2-3"), (bishopvilleIIinv14daykwavg, "2-5"), (bishopvilleIIinv16daykwavg, "2-7"), (bishopvilleIIinv17daykwavg, "2-8"), (bishopvilleIIinv18daykwavg, "2-9"), (bishopvilleIIinv31daykwavg, "4-4"), (bishopvilleIIinv33daykwavg, "4-6"), (bishopvilleIIinv35daykwavg, "4-8"), (bishopvilleIIinv36daykwavg, "4-9")]
        bishopvilleII36strdaykwList = [(bishopvilleIIinv24daykwavg, "3-6"), (bishopvilleIIinv25daykwavg, "3-7")]
        hicksondaykwList = [(hicksoninv7daykwavg, "7"), (hicksoninv8daykwavg, "8"), (hicksoninv9daykwavg, "9"), (hicksoninv12daykwavg, "12"), (hicksoninv13daykwavg, "13"), (hicksoninv14daykwavg, "14"), (hicksoninv15daykwavg, "15"), (hicksoninv16daykwavg, "16")]
        hickson17strdaykwList = [(hicksoninv1daykwavg, "1"), (hicksoninv2daykwavg, "2"), (hicksoninv3daykwavg, "3"), (hicksoninv4daykwavg, "4"), (hicksoninv5daykwavg, "5"), (hicksoninv6daykwavg, "6"), (hicksoninv10daykwavg, "10"), (hicksoninv11daykwavg, "11")]
        jeffersondaykwList = [(jeffersoninv5daykwavg, "1-5"),  (jeffersoninv7daykwavg, "1-7"), (jeffersoninv8daykwavg, "1-8"), (jeffersoninv9daykwavg, "1-9"), (jeffersoninv10daykwavg, "1-10"), (jeffersoninv11daykwavg, "1-11"), (jeffersoninv12daykwavg, "1-12"), (jeffersoninv15daykwavg, "1-15"), (jeffersoninv16daykwavg, "1-16"), (jeffersoninv19daykwavg, "2-3"), (jeffersoninv24daykwavg, "2-8"), (jeffersoninv26daykwavg, "2-10"), (jeffersoninv27daykwavg, "2-11"), (jeffersoninv28daykwavg, "2-12"), (jeffersoninv29daykwavg, "2-13"), (jeffersoninv30daykwavg, "2-14"), (jeffersoninv31daykwavg, "2-15"), (jeffersoninv32daykwavg, "2-16"), (jeffersoninv33daykwavg, "3-1"), (jeffersoninv34daykwavg, "3-2"), (jeffersoninv35daykwavg, "3-3"), (jeffersoninv36daykwavg, "3-4"), (jeffersoninv37daykwavg, "3-5"), (jeffersoninv38daykwavg, "3-6"), (jeffersoninv39daykwavg, "3-7"),  (jeffersoninv48daykwavg, "3-16"), (jeffersoninv57daykwavg, "4-9"), (jeffersoninv58daykwavg, "4-10"), (jeffersoninv59daykwavg, "4-11"), (jeffersoninv60daykwavg, "4-12"), (jeffersoninv61daykwavg, "4-13"), (jeffersoninv62daykwavg, "4-14"), (jeffersoninv63daykwavg, "4-15"), (jeffersoninv64daykwavg, "4-16")]
        jefferson18strdaykwList = [(jeffersoninv1daykwavg, "1-1"), (jeffersoninv2daykwavg, "1-2"), (jeffersoninv3daykwavg, "1-3"), (jeffersoninv4daykwavg, "1-4"), (jeffersoninv6daykwavg, "1-6"), (jeffersoninv13daykwavg, "1-13"), (jeffersoninv14daykwavg, "1-14"), (jeffersoninv17daykwavg, "2-1"), (jeffersoninv18daykwavg, "2-2"), (jeffersoninv20daykwavg, "2-4"), (jeffersoninv21daykwavg, "2-5"), (jeffersoninv22daykwavg, "2-6"), (jeffersoninv23daykwavg, "2-7"), (jeffersoninv25daykwavg, "2-9"), (jeffersoninv40daykwavg, "3-8"), (jeffersoninv41daykwavg, "3-9"), (jeffersoninv42daykwavg, "3-10"), (jeffersoninv43daykwavg, "3-11"), (jeffersoninv44daykwavg, "3-12"),  (jeffersoninv45daykwavg, "3-13"), (jeffersoninv46daykwavg, "3-14"), (jeffersoninv47daykwavg, "3-15"), (jeffersoninv49daykwavg, "4-1"), (jeffersoninv50daykwavg, "4-2"), (jeffersoninv51daykwavg, "4-3"), (jeffersoninv52daykwavg, "4-4"), (jeffersoninv53daykwavg, "4-5"), (jeffersoninv54daykwavg, "4-6"), (jeffersoninv55daykwavg, "4-7"), (jeffersoninv56daykwavg, "4-8")]
        marshalldaykwList = [(marshallinv1daykwavg, "1"), (marshallinv2daykwavg, "2"), (marshallinv3daykwavg, "3"), (marshallinv4daykwavg, "4"), (marshallinv5daykwavg, "5"), (marshallinv6daykwavg, "6"), (marshallinv7daykwavg, "7"), (marshallinv8daykwavg, "8"), (marshallinv9daykwavg, "9"), (marshallinv10daykwavg, "10"), (marshallinv11daykwavg, "11"), (marshallinv12daykwavg, "12"), (marshallinv13daykwavg, "13"), (marshallinv14daykwavg, "14"), (marshallinv15daykwavg, "15"), (marshallinv16daykwavg, "16")]
        ogburndaykwList = [(ogburninv1daykwavg, "1"), (ogburninv2daykwavg, "2"), (ogburninv3daykwavg, "3"), (ogburninv4daykwavg, "4"), (ogburninv5daykwavg, "5"), (ogburninv6daykwavg, "6"), (ogburninv7daykwavg, "7"), (ogburninv8daykwavg, "8"), (ogburninv9daykwavg, "9"), (ogburninv10daykwavg, "10"), (ogburninv11daykwavg, "11"), (ogburninv12daykwavg, "12"), (ogburninv13daykwavg, "13"), (ogburninv14daykwavg, "14"), (ogburninv15daykwavg, "15"), (ogburninv16daykwavg, "16")]
        tedderdaykwList = [(tedderinv5daykwavg, "5"), (tedderinv6daykwavg, "6"), (tedderinv7daykwavg, "7"), (tedderinv9daykwavg, "9"), (tedderinv10daykwavg, "10"), (tedderinv11daykwavg, "11"), (tedderinv12daykwavg, "12"), (tedderinv13daykwavg, "13"), (tedderinv14daykwavg, "14")]
        tedder15strdaykwList = [(tedderinv1daykwavg, "1"), (tedderinv2daykwavg, "2"), (tedderinv3daykwavg, "3"), (tedderinv4daykwavg, "4"), (tedderinv8daykwavg, "8"), (tedderinv15daykwavg, "15"), (tedderinv16daykwavg, "16")]
        thunderheaddaykwList = [(thunderheadinv1daykwavg, "1"), (thunderheadinv2daykwavg, "2"), (thunderheadinv3daykwavg, "3"), (thunderheadinv4daykwavg, "4"), (thunderheadinv5daykwavg, "5"), (thunderheadinv6daykwavg, "6"), (thunderheadinv7daykwavg, "7"), (thunderheadinv8daykwavg, "8"), (thunderheadinv9daykwavg, "9"), (thunderheadinv10daykwavg, "10"), (thunderheadinv11daykwavg, "11"), (thunderheadinv12daykwavg, "12"), (thunderheadinv14daykwavg, "14"), (thunderheadinv16daykwavg, "16")]
        thunderhead14strdaykwList = [(thunderheadinv15daykwavg, "15"), (thunderheadinv13daykwavg, "13")]
        bulloch1adaykwList = [(bulloch1ainv7daykwavg, "7"), (bulloch1ainv8daykwavg, "8"), (bulloch1ainv9daykwavg, "9"), (bulloch1ainv10daykwavg, "10"), (bulloch1ainv11daykwavg, "11"), (bulloch1ainv12daykwavg, "12"), (bulloch1ainv13daykwavg, "13"), (bulloch1ainv14daykwavg, "14"), (bulloch1ainv15daykwavg, "15"), (bulloch1ainv16daykwavg, "16"), (bulloch1ainv17daykwavg, "17"), (bulloch1ainv18daykwavg, "18"), (bulloch1ainv19daykwavg, "19"), (bulloch1ainv20daykwavg, "20"), (bulloch1ainv21daykwavg, "21"), (bulloch1ainv22daykwavg, "22"), (bulloch1ainv23daykwavg, "23"), (bulloch1ainv24daykwavg, "24")]
        bulloch1a10strdaykwList = [(bulloch1ainv1daykwavg, "1"), (bulloch1ainv2daykwavg, "2"), (bulloch1ainv3daykwavg, "3"), (bulloch1ainv4daykwavg, "4"), (bulloch1ainv5daykwavg, "5"), (bulloch1ainv6daykwavg, "6")]
        bulloch1bdaykwList = [(bulloch1binv2daykwavg, "2"), (bulloch1binv3daykwavg, "3"), (bulloch1binv4daykwavg, "4"), (bulloch1binv5daykwavg, "5"), (bulloch1binv6daykwavg, "6"), (bulloch1binv7daykwavg, "7"), (bulloch1binv8daykwavg, "8"), (bulloch1binv13daykwavg, "13"), (bulloch1binv14daykwavg, "14"), (bulloch1binv15daykwavg, "15"), (bulloch1binv16daykwavg, "16"), (bulloch1binv18daykwavg, "18"), (bulloch1binv19daykwavg, "19"), (bulloch1binv20daykwavg, "20"), (bulloch1binv21daykwavg, "21"), (bulloch1binv22daykwavg, "22"), (bulloch1binv23daykwavg, "23"), (bulloch1binv24daykwavg, "24")]
        bulloch1b10strdaykwList = [(bulloch1binv1daykwavg, "1"), (bulloch1binv9daykwavg, "9"), (bulloch1binv10daykwavg, "10"), (bulloch1binv11daykwavg, "11"), (bulloch1binv12daykwavg, "12"), (bulloch1binv17daykwavg, "17")]
        grayfoxdaykwList = [(grayfoxinv1daykwavg, "1-1"), (grayfoxinv2daykwavg, "1-2"), (grayfoxinv3daykwavg, "1-3"), (grayfoxinv4daykwavg, "1-4"), (grayfoxinv5daykwavg, "1-5"), (grayfoxinv6daykwavg, "1-6"), (grayfoxinv7daykwavg, "1-7"), (grayfoxinv8daykwavg, "1-8"), (grayfoxinv9daykwavg, "1-9"), (grayfoxinv10daykwavg, "1-10"), (grayfoxinv11daykwavg, "1-11"), (grayfoxinv12daykwavg, "1-12"), (grayfoxinv13daykwavg, "1-13"), (grayfoxinv14daykwavg, "1-14"), (grayfoxinv15daykwavg, "1-15"), (grayfoxinv16daykwavg, "1-16"), (grayfoxinv17daykwavg, "1-17"), (grayfoxinv18daykwavg, "1-18"), (grayfoxinv19daykwavg, "1-19"), (grayfoxinv20daykwavg, "1-20"), (grayfoxinv21daykwavg, "2-1"), (grayfoxinv22daykwavg, "2-2"), (grayfoxinv23daykwavg, "2-3"), (grayfoxinv24daykwavg, "2-4"), (grayfoxinv25daykwavg, "2-5"), (grayfoxinv26daykwavg, "2-6"), (grayfoxinv27daykwavg, "2-7"), (grayfoxinv28daykwavg, "2-8"), (grayfoxinv29daykwavg, "2-9"), (grayfoxinv30daykwavg, "3-1"), (grayfoxinv31daykwavg, "3-11"), (grayfoxinv32daykwavg, "3-12"), (grayfoxinv33daykwavg, "3-13"), (grayfoxinv34daykwavg, "3-14"), (grayfoxinv35daykwavg, "3-15"), (grayfoxinv36daykwavg, "3-16"), (grayfoxinv37daykwavg, "3-17"), (grayfoxinv38daykwavg, "3-18"), (grayfoxinv39daykwavg, "3-19"), (grayfoxinv40daykwavg, "3-20")]
        hardingdaykwList = [(hardinginv4daykwavg, "4"), (hardinginv5daykwavg, "5"), (hardinginv6daykwavg, "6"),  (hardinginv10daykwavg, "10"), (hardinginv11daykwavg, "11"), (hardinginv12daykwavg, "12"), (hardinginv13daykwavg, "13"), (hardinginv14daykwavg, "14"), (hardinginv15daykwavg, "15"),  (hardinginv17daykwavg, "17"), (hardinginv18daykwavg, "18"), (hardinginv19daykwavg, "19")]
        harding12strdaykwList = [(hardinginv1daykwavg, "1"), (hardinginv2daykwavg, "2"), (hardinginv3daykwavg, "3"), (hardinginv7daykwavg, "7"), (hardinginv8daykwavg, "8"), (hardinginv9daykwavg, "9"), (hardinginv16daykwavg, "16"), (hardinginv20daykwavg, "20"), (hardinginv21daykwavg, "21"), (hardinginv22daykwavg, "22"), (hardinginv23daykwavg, "23"), (hardinginv24daykwavg, "24")]
        mcLeandaykwList = [ (mcLeaninv2daykwavg, "2"), (mcLeaninv3daykwavg, "3"), (mcLeaninv4daykwavg, "4"), (mcLeaninv5daykwavg, "5"), (mcLeaninv6daykwavg, "6"), (mcLeaninv7daykwavg, "7"), (mcLeaninv8daykwavg, "8"), (mcLeaninv9daykwavg, "9"), (mcLeaninv10daykwavg, "10"), (mcLeaninv11daykwavg, "11"), (mcLeaninv12daykwavg, "12"), (mcLeaninv13daykwavg, "13"), (mcLeaninv14daykwavg, "14"), (mcLeaninv15daykwavg, "15"), (mcLeaninv16daykwavg, "16"), (mcLeaninv18daykwavg, "18"), (mcLeaninv20daykwavg, "20"),  (mcLeaninv22daykwavg, "22"),  (mcLeaninv24daykwavg, "24"), (mcLeaninv25daykwavg, "25"), (mcLeaninv26daykwavg, "26"), (mcLeaninv30daykwavg, "30")]
        mcLean10strdaykwList = [(mcLeaninv1daykwavg, "1"), (mcLeaninv17daykwavg, "17"), (mcLeaninv19daykwavg, "19"), (mcLeaninv21daykwavg, "21"), (mcLeaninv23daykwavg, "23"), (mcLeaninv27daykwavg, "27"), (mcLeaninv28daykwavg, "28"), (mcLeaninv29daykwavg, "29"), (mcLeaninv31daykwavg, "31"), (mcLeaninv32daykwavg, "32"), (mcLeaninv33daykwavg, "33"), (mcLeaninv34daykwavg, "34"), (mcLeaninv35daykwavg, "35"), (mcLeaninv36daykwavg, "36"), (mcLeaninv37daykwavg, "37"), (mcLeaninv38daykwavg, "38"), (mcLeaninv39daykwavg, "39"), (mcLeaninv40daykwavg, "40")]
        richmonddaykwList = [(richmondinv1daykwavg, "1"), (richmondinv2daykwavg, "2"), (richmondinv3daykwavg, "3"), (richmondinv4daykwavg, "4"), (richmondinv5daykwavg, "5"), (richmondinv6daykwavg, "6"), (richmondinv7daykwavg, "7"), (richmondinv11daykwavg, "11"), (richmondinv12daykwavg, "12"), (richmondinv13daykwavg, "13"), (richmondinv14daykwavg, "14"), (richmondinv15daykwavg, "15"), (richmondinv16daykwavg, "16"), (richmondinv17daykwavg, "17"), (richmondinv18daykwavg, "18"), (richmondinv19daykwavg, "19"), (richmondinv20daykwavg, "20"), (richmondinv21daykwavg, "21")]
        richmond10strdaykwList = [(richmondinv8daykwavg, "8"), (richmondinv9daykwavg, "9"), (richmondinv10daykwavg, "10"), (richmondinv22daykwavg, "22"), (richmondinv23daykwavg, "23"), (richmondinv24daykwavg, "24")]  
        shorthorndaykwList = [(shorthorninv1daykwavg, "1"), (shorthorninv2daykwavg, "2"), (shorthorninv3daykwavg, "3"), (shorthorninv4daykwavg, "4"), (shorthorninv5daykwavg, "5"), (shorthorninv6daykwavg, "6"), (shorthorninv7daykwavg, "7"), (shorthorninv8daykwavg, "8"), (shorthorninv9daykwavg, "9"), (shorthorninv10daykwavg, "10"), (shorthorninv11daykwavg, "11"), (shorthorninv12daykwavg, "12"), (shorthorninv13daykwavg, "13"), (shorthorninv14daykwavg, "14"), (shorthorninv15daykwavg, "15"), (shorthorninv16daykwavg, "16"), (shorthorninv17daykwavg, "17"), (shorthorninv18daykwavg, "18"), (shorthorninv19daykwavg, "19"), (shorthorninv20daykwavg, "20"), (shorthorninv22daykwavg, "22"), (shorthorninv23daykwavg, "23"), (shorthorninv24daykwavg, "24"),  (shorthorninv26daykwavg, "26"), (shorthorninv27daykwavg, "27"), (shorthorninv28daykwavg, "28"),  (shorthorninv32daykwavg, "32"), (shorthorninv33daykwavg, "33"),  (shorthorninv37daykwavg, "37"), (shorthorninv38daykwavg, "38"), (shorthorninv39daykwavg, "39"), (shorthorninv40daykwavg, "40"), (shorthorninv41daykwavg, "41"), (shorthorninv42daykwavg, "42"), (shorthorninv43daykwavg, "43"), (shorthorninv45daykwavg, "45"), (shorthorninv46daykwavg, "46"), (shorthorninv47daykwavg, "47"), (shorthorninv48daykwavg, "48"), (shorthorninv52daykwavg, "52"), (shorthorninv53daykwavg, "53"), (shorthorninv57daykwavg, "57"), (shorthorninv58daykwavg, "58"), (shorthorninv59daykwavg, "59"), (shorthorninv60daykwavg, "60"), (shorthorninv61daykwavg, "61"), (shorthorninv62daykwavg, "62"), (shorthorninv63daykwavg, "63"), (shorthorninv64daykwavg, "64"), (shorthorninv65daykwavg, "65"), (shorthorninv66daykwavg, "66")]
        shorthorn13strdaykwList = [(shorthorninv21daykwavg, "21"), (shorthorninv25daykwavg, "25"), (shorthorninv29daykwavg, "29"), (shorthorninv30daykwavg, "30"), (shorthorninv31daykwavg, "31"), (shorthorninv34daykwavg, "34"), (shorthorninv35daykwavg, "35"), (shorthorninv36daykwavg, "36"),  (shorthorninv44daykwavg, "44"), (shorthorninv49daykwavg, "49"), (shorthorninv50daykwavg, "50"), (shorthorninv51daykwavg, "51"), (shorthorninv54daykwavg, "54"), (shorthorninv55daykwavg, "55"), (shorthorninv56daykwavg, "56"), (shorthorninv67daykwavg, "67"), (shorthorninv68daykwavg, "68"), (shorthorninv69daykwavg, "69"), (shorthorninv70daykwavg, "70"), (shorthorninv71daykwavg, "71"), (shorthorninv72daykwavg, "72")]
        sunflowerdaykwList = [(sunflowerinv3daykwavg, "3"), (sunflowerinv4daykwavg, "4"), (sunflowerinv5daykwavg, "5"), (sunflowerinv6daykwavg, "6"), (sunflowerinv7daykwavg, "7"), (sunflowerinv8daykwavg, "8"), (sunflowerinv9daykwavg, "9"), (sunflowerinv10daykwavg, "10"), (sunflowerinv11daykwavg, "11"), (sunflowerinv12daykwavg, "12"), (sunflowerinv13daykwavg, "13"), (sunflowerinv14daykwavg, "14"), (sunflowerinv15daykwavg, "15"), (sunflowerinv16daykwavg, "16"), (sunflowerinv17daykwavg, "17"), (sunflowerinv18daykwavg, "18"), (sunflowerinv19daykwavg, "19"), (sunflowerinv20daykwavg, "20"),  (sunflowerinv34daykwavg, "34"),  (sunflowerinv62daykwavg, "62"), (sunflowerinv63daykwavg, "63"), (sunflowerinv64daykwavg, "64"), (sunflowerinv65daykwavg, "65"), (sunflowerinv66daykwavg, "66"), (sunflowerinv67daykwavg, "67"), (sunflowerinv68daykwavg, "68"), (sunflowerinv69daykwavg, "69"), (sunflowerinv70daykwavg, "70"), (sunflowerinv71daykwavg, "71"), (sunflowerinv72daykwavg, "72"), (sunflowerinv73daykwavg, "73"), (sunflowerinv74daykwavg, "74"), (sunflowerinv75daykwavg, "75"), (sunflowerinv76daykwavg, "76"), (sunflowerinv77daykwavg, "77")]
        sunflower12strdaykwList = [(sunflowerinv1daykwavg, "1"), (sunflowerinv2daykwavg, "2"), (sunflowerinv21daykwavg, "21"), (sunflowerinv22daykwavg, "22"), (sunflowerinv23daykwavg, "23"), (sunflowerinv24daykwavg, "24"), (sunflowerinv25daykwavg, "25"), (sunflowerinv26daykwavg, "26"),  (sunflowerinv27daykwavg, "27"), (sunflowerinv28daykwavg, "28"), (sunflowerinv29daykwavg, "29"), (sunflowerinv30daykwavg, "30"), (sunflowerinv31daykwavg, "31"), (sunflowerinv32daykwavg, "32"),  (sunflowerinv33daykwavg, "33"), (sunflowerinv35daykwavg, "35"), (sunflowerinv36daykwavg, "36"), (sunflowerinv37daykwavg, "37"), (sunflowerinv38daykwavg, "38"), (sunflowerinv39daykwavg, "39"), (sunflowerinv40daykwavg, "40"), (sunflowerinv41daykwavg, "41"), (sunflowerinv42daykwavg, "42"), (sunflowerinv43daykwavg, "43"), (sunflowerinv44daykwavg, "44"), (sunflowerinv45daykwavg, "45"), (sunflowerinv46daykwavg, "46"), (sunflowerinv47daykwavg, "47"), (sunflowerinv48daykwavg, "48"), (sunflowerinv49daykwavg, "49"), (sunflowerinv50daykwavg, "50"), (sunflowerinv51daykwavg, "51"), (sunflowerinv52daykwavg, "52"), (sunflowerinv53daykwavg, "53"), (sunflowerinv54daykwavg, "54"),(sunflowerinv55daykwavg, "55"), (sunflowerinv56daykwavg, "56"), (sunflowerinv57daykwavg, "57"), (sunflowerinv58daykwavg, "58"), (sunflowerinv59daykwavg, "59"), (sunflowerinv60daykwavg, "60"),(sunflowerinv61daykwavg, "61"), (sunflowerinv78daykwavg, "78"), (sunflowerinv79daykwavg, "79"), (sunflowerinv80daykwavg, "80") ]
        upsondaykwList = [(upsoninv1daykwavg, "1"), (upsoninv2daykwavg, "2"), (upsoninv3daykwavg, "3"), (upsoninv4daykwavg, "4"), (upsoninv5daykwavg, "5"), (upsoninv9daykwavg, "9"), (upsoninv10daykwavg, "10"), (upsoninv11daykwavg, "11"), (upsoninv12daykwavg, "12"), (upsoninv13daykwavg, "13"), (upsoninv14daykwavg, "14"), (upsoninv15daykwavg, "15"), (upsoninv16daykwavg, "16"), (upsoninv17daykwavg, "17"), (upsoninv21daykwavg, "21"), (upsoninv22daykwavg, "22"), (upsoninv23daykwavg, "23"), (upsoninv24daykwavg, "24")]
        upson10strdaykwList = [(upsoninv6daykwavg, "6"), (upsoninv7daykwavg, "7"), (upsoninv8daykwavg, "8"), (upsoninv18daykwavg, "18"), (upsoninv19daykwavg, "19"), (upsoninv20daykwavg, "20")]
        warblerdaykwList = [(warblerinv1daykwavg, "1"), (warblerinv2daykwavg, "2"), (warblerinv3daykwavg, "3"), (warblerinv4daykwavg, "4"), (warblerinv5daykwavg, "5"), (warblerinv6daykwavg, "6"), (warblerinv7daykwavg, "7"), (warblerinv8daykwavg, "8"), (warblerinv9daykwavg, "9"), (warblerinv10daykwavg, "10"), (warblerinv11daykwavg, "11"), (warblerinv12daykwavg, "12"), (warblerinv13daykwavg, "13"), (warblerinv14daykwavg, "14"), (warblerinv15daykwavg, "15"), (warblerinv16daykwavg, "16"), (warblerinv17daykwavg, "17"), (warblerinv18daykwavg, "18"), (warblerinv19daykwavg, "19"), (warblerinv20daykwavg, "20"), (warblerinv21daykwavg, "21"), (warblerinv22daykwavg, "22"), (warblerinv23daykwavg, "23"), (warblerinv24daykwavg, "24"), (warblerinv25daykwavg, "25"), (warblerinv26daykwavg, "26"), (warblerinv27daykwavg, "27"), (warblerinv28daykwavg, "28"), (warblerinv29daykwavg, "29"), (warblerinv30daykwavg, "30"), (warblerinv31daykwavg, "31"), (warblerinv32daykwavg, "32")]
        washingtondaykwList = [(washingtoninv4daykwavg, "4"), (washingtoninv5daykwavg, "5"), (washingtoninv6daykwavg, "6"), (washingtoninv7daykwavg, "7"), (washingtoninv8daykwavg, "8"), (washingtoninv9daykwavg, "9"), (washingtoninv10daykwavg, "10"), (washingtoninv11daykwavg, "11"), (washingtoninv12daykwavg, "12"), (washingtoninv15daykwavg, "15"), (washingtoninv16daykwavg, "16"), (washingtoninv17daykwavg, "17"), (washingtoninv18daykwavg, "18"), (washingtoninv19daykwavg, "19"),  (washingtoninv21daykwavg, "21"), (washingtoninv22daykwavg, "22"), (washingtoninv23daykwavg, "23"), (washingtoninv24daykwavg, "24"), (washingtoninv40daykwavg, "40")]
        washington12strdaykwList = [(washingtoninv1daykwavg, "1"), (washingtoninv2daykwavg, "2"), (washingtoninv3daykwavg, "3"), (washingtoninv13daykwavg, "13"), (washingtoninv14daykwavg, "14"), (washingtoninv20daykwavg, "20"), (washingtoninv25daykwavg, "25"), (washingtoninv26daykwavg, "26"), (washingtoninv27daykwavg, "27"), (washingtoninv28daykwavg, "28"), (washingtoninv29daykwavg, "29"), (washingtoninv30daykwavg, "30"), (washingtoninv31daykwavg, "31"), (washingtoninv32daykwavg, "32"), (washingtoninv33daykwavg, "33"), (washingtoninv34daykwavg, "34"), (washingtoninv35daykwavg, "35"), (washingtoninv36daykwavg, "36"), (washingtoninv37daykwavg, "37"), (washingtoninv38daykwavg, "38"), (washingtoninv39daykwavg, "39")]
        whitehalldaykwList = [(whitehallinv1daykwavg, "1"), (whitehallinv3daykwavg, "3"), (whitehallinv4daykwavg, "4"), (whitehallinv5daykwavg, "5"),  (whitehallinv13daykwavg, "13"), (whitehallinv14daykwavg, "14"), (whitehallinv15daykwavg, "15"), (whitehallinv16daykwavg, "16")]
        whitehall13strdaykwList = [(whitehallinv2daykwavg, "2"), (whitehallinv6daykwavg, "6"), (whitehallinv7daykwavg, "7"), (whitehallinv8daykwavg, "8"), (whitehallinv9daykwavg, "9"), (whitehallinv10daykwavg, "10"), (whitehallinv11daykwavg, "11"), (whitehallinv12daykwavg, "12")]
        whitetaildaykwList = [(whitetailinv1daykwavg, "1"), (whitetailinv2daykwavg, "2"), (whitetailinv3daykwavg, "3"), (whitetailinv5daykwavg, "5"), (whitetailinv6daykwavg, "6"), (whitetailinv7daykwavg, "7"), (whitetailinv8daykwavg, "8"), (whitetailinv9daykwavg, "9"), (whitetailinv10daykwavg, "10"), (whitetailinv11daykwavg, "11"), (whitetailinv12daykwavg, "12"),  (whitetailinv22daykwavg, "22"), (whitetailinv23daykwavg, "23"), (whitetailinv24daykwavg, "24"), (whitetailinv25daykwavg, "25"),  (whitetailinv32daykwavg, "32"), (whitetailinv33daykwavg, "33"),  (whitetailinv35daykwavg, "35"), (whitetailinv36daykwavg, "36"), (whitetailinv37daykwavg, "37"), (whitetailinv38daykwavg, "38"), (whitetailinv39daykwavg, "39"), (whitetailinv40daykwavg, "40"), (whitetailinv41daykwavg, "41"), (whitetailinv42daykwavg, "42"),  (whitetailinv49daykwavg, "49"), (whitetailinv50daykwavg, "50"), (whitetailinv51daykwavg, "51"),  (whitetailinv57daykwavg, "57"),  (whitetailinv61daykwavg, "61"), (whitetailinv62daykwavg, "62"), (whitetailinv63daykwavg, "63"), (whitetailinv65daykwavg, "65"), (whitetailinv66daykwavg, "66"), (whitetailinv67daykwavg, "67"), (whitetailinv68daykwavg, "68"), (whitetailinv69daykwavg, "69"), (whitetailinv70daykwavg, "70"), (whitetailinv71daykwavg, "71"), (whitetailinv72daykwavg, "72"), (whitetailinv73daykwavg, "73"), (whitetailinv74daykwavg, "74"), (whitetailinv75daykwavg, "75"), (whitetailinv76daykwavg, "76"), (whitetailinv77daykwavg, "77"), (whitetailinv78daykwavg, "78"), (whitetailinv79daykwavg, "79"), (whitetailinv80daykwavg, "80")]
        whitetail17strdaykwList = [(whitetailinv4daykwavg, "4"), (whitetailinv13daykwavg, "13"), (whitetailinv14daykwavg, "14"), (whitetailinv15daykwavg, "15"), (whitetailinv16daykwavg, "16"), (whitetailinv17daykwavg, "17"), (whitetailinv18daykwavg, "18"), (whitetailinv19daykwavg, "19"), (whitetailinv20daykwavg, "20"), (whitetailinv21daykwavg, "21"), (whitetailinv26daykwavg, "26"), (whitetailinv27daykwavg, "27"), (whitetailinv28daykwavg, "28"), (whitetailinv29daykwavg, "29"), (whitetailinv30daykwavg, "30"), (whitetailinv31daykwavg, "31"), (whitetailinv34daykwavg, "34"), (whitetailinv43daykwavg, "43"), (whitetailinv44daykwavg, "44"), (whitetailinv45daykwavg, "45"), (whitetailinv46daykwavg, "46"), (whitetailinv47daykwavg, "47"), (whitetailinv48daykwavg, "48"), (whitetailinv52daykwavg, "52"), (whitetailinv53daykwavg, "53"), (whitetailinv54daykwavg, "54"), (whitetailinv55daykwavg, "55"), (whitetailinv56daykwavg, "56"), (whitetailinv58daykwavg, "58"), (whitetailinv59daykwavg, "59"), (whitetailinv60daykwavg, "60"), (whitetailinv64daykwavg, "64")]
        conetoedaykwList = [(conetoeinv1daykwavg, "1"), (conetoeinv2daykwavg, "2"), (conetoeinv3daykwavg, "3"), (conetoeinv4daykwavg, "4")]
        duplindaykwList = [(duplinsinv1daykwavg, "1"), (duplinsinv2daykwavg, "2"), (duplinsinv3daykwavg, "3"), (duplinsinv8daykwavg, "4"), (duplinsinv5daykwavg, "5"), (duplinsinv6daykwavg, "6"), (duplinsinv7daykwavg, "7"), (duplinsinv8daykwavg, "8"), (duplinsinv9daykwavg, "9"), (duplinsinv10daykwavg, "10"), (duplinsinv11daykwavg, "11"), (duplinsinv12daykwavg, "12"), (duplinsinv13daykwavg, "13"), (duplinsinv14daykwavg, "14"), (duplinsinv15daykwavg, "15"), (duplinsinv16daykwavg, "16"), (duplinsinv17daykwavg, "17"), (duplinsinv18daykwavg, "18")]
        duplinCentraldaykwList = [(duplininv1daykwavg, "1"), (duplininv2daykwavg, "2"), (duplininv3daykwavg, "3")]
        wayne11000daykwList = [(wayne1inv1daykwavg, "1"), (wayne1inv4daykwavg, "4")]
        wayne1daykwList = [(wayne1inv2daykwavg, "2"), (wayne1inv3daykwavg, "3")]
        wayne21000daykwList = [(wayne2inv3daykwavg, "3"), (wayne2inv4daykwavg, "4")]
        wayne2daykwList = [(wayne2inv1daykwavg, "1"), (wayne2inv2daykwavg, "2")]
        wayne31000daykwList = [(wayne3inv1daykwavg, "1"), (wayne3inv2daykwavg, "2")]
        wayne3daykwList = [(wayne3inv3daykwavg, "3"), (wayne3inv4daykwavg, "4")]
        freightlinedaykwList = [(freightlineinv1daykwavg, "1"), (freightlineinv3daykwavg, "3"), (freightlineinv4daykwavg, "4"), (freightlineinv5daykwavg, "5"), (freightlineinv8daykwavg, "8"), (freightlineinv9daykwavg, "9"), (freightlineinv10daykwavg, "10"), (freightlineinv11daykwavg, "11"), (freightlineinv12daykwavg, "12"), (freightlineinv15daykwavg, "15"), (freightlineinv16daykwavg, "16"), (freightlineinv17daykwavg, "17"), (freightlineinv18daykwavg, "18")]
        freightline66daykwList = [(freightlineinv2daykwavg, "2"), (freightlineinv6daykwavg, "6"), (freightlineinv7daykwavg, "7"), (freightlineinv13daykwavg, "13"), (freightlineinv14daykwavg, "14")]
        hollyswampdaykwList = [(hollyswampinv1daykwavg, "1"), (hollyswampinv2daykwavg, "2"), (hollyswampinv3daykwavg, "3"), (hollyswampinv4daykwavg, "4"), (hollyswampinv5daykwavg, "5"), (hollyswampinv6daykwavg, "6"), (hollyswampinv7daykwavg, "7"), (hollyswampinv8daykwavg, "8"), (hollyswampinv9daykwavg, "9"), (hollyswampinv10daykwavg, "10"), (hollyswampinv11daykwavg, "11"), (hollyswampinv12daykwavg, "12"), (hollyswampinv14daykwavg, "14"), (hollyswampinv16daykwavg, "16")]
        hollyswamp18strdaykwList = [(hollyswampinv15daykwavg, "15"), (hollyswampinv13daykwavg, "13")]
        pgdaykwList = [(pginv7daykwavg, "7"), (pginv8daykwavg, "8"), (pginv9daykwavg, "9"), (pginv10daykwavg, "10"), (pginv11daykwavg, "11"), (pginv12daykwavg, "12"), (pginv13daykwavg, "13"), (pginv14daykwavg, "14"), (pginv15daykwavg, "15"), (pginv16daykwavg, "16"), (pginv17daykwavg, "17"), (pginv18daykwavg, "18")]
        pg66daykwList = [(pginv1daykwavg, "1"), (pginv2daykwavg, "2"), (pginv3daykwavg, "3"), (pginv4daykwavg, "4"), (pginv5daykwavg, "5"), (pginv6daykwavg, "6")]

        site_under_Lists = {
            "Duplin Central Inverters": duplinCentraldaykwList,
            "Bulloch 1A 11 String Inverters": bulloch1adaykwList,
            "Bulloch 1A 10 String Inverters": bulloch1a10strdaykwList,
            "Bulloch 1B 11 String Inverters": bulloch1bdaykwList,
            "Bulloch 1B 10 String Inverters": bulloch1b10strdaykwList,
            "Gray Fox Inverters": grayfoxdaykwList,
            #Is seperate groups but I don't know how to split them based on As Builts

            "Harding 13 String Inverters": hardingdaykwList,
            "Harding 12 String Inverters": harding12strdaykwList,
            "McLean Inverters": mcLeandaykwList,
            "McLean 10 String Inverters": mcLean10strdaykwList,
            "Richmond 11 String Inverters": richmonddaykwList,
            "Richmond 10 String Inverters": richmond10strdaykwList,
            "Shorthorn 12 String Inverters": shorthorndaykwList,
            "Shorthorn 13 String Inverters": shorthorn13strdaykwList,
            "Sunflower 13 String Inverters": sunflowerdaykwList,
            "Sunflower 12 String Inverters": sunflower12strdaykwList,
            "Upson 11 String Inverters": upsondaykwList,
            "Upson 10 String Inverters": upson10strdaykwList,
            "WarblerInverters": warblerdaykwList,
            "Washington 13 String Inverters": washingtondaykwList,
            "Washington 12 String Inverters": washington12strdaykwList,
            "Whitehall 12 String Inverters": whitehalldaykwList,
            "Whitehall 13 String Inverters": whitehall13strdaykwList,
            "Whitetail 16 String Inverters": whitetaildaykwList,
            "Whitetail 17 String Inverters": whitetail17strdaykwList,
            "Conetoe Inverters": conetoedaykwList,
            "Duplin String Inverters": duplindaykwList,
            "Wayne 1 Inverters": wayne1daykwList,
            "Wayne 1 1000's": wayne11000daykwList, 
            "Wayne 2 Inverters": wayne2daykwList,
            "Wayne 2 1000's": wayne21000daykwList, 
            "Wayne 3 Inverters": wayne3daykwList,
            "Wayne 3 1000's": wayne31000daykwList, 
            "Freight Line 100% Inverters": freightlinedaykwList,
            "Freight Line 66% Inverters": freightline66daykwList,
            "Holly Swamp 19 String Inverters": hollyswampdaykwList,
            "Holly Swamp 18 String Inverters": hollyswamp18strdaykwList,
            "PG 100% Inverters": pgdaykwList,
            "PG 66% Inverters": pg66daykwList,
            "Thunderhead 15 & 1, 16 String Inverters": thunderheaddaykwList,
            "Thunderhead 14 String Inverters": thunderhead14strdaykwList,
            "Tedder 16 String Inverters": tedderdaykwList,
            "Tedder 15 String Inverters": tedder15strdaykwList,
            "Ogburn Inverters": ogburndaykwList,
            "Marshall Inverters": marshalldaykwList,
            "Jefferson 17 String Inverters": jeffersondaykwList,
            "Jefferson 18 String Inverters": jefferson18strdaykwList,
            "Hickson 18 String Inverters": hicksondaykwList,
            "Hickson 17 String Inverters": hickson17strdaykwList,
            "Bishopville II 32 String Inverters": bishopvilleIIdaykwList,
            "Bishopville II 34 String Inverters": bishopvilleII34strdaykwList,
            "Bishopville II 36 String Inverters": bishopvilleII36strdaykwList,
            "Bluebird Inverters": bluebirddaykwList,
            "Wellons Inverters": wellonsdaykwList,
            "Violet Inverters": violetdaykwList,
            "Van Buren 94.4% Inverters": vanburendaykwList,
            "Van Buren 93.6% Inverters": vanburen93daykwList,
            "Hickory Inverters": hickorydaykwList,
            "Hayes 92% Inverters": hayesdaykwList,
            "Hayes 96% Inverters": hayes96daykwList,
            "Harrison 93.6% Inverters": harrisondaykwList,
            "Harrison 92% & 91.2% Inverters": harrison92daykwList,
            "Cherry Blossom Inverters": cherrydaykwList,
            "Cardinal 96.6% Inverters": cardinal96daykwList,
            "Cardinal 95.2% Inverters": cardinal952daykwList,
            "Cardinal 94.4% Inverters": cardinal944daykwList
        }


        for site_name, underperformance_list in site_under_Lists.items():
            underperformers = identify_underperformers(underperformance_list)
            if underperformers:
                messagebox.showinfo(parent=alertW, title=site_name, message=f"Inverters {underperformers} Underperforming > 15%")


            

    gui_update_timer.resume()





def identify_underperformers(data):
    list_values = []
    for value, invnum in data:
        list_values.append(value)
    avg_value = np.mean(list_values)
    threshold = 0.15 * avg_value
    

    underperformers = []
    for value, invnum in data:
        if value < (avg_value - threshold):
            underperformers.append(invnum)
    
    return ','.join(underperformers)




def checkin():
    for widget in checkIns.winfo_children():
        widget.destroy()

    connect_Logbook()

    cur.execute("SELECT Location, Company, Employee FROM [Checked In]")
    checkedIn = cur.fetchall()

    for row_index, row in enumerate(checkedIn):
        for col_index, value in enumerate(row):
           # Check if the value is a datetime object and format it
            if isinstance(value, datetime):
                value = value.strftime('%m/%d/%y')
            # Apply different formatting for specific columns
            if row_index in range(1, 100, 2):
                bg_color = 'orange'
            else:
                bg_color = 'yellow'
            if col_index == 2:
                wsize = 24
            elif col_index == 1:
                wsize = 32
            else:
                wsize = 23
            label = Label(checkIns, text=value, font=("Calibri", 14), borderwidth=1, relief="solid", width=wsize, bg=bg_color)
            label.grid(row=row_index, column=col_index)

    lbconnection.close()

    update_data()


def time_window():

    global timecurrent
    #SELECT 15 = 30 Mins
    c.execute("SELECT TOP 16 [Date & Time] FROM [Whitetail Meter Data] ORDER BY [Date & Time] DESC")
    data_timestamps = c.fetchall()
    firsttime = data_timestamps[0][0]
    secondtime = data_timestamps[1][0]
    thirdtime = data_timestamps[2][0]
    fourthtime = data_timestamps[3][0]
    tenthtime = data_timestamps[5][0]
    lasttime = data_timestamps[15][0]

    hm_firsttime = firsttime.strftime('%H:%M')
    hm_secondtime = secondtime.strftime('%H:%M')
    hm_thirdtime = thirdtime.strftime('%H:%M')
    hm_fourthtime = fourthtime.strftime('%H:%M')
    hm_tenthtime = tenthtime.strftime('%H:%M')
    hm_lasttime = lasttime.strftime('%H:%M')

    time1v.config(text=hm_firsttime, font=("Calibri", 20))
    time2v.config(text=hm_secondtime, font=("Calibri", 20))
    time3v.config(text=hm_thirdtime, font=("Calibri", 20))
    time4v.config(text=hm_fourthtime, font=("Calibri", 20))
    time10v.config(text=hm_tenthtime, font=("Calibri", 20))
    timeLv.config(text=hm_lasttime, font=("Calibri", 20))

    pulls5TD = firsttime - tenthtime
    pulls5TDmins = round(pulls5TD.total_seconds() / 60, 2)
    pulls15TD = firsttime - lasttime
    pulls15TDmins = round(pulls15TD.total_seconds() / 60, 2)
    spread10.config(text=f"5 Pulls | {pulls5TDmins} Minutes")
    spread15.config(text=f"15 Pulls | {pulls15TDmins} Minutes")
    
    timecurrent = datetime.now()
    db_update_time = 10
    timecompare = timecurrent - timedelta(minutes=db_update_time)

    if firsttime < timecompare:
        os.startfile(r"G:\Shared drives\O&M\NCC Automations\Notification System\API Data Pull, Multi.py")
        messagebox.showerror(parent=timeW, title="Notification System/GUI", message= f"The Database has not been updated in {str(db_update_time)} Minutes and usually updates every 2\nLaunching Data Pull Script in response.")

    tupdate = timecurrent.strftime('%H:%M')

    timmytimeLabel.config(text= tupdate, font= ("Calibiri", 30))
    
    checkin() 

def db_to_dict():
    query_start = ty.perf_counter()
    underperformance_check_button.config(state=DISABLED)
    notes_button.config(state=DISABLED)

    connect_db()
    global tables, inv_data, breaker_data, meter_data, comm_data, POA_data, begin
    tables = []
    for tb in c.tables(tableType='TABLE'):
        tables.append(tb)
    #ic(tables)
    excluded_tables = ["1)Sites", "2)Breakers", "3)Meters", "4)Inverters", "5)POA"]

    tb_file = r"C:\Users\omops\Documents\Automations\Troubleshooting.txt"
    comm_data = {}
    for table in tables:
        table_name = table.table_name
        if table_name not in excluded_tables:
            c.execute(f"SELECT TOP 3 lastUpload FROM [{table_name}] ORDER BY [Date & Time] DESC")
            comm_value = c.fetchall()
            comm_data[table_name] = comm_value

    #ic(comm_data)
    inv_data = {}
    for table in tables:
        table_name = table.table_name
        if "INV" in table_name and table_name not in excluded_tables:
            #SELECT 15 = 30 Mins
            c.execute(f"SELECT TOP 16 * FROM [{table_name}] ORDER BY [Date & Time] DESC")
            inv_rows = c.fetchall()
            #ic(inv_rows)
            inv_data[table_name] = inv_rows
    #ic(inv_data)

    meter_data = {}
    for table in tables:
        table_name = table.table_name
        if any(name in table_name for name in ["Hickory", "Whitehall"]) and "Meter" in table_name:
            #SELECT 13 = 17 Mins of Data
            c.execute(f"SELECT TOP 16 * FROM [{table_name}] ORDER BY [Date & Time] DESC")
            meter_rows = c.fetchall()
            meter_data[table_name] = meter_rows 
        elif any(name in table_name for name in ["Wellons",]) and "Meter" in table_name:
            #SELECT 45 = 60 Mins of Data | Wellons has a severe intermittent comms issue.
            c.execute(f"SELECT TOP 60 * FROM [{table_name}] ORDER BY [Date & Time] DESC")
            meter_rows = c.fetchall()
            meter_data[table_name] = meter_rows 
        elif "Meter" in table_name and table_name not in excluded_tables:
            #SELECT 5 = 5.5 Mins of Data
            c.execute(f"SELECT TOP {meter_pulls} * FROM [{table_name}] ORDER BY [Date & Time] DESC")
            meter_rows = c.fetchall()
            meter_data[table_name] = meter_rows

    #ic(meter_data)
    POA_data = {}
    for table in tables:
        table_name = table.table_name
        if "POA" in table_name and table_name not in excluded_tables:
            c.execute(f"SELECT TOP 1 [W/M²] FROM [{table_name}] ORDER BY [Date & Time] DESC")
            POA_rows = c.fetchone()
            POA_data[table_name] = POA_rows
    

    #ic(POA_data)

    breaker_data = {}
    for table in tables:
        table_name = table.table_name
        if "Breaker" in table_name and table_name not in excluded_tables:
            c.execute(f"SELECT TOP {breaker_pulls} [Status] FROM [{table_name}] ORDER BY [Date & Time] DESC")
            breaker_rows = c.fetchall()
            breaker_data[table_name] = breaker_rows
    #ic(breaker_data)

    begin = launch_check()

    query_end = ty.perf_counter()
    print("Query Time (secs):", round(query_end - query_start, 2))
    time_window()

STATE_FILE = r"G:\Shared drives\O&M\NCC Automations\Notification System\CheckBoxState.json"

def save_cb_state():
    state = [var.get() for var in all_CBs]
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def load_cb_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            try:
                state = json.load(f)
                for var, value in zip(all_CBs, state):
                    var.set(value)
            except json.decoder.JSONDecodeError as e:
                print(f"Error decoding JSON data: {e}")
                # Handle the error or provide appropriate fallback behavior
    else:
        print(f"File {STATE_FILE} does not exist.")
def check_button_notes():
    gui_update_timer.pause()
    messagebox.showinfo(parent=alertW, title="Checkbutton Info", message= "The First column of CheckButtons in the Site Data Window turns off all notifications associated with that Site. The Checkbuttons for each associated device; POA and INV's, turns off notifications for that specific device by selecting the CB next to the device status.")
    gui_update_timer.resume()

def open_file():
    os.startfile(r"G:\Shared drives\Narenco Projects\O&M Projects\NCC\Procedures\Also Energy GUI Interactions.docx")
                

cur_time = datetime.now()
tupdate =  cur_time.strftime('%H:%M')
notesFrame = Frame(alertW, height= 5, bd= 3, relief= 'groove')
notesFrame.pack(fill='x')
alertwnotes = Label(notesFrame, text= "Checkbox: ✓ = Open WO", font= ("Calibiri", 14))
alertwnotes.pack()
alertWnote1 = Label(notesFrame, text= "& pauses my notifications", font= ("Calibiri", 14))
alertWnote1.pack()
tupdateLabel = Label(alertW, text= "GUI Last Updated", font= ("Calibiri", 18))
tupdateLabel.pack()
timmytimeLabel = Label(alertW, text= tupdate, font= ("Calibiri", 30))
timmytimeLabel.pack()
underperformance_check_button = Button(alertW, command= underperformance_data, text= "Performance Analysis", font=("Calibiri", 14))
underperformance_check_button.pack(padx= 2, pady= 2)
notes_button = Button(alertW, command= lambda: check_button_notes(), text= "Checkbutton Notes", font=("Calibiri", 14))
notes_button.pack(padx= 2, pady= 2)
proc_button = Button(alertW, command= lambda: open_file(), text= "Procedure Doc", font=("Calibiri", 14))
proc_button.pack(padx= 2, pady= 2)

root.after(10, load_cb_state)
launch_end = ty.perf_counter()
print("Launch Time (secs):", launch_end - start)

#Start Update Cycle
root.after(10, db_to_dict)
root.mainloop()


#At Exit Tasks
def allinv_message_reset():
    for num in range(1, 38):
        with open(f"C:\\Users\\OMOPS\\OneDrive - Narenco\\Documents\\APISiteStat\\Site {num} All INV Msg Stat.txt", "w+") as outfile:
            outfile.write("1")



atexit.register(allinv_message_reset)
atexit.register(save_cb_state)