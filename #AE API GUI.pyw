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

master_List_Sites = [('Bishopville II', 36, 'bishopvilleII'), ('Bluebird', 24, 'bluebird'), ('Bulloch 1A', 24, 'bulloch1a'), ('Bulloch 1B', 24, 'bulloch1b'), ('Cardinal', 59, 'cardinal'),
                     ('Cherry', 4, 'cherry'), ('Cougar', 30, 'cougar'), ('Conetoe', 4, 'conetoe'), ('Duplin', 21, 'duplin'), ('Freight Line', 18, 'freightline'), ('Gray Fox', 40, 'grayfox'),
                      ('Harding', 24, 'harding'), ('Harrison', 43, 'harrison'), ('Hayes', 26, 'hayes'), ('Hickory', 2, 'hickory'), ('Hickson', 16, 'hickson'), ('Holly Swamp', 16, 'hollyswamp'),
                       ('Jefferson', 64, 'jefferson'), ('Marshall', 16, 'marshall'), ('McLean', 40, 'mcLean'), ('Ogburn', 16, 'ogburn'), ('PG', 18, 'pg'), ('Richmond', 24, 'richmond'),
                        ('Shorthorn', 72, 'shorthorn'), ('Sunflower', 80, 'sunflower'), ('Tedder', 16, 'tedder'), ('Thunderhead', 16, 'thunderhead'), ('Upson', 24, 'upson'), 
                        ('Van Buren', 17, 'vanburen'), ('Violet', 2, 'violet'), ('Warbler', 32, 'warbler'), ('Washington', 40, 'washington'), ('Wayne 1', 4, 'wayne1'),
                        ('Wayne 2', 4, 'wayne2'), ('Wayne 3', 4, 'wayne3'), ('Wellons', 6, 'wellons'), ('Whitehall', 16, 'whitehall'), ('Whitetail', 80, 'whitetail'), ('Elk', 43, 'elk'), ('CDIA', 1, 'cdia')]


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
        name, inverters, var_name = site_info
        l = []
        if name != "CDIA":
            for i in range(1, inverters + 1):
                checkbox_var = globals()[f'{var_name}inv{i}cbval']
                if not checkbox_var.get():
                    config_color = globals()[f'{var_name}inv{i}Label'].cget("bg")
                    l.append(config_color)
            status_all[f'{var_name}'] = l



    tm_now = datetime.now()
    str_tm_now = tm_now.strftime('%H')
    h_tm_now = int(str_tm_now)

    for site_info in master_List_Sites:
        name, inverters, var_name = site_info
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
            poalbl = globals()[f'{var_name}POALabel'].cget('bg')
            if poalbl != 'pink' and poa_noti:
                messagebox.showwarning(parent= alertW, title=f"{name}, POA Comms Error", message=f"{name} lost comms with POA sensor at {strtime_poa}")
            globals()[f'{var_name}POALabel'].config(bg='pink', text=poa)
        else:
            globals()[f'{var_name}POALabel'].config(bg='yellow', text=poa)

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
                        meterAstatus= '❌❌'
                        meterAstatuscolor= 'red'
                        meterlbl = globals()[f'{var_name}meterALabel'].cget('bg')
                        if meterlbl != 'red' and master_cb_skips_INV_check:
                            online = meter_last_online(name)
                            messagebox.showerror(parent= alertW, title=f"{name}, Power Loss", message=f"Site: {name}\nMeter Production: {round(meterdataKW, 2)}\nMeter Amps:\nA: {round(meterdataavgAA, 2)}\nB: {round(meterdataavgAB, 2)}\nC: {round(meterdataavgAC, 2)}\n{online}")
                
                    elif meterdataAC or meterdataAB or meterdataKW < 2:
                        meterAstatus= '❌❌'
                        meterAstatuscolor= 'red'
                        meterlbl = globals()[f'{var_name}meterALabel'].cget('bg')
                        if meterlbl != 'red' and master_cb_skips_INV_check:
                            online = meter_last_online(name)
                            messagebox.showerror(parent= alertW, title=f"{name}, Meter Power Loss", message=f"Site: {name}\nMeter Production: {round(meterdataKW, 2)}\nMeter Amps:\nA: {round(meterdataavgAA, 2)}\nB: {round(meterdataavgAB, 2)}\nC: {round(meterdataavgAC, 2)}\n{online}")
                
                    

                else:
                    meterAstatus= '✓✓✓'
                    meterAstatuscolor= 'green'
                globals()[f'{var_name}meterVLabel'].config(text= meterVstatus, bg= meterVstatuscolor)
                globals()[f'{var_name}meterALabel'].config(text= meterAstatus, bg= meterAstatuscolor)

            else:
                meterlbl = globals()[f'{var_name}meterALabel'].cget('bg')
                if meterlbl != 'pink' and master_cb_skips_INV_check:
                    messagebox.showerror(parent= alertW, title=f"{name}, Meter Comms Loss", message=f"Meter Comms lost {meter_Ltime} with the Meter at {name}! Please Investigate!")
                globals()[f'{var_name}meterALabel'].config(bg='pink')
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
                current_config = globals()[f'{var_name}inv{r}Label'].cget("bg")
                cbval = globals()[f'{var_name}inv{r}cbval'].get()
                total_dcv = sum(row[4] for row in data)
                avg_dcv = total_dcv / len(data)
                inv_comm = max(comm_data[f'{name} Central INV {r} Data'])[0]
                inv_Ltime = inv_comm.strftime('%m/%d/%y | %H:%M')
                if inv_comm > time_date_compare:
                    if all(point[3] <= 1 for point in data):
                        if avg_dcv > 100:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 75)) and cbval == 0 and master_cb_skips_INV_check:
                                online_last = duplinC_last_online(name, r)
                                messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Central Inverter {r} Offline, Good DC Voltage | {online_last}")
                            globals()[f'{var_name}inv{r}Label'].config(text="X✓", bg='orange')
                        else:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 75)) and cbval == 0 and master_cb_skips_INV_check:
                                online_last = duplinC_last_online(name, r)
                                messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Central Inverter {r} Offline | {online_last}")
                            globals()[f'{var_name}inv{r}Label'].config(text="❌", bg='red')
                    else:
                        if check_inv_consecutively_online(point[3] for point in data):
                            globals()[f'{var_name}inv{r}Label'].config(text="✓", bg='green')
                else:
                    invlbl = globals()[f'{var_name}inv{r}Label'].cget('bg')
                    globals()[f'{var_name}inv{r}Label'].config(bg='pink')
                    if invlbl != 'pink' and cbval == 0 and master_cb_skips_INV_check:
                        messagebox.showerror(parent= alertW, title=f"{name}, Inverter Comms Loss", message=f"INV Comms lost {inv_Ltime} with Central Inverter {r} at {name}! Please Investigate!")

            stringinv = 4
            for r in range(1, 19):
                data = inv_data[f'{name} String INV {r} Data']
                current_config = globals()[f'{var_name}inv{stringinv}Label'].cget("bg")
                cbval = globals()[f'{var_name}inv{r}cbval'].get()
                total_dcv = sum(row[4] for row in data)
                avg_dcv = total_dcv / len(data)
                inv_comm = max(comm_data[f'{name} String INV {r} Data'])[0]
                inv_Ltime = inv_comm.strftime('%m/%d/%y | %H:%M')
                if inv_comm > time_date_compare:
                    if all(point[3] <= 1 for point in data):
                        if avg_dcv > 100:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 75)) and cbval == 0 and master_cb_skips_INV_check:
                                online_last = duplinS_last_online(name, r)
                                messagebox.showwarning(title=f"{name}", parent= alertW, message= f"String Inverter {r} Offline, Good DC Voltage | {online_last}")
                            globals()[f'{var_name}inv{stringinv}Label'].config(text="X✓", bg='orange')
                            stringinv += 1  
                        else:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 75)) and cbval == 0 and master_cb_skips_INV_check:
                                online_last = duplinS_last_online(name, r)
                                messagebox.showwarning(title=f"{name}", parent= alertW, message= f"String Inverter {r} Offline | {online_last}")
                            globals()[f'{var_name}inv{stringinv}Label'].config(text="❌", bg='red')
                            stringinv += 1  
                    else:
                        if check_inv_consecutively_online(point[3] for point in data):
                            globals()[f'{var_name}inv{stringinv}Label'].config(text="✓", bg='green')
                        stringinv += 1  
                else:
                    invlbl = globals()[f'{var_name}inv{r}Label'].cget('bg')
                    globals()[f'{var_name}inv{stringinv}Label'].config(bg='pink')
                    if invlbl != 'pink' and cbval == 0 and master_cb_skips_INV_check:
                        messagebox.showerror(parent= alertW, title=f"{name}, Inverter Comms Loss", message=f"INV Comms lost {inv_Ltime} with String Inverter {r} at {name}! Please Investigate!")
                    stringinv += 1               
        elif name == "CDIA":
                data = inv_data[f'{name} INV 1 Data']
                current_config = globals()[f'{var_name}meterALabel'].cget("bg")
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

                            globals()[f'{var_name}meterALabel'].config(text="X✓", bg='orange')
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

                            globals()[f'{var_name}meterALabel'].config(text="❌❌", bg='red')
                    else:
                        if check_inv_consecutively_online(point[3] for point in data):
                            globals()[f'{var_name}meterALabel'].config(text="✓✓✓", bg='green')
                else:
                    invlbl = globals()[f'{var_name}meterALabel'].cget('bg')
                    globals()[f'{var_name}meterALabel'].config(bg='pink')
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
                current_config = globals()[f'{var_name}inv{r}Label'].cget("bg")
                cbval = globals()[f'{var_name}inv{r}cbval'].get()
                total_dcv = sum(row[4] for row in data)
                avg_dcv = total_dcv / len(data)
                inv_comm = max(comm_data[f'{name} INV {r} Data'])[0]
                inv_Ltime = inv_comm.strftime('%m/%d/%y | %H:%M')
                if inv_comm > time_date_compare:
                    if all(point[3] <= 1 for point in data):
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

                            globals()[f'{var_name}inv{r}Label'].config(text="X✓", bg='orange')
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

                            globals()[f'{var_name}inv{r}Label'].config(text="❌", bg='red')
                    else:
                        if check_inv_consecutively_online(point[3] for point in data):
                            globals()[f'{var_name}inv{r}Label'].config(text="✓", bg='green')
                else:
                    invlbl = globals()[f'{var_name}inv{r}Label'].cget('bg')
                    globals()[f'{var_name}inv{r}Label'].config(bg='pink')
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
        name, inverters, var_name = site_info
        l = []
        if name != "CDIA":
            for i in range(1, inverters + 1):
                checkbox_var = globals()[f'{var_name}inv{i}cbval']
                if not checkbox_var.get():
                    config_color = globals()[f'{var_name}inv{i}Label'].cget("bg")
                    l.append(config_color)
            poststatus_all[f'{var_name}'] = l
    #ic(poststatus_all['vanburen'])
    for index, site_info in enumerate(master_List_Sites):
        name, inverters, var_name = site_info
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
        name, inverters, var_name = site_info
        if int(globals()[f'{var_name}POALabel'].cget("text")) > 100:
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

        
        for site, inv, var in master_List_Sites:
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




#Top Labels
siteLabel = Label(root, bg="yellow", text= "Sites")
siteLabel.grid(row=0, column= 0, sticky=W)
breakerstatusLabel= Label(root, bg="yellow", text= "Breaker Status")
breakerstatusLabel.grid(row=0, column=1)
meterVLabel = Label(root, bg="yellow", text= "Utility V")
meterVLabel.grid(row= 0, column=2)
meterALabel = Label(root, bg="yellow", text="Meter kW")
meterALabel.grid(row=0, column=4)
POALabel = Label(root, bg="yellow", text= "POA")
POALabel.grid(row=0, column= 5, columnspan=2)

bishopvilleIILabel = Label(root, bg="yellow", text= "Bishopville II")
bishopvilleIILabel.grid(row=1, column=0, sticky=W)
bishopvilleIIstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
bishopvilleIIstatusLabel.grid(row= 1, column=1)
bishopvilleIImeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
bishopvilleIImeterVLabel.grid(row=1, column=2)

bishopvilleIImeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
bishopvilleIImeterALabel.grid(row=1, column=4)
bishopvilleIIPOALabel= Label(root, bg="yellow", text= '-1')
bishopvilleIIPOALabel.grid(row=1, column=5)

bluebirdLabel = Label(root, bg="yellow", text= "Bluebird")
bluebirdLabel.grid(row=2, column=0, sticky= W)
bluebirdmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
bluebirdmeterVLabel.grid(row=2, column=2)
bluebirdmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
bluebirdmeterALabel.grid(row=2, column=4)
bluebirdPOALabel= Label(root, bg="yellow", text= '-1')
bluebirdPOALabel.grid(row=2, column=5)

bulloch1aLabel= Label(root, bg="yellow", text= "Bulloch 1A")
bulloch1aLabel.grid(row= 3, column= 0, sticky=W)
bulloch1ameterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
bulloch1ameterVLabel.grid(row=3, column=2)
bulloch1ameterALabel = Label(root, bg="yellow", text='X', fg= 'black')
bulloch1ameterALabel.grid(row=3, column=4)
bulloch1aPOALabel= Label(root, bg="yellow", text= '-1')
bulloch1aPOALabel.grid(row=3, column=5)

bulloch1bLabel= Label(root, bg="yellow", text="Bulloch 1B")
bulloch1bLabel.grid(row= 4, column= 0, sticky=W)
bulloch1bmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
bulloch1bmeterVLabel.grid(row=4, column=2)
bulloch1bmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
bulloch1bmeterALabel.grid(row=4, column=4)
bulloch1bPOALabel= Label(root, bg="yellow", text= '-1')
bulloch1bPOALabel.grid(row=4, column=5)

cardinalLabel = Label(root, bg="yellow", text= "Cardinal")
cardinalLabel.grid(row=5, column=0, sticky=W)
cardinalstatusLabel = Label(root, bg="yellow", text='❌', fg='black')
cardinalstatusLabel.grid(row= 5, column=1)
cardinalmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
cardinalmeterVLabel.grid(row=5, column=2)
cardinalmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
cardinalmeterALabel.grid(row=5, column=4)
cardinalPOALabel= Label(root, bg="yellow", text= '-1')
cardinalPOALabel.grid(row=5, column=5)

cdiaLabel = Label(root, bg="yellow", text= "CDIA")
cdiaLabel.grid(row=6, column=0, sticky=W)
cdiameterALabel = Label(root, bg="yellow", text='X', fg= 'black')
cdiameterALabel.grid(row=6, column=4)
cdiaPOALabel= Label(root, bg="yellow", text= '-1')
cdiaPOALabel.grid(row=6, column=5)

cherryblossomLabel = Label(root, bg="yellow", text= "Cherry Blossom")
cherryblossomLabel.grid(row=7, column=0, sticky=W)
cherrystatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
cherrystatusLabel.grid(row= 7, column=1)
cherrymeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
cherrymeterVLabel.grid(row=7, column=2)
cherrymeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
cherrymeterALabel.grid(row=7, column=4)
cherryPOALabel= Label(root, bg="yellow", text= '-1')
cherryPOALabel.grid(row=7, column=5)

cougarLabel = Label(root, bg="yellow", text= "Cougar")
cougarLabel.grid(row= 8, column=0, sticky=W)
cougarmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
cougarmeterVLabel.grid(row=8, column=2)
cougarmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
cougarmeterALabel.grid(row=8, column=4)
cougarPOALabel= Label(root, bg="yellow", text= '-1')
cougarPOALabel.grid(row=8, column=5)

conetoeLabel = Label(root, bg="yellow", text= "Conetoe")
conetoeLabel.grid(row= 9, column=0, sticky=W)
conetoemeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
conetoemeterVLabel.grid(row=9, column=2)
conetoemeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
conetoemeterALabel.grid(row=9, column=4)
conetoePOALabel= Label(root, bg="yellow", text= '-1')
conetoePOALabel.grid(row=9, column=5)

duplinLabel= Label(root, bg="yellow", text= "Duplin")
duplinLabel.grid(row= 10, column=0, sticky=W)
duplinmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
duplinmeterVLabel.grid(row=10, column=2)
duplinmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
duplinmeterALabel.grid(row=10, column=4)
duplinPOALabel= Label(root, bg="yellow", text= '-1')
duplinPOALabel.grid(row=10, column=5)

elkLabel= Label(root, bg="yellow", text= "Elk")
elkLabel.grid(row= 11, column= 0, sticky=W)
elkstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
elkstatusLabel.grid(row= 11, column=1)
elkmeterVLabel = Label(root, bg="yellow", text= "❌", fg= 'black')
elkmeterVLabel.grid(row=11, column=2)
elkmeterALabel = Label(root, bg="yellow", text= '❌', fg= 'black')
elkmeterALabel.grid(row=11, column=4)
elkPOALabel= Label(root, bg="yellow", text= '0')
elkPOALabel.grid(row=11, column=5)

freightlineLabel= Label(root, bg="yellow", text= "Freight Line")
freightlineLabel.grid(row= 12, column= 0, sticky=W)
freightlinemeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
freightlinemeterVLabel.grid(row=12, column=2)
freightlinemeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
freightlinemeterALabel.grid(row=12, column=4)
freightlinePOALabel= Label(root, bg="yellow", text= '-1')
freightlinePOALabel.grid(row=12, column=5)

grayfoxLabel = Label (root, bg="yellow", text= "Gray Fox")
grayfoxLabel.grid(row=13, column=0, sticky=W)
grayfoxstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
grayfoxstatusLabel.grid(row= 13, column=1)
grayfoxmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
grayfoxmeterVLabel.grid(row=13, column=2)
grayfoxmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
grayfoxmeterALabel.grid(row=13, column=4)
grayfoxPOALabel= Label(root, bg="yellow", text= '-1')
grayfoxPOALabel.grid(row=13, column=5)

hardingLabel= Label(root, bg="yellow", text= "Harding")
hardingLabel.grid(row=14, column= 0, sticky=W)
hardingstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
hardingstatusLabel.grid(row= 14, column=1)
hardingmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
hardingmeterVLabel.grid(row=14, column=2)
hardingmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
hardingmeterALabel.grid(row=14, column=4)
hardingPOALabel= Label(root, bg="yellow", text= '-1')
hardingPOALabel.grid(row=14, column=5)

harrisonLabel = Label(root, bg="yellow", text= "Harrison")
harrisonLabel.grid(row= 15, column= 0, sticky=W)
harrisonstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
harrisonstatusLabel.grid(row= 15, column=1)
harrisonmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
harrisonmeterVLabel.grid(row=15, column=2)
harrisonmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
harrisonmeterALabel.grid(row=15, column=4)
harrisonPOALabel= Label(root, bg="yellow", text= '-1')
harrisonPOALabel.grid(row=15, column=5)

hayesLabel= Label(root, bg="yellow", text= "Hayes")
hayesLabel.grid(row=16, column=0, sticky=W)
hayesstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
hayesstatusLabel.grid(row= 16, column=1)
hayesmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
hayesmeterVLabel.grid(row=16, column=2)
hayesmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
hayesmeterALabel.grid(row=16, column=4)
hayesPOALabel= Label(root, bg="yellow", text= '-1')
hayesPOALabel.grid(row=16, column=5)

hickoryLabel= Label(root, bg="yellow", text= "Hickory")
hickoryLabel.grid(row=17, column=0, sticky=W)
hickorystatusLabel = Label(root, bg="yellow", text='X', fg= 'black')
hickorystatusLabel.grid(row= 17, column=1)
hickorymeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
hickorymeterVLabel.grid(row=17, column=2)
hickorymeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
hickorymeterALabel.grid(row=17, column=4)
hickoryPOALabel= Label(root, bg="yellow", text= '-1')
hickoryPOALabel.grid(row=17, column=5)

hicksonLabel= Label(root, bg="yellow", text= "Hickson")
hicksonLabel.grid(row=18, column= 0, sticky=W)
hicksonstatusLabel = Label(root, bg="yellow", text='X', fg= 'black')
hicksonstatusLabel.grid(row= 18, column=1)
hicksonmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
hicksonmeterVLabel.grid(row=18, column=2)
hicksonmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
hicksonmeterALabel.grid(row=18, column=4)
hicksonPOALabel= Label(root, bg="yellow", text= '-1')
hicksonPOALabel.grid(row=18, column=5)

hollyswampLabel = Label(root, bg="yellow", text= "Holly Swamp")
hollyswampLabel.grid(row= 19, column=0, sticky=W)
hollyswampmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
hollyswampmeterVLabel.grid(row=19, column=2)
hollyswampmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
hollyswampmeterALabel.grid(row=19, column=4)
hollyswampPOALabel= Label(root, bg="yellow", text= '-1')
hollyswampPOALabel.grid(row=19, column=5)

jeffersonLabel = Label(root, bg="yellow", text= "Jefferson")
jeffersonLabel.grid(row= 20,column=0 , sticky=W)
jeffersonstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
jeffersonstatusLabel.grid(row= 20, column=1)
jeffersonmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
jeffersonmeterVLabel.grid(row=20, column=2)
jeffersonmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
jeffersonmeterALabel.grid(row=20, column=4)
jeffersonPOALabel= Label(root, bg="yellow", text= '-1')
jeffersonPOALabel.grid(row=20, column=5)

marshallLabel= Label(root, bg="yellow", text= "Marshall")
marshallLabel.grid(row= 21, column=0, sticky=W)
marshallstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
marshallstatusLabel.grid(row= 21, column=1)
marshallmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
marshallmeterVLabel.grid(row=21, column=2)
marshallmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
marshallmeterALabel.grid(row=21, column=4)
marshallPOALabel= Label(root, bg="yellow", text= '-1')
marshallPOALabel.grid(row=21, column=5)

mcLeanLabel= Label(root, bg="yellow", text= "McLean")
mcLeanLabel.grid(row=22, column=0, sticky=W)
mcLeanstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
mcLeanstatusLabel.grid(row= 22, column=1)
mcLeanmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
mcLeanmeterVLabel.grid(row=22, column=2)
mcLeanmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
mcLeanmeterALabel.grid(row=22, column=4)
mcLeanPOALabel= Label(root, bg="yellow", text= '-1')
mcLeanPOALabel.grid(row=22, column=5)

ogburnLabel= Label(root, bg="yellow", text= "Ogburn")
ogburnLabel.grid(row=23, column= 0, sticky=W)
ogburnstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
ogburnstatusLabel.grid(row= 23, column=1)
ogburnmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
ogburnmeterVLabel.grid(row=23, column=2)
ogburnmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
ogburnmeterALabel.grid(row=23, column=4)
ogburnPOALabel= Label(root, bg="yellow", text= '-1')
ogburnPOALabel.grid(row=23, column=5)

pgLabel= Label(root, bg="yellow", text= "PG")
pgLabel.grid(row=24, column= 0, sticky=W)
pgmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
pgmeterVLabel.grid(row=24, column=2)
pgmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
pgmeterALabel.grid(row=24, column=4)
pgPOALabel= Label(root, bg="yellow", text= '-1')
pgPOALabel.grid(row=24, column=5)

richmondLabel= Label(root, bg="yellow", text= "Richmond")
richmondLabel.grid(row= 25, column=0, sticky=W)
richmondmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
richmondmeterVLabel.grid(row=25, column=2)
richmondmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
richmondmeterALabel.grid(row=25, column=4)
richmondPOALabel= Label(root, bg="yellow", text= '-1')
richmondPOALabel.grid(row=25, column=5)

shorthornLabel= Label(root, bg="yellow", text= "Shorthorn")
shorthornLabel.grid(row=26, column=0, sticky=W)
shorthornstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
shorthornstatusLabel.grid(row= 26, column=1)
shorthornmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
shorthornmeterVLabel.grid(row=26, column=2)
shorthornmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
shorthornmeterALabel.grid(row=26, column=4)
shorthornPOALabel= Label(root, bg="yellow", text= '-1')
shorthornPOALabel.grid(row=26, column=5)

sunflowerLabel= Label(root, bg="yellow", text= "Sunflower")
sunflowerLabel.grid(row=27, column=0, sticky=W)
sunflowerstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
sunflowerstatusLabel.grid(row= 27, column=1)
sunflowermeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
sunflowermeterVLabel.grid(row=27, column=2)
sunflowermeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
sunflowermeterALabel.grid(row=27, column=4)
sunflowerPOALabel= Label(root, bg="yellow", text= '-1')
sunflowerPOALabel.grid(row=27, column=5)

tedderLabel= Label(root, bg="yellow", text= "Tedder")
tedderLabel.grid(row=28, column=0, sticky=W)
tedderstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
tedderstatusLabel.grid(row= 28, column=1)
teddermeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
teddermeterVLabel.grid(row=28, column=2)
teddermeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
teddermeterALabel.grid(row=28, column=4)
tedderPOALabel= Label(root, bg="yellow", text= '-1')
tedderPOALabel.grid(row=28, column=5)

thunderheadLabel= Label(root, bg="yellow", text= "Thunderhead")
thunderheadLabel.grid(row=29, column=0, sticky=W)
thunderheadstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
thunderheadstatusLabel.grid(row= 29, column=1)
thunderheadmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
thunderheadmeterVLabel.grid(row=29, column=2)
thunderheadmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
thunderheadmeterALabel.grid(row=29, column=4)
thunderheadPOALabel= Label(root, bg="yellow", text= '-1')
thunderheadPOALabel.grid(row=29, column=5)

upsonLabel= Label(root, bg="yellow", text= "Upson")
upsonLabel.grid(row= 30, column=0, sticky=W)
upsonmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
upsonmeterVLabel.grid(row=30, column=2)
upsonmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
upsonmeterALabel.grid(row=30, column=4)
upsonPOALabel= Label(root, bg="yellow", text= '-1')
upsonPOALabel.grid(row=30, column=5)

vanburenLabel= Label(root, bg="yellow", text= "Van Buren")
vanburenLabel.grid(row=31, column= 0, sticky=W)
vanburenmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
vanburenmeterVLabel.grid(row=31, column=2)
vanburenmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
vanburenmeterALabel.grid(row=31, column=4)
vanburenPOALabel= Label(root, bg="yellow", text= '-1')
vanburenPOALabel.grid(row=31, column=5)

violetLabel= Label(root, bg="yellow", text= "Violet")
violetLabel.grid(row= 32, column=0, sticky=W, rowspan=2)
violet1statusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
violet1statusLabel.grid(row= 32, column=1)
violet2statusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
violet2statusLabel.grid(row= 33, column=1)
violetmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
violetmeterVLabel.grid(row=32, column=2, rowspan=2)
violetmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
violetmeterALabel.grid(row=32, column=4, rowspan=2)
violetPOALabel= Label(root, bg="yellow", text= '0')
violetPOALabel.grid(row=32, column=5, rowspan=2)

warblerLabel= Label(root, bg="yellow", text= "Warbler")
warblerLabel.grid(row=34, column=0, sticky=W)
warblerstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
warblerstatusLabel.grid(row= 34, column=1)
warblermeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
warblermeterVLabel.grid(row=34, column=2)
warblermeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
warblermeterALabel.grid(row=34, column=4)
warblerPOALabel= Label(root, bg="yellow", text= '-1')
warblerPOALabel.grid(row=34, column=5)

washingtonLabel= Label(root, bg="yellow", text= "Washington")
washingtonLabel.grid(row=35, column=0, sticky=W)
washingtonstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
washingtonstatusLabel.grid(row= 35, column=1)
washingtonmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
washingtonmeterVLabel.grid(row=35, column=2)
washingtonmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
washingtonmeterALabel.grid(row=35, column=4)
washingtonPOALabel= Label(root, bg="yellow", text= '-1')
washingtonPOALabel.grid(row=35, column=5)

wayne1Label= Label(root, bg="yellow", text= "Wayne 1")
wayne1Label.grid(row= 36, column= 0, sticky=W)
wayne1meterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
wayne1meterVLabel.grid(row=36, column=2)
wayne1meterALabel = Label(root, bg="yellow", text='X', fg= 'black')
wayne1meterALabel.grid(row=36, column=4)
wayne1POALabel= Label(root, bg="yellow", text= '-1')
wayne1POALabel.grid(row=36, column=5)

wayne2Label= Label(root, bg="yellow", text= "Wayne 2")
wayne2Label.grid(row= 37, column=0, sticky=W)
wayne2meterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
wayne2meterVLabel.grid(row=37, column=2)
wayne2meterALabel = Label(root, bg="yellow", text='X', fg= 'black')
wayne2meterALabel.grid(row=37, column=4)
wayne2POALabel= Label(root, bg="yellow", text= '-1')
wayne2POALabel.grid(row=37, column=5)

wayne3Label= Label(root, bg="yellow", text= "Wayne 3")
wayne3Label.grid(row= 38, column= 0, sticky=W)
wayne3meterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
wayne3meterVLabel.grid(row=38, column=2)
wayne3meterALabel = Label(root, bg="yellow", text='X', fg= 'black')
wayne3meterALabel.grid(row=38, column=4)
wayne3POALabel= Label(root, bg="yellow", text= '-1')
wayne3POALabel.grid(row=38, column=5)

wellonsLabel= Label(root, bg="yellow", text= "Wellons")
wellonsLabel.grid(row= 39, column= 0, sticky=W)
wellonsmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
wellonsmeterVLabel.grid(row=39, column=2)
wellonsmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
wellonsmeterALabel.grid(row=39, column=4)
wellonsPOALabel= Label(root, bg="yellow", text= '-1')
wellonsPOALabel.grid(row=39, column=5)

whitehallLabel= Label(root, bg="yellow", text= "Whitehall")
whitehallLabel.grid(row=40, column=0, sticky=W)
whitehallstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
whitehallstatusLabel.grid(row= 40, column=1)
whitehallmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
whitehallmeterVLabel.grid(row=40, column=2)
whitehallmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
whitehallmeterALabel.grid(row=40, column=4)
whitehallPOALabel= Label(root, bg="yellow", text= '-1')
whitehallPOALabel.grid(row=40, column=5)

whitetailLabel= Label(root, bg="yellow", text= "Whitetail")
whitetailLabel.grid(row=41, column=0, sticky=W)
whitetailstatusLabel = Label(root, bg="yellow", text='❌', fg= 'black')
whitetailstatusLabel.grid(row= 41, column=1)
whitetailmeterVLabel = Label(root, bg="yellow", text='X', fg= 'black')
whitetailmeterVLabel.grid(row=41, column=2)
whitetailmeterALabel = Label(root, bg="yellow", text='X', fg= 'black')
whitetailmeterALabel.grid(row=41, column=4)
whitetailPOALabel= Label(root, bg="yellow", text= '-1')
whitetailPOALabel.grid(row=41, column=5)



#Main INV
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


bluebirdinv1cbval = IntVar()
bluebirdinv2cbval = IntVar()
bluebirdinv3cbval = IntVar()
bluebirdinv4cbval = IntVar()
bluebirdinv5cbval = IntVar()
bluebirdinv6cbval = IntVar()
bluebirdinv7cbval = IntVar()
bluebirdinv8cbval = IntVar()
bluebirdinv9cbval = IntVar()
bluebirdinv10cbval = IntVar()
bluebirdinv11cbval = IntVar()
bluebirdinv12cbval = IntVar()
bluebirdinv13cbval = IntVar()
bluebirdinv14cbval = IntVar()
bluebirdinv15cbval = IntVar()
bluebirdinv16cbval = IntVar()
bluebirdinv17cbval = IntVar()
bluebirdinv18cbval = IntVar()
bluebirdinv19cbval = IntVar()
bluebirdinv20cbval = IntVar()
bluebirdinv21cbval = IntVar()
bluebirdinv22cbval = IntVar()
bluebirdinv23cbval = IntVar()
bluebirdinv24cbval = IntVar()

cardinalinv1cbval = IntVar()
cardinalinv2cbval = IntVar()
cardinalinv3cbval = IntVar()
cardinalinv4cbval = IntVar()
cardinalinv5cbval = IntVar()
cardinalinv6cbval = IntVar()
cardinalinv7cbval = IntVar()
cardinalinv8cbval = IntVar()
cardinalinv9cbval = IntVar()
cardinalinv10cbval = IntVar()
cardinalinv11cbval = IntVar()
cardinalinv12cbval = IntVar()
cardinalinv13cbval = IntVar()
cardinalinv14cbval = IntVar()
cardinalinv15cbval = IntVar()
cardinalinv16cbval = IntVar()
cardinalinv17cbval = IntVar()
cardinalinv18cbval = IntVar()
cardinalinv19cbval = IntVar()
cardinalinv20cbval = IntVar()
cardinalinv21cbval = IntVar()
cardinalinv22cbval = IntVar()
cardinalinv23cbval = IntVar()
cardinalinv24cbval = IntVar()
cardinalinv25cbval = IntVar()
cardinalinv26cbval = IntVar()
cardinalinv27cbval = IntVar()
cardinalinv28cbval = IntVar()
cardinalinv29cbval = IntVar()
cardinalinv30cbval = IntVar()
cardinalinv31cbval = IntVar()
cardinalinv32cbval = IntVar()
cardinalinv33cbval = IntVar()
cardinalinv34cbval = IntVar()
cardinalinv35cbval = IntVar()
cardinalinv36cbval = IntVar()
cardinalinv37cbval = IntVar()
cardinalinv38cbval = IntVar()
cardinalinv39cbval = IntVar()
cardinalinv40cbval = IntVar()
cardinalinv41cbval = IntVar()
cardinalinv42cbval = IntVar()
cardinalinv43cbval = IntVar()
cardinalinv44cbval = IntVar()
cardinalinv45cbval = IntVar()
cardinalinv46cbval = IntVar()
cardinalinv47cbval = IntVar()
cardinalinv48cbval = IntVar()
cardinalinv49cbval = IntVar()
cardinalinv50cbval = IntVar()
cardinalinv51cbval = IntVar()
cardinalinv52cbval = IntVar()
cardinalinv53cbval = IntVar()
cardinalinv54cbval = IntVar()
cardinalinv55cbval = IntVar()
cardinalinv56cbval = IntVar()
cardinalinv57cbval = IntVar()
cardinalinv58cbval = IntVar()
cardinalinv59cbval = IntVar()

cougarinv1cbval = IntVar()
cougarinv2cbval = IntVar()
cougarinv3cbval = IntVar()
cougarinv4cbval = IntVar()
cougarinv5cbval = IntVar()
cougarinv6cbval = IntVar()
cougarinv7cbval = IntVar()
cougarinv8cbval = IntVar()
cougarinv9cbval = IntVar()
cougarinv10cbval = IntVar()
cougarinv11cbval = IntVar()
cougarinv12cbval = IntVar()
cougarinv13cbval = IntVar()
cougarinv14cbval = IntVar()
cougarinv15cbval = IntVar()
cougarinv16cbval = IntVar()
cougarinv17cbval = IntVar()
cougarinv18cbval = IntVar()
cougarinv19cbval = IntVar()
cougarinv20cbval = IntVar()
cougarinv21cbval = IntVar()
cougarinv22cbval = IntVar()
cougarinv23cbval = IntVar()
cougarinv24cbval = IntVar()
cougarinv25cbval = IntVar()
cougarinv26cbval = IntVar()
cougarinv27cbval = IntVar()
cougarinv28cbval = IntVar()
cougarinv29cbval = IntVar()
cougarinv30cbval = IntVar()

cherryinv1cbval = IntVar()
cherryinv2cbval = IntVar()
cherryinv3cbval = IntVar()
cherryinv4cbval = IntVar()

harrisoninv1cbval = IntVar()
harrisoninv2cbval = IntVar()
harrisoninv3cbval = IntVar()
harrisoninv4cbval = IntVar()
harrisoninv5cbval = IntVar()
harrisoninv6cbval = IntVar()
harrisoninv7cbval = IntVar()
harrisoninv8cbval = IntVar()
harrisoninv9cbval = IntVar()
harrisoninv10cbval = IntVar()
harrisoninv11cbval = IntVar()
harrisoninv12cbval = IntVar()
harrisoninv13cbval = IntVar()
harrisoninv14cbval = IntVar()
harrisoninv15cbval = IntVar()
harrisoninv16cbval = IntVar()
harrisoninv17cbval = IntVar()
harrisoninv18cbval = IntVar()
harrisoninv19cbval = IntVar()
harrisoninv20cbval = IntVar()
harrisoninv21cbval = IntVar()
harrisoninv22cbval = IntVar()
harrisoninv23cbval = IntVar()
harrisoninv24cbval = IntVar()
harrisoninv25cbval = IntVar()
harrisoninv26cbval = IntVar()
harrisoninv27cbval = IntVar()
harrisoninv28cbval = IntVar()
harrisoninv29cbval = IntVar()
harrisoninv30cbval = IntVar()
harrisoninv31cbval = IntVar()
harrisoninv32cbval = IntVar()
harrisoninv33cbval = IntVar()
harrisoninv34cbval = IntVar()
harrisoninv35cbval = IntVar()
harrisoninv36cbval = IntVar()
harrisoninv37cbval = IntVar()
harrisoninv38cbval = IntVar()
harrisoninv39cbval = IntVar()
harrisoninv40cbval = IntVar()
harrisoninv41cbval = IntVar()
harrisoninv42cbval = IntVar()
harrisoninv43cbval = IntVar()

hayesinv1cbval = IntVar()
hayesinv2cbval = IntVar()
hayesinv3cbval = IntVar()
hayesinv4cbval = IntVar()
hayesinv5cbval = IntVar()
hayesinv6cbval = IntVar()
hayesinv7cbval = IntVar()
hayesinv8cbval = IntVar()
hayesinv9cbval = IntVar()
hayesinv10cbval = IntVar()
hayesinv11cbval = IntVar()
hayesinv12cbval = IntVar()
hayesinv13cbval = IntVar()
hayesinv14cbval = IntVar()
hayesinv15cbval = IntVar()
hayesinv16cbval = IntVar()
hayesinv17cbval = IntVar()
hayesinv18cbval = IntVar()
hayesinv19cbval = IntVar()
hayesinv20cbval = IntVar()
hayesinv21cbval = IntVar()
hayesinv22cbval = IntVar()
hayesinv23cbval = IntVar()
hayesinv24cbval = IntVar()
hayesinv25cbval = IntVar()
hayesinv26cbval = IntVar()

hickoryinv1cbval = IntVar()
hickoryinv2cbval = IntVar()

vanbureninv1cbval = IntVar()
vanbureninv2cbval = IntVar()
vanbureninv3cbval = IntVar()
vanbureninv4cbval = IntVar()
vanbureninv5cbval = IntVar()
vanbureninv6cbval = IntVar()
vanbureninv7cbval = IntVar()
vanbureninv8cbval = IntVar()
vanbureninv9cbval = IntVar()
vanbureninv10cbval = IntVar()
vanbureninv11cbval = IntVar()
vanbureninv12cbval = IntVar()
vanbureninv13cbval = IntVar()
vanbureninv14cbval = IntVar()
vanbureninv15cbval = IntVar()
vanbureninv16cbval = IntVar()
vanbureninv17cbval = IntVar()

violetinv1cbval = IntVar()
violetinv2cbval = IntVar()

wellonsinv1cbval = IntVar()
wellonsinv2cbval = IntVar()
wellonsinv3cbval = IntVar()
wellonsinv4cbval = IntVar()
wellonsinv5cbval = IntVar()
wellonsinv6cbval = IntVar()

bishopvilleIIinv1cbval = IntVar()
bishopvilleIIinv2cbval = IntVar()
bishopvilleIIinv3cbval = IntVar()
bishopvilleIIinv4cbval = IntVar()
bishopvilleIIinv5cbval = IntVar()
bishopvilleIIinv6cbval = IntVar()
bishopvilleIIinv7cbval = IntVar()
bishopvilleIIinv8cbval = IntVar()
bishopvilleIIinv9cbval = IntVar()
bishopvilleIIinv10cbval = IntVar()
bishopvilleIIinv11cbval = IntVar()
bishopvilleIIinv12cbval = IntVar()
bishopvilleIIinv13cbval = IntVar()
bishopvilleIIinv14cbval = IntVar()
bishopvilleIIinv15cbval = IntVar()
bishopvilleIIinv16cbval = IntVar()
bishopvilleIIinv17cbval = IntVar()
bishopvilleIIinv18cbval = IntVar()
bishopvilleIIinv19cbval = IntVar()
bishopvilleIIinv20cbval = IntVar()
bishopvilleIIinv21cbval = IntVar()
bishopvilleIIinv22cbval = IntVar()
bishopvilleIIinv23cbval = IntVar()
bishopvilleIIinv24cbval = IntVar()
bishopvilleIIinv25cbval = IntVar()
bishopvilleIIinv26cbval = IntVar()
bishopvilleIIinv27cbval = IntVar()
bishopvilleIIinv28cbval = IntVar()
bishopvilleIIinv29cbval = IntVar()
bishopvilleIIinv30cbval = IntVar()
bishopvilleIIinv31cbval = IntVar()
bishopvilleIIinv32cbval = IntVar()
bishopvilleIIinv33cbval = IntVar()
bishopvilleIIinv34cbval = IntVar()
bishopvilleIIinv35cbval = IntVar()
bishopvilleIIinv36cbval = IntVar()

hicksoninv1cbval = IntVar()
hicksoninv2cbval = IntVar()
hicksoninv3cbval = IntVar()
hicksoninv4cbval = IntVar()
hicksoninv5cbval = IntVar()
hicksoninv6cbval = IntVar()
hicksoninv7cbval = IntVar()
hicksoninv8cbval = IntVar()
hicksoninv9cbval = IntVar()
hicksoninv10cbval = IntVar()
hicksoninv11cbval = IntVar()
hicksoninv12cbval = IntVar()
hicksoninv13cbval = IntVar()
hicksoninv14cbval = IntVar()
hicksoninv15cbval = IntVar()
hicksoninv16cbval = IntVar()

jeffersoninv1cbval = IntVar()
jeffersoninv2cbval = IntVar()
jeffersoninv3cbval = IntVar()
jeffersoninv4cbval = IntVar()
jeffersoninv5cbval = IntVar()
jeffersoninv6cbval = IntVar()
jeffersoninv7cbval = IntVar()
jeffersoninv8cbval = IntVar()
jeffersoninv9cbval = IntVar()
jeffersoninv10cbval = IntVar()
jeffersoninv11cbval = IntVar()
jeffersoninv12cbval = IntVar()
jeffersoninv13cbval = IntVar()
jeffersoninv14cbval = IntVar()
jeffersoninv15cbval = IntVar()
jeffersoninv16cbval = IntVar()
jeffersoninv17cbval = IntVar()
jeffersoninv18cbval = IntVar()
jeffersoninv19cbval = IntVar()
jeffersoninv20cbval = IntVar()
jeffersoninv21cbval = IntVar()
jeffersoninv22cbval = IntVar()
jeffersoninv23cbval = IntVar()
jeffersoninv24cbval = IntVar()
jeffersoninv25cbval = IntVar()
jeffersoninv26cbval = IntVar()
jeffersoninv27cbval = IntVar()
jeffersoninv28cbval = IntVar()
jeffersoninv29cbval = IntVar()
jeffersoninv30cbval = IntVar()
jeffersoninv31cbval = IntVar()
jeffersoninv32cbval = IntVar()
jeffersoninv33cbval = IntVar()
jeffersoninv34cbval = IntVar()
jeffersoninv35cbval = IntVar()
jeffersoninv36cbval = IntVar()
jeffersoninv37cbval = IntVar()
jeffersoninv38cbval = IntVar()
jeffersoninv39cbval = IntVar()
jeffersoninv40cbval = IntVar()
jeffersoninv41cbval = IntVar()
jeffersoninv42cbval = IntVar()
jeffersoninv43cbval = IntVar()
jeffersoninv44cbval = IntVar()
jeffersoninv45cbval = IntVar()
jeffersoninv46cbval = IntVar()
jeffersoninv47cbval = IntVar()
jeffersoninv48cbval = IntVar()
jeffersoninv49cbval = IntVar()
jeffersoninv50cbval = IntVar()
jeffersoninv51cbval = IntVar()
jeffersoninv52cbval = IntVar()
jeffersoninv53cbval = IntVar()
jeffersoninv54cbval = IntVar()
jeffersoninv55cbval = IntVar()
jeffersoninv56cbval = IntVar()
jeffersoninv57cbval = IntVar()
jeffersoninv58cbval = IntVar()
jeffersoninv59cbval = IntVar()
jeffersoninv60cbval = IntVar()
jeffersoninv61cbval = IntVar()
jeffersoninv62cbval = IntVar()
jeffersoninv63cbval = IntVar()
jeffersoninv64cbval = IntVar()

marshallinv1cbval = IntVar()
marshallinv2cbval = IntVar()
marshallinv3cbval = IntVar()
marshallinv4cbval = IntVar()
marshallinv5cbval = IntVar()
marshallinv6cbval = IntVar()
marshallinv7cbval = IntVar()
marshallinv8cbval = IntVar()
marshallinv9cbval = IntVar()
marshallinv10cbval = IntVar()
marshallinv11cbval = IntVar()
marshallinv12cbval = IntVar()
marshallinv13cbval = IntVar()
marshallinv14cbval = IntVar()
marshallinv15cbval = IntVar()
marshallinv16cbval = IntVar()

mcLeaninv1cbval = IntVar()
mcLeaninv2cbval = IntVar()
mcLeaninv3cbval = IntVar()
mcLeaninv4cbval = IntVar()
mcLeaninv5cbval = IntVar()
mcLeaninv6cbval = IntVar()
mcLeaninv7cbval = IntVar()
mcLeaninv8cbval = IntVar()
mcLeaninv9cbval = IntVar()
mcLeaninv10cbval = IntVar()
mcLeaninv11cbval = IntVar()
mcLeaninv12cbval = IntVar()
mcLeaninv13cbval = IntVar()
mcLeaninv14cbval = IntVar()
mcLeaninv15cbval = IntVar()
mcLeaninv16cbval = IntVar()
mcLeaninv17cbval = IntVar()
mcLeaninv18cbval = IntVar()
mcLeaninv19cbval = IntVar()
mcLeaninv20cbval = IntVar()
mcLeaninv21cbval = IntVar()
mcLeaninv22cbval = IntVar()
mcLeaninv23cbval = IntVar()
mcLeaninv24cbval = IntVar()
mcLeaninv25cbval = IntVar()
mcLeaninv26cbval = IntVar()
mcLeaninv27cbval = IntVar()
mcLeaninv28cbval = IntVar()
mcLeaninv29cbval = IntVar()
mcLeaninv30cbval = IntVar()
mcLeaninv31cbval = IntVar()
mcLeaninv32cbval = IntVar()
mcLeaninv33cbval = IntVar()
mcLeaninv34cbval = IntVar()
mcLeaninv35cbval = IntVar()
mcLeaninv36cbval = IntVar()
mcLeaninv37cbval = IntVar()
mcLeaninv38cbval = IntVar()
mcLeaninv39cbval = IntVar()
mcLeaninv40cbval = IntVar()

ogburninv1cbval = IntVar()
ogburninv2cbval = IntVar()
ogburninv3cbval = IntVar()
ogburninv4cbval = IntVar()
ogburninv5cbval = IntVar()
ogburninv6cbval = IntVar()
ogburninv7cbval = IntVar()
ogburninv8cbval = IntVar()
ogburninv9cbval = IntVar()
ogburninv10cbval = IntVar()
ogburninv11cbval = IntVar()
ogburninv12cbval = IntVar()
ogburninv13cbval = IntVar()
ogburninv14cbval = IntVar()
ogburninv15cbval = IntVar()
ogburninv16cbval = IntVar()

tedderinv1cbval = IntVar()
tedderinv2cbval = IntVar()
tedderinv3cbval = IntVar()
tedderinv4cbval = IntVar()
tedderinv5cbval = IntVar()
tedderinv6cbval = IntVar()
tedderinv7cbval = IntVar()
tedderinv8cbval = IntVar()
tedderinv9cbval = IntVar()
tedderinv10cbval = IntVar()
tedderinv11cbval = IntVar()
tedderinv12cbval = IntVar()
tedderinv13cbval = IntVar()
tedderinv14cbval = IntVar()
tedderinv15cbval = IntVar()
tedderinv16cbval = IntVar()

thunderheadinv1cbval = IntVar()
thunderheadinv2cbval = IntVar()
thunderheadinv3cbval = IntVar()
thunderheadinv4cbval = IntVar()
thunderheadinv5cbval = IntVar()
thunderheadinv6cbval = IntVar()
thunderheadinv7cbval = IntVar()
thunderheadinv8cbval = IntVar()
thunderheadinv9cbval = IntVar()
thunderheadinv10cbval = IntVar()
thunderheadinv11cbval = IntVar()
thunderheadinv12cbval = IntVar()
thunderheadinv13cbval = IntVar()
thunderheadinv14cbval = IntVar()
thunderheadinv15cbval = IntVar()
thunderheadinv16cbval = IntVar()

bulloch1ainv1cbval = IntVar()
bulloch1ainv2cbval = IntVar()
bulloch1ainv3cbval = IntVar()
bulloch1ainv4cbval = IntVar()
bulloch1ainv5cbval = IntVar()
bulloch1ainv6cbval = IntVar()
bulloch1ainv7cbval = IntVar()
bulloch1ainv8cbval = IntVar()
bulloch1ainv9cbval = IntVar()
bulloch1ainv10cbval = IntVar()
bulloch1ainv11cbval = IntVar()
bulloch1ainv12cbval = IntVar()
bulloch1ainv13cbval = IntVar()
bulloch1ainv14cbval = IntVar()
bulloch1ainv15cbval = IntVar()
bulloch1ainv16cbval = IntVar()
bulloch1ainv17cbval = IntVar()
bulloch1ainv18cbval = IntVar()
bulloch1ainv19cbval = IntVar()
bulloch1ainv20cbval = IntVar()
bulloch1ainv21cbval = IntVar()
bulloch1ainv22cbval = IntVar()
bulloch1ainv23cbval = IntVar()
bulloch1ainv24cbval = IntVar()

bulloch1binv1cbval = IntVar()
bulloch1binv2cbval = IntVar()
bulloch1binv3cbval = IntVar()
bulloch1binv4cbval = IntVar()
bulloch1binv5cbval = IntVar()
bulloch1binv6cbval = IntVar()
bulloch1binv7cbval = IntVar()
bulloch1binv8cbval = IntVar()
bulloch1binv9cbval = IntVar()
bulloch1binv10cbval = IntVar()
bulloch1binv11cbval = IntVar()
bulloch1binv12cbval = IntVar()
bulloch1binv13cbval = IntVar()
bulloch1binv14cbval = IntVar()
bulloch1binv15cbval = IntVar()
bulloch1binv16cbval = IntVar()
bulloch1binv17cbval = IntVar()
bulloch1binv18cbval = IntVar()
bulloch1binv19cbval = IntVar()
bulloch1binv20cbval = IntVar()
bulloch1binv21cbval = IntVar()
bulloch1binv22cbval = IntVar()
bulloch1binv23cbval = IntVar()
bulloch1binv24cbval = IntVar()

elkinv1cbval = IntVar()
elkinv2cbval = IntVar()
elkinv3cbval = IntVar()
elkinv4cbval = IntVar()
elkinv5cbval = IntVar()
elkinv6cbval = IntVar()
elkinv7cbval = IntVar()
elkinv8cbval = IntVar()
elkinv9cbval = IntVar()
elkinv10cbval = IntVar()
elkinv11cbval = IntVar()
elkinv12cbval = IntVar()
elkinv13cbval = IntVar()
elkinv14cbval = IntVar()
elkinv15cbval = IntVar()
elkinv16cbval = IntVar()
elkinv17cbval = IntVar()
elkinv18cbval = IntVar()
elkinv19cbval = IntVar()
elkinv20cbval = IntVar()
elkinv21cbval = IntVar()
elkinv22cbval = IntVar()
elkinv23cbval = IntVar()
elkinv24cbval = IntVar()
elkinv25cbval = IntVar()
elkinv26cbval = IntVar()
elkinv27cbval = IntVar()
elkinv28cbval = IntVar()
elkinv29cbval = IntVar()
elkinv30cbval = IntVar()
elkinv31cbval = IntVar()
elkinv32cbval = IntVar()
elkinv33cbval = IntVar()
elkinv34cbval = IntVar()
elkinv35cbval = IntVar()
elkinv36cbval = IntVar()
elkinv37cbval = IntVar()
elkinv38cbval = IntVar()
elkinv39cbval = IntVar()
elkinv40cbval = IntVar()
elkinv41cbval = IntVar()
elkinv42cbval = IntVar()
elkinv43cbval = IntVar()

grayfoxinv1cbval = IntVar()
grayfoxinv2cbval = IntVar()
grayfoxinv3cbval = IntVar()
grayfoxinv4cbval = IntVar()
grayfoxinv5cbval = IntVar()
grayfoxinv6cbval = IntVar()
grayfoxinv7cbval = IntVar()
grayfoxinv8cbval = IntVar()
grayfoxinv9cbval = IntVar()
grayfoxinv10cbval = IntVar()
grayfoxinv11cbval = IntVar()
grayfoxinv12cbval = IntVar()
grayfoxinv13cbval = IntVar()
grayfoxinv14cbval = IntVar()
grayfoxinv15cbval = IntVar()
grayfoxinv16cbval = IntVar()
grayfoxinv17cbval = IntVar()
grayfoxinv18cbval = IntVar()
grayfoxinv19cbval = IntVar()
grayfoxinv20cbval = IntVar()
grayfoxinv21cbval = IntVar()
grayfoxinv22cbval = IntVar()
grayfoxinv23cbval = IntVar()
grayfoxinv24cbval = IntVar()
grayfoxinv25cbval = IntVar()
grayfoxinv26cbval = IntVar()
grayfoxinv27cbval = IntVar()
grayfoxinv28cbval = IntVar()
grayfoxinv29cbval = IntVar()
grayfoxinv30cbval = IntVar()
grayfoxinv31cbval = IntVar()
grayfoxinv32cbval = IntVar()
grayfoxinv33cbval = IntVar()
grayfoxinv34cbval = IntVar()
grayfoxinv35cbval = IntVar()
grayfoxinv36cbval = IntVar()
grayfoxinv37cbval = IntVar()
grayfoxinv38cbval = IntVar()
grayfoxinv39cbval = IntVar()
grayfoxinv40cbval = IntVar()

hardinginv1cbval = IntVar()
hardinginv2cbval = IntVar()
hardinginv3cbval = IntVar()
hardinginv4cbval = IntVar()
hardinginv5cbval = IntVar()
hardinginv6cbval = IntVar()
hardinginv7cbval = IntVar()
hardinginv8cbval = IntVar()
hardinginv9cbval = IntVar()
hardinginv10cbval = IntVar()
hardinginv11cbval = IntVar()
hardinginv12cbval = IntVar()
hardinginv13cbval = IntVar()
hardinginv14cbval = IntVar()
hardinginv15cbval = IntVar()
hardinginv16cbval = IntVar()
hardinginv17cbval = IntVar()
hardinginv18cbval = IntVar()
hardinginv19cbval = IntVar()
hardinginv20cbval = IntVar()
hardinginv21cbval = IntVar()
hardinginv22cbval = IntVar()
hardinginv23cbval = IntVar()
hardinginv24cbval = IntVar()

richmondinv1cbval = IntVar()
richmondinv2cbval = IntVar()
richmondinv3cbval = IntVar()
richmondinv4cbval = IntVar()
richmondinv5cbval = IntVar()
richmondinv6cbval = IntVar()
richmondinv7cbval = IntVar()
richmondinv8cbval = IntVar()
richmondinv9cbval = IntVar()
richmondinv10cbval = IntVar()
richmondinv11cbval = IntVar()
richmondinv12cbval = IntVar()
richmondinv13cbval = IntVar()
richmondinv14cbval = IntVar()
richmondinv15cbval = IntVar()
richmondinv16cbval = IntVar()
richmondinv17cbval = IntVar()
richmondinv18cbval = IntVar()
richmondinv19cbval = IntVar()
richmondinv20cbval = IntVar()
richmondinv21cbval = IntVar()
richmondinv22cbval = IntVar()
richmondinv23cbval = IntVar()
richmondinv24cbval = IntVar()

shorthorninv1cbval = IntVar()
shorthorninv2cbval = IntVar()
shorthorninv3cbval = IntVar()
shorthorninv4cbval = IntVar()
shorthorninv5cbval = IntVar()
shorthorninv6cbval = IntVar()
shorthorninv7cbval = IntVar()
shorthorninv8cbval = IntVar()
shorthorninv9cbval = IntVar()
shorthorninv10cbval = IntVar()
shorthorninv11cbval = IntVar()
shorthorninv12cbval = IntVar()
shorthorninv13cbval = IntVar()
shorthorninv14cbval = IntVar()
shorthorninv15cbval = IntVar()
shorthorninv16cbval = IntVar()
shorthorninv17cbval = IntVar()
shorthorninv18cbval = IntVar()
shorthorninv19cbval = IntVar()
shorthorninv20cbval = IntVar()
shorthorninv21cbval = IntVar()
shorthorninv22cbval = IntVar()
shorthorninv23cbval = IntVar()
shorthorninv24cbval = IntVar()
shorthorninv25cbval = IntVar()
shorthorninv26cbval = IntVar()
shorthorninv27cbval = IntVar()
shorthorninv28cbval = IntVar()
shorthorninv29cbval = IntVar()
shorthorninv30cbval = IntVar()
shorthorninv31cbval = IntVar()
shorthorninv32cbval = IntVar()
shorthorninv33cbval = IntVar()
shorthorninv34cbval = IntVar()
shorthorninv35cbval = IntVar()
shorthorninv36cbval = IntVar()
shorthorninv37cbval = IntVar()
shorthorninv38cbval = IntVar()
shorthorninv39cbval = IntVar()
shorthorninv40cbval = IntVar()
shorthorninv41cbval = IntVar()
shorthorninv42cbval = IntVar()
shorthorninv43cbval = IntVar()
shorthorninv44cbval = IntVar()
shorthorninv45cbval = IntVar()
shorthorninv46cbval = IntVar()
shorthorninv47cbval = IntVar()
shorthorninv48cbval = IntVar()
shorthorninv49cbval = IntVar()
shorthorninv50cbval = IntVar()
shorthorninv51cbval = IntVar()
shorthorninv52cbval = IntVar()
shorthorninv53cbval = IntVar()
shorthorninv54cbval = IntVar()
shorthorninv55cbval = IntVar()
shorthorninv56cbval = IntVar()
shorthorninv57cbval = IntVar()
shorthorninv58cbval = IntVar()
shorthorninv59cbval = IntVar()
shorthorninv60cbval = IntVar()
shorthorninv61cbval = IntVar()
shorthorninv62cbval = IntVar()
shorthorninv63cbval = IntVar()
shorthorninv64cbval = IntVar()
shorthorninv65cbval = IntVar()
shorthorninv66cbval = IntVar()
shorthorninv67cbval = IntVar()
shorthorninv68cbval = IntVar()
shorthorninv69cbval = IntVar()
shorthorninv70cbval = IntVar()
shorthorninv71cbval = IntVar()
shorthorninv72cbval = IntVar()

sunflowerinv1cbval = IntVar()
sunflowerinv2cbval = IntVar()
sunflowerinv3cbval = IntVar()
sunflowerinv4cbval = IntVar()
sunflowerinv5cbval = IntVar()
sunflowerinv6cbval = IntVar()
sunflowerinv7cbval = IntVar()
sunflowerinv8cbval = IntVar()
sunflowerinv9cbval = IntVar()
sunflowerinv10cbval = IntVar()
sunflowerinv11cbval = IntVar()
sunflowerinv12cbval = IntVar()
sunflowerinv13cbval = IntVar()
sunflowerinv14cbval = IntVar()
sunflowerinv15cbval = IntVar()
sunflowerinv16cbval = IntVar()
sunflowerinv17cbval = IntVar()
sunflowerinv18cbval = IntVar()
sunflowerinv19cbval = IntVar()
sunflowerinv20cbval = IntVar()
sunflowerinv21cbval = IntVar()
sunflowerinv22cbval = IntVar()
sunflowerinv23cbval = IntVar()
sunflowerinv24cbval = IntVar()
sunflowerinv25cbval = IntVar()
sunflowerinv26cbval = IntVar()
sunflowerinv27cbval = IntVar()
sunflowerinv28cbval = IntVar()
sunflowerinv29cbval = IntVar()
sunflowerinv30cbval = IntVar()
sunflowerinv31cbval = IntVar()
sunflowerinv32cbval = IntVar()
sunflowerinv33cbval = IntVar()
sunflowerinv34cbval = IntVar()
sunflowerinv35cbval = IntVar()
sunflowerinv36cbval = IntVar()
sunflowerinv37cbval = IntVar()
sunflowerinv38cbval = IntVar()
sunflowerinv39cbval = IntVar()
sunflowerinv40cbval = IntVar()
sunflowerinv41cbval = IntVar()
sunflowerinv42cbval = IntVar()
sunflowerinv43cbval = IntVar()
sunflowerinv44cbval = IntVar()
sunflowerinv45cbval = IntVar()
sunflowerinv46cbval = IntVar()
sunflowerinv47cbval = IntVar()
sunflowerinv48cbval = IntVar()
sunflowerinv49cbval = IntVar()
sunflowerinv50cbval = IntVar()
sunflowerinv51cbval = IntVar()
sunflowerinv52cbval = IntVar()
sunflowerinv53cbval = IntVar()
sunflowerinv54cbval = IntVar()
sunflowerinv55cbval = IntVar()
sunflowerinv56cbval = IntVar()
sunflowerinv57cbval = IntVar()
sunflowerinv58cbval = IntVar()
sunflowerinv59cbval = IntVar()
sunflowerinv60cbval = IntVar()
sunflowerinv61cbval = IntVar()
sunflowerinv62cbval = IntVar()
sunflowerinv63cbval = IntVar()
sunflowerinv64cbval = IntVar()
sunflowerinv65cbval = IntVar()
sunflowerinv66cbval = IntVar()
sunflowerinv67cbval = IntVar()
sunflowerinv68cbval = IntVar()
sunflowerinv69cbval = IntVar()
sunflowerinv70cbval = IntVar()
sunflowerinv71cbval = IntVar()
sunflowerinv72cbval = IntVar()
sunflowerinv73cbval = IntVar()
sunflowerinv74cbval = IntVar()
sunflowerinv75cbval = IntVar()
sunflowerinv76cbval = IntVar()
sunflowerinv77cbval = IntVar()
sunflowerinv78cbval = IntVar()
sunflowerinv79cbval = IntVar()
sunflowerinv80cbval = IntVar()

upsoninv1cbval = IntVar()
upsoninv2cbval = IntVar()
upsoninv3cbval = IntVar()
upsoninv4cbval = IntVar()
upsoninv5cbval = IntVar()
upsoninv6cbval = IntVar()
upsoninv7cbval = IntVar()
upsoninv8cbval = IntVar()
upsoninv9cbval = IntVar()
upsoninv10cbval = IntVar()
upsoninv11cbval = IntVar()
upsoninv12cbval = IntVar()
upsoninv13cbval = IntVar()
upsoninv14cbval = IntVar()
upsoninv15cbval = IntVar()
upsoninv16cbval = IntVar()
upsoninv17cbval = IntVar()
upsoninv18cbval = IntVar()
upsoninv19cbval = IntVar()
upsoninv20cbval = IntVar()
upsoninv21cbval = IntVar()
upsoninv22cbval = IntVar()
upsoninv23cbval = IntVar()
upsoninv24cbval = IntVar()

warblerinv1cbval = IntVar()
warblerinv2cbval = IntVar()
warblerinv3cbval = IntVar()
warblerinv4cbval = IntVar()
warblerinv5cbval = IntVar()
warblerinv6cbval = IntVar()
warblerinv7cbval = IntVar()
warblerinv8cbval = IntVar()
warblerinv9cbval = IntVar()
warblerinv10cbval = IntVar()
warblerinv11cbval = IntVar()
warblerinv12cbval = IntVar()
warblerinv13cbval = IntVar()
warblerinv14cbval = IntVar()
warblerinv15cbval = IntVar()
warblerinv16cbval = IntVar()
warblerinv17cbval = IntVar()
warblerinv18cbval = IntVar()
warblerinv19cbval = IntVar()
warblerinv20cbval = IntVar()
warblerinv21cbval = IntVar()
warblerinv22cbval = IntVar()
warblerinv23cbval = IntVar()
warblerinv24cbval = IntVar()
warblerinv25cbval = IntVar()
warblerinv26cbval = IntVar()
warblerinv27cbval = IntVar()
warblerinv28cbval = IntVar()
warblerinv29cbval = IntVar()
warblerinv30cbval = IntVar()
warblerinv31cbval = IntVar()
warblerinv32cbval = IntVar()

washingtoninv1cbval = IntVar()
washingtoninv2cbval = IntVar()
washingtoninv3cbval = IntVar()
washingtoninv4cbval = IntVar()
washingtoninv5cbval = IntVar()
washingtoninv6cbval = IntVar()
washingtoninv7cbval = IntVar()
washingtoninv8cbval = IntVar()
washingtoninv9cbval = IntVar()
washingtoninv10cbval = IntVar()
washingtoninv11cbval = IntVar()
washingtoninv12cbval = IntVar()
washingtoninv13cbval = IntVar()
washingtoninv14cbval = IntVar()
washingtoninv15cbval = IntVar()
washingtoninv16cbval = IntVar()
washingtoninv17cbval = IntVar()
washingtoninv18cbval = IntVar()
washingtoninv19cbval = IntVar()
washingtoninv20cbval = IntVar()
washingtoninv21cbval = IntVar()
washingtoninv22cbval = IntVar()
washingtoninv23cbval = IntVar()
washingtoninv24cbval = IntVar()
washingtoninv25cbval = IntVar()
washingtoninv26cbval = IntVar()
washingtoninv27cbval = IntVar()
washingtoninv28cbval = IntVar()
washingtoninv29cbval = IntVar()
washingtoninv30cbval = IntVar()
washingtoninv31cbval = IntVar()
washingtoninv32cbval = IntVar()
washingtoninv33cbval = IntVar()
washingtoninv34cbval = IntVar()
washingtoninv35cbval = IntVar()
washingtoninv36cbval = IntVar()
washingtoninv37cbval = IntVar()
washingtoninv38cbval = IntVar()
washingtoninv39cbval = IntVar()
washingtoninv40cbval = IntVar()

whitehallinv1cbval = IntVar()
whitehallinv2cbval = IntVar()
whitehallinv3cbval = IntVar()
whitehallinv4cbval = IntVar()
whitehallinv5cbval = IntVar()
whitehallinv6cbval = IntVar()
whitehallinv7cbval = IntVar()
whitehallinv8cbval = IntVar()
whitehallinv9cbval = IntVar()
whitehallinv10cbval = IntVar()
whitehallinv11cbval = IntVar()
whitehallinv12cbval = IntVar()
whitehallinv13cbval = IntVar()
whitehallinv14cbval = IntVar()
whitehallinv15cbval = IntVar()
whitehallinv16cbval = IntVar()

whitetailinv1cbval = IntVar()
whitetailinv2cbval = IntVar()
whitetailinv3cbval = IntVar()
whitetailinv4cbval = IntVar()
whitetailinv5cbval = IntVar()
whitetailinv6cbval = IntVar()
whitetailinv7cbval = IntVar()
whitetailinv8cbval = IntVar()
whitetailinv9cbval = IntVar()
whitetailinv10cbval = IntVar()
whitetailinv11cbval = IntVar()
whitetailinv12cbval = IntVar()
whitetailinv13cbval = IntVar()
whitetailinv14cbval = IntVar()
whitetailinv15cbval = IntVar()
whitetailinv16cbval = IntVar()
whitetailinv17cbval = IntVar()
whitetailinv18cbval = IntVar()
whitetailinv19cbval = IntVar()
whitetailinv20cbval = IntVar()
whitetailinv21cbval = IntVar()
whitetailinv22cbval = IntVar()
whitetailinv23cbval = IntVar()
whitetailinv24cbval = IntVar()
whitetailinv25cbval = IntVar()
whitetailinv26cbval = IntVar()
whitetailinv27cbval = IntVar()
whitetailinv28cbval = IntVar()
whitetailinv29cbval = IntVar()
whitetailinv30cbval = IntVar()
whitetailinv31cbval = IntVar()
whitetailinv32cbval = IntVar()
whitetailinv33cbval = IntVar()
whitetailinv34cbval = IntVar()
whitetailinv35cbval = IntVar()
whitetailinv36cbval = IntVar()
whitetailinv37cbval = IntVar()
whitetailinv38cbval = IntVar()
whitetailinv39cbval = IntVar()
whitetailinv40cbval = IntVar()
whitetailinv41cbval = IntVar()
whitetailinv42cbval = IntVar()
whitetailinv43cbval = IntVar()
whitetailinv44cbval = IntVar()
whitetailinv45cbval = IntVar()
whitetailinv46cbval = IntVar()
whitetailinv47cbval = IntVar()
whitetailinv48cbval = IntVar()
whitetailinv49cbval = IntVar()
whitetailinv50cbval = IntVar()
whitetailinv51cbval = IntVar()
whitetailinv52cbval = IntVar()
whitetailinv53cbval = IntVar()
whitetailinv54cbval = IntVar()
whitetailinv55cbval = IntVar()
whitetailinv56cbval = IntVar()
whitetailinv57cbval = IntVar()
whitetailinv58cbval = IntVar()
whitetailinv59cbval = IntVar()
whitetailinv60cbval = IntVar()
whitetailinv61cbval = IntVar()
whitetailinv62cbval = IntVar()
whitetailinv63cbval = IntVar()
whitetailinv64cbval = IntVar()
whitetailinv65cbval = IntVar()
whitetailinv66cbval = IntVar()
whitetailinv67cbval = IntVar()
whitetailinv68cbval = IntVar()
whitetailinv69cbval = IntVar()
whitetailinv70cbval = IntVar()
whitetailinv71cbval = IntVar()
whitetailinv72cbval = IntVar()
whitetailinv73cbval = IntVar()
whitetailinv74cbval = IntVar()
whitetailinv75cbval = IntVar()
whitetailinv76cbval = IntVar()
whitetailinv77cbval = IntVar()
whitetailinv78cbval = IntVar()
whitetailinv79cbval = IntVar()
whitetailinv80cbval = IntVar()

conetoeinv1cbval = IntVar()
conetoeinv2cbval = IntVar()
conetoeinv3cbval = IntVar()
conetoeinv4cbval = IntVar()

duplininv1cbval = IntVar()
duplininv2cbval = IntVar()
duplininv3cbval = IntVar()
duplininv4cbval = IntVar()
duplininv5cbval = IntVar()
duplininv6cbval = IntVar()
duplininv7cbval = IntVar()
duplininv8cbval = IntVar()
duplininv9cbval = IntVar()
duplininv10cbval = IntVar()
duplininv11cbval = IntVar()
duplininv12cbval = IntVar()
duplininv13cbval = IntVar()
duplininv14cbval = IntVar()
duplininv15cbval = IntVar()
duplininv16cbval = IntVar()
duplininv17cbval = IntVar()
duplininv18cbval = IntVar()
duplininv19cbval = IntVar()
duplininv20cbval = IntVar()
duplininv21cbval = IntVar()

wayne1inv1cbval = IntVar()
wayne1inv2cbval = IntVar()
wayne1inv3cbval = IntVar()
wayne1inv4cbval = IntVar()

wayne2inv1cbval = IntVar()
wayne2inv2cbval = IntVar()
wayne2inv3cbval = IntVar()
wayne2inv4cbval = IntVar()

wayne3inv1cbval = IntVar()
wayne3inv2cbval = IntVar()
wayne3inv3cbval = IntVar()
wayne3inv4cbval = IntVar()

freightlineinv1cbval = IntVar()
freightlineinv2cbval = IntVar()
freightlineinv3cbval = IntVar()
freightlineinv4cbval = IntVar()
freightlineinv5cbval = IntVar()
freightlineinv6cbval = IntVar()
freightlineinv7cbval = IntVar()
freightlineinv8cbval = IntVar()
freightlineinv9cbval = IntVar()
freightlineinv10cbval = IntVar()
freightlineinv11cbval = IntVar()
freightlineinv12cbval = IntVar()
freightlineinv13cbval = IntVar()
freightlineinv14cbval = IntVar()
freightlineinv15cbval = IntVar()
freightlineinv16cbval = IntVar()
freightlineinv17cbval = IntVar()
freightlineinv18cbval = IntVar()

hollyswampinv1cbval = IntVar()
hollyswampinv2cbval = IntVar()
hollyswampinv3cbval = IntVar()
hollyswampinv4cbval = IntVar()
hollyswampinv5cbval = IntVar()
hollyswampinv6cbval = IntVar()
hollyswampinv7cbval = IntVar()
hollyswampinv8cbval = IntVar()
hollyswampinv9cbval = IntVar()
hollyswampinv10cbval = IntVar()
hollyswampinv11cbval = IntVar()
hollyswampinv12cbval = IntVar()
hollyswampinv13cbval = IntVar()
hollyswampinv14cbval = IntVar()
hollyswampinv15cbval = IntVar()
hollyswampinv16cbval = IntVar()

pginv1cbval = IntVar()
pginv2cbval = IntVar()
pginv3cbval = IntVar()
pginv4cbval = IntVar()
pginv5cbval = IntVar()
pginv6cbval = IntVar()
pginv7cbval = IntVar()
pginv8cbval = IntVar()
pginv9cbval = IntVar()
pginv10cbval = IntVar()
pginv11cbval = IntVar()
pginv12cbval = IntVar()
pginv13cbval = IntVar()
pginv14cbval = IntVar()
pginv15cbval = IntVar()
pginv16cbval = IntVar()
pginv17cbval = IntVar()
pginv18cbval = IntVar()

bishopvilleIImetercbval = IntVar()
bluebirdmetercbval = IntVar()
bulloch1ametercbval = IntVar()
bulloch1bmetercbval = IntVar()
cardinalmetercbval = IntVar()
cdiametercbval = IntVar()
cherrymetercbval = IntVar()
cougarmetercbval = IntVar()
conetoemetercbval = IntVar()
duplinmetercbval = IntVar()
elkmetercbval = IntVar()
freightlinemetercbval = IntVar()
grayfoxmetercbval = IntVar()
hardingmetercbval = IntVar()
harrisonmetercbval = IntVar()
hayesmetercbval = IntVar()
hickorymetercbval = IntVar()
hicksonmetercbval = IntVar()
hollyswampmetercbval = IntVar()
jeffersonmetercbval = IntVar()
marshallmetercbval = IntVar()
mcLeanmetercbval = IntVar()
ogburnmetercbval = IntVar()
pgmetercbval = IntVar()
richmondmetercbval = IntVar()
shorthornmetercbval = IntVar()
sunflowermetercbval = IntVar()
teddermetercbval = IntVar()
thunderheadmetercbval = IntVar()
upsonmetercbval = IntVar()
vanburenmetercbval = IntVar()
violetmetercbval = IntVar()
warblermetercbval = IntVar()
washingtonmetercbval = IntVar()
wayne1metercbval = IntVar()
wayne2metercbval = IntVar()
wayne3metercbval = IntVar()
wellonsmetercbval = IntVar()
whitetailmetercbval = IntVar()
whitehallmetercbval = IntVar()

bishopvilleIIPOAcbval = IntVar()
bluebirdPOAcbval = IntVar()
bulloch1aPOAcbval = IntVar()
bulloch1bPOAcbval = IntVar()
cardinalPOAcbval = IntVar()
cdiaPOAcbval = IntVar()
cherryPOAcbval = IntVar()
cougarPOAcbval = IntVar()
conetoePOAcbval = IntVar()
duplinPOAcbval = IntVar()
elkPOAcbval = IntVar()
freightlinePOAcbval = IntVar()
grayfoxPOAcbval = IntVar()
hardingPOAcbval = IntVar()
harrisonPOAcbval = IntVar()
hayesPOAcbval = IntVar()
hickoryPOAcbval = IntVar()
hicksonPOAcbval = IntVar()
hollyswampPOAcbval = IntVar()
jeffersonPOAcbval = IntVar()
marshallPOAcbval = IntVar()
mcLeanPOAcbval = IntVar()
ogburnPOAcbval = IntVar()
pgPOAcbval = IntVar()
richmondPOAcbval = IntVar()
shorthornPOAcbval = IntVar()
sunflowerPOAcbval = IntVar()
tedderPOAcbval = IntVar()
thunderheadPOAcbval = IntVar()
upsonPOAcbval = IntVar()
vanburenPOAcbval = IntVar()
violetPOAcbval = IntVar()
warblerPOAcbval = IntVar()
washingtonPOAcbval = IntVar()
wayne1POAcbval = IntVar()
wayne2POAcbval = IntVar()
wayne3POAcbval = IntVar()
wellonsPOAcbval = IntVar()
whitetailPOAcbval = IntVar()
whitehallPOAcbval = IntVar()



#NARENCO Window
site2Label = Label(narenco, text= "Sites:")
site2Label.grid(row=0, column= 0)

narencoinv1Label= Label(narenco, text= "Inverter 1")
narencoinv1Label.grid(row=1, column= 0, sticky=W)

narencoinv2Label = Label(narenco, text="Inverter 2")
narencoinv2Label.grid(row=2, column=0, sticky=W)

narencoinv3Label = Label(narenco, text="Inverter 3")
narencoinv3Label.grid(row=3, column=0, sticky=W)

narencoinv4Label = Label(narenco, text="Inverter 4")
narencoinv4Label.grid(row=4, column=0, sticky=W)

narencoinv5Label = Label(narenco, text="Inverter 5")
narencoinv5Label.grid(row=5, column=0, sticky=W)

narencoinv6Label = Label(narenco, text="Inverter 6")
narencoinv6Label.grid(row=6, column=0, sticky=W)

narencoinv7Label = Label(narenco, text="Inverter 7")
narencoinv7Label.grid(row=7, column=0, sticky=W)

narencoinv8Label = Label(narenco, text="Inverter 8")
narencoinv8Label.grid(row=8, column=0, sticky=W)

narencoinv9Label = Label(narenco, text="Inverter 9")
narencoinv9Label.grid(row=9, column=0, sticky=W)

narencoinv10Label = Label(narenco, text="Inverter 10")
narencoinv10Label.grid(row=10, column=0, sticky=W)

narencoinv11Label = Label(narenco, text="Inverter 11")
narencoinv11Label.grid(row=11, column=0, sticky=W)

# Inverter 12
narencoinv12Label = Label(narenco, text="Inverter 12")
narencoinv12Label.grid(row=12, column=0, sticky=W)

# Inverter 13
narencoinv13Label = Label(narenco, text="Inverter 13")
narencoinv13Label.grid(row=13, column=0, sticky=W)

# Inverter 14
narencoinv14Label = Label(narenco, text="Inverter 14")
narencoinv14Label.grid(row=14, column=0, sticky=W)

# Inverter 15
narencoinv15Label = Label(narenco, text="Inverter 15")
narencoinv15Label.grid(row=15, column=0, sticky=W)

# Inverter 16
narencoinv16Label = Label(narenco, text="Inverter 16")
narencoinv16Label.grid(row=16, column=0, sticky=W)

# Inverter 17
narencoinv17Label = Label(narenco, text="Inverter 17")
narencoinv17Label.grid(row=17, column=0, sticky=W)

# Inverter 18
narencoinv18Label = Label(narenco, text="Inverter 18")
narencoinv18Label.grid(row=18, column=0, sticky=W)

# Inverter 19
narencoinv19Label = Label(narenco, text="Inverter 19")
narencoinv19Label.grid(row=19, column=0, sticky=W)

# Inverter 20
narencoinv20Label = Label(narenco, text="Inverter 20")
narencoinv20Label.grid(row=20, column=0, sticky=W)

narencoinv21Label = Label(narenco, text="Inverter 21")
narencoinv21Label.grid(row=21, column=0, sticky=W)

# Inverter 22
narencoinv22Label = Label(narenco, text="Inverter 22")
narencoinv22Label.grid(row=22, column=0, sticky=W)

# Inverter 23
narencoinv23Label = Label(narenco, text="Inverter 23")
narencoinv23Label.grid(row=23, column=0, sticky=W)

# Inverter 24
narencoinv24Label = Label(narenco, text="Inverter 24")
narencoinv24Label.grid(row=24, column=0, sticky=W)

# Inverter 25
narencoinv25Label = Label(narenco, text="Inverter 25")
narencoinv25Label.grid(row=25, column=0, sticky=W)

# Inverter 26
narencoinv26Label = Label(narenco, text="Inverter 26")
narencoinv26Label.grid(row=26, column=0, sticky=W)

# Inverter 27
narencoinv27Label = Label(narenco, text="Inverter 27")
narencoinv27Label.grid(row=27, column=0, sticky=W)

# Inverter 28
narencoinv28Label = Label(narenco, text="Inverter 28")
narencoinv28Label.grid(row=28, column=0, sticky=W)

# Inverter 29
narencoinv29Label = Label(narenco, text="Inverter 29")
narencoinv29Label.grid(row=29, column=0, sticky=W)

# Inverter 30
narencoinv30Label = Label(narenco, text="Inverter 30")
narencoinv30Label.grid(row=30, column=0, sticky=W)

narencoinv31Label = Label(narenco, text="Inverter 31")
narencoinv31Label.grid(row=31, column=0, sticky=W)

# Inverter 32
narencoinv32Label = Label(narenco, text="Inverter 32")
narencoinv32Label.grid(row=32, column=0, sticky=W)

# Inverter 33
narencoinv33Label = Label(narenco, text="Inverter 33")
narencoinv33Label.grid(row=33, column=0, sticky=W)

# Inverter 34
narencoinv34Label = Label(narenco, text="Inverter 34")
narencoinv34Label.grid(row=34, column=0, sticky=W)

# Inverter 35
narencoinv35Label = Label(narenco, text="Inverter 35")
narencoinv35Label.grid(row=35, column=0, sticky=W)

# Inverter 36
narencoinv36Label = Label(narenco, text="Inverter 36")
narencoinv36Label.grid(row=36, column=0, sticky=W)

# Inverter 37
narencoinv37Label = Label(narenco, text="Inverter 37")
narencoinv37Label.grid(row=37, column=0, sticky=W)

# Inverter 38
narencoinv38Label = Label(narenco, text="Inverter 38")
narencoinv38Label.grid(row=38, column=0, sticky=W)

# Inverter 39
narencoinv39Label = Label(narenco, text="Inverter 39")
narencoinv39Label.grid(row=39, column=0, sticky=W)

# Inverter 40
narencoinv40Label = Label(narenco, text="Inverter 40")
narencoinv40Label.grid(row=40, column=0, sticky=W)

narencoinv41Label = Label(narenco, text="Inverter 41")
narencoinv41Label.grid(row=41, column=0, sticky=W)

# Inverter 42
narencoinv42Label = Label(narenco, text="Inverter 42")
narencoinv42Label.grid(row=42, column=0, sticky=W)

# Inverter 43
narencoinv43Label = Label(narenco, text="Inverter 43")
narencoinv43Label.grid(row=43, column=0, sticky=W)

# Inverter 44
narencoinv44Label = Label(narenco, text="Inverter 44")
narencoinv44Label.grid(row=44, column=0, sticky=W)

# Inverter 45
narencoinv45Label = Label(narenco, text="Inverter 45")
narencoinv45Label.grid(row=45, column=0, sticky=W)

# Inverter 46
narencoinv46Label = Label(narenco, text="Inverter 46")
narencoinv46Label.grid(row=46, column=0, sticky=W)

# Inverter 47
narencoinv47Label = Label(narenco, text="Inverter 47")
narencoinv47Label.grid(row=47, column=0, sticky=W)

# Inverter 48
narencoinv48Label = Label(narenco, text="Inverter 48")
narencoinv48Label.grid(row=48, column=0, sticky=W)

# Inverter 49
narencoinv49Label = Label(narenco, text="Inverter 49")
narencoinv49Label.grid(row=49, column=0, sticky=W)

# Inverter 50
narencoinv50Label = Label(narenco, text="Inverter 50")
narencoinv50Label.grid(row=50, column=0, sticky=W)

# Inverter 51
narencoinv51Label = Label(narenco, text="Inverter 51")
narencoinv51Label.grid(row=51, column=0, sticky=W)

# Inverter 52
narencoinv52Label = Label(narenco, text="Inverter 52")
narencoinv52Label.grid(row=52, column=0, sticky=W)

# Inverter 53
narencoinv53Label = Label(narenco, text="Inverter 53")
narencoinv53Label.grid(row=53, column=0, sticky=W)

# Inverter 54
narencoinv54Label = Label(narenco, text="Inverter 54")
narencoinv54Label.grid(row=54, column=0, sticky=W)

# Inverter 55
narencoinv55Label = Label(narenco, text="Inverter 55")
narencoinv55Label.grid(row=55, column=0, sticky=W)

# Inverter 56
narencoinv56Label = Label(narenco, text="Inverter 56")
narencoinv56Label.grid(row=56, column=0, sticky=W)

# Inverter 57
narencoinv57Label = Label(narenco, text="Inverter 57")
narencoinv57Label.grid(row=57, column=0, sticky=W)

# Inverter 58
narencoinv58Label = Label(narenco, text="Inverter 58")
narencoinv58Label.grid(row=58, column=0, sticky=W)

# Inverter 59
narencoinv59Label = Label(narenco, text="Inverter 59")
narencoinv59Label.grid(row=59, column=0, sticky=W)
#SolRiver Window
site3Label = Label(solrvr, text= "Sites:")
site3Label.grid(row=0, column= 0)
solrvrinv1Label= Label(solrvr, text= "Inverter 1")
solrvrinv1Label.grid(row=1, column= 0, sticky=W)

solrvrinv2Label = Label(solrvr, text="Inverter 2")
solrvrinv2Label.grid(row=2, column=0, sticky=W)

solrvrinv3Label = Label(solrvr, text="Inverter 3")
solrvrinv3Label.grid(row=3, column=0, sticky=W)

solrvrinv4Label = Label(solrvr, text="Inverter 4")
solrvrinv4Label.grid(row=4, column=0, sticky=W)

solrvrinv5Label = Label(solrvr, text="Inverter 5")
solrvrinv5Label.grid(row=5, column=0, sticky=W)

solrvrinv6Label = Label(solrvr, text="Inverter 6")
solrvrinv6Label.grid(row=6, column=0, sticky=W)

solrvrinv7Label = Label(solrvr, text="Inverter 7")
solrvrinv7Label.grid(row=7, column=0, sticky=W)

solrvrinv8Label = Label(solrvr, text="Inverter 8")
solrvrinv8Label.grid(row=8, column=0, sticky=W)

solrvrinv9Label = Label(solrvr, text="Inverter 9")
solrvrinv9Label.grid(row=9, column=0, sticky=W)

solrvrinv10Label = Label(solrvr, text="Inverter 10")
solrvrinv10Label.grid(row=10, column=0, sticky=W)

solrvrinv11Label = Label(solrvr, text="Inverter 11")
solrvrinv11Label.grid(row=11, column=0, sticky=W)

# Inverter 12
solrvrinv12Label = Label(solrvr, text="Inverter 12")
solrvrinv12Label.grid(row=12, column=0, sticky=W)

# Inverter 13
solrvrinv13Label = Label(solrvr, text="Inverter 13")
solrvrinv13Label.grid(row=13, column=0, sticky=W)

# Inverter 14
solrvrinv14Label = Label(solrvr, text="Inverter 14")
solrvrinv14Label.grid(row=14, column=0, sticky=W)

# Inverter 15
solrvrinv15Label = Label(solrvr, text="Inverter 15")
solrvrinv15Label.grid(row=15, column=0, sticky=W)

# Inverter 16
solrvrinv16Label = Label(solrvr, text="Inverter 16")
solrvrinv16Label.grid(row=16, column=0, sticky=W)

# Inverter 17
solrvrinv17Label = Label(solrvr, text="Inverter 17")
solrvrinv17Label.grid(row=17, column=0, sticky=W)

# Inverter 18
solrvrinv18Label = Label(solrvr, text="Inverter 18")
solrvrinv18Label.grid(row=18, column=0, sticky=W)

# Inverter 19
solrvrinv19Label = Label(solrvr, text="Inverter 19")
solrvrinv19Label.grid(row=19, column=0, sticky=W)

# Inverter 20
solrvrinv20Label = Label(solrvr, text="Inverter 20")
solrvrinv20Label.grid(row=20, column=0, sticky=W)

solrvrinv21Label = Label(solrvr, text="Inverter 21")
solrvrinv21Label.grid(row=21, column=0, sticky=W)

# Inverter 22
solrvrinv22Label = Label(solrvr, text="Inverter 22")
solrvrinv22Label.grid(row=22, column=0, sticky=W)

# Inverter 23
solrvrinv23Label = Label(solrvr, text="Inverter 23")
solrvrinv23Label.grid(row=23, column=0, sticky=W)

# Inverter 24
solrvrinv24Label = Label(solrvr, text="Inverter 24")
solrvrinv24Label.grid(row=24, column=0, sticky=W)

# Inverter 25
solrvrinv25Label = Label(solrvr, text="Inverter 25")
solrvrinv25Label.grid(row=25, column=0, sticky=W)

# Inverter 26
solrvrinv26Label = Label(solrvr, text="Inverter 26")
solrvrinv26Label.grid(row=26, column=0, sticky=W)

# Inverter 27
solrvrinv27Label = Label(solrvr, text="Inverter 27")
solrvrinv27Label.grid(row=27, column=0, sticky=W)

# Inverter 28
solrvrinv28Label = Label(solrvr, text="Inverter 28")
solrvrinv28Label.grid(row=28, column=0, sticky=W)

# Inverter 29
solrvrinv29Label = Label(solrvr, text="Inverter 29")
solrvrinv29Label.grid(row=29, column=0, sticky=W)

# Inverter 30
solrvrinv30Label = Label(solrvr, text="Inverter 30")
solrvrinv30Label.grid(row=30, column=0, sticky=W)

solrvrinv31Label = Label(solrvr, text="Inverter 31")
solrvrinv31Label.grid(row=31, column=0, sticky=W)

# Inverter 32
solrvrinv32Label = Label(solrvr, text="Inverter 32")
solrvrinv32Label.grid(row=32, column=0, sticky=W)

# Inverter 33
solrvrinv33Label = Label(solrvr, text="Inverter 33")
solrvrinv33Label.grid(row=33, column=0, sticky=W)

# Inverter 34
solrvrinv34Label = Label(solrvr, text="Inverter 34")
solrvrinv34Label.grid(row=34, column=0, sticky=W)

# Inverter 35
solrvrinv35Label = Label(solrvr, text="Inverter 35")
solrvrinv35Label.grid(row=35, column=0, sticky=W)

# Inverter 36
solrvrinv36Label = Label(solrvr, text="Inverter 36")
solrvrinv36Label.grid(row=36, column=0, sticky=W)

# Inverter 37
solrvrinv37Label = Label(solrvr, text="Inverter 37")
solrvrinv37Label.grid(row=37, column=0, sticky=W)

# Inverter 38
solrvrinv38Label = Label(solrvr, text="Inverter 38")
solrvrinv38Label.grid(row=38, column=0, sticky=W)

# Inverter 39
solrvrinv39Label = Label(solrvr, text="Inverter 39")
solrvrinv39Label.grid(row=39, column=0, sticky=W)

# Inverter 40
solrvrinv40Label = Label(solrvr, text="Inverter 40")
solrvrinv40Label.grid(row=40, column=0, sticky=W)

solrvrinv41Label = Label(solrvr, text="Inverter 41")
solrvrinv41Label.grid(row=41, column=0, sticky=W)

# Inverter 42
solrvrinv42Label = Label(solrvr, text="Inverter 42")
solrvrinv42Label.grid(row=42, column=0, sticky=W)

# Inverter 43
solrvrinv43Label = Label(solrvr, text="Inverter 43")
solrvrinv43Label.grid(row=43, column=0, sticky=W)

# Inverter 44
solrvrinv44Label = Label(solrvr, text="Inverter 44")
solrvrinv44Label.grid(row=44, column=0, sticky=W)

# Inverter 45
solrvrinv45Label = Label(solrvr, text="Inverter 45")
solrvrinv45Label.grid(row=45, column=0, sticky=W)

# Inverter 46
solrvrinv46Label = Label(solrvr, text="Inverter 46")
solrvrinv46Label.grid(row=46, column=0, sticky=W)

# Inverter 47
solrvrinv47Label = Label(solrvr, text="Inverter 47")
solrvrinv47Label.grid(row=47, column=0, sticky=W)

# Inverter 48
solrvrinv48Label = Label(solrvr, text="Inverter 48")
solrvrinv48Label.grid(row=48, column=0, sticky=W)

# Inverter 49
solrvrinv49Label = Label(solrvr, text="Inverter 49")
solrvrinv49Label.grid(row=49, column=0, sticky=W)

# Inverter 50
solrvrinv50Label = Label(solrvr, text="Inverter 50")
solrvrinv50Label.grid(row=50, column=0, sticky=W)

# Inverter 51
solrvrinv51Label = Label(solrvr, text="Inverter 51")
solrvrinv51Label.grid(row=51, column=0, sticky=W)

# Inverter 52
solrvrinv52Label = Label(solrvr, text="Inverter 52")
solrvrinv52Label.grid(row=52, column=0, sticky=W)

# Inverter 53
solrvrinv53Label = Label(solrvr, text="Inverter 53")
solrvrinv53Label.grid(row=53, column=0, sticky=W)

# Inverter 54
solrvrinv54Label = Label(solrvr, text="Inverter 54")
solrvrinv54Label.grid(row=54, column=0, sticky=W)

# Inverter 55
solrvrinv55Label = Label(solrvr, text="Inverter 55")
solrvrinv55Label.grid(row=55, column=0, sticky=W)

# Inverter 56
solrvrinv56Label = Label(solrvr, text="Inverter 56")
solrvrinv56Label.grid(row=56, column=0, sticky=W)

# Inverter 57
solrvrinv57Label = Label(solrvr, text="Inverter 57")
solrvrinv57Label.grid(row=57, column=0, sticky=W)

# Inverter 58
solrvrinv58Label = Label(solrvr, text="Inverter 58")
solrvrinv58Label.grid(row=58, column=0, sticky=W)

# Inverter 59
solrvrinv59Label = Label(solrvr, text="Inverter 59")
solrvrinv59Label.grid(row=59, column=0, sticky=W)

# Inverter 60
solrvrinv60Label = Label(solrvr, text="Inverter 60")
solrvrinv60Label.grid(row=60, column=0, sticky=W)

solrvrinv61Label = Label(solrvr, text="Inverter 61")
solrvrinv61Label.grid(row=61, column=0, sticky=W)

# Inverter 62
solrvrinv62Label = Label(solrvr, text="Inverter 62")
solrvrinv62Label.grid(row=62, column=0, sticky=W)

# Inverter 63
solrvrinv63Label = Label(solrvr, text="Inverter 63")
solrvrinv63Label.grid(row=63, column=0, sticky=W)

# Inverter 64
solrvrinv64Label = Label(solrvr, text="Inverter 64")
solrvrinv64Label.grid(row=64, column=0, sticky=W)

# Inverter 65
solrvrinv65Label = Label(solrvr, text="Inverter 65")
solrvrinv65Label.grid(row=65, column=0, sticky=W)

# Inverter 66
solrvrinv66Label = Label(solrvr, text="Inverter 66")
solrvrinv66Label.grid(row=66, column=0, sticky=W)

# Inverter 67
solrvrinv67Label = Label(solrvr, text="Inverter 67")
solrvrinv67Label.grid(row=67, column=0, sticky=W)

# Inverter 68
solrvrinv68Label = Label(solrvr, text="Inverter 68")
solrvrinv68Label.grid(row=68, column=0, sticky=W)

# Inverter 69
solrvrinv69Label = Label(solrvr, text="Inverter 69")
solrvrinv69Label.grid(row=69, column=0, sticky=W)

# Inverter 70
solrvrinv70Label = Label(solrvr, text="Inverter 70")
solrvrinv70Label.grid(row=70, column=0, sticky=W)

# Inverter 71
solrvrinv71Label = Label(solrvr, text="Inverter 71")
solrvrinv71Label.grid(row=71, column=0, sticky=W)

# Inverter 72
solrvrinv72Label = Label(solrvr, text="Inverter 72")
solrvrinv72Label.grid(row=72, column=0, sticky=W)

# Inverter 73
solrvrinv73Label = Label(solrvr, text="Inverter 73")
solrvrinv73Label.grid(row=73, column=0, sticky=W)

# Inverter 74
solrvrinv74Label = Label(solrvr, text="Inverter 74")
solrvrinv74Label.grid(row=74, column=0, sticky=W)

# Inverter 75
solrvrinv75Label = Label(solrvr, text="Inverter 75")
solrvrinv75Label.grid(row=75, column=0, sticky=W)

# Inverter 76
solrvrinv76Label = Label(solrvr, text="Inverter 76")
solrvrinv76Label.grid(row=76, column=0, sticky=W)

# Inverter 77
solrvrinv77Label = Label(solrvr, text="Inverter 77")
solrvrinv77Label.grid(row=77, column=0, sticky=W)

# Inverter 78
solrvrinv78Label = Label(solrvr, text="Inverter 78")
solrvrinv78Label.grid(row=78, column=0, sticky=W)

# Inverter 79
solrvrinv79Label = Label(solrvr, text="Inverter 79")
solrvrinv79Label.grid(row=79, column=0, sticky=W)

# Inverter 80
solrvrinv80Label = Label(solrvr, text="Inverter 80")
solrvrinv80Label.grid(row=80, column=0, sticky=W)





#Soltage Window
site4Label = Label(soltage, text= "Sites:")
site4Label.grid(row=0, column= 0)

soltageinv1Label= Label(soltage, text= "Inverter 1")
soltageinv1Label.grid(row=1, column= 0, sticky=W)

soltageinv2Label = Label(soltage, text="Inverter 2")
soltageinv2Label.grid(row=2, column=0, sticky=W)

soltageinv3Label = Label(soltage, text="Inverter 3")
soltageinv3Label.grid(row=3, column=0, sticky=W)

soltageinv4Label = Label(soltage, text="Inverter 4")
soltageinv4Label.grid(row=4, column=0, sticky=W)

soltageinv5Label = Label(soltage, text="Inverter 5")
soltageinv5Label.grid(row=5, column=0, sticky=W)

soltageinv6Label = Label(soltage, text="Inverter 6")
soltageinv6Label.grid(row=6, column=0, sticky=W)

soltageinv7Label = Label(soltage, text="Inverter 7")
soltageinv7Label.grid(row=7, column=0, sticky=W)

soltageinv8Label = Label(soltage, text="Inverter 8")
soltageinv8Label.grid(row=8, column=0, sticky=W)

soltageinv9Label = Label(soltage, text="Inverter 9")
soltageinv9Label.grid(row=9, column=0, sticky=W)

soltageinv10Label = Label(soltage, text="Inverter 10")
soltageinv10Label.grid(row=10, column=0, sticky=W)

soltageinv11Label = Label(soltage, text="Inverter 11")
soltageinv11Label.grid(row=11, column=0, sticky=W)

# Inverter 12
soltageinv12Label = Label(soltage, text="Inverter 12")
soltageinv12Label.grid(row=12, column=0, sticky=W)

# Inverter 13
soltageinv13Label = Label(soltage, text="Inverter 13")
soltageinv13Label.grid(row=13, column=0, sticky=W)

# Inverter 14
soltageinv14Label = Label(soltage, text="Inverter 14")
soltageinv14Label.grid(row=14, column=0, sticky=W)

# Inverter 15
soltageinv15Label = Label(soltage, text="Inverter 15")
soltageinv15Label.grid(row=15, column=0, sticky=W)

# Inverter 16
soltageinv16Label = Label(soltage, text="Inverter 16")
soltageinv16Label.grid(row=16, column=0, sticky=W)

# Inverter 17
soltageinv17Label = Label(soltage, text="Inverter 17")
soltageinv17Label.grid(row=17, column=0, sticky=W)

# Inverter 18
soltageinv18Label = Label(soltage, text="Inverter 18")
soltageinv18Label.grid(row=18, column=0, sticky=W)

# Inverter 19
soltageinv19Label = Label(soltage, text="Inverter 19")
soltageinv19Label.grid(row=19, column=0, sticky=W)

# Inverter 20
soltageinv20Label = Label(soltage, text="Inverter 20")
soltageinv20Label.grid(row=20, column=0, sticky=W)

soltageinv21Label = Label(soltage, text="Inverter 21")
soltageinv21Label.grid(row=21, column=0, sticky=W)
#NCEMC Window
site5Label = Label(ncemc, text= "Sites:")
site5Label.grid(row=0, column= 0)
ncemcinv1Label= Label(ncemc, text= "Inverter 1")
ncemcinv1Label.grid(row=1, column= 0, sticky=W)

ncemcinv2Label = Label(ncemc, text="Inverter 2")
ncemcinv2Label.grid(row=2, column=0, sticky=W)

ncemcinv3Label = Label(ncemc, text="Inverter 3")
ncemcinv3Label.grid(row=3, column=0, sticky=W)

ncemcinv4Label = Label(ncemc, text="Inverter 4")
ncemcinv4Label.grid(row=4, column=0, sticky=W)

ncemcinv5Label = Label(ncemc, text="Inverter 5")
ncemcinv5Label.grid(row=5, column=0, sticky=W)

ncemcinv6Label = Label(ncemc, text="Inverter 6")
ncemcinv6Label.grid(row=6, column=0, sticky=W)

ncemcinv7Label = Label(ncemc, text="Inverter 7")
ncemcinv7Label.grid(row=7, column=0, sticky=W)

ncemcinv8Label = Label(ncemc, text="Inverter 8")
ncemcinv8Label.grid(row=8, column=0, sticky=W)

ncemcinv9Label = Label(ncemc, text="Inverter 9")
ncemcinv9Label.grid(row=9, column=0, sticky=W)

ncemcinv10Label = Label(ncemc, text="Inverter 10")
ncemcinv10Label.grid(row=10, column=0, sticky=W)

ncemcinv11Label = Label(ncemc, text="Inverter 11")
ncemcinv11Label.grid(row=11, column=0, sticky=W)

# Inverter 12
ncemcinv12Label = Label(ncemc, text="Inverter 12")
ncemcinv12Label.grid(row=12, column=0, sticky=W)

# Inverter 13
ncemcinv13Label = Label(ncemc, text="Inverter 13")
ncemcinv13Label.grid(row=13, column=0, sticky=W)

# Inverter 14
ncemcinv14Label = Label(ncemc, text="Inverter 14")
ncemcinv14Label.grid(row=14, column=0, sticky=W)

# Inverter 15
ncemcinv15Label = Label(ncemc, text="Inverter 15")
ncemcinv15Label.grid(row=15, column=0, sticky=W)

# Inverter 16
ncemcinv16Label = Label(ncemc, text="Inverter 16")
ncemcinv16Label.grid(row=16, column=0, sticky=W)

# Inverter 17
ncemcinv17Label = Label(ncemc, text="Inverter 17")
ncemcinv17Label.grid(row=17, column=0, sticky=W)

# Inverter 18
ncemcinv18Label = Label(ncemc, text="Inverter 18")
ncemcinv18Label.grid(row=18, column=0, sticky=W)


#Harrison Street Window
siteLabel = Label(inv, text= "Sites:")
siteLabel.grid(row=0, column= 0)

inverter1Label= Label(inv, text= "Inverter 1")
inverter1Label.grid(row=1, column= 0, sticky=W)

inverter2Label = Label(inv, text="Inverter 2")
inverter2Label.grid(row=2, column=0, sticky=W)

inverter3Label = Label(inv, text="Inverter 3")
inverter3Label.grid(row=3, column=0, sticky=W)

inverter4Label = Label(inv, text="Inverter 4")
inverter4Label.grid(row=4, column=0, sticky=W)

inverter5Label = Label(inv, text="Inverter 5")
inverter5Label.grid(row=5, column=0, sticky=W)

inverter6Label = Label(inv, text="Inverter 6")
inverter6Label.grid(row=6, column=0, sticky=W)

inverter7Label = Label(inv, text="Inverter 7")
inverter7Label.grid(row=7, column=0, sticky=W)

inverter8Label = Label(inv, text="Inverter 8")
inverter8Label.grid(row=8, column=0, sticky=W)

inverter9Label = Label(inv, text="Inverter 9")
inverter9Label.grid(row=9, column=0, sticky=W)

inverter10Label = Label(inv, text="Inverter 10")
inverter10Label.grid(row=10, column=0, sticky=W)

inverter11Label = Label(inv, text="Inverter 11")
inverter11Label.grid(row=11, column=0, sticky=W)

# Inverter 12
inverter12Label = Label(inv, text="Inverter 12")
inverter12Label.grid(row=12, column=0, sticky=W)

# Inverter 13
inverter13Label = Label(inv, text="Inverter 13")
inverter13Label.grid(row=13, column=0, sticky=W)

# Inverter 14
inverter14Label = Label(inv, text="Inverter 14")
inverter14Label.grid(row=14, column=0, sticky=W)

# Inverter 15
inverter15Label = Label(inv, text="Inverter 15")
inverter15Label.grid(row=15, column=0, sticky=W)

# Inverter 16
inverter16Label = Label(inv, text="Inverter 16")
inverter16Label.grid(row=16, column=0, sticky=W)

# Inverter 17
inverter17Label = Label(inv, text="Inverter 17")
inverter17Label.grid(row=17, column=0, sticky=W)

# Inverter 18
inverter18Label = Label(inv, text="Inverter 18")
inverter18Label.grid(row=18, column=0, sticky=W)

# Inverter 19
inverter19Label = Label(inv, text="Inverter 19")
inverter19Label.grid(row=19, column=0, sticky=W)

# Inverter 20
inverter20Label = Label(inv, text="Inverter 20")
inverter20Label.grid(row=20, column=0, sticky=W)

inverter21Label = Label(inv, text="Inverter 21")
inverter21Label.grid(row=21, column=0, sticky=W)

# Inverter 22
inverter22Label = Label(inv, text="Inverter 22")
inverter22Label.grid(row=22, column=0, sticky=W)

# Inverter 23
inverter23Label = Label(inv, text="Inverter 23")
inverter23Label.grid(row=23, column=0, sticky=W)

# Inverter 24
inverter24Label = Label(inv, text="Inverter 24")
inverter24Label.grid(row=24, column=0, sticky=W)

# Inverter 25
inverter25Label = Label(inv, text="Inverter 25")
inverter25Label.grid(row=25, column=0, sticky=W)

# Inverter 26
inverter26Label = Label(inv, text="Inverter 26")
inverter26Label.grid(row=26, column=0, sticky=W)

# Inverter 27
inverter27Label = Label(inv, text="Inverter 27")
inverter27Label.grid(row=27, column=0, sticky=W)

# Inverter 28
inverter28Label = Label(inv, text="Inverter 28")
inverter28Label.grid(row=28, column=0, sticky=W)

# Inverter 29
inverter29Label = Label(inv, text="Inverter 29")
inverter29Label.grid(row=29, column=0, sticky=W)

# Inverter 30
inverter30Label = Label(inv, text="Inverter 30")
inverter30Label.grid(row=30, column=0, sticky=W)

inverter31Label = Label(inv, text="Inverter 31")
inverter31Label.grid(row=31, column=0, sticky=W)

# Inverter 32
inverter32Label = Label(inv, text="Inverter 32")
inverter32Label.grid(row=32, column=0, sticky=W)

# Inverter 33
inverter33Label = Label(inv, text="Inverter 33")
inverter33Label.grid(row=33, column=0, sticky=W)

# Inverter 34
inverter34Label = Label(inv, text="Inverter 34")
inverter34Label.grid(row=34, column=0, sticky=W)

# Inverter 35
inverter35Label = Label(inv, text="Inverter 35")
inverter35Label.grid(row=35, column=0, sticky=W)

# Inverter 36
inverter36Label = Label(inv, text="Inverter 36")
inverter36Label.grid(row=36, column=0, sticky=W)

# Inverter 37
inverter37Label = Label(inv, text="Inverter 37")
inverter37Label.grid(row=37, column=0, sticky=W)

# Inverter 38
inverter38Label = Label(inv, text="Inverter 38")
inverter38Label.grid(row=38, column=0, sticky=W)

# Inverter 39
inverter39Label = Label(inv, text="Inverter 39")
inverter39Label.grid(row=39, column=0, sticky=W)

# Inverter 40
inverter40Label = Label(inv, text="Inverter 40")
inverter40Label.grid(row=40, column=0, sticky=W)

inverter41Label = Label(inv, text="Inverter 41")
inverter41Label.grid(row=41, column=0, sticky=W)

# Inverter 42
inverter42Label = Label(inv, text="Inverter 42")
inverter42Label.grid(row=42, column=0, sticky=W)

# Inverter 43
inverter43Label = Label(inv, text="Inverter 43")
inverter43Label.grid(row=43, column=0, sticky=W)

# Inverter 44
inverter44Label = Label(inv, text="Inverter 44")
inverter44Label.grid(row=44, column=0, sticky=W)

# Inverter 45
inverter45Label = Label(inv, text="Inverter 45")
inverter45Label.grid(row=45, column=0, sticky=W)

# Inverter 46
inverter46Label = Label(inv, text="Inverter 46")
inverter46Label.grid(row=46, column=0, sticky=W)

# Inverter 47
inverter47Label = Label(inv, text="Inverter 47")
inverter47Label.grid(row=47, column=0, sticky=W)

# Inverter 48
inverter48Label = Label(inv, text="Inverter 48")
inverter48Label.grid(row=48, column=0, sticky=W)

# Inverter 49
inverter49Label = Label(inv, text="Inverter 49")
inverter49Label.grid(row=49, column=0, sticky=W)

# Inverter 50
inverter50Label = Label(inv, text="Inverter 50")
inverter50Label.grid(row=50, column=0, sticky=W)

# Inverter 51
inverter51Label = Label(inv, text="Inverter 51")
inverter51Label.grid(row=51, column=0, sticky=W)

# Inverter 52
inverter52Label = Label(inv, text="Inverter 52")
inverter52Label.grid(row=52, column=0, sticky=W)

# Inverter 53
inverter53Label = Label(inv, text="Inverter 53")
inverter53Label.grid(row=53, column=0, sticky=W)

# Inverter 54
inverter54Label = Label(inv, text="Inverter 54")
inverter54Label.grid(row=54, column=0, sticky=W)

# Inverter 55
inverter55Label = Label(inv, text="Inverter 55")
inverter55Label.grid(row=55, column=0, sticky=W)

# Inverter 56
inverter56Label = Label(inv, text="Inverter 56")
inverter56Label.grid(row=56, column=0, sticky=W)

# Inverter 57
inverter57Label = Label(inv, text="Inverter 57")
inverter57Label.grid(row=57, column=0, sticky=W)

# Inverter 58
inverter58Label = Label(inv, text="Inverter 58")
inverter58Label.grid(row=58, column=0, sticky=W)

# Inverter 59
inverter59Label = Label(inv, text="Inverter 59")
inverter59Label.grid(row=59, column=0, sticky=W)

# Inverter 60
inverter60Label = Label(inv, text="Inverter 60")
inverter60Label.grid(row=60, column=0, sticky=W)

inverter61Label = Label(inv, text="Inverter 61")
inverter61Label.grid(row=61, column=0, sticky=W)

# Inverter 62
inverter62Label = Label(inv, text="Inverter 62")
inverter62Label.grid(row=62, column=0, sticky=W)

# Inverter 63
inverter63Label = Label(inv, text="Inverter 63")
inverter63Label.grid(row=63, column=0, sticky=W)

# Inverter 64
inverter64Label = Label(inv, text="Inverter 64")
inverter64Label.grid(row=64, column=0, sticky=W)



bishopIILabel= Label(inv, text= "Bishopville II")
bishopIILabel.grid(row= 0, column=1, columnspan=2)
bishopvilleIIinv1Label= Label(inv, text="X")
bishopvilleIIinv1Label.grid(row=1, column=1)
bishopvilleIIinv2Label = Label(inv, text="X")
bishopvilleIIinv2Label.grid(row=2, column=1)
bishopvilleIIinv3Label = Label(inv, text="X")
bishopvilleIIinv3Label.grid(row=3, column=1)
bishopvilleIIinv4Label = Label(inv, text="X")
bishopvilleIIinv4Label.grid(row=4, column=1)
bishopvilleIIinv5Label = Label(inv, text="X")
bishopvilleIIinv5Label.grid(row=5, column=1)
bishopvilleIIinv6Label = Label(inv, text="X")
bishopvilleIIinv6Label.grid(row=6, column=1)

bishopvilleIIinv7Label = Label(inv, text="X")
bishopvilleIIinv7Label.grid(row=7, column=1)

bishopvilleIIinv8Label = Label(inv, text="X")
bishopvilleIIinv8Label.grid(row=8, column=1)

# Bishopville II Inv 9
bishopvilleIIinv9Label = Label(inv, text="X")
bishopvilleIIinv9Label.grid(row=9, column=1)

# Bishopville II Inv 10
bishopvilleIIinv10Label = Label(inv, text="X")
bishopvilleIIinv10Label.grid(row=10, column=1)

# Bishopville II Inv 11
bishopvilleIIinv11Label = Label(inv, text="X")
bishopvilleIIinv11Label.grid(row=11, column=1)

# Bishopville II Inv 12
bishopvilleIIinv12Label = Label(inv, text="X")
bishopvilleIIinv12Label.grid(row=12, column=1)

# Bishopville II Inv 13
bishopvilleIIinv13Label = Label(inv, text="X")
bishopvilleIIinv13Label.grid(row=13, column=1)

# Bishopville II Inv 14
bishopvilleIIinv14Label = Label(inv, text="X")
bishopvilleIIinv14Label.grid(row=14, column=1)

# Bishopville II Inv 15
bishopvilleIIinv15Label = Label(inv, text="X")
bishopvilleIIinv15Label.grid(row=15, column=1)

# Bishopville II Inv 16
bishopvilleIIinv16Label = Label(inv, text="X")
bishopvilleIIinv16Label.grid(row=16, column=1)

# Bishopville II Inv 17
bishopvilleIIinv17Label = Label(inv, text="X")
bishopvilleIIinv17Label.grid(row=17, column=1)

# Bishopville II Inv 18
bishopvilleIIinv18Label = Label(inv, text="X")
bishopvilleIIinv18Label.grid(row=18, column=1)

# Bishopville II Inv 19
bishopvilleIIinv19Label = Label(inv, text="X")
bishopvilleIIinv19Label.grid(row=19, column=1)

# Bishopville II Inv 20
bishopvilleIIinv20Label = Label(inv, text="X")
bishopvilleIIinv20Label.grid(row=20, column=1)

# Bishopville II Inv 21
bishopvilleIIinv21Label = Label(inv, text="X")
bishopvilleIIinv21Label.grid(row=21, column=1)

# Bishopville II Inv 22
bishopvilleIIinv22Label = Label(inv, text="X")
bishopvilleIIinv22Label.grid(row=22, column=1)

# Bishopville II Inv 23
bishopvilleIIinv23Label = Label(inv, text="X")
bishopvilleIIinv23Label.grid(row=23, column=1)

# Bishopville II Inv 24
bishopvilleIIinv24Label = Label(inv, text="X")
bishopvilleIIinv24Label.grid(row=24, column=1)

# Bishopville II Inv 25
bishopvilleIIinv25Label = Label(inv, text="X")
bishopvilleIIinv25Label.grid(row=25, column=1)

# Bishopville II Inv 26
bishopvilleIIinv26Label = Label(inv, text="X")
bishopvilleIIinv26Label.grid(row=26, column=1)

# Bishopville II Inv 27
bishopvilleIIinv27Label = Label(inv, text="X")
bishopvilleIIinv27Label.grid(row=27, column=1)

# Bishopville II Inv 28
bishopvilleIIinv28Label = Label(inv, text="X")
bishopvilleIIinv28Label.grid(row=28, column=1)

# Bishopville II Inv 29
bishopvilleIIinv29Label = Label(inv, text="X")
bishopvilleIIinv29Label.grid(row=29, column=1)

# Bishopville II Inv 30
bishopvilleIIinv30Label = Label(inv, text="X")
bishopvilleIIinv30Label.grid(row=30, column=1)

# Bishopville II Inv 31
bishopvilleIIinv31Label = Label(inv, text="X")
bishopvilleIIinv31Label.grid(row=31, column=1)

# Bishopville II Inv 32
bishopvilleIIinv32Label = Label(inv, text="X")
bishopvilleIIinv32Label.grid(row=32, column=1)

# Bishopville II Inv 33
bishopvilleIIinv33Label = Label(inv, text="X")
bishopvilleIIinv33Label.grid(row=33, column=1)

# Bishopville II Inv 34
bishopvilleIIinv34Label = Label(inv, text="X")
bishopvilleIIinv34Label.grid(row=34, column=1)

# Bishopville II Inv 35
bishopvilleIIinv35Label = Label(inv, text="X")
bishopvilleIIinv35Label.grid(row=35, column=1)

# Bishopville II Inv 36
bishopvilleIIinv36Label = Label(inv, text="X")
bishopvilleIIinv36Label.grid(row=36, column=1)

bishopvilleIIinv1cb = Checkbutton(inv, variable=bishopvilleIIinv1cbval)
bishopvilleIIinv1cb.grid(row=1, column=2)
bishopvilleIIinv2cb = Checkbutton(inv, variable=bishopvilleIIinv2cbval)
bishopvilleIIinv2cb.grid(row=2, column=2)
bishopvilleIIinv3cb = Checkbutton(inv, variable=bishopvilleIIinv3cbval)
bishopvilleIIinv3cb.grid(row=3, column=2)
bishopvilleIIinv4cb = Checkbutton(inv, variable=bishopvilleIIinv4cbval)
bishopvilleIIinv4cb.grid(row=4, column=2)
bishopvilleIIinv5cb = Checkbutton(inv, variable=bishopvilleIIinv5cbval)
bishopvilleIIinv5cb.grid(row=5, column=2)
bishopvilleIIinv6cb = Checkbutton(inv, variable=bishopvilleIIinv6cbval)
bishopvilleIIinv6cb.grid(row=6, column=2)
bishopvilleIIinv7cb = Checkbutton(inv, variable=bishopvilleIIinv7cbval)
bishopvilleIIinv7cb.grid(row=7, column=2)
bishopvilleIIinv8cb = Checkbutton(inv, variable=bishopvilleIIinv8cbval)
bishopvilleIIinv8cb.grid(row=8, column=2)
bishopvilleIIinv9cb = Checkbutton(inv, variable=bishopvilleIIinv9cbval)
bishopvilleIIinv9cb.grid(row=9, column=2)
bishopvilleIIinv10cb = Checkbutton(inv, variable=bishopvilleIIinv10cbval)
bishopvilleIIinv10cb.grid(row=10, column=2)
bishopvilleIIinv11cb = Checkbutton(inv, variable=bishopvilleIIinv11cbval)
bishopvilleIIinv11cb.grid(row=11, column=2)
bishopvilleIIinv12cb = Checkbutton(inv, variable=bishopvilleIIinv12cbval)
bishopvilleIIinv12cb.grid(row=12, column=2)
bishopvilleIIinv13cb = Checkbutton(inv, variable=bishopvilleIIinv13cbval)
bishopvilleIIinv13cb.grid(row=13, column=2)
bishopvilleIIinv14cb = Checkbutton(inv, variable=bishopvilleIIinv14cbval)
bishopvilleIIinv14cb.grid(row=14, column=2)
bishopvilleIIinv15cb = Checkbutton(inv, variable=bishopvilleIIinv15cbval)
bishopvilleIIinv15cb.grid(row=15, column=2)
bishopvilleIIinv16cb = Checkbutton(inv, variable=bishopvilleIIinv16cbval)
bishopvilleIIinv16cb.grid(row=16, column=2)
bishopvilleIIinv17cb = Checkbutton(inv, variable=bishopvilleIIinv17cbval)
bishopvilleIIinv17cb.grid(row=17, column=2)
bishopvilleIIinv18cb = Checkbutton(inv, variable=bishopvilleIIinv18cbval)
bishopvilleIIinv18cb.grid(row=18, column=2)
bishopvilleIIinv19cb = Checkbutton(inv, variable=bishopvilleIIinv19cbval)
bishopvilleIIinv19cb.grid(row=19, column=2)
bishopvilleIIinv20cb = Checkbutton(inv, variable=bishopvilleIIinv20cbval)
bishopvilleIIinv20cb.grid(row=20, column=2)
bishopvilleIIinv21cb = Checkbutton(inv, variable=bishopvilleIIinv21cbval)
bishopvilleIIinv21cb.grid(row=21, column=2)
bishopvilleIIinv22cb = Checkbutton(inv, variable=bishopvilleIIinv22cbval)
bishopvilleIIinv22cb.grid(row=22, column=2)
bishopvilleIIinv23cb = Checkbutton(inv, variable=bishopvilleIIinv23cbval)
bishopvilleIIinv23cb.grid(row=23, column=2)
bishopvilleIIinv24cb = Checkbutton(inv, variable=bishopvilleIIinv24cbval)
bishopvilleIIinv24cb.grid(row=24, column=2)
bishopvilleIIinv25cb = Checkbutton(inv, variable=bishopvilleIIinv25cbval)
bishopvilleIIinv25cb.grid(row=25, column=2)
bishopvilleIIinv26cb = Checkbutton(inv, variable=bishopvilleIIinv26cbval)
bishopvilleIIinv26cb.grid(row=26, column=2)
bishopvilleIIinv27cb = Checkbutton(inv, variable=bishopvilleIIinv27cbval)
bishopvilleIIinv27cb.grid(row=27, column=2)
bishopvilleIIinv28cb = Checkbutton(inv, variable=bishopvilleIIinv28cbval)
bishopvilleIIinv28cb.grid(row=28, column=2)
bishopvilleIIinv29cb = Checkbutton(inv, variable=bishopvilleIIinv29cbval)
bishopvilleIIinv29cb.grid(row=29, column=2)
bishopvilleIIinv30cb = Checkbutton(inv, variable=bishopvilleIIinv30cbval)
bishopvilleIIinv30cb.grid(row=30, column=2)
bishopvilleIIinv31cb = Checkbutton(inv, variable=bishopvilleIIinv31cbval)
bishopvilleIIinv31cb.grid(row=31, column=2)
bishopvilleIIinv32cb = Checkbutton(inv, variable=bishopvilleIIinv32cbval)
bishopvilleIIinv32cb.grid(row=32, column=2)
bishopvilleIIinv33cb = Checkbutton(inv, variable=bishopvilleIIinv33cbval)
bishopvilleIIinv33cb.grid(row=33, column=2)
bishopvilleIIinv34cb = Checkbutton(inv, variable=bishopvilleIIinv34cbval)
bishopvilleIIinv34cb.grid(row=34, column=2)
bishopvilleIIinv35cb = Checkbutton(inv, variable=bishopvilleIIinv35cbval)
bishopvilleIIinv35cb.grid(row=35, column=2)
bishopvilleIIinv36cb = Checkbutton(inv, variable=bishopvilleIIinv36cbval)
bishopvilleIIinv36cb.grid(row=36, column=2)

bluebird1Label= Label(narenco, text= "Bluebird")
bluebird1Label.grid(row=0, column=1, columnspan=2)
bluebirdinv1Label= Label(narenco, text= "X")
bluebirdinv1Label.grid(row=1, column= 1)
# Bluebird Inv 2
bluebirdinv2Label = Label(narenco, text="X")
bluebirdinv2Label.grid(row=2, column=1)

# Bluebird Inv 3
bluebirdinv3Label = Label(narenco, text="X")
bluebirdinv3Label.grid(row=3, column=1)

# Bluebird Inv 4
bluebirdinv4Label = Label(narenco, text="X")
bluebirdinv4Label.grid(row=4, column=1)

# Bluebird Inv 5
bluebirdinv5Label = Label(narenco, text="X")
bluebirdinv5Label.grid(row=5, column=1)

# Bluebird Inv 6
bluebirdinv6Label = Label(narenco, text="X")
bluebirdinv6Label.grid(row=6, column=1)

# Bluebird Inv 7
bluebirdinv7Label = Label(narenco, text="X")
bluebirdinv7Label.grid(row=7, column=1)

# Bluebird Inv 8
bluebirdinv8Label = Label(narenco, text="X")
bluebirdinv8Label.grid(row=8, column=1)

# Bluebird Inv 9
bluebirdinv9Label = Label(narenco, text="X")
bluebirdinv9Label.grid(row=9, column=1)

# Bluebird Inv 10
bluebirdinv10Label = Label(narenco, text="X")
bluebirdinv10Label.grid(row=10, column=1)

# Bluebird Inv 11
bluebirdinv11Label = Label(narenco, text="X")
bluebirdinv11Label.grid(row=11, column=1)

# Bluebird Inv 12
bluebirdinv12Label = Label(narenco, text="X")
bluebirdinv12Label.grid(row=12, column=1)

# Bluebird Inv 13
bluebirdinv13Label = Label(narenco, text="X")
bluebirdinv13Label.grid(row=13, column=1)

# Bluebird Inv 14
bluebirdinv14Label = Label(narenco, text="X")
bluebirdinv14Label.grid(row=14, column=1)

# Bluebird Inv 15
bluebirdinv15Label = Label(narenco, text="X")
bluebirdinv15Label.grid(row=15, column=1)

# Bluebird Inv 16
bluebirdinv16Label = Label(narenco, text="X")
bluebirdinv16Label.grid(row=16, column=1)

# Bluebird Inv 17
bluebirdinv17Label = Label(narenco, text="X")
bluebirdinv17Label.grid(row=17, column=1)

# Bluebird Inv 18
bluebirdinv18Label = Label(narenco, text="X")
bluebirdinv18Label.grid(row=18, column=1)

# Bluebird Inv 19
bluebirdinv19Label = Label(narenco, text="X")
bluebirdinv19Label.grid(row=19, column=1)

# Bluebird Inv 20
bluebirdinv20Label = Label(narenco, text="X")
bluebirdinv20Label.grid(row=20, column=1)

# Bluebird Inv 21
bluebirdinv21Label = Label(narenco, text="X")
bluebirdinv21Label.grid(row=21, column=1)

# Bluebird Inv 22
bluebirdinv22Label = Label(narenco, text="X")
bluebirdinv22Label.grid(row=22, column=1)

# Bluebird Inv 23
bluebirdinv23Label = Label(narenco, text="X")
bluebirdinv23Label.grid(row=23, column=1)

# Bluebird Inv 24
bluebirdinv24Label = Label(narenco, text="X")
bluebirdinv24Label.grid(row=24, column=1)

bluebirdinv1cb = Checkbutton(narenco, variable=bluebirdinv1cbval)
bluebirdinv1cb.grid(row=1, column=2)
bluebirdinv2cb = Checkbutton(narenco, variable=bluebirdinv2cbval)
bluebirdinv2cb.grid(row=2, column=2)
bluebirdinv3cb = Checkbutton(narenco, variable=bluebirdinv3cbval)
bluebirdinv3cb.grid(row=3, column=2)
bluebirdinv4cb = Checkbutton(narenco, variable=bluebirdinv4cbval)
bluebirdinv4cb.grid(row=4, column=2)
bluebirdinv5cb = Checkbutton(narenco, variable=bluebirdinv5cbval)
bluebirdinv5cb.grid(row=5, column=2)
bluebirdinv6cb = Checkbutton(narenco, variable=bluebirdinv6cbval)
bluebirdinv6cb.grid(row=6, column=2)
bluebirdinv7cb = Checkbutton(narenco, variable=bluebirdinv7cbval)
bluebirdinv7cb.grid(row=7, column=2)
bluebirdinv8cb = Checkbutton(narenco, variable=bluebirdinv8cbval)
bluebirdinv8cb.grid(row=8, column=2)
bluebirdinv9cb = Checkbutton(narenco, variable=bluebirdinv9cbval)
bluebirdinv9cb.grid(row=9, column=2)
bluebirdinv10cb = Checkbutton(narenco, variable=bluebirdinv10cbval)
bluebirdinv10cb.grid(row=10, column=2)
bluebirdinv11cb = Checkbutton(narenco, variable=bluebirdinv11cbval)
bluebirdinv11cb.grid(row=11, column=2)
bluebirdinv12cb = Checkbutton(narenco, variable=bluebirdinv12cbval)
bluebirdinv12cb.grid(row=12, column=2)
bluebirdinv13cb = Checkbutton(narenco, variable=bluebirdinv13cbval)
bluebirdinv13cb.grid(row=13, column=2)
bluebirdinv14cb = Checkbutton(narenco, variable=bluebirdinv14cbval)
bluebirdinv14cb.grid(row=14, column=2)
bluebirdinv15cb = Checkbutton(narenco, variable=bluebirdinv15cbval)
bluebirdinv15cb.grid(row=15, column=2)
bluebirdinv16cb = Checkbutton(narenco, variable=bluebirdinv16cbval)
bluebirdinv16cb.grid(row=16, column=2)
bluebirdinv17cb = Checkbutton(narenco, variable=bluebirdinv17cbval)
bluebirdinv17cb.grid(row=17, column=2)
bluebirdinv18cb = Checkbutton(narenco, variable=bluebirdinv18cbval)
bluebirdinv18cb.grid(row=18, column=2)
bluebirdinv19cb = Checkbutton(narenco, variable=bluebirdinv19cbval)
bluebirdinv19cb.grid(row=19, column=2)
bluebirdinv20cb = Checkbutton(narenco, variable=bluebirdinv20cbval)
bluebirdinv20cb.grid(row=20, column=2)
bluebirdinv21cb = Checkbutton(narenco, variable=bluebirdinv21cbval)
bluebirdinv21cb.grid(row=21, column=2)
bluebirdinv22cb = Checkbutton(narenco, variable=bluebirdinv22cbval)
bluebirdinv22cb.grid(row=22, column=2)
bluebirdinv23cb = Checkbutton(narenco, variable=bluebirdinv23cbval)
bluebirdinv23cb.grid(row=23, column=2)
bluebirdinv24cb = Checkbutton(narenco, variable=bluebirdinv24cbval)
bluebirdinv24cb.grid(row=24, column=2)


bulloch1a1Label= Label(solrvr, text= "Bulloch 1A")
bulloch1a1Label.grid(row=0, column=1, columnspan=2)
bulloch1ainv1Label= Label(solrvr, text= "X")
bulloch1ainv1Label.grid(row=1, column=1)
bulloch1ainv2Label = Label(solrvr, text="X")
bulloch1ainv2Label.grid(row=2, column=1)

# Bulloch 1a Inv 3
bulloch1ainv3Label = Label(solrvr, text="X")
bulloch1ainv3Label.grid(row=3, column=1)

# Bulloch 1a Inv 4
bulloch1ainv4Label = Label(solrvr, text="X")
bulloch1ainv4Label.grid(row=4, column=1)

# Bulloch 1a Inv 5
bulloch1ainv5Label = Label(solrvr, text="X")
bulloch1ainv5Label.grid(row=5, column=1)

# Bulloch 1a Inv 6
bulloch1ainv6Label = Label(solrvr, text="X")
bulloch1ainv6Label.grid(row=6, column=1)

# Bulloch 1a Inv 7
bulloch1ainv7Label = Label(solrvr, text="X")
bulloch1ainv7Label.grid(row=7, column=1)

# Bulloch 1a Inv 8
bulloch1ainv8Label = Label(solrvr, text="X")
bulloch1ainv8Label.grid(row=8, column=1)

# Bulloch 1a Inv 9
bulloch1ainv9Label = Label(solrvr, text="X")
bulloch1ainv9Label.grid(row=9, column=1)

# Bulloch 1a Inv 10
bulloch1ainv10Label = Label(solrvr, text="X")
bulloch1ainv10Label.grid(row=10, column=1)

# Bulloch 1a Inv 11
bulloch1ainv11Label = Label(solrvr, text="X")
bulloch1ainv11Label.grid(row=11, column=1)

# Bulloch 1a Inv 12
bulloch1ainv12Label = Label(solrvr, text="X")
bulloch1ainv12Label.grid(row=12, column=1)

# Bulloch 1a Inv 13
bulloch1ainv13Label = Label(solrvr, text="X")
bulloch1ainv13Label.grid(row=13, column=1)

# Bulloch 1a Inv 14
bulloch1ainv14Label = Label(solrvr, text="X")
bulloch1ainv14Label.grid(row=14, column=1)

# Bulloch 1a Inv 15
bulloch1ainv15Label = Label(solrvr, text="X")
bulloch1ainv15Label.grid(row=15, column=1)

# Bulloch 1a Inv 16
bulloch1ainv16Label = Label(solrvr, text="X")
bulloch1ainv16Label.grid(row=16, column=1)

# Bulloch 1a Inv 17
bulloch1ainv17Label = Label(solrvr, text="X")
bulloch1ainv17Label.grid(row=17, column=1)

# Bulloch 1a Inv 18
bulloch1ainv18Label = Label(solrvr, text="X")
bulloch1ainv18Label.grid(row=18, column=1)

# Bulloch 1a Inv 19
bulloch1ainv19Label = Label(solrvr, text="X")
bulloch1ainv19Label.grid(row=19, column=1)

# Bulloch 1a Inv 20
bulloch1ainv20Label = Label(solrvr, text="X")
bulloch1ainv20Label.grid(row=20, column=1)
bulloch1ainv21Label = Label(solrvr, text="X")
bulloch1ainv21Label.grid(row=21, column=1)

# Bulloch 1a Inv 22
bulloch1ainv22Label = Label(solrvr, text="X")
bulloch1ainv22Label.grid(row=22, column=1)

# Bulloch 1a Inv 23
bulloch1ainv23Label = Label(solrvr, text="X")
bulloch1ainv23Label.grid(row=23, column=1)

# Bulloch 1a Inv 24
bulloch1ainv24Label = Label(solrvr, text="X")
bulloch1ainv24Label.grid(row=24, column=1)

bulloch1ainv1cb = Checkbutton(solrvr, variable=bulloch1ainv1cbval)
bulloch1ainv1cb.grid(row=1, column=2)
bulloch1ainv2cb = Checkbutton(solrvr, variable=bulloch1ainv2cbval)
bulloch1ainv2cb.grid(row=2, column=2)
bulloch1ainv3cb = Checkbutton(solrvr, variable=bulloch1ainv3cbval)
bulloch1ainv3cb.grid(row=3, column=2)
bulloch1ainv4cb = Checkbutton(solrvr, variable=bulloch1ainv4cbval)
bulloch1ainv4cb.grid(row=4, column=2)
bulloch1ainv5cb = Checkbutton(solrvr, variable=bulloch1ainv5cbval)
bulloch1ainv5cb.grid(row=5, column=2)
bulloch1ainv6cb = Checkbutton(solrvr, variable=bulloch1ainv6cbval)
bulloch1ainv6cb.grid(row=6, column=2)
bulloch1ainv7cb = Checkbutton(solrvr, variable=bulloch1ainv7cbval)
bulloch1ainv7cb.grid(row=7, column=2)
bulloch1ainv8cb = Checkbutton(solrvr, variable=bulloch1ainv8cbval)
bulloch1ainv8cb.grid(row=8, column=2)
bulloch1ainv9cb = Checkbutton(solrvr, variable=bulloch1ainv9cbval)
bulloch1ainv9cb.grid(row=9, column=2)
bulloch1ainv10cb = Checkbutton(solrvr, variable=bulloch1ainv10cbval)
bulloch1ainv10cb.grid(row=10, column=2)
bulloch1ainv11cb = Checkbutton(solrvr, variable=bulloch1ainv11cbval)
bulloch1ainv11cb.grid(row=11, column=2)
bulloch1ainv12cb = Checkbutton(solrvr, variable=bulloch1ainv12cbval)
bulloch1ainv12cb.grid(row=12, column=2)
bulloch1ainv13cb = Checkbutton(solrvr, variable=bulloch1ainv13cbval)
bulloch1ainv13cb.grid(row=13, column=2)
bulloch1ainv14cb = Checkbutton(solrvr, variable=bulloch1ainv14cbval)
bulloch1ainv14cb.grid(row=14, column=2)
bulloch1ainv15cb = Checkbutton(solrvr, variable=bulloch1ainv15cbval)
bulloch1ainv15cb.grid(row=15, column=2)
bulloch1ainv16cb = Checkbutton(solrvr, variable=bulloch1ainv16cbval)
bulloch1ainv16cb.grid(row=16, column=2)
bulloch1ainv17cb = Checkbutton(solrvr, variable=bulloch1ainv17cbval)
bulloch1ainv17cb.grid(row=17, column=2)
bulloch1ainv18cb = Checkbutton(solrvr, variable=bulloch1ainv18cbval)
bulloch1ainv18cb.grid(row=18, column=2)
bulloch1ainv19cb = Checkbutton(solrvr, variable=bulloch1ainv19cbval)
bulloch1ainv19cb.grid(row=19, column=2)
bulloch1ainv20cb = Checkbutton(solrvr, variable=bulloch1ainv20cbval)
bulloch1ainv20cb.grid(row=20, column=2)
bulloch1ainv21cb = Checkbutton(solrvr, variable=bulloch1ainv21cbval)
bulloch1ainv21cb.grid(row=21, column=2)
bulloch1ainv22cb = Checkbutton(solrvr, variable=bulloch1ainv22cbval)
bulloch1ainv22cb.grid(row=22, column=2)
bulloch1ainv23cb = Checkbutton(solrvr, variable=bulloch1ainv23cbval)
bulloch1ainv23cb.grid(row=23, column=2)
bulloch1ainv24cb = Checkbutton(solrvr, variable=bulloch1ainv24cbval)
bulloch1ainv24cb.grid(row=24, column=2)


bulloch1b1Label= Label(solrvr, text= "Bulloch 1B")
bulloch1b1Label.grid(row=0, column=3, columnspan=2)

bulloch1binv1Label = Label(solrvr, text="X")
bulloch1binv1Label.grid(row=1, column=3)
bulloch1binv2Label = Label(solrvr, text="X")
bulloch1binv2Label.grid(row=2, column=3)

# Bulloch 1b Inv 3
bulloch1binv3Label = Label(solrvr, text="X")
bulloch1binv3Label.grid(row=3, column=3)

# Bulloch 1b Inv 4
bulloch1binv4Label = Label(solrvr, text="X")
bulloch1binv4Label.grid(row=4, column=3)

# Bulloch 1b Inv 5
bulloch1binv5Label = Label(solrvr, text="X")
bulloch1binv5Label.grid(row=5, column=3)

# Bulloch 1b Inv 6
bulloch1binv6Label = Label(solrvr, text="X")
bulloch1binv6Label.grid(row=6, column=3)

# Bulloch 1b Inv 7
bulloch1binv7Label = Label(solrvr, text="X")
bulloch1binv7Label.grid(row=7, column=3)

# Bulloch 1b Inv 8
bulloch1binv8Label = Label(solrvr, text="X")
bulloch1binv8Label.grid(row=8, column=3)

# Bulloch 1b Inv 9
bulloch1binv9Label = Label(solrvr, text="X")
bulloch1binv9Label.grid(row=9, column=3)

# Bulloch 1b Inv 10
bulloch1binv10Label = Label(solrvr, text="X")
bulloch1binv10Label.grid(row=10, column=3)

# Bulloch 1b Inv 11
bulloch1binv11Label = Label(solrvr, text="X")
bulloch1binv11Label.grid(row=11, column=3)

# Bulloch 1b Inv 12
bulloch1binv12Label = Label(solrvr, text="X")
bulloch1binv12Label.grid(row=12, column=3)

# Bulloch 1b Inv 13
bulloch1binv13Label = Label(solrvr, text="X")
bulloch1binv13Label.grid(row=13, column=3)

# Bulloch 1b Inv 14
bulloch1binv14Label = Label(solrvr, text="X")
bulloch1binv14Label.grid(row=14, column=3)

# Bulloch 1b Inv 15
bulloch1binv15Label = Label(solrvr, text="X")
bulloch1binv15Label.grid(row=15, column=3)

# Bulloch 1b Inv 16
bulloch1binv16Label = Label(solrvr, text="X")
bulloch1binv16Label.grid(row=16, column=3)

# Bulloch 1b Inv 17
bulloch1binv17Label = Label(solrvr, text="X")
bulloch1binv17Label.grid(row=17, column=3)

# Bulloch 1b Inv 18
bulloch1binv18Label = Label(solrvr, text="X")
bulloch1binv18Label.grid(row=18, column=3)

# Bulloch 1b Inv 19
bulloch1binv19Label = Label(solrvr, text="X")
bulloch1binv19Label.grid(row=19, column=3)

# Bulloch 1b Inv 20
bulloch1binv20Label = Label(solrvr, text="X")
bulloch1binv20Label.grid(row=20, column=3)
# Bulloch 1b Inv 21
bulloch1binv21Label = Label(solrvr, text="X")
bulloch1binv21Label.grid(row=21, column=3)

# Bulloch 1b Inv 22
bulloch1binv22Label = Label(solrvr, text="X")
bulloch1binv22Label.grid(row=22, column=3)

# Bulloch 1b Inv 23
bulloch1binv23Label = Label(solrvr, text="X")
bulloch1binv23Label.grid(row=23, column=3)

# Bulloch 1b Inv 24
bulloch1binv24Label = Label(solrvr, text="X")
bulloch1binv24Label.grid(row=24, column=3)

bulloch1binv1cb = Checkbutton(solrvr, variable=bulloch1binv1cbval)
bulloch1binv1cb.grid(row=1, column=4)
bulloch1binv2cb = Checkbutton(solrvr, variable=bulloch1binv2cbval)
bulloch1binv2cb.grid(row=2, column=4)
bulloch1binv3cb = Checkbutton(solrvr, variable=bulloch1binv3cbval)
bulloch1binv3cb.grid(row=3, column=4)
bulloch1binv4cb = Checkbutton(solrvr, variable=bulloch1binv4cbval)
bulloch1binv4cb.grid(row=4, column=4)
bulloch1binv5cb = Checkbutton(solrvr, variable=bulloch1binv5cbval)
bulloch1binv5cb.grid(row=5, column=4)
bulloch1binv6cb = Checkbutton(solrvr, variable=bulloch1binv6cbval)
bulloch1binv6cb.grid(row=6, column=4)
bulloch1binv7cb = Checkbutton(solrvr, variable=bulloch1binv7cbval)
bulloch1binv7cb.grid(row=7, column=4)
bulloch1binv8cb = Checkbutton(solrvr, variable=bulloch1binv8cbval)
bulloch1binv8cb.grid(row=8, column=4)
bulloch1binv9cb = Checkbutton(solrvr, variable=bulloch1binv9cbval)
bulloch1binv9cb.grid(row=9, column=4)
bulloch1binv10cb = Checkbutton(solrvr, variable=bulloch1binv10cbval)
bulloch1binv10cb.grid(row=10, column=4)
bulloch1binv11cb = Checkbutton(solrvr, variable=bulloch1binv11cbval)
bulloch1binv11cb.grid(row=11, column=4)
bulloch1binv12cb = Checkbutton(solrvr, variable=bulloch1binv12cbval)
bulloch1binv12cb.grid(row=12, column=4)
bulloch1binv13cb = Checkbutton(solrvr, variable=bulloch1binv13cbval)
bulloch1binv13cb.grid(row=13, column=4)
bulloch1binv14cb = Checkbutton(solrvr, variable=bulloch1binv14cbval)
bulloch1binv14cb.grid(row=14, column=4)
bulloch1binv15cb = Checkbutton(solrvr, variable=bulloch1binv15cbval)
bulloch1binv15cb.grid(row=15, column=4)
bulloch1binv16cb = Checkbutton(solrvr, variable=bulloch1binv16cbval)
bulloch1binv16cb.grid(row=16, column=4)
bulloch1binv17cb = Checkbutton(solrvr, variable=bulloch1binv17cbval)
bulloch1binv17cb.grid(row=17, column=4)
bulloch1binv18cb = Checkbutton(solrvr, variable=bulloch1binv18cbval)
bulloch1binv18cb.grid(row=18, column=4)
bulloch1binv19cb = Checkbutton(solrvr, variable=bulloch1binv19cbval)
bulloch1binv19cb.grid(row=19, column=4)
bulloch1binv20cb = Checkbutton(solrvr, variable=bulloch1binv20cbval)
bulloch1binv20cb.grid(row=20, column=4)
bulloch1binv21cb = Checkbutton(solrvr, variable=bulloch1binv21cbval)
bulloch1binv21cb.grid(row=21, column=4)
bulloch1binv22cb = Checkbutton(solrvr, variable=bulloch1binv22cbval)
bulloch1binv22cb.grid(row=22, column=4)
bulloch1binv23cb = Checkbutton(solrvr, variable=bulloch1binv23cbval)
bulloch1binv23cb.grid(row=23, column=4)
bulloch1binv24cb = Checkbutton(solrvr, variable=bulloch1binv24cbval)
bulloch1binv24cb.grid(row=24, column=4)


cardinal1Label= Label(narenco, text= "Cardinal")
cardinal1Label.grid(row=0, column=3, columnspan=2)

cardinalinv1Label= Label(narenco, text="X")
cardinalinv1Label.grid(row=1, column=3)

# Cardinal Inv 2
cardinalinv2Label = Label(narenco, text="X")
cardinalinv2Label.grid(row=2, column=3)

# Cardinal Inv 3
cardinalinv3Label = Label(narenco, text="X")
cardinalinv3Label.grid(row=3, column=3)

# Cardinal Inv 4
cardinalinv4Label = Label(narenco, text="X")
cardinalinv4Label.grid(row=4, column=3)

# Cardinal Inv 5
cardinalinv5Label = Label(narenco, text="X")
cardinalinv5Label.grid(row=5, column=3)

# Cardinal Inv 6
cardinalinv6Label = Label(narenco, text="X")
cardinalinv6Label.grid(row=6, column=3)

# Cardinal Inv 7
cardinalinv7Label = Label(narenco, text="X")
cardinalinv7Label.grid(row=7, column=3)

# Cardinal Inv 8
cardinalinv8Label = Label(narenco, text="X")
cardinalinv8Label.grid(row=8, column=3)

# Cardinal Inv 9
cardinalinv9Label = Label(narenco, text="X")
cardinalinv9Label.grid(row=9, column=3)

# Cardinal Inv 10
cardinalinv10Label = Label(narenco, text="X")
cardinalinv10Label.grid(row=10, column=3)

# Cardinal Inv 11
cardinalinv11Label = Label(narenco, text="X")
cardinalinv11Label.grid(row=11, column=3)

# Cardinal Inv 12
cardinalinv12Label = Label(narenco, text="X")
cardinalinv12Label.grid(row=12, column=3)

# Cardinal Inv 13
cardinalinv13Label = Label(narenco, text="X")
cardinalinv13Label.grid(row=13, column=3)

# Cardinal Inv 14
cardinalinv14Label = Label(narenco, text="X")
cardinalinv14Label.grid(row=14, column=3)

# Cardinal Inv 15
cardinalinv15Label = Label(narenco, text="X")
cardinalinv15Label.grid(row=15, column=3)

# Cardinal Inv 16
cardinalinv16Label = Label(narenco, text="X")
cardinalinv16Label.grid(row=16, column=3)

# Cardinal Inv 17
cardinalinv17Label = Label(narenco, text="X")
cardinalinv17Label.grid(row=17, column=3)

# Cardinal Inv 18
cardinalinv18Label = Label(narenco, text="X")
cardinalinv18Label.grid(row=18, column=3)

# Cardinal Inv 19
cardinalinv19Label = Label(narenco, text="X")
cardinalinv19Label.grid(row=19, column=3)

# Cardinal Inv 20
cardinalinv20Label = Label(narenco, text="X")
cardinalinv20Label.grid(row=20, column=3)

# Cardinal Inv 21
cardinalinv21Label = Label(narenco, text="X")
cardinalinv21Label.grid(row=21, column=3)

# Cardinal Inv 22
cardinalinv22Label = Label(narenco, text="X")
cardinalinv22Label.grid(row=22, column=3)

# Cardinal Inv 23
cardinalinv23Label = Label(narenco, text="X")
cardinalinv23Label.grid(row=23, column=3)

# Cardinal Inv 24
cardinalinv24Label = Label(narenco, text="X")
cardinalinv24Label.grid(row=24, column=3)

# Cardinal Inv 25
cardinalinv25Label = Label(narenco, text="X")
cardinalinv25Label.grid(row=25, column=3)

# Cardinal Inv 26
cardinalinv26Label = Label(narenco, text="X")
cardinalinv26Label.grid(row=26, column=3)

# Cardinal Inv 27
cardinalinv27Label = Label(narenco, text="X")
cardinalinv27Label.grid(row=27, column=3)

# Cardinal Inv 28
cardinalinv28Label = Label(narenco, text="X")
cardinalinv28Label.grid(row=28, column=3)

# Cardinal Inv 29
cardinalinv29Label = Label(narenco, text="X")
cardinalinv29Label.grid(row=29, column=3)

# Cardinal Inv 30
cardinalinv30Label = Label(narenco, text="X")
cardinalinv30Label.grid(row=30, column=3)

# Cardinal Inv 31
cardinalinv31Label = Label(narenco, text="X")
cardinalinv31Label.grid(row=31, column=3)

# Cardinal Inv 32
cardinalinv32Label = Label(narenco, text="X")
cardinalinv32Label.grid(row=32, column=3)

# Cardinal Inv 33
cardinalinv33Label = Label(narenco, text="X")
cardinalinv33Label.grid(row=33, column=3)

# Cardinal Inv 34
cardinalinv34Label = Label(narenco, text="X")
cardinalinv34Label.grid(row=34, column=3)

# Cardinal Inv 35
cardinalinv35Label = Label(narenco, text="X")
cardinalinv35Label.grid(row=35, column=3)

# Cardinal Inv 36
cardinalinv36Label = Label(narenco, text="X")
cardinalinv36Label.grid(row=36, column=3)

# Cardinal Inv 37
cardinalinv37Label = Label(narenco, text="X")
cardinalinv37Label.grid(row=37, column=3)

# Cardinal Inv 38
cardinalinv38Label = Label(narenco, text="X")
cardinalinv38Label.grid(row=38, column=3)

# Cardinal Inv 39
cardinalinv39Label = Label(narenco, text="X")
cardinalinv39Label.grid(row=39, column=3)

# Cardinal Inv 40
cardinalinv40Label = Label(narenco, text="X")
cardinalinv40Label.grid(row=40, column=3)

# Cardinal Inv 41
cardinalinv41Label = Label(narenco, text="X")
cardinalinv41Label.grid(row=41, column=3)

# Cardinal Inv 42
cardinalinv42Label = Label(narenco, text="X")
cardinalinv42Label.grid(row=42, column=3)

# Cardinal Inv 43
cardinalinv43Label = Label(narenco, text="X")
cardinalinv43Label.grid(row=43, column=3)

# Cardinal Inv 44
cardinalinv44Label = Label(narenco, text="X")
cardinalinv44Label.grid(row=44, column=3)

# Cardinal Inv 45
cardinalinv45Label = Label(narenco, text="X")
cardinalinv45Label.grid(row=45, column=3)
4
# Cardinal Inv 46
cardinalinv46Label = Label(narenco, text="X")
cardinalinv46Label.grid(row=46, column=3)

# Cardinal Inv 47
cardinalinv47Label = Label(narenco, text="X")
cardinalinv47Label.grid(row=47, column=3)

# Cardinal Inv 48
cardinalinv48Label = Label(narenco, text="X")
cardinalinv48Label.grid(row=48, column=3)

# Cardinal Inv 49
cardinalinv49Label = Label(narenco, text="X")
cardinalinv49Label.grid(row=49, column=3)

# Cardinal Inv 50
cardinalinv50Label = Label(narenco, text="X")
cardinalinv50Label.grid(row=50, column=3)

# Cardinal Inv 51
cardinalinv51Label = Label(narenco, text="X")
cardinalinv51Label.grid(row=51, column=3)

# Cardinal Inv 52
cardinalinv52Label = Label(narenco, text="X")
cardinalinv52Label.grid(row=52, column=3)

# Cardinal Inv 53
cardinalinv53Label = Label(narenco, text="X")
cardinalinv53Label.grid(row=53, column=3)

# Cardinal Inv 54
cardinalinv54Label = Label(narenco, text="X")
cardinalinv54Label.grid(row=54, column=3)

# Cardinal Inv 55
cardinalinv55Label = Label(narenco, text="X")
cardinalinv55Label.grid(row=55, column=3)

# Cardinal Inv 56
cardinalinv56Label = Label(narenco, text="X")
cardinalinv56Label.grid(row=56, column=3)

# Cardinal Inv 57
cardinalinv57Label = Label(narenco, text="X")
cardinalinv57Label.grid(row=57, column=3)

# Cardinal Inv 58
cardinalinv58Label = Label(narenco, text="X")
cardinalinv58Label.grid(row=58, column=3)

# Cardinal Inv 59
cardinalinv59Label = Label(narenco, text="X")
cardinalinv59Label.grid(row=59, column=3)


cardinalinv1cb = Checkbutton(narenco, variable=cardinalinv1cbval)
cardinalinv1cb.grid(row=1, column=4)
cardinalinv2cb = Checkbutton(narenco, variable=cardinalinv2cbval)
cardinalinv2cb.grid(row=2, column=4)
cardinalinv3cb = Checkbutton(narenco, variable=cardinalinv3cbval)
cardinalinv3cb.grid(row=3, column=4)
cardinalinv4cb = Checkbutton(narenco, variable=cardinalinv4cbval)
cardinalinv4cb.grid(row=4, column=4)
cardinalinv5cb = Checkbutton(narenco, variable=cardinalinv5cbval)
cardinalinv5cb.grid(row=5, column=4)
cardinalinv6cb = Checkbutton(narenco, variable=cardinalinv6cbval)
cardinalinv6cb.grid(row=6, column=4)
cardinalinv7cb = Checkbutton(narenco, variable=cardinalinv7cbval)
cardinalinv7cb.grid(row=7, column=4)
cardinalinv8cb = Checkbutton(narenco, variable=cardinalinv8cbval)
cardinalinv8cb.grid(row=8, column=4)
cardinalinv9cb = Checkbutton(narenco, variable=cardinalinv9cbval)
cardinalinv9cb.grid(row=9, column=4)
cardinalinv10cb = Checkbutton(narenco, variable=cardinalinv10cbval)
cardinalinv10cb.grid(row=10, column=4)
cardinalinv11cb = Checkbutton(narenco, variable=cardinalinv11cbval)
cardinalinv11cb.grid(row=11, column=4)
cardinalinv12cb = Checkbutton(narenco, variable=cardinalinv12cbval)
cardinalinv12cb.grid(row=12, column=4)
cardinalinv13cb = Checkbutton(narenco, variable=cardinalinv13cbval)
cardinalinv13cb.grid(row=13, column=4)
cardinalinv14cb = Checkbutton(narenco, variable=cardinalinv14cbval)
cardinalinv14cb.grid(row=14, column=4)
cardinalinv15cb = Checkbutton(narenco, variable=cardinalinv15cbval)
cardinalinv15cb.grid(row=15, column=4)
cardinalinv16cb = Checkbutton(narenco, variable=cardinalinv16cbval)
cardinalinv16cb.grid(row=16, column=4)
cardinalinv17cb = Checkbutton(narenco, variable=cardinalinv17cbval)
cardinalinv17cb.grid(row=17, column=4)
cardinalinv18cb = Checkbutton(narenco, variable=cardinalinv18cbval)
cardinalinv18cb.grid(row=18, column=4)
cardinalinv19cb = Checkbutton(narenco, variable=cardinalinv19cbval)
cardinalinv19cb.grid(row=19, column=4)
cardinalinv20cb = Checkbutton(narenco, variable=cardinalinv20cbval)
cardinalinv20cb.grid(row=20, column=4)
cardinalinv21cb = Checkbutton(narenco, variable=cardinalinv21cbval)
cardinalinv21cb.grid(row=21, column=4)
cardinalinv22cb = Checkbutton(narenco, variable=cardinalinv22cbval)
cardinalinv22cb.grid(row=22, column=4)
cardinalinv23cb = Checkbutton(narenco, variable=cardinalinv23cbval)
cardinalinv23cb.grid(row=23, column=4)
cardinalinv24cb = Checkbutton(narenco, variable=cardinalinv24cbval)
cardinalinv24cb.grid(row=24, column=4)
cardinalinv25cb = Checkbutton(narenco, variable=cardinalinv25cbval)
cardinalinv25cb.grid(row=25, column=4)
cardinalinv26cb = Checkbutton(narenco, variable=cardinalinv26cbval)
cardinalinv26cb.grid(row=26, column=4)
cardinalinv27cb = Checkbutton(narenco, variable=cardinalinv27cbval)
cardinalinv27cb.grid(row=27, column=4)
cardinalinv28cb = Checkbutton(narenco, variable=cardinalinv28cbval)
cardinalinv28cb.grid(row=28, column=4)
cardinalinv29cb = Checkbutton(narenco, variable=cardinalinv29cbval)
cardinalinv29cb.grid(row=29, column=4)
cardinalinv30cb = Checkbutton(narenco, variable=cardinalinv30cbval)
cardinalinv30cb.grid(row=30, column=4)
cardinalinv31cb = Checkbutton(narenco, variable=cardinalinv31cbval)
cardinalinv31cb.grid(row=31, column=4)
cardinalinv32cb = Checkbutton(narenco, variable=cardinalinv32cbval)
cardinalinv32cb.grid(row=32, column=4)
cardinalinv33cb = Checkbutton(narenco, variable=cardinalinv33cbval)
cardinalinv33cb.grid(row=33, column=4)
cardinalinv34cb = Checkbutton(narenco, variable=cardinalinv34cbval)
cardinalinv34cb.grid(row=34, column=4)
cardinalinv35cb = Checkbutton(narenco, variable=cardinalinv35cbval)
cardinalinv35cb.grid(row=35, column=4)
cardinalinv36cb = Checkbutton(narenco, variable=cardinalinv36cbval)
cardinalinv36cb.grid(row=36, column=4)
cardinalinv37cb = Checkbutton(narenco, variable=cardinalinv37cbval)
cardinalinv37cb.grid(row=37, column=4)
cardinalinv38cb = Checkbutton(narenco, variable=cardinalinv38cbval)
cardinalinv38cb.grid(row=38, column=4)
cardinalinv39cb = Checkbutton(narenco, variable=cardinalinv39cbval)
cardinalinv39cb.grid(row=39, column=4)
cardinalinv40cb = Checkbutton(narenco, variable=cardinalinv40cbval)
cardinalinv40cb.grid(row=40, column=4)
cardinalinv41cb = Checkbutton(narenco, variable=cardinalinv41cbval)
cardinalinv41cb.grid(row=41, column=4)
cardinalinv42cb = Checkbutton(narenco, variable=cardinalinv42cbval)
cardinalinv42cb.grid(row=42, column=4)
cardinalinv43cb = Checkbutton(narenco, variable=cardinalinv43cbval)
cardinalinv43cb.grid(row=43, column=4)
cardinalinv44cb = Checkbutton(narenco, variable=cardinalinv44cbval)
cardinalinv44cb.grid(row=44, column=4)
cardinalinv45cb = Checkbutton(narenco, variable=cardinalinv45cbval)
cardinalinv45cb.grid(row=45, column=4)
cardinalinv46cb = Checkbutton(narenco, variable=cardinalinv46cbval)
cardinalinv46cb.grid(row=46, column=4)
cardinalinv47cb = Checkbutton(narenco, variable=cardinalinv47cbval)
cardinalinv47cb.grid(row=47, column=4)
cardinalinv48cb = Checkbutton(narenco, variable=cardinalinv48cbval)
cardinalinv48cb.grid(row=48, column=4)
cardinalinv49cb = Checkbutton(narenco, variable=cardinalinv49cbval)
cardinalinv49cb.grid(row=49, column=4)
cardinalinv50cb = Checkbutton(narenco, variable=cardinalinv50cbval)
cardinalinv50cb.grid(row=50, column=4)
cardinalinv51cb = Checkbutton(narenco, variable=cardinalinv51cbval)
cardinalinv51cb.grid(row=51, column=4)
cardinalinv52cb = Checkbutton(narenco, variable=cardinalinv52cbval)
cardinalinv52cb.grid(row=52, column=4)
cardinalinv53cb = Checkbutton(narenco, variable=cardinalinv53cbval)
cardinalinv53cb.grid(row=53, column=4)
cardinalinv54cb = Checkbutton(narenco, variable=cardinalinv54cbval)
cardinalinv54cb.grid(row=54, column=4)
cardinalinv55cb = Checkbutton(narenco, variable=cardinalinv55cbval)
cardinalinv55cb.grid(row=55, column=4)
cardinalinv56cb = Checkbutton(narenco, variable=cardinalinv56cbval)
cardinalinv56cb.grid(row=56, column=4)
cardinalinv57cb = Checkbutton(narenco, variable=cardinalinv57cbval)
cardinalinv57cb.grid(row=57, column=4)
cardinalinv58cb = Checkbutton(narenco, variable=cardinalinv58cbval)
cardinalinv58cb.grid(row=58, column=4)
cardinalinv59cb = Checkbutton(narenco, variable=cardinalinv59cbval)
cardinalinv59cb.grid(row=59, column=4)

cougar1Label= Label(narenco, text= "Cougar")
cougar1Label.grid(row=0, column=5, columnspan=2)
cougarinv1Label= Label(narenco, text="X")
cougarinv1Label.grid(row=1, column=5)
cougarinv2Label = Label(narenco, text="X")
cougarinv2Label.grid(row=2, column=5)
cougarinv3Label = Label(narenco, text="X")
cougarinv3Label.grid(row=3, column=5)
cougarinv4Label = Label(narenco, text="X")
cougarinv4Label.grid(row=4, column=5)
cougarinv5Label = Label(narenco, text="X")
cougarinv5Label.grid(row=5, column=5)
cougarinv6Label = Label(narenco, text="X")
cougarinv6Label.grid(row=6, column=5)
cougarinv7Label = Label(narenco, text="X")
cougarinv7Label.grid(row=7, column=5)
cougarinv8Label = Label(narenco, text="X")
cougarinv8Label.grid(row=8, column=5)
cougarinv9Label = Label(narenco, text="X")
cougarinv9Label.grid(row=9, column=5)
cougarinv10Label = Label(narenco, text="X")
cougarinv10Label.grid(row=10, column=5)
cougarinv11Label = Label(narenco, text="X")
cougarinv11Label.grid(row=11, column=5)
cougarinv12Label = Label(narenco, text="X")
cougarinv12Label.grid(row=12, column=5)
cougarinv13Label = Label(narenco, text="X")
cougarinv13Label.grid(row=13, column=5)
cougarinv14Label = Label(narenco, text="X")
cougarinv14Label.grid(row=14, column=5)
cougarinv15Label = Label(narenco, text="X")
cougarinv15Label.grid(row=15, column=5)
cougarinv16Label = Label(narenco, text="X")
cougarinv16Label.grid(row=16, column=5)
cougarinv17Label = Label(narenco, text="X")
cougarinv17Label.grid(row=17, column=5)
cougarinv18Label = Label(narenco, text="X")
cougarinv18Label.grid(row=18, column=5)
cougarinv19Label = Label(narenco, text="X")
cougarinv19Label.grid(row=19, column=5)
cougarinv20Label = Label(narenco, text="X")
cougarinv20Label.grid(row=20, column=5)
cougarinv21Label = Label(narenco, text="X")
cougarinv21Label.grid(row=21, column=5)
cougarinv22Label = Label(narenco, text="X")
cougarinv22Label.grid(row=22, column=5)
cougarinv23Label = Label(narenco, text="X")
cougarinv23Label.grid(row=23, column=5)
cougarinv24Label = Label(narenco, text="X")
cougarinv24Label.grid(row=24, column=5)
cougarinv25Label = Label(narenco, text="X")
cougarinv25Label.grid(row=25, column=5)
cougarinv26Label = Label(narenco, text="X")
cougarinv26Label.grid(row=26, column=5)
cougarinv27Label = Label(narenco, text="X")
cougarinv27Label.grid(row=27, column=5)
cougarinv28Label = Label(narenco, text="X")
cougarinv28Label.grid(row=28, column=5)
cougarinv29Label = Label(narenco, text="X")
cougarinv29Label.grid(row=29, column=5)
cougarinv30Label = Label(narenco, text="X")
cougarinv30Label.grid(row=30, column=5)

cougarinv1cb = Checkbutton(narenco, variable=cougarinv1cbval)
cougarinv1cb.grid(row=1, column=6)
cougarinv2cb = Checkbutton(narenco, variable=cougarinv2cbval)
cougarinv2cb.grid(row=2, column=6)
cougarinv3cb = Checkbutton(narenco, variable=cougarinv3cbval)
cougarinv3cb.grid(row=3, column=6)
cougarinv4cb = Checkbutton(narenco, variable=cougarinv4cbval)
cougarinv4cb.grid(row=4, column=6)
cougarinv5cb = Checkbutton(narenco, variable=cougarinv5cbval)
cougarinv5cb.grid(row=5, column=6)
cougarinv6cb = Checkbutton(narenco, variable=cougarinv6cbval)
cougarinv6cb.grid(row=6, column=6)
cougarinv7cb = Checkbutton(narenco, variable=cougarinv7cbval)
cougarinv7cb.grid(row=7, column=6)
cougarinv8cb = Checkbutton(narenco, variable=cougarinv8cbval)
cougarinv8cb.grid(row=8, column=6)
cougarinv9cb = Checkbutton(narenco, variable=cougarinv9cbval)
cougarinv9cb.grid(row=9, column=6)
cougarinv10cb = Checkbutton(narenco, variable=cougarinv10cbval)
cougarinv10cb.grid(row=10, column=6)
cougarinv11cb = Checkbutton(narenco, variable=cougarinv11cbval)
cougarinv11cb.grid(row=11, column=6)
cougarinv12cb = Checkbutton(narenco, variable=cougarinv12cbval)
cougarinv12cb.grid(row=12, column=6)
cougarinv13cb = Checkbutton(narenco, variable=cougarinv13cbval)
cougarinv13cb.grid(row=13, column=6)
cougarinv14cb = Checkbutton(narenco, variable=cougarinv14cbval)
cougarinv14cb.grid(row=14, column=6)
cougarinv15cb = Checkbutton(narenco, variable=cougarinv15cbval)
cougarinv15cb.grid(row=15, column=6)
cougarinv16cb = Checkbutton(narenco, variable=cougarinv16cbval)
cougarinv16cb.grid(row=16, column=6)
cougarinv17cb = Checkbutton(narenco, variable=cougarinv17cbval)
cougarinv17cb.grid(row=17, column=6)
cougarinv18cb = Checkbutton(narenco, variable=cougarinv18cbval)
cougarinv18cb.grid(row=18, column=6)
cougarinv19cb = Checkbutton(narenco, variable=cougarinv19cbval)
cougarinv19cb.grid(row=19, column=6)
cougarinv20cb = Checkbutton(narenco, variable=cougarinv20cbval)
cougarinv20cb.grid(row=20, column=6)
cougarinv21cb = Checkbutton(narenco, variable=cougarinv21cbval)
cougarinv21cb.grid(row=21, column=6)
cougarinv22cb = Checkbutton(narenco, variable=cougarinv22cbval)
cougarinv22cb.grid(row=22, column=6)
cougarinv23cb = Checkbutton(narenco, variable=cougarinv23cbval)
cougarinv23cb.grid(row=23, column=6)
cougarinv24cb = Checkbutton(narenco, variable=cougarinv24cbval)
cougarinv24cb.grid(row=24, column=6)
cougarinv25cb = Checkbutton(narenco, variable=cougarinv25cbval)
cougarinv25cb.grid(row=25, column=6)
cougarinv26cb = Checkbutton(narenco, variable=cougarinv26cbval)
cougarinv26cb.grid(row=26, column=6)
cougarinv27cb = Checkbutton(narenco, variable=cougarinv27cbval)
cougarinv27cb.grid(row=27, column=6)
cougarinv28cb = Checkbutton(narenco, variable=cougarinv28cbval)
cougarinv28cb.grid(row=28, column=6)
cougarinv29cb = Checkbutton(narenco, variable=cougarinv29cbval)
cougarinv29cb.grid(row=29, column=6)
cougarinv30cb = Checkbutton(narenco, variable=cougarinv30cbval)
cougarinv30cb.grid(row=30, column=6)

cherry1Label= Label(narenco, text= "Cherry")
cherry1Label.grid(row=0, column=7, columnspan=2)
cherryinv1Label= Label(narenco, text= "X")
cherryinv1Label.grid(row=1, column=7)
cherryinv2Label = Label(narenco, text="X")
cherryinv2Label.grid(row=2, column=7)

# Cherry Inv 3
cherryinv3Label = Label(narenco, text="X")
cherryinv3Label.grid(row=3, column=7)

# Cherry Inv 4
cherryinv4Label = Label(narenco, text="X")
cherryinv4Label.grid(row=4, column=7)
#CheckBoxes
cherryinv1cb = Checkbutton(narenco, variable=cherryinv1cbval)
cherryinv1cb.grid(row=1, column=8)
cherryinv2cb = Checkbutton(narenco, variable=cherryinv2cbval)
cherryinv2cb.grid(row=2, column=8)
cherryinv3cb = Checkbutton(narenco, variable=cherryinv3cbval)
cherryinv3cb.grid(row=3, column=8)
cherryinv4cb = Checkbutton(narenco, variable=cherryinv4cbval)
cherryinv4cb.grid(row=4, column=8)

conetoe1Label= Label(soltage, text= "Conetoe")
conetoe1Label.grid(row=0, column=1, columnspan= 2)

conetoeinv1Label= Label(soltage, text= "X")
conetoeinv1Label.grid(row=1, column= 1)

# Conetoe Inv 2
conetoeinv2Label = Label(soltage, text="X")
conetoeinv2Label.grid(row=2, column=1)

# Conetoe Inv 3
conetoeinv3Label = Label(soltage, text="X")
conetoeinv3Label.grid(row=3, column=1)

# Conetoe Inv 4
conetoeinv4Label = Label(soltage, text="X")
conetoeinv4Label.grid(row=4, column=1)

#CheckBoxes
conetoeinv1cb = Checkbutton(soltage, variable=conetoeinv1cbval)
conetoeinv1cb.grid(row=1, column= 2)
conetoeinv2cb = Checkbutton(soltage, variable=conetoeinv2cbval)
conetoeinv2cb.grid(row=2, column= 2)
conetoeinv3cb = Checkbutton(soltage, variable=conetoeinv3cbval)
conetoeinv3cb.grid(row=3, column= 2)
conetoeinv4cb = Checkbutton(soltage, variable=conetoeinv4cbval)
conetoeinv4cb.grid(row=4, column= 2)

duplin1Label= Label(soltage, text= "Duplin")
duplin1Label.grid(row=0, column=3, columnspan= 2)
duplininv1Label= Label(soltage, text= "X")
duplininv1Label.grid(row=1, column=3)
duplininv1cb = Checkbutton(soltage, variable=duplininv1cbval)
duplininv1cb.grid(row=1, column= 4)

duplininv2Label = Label(soltage, text="X")
duplininv2Label.grid(row=2, column=3)
duplininv2cb = Checkbutton(soltage, variable=duplininv2cbval)
duplininv2cb.grid(row=2, column= 4)

duplininv3Label = Label(soltage, text="X")
duplininv3Label.grid(row=3, column=3)
duplininv3cb = Checkbutton(soltage, variable=duplininv3cbval)
duplininv3cb.grid(row=3, column= 4)

# String Inv 1
duplininv4Label = Label(soltage, text="X")
duplininv4Label.grid(row=4, column=3)
duplininv4cb = Checkbutton(soltage, variable=duplininv4cbval)
duplininv4cb.grid(row=4, column= 4)
# String Inv 2
duplininv5Label = Label(soltage, text="X")
duplininv5Label.grid(row=5, column=3)
duplininv5cb = Checkbutton(soltage, variable=duplininv5cbval)
duplininv5cb.grid(row=5, column= 4)
#
duplininv6Label = Label(soltage, text="X")
duplininv6Label.grid(row=6, column=3)
duplininv6cb = Checkbutton(soltage, variable=duplininv6cbval)
duplininv6cb.grid(row=6, column= 4)
#
duplininv7Label = Label(soltage, text="X")
duplininv7Label.grid(row=7, column=3)
duplininv7cb = Checkbutton(soltage, variable=duplininv7cbval)
duplininv7cb.grid(row=7, column= 4)
duplininv8Label = Label(soltage, text="X")
duplininv8Label.grid(row=8, column=3)
duplininv8cb = Checkbutton(soltage, variable=duplininv8cbval)
duplininv8cb.grid(row=8, column= 4)
duplininv9Label = Label(soltage, text="X")
duplininv9Label.grid(row=9, column=3)
duplininv9cb = Checkbutton(soltage, variable=duplininv9cbval)
duplininv9cb.grid(row=9, column= 4)
duplininv10Label = Label(soltage, text="X")
duplininv10Label.grid(row=10, column=3)
duplininv10cb = Checkbutton(soltage, variable=duplininv10cbval)
duplininv10cb.grid(row=10, column= 4)
duplininv11Label = Label(soltage, text="X")
duplininv11Label.grid(row=11, column=3)
duplininv11cb = Checkbutton(soltage, variable=duplininv11cbval)
duplininv11cb.grid(row=11, column= 4)
duplininv12Label = Label(soltage, text="X")
duplininv12Label.grid(row=12, column=3)
duplininv12cb = Checkbutton(soltage, variable=duplininv12cbval)
duplininv12cb.grid(row=12, column= 4)
duplininv13Label = Label(soltage, text="X")
duplininv13Label.grid(row=13, column=3)
duplininv13cb = Checkbutton(soltage, variable=duplininv13cbval)
duplininv13cb.grid(row=13, column= 4)
duplininv14Label = Label(soltage, text="X")
duplininv14Label.grid(row=14, column=3)
duplininv14cb = Checkbutton(soltage, variable=duplininv14cbval)
duplininv14cb.grid(row=14, column= 4)
duplininv15Label = Label(soltage, text="X")
duplininv15Label.grid(row=15, column=3)
duplininv15cb = Checkbutton(soltage, variable=duplininv15cbval)
duplininv15cb.grid(row=15, column= 4)
duplininv16Label = Label(soltage, text="X")
duplininv16Label.grid(row=16, column=3)
duplininv16cb = Checkbutton(soltage, variable=duplininv16cbval)
duplininv16cb.grid(row=16, column= 4)
duplininv17Label = Label(soltage, text="X")
duplininv17Label.grid(row=17, column=3)
duplininv17cb = Checkbutton(soltage, variable=duplininv17cbval)
duplininv17cb.grid(row=17, column= 4)
duplininv18Label = Label(soltage, text="X")
duplininv18Label.grid(row=18, column=3)
duplininv18cb = Checkbutton(soltage, variable=duplininv18cbval)
duplininv18cb.grid(row=18, column= 4)
duplininv19Label = Label(soltage, text="X")
duplininv19Label.grid(row=19, column=3)
duplininv19cb = Checkbutton(soltage, variable=duplininv19cbval)
duplininv19cb.grid(row=19, column= 4)
duplininv20Label = Label(soltage, text="X")
duplininv20Label.grid(row=20, column=3)
duplininv20cb = Checkbutton(soltage, variable=duplininv20cbval)
duplininv20cb.grid(row=20, column= 4)
duplininv21Label = Label(soltage, text="X")
duplininv21Label.grid(row=21, column=3)
duplininv21cb = Checkbutton(soltage, variable=duplininv21cbval)
duplininv21cb.grid(row=21, column= 4)

#Elk
elk1Label= Label(solrvr, text= "Elk")
elk1Label.grid(row=0, column=5, columnspan=2)

elkinv1Label= Label(solrvr, text= "X")
elkinv1Label.grid(row= 1, column=5)

elkinv2Label = Label(solrvr, text="X")
elkinv2Label.grid(row=2, column=5)

# elk Inv 3
elkinv3Label = Label(solrvr, text="X")
elkinv3Label.grid(row=3, column=5)

# elk Inv 4
elkinv4Label = Label(solrvr, text="X")
elkinv4Label.grid(row=4, column=5)

# elk Inv 5
elkinv5Label = Label(solrvr, text="X")
elkinv5Label.grid(row=5, column=5)

# elk Inv 6
elkinv6Label = Label(solrvr, text="X")
elkinv6Label.grid(row=6, column=5)

# elk Inv 7
elkinv7Label = Label(solrvr, text="X")
elkinv7Label.grid(row=7, column=5)

# elk Inv 8
elkinv8Label = Label(solrvr, text="X")
elkinv8Label.grid(row=8, column=5)

# elk Inv 9
elkinv9Label = Label(solrvr, text="X")
elkinv9Label.grid(row=9, column=5)

# elk Inv 10
elkinv10Label = Label(solrvr, text="X")
elkinv10Label.grid(row=10, column=5)

# elk Inv 11
elkinv11Label = Label(solrvr, text="X")
elkinv11Label.grid(row=11, column=5)

# elk Inv 12
elkinv12Label = Label(solrvr, text="X")
elkinv12Label.grid(row=12, column=5)

# elk Inv 13
elkinv13Label = Label(solrvr, text="X")
elkinv13Label.grid(row=13, column=5)

# elk Inv 14
elkinv14Label = Label(solrvr, text="X")
elkinv14Label.grid(row=14, column=5)

# elk Inv 15
elkinv15Label = Label(solrvr, text="X")
elkinv15Label.grid(row=15, column=5)

# elk Inv 16
elkinv16Label = Label(solrvr, text="X")
elkinv16Label.grid(row=16, column=5)

# elk Inv 17
elkinv17Label = Label(solrvr, text="X")
elkinv17Label.grid(row=17, column=5)

# elk Inv 18
elkinv18Label = Label(solrvr, text="X")
elkinv18Label.grid(row=18, column=5)

# elk Inv 19
elkinv19Label = Label(solrvr, text="X")
elkinv19Label.grid(row=19, column=5)

# elk Inv 20
elkinv20Label = Label(solrvr, text="X")
elkinv20Label.grid(row=20, column=5)

# elk Inv 21
elkinv21Label = Label(solrvr, text="X")
elkinv21Label.grid(row=21, column=5)

# elk Inv 22
elkinv22Label = Label(solrvr, text="X")
elkinv22Label.grid(row=22, column=5)

# elk Inv 23
elkinv23Label = Label(solrvr, text="X")
elkinv23Label.grid(row=23, column=5)

# elk Inv 24
elkinv24Label = Label(solrvr, text="X")
elkinv24Label.grid(row=24, column=5)

# elk Inv 25
elkinv25Label = Label(solrvr, text="X")
elkinv25Label.grid(row=25, column=5)

# elk Inv 26
elkinv26Label = Label(solrvr, text="X")
elkinv26Label.grid(row=26, column=5)

# elk Inv 27
elkinv27Label = Label(solrvr, text="X")
elkinv27Label.grid(row=27, column=5)

# elk Inv 28
elkinv28Label = Label(solrvr, text="X")
elkinv28Label.grid(row=28, column=5)

# elk Inv 29
elkinv29Label = Label(solrvr, text="X")
elkinv29Label.grid(row=29, column=5)

# elk Inv 30
elkinv30Label = Label(solrvr, text="X")
elkinv30Label.grid(row=30, column=5)

# elk Inv 31
elkinv31Label = Label(solrvr, text="X")
elkinv31Label.grid(row=31, column=5)

# elk Inv 32
elkinv32Label = Label(solrvr, text="X")
elkinv32Label.grid(row=32, column=5)

# elk Inv 33
elkinv33Label = Label(solrvr, text="X")
elkinv33Label.grid(row=33, column=5)

# elk Inv 34
elkinv34Label = Label(solrvr, text="X")
elkinv34Label.grid(row=34, column=5)

# elk Inv 35
elkinv35Label = Label(solrvr, text="X")
elkinv35Label.grid(row=35, column=5)

# elk Inv 36
elkinv36Label = Label(solrvr, text="X")
elkinv36Label.grid(row=36, column=5)

elkinv37Label = Label(solrvr, text="X")
elkinv37Label.grid(row=37, column=5)

# elk Inv 38
elkinv38Label = Label(solrvr, text="X")
elkinv38Label.grid(row=38, column=5)

# elk Inv 39
elkinv39Label = Label(solrvr, text="X")
elkinv39Label.grid(row=39, column=5)

# elk Inv 40
elkinv40Label = Label(solrvr, text="X")
elkinv40Label.grid(row=40, column=5)

# elk Inv 41
elkinv41Label = Label(solrvr, text="X")
elkinv41Label.grid(row=41, column=5)

# elk Inv 42
elkinv42Label = Label(solrvr, text="X")
elkinv42Label.grid(row=42, column=5)

# elk Inv 43
elkinv43Label = Label(solrvr, text="X")
elkinv43Label.grid(row=43, column=5)

elkinv1cb = Checkbutton(solrvr, variable=elkinv1cbval)
elkinv1cb.grid(row=1, column=6)
elkinv2cb = Checkbutton(solrvr, variable=elkinv2cbval)
elkinv2cb.grid(row=2, column=6)
elkinv3cb = Checkbutton(solrvr, variable=elkinv3cbval)
elkinv3cb.grid(row=3, column=6)
elkinv4cb = Checkbutton(solrvr, variable=elkinv4cbval)
elkinv4cb.grid(row=4, column=6)
elkinv5cb = Checkbutton(solrvr, variable=elkinv5cbval)
elkinv5cb.grid(row=5, column=6)
elkinv6cb = Checkbutton(solrvr, variable=elkinv6cbval)
elkinv6cb.grid(row=6, column=6)
elkinv7cb = Checkbutton(solrvr, variable=elkinv7cbval)
elkinv7cb.grid(row=7, column=6)
elkinv8cb = Checkbutton(solrvr, variable=elkinv8cbval)
elkinv8cb.grid(row=8, column=6)
elkinv9cb = Checkbutton(solrvr, variable=elkinv9cbval)
elkinv9cb.grid(row=9, column=6)
elkinv10cb = Checkbutton(solrvr, variable=elkinv10cbval)
elkinv10cb.grid(row=10, column=6)
elkinv11cb = Checkbutton(solrvr, variable=elkinv11cbval)
elkinv11cb.grid(row=11, column=6)
elkinv12cb = Checkbutton(solrvr, variable=elkinv12cbval)
elkinv12cb.grid(row=12, column=6)
elkinv13cb = Checkbutton(solrvr, variable=elkinv13cbval)
elkinv13cb.grid(row=13, column=6)
elkinv14cb = Checkbutton(solrvr, variable=elkinv14cbval)
elkinv14cb.grid(row=14, column=6)
elkinv15cb = Checkbutton(solrvr, variable=elkinv15cbval)
elkinv15cb.grid(row=15, column=6)
elkinv16cb = Checkbutton(solrvr, variable=elkinv16cbval)
elkinv16cb.grid(row=16, column=6)
elkinv17cb = Checkbutton(solrvr, variable=elkinv17cbval)
elkinv17cb.grid(row=17, column=6)
elkinv18cb = Checkbutton(solrvr, variable=elkinv18cbval)
elkinv18cb.grid(row=18, column=6)
elkinv19cb = Checkbutton(solrvr, variable=elkinv19cbval)
elkinv19cb.grid(row=19, column=6)
elkinv20cb = Checkbutton(solrvr, variable=elkinv20cbval)
elkinv20cb.grid(row=20, column=6)
elkinv21cb = Checkbutton(solrvr, variable=elkinv21cbval)
elkinv21cb.grid(row=21, column=6)
elkinv22cb = Checkbutton(solrvr, variable=elkinv22cbval)
elkinv22cb.grid(row=22, column=6)
elkinv23cb = Checkbutton(solrvr, variable=elkinv23cbval)
elkinv23cb.grid(row=23, column=6)
elkinv24cb = Checkbutton(solrvr, variable=elkinv24cbval)
elkinv24cb.grid(row=24, column=6)
elkinv25cb = Checkbutton(solrvr, variable=elkinv25cbval)
elkinv25cb.grid(row=25, column=6)
elkinv26cb = Checkbutton(solrvr, variable=elkinv26cbval)
elkinv26cb.grid(row=26, column=6)
elkinv27cb = Checkbutton(solrvr, variable=elkinv27cbval)
elkinv27cb.grid(row=27, column=6)
elkinv28cb = Checkbutton(solrvr, variable=elkinv28cbval)
elkinv28cb.grid(row=28, column=6)
elkinv29cb = Checkbutton(solrvr, variable=elkinv29cbval)
elkinv29cb.grid(row=29, column=6)
elkinv30cb = Checkbutton(solrvr, variable=elkinv30cbval)
elkinv30cb.grid(row=30, column=6)
elkinv31cb = Checkbutton(solrvr, variable=elkinv31cbval)
elkinv31cb.grid(row=31, column=6)
elkinv32cb = Checkbutton(solrvr, variable=elkinv32cbval)
elkinv32cb.grid(row=32, column=6)
elkinv33cb = Checkbutton(solrvr, variable=elkinv33cbval)
elkinv33cb.grid(row=33, column=6)
elkinv34cb = Checkbutton(solrvr, variable=elkinv34cbval)
elkinv34cb.grid(row=34, column=6)
elkinv35cb = Checkbutton(solrvr, variable=elkinv35cbval)
elkinv35cb.grid(row=35, column=6)
elkinv36cb = Checkbutton(solrvr, variable=elkinv36cbval)
elkinv36cb.grid(row=36, column=6)
elkinv37cb = Checkbutton(solrvr, variable=elkinv37cbval)
elkinv37cb.grid(row=37, column=6)
elkinv38cb = Checkbutton(solrvr, variable=elkinv38cbval)
elkinv38cb.grid(row=38, column=6)
elkinv39cb = Checkbutton(solrvr, variable=elkinv39cbval)
elkinv39cb.grid(row=39, column=6)
elkinv40cb = Checkbutton(solrvr, variable=elkinv40cbval)
elkinv40cb.grid(row=40, column=6)
elkinv41cb = Checkbutton(solrvr, variable=elkinv41cbval)
elkinv41cb.grid(row=41, column=6)
elkinv42cb = Checkbutton(solrvr, variable=elkinv42cbval)
elkinv42cb.grid(row=42, column=6)
elkinv43cb = Checkbutton(solrvr, variable=elkinv43cbval)
elkinv43cb.grid(row=43, column=6)








freight1Label= Label(ncemc, text= "Freight Line")
freight1Label.grid(row=0, column=1, columnspan=2)
freightlineinv1Label= Label(ncemc, text= "X")
freightlineinv1Label.grid(row=1, column=1)

freightlineinv2Label = Label(ncemc, text="X")
freightlineinv2Label.grid(row=2, column=1)

# Freightline Inv 3
freightlineinv3Label = Label(ncemc, text="X")
freightlineinv3Label.grid(row=3, column=1)

# Freightline Inv 4
freightlineinv4Label = Label(ncemc, text="X")
freightlineinv4Label.grid(row=4, column=1)

# Freightline Inv 5
freightlineinv5Label = Label(ncemc, text="X")
freightlineinv5Label.grid(row=5, column=1)

# Freightline Inv 6
freightlineinv6Label = Label(ncemc, text="X")
freightlineinv6Label.grid(row=6, column=1)

# Freightline Inv 7
freightlineinv7Label = Label(ncemc, text="X")
freightlineinv7Label.grid(row=7, column=1)

# Freightline Inv 8
freightlineinv8Label = Label(ncemc, text="X")
freightlineinv8Label.grid(row=8, column=1)

# Freightline Inv 9
freightlineinv9Label = Label(ncemc, text="X")
freightlineinv9Label.grid(row=9, column=1)

# Freightline Inv 10
freightlineinv10Label = Label(ncemc, text="X")
freightlineinv10Label.grid(row=10, column=1)

# Freightline Inv 11
freightlineinv11Label = Label(ncemc, text="X")
freightlineinv11Label.grid(row=11, column=1)

# Freightline Inv 12
freightlineinv12Label = Label(ncemc, text="X")
freightlineinv12Label.grid(row=12, column=1)

# Freightline Inv 13
freightlineinv13Label = Label(ncemc, text="X")
freightlineinv13Label.grid(row=13, column=1)

# Freightline Inv 14
freightlineinv14Label = Label(ncemc, text="X")
freightlineinv14Label.grid(row=14, column=1)

# Freightline Inv 15
freightlineinv15Label = Label(ncemc, text="X")
freightlineinv15Label.grid(row=15, column=1)

# Freightline Inv 16
freightlineinv16Label = Label(ncemc, text="X")
freightlineinv16Label.grid(row=16, column=1)

# Freightline Inv 17
freightlineinv17Label = Label(ncemc, text="X")
freightlineinv17Label.grid(row=17, column=1)

# Freightline Inv 18
freightlineinv18Label = Label(ncemc, text="X")
freightlineinv18Label.grid(row=18, column=1)
freightlineinv1cb = Checkbutton(ncemc, variable=freightlineinv1cbval)
freightlineinv1cb.grid(row=1, column= 2)
freightlineinv2cb = Checkbutton(ncemc, variable=freightlineinv2cbval)
freightlineinv2cb.grid(row=2, column= 2)
freightlineinv3cb = Checkbutton(ncemc, variable=freightlineinv3cbval)
freightlineinv3cb.grid(row=3, column= 2)
freightlineinv4cb = Checkbutton(ncemc, variable=freightlineinv4cbval)
freightlineinv4cb.grid(row=4, column= 2)
freightlineinv5cb = Checkbutton(ncemc, variable=freightlineinv5cbval)
freightlineinv5cb.grid(row=5, column= 2)
freightlineinv6cb = Checkbutton(ncemc, variable=freightlineinv6cbval)
freightlineinv6cb.grid(row=6, column= 2)
freightlineinv7cb = Checkbutton(ncemc, variable=freightlineinv7cbval)
freightlineinv7cb.grid(row=7, column= 2)
freightlineinv8cb = Checkbutton(ncemc, variable=freightlineinv8cbval)
freightlineinv8cb.grid(row=8, column= 2)
freightlineinv9cb = Checkbutton(ncemc, variable=freightlineinv9cbval)
freightlineinv9cb.grid(row=9, column= 2)
freightlineinv10cb = Checkbutton(ncemc, variable=freightlineinv10cbval)
freightlineinv10cb.grid(row=10, column= 2)
freightlineinv11cb = Checkbutton(ncemc, variable=freightlineinv11cbval)
freightlineinv11cb.grid(row=11, column= 2)
freightlineinv12cb = Checkbutton(ncemc, variable=freightlineinv12cbval)
freightlineinv12cb.grid(row=12, column= 2)
freightlineinv13cb = Checkbutton(ncemc, variable=freightlineinv13cbval)
freightlineinv13cb.grid(row=13, column= 2)
freightlineinv14cb = Checkbutton(ncemc, variable=freightlineinv14cbval)
freightlineinv14cb.grid(row=14, column= 2)
freightlineinv15cb = Checkbutton(ncemc, variable=freightlineinv15cbval)
freightlineinv15cb.grid(row=15, column= 2)
freightlineinv16cb = Checkbutton(ncemc, variable=freightlineinv16cbval)
freightlineinv16cb.grid(row=16, column= 2)
freightlineinv17cb = Checkbutton(ncemc, variable=freightlineinv17cbval)
freightlineinv17cb.grid(row=17, column= 2)
freightlineinv18cb = Checkbutton(ncemc, variable=freightlineinv18cbval)
freightlineinv18cb.grid(row=18, column= 2)


grayfox1Label= Label(solrvr, text= "Gray Fox")
grayfox1Label.grid(row=0, column=7, columnspan=2)

grayfoxinv1Label= Label(solrvr, text= "X")
grayfoxinv1Label.grid(row= 1, column=7)

grayfoxinv2Label = Label(solrvr, text="X")
grayfoxinv2Label.grid(row=2, column=7)

# Grayfox Inv 3
grayfoxinv3Label = Label(solrvr, text="X")
grayfoxinv3Label.grid(row=3, column=7)

# Grayfox Inv 4
grayfoxinv4Label = Label(solrvr, text="X")
grayfoxinv4Label.grid(row=4, column=7)

# Grayfox Inv 5
grayfoxinv5Label = Label(solrvr, text="X")
grayfoxinv5Label.grid(row=5, column=7)

# Grayfox Inv 6
grayfoxinv6Label = Label(solrvr, text="X")
grayfoxinv6Label.grid(row=6, column=7)

# Grayfox Inv 7
grayfoxinv7Label = Label(solrvr, text="X")
grayfoxinv7Label.grid(row=7, column=7)

# Grayfox Inv 8
grayfoxinv8Label = Label(solrvr, text="X")
grayfoxinv8Label.grid(row=8, column=7)

# Grayfox Inv 9
grayfoxinv9Label = Label(solrvr, text="X")
grayfoxinv9Label.grid(row=9, column=7)

# Grayfox Inv 10
grayfoxinv10Label = Label(solrvr, text="X")
grayfoxinv10Label.grid(row=10, column=7)

# Grayfox Inv 11
grayfoxinv11Label = Label(solrvr, text="X")
grayfoxinv11Label.grid(row=11, column=7)

# Grayfox Inv 12
grayfoxinv12Label = Label(solrvr, text="X")
grayfoxinv12Label.grid(row=12, column=7)

# Grayfox Inv 13
grayfoxinv13Label = Label(solrvr, text="X")
grayfoxinv13Label.grid(row=13, column=7)

# Grayfox Inv 14
grayfoxinv14Label = Label(solrvr, text="X")
grayfoxinv14Label.grid(row=14, column=7)

# Grayfox Inv 15
grayfoxinv15Label = Label(solrvr, text="X")
grayfoxinv15Label.grid(row=15, column=7)

# Grayfox Inv 16
grayfoxinv16Label = Label(solrvr, text="X")
grayfoxinv16Label.grid(row=16, column=7)

# Grayfox Inv 17
grayfoxinv17Label = Label(solrvr, text="X")
grayfoxinv17Label.grid(row=17, column=7)

# Grayfox Inv 18
grayfoxinv18Label = Label(solrvr, text="X")
grayfoxinv18Label.grid(row=18, column=7)

# Grayfox Inv 19
grayfoxinv19Label = Label(solrvr, text="X")
grayfoxinv19Label.grid(row=19, column=7)

# Grayfox Inv 20
grayfoxinv20Label = Label(solrvr, text="X")
grayfoxinv20Label.grid(row=20, column=7)

# Grayfox Inv 21
grayfoxinv21Label = Label(solrvr, text="X")
grayfoxinv21Label.grid(row=21, column=7)

# Grayfox Inv 22
grayfoxinv22Label = Label(solrvr, text="X")
grayfoxinv22Label.grid(row=22, column=7)

# Grayfox Inv 23
grayfoxinv23Label = Label(solrvr, text="X")
grayfoxinv23Label.grid(row=23, column=7)

# Grayfox Inv 24
grayfoxinv24Label = Label(solrvr, text="X")
grayfoxinv24Label.grid(row=24, column=7)

# Grayfox Inv 25
grayfoxinv25Label = Label(solrvr, text="X")
grayfoxinv25Label.grid(row=25, column=7)

# Grayfox Inv 26
grayfoxinv26Label = Label(solrvr, text="X")
grayfoxinv26Label.grid(row=26, column=7)

# Grayfox Inv 27
grayfoxinv27Label = Label(solrvr, text="X")
grayfoxinv27Label.grid(row=27, column=7)

# Grayfox Inv 28
grayfoxinv28Label = Label(solrvr, text="X")
grayfoxinv28Label.grid(row=28, column=7)

# Grayfox Inv 29
grayfoxinv29Label = Label(solrvr, text="X")
grayfoxinv29Label.grid(row=29, column=7)

# Grayfox Inv 30
grayfoxinv30Label = Label(solrvr, text="X")
grayfoxinv30Label.grid(row=30, column=7)

# Grayfox Inv 31
grayfoxinv31Label = Label(solrvr, text="X")
grayfoxinv31Label.grid(row=31, column=7)

# Grayfox Inv 32
grayfoxinv32Label = Label(solrvr, text="X")
grayfoxinv32Label.grid(row=32, column=7)

# Grayfox Inv 33
grayfoxinv33Label = Label(solrvr, text="X")
grayfoxinv33Label.grid(row=33, column=7)

# Grayfox Inv 34
grayfoxinv34Label = Label(solrvr, text="X")
grayfoxinv34Label.grid(row=34, column=7)

# Grayfox Inv 35
grayfoxinv35Label = Label(solrvr, text="X")
grayfoxinv35Label.grid(row=35, column=7)

# Grayfox Inv 36
grayfoxinv36Label = Label(solrvr, text="X")
grayfoxinv36Label.grid(row=36, column=7)

grayfoxinv37Label = Label(solrvr, text="X")
grayfoxinv37Label.grid(row=37, column=7)

# Grayfox Inv 38
grayfoxinv38Label = Label(solrvr, text="X")
grayfoxinv38Label.grid(row=38, column=7)

# Grayfox Inv 39
grayfoxinv39Label = Label(solrvr, text="X")
grayfoxinv39Label.grid(row=39, column=7)

# Grayfox Inv 40
grayfoxinv40Label = Label(solrvr, text="X")
grayfoxinv40Label.grid(row=40, column=7)

grayfoxinv1cb = Checkbutton(solrvr, variable=grayfoxinv1cbval)
grayfoxinv1cb.grid(row=1, column=8)
grayfoxinv2cb = Checkbutton(solrvr, variable=grayfoxinv2cbval)
grayfoxinv2cb.grid(row=2, column=8)
grayfoxinv3cb = Checkbutton(solrvr, variable=grayfoxinv3cbval)
grayfoxinv3cb.grid(row=3, column=8)
grayfoxinv4cb = Checkbutton(solrvr, variable=grayfoxinv4cbval)
grayfoxinv4cb.grid(row=4, column=8)
grayfoxinv5cb = Checkbutton(solrvr, variable=grayfoxinv5cbval)
grayfoxinv5cb.grid(row=5, column=8)
grayfoxinv6cb = Checkbutton(solrvr, variable=grayfoxinv6cbval)
grayfoxinv6cb.grid(row=6, column=8)
grayfoxinv7cb = Checkbutton(solrvr, variable=grayfoxinv7cbval)
grayfoxinv7cb.grid(row=7, column=8)
grayfoxinv8cb = Checkbutton(solrvr, variable=grayfoxinv8cbval)
grayfoxinv8cb.grid(row=8, column=8)
grayfoxinv9cb = Checkbutton(solrvr, variable=grayfoxinv9cbval)
grayfoxinv9cb.grid(row=9, column=8)
grayfoxinv10cb = Checkbutton(solrvr, variable=grayfoxinv10cbval)
grayfoxinv10cb.grid(row=10, column=8)
grayfoxinv11cb = Checkbutton(solrvr, variable=grayfoxinv11cbval)
grayfoxinv11cb.grid(row=11, column=8)
grayfoxinv12cb = Checkbutton(solrvr, variable=grayfoxinv12cbval)
grayfoxinv12cb.grid(row=12, column=8)
grayfoxinv13cb = Checkbutton(solrvr, variable=grayfoxinv13cbval)
grayfoxinv13cb.grid(row=13, column=8)
grayfoxinv14cb = Checkbutton(solrvr, variable=grayfoxinv14cbval)
grayfoxinv14cb.grid(row=14, column=8)
grayfoxinv15cb = Checkbutton(solrvr, variable=grayfoxinv15cbval)
grayfoxinv15cb.grid(row=15, column=8)
grayfoxinv16cb = Checkbutton(solrvr, variable=grayfoxinv16cbval)
grayfoxinv16cb.grid(row=16, column=8)
grayfoxinv17cb = Checkbutton(solrvr, variable=grayfoxinv17cbval)
grayfoxinv17cb.grid(row=17, column=8)
grayfoxinv18cb = Checkbutton(solrvr, variable=grayfoxinv18cbval)
grayfoxinv18cb.grid(row=18, column=8)
grayfoxinv19cb = Checkbutton(solrvr, variable=grayfoxinv19cbval)
grayfoxinv19cb.grid(row=19, column=8)
grayfoxinv20cb = Checkbutton(solrvr, variable=grayfoxinv20cbval)
grayfoxinv20cb.grid(row=20, column=8)
grayfoxinv21cb = Checkbutton(solrvr, variable=grayfoxinv21cbval)
grayfoxinv21cb.grid(row=21, column=8)
grayfoxinv22cb = Checkbutton(solrvr, variable=grayfoxinv22cbval)
grayfoxinv22cb.grid(row=22, column=8)
grayfoxinv23cb = Checkbutton(solrvr, variable=grayfoxinv23cbval)
grayfoxinv23cb.grid(row=23, column=8)
grayfoxinv24cb = Checkbutton(solrvr, variable=grayfoxinv24cbval)
grayfoxinv24cb.grid(row=24, column=8)
grayfoxinv25cb = Checkbutton(solrvr, variable=grayfoxinv25cbval)
grayfoxinv25cb.grid(row=25, column=8)
grayfoxinv26cb = Checkbutton(solrvr, variable=grayfoxinv26cbval)
grayfoxinv26cb.grid(row=26, column=8)
grayfoxinv27cb = Checkbutton(solrvr, variable=grayfoxinv27cbval)
grayfoxinv27cb.grid(row=27, column=8)
grayfoxinv28cb = Checkbutton(solrvr, variable=grayfoxinv28cbval)
grayfoxinv28cb.grid(row=28, column=8)
grayfoxinv29cb = Checkbutton(solrvr, variable=grayfoxinv29cbval)
grayfoxinv29cb.grid(row=29, column=8)
grayfoxinv30cb = Checkbutton(solrvr, variable=grayfoxinv30cbval)
grayfoxinv30cb.grid(row=30, column=8)
grayfoxinv31cb = Checkbutton(solrvr, variable=grayfoxinv31cbval)
grayfoxinv31cb.grid(row=31, column=8)
grayfoxinv32cb = Checkbutton(solrvr, variable=grayfoxinv32cbval)
grayfoxinv32cb.grid(row=32, column=8)
grayfoxinv33cb = Checkbutton(solrvr, variable=grayfoxinv33cbval)
grayfoxinv33cb.grid(row=33, column=8)
grayfoxinv34cb = Checkbutton(solrvr, variable=grayfoxinv34cbval)
grayfoxinv34cb.grid(row=34, column=8)
grayfoxinv35cb = Checkbutton(solrvr, variable=grayfoxinv35cbval)
grayfoxinv35cb.grid(row=35, column=8)
grayfoxinv36cb = Checkbutton(solrvr, variable=grayfoxinv36cbval)
grayfoxinv36cb.grid(row=36, column=8)
grayfoxinv37cb = Checkbutton(solrvr, variable=grayfoxinv37cbval)
grayfoxinv37cb.grid(row=37, column=8)
grayfoxinv38cb = Checkbutton(solrvr, variable=grayfoxinv38cbval)
grayfoxinv38cb.grid(row=38, column=8)
grayfoxinv39cb = Checkbutton(solrvr, variable=grayfoxinv39cbval)
grayfoxinv39cb.grid(row=39, column=8)
grayfoxinv40cb = Checkbutton(solrvr, variable=grayfoxinv40cbval)
grayfoxinv40cb.grid(row=40, column=8)




harding1Label= Label(solrvr, text= "Harding")
harding1Label.grid(row=0, column=9, columnspan=2)

hardinginv1Label= Label(solrvr, text= "X")
hardinginv1Label.grid(row= 1, column=9)

hardinginv2Label = Label(solrvr, text="X")
hardinginv2Label.grid(row=2, column=9)

# Harding Inv 3
hardinginv3Label = Label(solrvr, text="X")
hardinginv3Label.grid(row=3, column=9)

# Harding Inv 4
hardinginv4Label = Label(solrvr, text="X")
hardinginv4Label.grid(row=4, column=9)

# Harding Inv 5
hardinginv5Label = Label(solrvr, text="X")
hardinginv5Label.grid(row=5, column=9)

# Harding Inv 6
hardinginv6Label = Label(solrvr, text="X")
hardinginv6Label.grid(row=6, column=9)

# Harding Inv 7
hardinginv7Label = Label(solrvr, text="X")
hardinginv7Label.grid(row=7, column=9)

# Harding Inv 8
hardinginv8Label = Label(solrvr, text="X")
hardinginv8Label.grid(row=8, column=9)

# Harding Inv 9
hardinginv9Label = Label(solrvr, text="X")
hardinginv9Label.grid(row=9, column=9)

# Harding Inv 10
hardinginv10Label = Label(solrvr, text="X")
hardinginv10Label.grid(row=10, column=9)

# Harding Inv 11
hardinginv11Label = Label(solrvr, text="X")
hardinginv11Label.grid(row=11, column=9)

# Harding Inv 12
hardinginv12Label = Label(solrvr, text="X")
hardinginv12Label.grid(row=12, column=9)

# Harding Inv 13
hardinginv13Label = Label(solrvr, text="X")
hardinginv13Label.grid(row=13, column=9)

# Harding Inv 14
hardinginv14Label = Label(solrvr, text="X")
hardinginv14Label.grid(row=14, column=9)

# Harding Inv 15
hardinginv15Label = Label(solrvr, text="X")
hardinginv15Label.grid(row=15, column=9)

# Harding Inv 16
hardinginv16Label = Label(solrvr, text="X")
hardinginv16Label.grid(row=16, column=9)

# Harding Inv 17
hardinginv17Label = Label(solrvr, text="X")
hardinginv17Label.grid(row=17, column=9)

# Harding Inv 18
hardinginv18Label = Label(solrvr, text="X")
hardinginv18Label.grid(row=18, column=9)

# Harding Inv 19
hardinginv19Label = Label(solrvr, text="X")
hardinginv19Label.grid(row=19, column=9)

# Harding Inv 20
hardinginv20Label = Label(solrvr, text="X")
hardinginv20Label.grid(row=20, column=9)
# Harding Inv 21
hardinginv21Label = Label(solrvr, text="X")
hardinginv21Label.grid(row=21, column=9)

# Harding Inv 22
hardinginv22Label = Label(solrvr, text="X")
hardinginv22Label.grid(row=22, column=9)

# Harding Inv 23
hardinginv23Label = Label(solrvr, text="X")
hardinginv23Label.grid(row=23, column=9)

# Harding Inv 24
hardinginv24Label = Label(solrvr, text="X")
hardinginv24Label.grid(row=24, column=9)

hardinginv1cb = Checkbutton(solrvr, variable=hardinginv1cbval)
hardinginv1cb.grid(row=1, column=10)
hardinginv2cb = Checkbutton(solrvr, variable=hardinginv2cbval)
hardinginv2cb.grid(row=2, column=10)
hardinginv3cb = Checkbutton(solrvr, variable=hardinginv3cbval)
hardinginv3cb.grid(row=3, column=10)
hardinginv4cb = Checkbutton(solrvr, variable=hardinginv4cbval)
hardinginv4cb.grid(row=4, column=10)
hardinginv5cb = Checkbutton(solrvr, variable=hardinginv5cbval)
hardinginv5cb.grid(row=5, column=10)
hardinginv6cb = Checkbutton(solrvr, variable=hardinginv6cbval)
hardinginv6cb.grid(row=6, column=10)
hardinginv7cb = Checkbutton(solrvr, variable=hardinginv7cbval)
hardinginv7cb.grid(row=7, column=10)
hardinginv8cb = Checkbutton(solrvr, variable=hardinginv8cbval)
hardinginv8cb.grid(row=8, column=10)
hardinginv9cb = Checkbutton(solrvr, variable=hardinginv9cbval)
hardinginv9cb.grid(row=9, column=10)
hardinginv10cb = Checkbutton(solrvr, variable=hardinginv10cbval)
hardinginv10cb.grid(row=10, column=10)
hardinginv11cb = Checkbutton(solrvr, variable=hardinginv11cbval)
hardinginv11cb.grid(row=11, column=10)
hardinginv12cb = Checkbutton(solrvr, variable=hardinginv12cbval)
hardinginv12cb.grid(row=12, column=10)
hardinginv13cb = Checkbutton(solrvr, variable=hardinginv13cbval)
hardinginv13cb.grid(row=13, column=10)
hardinginv14cb = Checkbutton(solrvr, variable=hardinginv14cbval)
hardinginv14cb.grid(row=14, column=10)
hardinginv15cb = Checkbutton(solrvr, variable=hardinginv15cbval)
hardinginv15cb.grid(row=15, column=10)
hardinginv16cb = Checkbutton(solrvr, variable=hardinginv16cbval)
hardinginv16cb.grid(row=16, column=10)
hardinginv17cb = Checkbutton(solrvr, variable=hardinginv17cbval)
hardinginv17cb.grid(row=17, column=10)
hardinginv18cb = Checkbutton(solrvr, variable=hardinginv18cbval)
hardinginv18cb.grid(row=18, column=10)
hardinginv19cb = Checkbutton(solrvr, variable=hardinginv19cbval)
hardinginv19cb.grid(row=19, column=10)
hardinginv20cb = Checkbutton(solrvr, variable=hardinginv20cbval)
hardinginv20cb.grid(row=20, column=10)
hardinginv21cb = Checkbutton(solrvr, variable=hardinginv21cbval)
hardinginv21cb.grid(row=21, column=10)
hardinginv22cb = Checkbutton(solrvr, variable=hardinginv22cbval)
hardinginv22cb.grid(row=22, column=10)
hardinginv23cb = Checkbutton(solrvr, variable=hardinginv23cbval)
hardinginv23cb.grid(row=23, column=10)
hardinginv24cb = Checkbutton(solrvr, variable=hardinginv24cbval)
hardinginv24cb.grid(row=24, column=10)



harrison1Label= Label(narenco, text= "Harrison")
harrison1Label.grid(row=0, column=9, columnspan=2)

harrisoninv1Label= Label(narenco, text= "X")
harrisoninv1Label.grid(row= 1, column=9)

harrisoninv2Label = Label(narenco, text="X")
harrisoninv2Label.grid(row=2, column=9)

# Harrison Inv 3
harrisoninv3Label = Label(narenco, text="X")
harrisoninv3Label.grid(row=3, column=9)

# Harrison Inv 4
harrisoninv4Label = Label(narenco, text="X")
harrisoninv4Label.grid(row=4, column=9)

# Harrison Inv 5
harrisoninv5Label = Label(narenco, text="X")
harrisoninv5Label.grid(row=5, column=9)

# Harrison Inv 6
harrisoninv6Label = Label(narenco, text="X")
harrisoninv6Label.grid(row=6, column=9)

# Harrison Inv 7
harrisoninv7Label = Label(narenco, text="X")
harrisoninv7Label.grid(row=7, column=9)

# Harrison Inv 8
harrisoninv8Label = Label(narenco, text="X")
harrisoninv8Label.grid(row=8, column=9)

# Harrison Inv 9
harrisoninv9Label = Label(narenco, text="X")
harrisoninv9Label.grid(row=9, column=9)

# Harrison Inv 10
harrisoninv10Label = Label(narenco, text="X")
harrisoninv10Label.grid(row=10, column=9)

# Harrison Inv 11
harrisoninv11Label = Label(narenco, text="X")
harrisoninv11Label.grid(row=11, column=9)

# Harrison Inv 12
harrisoninv12Label = Label(narenco, text="X")
harrisoninv12Label.grid(row=12, column=9)

# Harrison Inv 13
harrisoninv13Label = Label(narenco, text="X")
harrisoninv13Label.grid(row=13, column=9)

# Harrison Inv 14
harrisoninv14Label = Label(narenco, text="X")
harrisoninv14Label.grid(row=14, column=9)

# Harrison Inv 15
harrisoninv15Label = Label(narenco, text="X")
harrisoninv15Label.grid(row=15, column=9)

# Harrison Inv 16
harrisoninv16Label = Label(narenco, text="X")
harrisoninv16Label.grid(row=16, column=9)

# Harrison Inv 17
harrisoninv17Label = Label(narenco, text="X")
harrisoninv17Label.grid(row=17, column=9)

# Harrison Inv 18
harrisoninv18Label = Label(narenco, text="X")
harrisoninv18Label.grid(row=18, column=9)

# Harrison Inv 19
harrisoninv19Label = Label(narenco, text="X")
harrisoninv19Label.grid(row=19, column=9)

# Harrison Inv 20
harrisoninv20Label = Label(narenco, text="X")
harrisoninv20Label.grid(row=20, column=9)

# Harrison Inv 21
harrisoninv21Label = Label(narenco, text="X")
harrisoninv21Label.grid(row=21, column=9)

# Harrison Inv 22
harrisoninv22Label = Label(narenco, text="X")
harrisoninv22Label.grid(row=22, column=9)

# Harrison Inv 23
harrisoninv23Label = Label(narenco, text="X")
harrisoninv23Label.grid(row=23, column=9)

# Harrison Inv 24
harrisoninv24Label = Label(narenco, text="X")
harrisoninv24Label.grid(row=24, column=9)

# Harrison Inv 25
harrisoninv25Label = Label(narenco, text="X")
harrisoninv25Label.grid(row=25, column=9)

# Harrison Inv 26
harrisoninv26Label = Label(narenco, text="X")
harrisoninv26Label.grid(row=26, column=9)

# Harrison Inv 27
harrisoninv27Label = Label(narenco, text="X")
harrisoninv27Label.grid(row=27, column=9)

# Harrison Inv 28
harrisoninv28Label = Label(narenco, text="X")
harrisoninv28Label.grid(row=28, column=9)

# Harrison Inv 29
harrisoninv29Label = Label(narenco, text="X")
harrisoninv29Label.grid(row=29, column=9)

# Harrison Inv 30
harrisoninv30Label = Label(narenco, text="X")
harrisoninv30Label.grid(row=30, column=9)

# Harrison Inv 31
harrisoninv31Label = Label(narenco, text="X")
harrisoninv31Label.grid(row=31, column=9)

# Harrison Inv 32
harrisoninv32Label = Label(narenco, text="X")
harrisoninv32Label.grid(row=32, column=9)

# Harrison Inv 33
harrisoninv33Label = Label(narenco, text="X")
harrisoninv33Label.grid(row=33, column=9)

# Harrison Inv 34
harrisoninv34Label = Label(narenco, text="X")
harrisoninv34Label.grid(row=34, column=9)

# Harrison Inv 35
harrisoninv35Label = Label(narenco, text="X")
harrisoninv35Label.grid(row=35, column=9)

# Harrison Inv 36
harrisoninv36Label = Label(narenco, text="X")
harrisoninv36Label.grid(row=36, column=9)

# Harrison Inv 37
harrisoninv37Label = Label(narenco, text="X")
harrisoninv37Label.grid(row=37, column=9)

# Harrison Inv 38
harrisoninv38Label = Label(narenco, text="X")
harrisoninv38Label.grid(row=38, column=9)

# Harrison Inv 39
harrisoninv39Label = Label(narenco, text="X")
harrisoninv39Label.grid(row=39, column=9)

# Harrison Inv 40
harrisoninv40Label = Label(narenco, text="X")
harrisoninv40Label.grid(row=40, column=9)

# Harrison Inv 41
harrisoninv41Label = Label(narenco, text="X")
harrisoninv41Label.grid(row=41, column=9)

# Harrison Inv 42
harrisoninv42Label = Label(narenco, text="X")
harrisoninv42Label.grid(row=42, column=9)

# Harrison Inv 43
harrisoninv43Label = Label(narenco, text="X")
harrisoninv43Label.grid(row=43, column=9)


harrisoninv1cb = Checkbutton(narenco, variable=harrisoninv1cbval)
harrisoninv1cb.grid(row=1, column=10)
harrisoninv2cb = Checkbutton(narenco, variable=harrisoninv2cbval)
harrisoninv2cb.grid(row=2, column=10)
harrisoninv3cb = Checkbutton(narenco, variable=harrisoninv3cbval)
harrisoninv3cb.grid(row=3, column=10)
harrisoninv4cb = Checkbutton(narenco, variable=harrisoninv4cbval)
harrisoninv4cb.grid(row=4, column=10)
harrisoninv5cb = Checkbutton(narenco, variable=harrisoninv5cbval)
harrisoninv5cb.grid(row=5, column=10)
harrisoninv6cb = Checkbutton(narenco, variable=harrisoninv6cbval)
harrisoninv6cb.grid(row=6, column=10)
harrisoninv7cb = Checkbutton(narenco, variable=harrisoninv7cbval)
harrisoninv7cb.grid(row=7, column=10)
harrisoninv8cb = Checkbutton(narenco, variable=harrisoninv8cbval)
harrisoninv8cb.grid(row=8, column=10)
harrisoninv9cb = Checkbutton(narenco, variable=harrisoninv9cbval)
harrisoninv9cb.grid(row=9, column=10)
harrisoninv10cb = Checkbutton(narenco, variable=harrisoninv10cbval)
harrisoninv10cb.grid(row=10, column=10)
harrisoninv11cb = Checkbutton(narenco, variable=harrisoninv11cbval)
harrisoninv11cb.grid(row=11, column=10)
harrisoninv12cb = Checkbutton(narenco, variable=harrisoninv12cbval)
harrisoninv12cb.grid(row=12, column=10)
harrisoninv13cb = Checkbutton(narenco, variable=harrisoninv13cbval)
harrisoninv13cb.grid(row=13, column=10)
harrisoninv14cb = Checkbutton(narenco, variable=harrisoninv14cbval)
harrisoninv14cb.grid(row=14, column=10)
harrisoninv15cb = Checkbutton(narenco, variable=harrisoninv15cbval)
harrisoninv15cb.grid(row=15, column=10)
harrisoninv16cb = Checkbutton(narenco, variable=harrisoninv16cbval)
harrisoninv16cb.grid(row=16, column=10)
harrisoninv17cb = Checkbutton(narenco, variable=harrisoninv17cbval)
harrisoninv17cb.grid(row=17, column=10)
harrisoninv18cb = Checkbutton(narenco, variable=harrisoninv18cbval)
harrisoninv18cb.grid(row=18, column=10)
harrisoninv19cb = Checkbutton(narenco, variable=harrisoninv19cbval)
harrisoninv19cb.grid(row=19, column=10)
harrisoninv20cb = Checkbutton(narenco, variable=harrisoninv20cbval)
harrisoninv20cb.grid(row=20, column=10)
harrisoninv21cb = Checkbutton(narenco, variable=harrisoninv21cbval)
harrisoninv21cb.grid(row=21, column=10)
harrisoninv22cb = Checkbutton(narenco, variable=harrisoninv22cbval)
harrisoninv22cb.grid(row=22, column=10)
harrisoninv23cb = Checkbutton(narenco, variable=harrisoninv23cbval)
harrisoninv23cb.grid(row=23, column=10)
harrisoninv24cb = Checkbutton(narenco, variable=harrisoninv24cbval)
harrisoninv24cb.grid(row=24, column=10)
harrisoninv25cb = Checkbutton(narenco, variable=harrisoninv25cbval)
harrisoninv25cb.grid(row=25, column=10)
harrisoninv26cb = Checkbutton(narenco, variable=harrisoninv26cbval)
harrisoninv26cb.grid(row=26, column=10)
harrisoninv27cb = Checkbutton(narenco, variable=harrisoninv27cbval)
harrisoninv27cb.grid(row=27, column=10)
harrisoninv28cb = Checkbutton(narenco, variable=harrisoninv28cbval)
harrisoninv28cb.grid(row=28, column=10)
harrisoninv29cb = Checkbutton(narenco, variable=harrisoninv29cbval)
harrisoninv29cb.grid(row=29, column=10)
harrisoninv30cb = Checkbutton(narenco, variable=harrisoninv30cbval)
harrisoninv30cb.grid(row=30, column=10)
harrisoninv31cb = Checkbutton(narenco, variable=harrisoninv31cbval)
harrisoninv31cb.grid(row=31, column=10)
harrisoninv32cb = Checkbutton(narenco, variable=harrisoninv32cbval)
harrisoninv32cb.grid(row=32, column=10)
harrisoninv33cb = Checkbutton(narenco, variable=harrisoninv33cbval)
harrisoninv33cb.grid(row=33, column=10)
harrisoninv34cb = Checkbutton(narenco, variable=harrisoninv34cbval)
harrisoninv34cb.grid(row=34, column=10)
harrisoninv35cb = Checkbutton(narenco, variable=harrisoninv35cbval)
harrisoninv35cb.grid(row=35, column=10)
harrisoninv36cb = Checkbutton(narenco, variable=harrisoninv36cbval)
harrisoninv36cb.grid(row=36, column=10)
harrisoninv37cb = Checkbutton(narenco, variable=harrisoninv37cbval)
harrisoninv37cb.grid(row=37, column=10)
harrisoninv38cb = Checkbutton(narenco, variable=harrisoninv38cbval)
harrisoninv38cb.grid(row=38, column=10)
harrisoninv39cb = Checkbutton(narenco, variable=harrisoninv39cbval)
harrisoninv39cb.grid(row=39, column=10)
harrisoninv40cb = Checkbutton(narenco, variable=harrisoninv40cbval)
harrisoninv40cb.grid(row=40, column=10)
harrisoninv41cb = Checkbutton(narenco, variable=harrisoninv41cbval)
harrisoninv41cb.grid(row=41, column=10)
harrisoninv42cb = Checkbutton(narenco, variable=harrisoninv42cbval)
harrisoninv42cb.grid(row=42, column=10)
harrisoninv43cb = Checkbutton(narenco, variable=harrisoninv43cbval)
harrisoninv43cb.grid(row=43, column=10)



hayes1Label= Label(narenco, text= "Hayes")
hayes1Label.grid(row=0, column=11, columnspan=2)

hayesinv1Label= Label(narenco, text= "X")
hayesinv1Label.grid(row=1, column=11)

hayesinv2Label = Label(narenco, text="X")
hayesinv2Label.grid(row=2, column=11)

# Hayes Inv 3
hayesinv3Label = Label(narenco, text="X")
hayesinv3Label.grid(row=3, column=11)

# Hayes Inv 4
hayesinv4Label = Label(narenco, text="X")
hayesinv4Label.grid(row=4, column=11)

# Hayes Inv 5
hayesinv5Label = Label(narenco, text="X")
hayesinv5Label.grid(row=5, column=11)

# Hayes Inv 6
hayesinv6Label = Label(narenco, text="X")
hayesinv6Label.grid(row=6, column=11)

# Hayes Inv 7
hayesinv7Label = Label(narenco, text="X")
hayesinv7Label.grid(row=7, column=11)

# Hayes Inv 8
hayesinv8Label = Label(narenco, text="X")
hayesinv8Label.grid(row=8, column=11)

# Hayes Inv 9
hayesinv9Label = Label(narenco, text="X")
hayesinv9Label.grid(row=9, column=11)

# Hayes Inv 10
hayesinv10Label = Label(narenco, text="X")
hayesinv10Label.grid(row=10, column=11)

# Hayes Inv 11
hayesinv11Label = Label(narenco, text="X")
hayesinv11Label.grid(row=11, column=11)

# Hayes Inv 12
hayesinv12Label = Label(narenco, text="X")
hayesinv12Label.grid(row=12, column=11)

# Hayes Inv 13
hayesinv13Label = Label(narenco, text="X")
hayesinv13Label.grid(row=13, column=11)

# Hayes Inv 14
hayesinv14Label = Label(narenco, text="X")
hayesinv14Label.grid(row=14, column=11)

# Hayes Inv 15
hayesinv15Label = Label(narenco, text="X")
hayesinv15Label.grid(row=15, column=11)

# Hayes Inv 16
hayesinv16Label = Label(narenco, text="X")
hayesinv16Label.grid(row=16, column=11)

# Hayes Inv 17
hayesinv17Label = Label(narenco, text="X")
hayesinv17Label.grid(row=17, column=11)

# Hayes Inv 18
hayesinv18Label = Label(narenco, text="X")
hayesinv18Label.grid(row=18, column=11)

# Hayes Inv 19
hayesinv19Label = Label(narenco, text="X")
hayesinv19Label.grid(row=19, column=11)

# Hayes Inv 20
hayesinv20Label = Label(narenco, text="X")
hayesinv20Label.grid(row=20, column=11)

# Hayes Inv 21
hayesinv21Label = Label(narenco, text="X")
hayesinv21Label.grid(row=21, column=11)

# Hayes Inv 22
hayesinv22Label = Label(narenco, text="X")
hayesinv22Label.grid(row=22, column=11)

hayesinv23Label = Label(narenco, text="X")
hayesinv23Label.grid(row=23, column=11)

# Hayes Inv 24
hayesinv24Label = Label(narenco, text="X")
hayesinv24Label.grid(row=24, column=11)

# Hayes Inv 25
hayesinv25Label = Label(narenco, text="X")
hayesinv25Label.grid(row=25, column=11)

# Hayes Inv 26
hayesinv26Label = Label(narenco, text="X")
hayesinv26Label.grid(row=26, column=11)


hayesinv1cb = Checkbutton(narenco, variable=hayesinv1cbval)
hayesinv1cb.grid(row=1, column=12)
hayesinv2cb = Checkbutton(narenco, variable=hayesinv2cbval)
hayesinv2cb.grid(row=2, column=12)
hayesinv3cb = Checkbutton(narenco, variable=hayesinv3cbval)
hayesinv3cb.grid(row=3, column=12)
hayesinv4cb = Checkbutton(narenco, variable=hayesinv4cbval)
hayesinv4cb.grid(row=4, column=12)
hayesinv5cb = Checkbutton(narenco, variable=hayesinv5cbval)
hayesinv5cb.grid(row=5, column=12)
hayesinv6cb = Checkbutton(narenco, variable=hayesinv6cbval)
hayesinv6cb.grid(row=6, column=12)
hayesinv7cb = Checkbutton(narenco, variable=hayesinv7cbval)
hayesinv7cb.grid(row=7, column=12)
hayesinv8cb = Checkbutton(narenco, variable=hayesinv8cbval)
hayesinv8cb.grid(row=8, column=12)
hayesinv9cb = Checkbutton(narenco, variable=hayesinv9cbval)
hayesinv9cb.grid(row=9, column=12)
hayesinv10cb = Checkbutton(narenco, variable=hayesinv10cbval)
hayesinv10cb.grid(row=10, column=12)
hayesinv11cb = Checkbutton(narenco, variable=hayesinv11cbval)
hayesinv11cb.grid(row=11, column=12)
hayesinv12cb = Checkbutton(narenco, variable=hayesinv12cbval)
hayesinv12cb.grid(row=12, column=12)
hayesinv13cb = Checkbutton(narenco, variable=hayesinv13cbval)
hayesinv13cb.grid(row=13, column=12)
hayesinv14cb = Checkbutton(narenco, variable=hayesinv14cbval)
hayesinv14cb.grid(row=14, column=12)
hayesinv15cb = Checkbutton(narenco, variable=hayesinv15cbval)
hayesinv15cb.grid(row=15, column=12)
hayesinv16cb = Checkbutton(narenco, variable=hayesinv16cbval)
hayesinv16cb.grid(row=16, column=12)
hayesinv17cb = Checkbutton(narenco, variable=hayesinv17cbval)
hayesinv17cb.grid(row=17, column=12)
hayesinv18cb = Checkbutton(narenco, variable=hayesinv18cbval)
hayesinv18cb.grid(row=18, column=12)
hayesinv19cb = Checkbutton(narenco, variable=hayesinv19cbval)
hayesinv19cb.grid(row=19, column=12)
hayesinv20cb = Checkbutton(narenco, variable=hayesinv20cbval)
hayesinv20cb.grid(row=20, column=12)
hayesinv21cb = Checkbutton(narenco, variable=hayesinv21cbval)
hayesinv21cb.grid(row=21, column=12)
hayesinv22cb = Checkbutton(narenco, variable=hayesinv22cbval)
hayesinv22cb.grid(row=22, column=12)
hayesinv23cb = Checkbutton(narenco, variable=hayesinv23cbval)
hayesinv23cb.grid(row=23, column=12)
hayesinv24cb = Checkbutton(narenco, variable=hayesinv24cbval)
hayesinv24cb.grid(row=24, column=12)
hayesinv25cb = Checkbutton(narenco, variable=hayesinv25cbval)
hayesinv25cb.grid(row=25, column=12)
hayesinv26cb = Checkbutton(narenco, variable=hayesinv26cbval)
hayesinv26cb.grid(row=26, column=12)


hickory1Label= Label(narenco, text= "Hickory")
hickory1Label.grid(row=0, column=13, columnspan=2)
hickoryinv1Label= Label(narenco, text= "X")
hickoryinv1Label.grid(row=1, column=13)
hickoryinv2Label= Label(narenco, text= "X")
hickoryinv2Label.grid(row=2, column=13)

hickoryinv1cb = Checkbutton(narenco, variable=hickoryinv1cbval)
hickoryinv1cb.grid(row=1, column=14)
hickoryinv2cb = Checkbutton(narenco, variable=hickoryinv2cbval)
hickoryinv2cb.grid(row=2, column=14)


hickson1Label= Label(inv, text= "Hickson")
hickson1Label.grid(row=0, column=3, columnspan=2)
hicksoninv1Label= Label(inv, text= "X")
hicksoninv1Label.grid(row= 1, column=3)
# Hickson Inv 2
hicksoninv2Label = Label(inv, text="X")
hicksoninv2Label.grid(row=2, column=3)

# Hickson Inv 3
hicksoninv3Label = Label(inv, text="X")
hicksoninv3Label.grid(row=3, column=3)

# Hickson Inv 4
hicksoninv4Label = Label(inv, text="X")
hicksoninv4Label.grid(row=4, column=3)

# Hickson Inv 5
hicksoninv5Label = Label(inv, text="X")
hicksoninv5Label.grid(row=5, column=3)

# Hickson Inv 6
hicksoninv6Label = Label(inv, text="X")
hicksoninv6Label.grid(row=6, column=3)

# Hickson Inv 7
hicksoninv7Label = Label(inv, text="X")
hicksoninv7Label.grid(row=7, column=3)

# Hickson Inv 8
hicksoninv8Label = Label(inv, text="X")
hicksoninv8Label.grid(row=8, column=3)

# Hickson Inv 9
hicksoninv9Label = Label(inv, text="X")
hicksoninv9Label.grid(row=9, column=3)

# Hickson Inv 10
hicksoninv10Label = Label(inv, text="X")
hicksoninv10Label.grid(row=10, column=3)

# Hickson Inv 11
hicksoninv11Label = Label(inv, text="X")
hicksoninv11Label.grid(row=11, column=3)

# Hickson Inv 12
hicksoninv12Label = Label(inv, text="X")
hicksoninv12Label.grid(row=12, column=3)
# Hickson Inv 13
hicksoninv13Label = Label(inv, text="X")
hicksoninv13Label.grid(row=13, column=3)

# Hickson Inv 14
hicksoninv14Label = Label(inv, text="X")
hicksoninv14Label.grid(row=14, column=3)

# Hickson Inv 15
hicksoninv15Label = Label(inv, text="X")
hicksoninv15Label.grid(row=15, column=3)

# Hickson Inv 16
hicksoninv16Label = Label(inv, text="X")
hicksoninv16Label.grid(row=16, column=3)



hicksoninv1cb = Checkbutton(inv, variable=hicksoninv1cbval)
hicksoninv1cb.grid(row=1, column=4)
hicksoninv2cb = Checkbutton(inv, variable=hicksoninv2cbval)
hicksoninv2cb.grid(row=2, column=4)
hicksoninv3cb = Checkbutton(inv, variable=hicksoninv3cbval)
hicksoninv3cb.grid(row=3, column=4)
hicksoninv4cb = Checkbutton(inv, variable=hicksoninv4cbval)
hicksoninv4cb.grid(row=4, column=4)
hicksoninv5cb = Checkbutton(inv, variable=hicksoninv5cbval)
hicksoninv5cb.grid(row=5, column=4)
hicksoninv6cb = Checkbutton(inv, variable=hicksoninv6cbval)
hicksoninv6cb.grid(row=6, column=4)
hicksoninv7cb = Checkbutton(inv, variable=hicksoninv7cbval)
hicksoninv7cb.grid(row=7, column=4)
hicksoninv8cb = Checkbutton(inv, variable=hicksoninv8cbval)
hicksoninv8cb.grid(row=8, column=4)
hicksoninv9cb = Checkbutton(inv, variable=hicksoninv9cbval)
hicksoninv9cb.grid(row=9, column=4)
hicksoninv10cb = Checkbutton(inv, variable=hicksoninv10cbval)
hicksoninv10cb.grid(row=10, column=4)
hicksoninv11cb = Checkbutton(inv, variable=hicksoninv11cbval)
hicksoninv11cb.grid(row=11, column=4)
hicksoninv12cb = Checkbutton(inv, variable=hicksoninv12cbval)
hicksoninv12cb.grid(row=12, column=4)
hicksoninv13cb = Checkbutton(inv, variable=hicksoninv13cbval)
hicksoninv13cb.grid(row=13, column=4)
hicksoninv14cb = Checkbutton(inv, variable=hicksoninv14cbval)
hicksoninv14cb.grid(row=14, column=4)
hicksoninv15cb = Checkbutton(inv, variable=hicksoninv15cbval)
hicksoninv15cb.grid(row=15, column=4)
hicksoninv16cb = Checkbutton(inv, variable=hicksoninv16cbval)
hicksoninv16cb.grid(row=16, column=4)



hollyswamp1Label= Label(ncemc, text= "Holly Swamp")
hollyswamp1Label.grid(row=0, column=3, columnspan=2)

hollyswampinv1Label= Label(ncemc, text= "X")
hollyswampinv1Label.grid(row=1, column=3)

hollyswampinv2Label = Label(ncemc, text="X")
hollyswampinv2Label.grid(row=2, column=3)

# Hollyswamp Inv 3
hollyswampinv3Label = Label(ncemc, text="X")
hollyswampinv3Label.grid(row=3, column=3)

# Hollyswamp Inv 4
hollyswampinv4Label = Label(ncemc, text="X")
hollyswampinv4Label.grid(row=4, column=3)

# Hollyswamp Inv 5
hollyswampinv5Label = Label(ncemc, text="X")
hollyswampinv5Label.grid(row=5, column=3)

# Hollyswamp Inv 6
hollyswampinv6Label = Label(ncemc, text="X")
hollyswampinv6Label.grid(row=6, column=3)

# Hollyswamp Inv 7
hollyswampinv7Label = Label(ncemc, text="X")
hollyswampinv7Label.grid(row=7, column=3)

# Hollyswamp Inv 8
hollyswampinv8Label = Label(ncemc, text="X")
hollyswampinv8Label.grid(row=8, column=3)

# Hollyswamp Inv 9
hollyswampinv9Label = Label(ncemc, text="X")
hollyswampinv9Label.grid(row=9, column=3)

# Hollyswamp Inv 10
hollyswampinv10Label = Label(ncemc, text="X")
hollyswampinv10Label.grid(row=10, column=3)

# Hollyswamp Inv 11
hollyswampinv11Label = Label(ncemc, text="X")
hollyswampinv11Label.grid(row=11, column=3)

# Hollyswamp Inv 12
hollyswampinv12Label = Label(ncemc, text="X")
hollyswampinv12Label.grid(row=12, column=3)

hollyswampinv13Label = Label(ncemc, text="X")
hollyswampinv13Label.grid(row=13, column=3)

# Hollyswamp Inv 14
hollyswampinv14Label = Label(ncemc, text="X")
hollyswampinv14Label.grid(row=14, column=3)

# Hollyswamp Inv 15
hollyswampinv15Label = Label(ncemc, text="X")
hollyswampinv15Label.grid(row=15, column=3)

# Hollyswamp Inv 16
hollyswampinv16Label = Label(ncemc, text="X")
hollyswampinv16Label.grid(row=16, column=3)

hollyswampinv1cb = Checkbutton(ncemc, variable=hollyswampinv1cbval)
hollyswampinv1cb.grid(row=1, column=4)
hollyswampinv2cb = Checkbutton(ncemc, variable=hollyswampinv2cbval)
hollyswampinv2cb.grid(row=2, column=4)
hollyswampinv3cb = Checkbutton(ncemc, variable=hollyswampinv3cbval)
hollyswampinv3cb.grid(row=3, column=4)
hollyswampinv4cb = Checkbutton(ncemc, variable=hollyswampinv4cbval)
hollyswampinv4cb.grid(row=4, column=4)
hollyswampinv5cb = Checkbutton(ncemc, variable=hollyswampinv5cbval)
hollyswampinv5cb.grid(row=5, column=4)
hollyswampinv6cb = Checkbutton(ncemc, variable=hollyswampinv6cbval)
hollyswampinv6cb.grid(row=6, column=4)
hollyswampinv7cb = Checkbutton(ncemc, variable=hollyswampinv7cbval)
hollyswampinv7cb.grid(row=7, column=4)
hollyswampinv8cb = Checkbutton(ncemc, variable=hollyswampinv8cbval)
hollyswampinv8cb.grid(row=8, column=4)
hollyswampinv9cb = Checkbutton(ncemc, variable=hollyswampinv9cbval)
hollyswampinv9cb.grid(row=9, column=4)
hollyswampinv10cb = Checkbutton(ncemc, variable=hollyswampinv10cbval)
hollyswampinv10cb.grid(row=10, column=4)
hollyswampinv11cb = Checkbutton(ncemc, variable=hollyswampinv11cbval)
hollyswampinv11cb.grid(row=11, column=4)
hollyswampinv12cb = Checkbutton(ncemc, variable=hollyswampinv12cbval)
hollyswampinv12cb.grid(row=12, column=4)
hollyswampinv13cb = Checkbutton(ncemc, variable=hollyswampinv13cbval)
hollyswampinv13cb.grid(row=13, column=4)
hollyswampinv14cb = Checkbutton(ncemc, variable=hollyswampinv14cbval)
hollyswampinv14cb.grid(row=14, column=4)
hollyswampinv15cb = Checkbutton(ncemc, variable=hollyswampinv15cbval)
hollyswampinv15cb.grid(row=15, column=4)
hollyswampinv16cb = Checkbutton(ncemc, variable=hollyswampinv16cbval)
hollyswampinv16cb.grid(row=16, column=4)



jefferson1Label= Label(inv, text= "Jefferson")
jefferson1Label.grid(row=0, column=5, columnspan=2)

jeffersoninv1Label= Label(inv, text= "X")
jeffersoninv1Label.grid(row=1, column=5)

jeffersoninv2Label= Label(inv, text= "X")
jeffersoninv2Label.grid(row=2, column=5)

# Jefferson Inv 3
jeffersoninv3Label = Label(inv, text="X")
jeffersoninv3Label.grid(row=3, column=5)

# Jefferson Inv 4
jeffersoninv4Label = Label(inv, text="X")
jeffersoninv4Label.grid(row=4, column=5)

# Jefferson Inv 5
jeffersoninv5Label = Label(inv, text="X")
jeffersoninv5Label.grid(row=5, column=5)

# Jefferson Inv 6
jeffersoninv6Label = Label(inv, text="X")
jeffersoninv6Label.grid(row=6, column=5)

# Jefferson Inv 7
jeffersoninv7Label = Label(inv, text="X")
jeffersoninv7Label.grid(row=7, column=5)

# Jefferson Inv 8
jeffersoninv8Label = Label(inv, text="X")
jeffersoninv8Label.grid(row=8, column=5)

# Jefferson Inv 9
jeffersoninv9Label = Label(inv, text="X")
jeffersoninv9Label.grid(row=9, column=5)

# Jefferson Inv 10
jeffersoninv10Label = Label(inv, text="X")
jeffersoninv10Label.grid(row=10, column=5)

# Jefferson Inv 11
jeffersoninv11Label = Label(inv, text="X")
jeffersoninv11Label.grid(row=11, column=5)

# Jefferson Inv 12
jeffersoninv12Label = Label(inv, text="X")
jeffersoninv12Label.grid(row=12, column=5)

# Jefferson Inv 13
jeffersoninv13Label = Label(inv, text="X")
jeffersoninv13Label.grid(row=13, column=5)

# Jefferson Inv 14
jeffersoninv14Label = Label(inv, text="X")
jeffersoninv14Label.grid(row=14, column=5)

# Jefferson Inv 15
jeffersoninv15Label = Label(inv, text="X")
jeffersoninv15Label.grid(row=15, column=5)

# Jefferson Inv 16
jeffersoninv16Label = Label(inv, text="X")
jeffersoninv16Label.grid(row=16, column=5)

jeffersoninv17Label = Label(inv, text="X")
jeffersoninv17Label.grid(row=17, column=5)

# Jefferson Inv 18
jeffersoninv18Label = Label(inv, text="X")
jeffersoninv18Label.grid(row=18, column=5)

# Jefferson Inv 19
jeffersoninv19Label = Label(inv, text="X")
jeffersoninv19Label.grid(row=19, column=5)

# Jefferson Inv 20
jeffersoninv20Label = Label(inv, text="X")
jeffersoninv20Label.grid(row=20, column=5)

# Jefferson Inv 21
jeffersoninv21Label = Label(inv, text="X")
jeffersoninv21Label.grid(row=21, column=5)

# Jefferson Inv 22
jeffersoninv22Label = Label(inv, text="X")
jeffersoninv22Label.grid(row=22, column=5)

# Jefferson Inv 23
jeffersoninv23Label = Label(inv, text="X")
jeffersoninv23Label.grid(row=23, column=5)

# Jefferson Inv 24
jeffersoninv24Label = Label(inv, text="X")
jeffersoninv24Label.grid(row=24, column=5)

# Jefferson Inv 25
jeffersoninv25Label = Label(inv, text="X")
jeffersoninv25Label.grid(row=25, column=5)

# Jefferson Inv 26
jeffersoninv26Label = Label(inv, text="X")
jeffersoninv26Label.grid(row=26, column=5)

# Jefferson Inv 27
jeffersoninv27Label = Label(inv, text="X")
jeffersoninv27Label.grid(row=27, column=5)

# Jefferson Inv 28
jeffersoninv28Label = Label(inv, text="X")
jeffersoninv28Label.grid(row=28, column=5)

# Jefferson Inv 29
jeffersoninv29Label = Label(inv, text="X")
jeffersoninv29Label.grid(row=29, column=5)

# Jefferson Inv 30
jeffersoninv30Label = Label(inv, text="X")
jeffersoninv30Label.grid(row=30, column=5)

# Jefferson Inv 31
jeffersoninv31Label = Label(inv, text="X")
jeffersoninv31Label.grid(row=31, column=5)

# Jefferson Inv 32
jeffersoninv32Label = Label(inv, text="X")
jeffersoninv32Label.grid(row=32, column=5)

# Jefferson Inv 33
jeffersoninv33Label = Label(inv, text="X")
jeffersoninv33Label.grid(row=33, column=5)

# Jefferson Inv 34
jeffersoninv34Label = Label(inv, text="X")
jeffersoninv34Label.grid(row=34, column=5)

# Jefferson Inv 35
jeffersoninv35Label = Label(inv, text="X")
jeffersoninv35Label.grid(row=35, column=5)

# Jefferson Inv 36
jeffersoninv36Label = Label(inv, text="X")
jeffersoninv36Label.grid(row=36, column=5)

# Jefferson Inv 37
jeffersoninv37Label = Label(inv, text="X")
jeffersoninv37Label.grid(row=37, column=5)

# Jefferson Inv 38
jeffersoninv38Label = Label(inv, text="X")
jeffersoninv38Label.grid(row=38, column=5)

# Jefferson Inv 39
jeffersoninv39Label = Label(inv, text="X")
jeffersoninv39Label.grid(row=39, column=5)

# Jefferson Inv 40
jeffersoninv40Label = Label(inv, text="X")
jeffersoninv40Label.grid(row=40, column=5)

# Jefferson Inv 41
jeffersoninv41Label = Label(inv, text="X")
jeffersoninv41Label.grid(row=41, column=5)

# Jefferson Inv 42
jeffersoninv42Label = Label(inv, text="X")
jeffersoninv42Label.grid(row=42, column=5)

# Jefferson Inv 43
jeffersoninv43Label = Label(inv, text="X")
jeffersoninv43Label.grid(row=43, column=5)

# Jefferson Inv 44
jeffersoninv44Label = Label(inv, text="X")
jeffersoninv44Label.grid(row=44, column=5)

# Jefferson Inv 45
jeffersoninv45Label = Label(inv, text="X")
jeffersoninv45Label.grid(row=45, column=5)

# Jefferson Inv 46
jeffersoninv46Label = Label(inv, text="X")
jeffersoninv46Label.grid(row=46, column=5)

# Jefferson Inv 47
jeffersoninv47Label = Label(inv, text="X")
jeffersoninv47Label.grid(row=47, column=5)

# Jefferson Inv 48
jeffersoninv48Label = Label(inv, text="X")
jeffersoninv48Label.grid(row=48, column=5)

# Jefferson Inv 49
jeffersoninv49Label = Label(inv, text="X")
jeffersoninv49Label.grid(row=49, column=5)

# Jefferson Inv 50
jeffersoninv50Label = Label(inv, text="X")
jeffersoninv50Label.grid(row=50, column=5)

# Jefferson Inv 51
jeffersoninv51Label = Label(inv, text="X")
jeffersoninv51Label.grid(row=51, column=5)

# Jefferson Inv 52
jeffersoninv52Label = Label(inv, text="X")
jeffersoninv52Label.grid(row=52, column=5)

# Jefferson Inv 53
jeffersoninv53Label = Label(inv, text="X")
jeffersoninv53Label.grid(row=53, column=5)

# Jefferson Inv 54
jeffersoninv54Label = Label(inv, text="X")
jeffersoninv54Label.grid(row=54, column=5)

# Jefferson Inv 55
jeffersoninv55Label = Label(inv, text="X")
jeffersoninv55Label.grid(row=55, column=5)

# Jefferson Inv 56
jeffersoninv56Label = Label(inv, text="X")
jeffersoninv56Label.grid(row=56, column=5)

# Jefferson Inv 57
jeffersoninv57Label = Label(inv, text="X")
jeffersoninv57Label.grid(row=57, column=5)

# Jefferson Inv 58
jeffersoninv58Label = Label(inv, text="X")
jeffersoninv58Label.grid(row=58, column=5)

# Jefferson Inv 59
jeffersoninv59Label = Label(inv, text="X")
jeffersoninv59Label.grid(row=59, column=5)

# Jefferson Inv 60
jeffersoninv60Label = Label(inv, text="X")
jeffersoninv60Label.grid(row=60, column=5)

# Jefferson Inv 61
jeffersoninv61Label = Label(inv, text="X")
jeffersoninv61Label.grid(row=61, column=5)

# Jefferson Inv 62
jeffersoninv62Label = Label(inv, text="X")
jeffersoninv62Label.grid(row=62, column=5)

# Jefferson Inv 63
jeffersoninv63Label = Label(inv, text="X")
jeffersoninv63Label.grid(row=63, column=5)

# Jefferson Inv 64
jeffersoninv64Label = Label(inv, text="X")
jeffersoninv64Label.grid(row=64, column=5)

jeffersoninv1cb = Checkbutton(inv, variable=jeffersoninv1cbval)
jeffersoninv1cb.grid(row=1, column=6)
jeffersoninv2cb = Checkbutton(inv, variable=jeffersoninv2cbval)
jeffersoninv2cb.grid(row=2, column=6)
jeffersoninv3cb = Checkbutton(inv, variable=jeffersoninv3cbval)
jeffersoninv3cb.grid(row=3, column=6)
jeffersoninv4cb = Checkbutton(inv, variable=jeffersoninv4cbval)
jeffersoninv4cb.grid(row=4, column=6)
jeffersoninv5cb = Checkbutton(inv, variable=jeffersoninv5cbval)
jeffersoninv5cb.grid(row=5, column=6)
jeffersoninv6cb = Checkbutton(inv, variable=jeffersoninv6cbval)
jeffersoninv6cb.grid(row=6, column=6)
jeffersoninv7cb = Checkbutton(inv, variable=jeffersoninv7cbval)
jeffersoninv7cb.grid(row=7, column=6)
jeffersoninv8cb = Checkbutton(inv, variable=jeffersoninv8cbval)
jeffersoninv8cb.grid(row=8, column=6)
jeffersoninv9cb = Checkbutton(inv, variable=jeffersoninv9cbval)
jeffersoninv9cb.grid(row=9, column=6)
jeffersoninv10cb = Checkbutton(inv, variable=jeffersoninv10cbval)
jeffersoninv10cb.grid(row=10, column=6)
jeffersoninv11cb = Checkbutton(inv, variable=jeffersoninv11cbval)
jeffersoninv11cb.grid(row=11, column=6)
jeffersoninv12cb = Checkbutton(inv, variable=jeffersoninv12cbval)
jeffersoninv12cb.grid(row=12, column=6)
jeffersoninv13cb = Checkbutton(inv, variable=jeffersoninv13cbval)
jeffersoninv13cb.grid(row=13, column=6)
jeffersoninv14cb = Checkbutton(inv, variable=jeffersoninv14cbval)
jeffersoninv14cb.grid(row=14, column=6)
jeffersoninv15cb = Checkbutton(inv, variable=jeffersoninv15cbval)
jeffersoninv15cb.grid(row=15, column=6)
jeffersoninv16cb = Checkbutton(inv, variable=jeffersoninv16cbval)
jeffersoninv16cb.grid(row=16, column=6)
jeffersoninv17cb = Checkbutton(inv, variable=jeffersoninv17cbval)
jeffersoninv17cb.grid(row=17, column=6)
jeffersoninv18cb = Checkbutton(inv, variable=jeffersoninv18cbval)
jeffersoninv18cb.grid(row=18, column=6)
jeffersoninv19cb = Checkbutton(inv, variable=jeffersoninv19cbval)
jeffersoninv19cb.grid(row=19, column=6)
jeffersoninv20cb = Checkbutton(inv, variable=jeffersoninv20cbval)
jeffersoninv20cb.grid(row=20, column=6)
jeffersoninv21cb = Checkbutton(inv, variable=jeffersoninv21cbval)
jeffersoninv21cb.grid(row=21, column=6)
jeffersoninv22cb = Checkbutton(inv, variable=jeffersoninv22cbval)
jeffersoninv22cb.grid(row=22, column=6)
jeffersoninv23cb = Checkbutton(inv, variable=jeffersoninv23cbval)
jeffersoninv23cb.grid(row=23, column=6)
jeffersoninv24cb = Checkbutton(inv, variable=jeffersoninv24cbval)
jeffersoninv24cb.grid(row=24, column=6)
jeffersoninv25cb = Checkbutton(inv, variable=jeffersoninv25cbval)
jeffersoninv25cb.grid(row=25, column=6)
jeffersoninv26cb = Checkbutton(inv, variable=jeffersoninv26cbval)
jeffersoninv26cb.grid(row=26, column=6)
jeffersoninv27cb = Checkbutton(inv, variable=jeffersoninv27cbval)
jeffersoninv27cb.grid(row=27, column=6)
jeffersoninv28cb = Checkbutton(inv, variable=jeffersoninv28cbval)
jeffersoninv28cb.grid(row=28, column=6)
jeffersoninv29cb = Checkbutton(inv, variable=jeffersoninv29cbval)
jeffersoninv29cb.grid(row=29, column=6)
jeffersoninv30cb = Checkbutton(inv, variable=jeffersoninv30cbval)
jeffersoninv30cb.grid(row=30, column=6)
jeffersoninv31cb = Checkbutton(inv, variable=jeffersoninv31cbval)
jeffersoninv31cb.grid(row=31, column=6)
jeffersoninv32cb = Checkbutton(inv, variable=jeffersoninv32cbval)
jeffersoninv32cb.grid(row=32, column=6)
jeffersoninv33cb = Checkbutton(inv, variable=jeffersoninv33cbval)
jeffersoninv33cb.grid(row=33, column=6)
jeffersoninv34cb = Checkbutton(inv, variable=jeffersoninv34cbval)
jeffersoninv34cb.grid(row=34, column=6)
jeffersoninv35cb = Checkbutton(inv, variable=jeffersoninv35cbval)
jeffersoninv35cb.grid(row=35, column=6)
jeffersoninv36cb = Checkbutton(inv, variable=jeffersoninv36cbval)
jeffersoninv36cb.grid(row=36, column=6)
jeffersoninv37cb = Checkbutton(inv, variable=jeffersoninv37cbval)
jeffersoninv37cb.grid(row=37, column=6)
jeffersoninv38cb = Checkbutton(inv, variable=jeffersoninv38cbval)
jeffersoninv38cb.grid(row=38, column=6)
jeffersoninv39cb = Checkbutton(inv, variable=jeffersoninv39cbval)
jeffersoninv39cb.grid(row=39, column=6)
jeffersoninv40cb = Checkbutton(inv, variable=jeffersoninv40cbval)
jeffersoninv40cb.grid(row=40, column=6)
jeffersoninv41cb = Checkbutton(inv, variable=jeffersoninv41cbval)
jeffersoninv41cb.grid(row=41, column=6)
jeffersoninv42cb = Checkbutton(inv, variable=jeffersoninv42cbval)
jeffersoninv42cb.grid(row=42, column=6)
jeffersoninv43cb = Checkbutton(inv, variable=jeffersoninv43cbval)
jeffersoninv43cb.grid(row=43, column=6)
jeffersoninv44cb = Checkbutton(inv, variable=jeffersoninv44cbval)
jeffersoninv44cb.grid(row=44, column=6)
jeffersoninv45cb = Checkbutton(inv, variable=jeffersoninv45cbval)
jeffersoninv45cb.grid(row=45, column=6)
jeffersoninv46cb = Checkbutton(inv, variable=jeffersoninv46cbval)
jeffersoninv46cb.grid(row=46, column=6)
jeffersoninv47cb = Checkbutton(inv, variable=jeffersoninv47cbval)
jeffersoninv47cb.grid(row=47, column=6)
jeffersoninv48cb = Checkbutton(inv, variable=jeffersoninv48cbval)
jeffersoninv48cb.grid(row=48, column=6)
jeffersoninv49cb = Checkbutton(inv, variable=jeffersoninv49cbval)
jeffersoninv49cb.grid(row=49, column=6)
jeffersoninv50cb = Checkbutton(inv, variable=jeffersoninv50cbval)
jeffersoninv50cb.grid(row=50, column=6)
jeffersoninv51cb = Checkbutton(inv, variable=jeffersoninv51cbval)
jeffersoninv51cb.grid(row=51, column=6)
jeffersoninv52cb = Checkbutton(inv, variable=jeffersoninv52cbval)
jeffersoninv52cb.grid(row=52, column=6)
jeffersoninv53cb = Checkbutton(inv, variable=jeffersoninv53cbval)
jeffersoninv53cb.grid(row=53, column=6)
jeffersoninv54cb = Checkbutton(inv, variable=jeffersoninv54cbval)
jeffersoninv54cb.grid(row=54, column=6)
jeffersoninv55cb = Checkbutton(inv, variable=jeffersoninv55cbval)
jeffersoninv55cb.grid(row=55, column=6)
jeffersoninv56cb = Checkbutton(inv, variable=jeffersoninv56cbval)
jeffersoninv56cb.grid(row=56, column=6)
jeffersoninv57cb = Checkbutton(inv, variable=jeffersoninv57cbval)
jeffersoninv57cb.grid(row=57, column=6)
jeffersoninv58cb = Checkbutton(inv, variable=jeffersoninv58cbval)
jeffersoninv58cb.grid(row=58, column=6)
jeffersoninv59cb = Checkbutton(inv, variable=jeffersoninv59cbval)
jeffersoninv59cb.grid(row=59, column=6)
jeffersoninv60cb = Checkbutton(inv, variable=jeffersoninv60cbval)
jeffersoninv60cb.grid(row=60, column=6)
jeffersoninv61cb = Checkbutton(inv, variable=jeffersoninv61cbval)
jeffersoninv61cb.grid(row=61, column=6)
jeffersoninv62cb = Checkbutton(inv, variable=jeffersoninv62cbval)
jeffersoninv62cb.grid(row=62, column=6)
jeffersoninv63cb = Checkbutton(inv, variable=jeffersoninv63cbval)
jeffersoninv63cb.grid(row=63, column=6)
jeffersoninv64cb = Checkbutton(inv, variable=jeffersoninv64cbval)
jeffersoninv64cb.grid(row=64, column=6)



marshall1Label= Label(inv, text= "Marshall")
marshall1Label.grid(row=0, column=7, columnspan=2)

marshallinv1Label= Label(inv, text= "X")
marshallinv1Label.grid(row=1, column=7)

marshallinv2Label = Label(inv, text="X")
marshallinv2Label.grid(row=2, column=7)

# Marshall Inv 3
marshallinv3Label = Label(inv, text="X")
marshallinv3Label.grid(row=3, column=7)

# Marshall Inv 4
marshallinv4Label = Label(inv, text="X")
marshallinv4Label.grid(row=4, column=7)

# Marshall Inv 5
marshallinv5Label = Label(inv, text="X")
marshallinv5Label.grid(row=5, column=7)

# Marshall Inv 6
marshallinv6Label = Label(inv, text="X")
marshallinv6Label.grid(row=6, column=7)

# Marshall Inv 7
marshallinv7Label = Label(inv, text="X")
marshallinv7Label.grid(row=7, column=7)

# Marshall Inv 8
marshallinv8Label = Label(inv, text="X")
marshallinv8Label.grid(row=8, column=7)

# Marshall Inv 9
marshallinv9Label = Label(inv, text="X")
marshallinv9Label.grid(row=9, column=7)

# Marshall Inv 10
marshallinv10Label = Label(inv, text="X")
marshallinv10Label.grid(row=10, column=7)

# Marshall Inv 11
marshallinv11Label = Label(inv, text="X")
marshallinv11Label.grid(row=11, column=7)

# Marshall Inv 12
marshallinv12Label = Label(inv, text="X")
marshallinv12Label.grid(row=12, column=7)

# Marshall Inv 13
marshallinv13Label = Label(inv, text="X")
marshallinv13Label.grid(row=13, column=7)

# Marshall Inv 14
marshallinv14Label = Label(inv, text="X")
marshallinv14Label.grid(row=14, column=7)

# Marshall Inv 15
marshallinv15Label = Label(inv, text="X")
marshallinv15Label.grid(row=15, column=7)

# Marshall Inv 16
marshallinv16Label = Label(inv, text="X")
marshallinv16Label.grid(row=16, column=7)


marshallinv1cb = Checkbutton(inv, variable=marshallinv1cbval)
marshallinv1cb.grid(row=1, column=8)
marshallinv2cb = Checkbutton(inv, variable=marshallinv2cbval)
marshallinv2cb.grid(row=2, column=8)
marshallinv3cb = Checkbutton(inv, variable=marshallinv3cbval)
marshallinv3cb.grid(row=3, column=8)
marshallinv4cb = Checkbutton(inv, variable=marshallinv4cbval)
marshallinv4cb.grid(row=4, column=8)
marshallinv5cb = Checkbutton(inv, variable=marshallinv5cbval)
marshallinv5cb.grid(row=5, column=8)
marshallinv6cb = Checkbutton(inv, variable=marshallinv6cbval)
marshallinv6cb.grid(row=6, column=8)
marshallinv7cb = Checkbutton(inv, variable=marshallinv7cbval)
marshallinv7cb.grid(row=7, column=8)
marshallinv8cb = Checkbutton(inv, variable=marshallinv8cbval)
marshallinv8cb.grid(row=8, column=8)
marshallinv9cb = Checkbutton(inv, variable=marshallinv9cbval)
marshallinv9cb.grid(row=9, column=8)
marshallinv10cb = Checkbutton(inv, variable=marshallinv10cbval)
marshallinv10cb.grid(row=10, column=8)
marshallinv11cb = Checkbutton(inv, variable=marshallinv11cbval)
marshallinv11cb.grid(row=11, column=8)
marshallinv12cb = Checkbutton(inv, variable=marshallinv12cbval)
marshallinv12cb.grid(row=12, column=8)
marshallinv13cb = Checkbutton(inv, variable=marshallinv13cbval)
marshallinv13cb.grid(row=13, column=8)
marshallinv14cb = Checkbutton(inv, variable=marshallinv14cbval)
marshallinv14cb.grid(row=14, column=8)
marshallinv15cb = Checkbutton(inv, variable=marshallinv15cbval)
marshallinv15cb.grid(row=15, column=8)
marshallinv16cb = Checkbutton(inv, variable=marshallinv16cbval)
marshallinv16cb.grid(row=16, column=8)



mcLean1Label= Label(solrvr, text= "McLean")
mcLean1Label.grid(row=0, column=11, columnspan=2)

mcLeaninv1Label= Label(solrvr, text= "X")
mcLeaninv1Label.grid(row=1, column=11)

mcLeaninv2Label = Label(solrvr, text="X")
mcLeaninv2Label.grid(row=2, column=11)

# McLean Inv 3
mcLeaninv3Label = Label(solrvr, text="X")
mcLeaninv3Label.grid(row=3, column=11)

# McLean Inv 4
mcLeaninv4Label = Label(solrvr, text="X")
mcLeaninv4Label.grid(row=4, column=11)

# McLean Inv 5
mcLeaninv5Label = Label(solrvr, text="X")
mcLeaninv5Label.grid(row=5, column=11)

# McLean Inv 6
mcLeaninv6Label = Label(solrvr, text="X")
mcLeaninv6Label.grid(row=6, column=11)

# McLean Inv 7
mcLeaninv7Label = Label(solrvr, text="X")
mcLeaninv7Label.grid(row=7, column=11)

# McLean Inv 8
mcLeaninv8Label = Label(solrvr, text="X")
mcLeaninv8Label.grid(row=8, column=11)

# McLean Inv 9
mcLeaninv9Label = Label(solrvr, text="X")
mcLeaninv9Label.grid(row=9, column=11)

# McLean Inv 10
mcLeaninv10Label = Label(solrvr, text="X")
mcLeaninv10Label.grid(row=10, column=11)

# McLean Inv 11
mcLeaninv11Label = Label(solrvr, text="X")
mcLeaninv11Label.grid(row=11, column=11)

# McLean Inv 12
mcLeaninv12Label = Label(solrvr, text="X")
mcLeaninv12Label.grid(row=12, column=11)

# McLean Inv 13
mcLeaninv13Label = Label(solrvr, text="X")
mcLeaninv13Label.grid(row=13, column=11)

# McLean Inv 14
mcLeaninv14Label = Label(solrvr, text="X")
mcLeaninv14Label.grid(row=14, column=11)

# McLean Inv 15
mcLeaninv15Label = Label(solrvr, text="X")
mcLeaninv15Label.grid(row=15, column=11)

# McLean Inv 16
mcLeaninv16Label = Label(solrvr, text="X")
mcLeaninv16Label.grid(row=16, column=11)

# McLean Inv 17
mcLeaninv17Label = Label(solrvr, text="X")
mcLeaninv17Label.grid(row=17, column=11)

# McLean Inv 18
mcLeaninv18Label = Label(solrvr, text="X")
mcLeaninv18Label.grid(row=18, column=11)

# McLean Inv 19
mcLeaninv19Label = Label(solrvr, text="X")
mcLeaninv19Label.grid(row=19, column=11)

# McLean Inv 20
mcLeaninv20Label = Label(solrvr, text="X")
mcLeaninv20Label.grid(row=20, column=11)

# McLean Inv 21
mcLeaninv21Label = Label(solrvr, text="X")
mcLeaninv21Label.grid(row=21, column=11)

# McLean Inv 22
mcLeaninv22Label = Label(solrvr, text="X")
mcLeaninv22Label.grid(row=22, column=11)

# McLean Inv 23
mcLeaninv23Label = Label(solrvr, text="X")
mcLeaninv23Label.grid(row=23, column=11)

# McLean Inv 24
mcLeaninv24Label = Label(solrvr, text="X")
mcLeaninv24Label.grid(row=24, column=11)

# McLean Inv 25
mcLeaninv25Label = Label(solrvr, text="X")
mcLeaninv25Label.grid(row=25, column=11)

# McLean Inv 26
mcLeaninv26Label = Label(solrvr, text="X")
mcLeaninv26Label.grid(row=26, column=11)

# McLean Inv 27
mcLeaninv27Label = Label(solrvr, text="X")
mcLeaninv27Label.grid(row=27, column=11)

# McLean Inv 28
mcLeaninv28Label = Label(solrvr, text="X")
mcLeaninv28Label.grid(row=28, column=11)

# McLean Inv 29
mcLeaninv29Label = Label(solrvr, text="X")
mcLeaninv29Label.grid(row=29, column=11)

# McLean Inv 30
mcLeaninv30Label = Label(solrvr, text="X")
mcLeaninv30Label.grid(row=30, column=11)

# McLean Inv 31
mcLeaninv31Label = Label(solrvr, text="X")
mcLeaninv31Label.grid(row=31, column=11)

# McLean Inv 32
mcLeaninv32Label = Label(solrvr, text="X")
mcLeaninv32Label.grid(row=32, column=11)

# McLean Inv 33
mcLeaninv33Label = Label(solrvr, text="X")
mcLeaninv33Label.grid(row=33, column=11)

# McLean Inv 34
mcLeaninv34Label = Label(solrvr, text="X")
mcLeaninv34Label.grid(row=34, column=11)

# McLean Inv 35
mcLeaninv35Label = Label(solrvr, text="X")
mcLeaninv35Label.grid(row=35, column=11)

# McLean Inv 36
mcLeaninv36Label = Label(solrvr, text="X")
mcLeaninv36Label.grid(row=36, column=11)

# McLean Inv 37
mcLeaninv37Label = Label(solrvr, text="X")
mcLeaninv37Label.grid(row=37, column=11)

# McLean Inv 38
mcLeaninv38Label = Label(solrvr, text="X")
mcLeaninv38Label.grid(row=38, column=11)

# McLean Inv 39
mcLeaninv39Label = Label(solrvr, text="X")
mcLeaninv39Label.grid(row=39, column=11)

# McLean Inv 40
mcLeaninv40Label = Label(solrvr, text="X")
mcLeaninv40Label.grid(row=40, column=11)

mcLeaninv1cb = Checkbutton(solrvr, variable=mcLeaninv1cbval)
mcLeaninv1cb.grid(row=1, column=12)
mcLeaninv2cb = Checkbutton(solrvr, variable=mcLeaninv2cbval)
mcLeaninv2cb.grid(row=2, column=12)
mcLeaninv3cb = Checkbutton(solrvr, variable=mcLeaninv3cbval)
mcLeaninv3cb.grid(row=3, column=12)
mcLeaninv4cb = Checkbutton(solrvr, variable=mcLeaninv4cbval)
mcLeaninv4cb.grid(row=4, column=12)
mcLeaninv5cb = Checkbutton(solrvr, variable=mcLeaninv5cbval)
mcLeaninv5cb.grid(row=5, column=12)
mcLeaninv6cb = Checkbutton(solrvr, variable=mcLeaninv6cbval)
mcLeaninv6cb.grid(row=6, column=12)
mcLeaninv7cb = Checkbutton(solrvr, variable=mcLeaninv7cbval)
mcLeaninv7cb.grid(row=7, column=12)
mcLeaninv8cb = Checkbutton(solrvr, variable=mcLeaninv8cbval)
mcLeaninv8cb.grid(row=8, column=12)
mcLeaninv9cb = Checkbutton(solrvr, variable=mcLeaninv9cbval)
mcLeaninv9cb.grid(row=9, column=12)
mcLeaninv10cb = Checkbutton(solrvr, variable=mcLeaninv10cbval)
mcLeaninv10cb.grid(row=10, column=12)
mcLeaninv11cb = Checkbutton(solrvr, variable=mcLeaninv11cbval)
mcLeaninv11cb.grid(row=11, column=12)
mcLeaninv12cb = Checkbutton(solrvr, variable=mcLeaninv12cbval)
mcLeaninv12cb.grid(row=12, column=12)
mcLeaninv13cb = Checkbutton(solrvr, variable=mcLeaninv13cbval)
mcLeaninv13cb.grid(row=13, column=12)
mcLeaninv14cb = Checkbutton(solrvr, variable=mcLeaninv14cbval)
mcLeaninv14cb.grid(row=14, column=12)
mcLeaninv15cb = Checkbutton(solrvr, variable=mcLeaninv15cbval)
mcLeaninv15cb.grid(row=15, column=12)
mcLeaninv16cb = Checkbutton(solrvr, variable=mcLeaninv16cbval)
mcLeaninv16cb.grid(row=16, column=12)
mcLeaninv17cb = Checkbutton(solrvr, variable=mcLeaninv17cbval)
mcLeaninv17cb.grid(row=17, column=12)
mcLeaninv18cb = Checkbutton(solrvr, variable=mcLeaninv18cbval)
mcLeaninv18cb.grid(row=18, column=12)
mcLeaninv19cb = Checkbutton(solrvr, variable=mcLeaninv19cbval)
mcLeaninv19cb.grid(row=19, column=12)
mcLeaninv20cb = Checkbutton(solrvr, variable=mcLeaninv20cbval)
mcLeaninv20cb.grid(row=20, column=12)
mcLeaninv21cb = Checkbutton(solrvr, variable=mcLeaninv21cbval)
mcLeaninv21cb.grid(row=21, column=12)
mcLeaninv22cb = Checkbutton(solrvr, variable=mcLeaninv22cbval)
mcLeaninv22cb.grid(row=22, column=12)
mcLeaninv23cb = Checkbutton(solrvr, variable=mcLeaninv23cbval)
mcLeaninv23cb.grid(row=23, column=12)
mcLeaninv24cb = Checkbutton(solrvr, variable=mcLeaninv24cbval)
mcLeaninv24cb.grid(row=24, column=12)
mcLeaninv25cb = Checkbutton(solrvr, variable=mcLeaninv25cbval)
mcLeaninv25cb.grid(row=25, column=12)
mcLeaninv26cb = Checkbutton(solrvr, variable=mcLeaninv26cbval)
mcLeaninv26cb.grid(row=26, column=12)
mcLeaninv27cb = Checkbutton(solrvr, variable=mcLeaninv27cbval)
mcLeaninv27cb.grid(row=27, column=12)
mcLeaninv28cb = Checkbutton(solrvr, variable=mcLeaninv28cbval)
mcLeaninv28cb.grid(row=28, column=12)
mcLeaninv29cb = Checkbutton(solrvr, variable=mcLeaninv29cbval)
mcLeaninv29cb.grid(row=29, column=12)
mcLeaninv30cb = Checkbutton(solrvr, variable=mcLeaninv30cbval)
mcLeaninv30cb.grid(row=30, column=12)
mcLeaninv31cb = Checkbutton(solrvr, variable=mcLeaninv31cbval)
mcLeaninv31cb.grid(row=31, column=12)
mcLeaninv32cb = Checkbutton(solrvr, variable=mcLeaninv32cbval)
mcLeaninv32cb.grid(row=32, column=12)
mcLeaninv33cb = Checkbutton(solrvr, variable=mcLeaninv33cbval)
mcLeaninv33cb.grid(row=33, column=12)
mcLeaninv34cb = Checkbutton(solrvr, variable=mcLeaninv34cbval)
mcLeaninv34cb.grid(row=34, column=12)
mcLeaninv35cb = Checkbutton(solrvr, variable=mcLeaninv35cbval)
mcLeaninv35cb.grid(row=35, column=12)
mcLeaninv36cb = Checkbutton(solrvr, variable=mcLeaninv36cbval)
mcLeaninv36cb.grid(row=36, column=12)
mcLeaninv37cb = Checkbutton(solrvr, variable=mcLeaninv37cbval)
mcLeaninv37cb.grid(row=37, column=12)
mcLeaninv38cb = Checkbutton(solrvr, variable=mcLeaninv38cbval)
mcLeaninv38cb.grid(row=38, column=12)
mcLeaninv39cb = Checkbutton(solrvr, variable=mcLeaninv39cbval)
mcLeaninv39cb.grid(row=39, column=12)
mcLeaninv40cb = Checkbutton(solrvr, variable=mcLeaninv40cbval)
mcLeaninv40cb.grid(row=40, column=12)


ogburn1Label= Label(inv, text= "Ogburn")
ogburn1Label.grid(row=0, column=11, columnspan=2)

ogburninv1Label = Label(inv, text= "X")
ogburninv1Label.grid(row= 1, column=11)
# Ogburn Inv 2
ogburninv2Label = Label(inv, text="X")
ogburninv2Label.grid(row=2, column=11)

# Ogburn Inv 3
ogburninv3Label = Label(inv, text="X")
ogburninv3Label.grid(row=3, column=11)

# Ogburn Inv 4
ogburninv4Label = Label(inv, text="X")
ogburninv4Label.grid(row=4, column=11)

# Ogburn Inv 5
ogburninv5Label = Label(inv, text="X")
ogburninv5Label.grid(row=5, column=11)

# Ogburn Inv 6
ogburninv6Label = Label(inv, text="X")
ogburninv6Label.grid(row=6, column=11)

# Ogburn Inv 7
ogburninv7Label = Label(inv, text="X")
ogburninv7Label.grid(row=7, column=11)

# Ogburn Inv 8
ogburninv8Label = Label(inv, text="X")
ogburninv8Label.grid(row=8, column=11)

# Ogburn Inv 9
ogburninv9Label = Label(inv, text="X")
ogburninv9Label.grid(row=9, column=11)

# Ogburn Inv 10
ogburninv10Label = Label(inv, text="X")
ogburninv10Label.grid(row=10, column=11)

# Ogburn Inv 11
ogburninv11Label = Label(inv, text="X")
ogburninv11Label.grid(row=11, column=11)

# Ogburn Inv 12
ogburninv12Label = Label(inv, text="X")
ogburninv12Label.grid(row=12, column=11)

# Ogburn Inv 13
ogburninv13Label = Label(inv, text="X")
ogburninv13Label.grid(row=13, column=11)

# Ogburn Inv 14
ogburninv14Label = Label(inv, text="X")
ogburninv14Label.grid(row=14, column=11)

# Ogburn Inv 15
ogburninv15Label = Label(inv, text="X")
ogburninv15Label.grid(row=15, column=11)

# Ogburn Inv 16
ogburninv16Label = Label(inv, text="X")
ogburninv16Label.grid(row=16, column=11)

ogburninv1cb = Checkbutton(inv, variable=ogburninv1cbval)
ogburninv1cb.grid(row=1, column=12)
ogburninv2cb = Checkbutton(inv, variable=ogburninv2cbval)
ogburninv2cb.grid(row=2, column=12)
ogburninv3cb = Checkbutton(inv, variable=ogburninv3cbval)
ogburninv3cb.grid(row=3, column=12)
ogburninv4cb = Checkbutton(inv, variable=ogburninv4cbval)
ogburninv4cb.grid(row=4, column=12)
ogburninv5cb = Checkbutton(inv, variable=ogburninv5cbval)
ogburninv5cb.grid(row=5, column=12)
ogburninv6cb = Checkbutton(inv, variable=ogburninv6cbval)
ogburninv6cb.grid(row=6, column=12)
ogburninv7cb = Checkbutton(inv, variable=ogburninv7cbval)
ogburninv7cb.grid(row=7, column=12)
ogburninv8cb = Checkbutton(inv, variable=ogburninv8cbval)
ogburninv8cb.grid(row=8, column=12)
ogburninv9cb = Checkbutton(inv, variable=ogburninv9cbval)
ogburninv9cb.grid(row=9, column=12)
ogburninv10cb = Checkbutton(inv, variable=ogburninv10cbval)
ogburninv10cb.grid(row=10, column=12)
ogburninv11cb = Checkbutton(inv, variable=ogburninv11cbval)
ogburninv11cb.grid(row=11, column=12)
ogburninv12cb = Checkbutton(inv, variable=ogburninv12cbval)
ogburninv12cb.grid(row=12, column=12)
ogburninv13cb = Checkbutton(inv, variable=ogburninv13cbval)
ogburninv13cb.grid(row=13, column=12)
ogburninv14cb = Checkbutton(inv, variable=ogburninv14cbval)
ogburninv14cb.grid(row=14, column=12)
ogburninv15cb = Checkbutton(inv, variable=ogburninv15cbval)
ogburninv15cb.grid(row=15, column=12)
ogburninv16cb = Checkbutton(inv, variable=ogburninv16cbval)
ogburninv16cb.grid(row=16, column=12)


pg1Label= Label(ncemc, text= "PG")
pg1Label.grid(row=0, column=6, columnspan=2)

pginv1Label= Label(ncemc, text= "X")
pginv1Label.grid(row=1, column=6)

# PG Inv 2
pginv2Label = Label(ncemc, text="X")
pginv2Label.grid(row=2, column=6)

# PG Inv 3
pginv3Label = Label(ncemc, text="X")
pginv3Label.grid(row=3, column=6)

# PG Inv 4
pginv4Label = Label(ncemc, text="X")
pginv4Label.grid(row=4, column=6)

# PG Inv 5
pginv5Label = Label(ncemc, text="X")
pginv5Label.grid(row=5, column=6)

# PG Inv 6
pginv6Label = Label(ncemc, text="X")
pginv6Label.grid(row=6, column=6)

# PG Inv 7
pginv7Label = Label(ncemc, text="X")
pginv7Label.grid(row=7, column=6)

# PG Inv 8
pginv8Label = Label(ncemc, text="X")
pginv8Label.grid(row=8, column=6)

# PG Inv 9
pginv9Label = Label(ncemc, text="X")
pginv9Label.grid(row=9, column=6)

# PG Inv 10
pginv10Label = Label(ncemc, text="X")
pginv10Label.grid(row=10, column=6)

# PG Inv 11
pginv11Label = Label(ncemc, text="X")
pginv11Label.grid(row=11, column=6)

# PG Inv 12
pginv12Label = Label(ncemc, text="X")
pginv12Label.grid(row=12, column=6)

# PG Inv 13
pginv13Label = Label(ncemc, text="X")
pginv13Label.grid(row=13, column=6)

# PG Inv 14
pginv14Label = Label(ncemc, text="X")
pginv14Label.grid(row=14, column=6)

# PG Inv 15
pginv15Label = Label(ncemc, text="X")
pginv15Label.grid(row=15, column=6)

# PG Inv 16
pginv16Label = Label(ncemc, text="X")
pginv16Label.grid(row=16, column=6)

# PG Inv 17
pginv17Label = Label(ncemc, text="X")
pginv17Label.grid(row=17, column=6)

# PG Inv 18
pginv18Label = Label(ncemc, text="X")
pginv18Label.grid(row=18, column=6)

pginv1cb = Checkbutton(ncemc, variable=pginv1cbval)
pginv1cb.grid(row=1, column=7)
pginv2cb = Checkbutton(ncemc, variable=pginv2cbval)
pginv2cb.grid(row=2, column=7)
pginv3cb = Checkbutton(ncemc, variable=pginv3cbval)
pginv3cb.grid(row=3, column=7)
pginv4cb = Checkbutton(ncemc, variable=pginv4cbval)
pginv4cb.grid(row=4, column=7)
pginv5cb = Checkbutton(ncemc, variable=pginv5cbval)
pginv5cb.grid(row=5, column=7)
pginv6cb = Checkbutton(ncemc, variable=pginv6cbval)
pginv6cb.grid(row=6, column=7)
pginv7cb = Checkbutton(ncemc, variable=pginv7cbval)
pginv7cb.grid(row=7, column=7)
pginv8cb = Checkbutton(ncemc, variable=pginv8cbval)
pginv8cb.grid(row=8, column=7)
pginv9cb = Checkbutton(ncemc, variable=pginv9cbval)
pginv9cb.grid(row=9, column=7)
pginv10cb = Checkbutton(ncemc, variable=pginv10cbval)
pginv10cb.grid(row=10, column=7)
pginv11cb = Checkbutton(ncemc, variable=pginv11cbval)
pginv11cb.grid(row=11, column=7)
pginv12cb = Checkbutton(ncemc, variable=pginv12cbval)
pginv12cb.grid(row=12, column=7)
pginv13cb = Checkbutton(ncemc, variable=pginv13cbval)
pginv13cb.grid(row=13, column=7)
pginv14cb = Checkbutton(ncemc, variable=pginv14cbval)
pginv14cb.grid(row=14, column=7)
pginv15cb = Checkbutton(ncemc, variable=pginv15cbval)
pginv15cb.grid(row=15, column=7)
pginv16cb = Checkbutton(ncemc, variable=pginv16cbval)
pginv16cb.grid(row=16, column=7)
pginv17cb = Checkbutton(ncemc, variable=pginv17cbval)
pginv17cb.grid(row=17, column=7)
pginv18cb = Checkbutton(ncemc, variable=pginv18cbval)
pginv18cb.grid(row=18, column=7)

richmond1Label= Label(solrvr, text= "Richmond")
richmond1Label.grid(row=0, column=13, columnspan=2)

richmondinv1Label = Label(solrvr, text= "X")
richmondinv1Label.grid(row=1, column=13)

richmondinv2Label = Label(solrvr, text="X")
richmondinv2Label.grid(row=2, column=13)

# Richmond Inv 3
richmondinv3Label = Label(solrvr, text="X")
richmondinv3Label.grid(row=3, column=13)

# Richmond Inv 4
richmondinv4Label = Label(solrvr, text="X")
richmondinv4Label.grid(row=4, column=13)

# Richmond Inv 5
richmondinv5Label = Label(solrvr, text="X")
richmondinv5Label.grid(row=5, column=13)

# Richmond Inv 6
richmondinv6Label = Label(solrvr, text="X")
richmondinv6Label.grid(row=6, column=13)

# Richmond Inv 7
richmondinv7Label = Label(solrvr, text="X")
richmondinv7Label.grid(row=7, column=13)

# Richmond Inv 8
richmondinv8Label = Label(solrvr, text="X")
richmondinv8Label.grid(row=8, column=13)

# Richmond Inv 9
richmondinv9Label = Label(solrvr, text="X")
richmondinv9Label.grid(row=9, column=13)

# Richmond Inv 10
richmondinv10Label = Label(solrvr, text="X")
richmondinv10Label.grid(row=10, column=13)

# Richmond Inv 11
richmondinv11Label = Label(solrvr, text="X")
richmondinv11Label.grid(row=11, column=13)

# Richmond Inv 12
richmondinv12Label = Label(solrvr, text="X")
richmondinv12Label.grid(row=12, column=13)

# Richmond Inv 13
richmondinv13Label = Label(solrvr, text="X")
richmondinv13Label.grid(row=13, column=13)

# Richmond Inv 14
richmondinv14Label = Label(solrvr, text="X")
richmondinv14Label.grid(row=14, column=13)

# Richmond Inv 15
richmondinv15Label = Label(solrvr, text="X")
richmondinv15Label.grid(row=15, column=13)

# Richmond Inv 16
richmondinv16Label = Label(solrvr, text="X")
richmondinv16Label.grid(row=16, column=13)

# Richmond Inv 17
richmondinv17Label = Label(solrvr, text="X")
richmondinv17Label.grid(row=17, column=13)

# Richmond Inv 18
richmondinv18Label = Label(solrvr, text="X")
richmondinv18Label.grid(row=18, column=13)

# Richmond Inv 19
richmondinv19Label = Label(solrvr, text="X")
richmondinv19Label.grid(row=19, column=13)

# Richmond Inv 20
richmondinv20Label = Label(solrvr, text="X")
richmondinv20Label.grid(row=20, column=13)

richmondinv21Label = Label(solrvr, text="X")
richmondinv21Label.grid(row=21, column=13)

# Richmond Inv 22
richmondinv22Label = Label(solrvr, text="X")
richmondinv22Label.grid(row=22, column=13)

# Richmond Inv 23
richmondinv23Label = Label(solrvr, text="X")
richmondinv23Label.grid(row=23, column=13)

# Richmond Inv 24
richmondinv24Label = Label(solrvr, text="X")
richmondinv24Label.grid(row=24, column=13)

richmondinv1cb = Checkbutton(solrvr, variable=richmondinv1cbval)
richmondinv1cb.grid(row=1, column=14)
richmondinv2cb = Checkbutton(solrvr, variable=richmondinv2cbval)
richmondinv2cb.grid(row=2, column=14)
richmondinv3cb = Checkbutton(solrvr, variable=richmondinv3cbval)
richmondinv3cb.grid(row=3, column=14)
richmondinv4cb = Checkbutton(solrvr, variable=richmondinv4cbval)
richmondinv4cb.grid(row=4, column=14)
richmondinv5cb = Checkbutton(solrvr, variable=richmondinv5cbval)
richmondinv5cb.grid(row=5, column=14)
richmondinv6cb = Checkbutton(solrvr, variable=richmondinv6cbval)
richmondinv6cb.grid(row=6, column=14)
richmondinv7cb = Checkbutton(solrvr, variable=richmondinv7cbval)
richmondinv7cb.grid(row=7, column=14)
richmondinv8cb = Checkbutton(solrvr, variable=richmondinv8cbval)
richmondinv8cb.grid(row=8, column=14)
richmondinv9cb = Checkbutton(solrvr, variable=richmondinv9cbval)
richmondinv9cb.grid(row=9, column=14)
richmondinv10cb = Checkbutton(solrvr, variable=richmondinv10cbval)
richmondinv10cb.grid(row=10, column=14)
richmondinv11cb = Checkbutton(solrvr, variable=richmondinv11cbval)
richmondinv11cb.grid(row=11, column=14)
richmondinv12cb = Checkbutton(solrvr, variable=richmondinv12cbval)
richmondinv12cb.grid(row=12, column=14)
richmondinv13cb = Checkbutton(solrvr, variable=richmondinv13cbval)
richmondinv13cb.grid(row=13, column=14)
richmondinv14cb = Checkbutton(solrvr, variable=richmondinv14cbval)
richmondinv14cb.grid(row=14, column=14)
richmondinv15cb = Checkbutton(solrvr, variable=richmondinv15cbval)
richmondinv15cb.grid(row=15, column=14)
richmondinv16cb = Checkbutton(solrvr, variable=richmondinv16cbval)
richmondinv16cb.grid(row=16, column=14)
richmondinv17cb = Checkbutton(solrvr, variable=richmondinv17cbval)
richmondinv17cb.grid(row=17, column=14)
richmondinv18cb = Checkbutton(solrvr, variable=richmondinv18cbval)
richmondinv18cb.grid(row=18, column=14)
richmondinv19cb = Checkbutton(solrvr, variable=richmondinv19cbval)
richmondinv19cb.grid(row=19, column=14)
richmondinv20cb = Checkbutton(solrvr, variable=richmondinv20cbval)
richmondinv20cb.grid(row=20, column=14)
richmondinv21cb = Checkbutton(solrvr, variable=richmondinv21cbval)
richmondinv21cb.grid(row=21, column=14)
richmondinv22cb = Checkbutton(solrvr, variable=richmondinv22cbval)
richmondinv22cb.grid(row=22, column=14)
richmondinv23cb = Checkbutton(solrvr, variable=richmondinv23cbval)
richmondinv23cb.grid(row=23, column=14)
richmondinv24cb = Checkbutton(solrvr, variable=richmondinv24cbval)
richmondinv24cb.grid(row=24, column=14)



shorthorn1Label= Label(solrvr, text= "Shorthorn")
shorthorn1Label.grid(row=0, column=15, columnspan=2)


shorthorninv1Label= Label(solrvr, text= "X")
shorthorninv1Label.grid(row= 1, column=15)
shorthorninv2Label = Label(solrvr, text="X")
shorthorninv2Label.grid(row=2, column=15)

# Shorthorn Inv 3
shorthorninv3Label = Label(solrvr, text="X")
shorthorninv3Label.grid(row=3, column=15)

# Shorthorn Inv 4
shorthorninv4Label = Label(solrvr, text="X")
shorthorninv4Label.grid(row=4, column=15)

# Shorthorn Inv 5
shorthorninv5Label = Label(solrvr, text="X")
shorthorninv5Label.grid(row=5, column=15)

# Shorthorn Inv 6
shorthorninv6Label = Label(solrvr, text="X")
shorthorninv6Label.grid(row=6, column=15)

# Shorthorn Inv 7
shorthorninv7Label = Label(solrvr, text="X")
shorthorninv7Label.grid(row=7, column=15)

# Shorthorn Inv 8
shorthorninv8Label = Label(solrvr, text="X")
shorthorninv8Label.grid(row=8, column=15)

# Shorthorn Inv 9
shorthorninv9Label = Label(solrvr, text="X")
shorthorninv9Label.grid(row=9, column=15)

# Shorthorn Inv 10
shorthorninv10Label = Label(solrvr, text="X")
shorthorninv10Label.grid(row=10, column=15)

# Shorthorn Inv 11
shorthorninv11Label = Label(solrvr, text="X")
shorthorninv11Label.grid(row=11, column=15)

# Shorthorn Inv 12
shorthorninv12Label = Label(solrvr, text="X")
shorthorninv12Label.grid(row=12, column=15)

# Shorthorn Inv 13
shorthorninv13Label = Label(solrvr, text="X")
shorthorninv13Label.grid(row=13, column=15)

# Shorthorn Inv 14
shorthorninv14Label = Label(solrvr, text="X")
shorthorninv14Label.grid(row=14, column=15)

# Shorthorn Inv 15
shorthorninv15Label = Label(solrvr, text="X")
shorthorninv15Label.grid(row=15, column=15)

# Shorthorn Inv 16
shorthorninv16Label = Label(solrvr, text="X")
shorthorninv16Label.grid(row=16, column=15)

# Shorthorn Inv 17
shorthorninv17Label = Label(solrvr, text="X")
shorthorninv17Label.grid(row=17, column=15)

# Shorthorn Inv 18
shorthorninv18Label = Label(solrvr, text="X")
shorthorninv18Label.grid(row=18, column=15)

# Shorthorn Inv 19
shorthorninv19Label = Label(solrvr, text="X")
shorthorninv19Label.grid(row=19, column=15)

# Shorthorn Inv 20
shorthorninv20Label = Label(solrvr, text="X")
shorthorninv20Label.grid(row=20, column=15)

# Shorthorn Inv 21
shorthorninv21Label = Label(solrvr, text="X")
shorthorninv21Label.grid(row=21, column=15)

# Shorthorn Inv 22
shorthorninv22Label = Label(solrvr, text="X")
shorthorninv22Label.grid(row=22, column=15)

# Shorthorn Inv 23
shorthorninv23Label = Label(solrvr, text="X")
shorthorninv23Label.grid(row=23, column=15)

# Shorthorn Inv 24
shorthorninv24Label = Label(solrvr, text="X")
shorthorninv24Label.grid(row=24, column=15)

# Shorthorn Inv 25
shorthorninv25Label = Label(solrvr, text="X")
shorthorninv25Label.grid(row=25, column=15)

# Shorthorn Inv 26
shorthorninv26Label = Label(solrvr, text="X")
shorthorninv26Label.grid(row=26, column=15)

# Shorthorn Inv 27
shorthorninv27Label = Label(solrvr, text="X")
shorthorninv27Label.grid(row=27, column=15)

# Shorthorn Inv 28
shorthorninv28Label = Label(solrvr, text="X")
shorthorninv28Label.grid(row=28, column=15)

# Shorthorn Inv 29
shorthorninv29Label = Label(solrvr, text="X")
shorthorninv29Label.grid(row=29, column=15)

# Shorthorn Inv 30
shorthorninv30Label = Label(solrvr, text="X")
shorthorninv30Label.grid(row=30, column=15)

# Shorthorn Inv 31
shorthorninv31Label = Label(solrvr, text="X")
shorthorninv31Label.grid(row=31, column=15)

# Shorthorn Inv 32
shorthorninv32Label = Label(solrvr, text="X")
shorthorninv32Label.grid(row=32, column=15)

# Shorthorn Inv 33
shorthorninv33Label = Label(solrvr, text="X")
shorthorninv33Label.grid(row=33, column=15)

# Shorthorn Inv 34
shorthorninv34Label = Label(solrvr, text="X")
shorthorninv34Label.grid(row=34, column=15)

# Shorthorn Inv 35
shorthorninv35Label = Label(solrvr, text="X")
shorthorninv35Label.grid(row=35, column=15)

# Shorthorn Inv 36
shorthorninv36Label = Label(solrvr, text="X")
shorthorninv36Label.grid(row=36, column=15)

# Shorthorn Inv 37
shorthorninv37Label = Label(solrvr, text="X")
shorthorninv37Label.grid(row=37, column=15)

# Shorthorn Inv 38
shorthorninv38Label = Label(solrvr, text="X")
shorthorninv38Label.grid(row=38, column=15)

# Shorthorn Inv 39
shorthorninv39Label = Label(solrvr, text="X")
shorthorninv39Label.grid(row=39, column=15)

# Shorthorn Inv 40
shorthorninv40Label = Label(solrvr, text="X")
shorthorninv40Label.grid(row=40, column=15)

# Shorthorn Inv 41
shorthorninv41Label = Label(solrvr, text="X")
shorthorninv41Label.grid(row=41, column=15)

# Shorthorn Inv 42
shorthorninv42Label = Label(solrvr, text="X")
shorthorninv42Label.grid(row=42, column=15)

# Shorthorn Inv 43
shorthorninv43Label = Label(solrvr, text="X")
shorthorninv43Label.grid(row=43, column=15)

# Shorthorn Inv 44
shorthorninv44Label = Label(solrvr, text="X")
shorthorninv44Label.grid(row=44, column=15)

# Shorthorn Inv 45
shorthorninv45Label = Label(solrvr, text="X")
shorthorninv45Label.grid(row=45, column=15)

# Shorthorn Inv 46
shorthorninv46Label = Label(solrvr, text="X")
shorthorninv46Label.grid(row=46, column=15)

# Shorthorn Inv 47
shorthorninv47Label = Label(solrvr, text="X")
shorthorninv47Label.grid(row=47, column=15)

# Shorthorn Inv 48
shorthorninv48Label = Label(solrvr, text="X")
shorthorninv48Label.grid(row=48, column=15)

# Shorthorn Inv 49
shorthorninv49Label = Label(solrvr, text="X")
shorthorninv49Label.grid(row=49, column=15)

# Shorthorn Inv 50
shorthorninv50Label = Label(solrvr, text="X")
shorthorninv50Label.grid(row=50, column=15)

# Shorthorn Inv 51
shorthorninv51Label = Label(solrvr, text="X")
shorthorninv51Label.grid(row=51, column=15)

# Shorthorn Inv 52
shorthorninv52Label = Label(solrvr, text="X")
shorthorninv52Label.grid(row=52, column=15)

# Shorthorn Inv 53
shorthorninv53Label = Label(solrvr, text="X")
shorthorninv53Label.grid(row=53, column=15)

# Shorthorn Inv 54
shorthorninv54Label = Label(solrvr, text="X")
shorthorninv54Label.grid(row=54, column=15)

# Shorthorn Inv 55
shorthorninv55Label = Label(solrvr, text="X")
shorthorninv55Label.grid(row=55, column=15)

# Shorthorn Inv 56
shorthorninv56Label = Label(solrvr, text="X")
shorthorninv56Label.grid(row=56, column=15)

# Shorthorn Inv 57
shorthorninv57Label = Label(solrvr, text="X")
shorthorninv57Label.grid(row=57, column=15)

# Shorthorn Inv 58
shorthorninv58Label = Label(solrvr, text="X")
shorthorninv58Label.grid(row=58, column=15)

# Shorthorn Inv 59
shorthorninv59Label = Label(solrvr, text="X")
shorthorninv59Label.grid(row=59, column=15)

# Shorthorn Inv 60
shorthorninv60Label = Label(solrvr, text="X")
shorthorninv60Label.grid(row=60, column=15)

# Shorthorn Inv 61
shorthorninv61Label = Label(solrvr, text="X")
shorthorninv61Label.grid(row=61, column=15)

# Shorthorn Inv 62
shorthorninv62Label = Label(solrvr, text="X")
shorthorninv62Label.grid(row=62, column=15)

# Shorthorn Inv 63
shorthorninv63Label = Label(solrvr, text="X")
shorthorninv63Label.grid(row=63, column=15)

# Shorthorn Inv 64
shorthorninv64Label = Label(solrvr, text="X")
shorthorninv64Label.grid(row=64, column=15)

# Shorthorn Inv 65
shorthorninv65Label = Label(solrvr, text="X")
shorthorninv65Label.grid(row=65, column=15)

# Shorthorn Inv 66
shorthorninv66Label = Label(solrvr, text="X")
shorthorninv66Label.grid(row=66, column=15)

# Shorthorn Inv 67
shorthorninv67Label = Label(solrvr, text="X")
shorthorninv67Label.grid(row=67, column=15)

# Shorthorn Inv 68
shorthorninv68Label = Label(solrvr, text="X")
shorthorninv68Label.grid(row=68, column=15)

# Shorthorn Inv 69
shorthorninv69Label = Label(solrvr, text="X")
shorthorninv69Label.grid(row=69, column=15)

# Shorthorn Inv 70
shorthorninv70Label = Label(solrvr, text="X")
shorthorninv70Label.grid(row=70, column=15)

# Shorthorn Inv 71
shorthorninv71Label = Label(solrvr, text="X")
shorthorninv71Label.grid(row=71, column=15)

# Shorthorn Inv 72
shorthorninv72Label = Label(solrvr, text="X")
shorthorninv72Label.grid(row=72, column=15)

shorthorninv1cb = Checkbutton(solrvr, variable=shorthorninv1cbval)
shorthorninv1cb.grid(row=1, column=16)
shorthorninv2cb = Checkbutton(solrvr, variable=shorthorninv2cbval)
shorthorninv2cb.grid(row=2, column=16)
shorthorninv3cb = Checkbutton(solrvr, variable=shorthorninv3cbval)
shorthorninv3cb.grid(row=3, column=16)
shorthorninv4cb = Checkbutton(solrvr, variable=shorthorninv4cbval)
shorthorninv4cb.grid(row=4, column=16)
shorthorninv5cb = Checkbutton(solrvr, variable=shorthorninv5cbval)
shorthorninv5cb.grid(row=5, column=16)
shorthorninv6cb = Checkbutton(solrvr, variable=shorthorninv6cbval)
shorthorninv6cb.grid(row=6, column=16)
shorthorninv7cb = Checkbutton(solrvr, variable=shorthorninv7cbval)
shorthorninv7cb.grid(row=7, column=16)
shorthorninv8cb = Checkbutton(solrvr, variable=shorthorninv8cbval)
shorthorninv8cb.grid(row=8, column=16)
shorthorninv9cb = Checkbutton(solrvr, variable=shorthorninv9cbval)
shorthorninv9cb.grid(row=9, column=16)
shorthorninv10cb = Checkbutton(solrvr, variable=shorthorninv10cbval)
shorthorninv10cb.grid(row=10, column=16)
shorthorninv11cb = Checkbutton(solrvr, variable=shorthorninv11cbval)
shorthorninv11cb.grid(row=11, column=16)
shorthorninv12cb = Checkbutton(solrvr, variable=shorthorninv12cbval)
shorthorninv12cb.grid(row=12, column=16)
shorthorninv13cb = Checkbutton(solrvr, variable=shorthorninv13cbval)
shorthorninv13cb.grid(row=13, column=16)
shorthorninv14cb = Checkbutton(solrvr, variable=shorthorninv14cbval)
shorthorninv14cb.grid(row=14, column=16)
shorthorninv15cb = Checkbutton(solrvr, variable=shorthorninv15cbval)
shorthorninv15cb.grid(row=15, column=16)
shorthorninv16cb = Checkbutton(solrvr, variable=shorthorninv16cbval)
shorthorninv16cb.grid(row=16, column=16)
shorthorninv17cb = Checkbutton(solrvr, variable=shorthorninv17cbval)
shorthorninv17cb.grid(row=17, column=16)
shorthorninv18cb = Checkbutton(solrvr, variable=shorthorninv18cbval)
shorthorninv18cb.grid(row=18, column=16)
shorthorninv19cb = Checkbutton(solrvr, variable=shorthorninv19cbval)
shorthorninv19cb.grid(row=19, column=16)
shorthorninv20cb = Checkbutton(solrvr, variable=shorthorninv20cbval)
shorthorninv20cb.grid(row=20, column=16)
shorthorninv21cb = Checkbutton(solrvr, variable=shorthorninv21cbval)
shorthorninv21cb.grid(row=21, column=16)
shorthorninv22cb = Checkbutton(solrvr, variable=shorthorninv22cbval)
shorthorninv22cb.grid(row=22, column=16)
shorthorninv23cb = Checkbutton(solrvr, variable=shorthorninv23cbval)
shorthorninv23cb.grid(row=23, column=16)
shorthorninv24cb = Checkbutton(solrvr, variable=shorthorninv24cbval)
shorthorninv24cb.grid(row=24, column=16)
shorthorninv25cb = Checkbutton(solrvr, variable=shorthorninv25cbval)
shorthorninv25cb.grid(row=25, column=16)
shorthorninv26cb = Checkbutton(solrvr, variable=shorthorninv26cbval)
shorthorninv26cb.grid(row=26, column=16)
shorthorninv27cb = Checkbutton(solrvr, variable=shorthorninv27cbval)
shorthorninv27cb.grid(row=27, column=16)
shorthorninv28cb = Checkbutton(solrvr, variable=shorthorninv28cbval)
shorthorninv28cb.grid(row=28, column=16)
shorthorninv29cb = Checkbutton(solrvr, variable=shorthorninv29cbval)
shorthorninv29cb.grid(row=29, column=16)
shorthorninv30cb = Checkbutton(solrvr, variable=shorthorninv30cbval)
shorthorninv30cb.grid(row=30, column=16)
shorthorninv31cb = Checkbutton(solrvr, variable=shorthorninv31cbval)
shorthorninv31cb.grid(row=31, column=16)
shorthorninv32cb = Checkbutton(solrvr, variable=shorthorninv32cbval)
shorthorninv32cb.grid(row=32, column=16)
shorthorninv33cb = Checkbutton(solrvr, variable=shorthorninv33cbval)
shorthorninv33cb.grid(row=33, column=16)
shorthorninv34cb = Checkbutton(solrvr, variable=shorthorninv34cbval)
shorthorninv34cb.grid(row=34, column=16)
shorthorninv35cb = Checkbutton(solrvr, variable=shorthorninv35cbval)
shorthorninv35cb.grid(row=35, column=16)
shorthorninv36cb = Checkbutton(solrvr, variable=shorthorninv36cbval)
shorthorninv36cb.grid(row=36, column=16)
shorthorninv37cb = Checkbutton(solrvr, variable=shorthorninv37cbval)
shorthorninv37cb.grid(row=37, column=16)
shorthorninv38cb = Checkbutton(solrvr, variable=shorthorninv38cbval)
shorthorninv38cb.grid(row=38, column=16)
shorthorninv39cb = Checkbutton(solrvr, variable=shorthorninv39cbval)
shorthorninv39cb.grid(row=39, column=16)
shorthorninv40cb = Checkbutton(solrvr, variable=shorthorninv40cbval)
shorthorninv40cb.grid(row=40, column=16)
shorthorninv41cb = Checkbutton(solrvr, variable=shorthorninv41cbval)
shorthorninv41cb.grid(row=41, column=16)
shorthorninv42cb = Checkbutton(solrvr, variable=shorthorninv42cbval)
shorthorninv42cb.grid(row=42, column=16)
shorthorninv43cb = Checkbutton(solrvr, variable=shorthorninv43cbval)
shorthorninv43cb.grid(row=43, column=16)
shorthorninv44cb = Checkbutton(solrvr, variable=shorthorninv44cbval)
shorthorninv44cb.grid(row=44, column=16)
shorthorninv45cb = Checkbutton(solrvr, variable=shorthorninv45cbval)
shorthorninv45cb.grid(row=45, column=16)
shorthorninv46cb = Checkbutton(solrvr, variable=shorthorninv46cbval)
shorthorninv46cb.grid(row=46, column=16)
shorthorninv47cb = Checkbutton(solrvr, variable=shorthorninv47cbval)
shorthorninv47cb.grid(row=47, column=16)
shorthorninv48cb = Checkbutton(solrvr, variable=shorthorninv48cbval)
shorthorninv48cb.grid(row=48, column=16)
shorthorninv49cb = Checkbutton(solrvr, variable=shorthorninv49cbval)
shorthorninv49cb.grid(row=49, column=16)
shorthorninv50cb = Checkbutton(solrvr, variable=shorthorninv50cbval)
shorthorninv50cb.grid(row=50, column=16)
shorthorninv51cb = Checkbutton(solrvr, variable=shorthorninv51cbval)
shorthorninv51cb.grid(row=51, column=16)
shorthorninv52cb = Checkbutton(solrvr, variable=shorthorninv52cbval)
shorthorninv52cb.grid(row=52, column=16)
shorthorninv53cb = Checkbutton(solrvr, variable=shorthorninv53cbval)
shorthorninv53cb.grid(row=53, column=16)
shorthorninv54cb = Checkbutton(solrvr, variable=shorthorninv54cbval)
shorthorninv54cb.grid(row=54, column=16)
shorthorninv55cb = Checkbutton(solrvr, variable=shorthorninv55cbval)
shorthorninv55cb.grid(row=55, column=16)
shorthorninv56cb = Checkbutton(solrvr, variable=shorthorninv56cbval)
shorthorninv56cb.grid(row=56, column=16)
shorthorninv57cb = Checkbutton(solrvr, variable=shorthorninv57cbval)
shorthorninv57cb.grid(row=57, column=16)
shorthorninv58cb = Checkbutton(solrvr, variable=shorthorninv58cbval)
shorthorninv58cb.grid(row=58, column=16)
shorthorninv59cb = Checkbutton(solrvr, variable=shorthorninv59cbval)
shorthorninv59cb.grid(row=59, column=16)
shorthorninv60cb = Checkbutton(solrvr, variable=shorthorninv60cbval)
shorthorninv60cb.grid(row=60, column=16)
shorthorninv61cb = Checkbutton(solrvr, variable=shorthorninv61cbval)
shorthorninv61cb.grid(row=61, column=16)
shorthorninv62cb = Checkbutton(solrvr, variable=shorthorninv62cbval)
shorthorninv62cb.grid(row=62, column=16)
shorthorninv63cb = Checkbutton(solrvr, variable=shorthorninv63cbval)
shorthorninv63cb.grid(row=63, column=16)
shorthorninv64cb = Checkbutton(solrvr, variable=shorthorninv64cbval)
shorthorninv64cb.grid(row=64, column=16)
shorthorninv65cb = Checkbutton(solrvr, variable=shorthorninv65cbval)
shorthorninv65cb.grid(row=65, column=16)
shorthorninv66cb = Checkbutton(solrvr, variable=shorthorninv66cbval)
shorthorninv66cb.grid(row=66, column=16)
shorthorninv67cb = Checkbutton(solrvr, variable=shorthorninv67cbval)
shorthorninv67cb.grid(row=67, column=16)
shorthorninv68cb = Checkbutton(solrvr, variable=shorthorninv68cbval)
shorthorninv68cb.grid(row=68, column=16)
shorthorninv69cb = Checkbutton(solrvr, variable=shorthorninv69cbval)
shorthorninv69cb.grid(row=69, column=16)
shorthorninv70cb = Checkbutton(solrvr, variable=shorthorninv70cbval)
shorthorninv70cb.grid(row=70, column=16)
shorthorninv71cb = Checkbutton(solrvr, variable=shorthorninv71cbval)
shorthorninv71cb.grid(row=71, column=16)
shorthorninv72cb = Checkbutton(solrvr, variable=shorthorninv72cbval)
shorthorninv72cb.grid(row=72, column=16)







sunflower1Label= Label(solrvr, text= "Sunflower")
sunflower1Label.grid(row=0, column=17, columnspan=2)

sunflowerinv1Label= Label(solrvr, text= "X")
sunflowerinv1Label.grid(row= 1, column=17)

sunflowerinv2Label = Label(solrvr, text="X")
sunflowerinv2Label.grid(row=2, column=17)

# Sunflower Inv 3
sunflowerinv3Label = Label(solrvr, text="X")
sunflowerinv3Label.grid(row=3, column=17)

# Sunflower Inv 4
sunflowerinv4Label = Label(solrvr, text="X")
sunflowerinv4Label.grid(row=4, column=17)

# Sunflower Inv 5
sunflowerinv5Label = Label(solrvr, text="X")
sunflowerinv5Label.grid(row=5, column=17)

# Sunflower Inv 6
sunflowerinv6Label = Label(solrvr, text="X")
sunflowerinv6Label.grid(row=6, column=17)

# Sunflower Inv 7
sunflowerinv7Label = Label(solrvr, text="X")
sunflowerinv7Label.grid(row=7, column=17)

# Sunflower Inv 8
sunflowerinv8Label = Label(solrvr, text="X")
sunflowerinv8Label.grid(row=8, column=17)

# Sunflower Inv 9
sunflowerinv9Label = Label(solrvr, text="X")
sunflowerinv9Label.grid(row=9, column=17)

# Sunflower Inv 10
sunflowerinv10Label = Label(solrvr, text="X")
sunflowerinv10Label.grid(row=10, column=17)

# Sunflower Inv 11
sunflowerinv11Label = Label(solrvr, text="X")
sunflowerinv11Label.grid(row=11, column=17)

# Sunflower Inv 12
sunflowerinv12Label = Label(solrvr, text="X")
sunflowerinv12Label.grid(row=12, column=17)

# Sunflower Inv 13
sunflowerinv13Label = Label(solrvr, text="X")
sunflowerinv13Label.grid(row=13, column=17)

# Sunflower Inv 14
sunflowerinv14Label = Label(solrvr, text="X")
sunflowerinv14Label.grid(row=14, column=17)

# Sunflower Inv 15
sunflowerinv15Label = Label(solrvr, text="X")
sunflowerinv15Label.grid(row=15, column=17)

# Sunflower Inv 16
sunflowerinv16Label = Label(solrvr, text="X")
sunflowerinv16Label.grid(row=16, column=17)

# Sunflower Inv 17
sunflowerinv17Label = Label(solrvr, text="X")
sunflowerinv17Label.grid(row=17, column=17)

# Sunflower Inv 18
sunflowerinv18Label = Label(solrvr, text="X")
sunflowerinv18Label.grid(row=18, column=17)

# Sunflower Inv 19
sunflowerinv19Label = Label(solrvr, text="X")
sunflowerinv19Label.grid(row=19, column=17)

# Sunflower Inv 20
sunflowerinv20Label = Label(solrvr, text="X")
sunflowerinv20Label.grid(row=20, column=17)

# Sunflower Inv 21
sunflowerinv21Label = Label(solrvr, text="X")
sunflowerinv21Label.grid(row=21, column=17)

# Sunflower Inv 22
sunflowerinv22Label = Label(solrvr, text="X")
sunflowerinv22Label.grid(row=22, column=17)

# Sunflower Inv 23
sunflowerinv23Label = Label(solrvr, text="X")
sunflowerinv23Label.grid(row=23, column=17)

# Sunflower Inv 24
sunflowerinv24Label = Label(solrvr, text="X")
sunflowerinv24Label.grid(row=24, column=17)

# Sunflower Inv 25
sunflowerinv25Label = Label(solrvr, text="X")
sunflowerinv25Label.grid(row=25, column=17)

# Sunflower Inv 26
sunflowerinv26Label = Label(solrvr, text="X")
sunflowerinv26Label.grid(row=26, column=17)

# Sunflower Inv 27
sunflowerinv27Label = Label(solrvr, text="X")
sunflowerinv27Label.grid(row=27, column=17)

# Sunflower Inv 28
sunflowerinv28Label = Label(solrvr, text="X")
sunflowerinv28Label.grid(row=28, column=17)

# Sunflower Inv 29
sunflowerinv29Label = Label(solrvr, text="X")
sunflowerinv29Label.grid(row=29, column=17)

# Sunflower Inv 30
sunflowerinv30Label = Label(solrvr, text="X")
sunflowerinv30Label.grid(row=30, column=17)

# Sunflower Inv 31
sunflowerinv31Label = Label(solrvr, text="X")
sunflowerinv31Label.grid(row=31, column=17)

# Sunflower Inv 32
sunflowerinv32Label = Label(solrvr, text="X")
sunflowerinv32Label.grid(row=32, column=17)

# Sunflower Inv 33
sunflowerinv33Label = Label(solrvr, text="X")
sunflowerinv33Label.grid(row=33, column=17)

# Sunflower Inv 34
sunflowerinv34Label = Label(solrvr, text="X")
sunflowerinv34Label.grid(row=34, column=17)

# Sunflower Inv 35
sunflowerinv35Label = Label(solrvr, text="X")
sunflowerinv35Label.grid(row=35, column=17)

# Sunflower Inv 36
sunflowerinv36Label = Label(solrvr, text="X")
sunflowerinv36Label.grid(row=36, column=17)

# Sunflower Inv 37
sunflowerinv37Label = Label(solrvr, text="X")
sunflowerinv37Label.grid(row=37, column=17)

# Sunflower Inv 38
sunflowerinv38Label = Label(solrvr, text="X")
sunflowerinv38Label.grid(row=38, column=17)

# Sunflower Inv 39
sunflowerinv39Label = Label(solrvr, text="X")
sunflowerinv39Label.grid(row=39, column=17)

# Sunflower Inv 40
sunflowerinv40Label = Label(solrvr, text="X")
sunflowerinv40Label.grid(row=40, column=17)

# Sunflower Inv 41
sunflowerinv41Label = Label(solrvr, text="X")
sunflowerinv41Label.grid(row=41, column=17)

# Sunflower Inv 42
sunflowerinv42Label = Label(solrvr, text="X")
sunflowerinv42Label.grid(row=42, column=17)

# Sunflower Inv 43
sunflowerinv43Label = Label(solrvr, text="X")
sunflowerinv43Label.grid(row=43, column=17)

# Sunflower Inv 44
sunflowerinv44Label = Label(solrvr, text="X")
sunflowerinv44Label.grid(row=44, column=17)

# Sunflower Inv 45
sunflowerinv45Label = Label(solrvr, text="X")
sunflowerinv45Label.grid(row=45, column=17)

# Sunflower Inv 46
sunflowerinv46Label = Label(solrvr, text="X")
sunflowerinv46Label.grid(row=46, column=17)

# Sunflower Inv 47
sunflowerinv47Label = Label(solrvr, text="X")
sunflowerinv47Label.grid(row=47, column=17)

# Sunflower Inv 48
sunflowerinv48Label = Label(solrvr, text="X")
sunflowerinv48Label.grid(row=48, column=17)

# Sunflower Inv 49
sunflowerinv49Label = Label(solrvr, text="X")
sunflowerinv49Label.grid(row=49, column=17)

# Sunflower Inv 50
sunflowerinv50Label = Label(solrvr, text="X")
sunflowerinv50Label.grid(row=50, column=17)

# Sunflower Inv 51
sunflowerinv51Label = Label(solrvr, text="X")
sunflowerinv51Label.grid(row=51, column=17)

# Sunflower Inv 52
sunflowerinv52Label = Label(solrvr, text="X")
sunflowerinv52Label.grid(row=52, column=17)

# Sunflower Inv 53
sunflowerinv53Label = Label(solrvr, text="X")
sunflowerinv53Label.grid(row=53, column=17)

# Sunflower Inv 54
sunflowerinv54Label = Label(solrvr, text="X")
sunflowerinv54Label.grid(row=54, column=17)

# Sunflower Inv 55
sunflowerinv55Label = Label(solrvr, text="X")
sunflowerinv55Label.grid(row=55, column=17)

# Sunflower Inv 56
sunflowerinv56Label = Label(solrvr, text="X")
sunflowerinv56Label.grid(row=56, column=17)

# Sunflower Inv 57
sunflowerinv57Label = Label(solrvr, text="X")
sunflowerinv57Label.grid(row=57, column=17)

# Sunflower Inv 58
sunflowerinv58Label = Label(solrvr, text="X")
sunflowerinv58Label.grid(row=58, column=17)

# Sunflower Inv 59
sunflowerinv59Label = Label(solrvr, text="X")
sunflowerinv59Label.grid(row=59, column=17)

# Sunflower Inv 60
sunflowerinv60Label = Label(solrvr, text="X")
sunflowerinv60Label.grid(row=60, column=17)

# Sunflower Inv 61
sunflowerinv61Label = Label(solrvr, text="X")
sunflowerinv61Label.grid(row=61, column=17)

# Sunflower Inv 62
sunflowerinv62Label = Label(solrvr, text="X")
sunflowerinv62Label.grid(row=62, column=17)

# Sunflower Inv 63
sunflowerinv63Label = Label(solrvr, text="X")
sunflowerinv63Label.grid(row=63, column=17)

# Sunflower Inv 64
sunflowerinv64Label = Label(solrvr, text="X")
sunflowerinv64Label.grid(row=64, column=17)

# Sunflower Inv 65
sunflowerinv65Label = Label(solrvr, text="X")
sunflowerinv65Label.grid(row=65, column=17)

# Sunflower Inv 66
sunflowerinv66Label = Label(solrvr, text="X")
sunflowerinv66Label.grid(row=66, column=17)

# Sunflower Inv 67
sunflowerinv67Label = Label(solrvr, text="X")
sunflowerinv67Label.grid(row=67, column=17)

# Sunflower Inv 68
sunflowerinv68Label = Label(solrvr, text="X")
sunflowerinv68Label.grid(row=68, column=17)

# Sunflower Inv 69
sunflowerinv69Label = Label(solrvr, text="X")
sunflowerinv69Label.grid(row=69, column=17)

# Sunflower Inv 70
sunflowerinv70Label = Label(solrvr, text="X")
sunflowerinv70Label.grid(row=70, column=17)

# Sunflower Inv 71
sunflowerinv71Label = Label(solrvr, text="X")
sunflowerinv71Label.grid(row=71, column=17)

# Sunflower Inv 72
sunflowerinv72Label = Label(solrvr, text="X")
sunflowerinv72Label.grid(row=72, column=17)

# Sunflower Inv 73
sunflowerinv73Label = Label(solrvr, text="X")
sunflowerinv73Label.grid(row=73, column=17)

# Sunflower Inv 74
sunflowerinv74Label = Label(solrvr, text="X")
sunflowerinv74Label.grid(row=74, column=17)

# Sunflower Inv 75
sunflowerinv75Label = Label(solrvr, text="X")
sunflowerinv75Label.grid(row=75, column=17)

# Sunflower Inv 76
sunflowerinv76Label = Label(solrvr, text="X")
sunflowerinv76Label.grid(row=76, column=17)

# Sunflower Inv 77
sunflowerinv77Label = Label(solrvr, text="X")
sunflowerinv77Label.grid(row=77, column=17)

# Sunflower Inv 78
sunflowerinv78Label = Label(solrvr, text="X")
sunflowerinv78Label.grid(row=78, column=17)

# Sunflower Inv 79
sunflowerinv79Label = Label(solrvr, text="X")
sunflowerinv79Label.grid(row=79, column=17)

# Sunflower Inv 80
sunflowerinv80Label = Label(solrvr, text="X")
sunflowerinv80Label.grid(row=80, column=17)


sunflowerinv1cb = Checkbutton(solrvr, variable=sunflowerinv1cbval)
sunflowerinv1cb.grid(row=1, column=18)
sunflowerinv2cb = Checkbutton(solrvr, variable=sunflowerinv2cbval)
sunflowerinv2cb.grid(row=2, column=18)
sunflowerinv3cb = Checkbutton(solrvr, variable=sunflowerinv3cbval)
sunflowerinv3cb.grid(row=3, column=18)
sunflowerinv4cb = Checkbutton(solrvr, variable=sunflowerinv4cbval)
sunflowerinv4cb.grid(row=4, column=18)
sunflowerinv5cb = Checkbutton(solrvr, variable=sunflowerinv5cbval)
sunflowerinv5cb.grid(row=5, column=18)
sunflowerinv6cb = Checkbutton(solrvr, variable=sunflowerinv6cbval)
sunflowerinv6cb.grid(row=6, column=18)
sunflowerinv7cb = Checkbutton(solrvr, variable=sunflowerinv7cbval)
sunflowerinv7cb.grid(row=7, column=18)
sunflowerinv8cb = Checkbutton(solrvr, variable=sunflowerinv8cbval)
sunflowerinv8cb.grid(row=8, column=18)
sunflowerinv9cb = Checkbutton(solrvr, variable=sunflowerinv9cbval)
sunflowerinv9cb.grid(row=9, column=18)
sunflowerinv10cb = Checkbutton(solrvr, variable=sunflowerinv10cbval)
sunflowerinv10cb.grid(row=10, column=18)
sunflowerinv11cb = Checkbutton(solrvr, variable=sunflowerinv11cbval)
sunflowerinv11cb.grid(row=11, column=18)
sunflowerinv12cb = Checkbutton(solrvr, variable=sunflowerinv12cbval)
sunflowerinv12cb.grid(row=12, column=18)
sunflowerinv13cb = Checkbutton(solrvr, variable=sunflowerinv13cbval)
sunflowerinv13cb.grid(row=13, column=18)
sunflowerinv14cb = Checkbutton(solrvr, variable=sunflowerinv14cbval)
sunflowerinv14cb.grid(row=14, column=18)
sunflowerinv15cb = Checkbutton(solrvr, variable=sunflowerinv15cbval)
sunflowerinv15cb.grid(row=15, column=18)
sunflowerinv16cb = Checkbutton(solrvr, variable=sunflowerinv16cbval)
sunflowerinv16cb.grid(row=16, column=18)
sunflowerinv17cb = Checkbutton(solrvr, variable=sunflowerinv17cbval)
sunflowerinv17cb.grid(row=17, column=18)
sunflowerinv18cb = Checkbutton(solrvr, variable=sunflowerinv18cbval)
sunflowerinv18cb.grid(row=18, column=18)
sunflowerinv19cb = Checkbutton(solrvr, variable=sunflowerinv19cbval)
sunflowerinv19cb.grid(row=19, column=18)
sunflowerinv20cb = Checkbutton(solrvr, variable=sunflowerinv20cbval)
sunflowerinv20cb.grid(row=20, column=18)
sunflowerinv21cb = Checkbutton(solrvr, variable=sunflowerinv21cbval)
sunflowerinv21cb.grid(row=21, column=18)
sunflowerinv22cb = Checkbutton(solrvr, variable=sunflowerinv22cbval)
sunflowerinv22cb.grid(row=22, column=18)
sunflowerinv23cb = Checkbutton(solrvr, variable=sunflowerinv23cbval)
sunflowerinv23cb.grid(row=23, column=18)
sunflowerinv24cb = Checkbutton(solrvr, variable=sunflowerinv24cbval)
sunflowerinv24cb.grid(row=24, column=18)
sunflowerinv25cb = Checkbutton(solrvr, variable=sunflowerinv25cbval)
sunflowerinv25cb.grid(row=25, column=18)
sunflowerinv26cb = Checkbutton(solrvr, variable=sunflowerinv26cbval)
sunflowerinv26cb.grid(row=26, column=18)
sunflowerinv27cb = Checkbutton(solrvr, variable=sunflowerinv27cbval)
sunflowerinv27cb.grid(row=27, column=18)
sunflowerinv28cb = Checkbutton(solrvr, variable=sunflowerinv28cbval)
sunflowerinv28cb.grid(row=28, column=18)
sunflowerinv29cb = Checkbutton(solrvr, variable=sunflowerinv29cbval)
sunflowerinv29cb.grid(row=29, column=18)
sunflowerinv30cb = Checkbutton(solrvr, variable=sunflowerinv30cbval)
sunflowerinv30cb.grid(row=30, column=18)
sunflowerinv31cb = Checkbutton(solrvr, variable=sunflowerinv31cbval)
sunflowerinv31cb.grid(row=31, column=18)
sunflowerinv32cb = Checkbutton(solrvr, variable=sunflowerinv32cbval)
sunflowerinv32cb.grid(row=32, column=18)
sunflowerinv33cb = Checkbutton(solrvr, variable=sunflowerinv33cbval)
sunflowerinv33cb.grid(row=33, column=18)
sunflowerinv34cb = Checkbutton(solrvr, variable=sunflowerinv34cbval)
sunflowerinv34cb.grid(row=34, column=18)
sunflowerinv35cb = Checkbutton(solrvr, variable=sunflowerinv35cbval)
sunflowerinv35cb.grid(row=35, column=18)
sunflowerinv36cb = Checkbutton(solrvr, variable=sunflowerinv36cbval)
sunflowerinv36cb.grid(row=36, column=18)
sunflowerinv37cb = Checkbutton(solrvr, variable=sunflowerinv37cbval)
sunflowerinv37cb.grid(row=37, column=18)
sunflowerinv38cb = Checkbutton(solrvr, variable=sunflowerinv38cbval)
sunflowerinv38cb.grid(row=38, column=18)
sunflowerinv39cb = Checkbutton(solrvr, variable=sunflowerinv39cbval)
sunflowerinv39cb.grid(row=39, column=18)
sunflowerinv40cb = Checkbutton(solrvr, variable=sunflowerinv40cbval)
sunflowerinv40cb.grid(row=40, column=18)
sunflowerinv41cb = Checkbutton(solrvr, variable=sunflowerinv41cbval)
sunflowerinv41cb.grid(row=41, column=18)
sunflowerinv42cb = Checkbutton(solrvr, variable=sunflowerinv42cbval)
sunflowerinv42cb.grid(row=42, column=18)
sunflowerinv43cb = Checkbutton(solrvr, variable=sunflowerinv43cbval)
sunflowerinv43cb.grid(row=43, column=18)
sunflowerinv44cb = Checkbutton(solrvr, variable=sunflowerinv44cbval)
sunflowerinv44cb.grid(row=44, column=18)
sunflowerinv45cb = Checkbutton(solrvr, variable=sunflowerinv45cbval)
sunflowerinv45cb.grid(row=45, column=18)
sunflowerinv46cb = Checkbutton(solrvr, variable=sunflowerinv46cbval)
sunflowerinv46cb.grid(row=46, column=18)
sunflowerinv47cb = Checkbutton(solrvr, variable=sunflowerinv47cbval)
sunflowerinv47cb.grid(row=47, column=18)
sunflowerinv48cb = Checkbutton(solrvr, variable=sunflowerinv48cbval)
sunflowerinv48cb.grid(row=48, column=18)
sunflowerinv49cb = Checkbutton(solrvr, variable=sunflowerinv49cbval)
sunflowerinv49cb.grid(row=49, column=18)
sunflowerinv50cb = Checkbutton(solrvr, variable=sunflowerinv50cbval)
sunflowerinv50cb.grid(row=50, column=18)
sunflowerinv51cb = Checkbutton(solrvr, variable=sunflowerinv51cbval)
sunflowerinv51cb.grid(row=51, column=18)
sunflowerinv52cb = Checkbutton(solrvr, variable=sunflowerinv52cbval)
sunflowerinv52cb.grid(row=52, column=18)
sunflowerinv53cb = Checkbutton(solrvr, variable=sunflowerinv53cbval)
sunflowerinv53cb.grid(row=53, column=18)
sunflowerinv54cb = Checkbutton(solrvr, variable=sunflowerinv54cbval)
sunflowerinv54cb.grid(row=54, column=18)
sunflowerinv55cb = Checkbutton(solrvr, variable=sunflowerinv55cbval)
sunflowerinv55cb.grid(row=55, column=18)
sunflowerinv56cb = Checkbutton(solrvr, variable=sunflowerinv56cbval)
sunflowerinv56cb.grid(row=56, column=18)
sunflowerinv57cb = Checkbutton(solrvr, variable=sunflowerinv57cbval)
sunflowerinv57cb.grid(row=57, column=18)
sunflowerinv58cb = Checkbutton(solrvr, variable=sunflowerinv58cbval)
sunflowerinv58cb.grid(row=58, column=18)
sunflowerinv59cb = Checkbutton(solrvr, variable=sunflowerinv59cbval)
sunflowerinv59cb.grid(row=59, column=18)
sunflowerinv60cb = Checkbutton(solrvr, variable=sunflowerinv60cbval)
sunflowerinv60cb.grid(row=60, column=18)
sunflowerinv61cb = Checkbutton(solrvr, variable=sunflowerinv61cbval)
sunflowerinv61cb.grid(row=61, column=18)
sunflowerinv62cb = Checkbutton(solrvr, variable=sunflowerinv62cbval)
sunflowerinv62cb.grid(row=62, column=18)
sunflowerinv63cb = Checkbutton(solrvr, variable=sunflowerinv63cbval)
sunflowerinv63cb.grid(row=63, column=18)
sunflowerinv64cb = Checkbutton(solrvr, variable=sunflowerinv64cbval)
sunflowerinv64cb.grid(row=64, column=18)
sunflowerinv65cb = Checkbutton(solrvr, variable=sunflowerinv65cbval)
sunflowerinv65cb.grid(row=65, column=18)
sunflowerinv66cb = Checkbutton(solrvr, variable=sunflowerinv66cbval)
sunflowerinv66cb.grid(row=66, column=18)
sunflowerinv67cb = Checkbutton(solrvr, variable=sunflowerinv67cbval)
sunflowerinv67cb.grid(row=67, column=18)
sunflowerinv68cb = Checkbutton(solrvr, variable=sunflowerinv68cbval)
sunflowerinv68cb.grid(row=68, column=18)
sunflowerinv69cb = Checkbutton(solrvr, variable=sunflowerinv69cbval)
sunflowerinv69cb.grid(row=69, column=18)
sunflowerinv70cb = Checkbutton(solrvr, variable=sunflowerinv70cbval)
sunflowerinv70cb.grid(row=70, column=18)
sunflowerinv71cb = Checkbutton(solrvr, variable=sunflowerinv71cbval)
sunflowerinv71cb.grid(row=71, column=18)
sunflowerinv72cb = Checkbutton(solrvr, variable=sunflowerinv72cbval)
sunflowerinv72cb.grid(row=72, column=18)
sunflowerinv73cb = Checkbutton(solrvr, variable=sunflowerinv73cbval)
sunflowerinv73cb.grid(row=73, column=18)
sunflowerinv74cb = Checkbutton(solrvr, variable=sunflowerinv74cbval)
sunflowerinv74cb.grid(row=74, column=18)
sunflowerinv75cb = Checkbutton(solrvr, variable=sunflowerinv75cbval)
sunflowerinv75cb.grid(row=75, column=18)
sunflowerinv76cb = Checkbutton(solrvr, variable=sunflowerinv76cbval)
sunflowerinv76cb.grid(row=76, column=18)
sunflowerinv77cb = Checkbutton(solrvr, variable=sunflowerinv77cbval)
sunflowerinv77cb.grid(row=77, column=18)
sunflowerinv78cb = Checkbutton(solrvr, variable=sunflowerinv78cbval)
sunflowerinv78cb.grid(row=78, column=18)
sunflowerinv79cb = Checkbutton(solrvr, variable=sunflowerinv79cbval)
sunflowerinv79cb.grid(row=79, column=18)
sunflowerinv80cb = Checkbutton(solrvr, variable=sunflowerinv80cbval)
sunflowerinv80cb.grid(row=80, column=18)


tedder1Label= Label(inv, text= "Tedder")
tedder1Label.grid(row=0, column=13, columnspan=2)

tedderinv1Label= Label(inv, text= "X")
tedderinv1Label.grid(row=1, column=13)

tedderinv2Label = Label(inv, text="X")
tedderinv2Label.grid(row=2, column=13)

# Tedder Inv 3
tedderinv3Label = Label(inv, text="X")
tedderinv3Label.grid(row=3, column=13)

# Tedder Inv 4
tedderinv4Label = Label(inv, text="X")
tedderinv4Label.grid(row=4, column=13)

# Tedder Inv 5
tedderinv5Label = Label(inv, text="X")
tedderinv5Label.grid(row=5, column=13)

# Tedder Inv 6
tedderinv6Label = Label(inv, text="X")
tedderinv6Label.grid(row=6, column=13)

# Tedder Inv 7
tedderinv7Label = Label(inv, text="X")
tedderinv7Label.grid(row=7, column=13)

# Tedder Inv 8
tedderinv8Label = Label(inv, text="X")
tedderinv8Label.grid(row=8, column=13)

# Tedder Inv 9
tedderinv9Label = Label(inv, text="X")
tedderinv9Label.grid(row=9, column=13)

# Tedder Inv 10
tedderinv10Label = Label(inv, text="X")
tedderinv10Label.grid(row=10, column=13)

# Tedder Inv 11
tedderinv11Label = Label(inv, text="X")
tedderinv11Label.grid(row=11, column=13)

# Tedder Inv 12
tedderinv12Label = Label(inv, text="X")
tedderinv12Label.grid(row=12, column=13)

# Tedder Inv 13
tedderinv13Label = Label(inv, text="X")
tedderinv13Label.grid(row=13, column=13)

# Tedder Inv 14
tedderinv14Label = Label(inv, text="X")
tedderinv14Label.grid(row=14, column=13)

# Tedder Inv 15
tedderinv15Label = Label(inv, text="X")
tedderinv15Label.grid(row=15, column=13)

# Tedder Inv 16
tedderinv16Label = Label(inv, text="X")
tedderinv16Label.grid(row=16, column=13)

tedderinv1cb = Checkbutton(inv, variable=tedderinv1cbval)
tedderinv1cb.grid(row=1, column=14)
tedderinv2cb = Checkbutton(inv, variable=tedderinv2cbval)
tedderinv2cb.grid(row=2, column=14)
tedderinv3cb = Checkbutton(inv, variable=tedderinv3cbval)
tedderinv3cb.grid(row=3, column=14)
tedderinv4cb = Checkbutton(inv, variable=tedderinv4cbval)
tedderinv4cb.grid(row=4, column=14)
tedderinv5cb = Checkbutton(inv, variable=tedderinv5cbval)
tedderinv5cb.grid(row=5, column=14)
tedderinv6cb = Checkbutton(inv, variable=tedderinv6cbval)
tedderinv6cb.grid(row=6, column=14)
tedderinv7cb = Checkbutton(inv, variable=tedderinv7cbval)
tedderinv7cb.grid(row=7, column=14)
tedderinv8cb = Checkbutton(inv, variable=tedderinv8cbval)
tedderinv8cb.grid(row=8, column=14)
tedderinv9cb = Checkbutton(inv, variable=tedderinv9cbval)
tedderinv9cb.grid(row=9, column=14)
tedderinv10cb = Checkbutton(inv, variable=tedderinv10cbval)
tedderinv10cb.grid(row=10, column=14)
tedderinv11cb = Checkbutton(inv, variable=tedderinv11cbval)
tedderinv11cb.grid(row=11, column=14)
tedderinv12cb = Checkbutton(inv, variable=tedderinv12cbval)
tedderinv12cb.grid(row=12, column=14)
tedderinv13cb = Checkbutton(inv, variable=tedderinv13cbval)
tedderinv13cb.grid(row=13, column=14)
tedderinv14cb = Checkbutton(inv, variable=tedderinv14cbval)
tedderinv14cb.grid(row=14, column=14)
tedderinv15cb = Checkbutton(inv, variable=tedderinv15cbval)
tedderinv15cb.grid(row=15, column=14)
tedderinv16cb = Checkbutton(inv, variable=tedderinv16cbval)
tedderinv16cb.grid(row=16, column=14)



thunderhead1Label= Label(inv, text= "Thunderhead")
thunderhead1Label.grid(row=0, column=15, columnspan=2)

thunderheadinv1Label= Label(inv, text= "X")
thunderheadinv1Label.grid(row= 1, column=15)

thunderheadinv2Label = Label(inv, text="X")
thunderheadinv2Label.grid(row=2, column=15)

# Thunderhead Inv 3
thunderheadinv3Label = Label(inv, text="X")
thunderheadinv3Label.grid(row=3, column=15)

# Thunderhead Inv 4
thunderheadinv4Label = Label(inv, text="X")
thunderheadinv4Label.grid(row=4, column=15)

# Thunderhead Inv 5
thunderheadinv5Label = Label(inv, text="X")
thunderheadinv5Label.grid(row=5, column=15)

# Thunderhead Inv 6
thunderheadinv6Label = Label(inv, text="X")
thunderheadinv6Label.grid(row=6, column=15)

# Thunderhead Inv 7
thunderheadinv7Label = Label(inv, text="X")
thunderheadinv7Label.grid(row=7, column=15)

# Thunderhead Inv 8
thunderheadinv8Label = Label(inv, text="X")
thunderheadinv8Label.grid(row=8, column=15)

# Thunderhead Inv 9
thunderheadinv9Label = Label(inv, text="X")
thunderheadinv9Label.grid(row=9, column=15)

# Thunderhead Inv 10
thunderheadinv10Label = Label(inv, text="X")
thunderheadinv10Label.grid(row=10, column=15)

# Thunderhead Inv 11
thunderheadinv11Label = Label(inv, text="X")
thunderheadinv11Label.grid(row=11, column=15)

# Thunderhead Inv 12
thunderheadinv12Label = Label(inv, text="X")
thunderheadinv12Label.grid(row=12, column=15)

# Thunderhead Inv 13
thunderheadinv13Label = Label(inv, text="X")
thunderheadinv13Label.grid(row=13, column=15)

# Thunderhead Inv 14
thunderheadinv14Label = Label(inv, text="X")
thunderheadinv14Label.grid(row=14, column=15)

# Thunderhead Inv 15
thunderheadinv15Label = Label(inv, text="X")
thunderheadinv15Label.grid(row=15, column=15)

# Thunderhead Inv 16
thunderheadinv16Label = Label(inv, text="X")
thunderheadinv16Label.grid(row=16, column=15)

thunderheadinv1cb = Checkbutton(inv, variable=thunderheadinv1cbval)
thunderheadinv1cb.grid(row=1, column=16)
thunderheadinv2cb = Checkbutton(inv, variable=thunderheadinv2cbval)
thunderheadinv2cb.grid(row=2, column=16)
thunderheadinv3cb = Checkbutton(inv, variable=thunderheadinv3cbval)
thunderheadinv3cb.grid(row=3, column=16)
thunderheadinv4cb = Checkbutton(inv, variable=thunderheadinv4cbval)
thunderheadinv4cb.grid(row=4, column=16)
thunderheadinv5cb = Checkbutton(inv, variable=thunderheadinv5cbval)
thunderheadinv5cb.grid(row=5, column=16)
thunderheadinv6cb = Checkbutton(inv, variable=thunderheadinv6cbval)
thunderheadinv6cb.grid(row=6, column=16)
thunderheadinv7cb = Checkbutton(inv, variable=thunderheadinv7cbval)
thunderheadinv7cb.grid(row=7, column=16)
thunderheadinv8cb = Checkbutton(inv, variable=thunderheadinv8cbval)
thunderheadinv8cb.grid(row=8, column=16)
thunderheadinv9cb = Checkbutton(inv, variable=thunderheadinv9cbval)
thunderheadinv9cb.grid(row=9, column=16)
thunderheadinv10cb = Checkbutton(inv, variable=thunderheadinv10cbval)
thunderheadinv10cb.grid(row=10, column=16)
thunderheadinv11cb = Checkbutton(inv, variable=thunderheadinv11cbval)
thunderheadinv11cb.grid(row=11, column=16)
thunderheadinv12cb = Checkbutton(inv, variable=thunderheadinv12cbval)
thunderheadinv12cb.grid(row=12, column=16)
thunderheadinv13cb = Checkbutton(inv, variable=thunderheadinv13cbval)
thunderheadinv13cb.grid(row=13, column=16)
thunderheadinv14cb = Checkbutton(inv, variable=thunderheadinv14cbval)
thunderheadinv14cb.grid(row=14, column=16)
thunderheadinv15cb = Checkbutton(inv, variable=thunderheadinv15cbval)
thunderheadinv15cb.grid(row=15, column=16)
thunderheadinv16cb = Checkbutton(inv, variable=thunderheadinv16cbval)
thunderheadinv16cb.grid(row=16, column=16)

upson1Label= Label(solrvr, text= "Upson")
upson1Label.grid(row=0, column=19, columnspan=2)

upsoninv1Label= Label(solrvr, text="X")
upsoninv1Label.grid(row= 1, column=19)
upsoninv2Label = Label(solrvr, text="X")
upsoninv2Label.grid(row=2, column=19)

# Upson Inv 3
upsoninv3Label = Label(solrvr, text="X")
upsoninv3Label.grid(row=3, column=19)

# Upson Inv 4
upsoninv4Label = Label(solrvr, text="X")
upsoninv4Label.grid(row=4, column=19)

# Upson Inv 5
upsoninv5Label = Label(solrvr, text="X")
upsoninv5Label.grid(row=5, column=19)

# Upson Inv 6
upsoninv6Label = Label(solrvr, text="X")
upsoninv6Label.grid(row=6, column=19)

# Upson Inv 7
upsoninv7Label = Label(solrvr, text="X")
upsoninv7Label.grid(row=7, column=19)

# Upson Inv 8
upsoninv8Label = Label(solrvr, text="X")
upsoninv8Label.grid(row=8, column=19)

# Upson Inv 9
upsoninv9Label = Label(solrvr, text="X")
upsoninv9Label.grid(row=9, column=19)

# Upson Inv 10
upsoninv10Label = Label(solrvr, text="X")
upsoninv10Label.grid(row=10, column=19)

# Upson Inv 11
upsoninv11Label = Label(solrvr, text="X")
upsoninv11Label.grid(row=11, column=19)

# Upson Inv 12
upsoninv12Label = Label(solrvr, text="X")
upsoninv12Label.grid(row=12, column=19)

# Upson Inv 13
upsoninv13Label = Label(solrvr, text="X")
upsoninv13Label.grid(row=13, column=19)

# Upson Inv 14
upsoninv14Label = Label(solrvr, text="X")
upsoninv14Label.grid(row=14, column=19)

# Upson Inv 15
upsoninv15Label = Label(solrvr, text="X")
upsoninv15Label.grid(row=15, column=19)

# Upson Inv 16
upsoninv16Label = Label(solrvr, text="X")
upsoninv16Label.grid(row=16, column=19)

# Upson Inv 17
upsoninv17Label = Label(solrvr, text="X")
upsoninv17Label.grid(row=17, column=19)

# Upson Inv 18
upsoninv18Label = Label(solrvr, text="X")
upsoninv18Label.grid(row=18, column=19)

# Upson Inv 19
upsoninv19Label = Label(solrvr, text="X")
upsoninv19Label.grid(row=19, column=19)

# Upson Inv 20
upsoninv20Label = Label(solrvr, text="X")
upsoninv20Label.grid(row=20, column=19)
# Upson Inv 21
upsoninv21Label = Label(solrvr, text="X")
upsoninv21Label.grid(row=21, column=19)

# Upson Inv 22
upsoninv22Label = Label(solrvr, text="X")
upsoninv22Label.grid(row=22, column=19)

# Upson Inv 23
upsoninv23Label = Label(solrvr, text="X")
upsoninv23Label.grid(row=23, column=19)

# Upson Inv 24
upsoninv24Label = Label(solrvr, text="X")
upsoninv24Label.grid(row=24, column=19)

upsoninv1cb = Checkbutton(solrvr, variable=upsoninv1cbval)
upsoninv1cb.grid(row=1, column=20)
upsoninv2cb = Checkbutton(solrvr, variable=upsoninv2cbval)
upsoninv2cb.grid(row=2, column=20)
upsoninv3cb = Checkbutton(solrvr, variable=upsoninv3cbval)
upsoninv3cb.grid(row=3, column=20)
upsoninv4cb = Checkbutton(solrvr, variable=upsoninv4cbval)
upsoninv4cb.grid(row=4, column=20)
upsoninv5cb = Checkbutton(solrvr, variable=upsoninv5cbval)
upsoninv5cb.grid(row=5, column=20)
upsoninv6cb = Checkbutton(solrvr, variable=upsoninv6cbval)
upsoninv6cb.grid(row=6, column=20)
upsoninv7cb = Checkbutton(solrvr, variable=upsoninv7cbval)
upsoninv7cb.grid(row=7, column=20)
upsoninv8cb = Checkbutton(solrvr, variable=upsoninv8cbval)
upsoninv8cb.grid(row=8, column=20)
upsoninv9cb = Checkbutton(solrvr, variable=upsoninv9cbval)
upsoninv9cb.grid(row=9, column=20)
upsoninv10cb = Checkbutton(solrvr, variable=upsoninv10cbval)
upsoninv10cb.grid(row=10, column=20)
upsoninv11cb = Checkbutton(solrvr, variable=upsoninv11cbval)
upsoninv11cb.grid(row=11, column=20)
upsoninv12cb = Checkbutton(solrvr, variable=upsoninv12cbval)
upsoninv12cb.grid(row=12, column=20)
upsoninv13cb = Checkbutton(solrvr, variable=upsoninv13cbval)
upsoninv13cb.grid(row=13, column=20)
upsoninv14cb = Checkbutton(solrvr, variable=upsoninv14cbval)
upsoninv14cb.grid(row=14, column=20)
upsoninv15cb = Checkbutton(solrvr, variable=upsoninv15cbval)
upsoninv15cb.grid(row=15, column=20)
upsoninv16cb = Checkbutton(solrvr, variable=upsoninv16cbval)
upsoninv16cb.grid(row=16, column=20)
upsoninv17cb = Checkbutton(solrvr, variable=upsoninv17cbval)
upsoninv17cb.grid(row=17, column=20)
upsoninv18cb = Checkbutton(solrvr, variable=upsoninv18cbval)
upsoninv18cb.grid(row=18, column=20)
upsoninv19cb = Checkbutton(solrvr, variable=upsoninv19cbval)
upsoninv19cb.grid(row=19, column=20)
upsoninv20cb = Checkbutton(solrvr, variable=upsoninv20cbval)
upsoninv20cb.grid(row=20, column=20)
upsoninv21cb = Checkbutton(solrvr, variable=upsoninv21cbval)
upsoninv21cb.grid(row=21, column=20)
upsoninv22cb = Checkbutton(solrvr, variable=upsoninv22cbval)
upsoninv22cb.grid(row=22, column=20)
upsoninv23cb = Checkbutton(solrvr, variable=upsoninv23cbval)
upsoninv23cb.grid(row=23, column=20)
upsoninv24cb = Checkbutton(solrvr, variable=upsoninv24cbval)
upsoninv24cb.grid(row=24, column=20)



vanburen1Label= Label(inv, text= "Van Buren")
vanburen1Label.grid(row=0, column=17, columnspan=2)

vanbureninv1Label= Label(inv, text= "X")
vanbureninv1Label.grid(row=1, column=17)

vanbureninv2Label = Label(inv, text="X")
vanbureninv2Label.grid(row=2, column=17)

# Van Buren Inv 3
vanbureninv3Label = Label(inv, text="X")
vanbureninv3Label.grid(row=3, column=17)

# Van Buren Inv 4
vanbureninv4Label = Label(inv, text="X")
vanbureninv4Label.grid(row=4, column=17)

# Van Buren Inv 5
vanbureninv5Label = Label(inv, text="X")
vanbureninv5Label.grid(row=5, column=17)

# Van Buren Inv 6
vanbureninv6Label = Label(inv, text="X")
vanbureninv6Label.grid(row=6, column=17)

# Van Buren Inv 7
vanbureninv7Label = Label(inv, text="X")
vanbureninv7Label.grid(row=7, column=17)

# Van Buren Inv 8
vanbureninv8Label = Label(inv, text="X")
vanbureninv8Label.grid(row=8, column=17)

# Van Buren Inv 9
vanbureninv9Label = Label(inv, text="X")
vanbureninv9Label.grid(row=9, column=17)

# Van Buren Inv 10
vanbureninv10Label = Label(inv, text="X")
vanbureninv10Label.grid(row=10, column=17)

# Van Buren Inv 11
vanbureninv11Label = Label(inv, text="X")
vanbureninv11Label.grid(row=11, column=17)

# Van Buren Inv 12
vanbureninv12Label = Label(inv, text="X")
vanbureninv12Label.grid(row=12, column=17)

# Van Buren Inv 13
vanbureninv13Label = Label(inv, text="X")
vanbureninv13Label.grid(row=13, column=17)

# Van Buren Inv 14
vanbureninv14Label = Label(inv, text="X")
vanbureninv14Label.grid(row=14, column=17)

# Van Buren Inv 15
vanbureninv15Label = Label(inv, text="X")
vanbureninv15Label.grid(row=15, column=17)

# Van Buren Inv 16
vanbureninv16Label = Label(inv, text="X")
vanbureninv16Label.grid(row=16, column=17)

# Van Buren Inv 17
vanbureninv17Label = Label(inv, text="X")
vanbureninv17Label.grid(row=17, column=17)

vanbureninv1cb = Checkbutton(inv, variable=vanbureninv1cbval)
vanbureninv1cb.grid(row=1, column=18)
vanbureninv2cb = Checkbutton(inv, variable=vanbureninv2cbval)
vanbureninv2cb.grid(row=2, column=18)
vanbureninv3cb = Checkbutton(inv, variable=vanbureninv3cbval)
vanbureninv3cb.grid(row=3, column=18)
vanbureninv4cb = Checkbutton(inv, variable=vanbureninv4cbval)
vanbureninv4cb.grid(row=4, column=18)
vanbureninv5cb = Checkbutton(inv, variable=vanbureninv5cbval)
vanbureninv5cb.grid(row=5, column=18)
vanbureninv6cb = Checkbutton(inv, variable=vanbureninv6cbval)
vanbureninv6cb.grid(row=6, column=18)
vanbureninv7cb = Checkbutton(inv, variable=vanbureninv7cbval)
vanbureninv7cb.grid(row=7, column=18)
vanbureninv8cb = Checkbutton(inv, variable=vanbureninv8cbval)
vanbureninv8cb.grid(row=8, column=18)
vanbureninv9cb = Checkbutton(inv, variable=vanbureninv9cbval)
vanbureninv9cb.grid(row=9, column=18)
vanbureninv10cb = Checkbutton(inv, variable=vanbureninv10cbval)
vanbureninv10cb.grid(row=10, column=18)
vanbureninv11cb = Checkbutton(inv, variable=vanbureninv11cbval)
vanbureninv11cb.grid(row=11, column=18)
vanbureninv12cb = Checkbutton(inv, variable=vanbureninv12cbval)
vanbureninv12cb.grid(row=12, column=18)
vanbureninv13cb = Checkbutton(inv, variable=vanbureninv13cbval)
vanbureninv13cb.grid(row=13, column=18)
vanbureninv14cb = Checkbutton(inv, variable=vanbureninv14cbval)
vanbureninv14cb.grid(row=14, column=18)
vanbureninv15cb = Checkbutton(inv, variable=vanbureninv15cbval)
vanbureninv15cb.grid(row=15, column=18)
vanbureninv16cb = Checkbutton(inv, variable=vanbureninv16cbval)
vanbureninv16cb.grid(row=16, column=18)
vanbureninv17cb = Checkbutton(inv, variable=vanbureninv17cbval)
vanbureninv17cb.grid(row=17, column=18)


violet1Label= Label(narenco, text= "Violet")
violet1Label.grid(row=0, column=17, columnspan=2)

violetinv1Label= Label(narenco, text= "X")
violetinv1Label.grid(row=1, column=17)
violetinv2Label= Label(narenco, text= "X")
violetinv2Label.grid(row=2, column=17)

violetinv1cb = Checkbutton(narenco, variable=violetinv1cbval)
violetinv1cb.grid(row=1, column=18)
violetinv2cb = Checkbutton(narenco, variable=violetinv2cbval)
violetinv2cb.grid(row=2, column=18)

warbler1Label= Label(solrvr, text= "Warbler")
warbler1Label.grid(row=0, column=21, columnspan=2)

warblerinv1Label= Label(solrvr, text= "X")
warblerinv1Label.grid(row=1, column=21)

warblerinv2Label = Label(solrvr, text="X")
warblerinv2Label.grid(row=2, column=21)

# Warbler Inv 3
warblerinv3Label = Label(solrvr, text="X")
warblerinv3Label.grid(row=3, column=21)

# Warbler Inv 4
warblerinv4Label = Label(solrvr, text="X")
warblerinv4Label.grid(row=4, column=21)

# Warbler Inv 5
warblerinv5Label = Label(solrvr, text="X")
warblerinv5Label.grid(row=5, column=21)

# Warbler Inv 6
warblerinv6Label = Label(solrvr, text="X")
warblerinv6Label.grid(row=6, column=21)

# Warbler Inv 7
warblerinv7Label = Label(solrvr, text="X")
warblerinv7Label.grid(row=7, column=21)

# Warbler Inv 8
warblerinv8Label = Label(solrvr, text="X")
warblerinv8Label.grid(row=8, column=21)

# Warbler Inv 9
warblerinv9Label = Label(solrvr, text="X")
warblerinv9Label.grid(row=9, column=21)

# Warbler Inv 10
warblerinv10Label = Label(solrvr, text="X")
warblerinv10Label.grid(row=10, column=21)

# Warbler Inv 11
warblerinv11Label = Label(solrvr, text="X")
warblerinv11Label.grid(row=11, column=21)

# Warbler Inv 12
warblerinv12Label = Label(solrvr, text="X")
warblerinv12Label.grid(row=12, column=21)

# Warbler Inv 13
warblerinv13Label = Label(solrvr, text="X")
warblerinv13Label.grid(row=13, column=21)

# Warbler Inv 14
warblerinv14Label = Label(solrvr, text="X")
warblerinv14Label.grid(row=14, column=21)

# Warbler Inv 15
warblerinv15Label = Label(solrvr, text="X")
warblerinv15Label.grid(row=15, column=21)

# Warbler Inv 16
warblerinv16Label = Label(solrvr, text="X")
warblerinv16Label.grid(row=16, column=21)

# Warbler Inv 17
warblerinv17Label = Label(solrvr, text="X")
warblerinv17Label.grid(row=17, column=21)

# Warbler Inv 18
warblerinv18Label = Label(solrvr, text="X")
warblerinv18Label.grid(row=18, column=21)

# Warbler Inv 19
warblerinv19Label = Label(solrvr, text="X")
warblerinv19Label.grid(row=19, column=21)

# Warbler Inv 20
warblerinv20Label = Label(solrvr, text="X")
warblerinv20Label.grid(row=20, column=21)

# Warbler Inv 21
warblerinv21Label = Label(solrvr, text="X")
warblerinv21Label.grid(row=21, column=21)

# Warbler Inv 22
warblerinv22Label = Label(solrvr, text="X")
warblerinv22Label.grid(row=22, column=21)

# Warbler Inv 23
warblerinv23Label = Label(solrvr, text="X")
warblerinv23Label.grid(row=23, column=21)

# Warbler Inv 24
warblerinv24Label = Label(solrvr, text="X")
warblerinv24Label.grid(row=24, column=21)

# Warbler Inv 25
warblerinv25Label = Label(solrvr, text="X")
warblerinv25Label.grid(row=25, column=21)

# Warbler Inv 26
warblerinv26Label = Label(solrvr, text="X")
warblerinv26Label.grid(row=26, column=21)

# Warbler Inv 27
warblerinv27Label = Label(solrvr, text="X")
warblerinv27Label.grid(row=27, column=21)

# Warbler Inv 28
warblerinv28Label = Label(solrvr, text="X")
warblerinv28Label.grid(row=28, column=21)

# Warbler Inv 29
warblerinv29Label = Label(solrvr, text="X")
warblerinv29Label.grid(row=29, column=21)

# Warbler Inv 30
warblerinv30Label = Label(solrvr, text="X")
warblerinv30Label.grid(row=30, column=21)

# Warbler Inv 31
warblerinv31Label = Label(solrvr, text="X")
warblerinv31Label.grid(row=31, column=21)

# Warbler Inv 32
warblerinv32Label = Label(solrvr, text="X")
warblerinv32Label.grid(row=32, column=21)


warblerinv1cb = Checkbutton(solrvr, variable=warblerinv1cbval)
warblerinv1cb.grid(row=1, column=22)
warblerinv2cb = Checkbutton(solrvr, variable=warblerinv2cbval)
warblerinv2cb.grid(row=2, column=22)
warblerinv3cb = Checkbutton(solrvr, variable=warblerinv3cbval)
warblerinv3cb.grid(row=3, column=22)
warblerinv4cb = Checkbutton(solrvr, variable=warblerinv4cbval)
warblerinv4cb.grid(row=4, column=22)
warblerinv5cb = Checkbutton(solrvr, variable=warblerinv5cbval)
warblerinv5cb.grid(row=5, column=22)
warblerinv6cb = Checkbutton(solrvr, variable=warblerinv6cbval)
warblerinv6cb.grid(row=6, column=22)
warblerinv7cb = Checkbutton(solrvr, variable=warblerinv7cbval)
warblerinv7cb.grid(row=7, column=22)
warblerinv8cb = Checkbutton(solrvr, variable=warblerinv8cbval)
warblerinv8cb.grid(row=8, column=22)
warblerinv9cb = Checkbutton(solrvr, variable=warblerinv9cbval)
warblerinv9cb.grid(row=9, column=22)
warblerinv10cb = Checkbutton(solrvr, variable=warblerinv10cbval)
warblerinv10cb.grid(row=10, column=22)
warblerinv11cb = Checkbutton(solrvr, variable=warblerinv11cbval)
warblerinv11cb.grid(row=11, column=22)
warblerinv12cb = Checkbutton(solrvr, variable=warblerinv12cbval)
warblerinv12cb.grid(row=12, column=22)
warblerinv13cb = Checkbutton(solrvr, variable=warblerinv13cbval)
warblerinv13cb.grid(row=13, column=22)
warblerinv14cb = Checkbutton(solrvr, variable=warblerinv14cbval)
warblerinv14cb.grid(row=14, column=22)
warblerinv15cb = Checkbutton(solrvr, variable=warblerinv15cbval)
warblerinv15cb.grid(row=15, column=22)
warblerinv16cb = Checkbutton(solrvr, variable=warblerinv16cbval)
warblerinv16cb.grid(row=16, column=22)
warblerinv17cb = Checkbutton(solrvr, variable=warblerinv17cbval)
warblerinv17cb.grid(row=17, column=22)
warblerinv18cb = Checkbutton(solrvr, variable=warblerinv18cbval)
warblerinv18cb.grid(row=18, column=22)
warblerinv19cb = Checkbutton(solrvr, variable=warblerinv19cbval)
warblerinv19cb.grid(row=19, column=22)
warblerinv20cb = Checkbutton(solrvr, variable=warblerinv20cbval)
warblerinv20cb.grid(row=20, column=22)
warblerinv21cb = Checkbutton(solrvr, variable=warblerinv21cbval)
warblerinv21cb.grid(row=21, column=22)
warblerinv22cb = Checkbutton(solrvr, variable=warblerinv22cbval)
warblerinv22cb.grid(row=22, column=22)
warblerinv23cb = Checkbutton(solrvr, variable=warblerinv23cbval)
warblerinv23cb.grid(row=23, column=22)
warblerinv24cb = Checkbutton(solrvr, variable=warblerinv24cbval)
warblerinv24cb.grid(row=24, column=22)
warblerinv25cb = Checkbutton(solrvr, variable=warblerinv25cbval)
warblerinv25cb.grid(row=25, column=22)
warblerinv26cb = Checkbutton(solrvr, variable=warblerinv26cbval)
warblerinv26cb.grid(row=26, column=22)
warblerinv27cb = Checkbutton(solrvr, variable=warblerinv27cbval)
warblerinv27cb.grid(row=27, column=22)
warblerinv28cb = Checkbutton(solrvr, variable=warblerinv28cbval)
warblerinv28cb.grid(row=28, column=22)
warblerinv29cb = Checkbutton(solrvr, variable=warblerinv29cbval)
warblerinv29cb.grid(row=29, column=22)
warblerinv30cb = Checkbutton(solrvr, variable=warblerinv30cbval)
warblerinv30cb.grid(row=30, column=22)
warblerinv31cb = Checkbutton(solrvr, variable=warblerinv31cbval)
warblerinv31cb.grid(row=31, column=22)
warblerinv32cb = Checkbutton(solrvr, variable=warblerinv32cbval)
warblerinv32cb.grid(row=32, column=22)



washington1Label= Label(solrvr, text= "Washington")
washington1Label.grid(row=0, column=23, columnspan=2)

washingtoninv1Label= Label(solrvr, text= "X")
washingtoninv1Label.grid(row=1, column=23)

washingtoninv2Label = Label(solrvr, text="X")
washingtoninv2Label.grid(row=2, column=23)

# Washington Inv 3
washingtoninv3Label = Label(solrvr, text="X")
washingtoninv3Label.grid(row=3, column=23)

# Washington Inv 4
washingtoninv4Label = Label(solrvr, text="X")
washingtoninv4Label.grid(row=4, column=23)

# Washington Inv 5
washingtoninv5Label = Label(solrvr, text="X")
washingtoninv5Label.grid(row=5, column=23)

# Washington Inv 6
washingtoninv6Label = Label(solrvr, text="X")
washingtoninv6Label.grid(row=6, column=23)

# Washington Inv 7
washingtoninv7Label = Label(solrvr, text="X")
washingtoninv7Label.grid(row=7, column=23)

# Washington Inv 8
washingtoninv8Label = Label(solrvr, text="X")
washingtoninv8Label.grid(row=8, column=23)

# Washington Inv 9
washingtoninv9Label = Label(solrvr, text="X")
washingtoninv9Label.grid(row=9, column=23)

# Washington Inv 10
washingtoninv10Label = Label(solrvr, text="X")
washingtoninv10Label.grid(row=10, column=23)

# Washington Inv 11
washingtoninv11Label = Label(solrvr, text="X")
washingtoninv11Label.grid(row=11, column=23)

# Washington Inv 12
washingtoninv12Label = Label(solrvr, text="X")
washingtoninv12Label.grid(row=12, column=23)

# Washington Inv 13
washingtoninv13Label = Label(solrvr, text="X")
washingtoninv13Label.grid(row=13, column=23)

# Washington Inv 14
washingtoninv14Label = Label(solrvr, text="X")
washingtoninv14Label.grid(row=14, column=23)

# Washington Inv 15
washingtoninv15Label = Label(solrvr, text="X")
washingtoninv15Label.grid(row=15, column=23)

# Washington Inv 16
washingtoninv16Label = Label(solrvr, text="X")
washingtoninv16Label.grid(row=16, column=23)

# Washington Inv 17
washingtoninv17Label = Label(solrvr, text="X")
washingtoninv17Label.grid(row=17, column=23)

# Washington Inv 18
washingtoninv18Label = Label(solrvr, text="X")
washingtoninv18Label.grid(row=18, column=23)

# Washington Inv 19
washingtoninv19Label = Label(solrvr, text="X")
washingtoninv19Label.grid(row=19, column=23)

# Washington Inv 20
washingtoninv20Label = Label(solrvr, text="X")
washingtoninv20Label.grid(row=20, column=23)

# Washington Inv 21
washingtoninv21Label = Label(solrvr, text="X")
washingtoninv21Label.grid(row=21, column=23)

# Washington Inv 22
washingtoninv22Label = Label(solrvr, text="X")
washingtoninv22Label.grid(row=22, column=23)

# Washington Inv 23
washingtoninv23Label = Label(solrvr, text="X")
washingtoninv23Label.grid(row=23, column=23)

# Washington Inv 24
washingtoninv24Label = Label(solrvr, text="X")
washingtoninv24Label.grid(row=24, column=23)

# Washington Inv 25
washingtoninv25Label = Label(solrvr, text="X")
washingtoninv25Label.grid(row=25, column=23)

# Washington Inv 26
washingtoninv26Label = Label(solrvr, text="X")
washingtoninv26Label.grid(row=26, column=23)

# Washington Inv 27
washingtoninv27Label = Label(solrvr, text="X")
washingtoninv27Label.grid(row=27, column=23)

# Washington Inv 28
washingtoninv28Label = Label(solrvr, text="X")
washingtoninv28Label.grid(row=28, column=23)

# Washington Inv 29
washingtoninv29Label = Label(solrvr, text="X")
washingtoninv29Label.grid(row=29, column=23)

# Washington Inv 30
washingtoninv30Label = Label(solrvr, text="X")
washingtoninv30Label.grid(row=30, column=23)

# Washington Inv 31
washingtoninv31Label = Label(solrvr, text="X")
washingtoninv31Label.grid(row=31, column=23)

# Washington Inv 32
washingtoninv32Label = Label(solrvr, text="X")
washingtoninv32Label.grid(row=32, column=23)

# Washington Inv 33
washingtoninv33Label = Label(solrvr, text="X")
washingtoninv33Label.grid(row=33, column=23)

# Washington Inv 34
washingtoninv34Label = Label(solrvr, text="X")
washingtoninv34Label.grid(row=34, column=23)

# Washington Inv 35
washingtoninv35Label = Label(solrvr, text="X")
washingtoninv35Label.grid(row=35, column=23)

# Washington Inv 36
washingtoninv36Label = Label(solrvr, text="X")
washingtoninv36Label.grid(row=36, column=23)

# Washington Inv 37
washingtoninv37Label = Label(solrvr, text="X")
washingtoninv37Label.grid(row=37, column=23)

# Washington Inv 38
washingtoninv38Label = Label(solrvr, text="X")
washingtoninv38Label.grid(row=38, column=23)

# Washington Inv 39
washingtoninv39Label = Label(solrvr, text="X")
washingtoninv39Label.grid(row=39, column=23)

# Washington Inv 40
washingtoninv40Label = Label(solrvr, text="X")
washingtoninv40Label.grid(row=40, column=23)

washingtoninv1cb = Checkbutton(solrvr, variable=washingtoninv1cbval)
washingtoninv1cb.grid(row=1, column=24)
washingtoninv2cb = Checkbutton(solrvr, variable=washingtoninv2cbval)
washingtoninv2cb.grid(row=2, column=24)
washingtoninv3cb = Checkbutton(solrvr, variable=washingtoninv3cbval)
washingtoninv3cb.grid(row=3, column=24)
washingtoninv4cb = Checkbutton(solrvr, variable=washingtoninv4cbval)
washingtoninv4cb.grid(row=4, column=24)
washingtoninv5cb = Checkbutton(solrvr, variable=washingtoninv5cbval)
washingtoninv5cb.grid(row=5, column=24)
washingtoninv6cb = Checkbutton(solrvr, variable=washingtoninv6cbval)
washingtoninv6cb.grid(row=6, column=24)
washingtoninv7cb = Checkbutton(solrvr, variable=washingtoninv7cbval)
washingtoninv7cb.grid(row=7, column=24)
washingtoninv8cb = Checkbutton(solrvr, variable=washingtoninv8cbval)
washingtoninv8cb.grid(row=8, column=24)
washingtoninv9cb = Checkbutton(solrvr, variable=washingtoninv9cbval)
washingtoninv9cb.grid(row=9, column=24)
washingtoninv10cb = Checkbutton(solrvr, variable=washingtoninv10cbval)
washingtoninv10cb.grid(row=10, column=24)
washingtoninv11cb = Checkbutton(solrvr, variable=washingtoninv11cbval)
washingtoninv11cb.grid(row=11, column=24)
washingtoninv12cb = Checkbutton(solrvr, variable=washingtoninv12cbval)
washingtoninv12cb.grid(row=12, column=24)
washingtoninv13cb = Checkbutton(solrvr, variable=washingtoninv13cbval)
washingtoninv13cb.grid(row=13, column=24)
washingtoninv14cb = Checkbutton(solrvr, variable=washingtoninv14cbval)
washingtoninv14cb.grid(row=14, column=24)
washingtoninv15cb = Checkbutton(solrvr, variable=washingtoninv15cbval)
washingtoninv15cb.grid(row=15, column=24)
washingtoninv16cb = Checkbutton(solrvr, variable=washingtoninv16cbval)
washingtoninv16cb.grid(row=16, column=24)
washingtoninv17cb = Checkbutton(solrvr, variable=washingtoninv17cbval)
washingtoninv17cb.grid(row=17, column=24)
washingtoninv18cb = Checkbutton(solrvr, variable=washingtoninv18cbval)
washingtoninv18cb.grid(row=18, column=24)
washingtoninv19cb = Checkbutton(solrvr, variable=washingtoninv19cbval)
washingtoninv19cb.grid(row=19, column=24)
washingtoninv20cb = Checkbutton(solrvr, variable=washingtoninv20cbval)
washingtoninv20cb.grid(row=20, column=24)
washingtoninv21cb = Checkbutton(solrvr, variable=washingtoninv21cbval)
washingtoninv21cb.grid(row=21, column=24)
washingtoninv22cb = Checkbutton(solrvr, variable=washingtoninv22cbval)
washingtoninv22cb.grid(row=22, column=24)
washingtoninv23cb = Checkbutton(solrvr, variable=washingtoninv23cbval)
washingtoninv23cb.grid(row=23, column=24)
washingtoninv24cb = Checkbutton(solrvr, variable=washingtoninv24cbval)
washingtoninv24cb.grid(row=24, column=24)
washingtoninv25cb = Checkbutton(solrvr, variable=washingtoninv25cbval)
washingtoninv25cb.grid(row=25, column=24)
washingtoninv26cb = Checkbutton(solrvr, variable=washingtoninv26cbval)
washingtoninv26cb.grid(row=26, column=24)
washingtoninv27cb = Checkbutton(solrvr, variable=washingtoninv27cbval)
washingtoninv27cb.grid(row=27, column=24)
washingtoninv28cb = Checkbutton(solrvr, variable=washingtoninv28cbval)
washingtoninv28cb.grid(row=28, column=24)
washingtoninv29cb = Checkbutton(solrvr, variable=washingtoninv29cbval)
washingtoninv29cb.grid(row=29, column=24)
washingtoninv30cb = Checkbutton(solrvr, variable=washingtoninv30cbval)
washingtoninv30cb.grid(row=30, column=24)
washingtoninv31cb = Checkbutton(solrvr, variable=washingtoninv31cbval)
washingtoninv31cb.grid(row=31, column=24)
washingtoninv32cb = Checkbutton(solrvr, variable=washingtoninv32cbval)
washingtoninv32cb.grid(row=32, column=24)
washingtoninv33cb = Checkbutton(solrvr, variable=washingtoninv33cbval)
washingtoninv33cb.grid(row=33, column=24)
washingtoninv34cb = Checkbutton(solrvr, variable=washingtoninv34cbval)
washingtoninv34cb.grid(row=34, column=24)
washingtoninv35cb = Checkbutton(solrvr, variable=washingtoninv35cbval)
washingtoninv35cb.grid(row=35, column=24)
washingtoninv36cb = Checkbutton(solrvr, variable=washingtoninv36cbval)
washingtoninv36cb.grid(row=36, column=24)
washingtoninv37cb = Checkbutton(solrvr, variable=washingtoninv37cbval)
washingtoninv37cb.grid(row=37, column=24)
washingtoninv38cb = Checkbutton(solrvr, variable=washingtoninv38cbval)
washingtoninv38cb.grid(row=38, column=24)
washingtoninv39cb = Checkbutton(solrvr, variable=washingtoninv39cbval)
washingtoninv39cb.grid(row=39, column=24)
washingtoninv40cb = Checkbutton(solrvr, variable=washingtoninv40cbval)
washingtoninv40cb.grid(row=40, column=24)




wayne11Label= Label(soltage, text= "Wayne 1")
wayne11Label.grid(row=0, column=5, columnspan=2)

wayne1inv1Label= Label(soltage, text= "X")
wayne1inv1Label.grid(row=1, column=5)

wayne1inv2Label = Label(soltage, text="X")
wayne1inv2Label.grid(row=2, column=5)

# Wayne1 Inv 3
wayne1inv3Label = Label(soltage, text="X")
wayne1inv3Label.grid(row=3, column=5)

# Wayne1 Inv 4
wayne1inv4Label = Label(soltage, text="X")
wayne1inv4Label.grid(row=4, column=5)

wayne1inv1cb = Checkbutton(soltage, variable=wayne1inv1cbval)
wayne1inv1cb.grid(row=1, column= 6)
wayne1inv2cb = Checkbutton(soltage, variable=wayne1inv2cbval)
wayne1inv2cb.grid(row=2, column= 6)
wayne1inv3cb = Checkbutton(soltage, variable=wayne1inv3cbval)
wayne1inv3cb.grid(row=3, column= 6)
wayne1inv4cb = Checkbutton(soltage, variable=wayne1inv4cbval)
wayne1inv4cb.grid(row=4, column= 6)

wayne21Label= Label(soltage, text= "Wayne 2")
wayne21Label.grid(row=0, column=7, columnspan=2)

wayne2inv1Label= Label(soltage, text= "X")
wayne2inv1Label.grid(row=1, column =7)
# Wayne2 Inv 2
wayne2inv2Label = Label(soltage, text="X")
wayne2inv2Label.grid(row=2, column=7)

# Wayne2 Inv 3
wayne2inv3Label = Label(soltage, text="X")
wayne2inv3Label.grid(row=3, column=7)

# Wayne2 Inv 4
wayne2inv4Label = Label(soltage, text="X")
wayne2inv4Label.grid(row=4, column=7)

wayne2inv1cb = Checkbutton(soltage, variable=wayne2inv1cbval)
wayne2inv1cb.grid(row=1, column= 8)
wayne2inv2cb = Checkbutton(soltage, variable=wayne2inv2cbval)
wayne2inv2cb.grid(row=2, column= 8)
wayne2inv3cb = Checkbutton(soltage, variable=wayne2inv3cbval)
wayne2inv3cb.grid(row=3, column= 8)
wayne2inv4cb = Checkbutton(soltage, variable=wayne2inv4cbval)
wayne2inv4cb.grid(row=4, column= 8)

wayne31Label= Label(soltage, text= "Wayne 3")
wayne31Label.grid(row=0, column=9, columnspan=2)

wayne3inv1Label= Label(soltage, text= "X")
wayne3inv1Label.grid(row=1, column =9)

wayne3inv2Label = Label(soltage, text="X")
wayne3inv2Label.grid(row=2, column=9)

# Wayne3 Inv 3
wayne3inv3Label = Label(soltage, text="X")
wayne3inv3Label.grid(row=3, column=9)

# Wayne3 Inv 4
wayne3inv4Label = Label(soltage, text="X")
wayne3inv4Label.grid(row=4, column=9)

wayne3inv1cb = Checkbutton(soltage, variable=wayne3inv1cbval)
wayne3inv1cb.grid(row=1, column= 10)
wayne3inv2cb = Checkbutton(soltage, variable=wayne3inv2cbval)
wayne3inv2cb.grid(row=2, column= 10)
wayne3inv3cb = Checkbutton(soltage, variable=wayne3inv3cbval)
wayne3inv3cb.grid(row=3, column= 10)
wayne3inv4cb = Checkbutton(soltage, variable=wayne3inv4cbval)
wayne3inv4cb.grid(row=4, column= 10)

wellons1Label= Label(narenco, text= "Wellons")
wellons1Label.grid(row=0, column=19, columnspan=2)

wellonsinv1Label = Label(narenco, text="X")
wellonsinv1Label.grid(row=1, column=19)

wellonsinv2Label = Label(narenco, text="X")
wellonsinv2Label.grid(row=2, column=19)

wellonsinv3Label = Label(narenco, text="X")
wellonsinv3Label.grid(row=3, column=19)

wellonsinv4Label = Label(narenco, text="X")
wellonsinv4Label.grid(row=4, column=19)

wellonsinv5Label = Label(narenco, text="X")
wellonsinv5Label.grid(row=5, column=19)

wellonsinv6Label = Label(narenco, text="X")
wellonsinv6Label.grid(row=6, column=19)

wellonsinv1cb = Checkbutton(narenco, variable=wellonsinv1cbval)
wellonsinv1cb.grid(row=1, column=20)
wellonsinv2cb = Checkbutton(narenco, variable=wellonsinv2cbval)
wellonsinv2cb.grid(row=2, column=20)
wellonsinv3cb = Checkbutton(narenco, variable=wellonsinv3cbval)
wellonsinv3cb.grid(row=3, column=20)
wellonsinv4cb = Checkbutton(narenco, variable=wellonsinv4cbval)
wellonsinv4cb.grid(row=4, column=20)
wellonsinv5cb = Checkbutton(narenco, variable=wellonsinv5cbval)
wellonsinv5cb.grid(row=5, column=20)
wellonsinv6cb = Checkbutton(narenco, variable=wellonsinv6cbval)
wellonsinv6cb.grid(row=6, column=20)

whitehall1Label= Label(solrvr, text= "Whitehall")
whitehall1Label.grid(row=0, column=25, columnspan=2)

whitehallinv1Label= Label(solrvr, text= "X")
whitehallinv1Label.grid(row=1, column=25)

# Whitehall Inv 2
whitehallinv2Label = Label(solrvr, text="X")
whitehallinv2Label.grid(row=2, column=25)

# Whitehall Inv 3
whitehallinv3Label = Label(solrvr, text="X")
whitehallinv3Label.grid(row=3, column=25)

# Whitehall Inv 4
whitehallinv4Label = Label(solrvr, text="X")
whitehallinv4Label.grid(row=4, column=25)

# Whitehall Inv 5
whitehallinv5Label = Label(solrvr, text="X")
whitehallinv5Label.grid(row=5, column=25)

# Whitehall Inv 6
whitehallinv6Label = Label(solrvr, text="X")
whitehallinv6Label.grid(row=6, column=25)

# Whitehall Inv 7
whitehallinv7Label = Label(solrvr, text="X")
whitehallinv7Label.grid(row=7, column=25)

# Whitehall Inv 8
whitehallinv8Label = Label(solrvr, text="X")
whitehallinv8Label.grid(row=8, column=25)

# Whitehall Inv 9
whitehallinv9Label = Label(solrvr, text="X")
whitehallinv9Label.grid(row=9, column=25)

# Whitehall Inv 10
whitehallinv10Label = Label(solrvr, text="X")
whitehallinv10Label.grid(row=10, column=25)

# Whitehall Inv 11
whitehallinv11Label = Label(solrvr, text="X")
whitehallinv11Label.grid(row=11, column=25)

# Whitehall Inv 12
whitehallinv12Label = Label(solrvr, text="X")
whitehallinv12Label.grid(row=12, column=25)

# Whitehall Inv 13
whitehallinv13Label = Label(solrvr, text="X")
whitehallinv13Label.grid(row=13, column=25)

# Whitehall Inv 14
whitehallinv14Label = Label(solrvr, text="X")
whitehallinv14Label.grid(row=14, column=25)

# Whitehall Inv 15
whitehallinv15Label = Label(solrvr, text="X")
whitehallinv15Label.grid(row=15, column=25)

# Whitehall Inv 16
whitehallinv16Label = Label(solrvr, text="X")
whitehallinv16Label.grid(row=16, column=25)

whitehallinv1cb = Checkbutton(solrvr, variable=whitehallinv1cbval)
whitehallinv1cb.grid(row=1, column=26)
whitehallinv2cb = Checkbutton(solrvr, variable=whitehallinv2cbval)
whitehallinv2cb.grid(row=2, column=26)
whitehallinv3cb = Checkbutton(solrvr, variable=whitehallinv3cbval)
whitehallinv3cb.grid(row=3, column=26)
whitehallinv4cb = Checkbutton(solrvr, variable=whitehallinv4cbval)
whitehallinv4cb.grid(row=4, column=26)
whitehallinv5cb = Checkbutton(solrvr, variable=whitehallinv5cbval)
whitehallinv5cb.grid(row=5, column=26)
whitehallinv6cb = Checkbutton(solrvr, variable=whitehallinv6cbval)
whitehallinv6cb.grid(row=6, column=26)
whitehallinv7cb = Checkbutton(solrvr, variable=whitehallinv7cbval)
whitehallinv7cb.grid(row=7, column=26)
whitehallinv8cb = Checkbutton(solrvr, variable=whitehallinv8cbval)
whitehallinv8cb.grid(row=8, column=26)
whitehallinv9cb = Checkbutton(solrvr, variable=whitehallinv9cbval)
whitehallinv9cb.grid(row=9, column=26)
whitehallinv10cb = Checkbutton(solrvr, variable=whitehallinv10cbval)
whitehallinv10cb.grid(row=10, column=26)
whitehallinv11cb = Checkbutton(solrvr, variable=whitehallinv11cbval)
whitehallinv11cb.grid(row=11, column=26)
whitehallinv12cb = Checkbutton(solrvr, variable=whitehallinv12cbval)
whitehallinv12cb.grid(row=12, column=26)
whitehallinv13cb = Checkbutton(solrvr, variable=whitehallinv13cbval)
whitehallinv13cb.grid(row=13, column=26)
whitehallinv14cb = Checkbutton(solrvr, variable=whitehallinv14cbval)
whitehallinv14cb.grid(row=14, column=26)
whitehallinv15cb = Checkbutton(solrvr, variable=whitehallinv15cbval)
whitehallinv15cb.grid(row=15, column=26)
whitehallinv16cb = Checkbutton(solrvr, variable=whitehallinv16cbval)
whitehallinv16cb.grid(row=16, column=26)

whitetail1Label= Label(solrvr, text= "Whitetail")
whitetail1Label.grid(row=0, column=27, columnspan=2)

whitetailinv1Label= Label(solrvr, text= "X")
whitetailinv1Label.grid(row=1, column=27)
whitetailinv2Label = Label(solrvr, text="X")
whitetailinv2Label.grid(row=2, column=27)

# Whitetail Inv 3
whitetailinv3Label = Label(solrvr, text="X")
whitetailinv3Label.grid(row=3, column=27)

# Whitetail Inv 4
whitetailinv4Label = Label(solrvr, text="X")
whitetailinv4Label.grid(row=4, column=27)

# Whitetail Inv 5
whitetailinv5Label = Label(solrvr, text="X")
whitetailinv5Label.grid(row=5, column=27)

# Whitetail Inv 6
whitetailinv6Label = Label(solrvr, text="X")
whitetailinv6Label.grid(row=6, column=27)

# Whitetail Inv 7
whitetailinv7Label = Label(solrvr, text="X")
whitetailinv7Label.grid(row=7, column=27)

# Whitetail Inv 8
whitetailinv8Label = Label(solrvr, text="X")
whitetailinv8Label.grid(row=8, column=27)

# Whitetail Inv 9
whitetailinv9Label = Label(solrvr, text="X")
whitetailinv9Label.grid(row=9, column=27)

# Whitetail Inv 10
whitetailinv10Label = Label(solrvr, text="X")
whitetailinv10Label.grid(row=10, column=27)

# Whitetail Inv 11
whitetailinv11Label = Label(solrvr, text="X")
whitetailinv11Label.grid(row=11, column=27)

# Whitetail Inv 12
whitetailinv12Label = Label(solrvr, text="X")
whitetailinv12Label.grid(row=12, column=27)

# Whitetail Inv 13
whitetailinv13Label = Label(solrvr, text="X")
whitetailinv13Label.grid(row=13, column=27)

# Whitetail Inv 14
whitetailinv14Label = Label(solrvr, text="X")
whitetailinv14Label.grid(row=14, column=27)

# Whitetail Inv 15
whitetailinv15Label = Label(solrvr, text="X")
whitetailinv15Label.grid(row=15, column=27)

# Whitetail Inv 16
whitetailinv16Label = Label(solrvr, text="X")
whitetailinv16Label.grid(row=16, column=27)

# Whitetail Inv 17
whitetailinv17Label = Label(solrvr, text="X")
whitetailinv17Label.grid(row=17, column=27)

# Whitetail Inv 18
whitetailinv18Label = Label(solrvr, text="X")
whitetailinv18Label.grid(row=18, column=27)

# Whitetail Inv 19
whitetailinv19Label = Label(solrvr, text="X")
whitetailinv19Label.grid(row=19, column=27)

# Whitetail Inv 20
whitetailinv20Label = Label(solrvr, text="X")
whitetailinv20Label.grid(row=20, column=27)

# Whitetail Inv 21
whitetailinv21Label = Label(solrvr, text="X")
whitetailinv21Label.grid(row=21, column=27)

# Whitetail Inv 22
whitetailinv22Label = Label(solrvr, text="X")
whitetailinv22Label.grid(row=22, column=27)

# Whitetail Inv 23
whitetailinv23Label = Label(solrvr, text="X")
whitetailinv23Label.grid(row=23, column=27)

# Whitetail Inv 24
whitetailinv24Label = Label(solrvr, text="X")
whitetailinv24Label.grid(row=24, column=27)

# Whitetail Inv 25
whitetailinv25Label = Label(solrvr, text="X")
whitetailinv25Label.grid(row=25, column=27)

# Whitetail Inv 26
whitetailinv26Label = Label(solrvr, text="X")
whitetailinv26Label.grid(row=26, column=27)

# Whitetail Inv 27
whitetailinv27Label = Label(solrvr, text="X")
whitetailinv27Label.grid(row=27, column=27)

# Whitetail Inv 28
whitetailinv28Label = Label(solrvr, text="X")
whitetailinv28Label.grid(row=28, column=27)

# Whitetail Inv 29
whitetailinv29Label = Label(solrvr, text="X")
whitetailinv29Label.grid(row=29, column=27)

# Whitetail Inv 30
whitetailinv30Label = Label(solrvr, text="X")
whitetailinv30Label.grid(row=30, column=27)

# Whitetail Inv 31
whitetailinv31Label = Label(solrvr, text="X")
whitetailinv31Label.grid(row=31, column=27)

# Whitetail Inv 32
whitetailinv32Label = Label(solrvr, text="X")
whitetailinv32Label.grid(row=32, column=27)

# Whitetail Inv 33
whitetailinv33Label = Label(solrvr, text="X")
whitetailinv33Label.grid(row=33, column=27)

# Whitetail Inv 34
whitetailinv34Label = Label(solrvr, text="X")
whitetailinv34Label.grid(row=34, column=27)

# Whitetail Inv 35
whitetailinv35Label = Label(solrvr, text="X")
whitetailinv35Label.grid(row=35, column=27)

# Whitetail Inv 36
whitetailinv36Label = Label(solrvr, text="X")
whitetailinv36Label.grid(row=36, column=27)

# Whitetail Inv 37
whitetailinv37Label = Label(solrvr, text="X")
whitetailinv37Label.grid(row=37, column=27)

# Whitetail Inv 38
whitetailinv38Label = Label(solrvr, text="X")
whitetailinv38Label.grid(row=38, column=27)

# Whitetail Inv 39
whitetailinv39Label = Label(solrvr, text="X")
whitetailinv39Label.grid(row=39, column=27)

# Whitetail Inv 40
whitetailinv40Label = Label(solrvr, text="X")
whitetailinv40Label.grid(row=40, column=27)

# Whitetail Inv 41
whitetailinv41Label = Label(solrvr, text="X")
whitetailinv41Label.grid(row=41, column=27)

# Whitetail Inv 42
whitetailinv42Label = Label(solrvr, text="X")
whitetailinv42Label.grid(row=42, column=27)

# Whitetail Inv 43
whitetailinv43Label = Label(solrvr, text="X")
whitetailinv43Label.grid(row=43, column=27)

# Whitetail Inv 44
whitetailinv44Label = Label(solrvr, text="X")
whitetailinv44Label.grid(row=44, column=27)

# Whitetail Inv 45
whitetailinv45Label = Label(solrvr, text="X")
whitetailinv45Label.grid(row=45, column=27)

# Whitetail Inv 46
whitetailinv46Label = Label(solrvr, text="X")
whitetailinv46Label.grid(row=46, column=27)

# Whitetail Inv 47
whitetailinv47Label = Label(solrvr, text="X")
whitetailinv47Label.grid(row=47, column=27)

# Whitetail Inv 48
whitetailinv48Label = Label(solrvr, text="X")
whitetailinv48Label.grid(row=48, column=27)

# Whitetail Inv 49
whitetailinv49Label = Label(solrvr, text="X")
whitetailinv49Label.grid(row=49, column=27)

# Whitetail Inv 50
whitetailinv50Label = Label(solrvr, text="X")
whitetailinv50Label.grid(row=50, column=27)

# Whitetail Inv 51
whitetailinv51Label = Label(solrvr, text="X")
whitetailinv51Label.grid(row=51, column=27)

# Whitetail Inv 52
whitetailinv52Label = Label(solrvr, text="X")
whitetailinv52Label.grid(row=52, column=27)

# Whitetail Inv 53
whitetailinv53Label = Label(solrvr, text="X")
whitetailinv53Label.grid(row=53, column=27)

# Whitetail Inv 54
whitetailinv54Label = Label(solrvr, text="X")
whitetailinv54Label.grid(row=54, column=27)

# Whitetail Inv 55
whitetailinv55Label = Label(solrvr, text="X")
whitetailinv55Label.grid(row=55, column=27)

# Whitetail Inv 56
whitetailinv56Label = Label(solrvr, text="X")
whitetailinv56Label.grid(row=56, column=27)

# Whitetail Inv 57
whitetailinv57Label = Label(solrvr, text="X")
whitetailinv57Label.grid(row=57, column=27)

# Whitetail Inv 58
whitetailinv58Label = Label(solrvr, text="X")
whitetailinv58Label.grid(row=58, column=27)

# Whitetail Inv 59
whitetailinv59Label = Label(solrvr, text="X")
whitetailinv59Label.grid(row=59, column=27)

# Whitetail Inv 60
whitetailinv60Label = Label(solrvr, text="X")
whitetailinv60Label.grid(row=60, column=27)

# Whitetail Inv 61
whitetailinv61Label = Label(solrvr, text="X")
whitetailinv61Label.grid(row=61, column=27)

# Whitetail Inv 62
whitetailinv62Label = Label(solrvr, text="X")
whitetailinv62Label.grid(row=62, column=27)

# Whitetail Inv 63
whitetailinv63Label = Label(solrvr, text="X")
whitetailinv63Label.grid(row=63, column=27)

# Whitetail Inv 64
whitetailinv64Label = Label(solrvr, text="X")
whitetailinv64Label.grid(row=64, column=27)

# Whitetail Inv 65
whitetailinv65Label = Label(solrvr, text="X")
whitetailinv65Label.grid(row=65, column=27)

# Whitetail Inv 66
whitetailinv66Label = Label(solrvr, text="X")
whitetailinv66Label.grid(row=66, column=27)

# Whitetail Inv 67
whitetailinv67Label = Label(solrvr, text="X")
whitetailinv67Label.grid(row=67, column=27)

# Whitetail Inv 68
whitetailinv68Label = Label(solrvr, text="X")
whitetailinv68Label.grid(row=68, column=27)

# Whitetail Inv 69
whitetailinv69Label = Label(solrvr, text="X")
whitetailinv69Label.grid(row=69, column=27)

# Whitetail Inv 70
whitetailinv70Label = Label(solrvr, text="X")
whitetailinv70Label.grid(row=70, column=27)

# Whitetail Inv 71
whitetailinv71Label = Label(solrvr, text="X")
whitetailinv71Label.grid(row=71, column=27)

# Whitetail Inv 72
whitetailinv72Label = Label(solrvr, text="X")
whitetailinv72Label.grid(row=72, column=27)

# Whitetail Inv 73
whitetailinv73Label = Label(solrvr, text="X")
whitetailinv73Label.grid(row=73, column=27)

# Whitetail Inv 74
whitetailinv74Label = Label(solrvr, text="X")
whitetailinv74Label.grid(row=74, column=27)

# Whitetail Inv 75
whitetailinv75Label = Label(solrvr, text="X")
whitetailinv75Label.grid(row=75, column=27)

# Whitetail Inv 76
whitetailinv76Label = Label(solrvr, text="X")
whitetailinv76Label.grid(row=76, column=27)

# Whitetail Inv 77
whitetailinv77Label = Label(solrvr, text="X")
whitetailinv77Label.grid(row=77, column=27)

# Whitetail Inv 78
whitetailinv78Label = Label(solrvr, text="X")
whitetailinv78Label.grid(row=78, column=27)

# Whitetail Inv 79
whitetailinv79Label = Label(solrvr, text="X")
whitetailinv79Label.grid(row=79, column=27)

# Whitetail Inv 80
whitetailinv80Label = Label(solrvr, text="X")
whitetailinv80Label.grid(row=80, column=27)

whitetailinv1cb = Checkbutton(solrvr, variable=whitetailinv1cbval)
whitetailinv1cb.grid(row=1, column=28)
whitetailinv2cb = Checkbutton(solrvr, variable=whitetailinv2cbval)
whitetailinv2cb.grid(row=2, column=28)
whitetailinv3cb = Checkbutton(solrvr, variable=whitetailinv3cbval)
whitetailinv3cb.grid(row=3, column=28)
whitetailinv4cb = Checkbutton(solrvr, variable=whitetailinv4cbval)
whitetailinv4cb.grid(row=4, column=28)
whitetailinv5cb = Checkbutton(solrvr, variable=whitetailinv5cbval)
whitetailinv5cb.grid(row=5, column=28)
whitetailinv6cb = Checkbutton(solrvr, variable=whitetailinv6cbval)
whitetailinv6cb.grid(row=6, column=28)
whitetailinv7cb = Checkbutton(solrvr, variable=whitetailinv7cbval)
whitetailinv7cb.grid(row=7, column=28)
whitetailinv8cb = Checkbutton(solrvr, variable=whitetailinv8cbval)
whitetailinv8cb.grid(row=8, column=28)
whitetailinv9cb = Checkbutton(solrvr, variable=whitetailinv9cbval)
whitetailinv9cb.grid(row=9, column=28)
whitetailinv10cb = Checkbutton(solrvr, variable=whitetailinv10cbval)
whitetailinv10cb.grid(row=10, column=28)
whitetailinv11cb = Checkbutton(solrvr, variable=whitetailinv11cbval)
whitetailinv11cb.grid(row=11, column=28)
whitetailinv12cb = Checkbutton(solrvr, variable=whitetailinv12cbval)
whitetailinv12cb.grid(row=12, column=28)
whitetailinv13cb = Checkbutton(solrvr, variable=whitetailinv13cbval)
whitetailinv13cb.grid(row=13, column=28)
whitetailinv14cb = Checkbutton(solrvr, variable=whitetailinv14cbval)
whitetailinv14cb.grid(row=14, column=28)
whitetailinv15cb = Checkbutton(solrvr, variable=whitetailinv15cbval)
whitetailinv15cb.grid(row=15, column=28)
whitetailinv16cb = Checkbutton(solrvr, variable=whitetailinv16cbval)
whitetailinv16cb.grid(row=16, column=28)
whitetailinv17cb = Checkbutton(solrvr, variable=whitetailinv17cbval)
whitetailinv17cb.grid(row=17, column=28)
whitetailinv18cb = Checkbutton(solrvr, variable=whitetailinv18cbval)
whitetailinv18cb.grid(row=18, column=28)
whitetailinv19cb = Checkbutton(solrvr, variable=whitetailinv19cbval)
whitetailinv19cb.grid(row=19, column=28)
whitetailinv20cb = Checkbutton(solrvr, variable=whitetailinv20cbval)
whitetailinv20cb.grid(row=20, column=28)
whitetailinv21cb = Checkbutton(solrvr, variable=whitetailinv21cbval)
whitetailinv21cb.grid(row=21, column=28)
whitetailinv22cb = Checkbutton(solrvr, variable=whitetailinv22cbval)
whitetailinv22cb.grid(row=22, column=28)
whitetailinv23cb = Checkbutton(solrvr, variable=whitetailinv23cbval)
whitetailinv23cb.grid(row=23, column=28)
whitetailinv24cb = Checkbutton(solrvr, variable=whitetailinv24cbval)
whitetailinv24cb.grid(row=24, column=28)
whitetailinv25cb = Checkbutton(solrvr, variable=whitetailinv25cbval)
whitetailinv25cb.grid(row=25, column=28)
whitetailinv26cb = Checkbutton(solrvr, variable=whitetailinv26cbval)
whitetailinv26cb.grid(row=26, column=28)
whitetailinv27cb = Checkbutton(solrvr, variable=whitetailinv27cbval)
whitetailinv27cb.grid(row=27, column=28)
whitetailinv28cb = Checkbutton(solrvr, variable=whitetailinv28cbval)
whitetailinv28cb.grid(row=28, column=28)
whitetailinv29cb = Checkbutton(solrvr, variable=whitetailinv29cbval)
whitetailinv29cb.grid(row=29, column=28)
whitetailinv30cb = Checkbutton(solrvr, variable=whitetailinv30cbval)
whitetailinv30cb.grid(row=30, column=28)
whitetailinv31cb = Checkbutton(solrvr, variable=whitetailinv31cbval)
whitetailinv31cb.grid(row=31, column=28)
whitetailinv32cb = Checkbutton(solrvr, variable=whitetailinv32cbval)
whitetailinv32cb.grid(row=32, column=28)
whitetailinv33cb = Checkbutton(solrvr, variable=whitetailinv33cbval)
whitetailinv33cb.grid(row=33, column=28)
whitetailinv34cb = Checkbutton(solrvr, variable=whitetailinv34cbval)
whitetailinv34cb.grid(row=34, column=28)
whitetailinv35cb = Checkbutton(solrvr, variable=whitetailinv35cbval)
whitetailinv35cb.grid(row=35, column=28)
whitetailinv36cb = Checkbutton(solrvr, variable=whitetailinv36cbval)
whitetailinv36cb.grid(row=36, column=28)
whitetailinv37cb = Checkbutton(solrvr, variable=whitetailinv37cbval)
whitetailinv37cb.grid(row=37, column=28)
whitetailinv38cb = Checkbutton(solrvr, variable=whitetailinv38cbval)
whitetailinv38cb.grid(row=38, column=28)
whitetailinv39cb = Checkbutton(solrvr, variable=whitetailinv39cbval)
whitetailinv39cb.grid(row=39, column=28)
whitetailinv40cb = Checkbutton(solrvr, variable=whitetailinv40cbval)
whitetailinv40cb.grid(row=40, column=28)
whitetailinv41cb = Checkbutton(solrvr, variable=whitetailinv41cbval)
whitetailinv41cb.grid(row=41, column=28)
whitetailinv42cb = Checkbutton(solrvr, variable=whitetailinv42cbval)
whitetailinv42cb.grid(row=42, column=28)
whitetailinv43cb = Checkbutton(solrvr, variable=whitetailinv43cbval)
whitetailinv43cb.grid(row=43, column=28)
whitetailinv44cb = Checkbutton(solrvr, variable=whitetailinv44cbval)
whitetailinv44cb.grid(row=44, column=28)
whitetailinv45cb = Checkbutton(solrvr, variable=whitetailinv45cbval)
whitetailinv45cb.grid(row=45, column=28)
whitetailinv46cb = Checkbutton(solrvr, variable=whitetailinv46cbval)
whitetailinv46cb.grid(row=46, column=28)
whitetailinv47cb = Checkbutton(solrvr, variable=whitetailinv47cbval)
whitetailinv47cb.grid(row=47, column=28)
whitetailinv48cb = Checkbutton(solrvr, variable=whitetailinv48cbval)
whitetailinv48cb.grid(row=48, column=28)
whitetailinv49cb = Checkbutton(solrvr, variable=whitetailinv49cbval)
whitetailinv49cb.grid(row=49, column=28)
whitetailinv50cb = Checkbutton(solrvr, variable=whitetailinv50cbval)
whitetailinv50cb.grid(row=50, column=28)
whitetailinv51cb = Checkbutton(solrvr, variable=whitetailinv51cbval)
whitetailinv51cb.grid(row=51, column=28)
whitetailinv52cb = Checkbutton(solrvr, variable=whitetailinv52cbval)
whitetailinv52cb.grid(row=52, column=28)
whitetailinv53cb = Checkbutton(solrvr, variable=whitetailinv53cbval)
whitetailinv53cb.grid(row=53, column=28)
whitetailinv54cb = Checkbutton(solrvr, variable=whitetailinv54cbval)
whitetailinv54cb.grid(row=54, column=28)
whitetailinv55cb = Checkbutton(solrvr, variable=whitetailinv55cbval)
whitetailinv55cb.grid(row=55, column=28)
whitetailinv56cb = Checkbutton(solrvr, variable=whitetailinv56cbval)
whitetailinv56cb.grid(row=56, column=28)
whitetailinv57cb = Checkbutton(solrvr, variable=whitetailinv57cbval)
whitetailinv57cb.grid(row=57, column=28)
whitetailinv58cb = Checkbutton(solrvr, variable=whitetailinv58cbval)
whitetailinv58cb.grid(row=58, column=28)
whitetailinv59cb = Checkbutton(solrvr, variable=whitetailinv59cbval)
whitetailinv59cb.grid(row=59, column=28)
whitetailinv60cb = Checkbutton(solrvr, variable=whitetailinv60cbval)
whitetailinv60cb.grid(row=60, column=28)
whitetailinv61cb = Checkbutton(solrvr, variable=whitetailinv61cbval)
whitetailinv61cb.grid(row=61, column=28)
whitetailinv62cb = Checkbutton(solrvr, variable=whitetailinv62cbval)
whitetailinv62cb.grid(row=62, column=28)
whitetailinv63cb = Checkbutton(solrvr, variable=whitetailinv63cbval)
whitetailinv63cb.grid(row=63, column=28)
whitetailinv64cb = Checkbutton(solrvr, variable=whitetailinv64cbval)
whitetailinv64cb.grid(row=64, column=28)
whitetailinv65cb = Checkbutton(solrvr, variable=whitetailinv65cbval)
whitetailinv65cb.grid(row=65, column=28)
whitetailinv66cb = Checkbutton(solrvr, variable=whitetailinv66cbval)
whitetailinv66cb.grid(row=66, column=28)
whitetailinv67cb = Checkbutton(solrvr, variable=whitetailinv67cbval)
whitetailinv67cb.grid(row=67, column=28)
whitetailinv68cb = Checkbutton(solrvr, variable=whitetailinv68cbval)
whitetailinv68cb.grid(row=68, column=28)
whitetailinv69cb = Checkbutton(solrvr, variable=whitetailinv69cbval)
whitetailinv69cb.grid(row=69, column=28)
whitetailinv70cb = Checkbutton(solrvr, variable=whitetailinv70cbval)
whitetailinv70cb.grid(row=70, column=28)
whitetailinv71cb = Checkbutton(solrvr, variable=whitetailinv71cbval)
whitetailinv71cb.grid(row=71, column=28)
whitetailinv72cb = Checkbutton(solrvr, variable=whitetailinv72cbval)
whitetailinv72cb.grid(row=72, column=28)
whitetailinv73cb = Checkbutton(solrvr, variable=whitetailinv73cbval)
whitetailinv73cb.grid(row=73, column=28)
whitetailinv74cb = Checkbutton(solrvr, variable=whitetailinv74cbval)
whitetailinv74cb.grid(row=74, column=28)
whitetailinv75cb = Checkbutton(solrvr, variable=whitetailinv75cbval)
whitetailinv75cb.grid(row=75, column=28)
whitetailinv76cb = Checkbutton(solrvr, variable=whitetailinv76cbval)
whitetailinv76cb.grid(row=76, column=28)
whitetailinv77cb = Checkbutton(solrvr, variable=whitetailinv77cbval)
whitetailinv77cb.grid(row=77, column=28)
whitetailinv78cb = Checkbutton(solrvr, variable=whitetailinv78cbval)
whitetailinv78cb.grid(row=78, column=28)
whitetailinv79cb = Checkbutton(solrvr, variable=whitetailinv79cbval)
whitetailinv79cb.grid(row=79, column=28)
whitetailinv80cb = Checkbutton(solrvr, variable=whitetailinv80cbval)
whitetailinv80cb.grid(row=80, column=28)

bishopvilleIImetercb = Checkbutton(root, variable=bishopvilleIImetercbval, bg='yellow')
bishopvilleIImetercb.grid(row= 1, column=3)
bluebirdmetercb = Checkbutton(root, variable=bluebirdmetercbval, bg='yellow')
bluebirdmetercb.grid(row= 2, column=3)
bulloch1ametercb = Checkbutton(root, variable=bulloch1ametercbval, bg='yellow')
bulloch1ametercb.grid(row= 3, column=3)
bulloch1bmetercb = Checkbutton(root, variable=bulloch1bmetercbval, bg='yellow')
bulloch1bmetercb.grid(row= 4, column=3)
cardinalmetercb = Checkbutton(root, variable=cardinalmetercbval, bg='yellow')
cardinalmetercb.grid(row= 5, column=3)
cdiametercb = Checkbutton(root, variable=cdiametercbval, bg='yellow')
cdiametercb.grid(row= 6, column=3)
cherrymetercb = Checkbutton(root, variable=cherrymetercbval, bg='yellow')
cherrymetercb.grid(row= 7, column=3)
cougarmetercb = Checkbutton(root, variable=cougarmetercbval, bg='yellow')
cougarmetercb.grid(row= 8, column=3)
conetoemetercb = Checkbutton(root, variable=conetoemetercbval, bg='yellow')
conetoemetercb.grid(row= 9, column=3)
duplinmetercb = Checkbutton(root, variable=duplinmetercbval, bg='yellow')
duplinmetercb.grid(row= 10, column=3)
elkmetercb = Checkbutton(root, variable=elkmetercbval, bg='yellow')
elkmetercb.grid(row= 11, column=3)
freightlinemetercb = Checkbutton(root, variable=freightlinemetercbval, bg='yellow')
freightlinemetercb.grid(row= 12, column=3)
grayfoxmetercb = Checkbutton(root, variable=grayfoxmetercbval, bg='yellow')
grayfoxmetercb.grid(row= 13, column=3)
hardingmetercb = Checkbutton(root, variable=hardingmetercbval, bg='yellow')
hardingmetercb.grid(row= 14, column=3)
harrisonmetercb = Checkbutton(root, variable=harrisonmetercbval, bg='yellow')
harrisonmetercb.grid(row= 15, column=3)
hayesmetercb = Checkbutton(root, variable=hayesmetercbval, bg='yellow')
hayesmetercb.grid(row= 16, column=3)
hickorymetercb = Checkbutton(root, variable=hickorymetercbval, bg='yellow')
hickorymetercb.grid(row= 17, column=3)
hicksonmetercb = Checkbutton(root, variable=hicksonmetercbval, bg='yellow')
hicksonmetercb.grid(row= 18, column=3)
hollyswampmetercb = Checkbutton(root, variable=hollyswampmetercbval, bg='yellow')
hollyswampmetercb.grid(row= 19, column=3)
jeffersonmetercb = Checkbutton(root, variable=jeffersonmetercbval, bg='yellow')
jeffersonmetercb.grid(row= 20, column=3)
marshallmetercb = Checkbutton(root, variable=marshallmetercbval, bg='yellow')
marshallmetercb.grid(row= 21, column=3)
mcLeanmetercb = Checkbutton(root, variable=mcLeanmetercbval, bg='yellow')
mcLeanmetercb.grid(row= 22, column=3)
ogburnmetercb = Checkbutton(root, variable=ogburnmetercbval, bg='yellow')
ogburnmetercb.grid(row= 23, column=3)
pgmetercb = Checkbutton(root, variable=pgmetercbval, bg='yellow')
pgmetercb.grid(row= 24, column=3)
richmondmetercb = Checkbutton(root, variable=richmondmetercbval, bg='yellow')
richmondmetercb.grid(row= 25, column=3)
shorthornmetercb = Checkbutton(root, variable=shorthornmetercbval, bg='yellow')
shorthornmetercb.grid(row= 26, column=3)
sunflowermetercb = Checkbutton(root, variable=sunflowermetercbval, bg='yellow')
sunflowermetercb.grid(row= 27, column=3)
teddermetercb = Checkbutton(root, variable=teddermetercbval, bg='yellow')
teddermetercb.grid(row= 28, column=3)
thunderheadmetercb = Checkbutton(root, variable=thunderheadmetercbval, bg='yellow')
thunderheadmetercb.grid(row= 29, column=3)
upsonmetercb = Checkbutton(root, variable=upsonmetercbval, bg='yellow')
upsonmetercb.grid(row= 30, column=3)
vanburenmetercb = Checkbutton(root, variable=vanburenmetercbval, bg='yellow')
vanburenmetercb.grid(row= 31, column=3)
violetmetercb = Checkbutton(root, variable=violetmetercbval, bg='yellow')
violetmetercb.grid(row= 32, column=3, rowspan= 2)
warblermetercb = Checkbutton(root, variable=warblermetercbval, bg='yellow')
warblermetercb.grid(row= 34, column=3)
washingtonmetercb = Checkbutton(root, variable=washingtonmetercbval, bg='yellow')
washingtonmetercb.grid(row= 35, column=3)
wayne1metercb = Checkbutton(root, variable=wayne1metercbval, bg='yellow')
wayne1metercb.grid(row= 36, column=3)
wayne2metercb = Checkbutton(root, variable=wayne2metercbval, bg='yellow')
wayne2metercb.grid(row= 37, column=3)
wayne3metercb = Checkbutton(root, variable=wayne3metercbval, bg='yellow')
wayne3metercb.grid(row= 38, column=3)
wellonsmetercb = Checkbutton(root, variable=wellonsmetercbval, bg='yellow')
wellonsmetercb.grid(row= 39, column=3)
whitehallmetercb = Checkbutton(root, variable=whitehallmetercbval, bg='yellow')
whitehallmetercb.grid(row= 40, column=3)
whitetailmetercb = Checkbutton(root, variable=whitetailmetercbval, bg='yellow')
whitetailmetercb.grid(row= 41, column=3)



bishopvilleIIPOAcb = Checkbutton(root, variable=bishopvilleIIPOAcbval, bg='yellow')
bishopvilleIIPOAcb.grid(row= 1, column=6)
bluebirdPOAcb = Checkbutton(root, variable=bluebirdPOAcbval, bg='yellow')
bluebirdPOAcb.grid(row= 2, column=6)
bulloch1aPOAcb = Checkbutton(root, variable=bulloch1aPOAcbval, bg='yellow')
bulloch1aPOAcb.grid(row= 3, column=6)
bulloch1bPOAcb = Checkbutton(root, variable=bulloch1bPOAcbval, bg='yellow')
bulloch1bPOAcb.grid(row= 4, column=6)
cardinalPOAcb = Checkbutton(root, variable=cardinalPOAcbval, bg='yellow')
cardinalPOAcb.grid(row= 5, column=6)
cdiaPOAcb = Checkbutton(root, variable=cdiaPOAcbval, bg='yellow')
cdiaPOAcb.grid(row= 6, column=6)
cherryPOAcb = Checkbutton(root, variable=cherryPOAcbval, bg='yellow')
cherryPOAcb.grid(row= 7, column=6)
cougarPOAcb = Checkbutton(root, variable=cougarPOAcbval, bg='yellow')
cougarPOAcb.grid(row= 8, column=6)
conetoePOAcb = Checkbutton(root, variable=conetoePOAcbval, bg='yellow')
conetoePOAcb.grid(row= 9, column=6)
duplinPOAcb = Checkbutton(root, variable=duplinPOAcbval, bg='yellow')
duplinPOAcb.grid(row= 10, column=6)
elkPOAcb = Checkbutton(root, variable=elkPOAcbval, bg='yellow')
elkPOAcb.grid(row= 11, column=6)
freightlinePOAcb = Checkbutton(root, variable=freightlinePOAcbval, bg='yellow')
freightlinePOAcb.grid(row= 12, column=6)
grayfoxPOAcb = Checkbutton(root, variable=grayfoxPOAcbval, bg='yellow')
grayfoxPOAcb.grid(row= 13, column=6)
hardingPOAcb = Checkbutton(root, variable=hardingPOAcbval, bg='yellow')
hardingPOAcb.grid(row= 14, column=6)
harrisonPOAcb = Checkbutton(root, variable=harrisonPOAcbval, bg='yellow')
harrisonPOAcb.grid(row= 15, column=6)
hayesPOAcb = Checkbutton(root, variable=hayesPOAcbval, bg='yellow')
hayesPOAcb.grid(row= 16, column=6)
hickoryPOAcb = Checkbutton(root, variable=hickoryPOAcbval, bg='yellow')
hickoryPOAcb.grid(row= 17, column=6)
hicksonPOAcb = Checkbutton(root, variable=hicksonPOAcbval, bg='yellow')
hicksonPOAcb.grid(row= 18, column=6)
hollyswampPOAcb = Checkbutton(root, variable=hollyswampPOAcbval, bg='yellow')
hollyswampPOAcb.grid(row= 19, column=6)
jeffersonPOAcb = Checkbutton(root, variable=jeffersonPOAcbval, bg='yellow')
jeffersonPOAcb.grid(row= 20, column=6)
marshallPOAcb = Checkbutton(root, variable=marshallPOAcbval, bg='yellow')
marshallPOAcb.grid(row= 21, column=6)
mcLeanPOAcb = Checkbutton(root, variable=mcLeanPOAcbval, bg='yellow')
mcLeanPOAcb.grid(row= 22, column=6)
ogburnPOAcb = Checkbutton(root, variable=ogburnPOAcbval, bg='yellow')
ogburnPOAcb.grid(row= 23, column=6)
pgPOAcb = Checkbutton(root, variable=pgPOAcbval, bg='yellow')
pgPOAcb.grid(row= 24, column=6)
richmondPOAcb = Checkbutton(root, variable=richmondPOAcbval, bg='yellow')
richmondPOAcb.grid(row= 25, column=6)
shorthornPOAcb = Checkbutton(root, variable=shorthornPOAcbval, bg='yellow')
shorthornPOAcb.grid(row= 26, column=6)
sunflowerPOAcb = Checkbutton(root, variable=sunflowerPOAcbval, bg='yellow')
sunflowerPOAcb.grid(row= 27, column=6)
tedderPOAcb = Checkbutton(root, variable=tedderPOAcbval, bg='yellow')
tedderPOAcb.grid(row= 28, column=6)
thunderheadPOAcb = Checkbutton(root, variable=thunderheadPOAcbval, bg='yellow')
thunderheadPOAcb.grid(row= 29, column=6)
upsonPOAcb = Checkbutton(root, variable=upsonPOAcbval, bg='yellow')
upsonPOAcb.grid(row= 30, column=6)
vanburenPOAcb = Checkbutton(root, variable=vanburenPOAcbval, bg='yellow')
vanburenPOAcb.grid(row= 31, column=6)
violetPOAcb = Checkbutton(root, variable=violetPOAcbval, bg='yellow')
violetPOAcb.grid(row= 32, column=6, rowspan=2)
warblerPOAcb = Checkbutton(root, variable=warblerPOAcbval, bg='yellow')
warblerPOAcb.grid(row= 34, column=6)
washingtonPOAcb = Checkbutton(root, variable=washingtonPOAcbval, bg='yellow')
washingtonPOAcb.grid(row= 35, column=6)
wayne1POAcb = Checkbutton(root, variable=wayne1POAcbval, bg='yellow')
wayne1POAcb.grid(row= 36, column=6)
wayne2POAcb = Checkbutton(root, variable=wayne2POAcbval, bg='yellow')
wayne2POAcb.grid(row= 37, column=6)
wayne3POAcb = Checkbutton(root, variable=wayne3POAcbval, bg='yellow')
wayne3POAcb.grid(row= 38, column=6)
wellonsPOAcb = Checkbutton(root, variable=wellonsPOAcbval, bg='yellow')
wellonsPOAcb.grid(row= 39, column=6)
whitehallPOAcb = Checkbutton(root, variable=whitehallPOAcbval, bg='yellow')
whitehallPOAcb.grid(row= 40, column=6)
whitetailPOAcb = Checkbutton(root, variable=whitetailPOAcbval, bg='yellow')
whitetailPOAcb.grid(row= 41, column=6)






STATE_FILE = r"G:\Shared drives\O&M\NCC Automations\Notification System\CheckBoxState.json"

all_CBs = [bishopvilleIImetercbval, bluebirdmetercbval, bulloch1ametercbval, bulloch1bmetercbval,
    cardinalmetercbval, cdiametercbval, cherrymetercbval, cougarmetercbval, conetoemetercbval, duplinmetercbval, elkmetercbval,
    freightlinemetercbval, grayfoxmetercbval, hardingmetercbval, harrisonmetercbval, hayesmetercbval,
    hickorymetercbval, hicksonmetercbval, hollyswampmetercbval, jeffersonmetercbval, marshallmetercbval,
    mcLeanmetercbval, ogburnmetercbval, pgmetercbval, richmondmetercbval, shorthornmetercbval,
    sunflowermetercbval, teddermetercbval, thunderheadmetercbval, upsonmetercbval, vanburenmetercbval,
    violetmetercbval, warblermetercbval, washingtonmetercbval, wayne1metercbval, wayne2metercbval,
    wayne3metercbval, wellonsmetercbval, whitetailmetercbval, whitehallmetercbval, bishopvilleIIPOAcbval,
    bluebirdPOAcbval, bulloch1aPOAcbval, bulloch1bPOAcbval, cardinalPOAcbval, cdiaPOAcbval, cherryPOAcbval, cougarPOAcbval,
    conetoePOAcbval, duplinPOAcbval, elkPOAcbval, freightlinePOAcbval, grayfoxPOAcbval, hardingPOAcbval,
    harrisonPOAcbval, hayesPOAcbval, hickoryPOAcbval, hicksonPOAcbval, hollyswampPOAcbval, jeffersonPOAcbval,
    marshallPOAcbval, mcLeanPOAcbval, ogburnPOAcbval, pgPOAcbval, richmondPOAcbval, shorthornPOAcbval,
    sunflowerPOAcbval, tedderPOAcbval, thunderheadPOAcbval, upsonPOAcbval, vanburenPOAcbval, violetPOAcbval,
    warblerPOAcbval, washingtonPOAcbval, wayne1POAcbval, wayne2POAcbval, wayne3POAcbval, wellonsPOAcbval,
    whitetailPOAcbval, whitehallPOAcbval,
    bluebirdinv1cbval, bluebirdinv2cbval, bluebirdinv3cbval, bluebirdinv4cbval, bluebirdinv5cbval, bluebirdinv6cbval, bluebirdinv7cbval, bluebirdinv8cbval, bluebirdinv9cbval, bluebirdinv10cbval, bluebirdinv11cbval, bluebirdinv12cbval, bluebirdinv13cbval, bluebirdinv14cbval, bluebirdinv15cbval, bluebirdinv16cbval, bluebirdinv17cbval, bluebirdinv18cbval, bluebirdinv19cbval, bluebirdinv20cbval, bluebirdinv21cbval, bluebirdinv22cbval, bluebirdinv23cbval, bluebirdinv24cbval,
    cardinalinv1cbval, cardinalinv2cbval, cardinalinv3cbval, cardinalinv4cbval, cardinalinv5cbval, cardinalinv6cbval, cardinalinv7cbval, cardinalinv8cbval, cardinalinv9cbval, cardinalinv10cbval, cardinalinv11cbval, cardinalinv12cbval, cardinalinv13cbval, cardinalinv14cbval, cardinalinv15cbval, cardinalinv16cbval, cardinalinv17cbval, cardinalinv18cbval, cardinalinv19cbval, cardinalinv20cbval, cardinalinv21cbval, cardinalinv22cbval, cardinalinv23cbval, cardinalinv24cbval, cardinalinv25cbval, cardinalinv26cbval, cardinalinv27cbval, cardinalinv28cbval, cardinalinv29cbval, cardinalinv30cbval, cardinalinv31cbval, cardinalinv32cbval, cardinalinv33cbval, cardinalinv34cbval, cardinalinv35cbval, cardinalinv36cbval, cardinalinv37cbval, cardinalinv38cbval, cardinalinv39cbval, cardinalinv40cbval, cardinalinv41cbval, cardinalinv42cbval, cardinalinv43cbval, cardinalinv44cbval, cardinalinv45cbval, cardinalinv46cbval, cardinalinv47cbval, cardinalinv48cbval, cardinalinv49cbval, cardinalinv50cbval, cardinalinv51cbval, cardinalinv52cbval, cardinalinv53cbval, cardinalinv54cbval, cardinalinv55cbval, cardinalinv56cbval, cardinalinv57cbval, cardinalinv58cbval, cardinalinv59cbval,
    cherryinv1cbval, cherryinv2cbval, cherryinv3cbval, cherryinv4cbval,
    harrisoninv1cbval, harrisoninv2cbval, harrisoninv3cbval, harrisoninv4cbval, harrisoninv5cbval, harrisoninv6cbval, harrisoninv7cbval, harrisoninv8cbval, harrisoninv9cbval, harrisoninv10cbval, harrisoninv11cbval, harrisoninv12cbval, harrisoninv13cbval, harrisoninv14cbval, harrisoninv15cbval, harrisoninv16cbval, harrisoninv17cbval, harrisoninv18cbval, harrisoninv19cbval, harrisoninv20cbval, harrisoninv21cbval, harrisoninv22cbval, harrisoninv23cbval, harrisoninv24cbval, harrisoninv25cbval, harrisoninv26cbval, harrisoninv27cbval, harrisoninv28cbval, harrisoninv29cbval, harrisoninv30cbval, harrisoninv31cbval, harrisoninv32cbval, harrisoninv33cbval, harrisoninv34cbval, harrisoninv35cbval, harrisoninv36cbval, harrisoninv37cbval, harrisoninv38cbval, harrisoninv39cbval, harrisoninv40cbval, harrisoninv41cbval, harrisoninv42cbval, harrisoninv43cbval,
    hayesinv1cbval, hayesinv2cbval, hayesinv3cbval, hayesinv4cbval, hayesinv5cbval, hayesinv6cbval, hayesinv7cbval, hayesinv8cbval, hayesinv9cbval, hayesinv10cbval, hayesinv11cbval, hayesinv12cbval, hayesinv13cbval, hayesinv14cbval, hayesinv15cbval, hayesinv16cbval, hayesinv17cbval, hayesinv18cbval, hayesinv19cbval, hayesinv20cbval, hayesinv21cbval, hayesinv22cbval, hayesinv23cbval, hayesinv24cbval, hayesinv25cbval, hayesinv26cbval,
    hickoryinv1cbval, hickoryinv2cbval,
    vanbureninv1cbval, vanbureninv2cbval, vanbureninv3cbval, vanbureninv4cbval, vanbureninv5cbval, vanbureninv6cbval, vanbureninv7cbval, vanbureninv8cbval, vanbureninv9cbval, vanbureninv10cbval, vanbureninv11cbval, vanbureninv12cbval, vanbureninv13cbval, vanbureninv14cbval, vanbureninv15cbval, vanbureninv16cbval, vanbureninv17cbval,
    violetinv1cbval, violetinv2cbval,
    wellonsinv1cbval, wellonsinv2cbval, wellonsinv3cbval, wellonsinv4cbval, wellonsinv5cbval, wellonsinv6cbval,
    bishopvilleIIinv1cbval, bishopvilleIIinv2cbval, bishopvilleIIinv3cbval, bishopvilleIIinv4cbval, bishopvilleIIinv5cbval, bishopvilleIIinv6cbval, bishopvilleIIinv7cbval, bishopvilleIIinv8cbval, bishopvilleIIinv9cbval, bishopvilleIIinv10cbval, bishopvilleIIinv11cbval, bishopvilleIIinv12cbval, bishopvilleIIinv13cbval, bishopvilleIIinv14cbval, bishopvilleIIinv15cbval, bishopvilleIIinv16cbval, bishopvilleIIinv17cbval, bishopvilleIIinv18cbval, bishopvilleIIinv19cbval, bishopvilleIIinv20cbval, bishopvilleIIinv21cbval, bishopvilleIIinv22cbval, bishopvilleIIinv23cbval, bishopvilleIIinv24cbval, bishopvilleIIinv25cbval, bishopvilleIIinv26cbval, bishopvilleIIinv27cbval, bishopvilleIIinv28cbval, bishopvilleIIinv29cbval, bishopvilleIIinv30cbval, bishopvilleIIinv31cbval, bishopvilleIIinv32cbval, bishopvilleIIinv33cbval, bishopvilleIIinv34cbval, bishopvilleIIinv35cbval, bishopvilleIIinv36cbval,
    hicksoninv1cbval, hicksoninv2cbval, hicksoninv3cbval, hicksoninv4cbval, hicksoninv5cbval, hicksoninv6cbval, hicksoninv7cbval, hicksoninv8cbval, hicksoninv9cbval, hicksoninv10cbval, hicksoninv11cbval, hicksoninv12cbval, hicksoninv13cbval, hicksoninv14cbval, hicksoninv15cbval, hicksoninv16cbval,
    jeffersoninv1cbval, jeffersoninv2cbval, jeffersoninv3cbval, jeffersoninv4cbval, jeffersoninv5cbval, jeffersoninv6cbval, jeffersoninv7cbval, jeffersoninv8cbval, jeffersoninv9cbval, jeffersoninv10cbval, jeffersoninv11cbval, jeffersoninv12cbval, jeffersoninv13cbval, jeffersoninv14cbval, jeffersoninv15cbval, jeffersoninv16cbval, jeffersoninv17cbval, jeffersoninv18cbval, jeffersoninv19cbval, jeffersoninv20cbval, jeffersoninv21cbval, jeffersoninv22cbval, jeffersoninv23cbval, jeffersoninv24cbval, jeffersoninv25cbval, jeffersoninv26cbval, jeffersoninv27cbval, jeffersoninv28cbval, jeffersoninv29cbval, jeffersoninv30cbval, jeffersoninv31cbval, jeffersoninv32cbval, jeffersoninv33cbval, jeffersoninv34cbval, jeffersoninv35cbval, jeffersoninv36cbval, jeffersoninv37cbval, jeffersoninv38cbval, jeffersoninv39cbval, jeffersoninv40cbval, jeffersoninv41cbval, jeffersoninv42cbval, jeffersoninv43cbval, jeffersoninv44cbval, jeffersoninv45cbval, jeffersoninv46cbval, jeffersoninv47cbval, jeffersoninv48cbval, jeffersoninv49cbval, jeffersoninv50cbval, jeffersoninv51cbval, jeffersoninv52cbval, jeffersoninv53cbval, jeffersoninv54cbval, jeffersoninv55cbval, jeffersoninv56cbval, jeffersoninv57cbval, jeffersoninv58cbval, jeffersoninv59cbval, jeffersoninv60cbval, jeffersoninv61cbval, jeffersoninv62cbval, jeffersoninv63cbval, jeffersoninv64cbval,
    marshallinv1cbval, marshallinv2cbval, marshallinv3cbval, marshallinv4cbval, marshallinv5cbval, marshallinv6cbval, marshallinv7cbval, marshallinv8cbval, marshallinv9cbval, marshallinv10cbval, marshallinv11cbval, marshallinv12cbval, marshallinv13cbval, marshallinv14cbval, marshallinv15cbval, marshallinv16cbval,
    mcLeaninv1cbval, mcLeaninv2cbval, mcLeaninv3cbval, mcLeaninv4cbval, mcLeaninv5cbval, mcLeaninv6cbval, mcLeaninv7cbval, mcLeaninv8cbval, mcLeaninv9cbval, mcLeaninv10cbval, mcLeaninv11cbval, mcLeaninv12cbval, mcLeaninv13cbval, mcLeaninv14cbval, mcLeaninv15cbval, mcLeaninv16cbval, mcLeaninv17cbval, mcLeaninv18cbval, mcLeaninv19cbval, mcLeaninv20cbval, mcLeaninv21cbval, mcLeaninv22cbval, mcLeaninv23cbval, mcLeaninv24cbval, mcLeaninv25cbval, mcLeaninv26cbval, mcLeaninv27cbval, mcLeaninv28cbval, mcLeaninv29cbval, mcLeaninv30cbval, mcLeaninv31cbval, mcLeaninv32cbval, mcLeaninv33cbval, mcLeaninv34cbval, mcLeaninv35cbval, mcLeaninv36cbval, mcLeaninv37cbval, mcLeaninv38cbval, mcLeaninv39cbval, mcLeaninv40cbval,
    ogburninv1cbval, ogburninv2cbval, ogburninv3cbval, ogburninv4cbval, ogburninv5cbval, ogburninv6cbval, ogburninv7cbval, ogburninv8cbval, ogburninv9cbval, ogburninv10cbval, ogburninv11cbval, ogburninv12cbval, ogburninv13cbval, ogburninv14cbval, ogburninv15cbval, ogburninv16cbval,
    tedderinv1cbval, tedderinv2cbval, tedderinv3cbval, tedderinv4cbval, tedderinv5cbval, tedderinv6cbval, tedderinv7cbval, tedderinv8cbval, tedderinv9cbval, tedderinv10cbval, tedderinv11cbval, tedderinv12cbval, tedderinv13cbval, tedderinv14cbval, tedderinv15cbval, tedderinv16cbval,
    thunderheadinv1cbval, thunderheadinv2cbval, thunderheadinv3cbval, thunderheadinv4cbval, thunderheadinv5cbval, thunderheadinv6cbval, thunderheadinv7cbval, thunderheadinv8cbval, thunderheadinv9cbval, thunderheadinv10cbval, thunderheadinv11cbval, thunderheadinv12cbval, thunderheadinv13cbval, thunderheadinv14cbval, thunderheadinv15cbval, thunderheadinv16cbval,
    bulloch1ainv1cbval, bulloch1ainv2cbval, bulloch1ainv3cbval, bulloch1ainv4cbval, bulloch1ainv5cbval, bulloch1ainv6cbval, bulloch1ainv7cbval, bulloch1ainv8cbval, bulloch1ainv9cbval, bulloch1ainv10cbval, bulloch1ainv11cbval, bulloch1ainv12cbval, bulloch1ainv13cbval, bulloch1ainv14cbval, bulloch1ainv15cbval, bulloch1ainv16cbval, bulloch1ainv17cbval, bulloch1ainv18cbval, bulloch1ainv19cbval, bulloch1ainv20cbval, bulloch1ainv21cbval, bulloch1ainv22cbval, bulloch1ainv23cbval, bulloch1ainv24cbval,
    bulloch1binv1cbval, bulloch1binv2cbval, bulloch1binv3cbval, bulloch1binv4cbval, bulloch1binv5cbval, bulloch1binv6cbval, bulloch1binv7cbval, bulloch1binv8cbval, bulloch1binv9cbval, bulloch1binv10cbval, bulloch1binv11cbval, bulloch1binv12cbval, bulloch1binv13cbval, bulloch1binv14cbval, bulloch1binv15cbval, bulloch1binv16cbval, bulloch1binv17cbval, bulloch1binv18cbval, bulloch1binv19cbval, bulloch1binv20cbval, bulloch1binv21cbval, bulloch1binv22cbval, bulloch1binv23cbval, bulloch1binv24cbval,
    grayfoxinv1cbval, grayfoxinv2cbval, grayfoxinv3cbval, grayfoxinv4cbval, grayfoxinv5cbval, grayfoxinv6cbval, grayfoxinv7cbval, grayfoxinv8cbval, grayfoxinv9cbval, grayfoxinv10cbval, grayfoxinv11cbval, grayfoxinv12cbval, grayfoxinv13cbval, grayfoxinv14cbval, grayfoxinv15cbval, grayfoxinv16cbval, grayfoxinv17cbval, grayfoxinv18cbval, grayfoxinv19cbval, grayfoxinv20cbval, grayfoxinv21cbval, grayfoxinv22cbval, grayfoxinv23cbval, grayfoxinv24cbval, grayfoxinv25cbval, grayfoxinv26cbval, grayfoxinv27cbval, grayfoxinv28cbval, grayfoxinv29cbval, grayfoxinv30cbval, grayfoxinv31cbval, grayfoxinv32cbval, grayfoxinv33cbval, grayfoxinv34cbval, grayfoxinv35cbval, grayfoxinv36cbval, grayfoxinv37cbval, grayfoxinv38cbval, grayfoxinv39cbval, grayfoxinv40cbval,
    hardinginv1cbval, hardinginv2cbval, hardinginv3cbval, hardinginv4cbval, hardinginv5cbval, hardinginv6cbval, hardinginv7cbval, hardinginv8cbval, hardinginv9cbval, hardinginv10cbval, hardinginv11cbval, hardinginv12cbval, hardinginv13cbval, hardinginv14cbval, hardinginv15cbval, hardinginv16cbval, hardinginv17cbval, hardinginv18cbval, hardinginv19cbval, hardinginv20cbval, hardinginv21cbval, hardinginv22cbval, hardinginv23cbval, hardinginv24cbval,
    richmondinv1cbval, richmondinv2cbval, richmondinv3cbval, richmondinv4cbval, richmondinv5cbval, richmondinv6cbval, richmondinv7cbval, richmondinv8cbval, richmondinv9cbval, richmondinv10cbval, richmondinv11cbval, richmondinv12cbval, richmondinv13cbval, richmondinv14cbval, richmondinv15cbval, richmondinv16cbval, richmondinv17cbval, richmondinv18cbval, richmondinv19cbval, richmondinv20cbval, richmondinv21cbval, richmondinv22cbval, richmondinv23cbval, richmondinv24cbval,
    shorthorninv1cbval, shorthorninv2cbval, shorthorninv3cbval, shorthorninv4cbval, shorthorninv5cbval, shorthorninv6cbval, shorthorninv7cbval, shorthorninv8cbval, shorthorninv9cbval, shorthorninv10cbval, shorthorninv11cbval, shorthorninv12cbval, shorthorninv13cbval, shorthorninv14cbval, shorthorninv15cbval, shorthorninv16cbval, shorthorninv17cbval, shorthorninv18cbval, shorthorninv19cbval, shorthorninv20cbval, shorthorninv21cbval, shorthorninv22cbval, shorthorninv23cbval, shorthorninv24cbval, shorthorninv25cbval, shorthorninv26cbval, shorthorninv27cbval, shorthorninv28cbval, shorthorninv29cbval, shorthorninv30cbval, shorthorninv31cbval, shorthorninv32cbval, shorthorninv33cbval, shorthorninv34cbval, shorthorninv35cbval, shorthorninv36cbval, shorthorninv37cbval, shorthorninv38cbval, shorthorninv39cbval, shorthorninv40cbval, shorthorninv41cbval, shorthorninv42cbval, shorthorninv43cbval, shorthorninv44cbval, shorthorninv45cbval, shorthorninv46cbval, shorthorninv47cbval, shorthorninv48cbval, shorthorninv49cbval, shorthorninv50cbval, shorthorninv51cbval, shorthorninv52cbval, shorthorninv53cbval, shorthorninv54cbval, shorthorninv55cbval, shorthorninv56cbval, shorthorninv57cbval, shorthorninv58cbval, shorthorninv59cbval, shorthorninv60cbval, shorthorninv61cbval, shorthorninv62cbval, shorthorninv63cbval, shorthorninv64cbval, shorthorninv65cbval, shorthorninv66cbval, shorthorninv67cbval, shorthorninv68cbval, shorthorninv69cbval, shorthorninv70cbval, shorthorninv71cbval, shorthorninv72cbval,
    sunflowerinv1cbval, sunflowerinv2cbval, sunflowerinv3cbval, sunflowerinv4cbval, sunflowerinv5cbval, sunflowerinv6cbval, sunflowerinv7cbval, sunflowerinv8cbval, sunflowerinv9cbval, sunflowerinv10cbval, sunflowerinv11cbval, sunflowerinv12cbval, sunflowerinv13cbval, sunflowerinv14cbval, sunflowerinv15cbval, sunflowerinv16cbval, sunflowerinv17cbval, sunflowerinv18cbval, sunflowerinv19cbval, sunflowerinv20cbval, sunflowerinv21cbval, sunflowerinv22cbval, sunflowerinv23cbval, sunflowerinv24cbval, sunflowerinv25cbval, sunflowerinv26cbval, sunflowerinv27cbval, sunflowerinv28cbval, sunflowerinv29cbval, sunflowerinv30cbval, sunflowerinv31cbval, sunflowerinv32cbval, sunflowerinv33cbval, sunflowerinv34cbval, sunflowerinv35cbval, sunflowerinv36cbval, sunflowerinv37cbval, sunflowerinv38cbval, sunflowerinv39cbval, sunflowerinv40cbval, sunflowerinv41cbval, sunflowerinv42cbval, sunflowerinv43cbval, sunflowerinv44cbval, sunflowerinv45cbval, sunflowerinv46cbval, sunflowerinv47cbval, sunflowerinv48cbval, sunflowerinv49cbval, sunflowerinv50cbval, sunflowerinv51cbval, sunflowerinv52cbval, sunflowerinv53cbval, sunflowerinv54cbval, sunflowerinv55cbval, sunflowerinv56cbval, sunflowerinv57cbval, sunflowerinv58cbval, sunflowerinv59cbval, sunflowerinv60cbval, sunflowerinv61cbval, sunflowerinv62cbval, sunflowerinv63cbval, sunflowerinv64cbval, sunflowerinv65cbval, sunflowerinv66cbval, sunflowerinv67cbval, sunflowerinv68cbval, sunflowerinv69cbval, sunflowerinv70cbval, sunflowerinv71cbval, sunflowerinv72cbval, sunflowerinv73cbval, sunflowerinv74cbval, sunflowerinv75cbval, sunflowerinv76cbval, sunflowerinv77cbval, sunflowerinv78cbval, sunflowerinv79cbval, sunflowerinv80cbval,
    upsoninv1cbval, upsoninv2cbval, upsoninv3cbval, upsoninv4cbval, upsoninv5cbval, upsoninv6cbval, upsoninv7cbval, upsoninv8cbval, upsoninv9cbval, upsoninv10cbval, upsoninv11cbval, upsoninv12cbval, upsoninv13cbval, upsoninv14cbval, upsoninv15cbval, upsoninv16cbval, upsoninv17cbval, upsoninv18cbval, upsoninv19cbval, upsoninv20cbval, upsoninv21cbval, upsoninv22cbval, upsoninv23cbval, upsoninv24cbval,
    warblerinv1cbval, warblerinv2cbval, warblerinv3cbval, warblerinv4cbval, warblerinv5cbval, warblerinv6cbval, warblerinv7cbval, warblerinv8cbval, warblerinv9cbval, warblerinv10cbval, warblerinv11cbval, warblerinv12cbval, warblerinv13cbval, warblerinv14cbval, warblerinv15cbval, warblerinv16cbval, warblerinv17cbval, warblerinv18cbval, warblerinv19cbval, warblerinv20cbval, warblerinv21cbval, warblerinv22cbval, warblerinv23cbval, warblerinv24cbval, warblerinv25cbval, warblerinv26cbval, warblerinv27cbval, warblerinv28cbval, warblerinv29cbval, warblerinv30cbval, warblerinv31cbval, warblerinv32cbval,
    washingtoninv1cbval, washingtoninv2cbval, washingtoninv3cbval, washingtoninv4cbval, washingtoninv5cbval, washingtoninv6cbval, washingtoninv7cbval, washingtoninv8cbval, washingtoninv9cbval, washingtoninv10cbval, washingtoninv11cbval, washingtoninv12cbval, washingtoninv13cbval, washingtoninv14cbval, washingtoninv15cbval, washingtoninv16cbval, washingtoninv17cbval, washingtoninv18cbval, washingtoninv19cbval, washingtoninv20cbval, washingtoninv21cbval, washingtoninv22cbval, washingtoninv23cbval, washingtoninv24cbval, washingtoninv25cbval, washingtoninv26cbval, washingtoninv27cbval, washingtoninv28cbval, washingtoninv29cbval, washingtoninv30cbval, washingtoninv31cbval, washingtoninv32cbval, washingtoninv33cbval, washingtoninv34cbval, washingtoninv35cbval, washingtoninv36cbval, washingtoninv37cbval, washingtoninv38cbval, washingtoninv39cbval, washingtoninv40cbval,
    whitehallinv1cbval, whitehallinv2cbval, whitehallinv3cbval, whitehallinv4cbval, whitehallinv5cbval, whitehallinv6cbval, whitehallinv7cbval, whitehallinv8cbval, whitehallinv9cbval, whitehallinv10cbval, whitehallinv11cbval, whitehallinv12cbval, whitehallinv13cbval, whitehallinv14cbval, whitehallinv15cbval, whitehallinv16cbval,
    whitetailinv1cbval, whitetailinv2cbval, whitetailinv3cbval, whitetailinv4cbval, whitetailinv5cbval, whitetailinv6cbval, whitetailinv7cbval, whitetailinv8cbval, whitetailinv9cbval, whitetailinv10cbval, whitetailinv11cbval, whitetailinv12cbval, whitetailinv13cbval, whitetailinv14cbval, whitetailinv15cbval, whitetailinv16cbval, whitetailinv17cbval, whitetailinv18cbval, whitetailinv19cbval, whitetailinv20cbval, whitetailinv21cbval, whitetailinv22cbval, whitetailinv23cbval, whitetailinv24cbval, whitetailinv25cbval, whitetailinv26cbval, whitetailinv27cbval, whitetailinv28cbval, whitetailinv29cbval, whitetailinv30cbval, whitetailinv31cbval, whitetailinv32cbval, whitetailinv33cbval, whitetailinv34cbval, whitetailinv35cbval, whitetailinv36cbval, whitetailinv37cbval, whitetailinv38cbval, whitetailinv39cbval, whitetailinv40cbval, whitetailinv41cbval, whitetailinv42cbval, whitetailinv43cbval, whitetailinv44cbval, whitetailinv45cbval, whitetailinv46cbval, whitetailinv47cbval, whitetailinv48cbval, whitetailinv49cbval, whitetailinv50cbval, whitetailinv51cbval, whitetailinv52cbval, whitetailinv53cbval, whitetailinv54cbval, whitetailinv55cbval, whitetailinv56cbval, whitetailinv57cbval, whitetailinv58cbval, whitetailinv59cbval, whitetailinv60cbval, whitetailinv61cbval, whitetailinv62cbval, whitetailinv63cbval, whitetailinv64cbval, whitetailinv65cbval, whitetailinv66cbval, whitetailinv67cbval, whitetailinv68cbval, whitetailinv69cbval, whitetailinv70cbval, whitetailinv71cbval, whitetailinv72cbval, whitetailinv73cbval, whitetailinv74cbval, whitetailinv75cbval, whitetailinv76cbval, whitetailinv77cbval, whitetailinv78cbval, whitetailinv79cbval, whitetailinv80cbval,
    conetoeinv1cbval, conetoeinv2cbval, conetoeinv3cbval, conetoeinv4cbval,
    duplininv1cbval, duplininv2cbval, duplininv3cbval, duplininv4cbval, duplininv5cbval, duplininv6cbval, duplininv7cbval, duplininv8cbval, duplininv9cbval, duplininv10cbval, duplininv11cbval, duplininv12cbval, duplininv13cbval, duplininv14cbval, duplininv15cbval, duplininv16cbval, duplininv17cbval, duplininv18cbval, duplininv19cbval, duplininv20cbval, duplininv21cbval,
    wayne1inv1cbval, wayne1inv2cbval, wayne1inv3cbval, wayne1inv4cbval,
    wayne2inv1cbval, wayne2inv2cbval, wayne2inv3cbval, wayne2inv4cbval,
    wayne3inv1cbval, wayne3inv2cbval, wayne3inv3cbval, wayne3inv4cbval,
    freightlineinv1cbval, freightlineinv2cbval, freightlineinv3cbval, freightlineinv4cbval, freightlineinv5cbval, freightlineinv6cbval, freightlineinv7cbval, freightlineinv8cbval, freightlineinv9cbval, freightlineinv10cbval, freightlineinv11cbval, freightlineinv12cbval, freightlineinv13cbval, freightlineinv14cbval, freightlineinv15cbval, freightlineinv16cbval, freightlineinv17cbval, freightlineinv18cbval,
    hollyswampinv1cbval, hollyswampinv2cbval, hollyswampinv3cbval, hollyswampinv4cbval, hollyswampinv5cbval, hollyswampinv6cbval, hollyswampinv7cbval, hollyswampinv8cbval, hollyswampinv9cbval, hollyswampinv10cbval, hollyswampinv11cbval, hollyswampinv12cbval, hollyswampinv13cbval, hollyswampinv14cbval, hollyswampinv15cbval, hollyswampinv16cbval,
    pginv1cbval, pginv2cbval, pginv3cbval, pginv4cbval, pginv5cbval, pginv6cbval, pginv7cbval, pginv8cbval, pginv9cbval, pginv10cbval, pginv11cbval, pginv12cbval, pginv13cbval, pginv14cbval, pginv15cbval, pginv16cbval, pginv17cbval, pginv18cbval,
    cougarinv1cbval, cougarinv2cbval, cougarinv3cbval, cougarinv4cbval, cougarinv5cbval, cougarinv6cbval, cougarinv7cbval, cougarinv8cbval, cougarinv9cbval, cougarinv10cbval, cougarinv11cbval, cougarinv12cbval, cougarinv13cbval, cougarinv14cbval, cougarinv15cbval, cougarinv16cbval, cougarinv17cbval, cougarinv18cbval, cougarinv19cbval, cougarinv20cbval, cougarinv21cbval, cougarinv22cbval, cougarinv23cbval, cougarinv24cbval, cougarinv25cbval, cougarinv26cbval, cougarinv27cbval, cougarinv28cbval, cougarinv29cbval, cougarinv30cbval
]

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