#AE API GUI
import pyodbc
from datetime import datetime
from tkinter import *
from tkinter import messagebox
import atexit
import time
import threading
import numpy as np
from datetime import timedelta
from datetime import date
from tkinter import simpledialog
import ctypes
from icecream import ic
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import os

#Number of Data points to check
breaker_pulls = 10
meter_pulls = 15
voltage_check = 5 

master_List_Sites = [('Bishopville II', 36, 'bishopvilleII'), ('Bluebird', 24, 'bluebird'), ('Bulloch 1A', 24, 'bulloch1a'), ('Bulloch 1B', 24, 'bulloch1b'), ('Cardinal', 59, 'cardinal'),
                     ('Cherry', 4, 'cherry'), ('Conetoe', 4, 'conetoe'), ('Cougar', 30, 'cougar'), ('Duplin', 21, 'duplin'), ('Elk', 43, 'elk'), ('Freight Line', 18, 'freightline'), ('Gray Fox', 40, 'grayfox'),
                      ('Harding', 24, 'harding'), ('Harrison', 43, 'harrison'), ('Hayes', 26, 'hayes'), ('Hickory', 2, 'hickory'), ('Hickson', 16, 'hickson'), ('Holly Swamp', 16, 'hollyswamp'),
                       ('Jefferson', 64, 'jefferson'), ('Marshall', 16, 'marshall'), ('McLean', 40, 'mcLean'), ('Ogburn', 16, 'ogburn'), ('PG', 18, 'pg'), ('Richmond', 24, 'richmond'),
                        ('Shorthorn', 72, 'shorthorn'), ('Sunflower', 80, 'sunflower'), ('Tedder', 16, 'tedder'), ('Thunderhead', 16, 'thunderhead'), ('Upson', 24, 'upson'), 
                        ('Van Buren', 17, 'vanburen'), ('Violet', 2, 'violet'), ('Warbler', 32, 'warbler'), ('Washington', 40, 'washington'), ('Wayne 1', 4, 'wayne1'),
                        ('Wayne 2', 4, 'wayne2'), ('Wayne 3', 4, 'wayne3'), ('Wellons', 6, 'wellons'), ('Whitehall', 16, 'whitehall'), ('Whitetail', 80, 'whitetail')]

has_breaker = ['Bishopville II', 'Cardinal', 'Cherry', 'Elk', 'Gray Fox', 'Harding', 'Harrison', 'Hayes', 'Hickory', 'Hickson', 'Jefferson', 'Marshall', 'McLean', 'Ogburn', 
               'Shorthorn', 'Sunflower', 'Tedder', 'Thunderhead', 'Warbler', 'Washington', 'Whitehall', 'Whitetail']


tables = []
breaker_data = {}
meter_data = {}
poa_data = {}
all_CBs = []


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
        start = time.time()
        while not self._stop_event.is_set() and self._elapsed < self._timeout:
            if self._pause_event.is_set():
                time.sleep(0.1)
                self._elapsed += time.time() - start
                start = time.time()
            else:
                start = time.time()
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



def email_notification(SiteName, status, device, poa, amps):
    sender_email = 'omops@narenco.com'
    test = 'joseph.lang@narenco.com'
    one = 'brandon.arrowood@narenco.com'
    two = 'jayme.orrock@narenco.com'
    three = 'newman.segars@narenco.com'
    admin = ['newman.segars@narenco.com', 'brandon.arrowood@narenco.com', 'jayme.orrock@narenco.com', 'joseph.lang@narenco.com']
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    with open(r"G:\Shared drives\O&M\NCC Automations\Credentials\app credentials.json", 'r') as credsfile:
        creds = json.load(credsfile)
    smtp_password = creds['credentials']['weekendEmail']

    msg = MIMEMultipart()
    msg['From'] = sender_email
    
    msg['To'] = ' , '.join(admin)
    #msg['To'] = test

    msg['Subject'] = f"{SiteName}, Outage"

    if poa == 9999 or poa == -1:
        poa = "No Comms"
    if amps:
        amp_data_str = '\n'.join(str(data) for data in amps)
    html_body_breaker = f"""<div style="color:black;">
                            <p>Hello Admins,</p>
                            
                            <p>{SiteName} is OFFLINE according to the {device}! Utility Voltage {status}. This Message is Auto-Generated.
                            <br>POA: {poa} W/M²
                            <br>Please Investigate the Outage on Also Energy remotely!</p>
                            <p>Amp Data [A], [B], [C]: {amp_data_str}</p>

                            <p>Thank you,
                            <br>NCC AE API</p>
                            </div>"""

    # Create a MIMEText object with HTML content
    text = MIMEText(html_body_breaker, 'html')
    msg.attach(text)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, smtp_password)
        server.send_message(msg)

def connect_db():
    global c, dbconn_str, dbconnection, db
    # Create a connection to the Access database
    dbconn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\OMOPS\OneDrive - Narenco\Documents\AE API DB.accdb;'
    dbconnection = pyodbc.connect(dbconn_str)
    c = dbconnection.cursor()
    db = r"C:\Users\OMOPS\OneDrive - Narenco\Documents\AE API DB.accdb"


def update_breaker_status():    
    #ic(breaker_data)
    curtime = datetime.now()
    compare_time = curtime - timedelta(hours=4)   
    h_time = curtime.hour
    for site, inv_num, var in master_List_Sites:
        try: #Defining POA for meter KW notification
            poa = max(poa_data[f'{site} POA Data'])[0]
        except Exception:
            if 8 < h_time < 15:
                poa = 9999
            else:
                poa = -1
        metercomms = max(meter_data[f'{site} Meter Data'][i][6] for i in range(meter_pulls))
        if site == "Violet":
            #Meter Check
            data = np.array(meter_data[f'{site} Meter Data'])
            lastUpload_col = data[:, 6]
            amps_columns = data[:, 3:6]  # Extract Amps Columns
            if all(tim > compare_time for tim in lastUpload_col):
                if any(np.all(amps_columns[:, j] == 0) for j in range(amps_columns.shape[1])):
                    amp_data = [amps_columns[:,j] for j in range(amps_columns.shape[1])]
                    if globals()[f'{var}MeterOnOffval'].get() == False:
                        if metercomms > compare_time:
                            if any(meter_data[f'{site} Meter Data'][i][j] > 5 for i in range(voltage_check) for j in range(3)):
                                status = "currently within parameters, but may have been lost briefly"
                                device = "Meter Amps"
                            else:
                                status = "Lost"
                                device = "Meter Amps"
                        else:
                            status = "Unknown, Lost Comms with Meter"
                            device = "Meter"
                        globals()[f'{var}MeterOnOff'].select()
                        globals()[f'{var}MeterOnOff'].config(bg='Red')
                        email_notification(site, status, device, poa, amp_data)
                elif np.mean([row[7] for row in data if row[7] is not None]) < 2:
                    if globals()[f'{var}MeterOnOffval'].get() == False:
                        if metercomms > compare_time:
                            if any(meter_data[f'{site} Meter Data'][i][j] > 5 for i in range(voltage_check) for j in range(3)):
                                status = "currently within parameters, but may have been lost briefly"
                                device = "Meter kW"
                            else:
                                status = "Lost"
                                device = "Meter kW"
                        else:
                            status = "Unknown, Lost Comms with Meter"
                            device = "Meter kW"
                        globals()[f'{var}MeterOnOff'].select()
                        globals()[f'{var}MeterOnOff'].config(bg='Red')
                        if device == "Meter kW" and status == "currently within parameters, but may have been lost briefly":
                            if poa > 100:
                                email_notification(site, status, device, poa, None)
                        else:
                            email_notification(site, status, device, poa, None)
                else:
                    globals()[f'{var}MeterOnOff'].deselect()
                    globals()[f'{var}MeterOnOff'].config(bg='Green')
            else:
                globals()[f'{var}MeterOnOff'].select()
                globals()[f'{var}MeterOnOff'].config(bg='Red')
                if globals()[f'{var}MeterOnOffval'].get() == False:
                    status = "Unknown, Comms consistently reporting last good data Upload as 4+ hrs ago."
                    device = "Meter"
                    email_notification(site, status, device, poa, None)

            #Breaker Check
            if all(not breaker_data['Violet Breaker Data 1'][i][0] for i in range(breaker_pulls)):
                if violetBreakerOnOffval.get() == False:
                    device = "Breaker"
                    email_notification("Violet 1", status, device, poa, None)
                    violetBreakerOnOff.select()
                    globals()[f'{var}BreakerOnOff'].config(bg='Red')
            else:
                violetBreakerOnOff.deselect()
                globals()[f'{var}BreakerOnOff'].config(bg='Green')
            #Breaker 2 Check
            if all(not breaker_data['Violet Breaker Data 2'][i][0] for i in range(breaker_pulls)):
                if violet2BreakerOnOffval.get() == False:
                    device = "Breaker"
                    email_notification("Violet 2", status, device, poa, None)
                    violet2BreakerOnOff.select()
                    globals()[f'{var}2BreakerOnOff'].config(bg='Red')

            else:
                violet2BreakerOnOff.deselect()
                globals()[f'{var}2BreakerOnOff'].config(bg='Green')

        else: #Meter Check for all other Sites besides Violet
            data = np.array(meter_data[f'{site} Meter Data'])
            lastUpload_col = data[:, 6]
            amps_columns = data[:, 3:6]  # Extract Amps Columns
            if all(tim > compare_time for tim in lastUpload_col):
                if any(np.all(amps_columns[:, j] == 0) for j in range(amps_columns.shape[1])):
                    amp_data = [amps_columns[:,j] for j in range(amps_columns.shape[1])]
                    if globals()[f'{var}MeterOnOffval'].get() == False:
                        if metercomms > compare_time:
                            if any(meter_data[f'{site} Meter Data'][i][j] > 5 for i in range(voltage_check) for j in range(3)):
                                status = "currently within parameters, but may have been lost briefly"
                                device = "Meter Amps"
                            else:
                                status = "Lost"
                                device = "Meter Amps"
                        else:
                            status = "Unknown, Lost Comms with Meter"
                            device = "Meter Amps"
                        globals()[f'{var}MeterOnOff'].select()
                        globals()[f'{var}MeterOnOff'].config(bg='Red')
                        email_notification(site, status, device, poa, amp_data)
                elif np.mean([row[7] for row in data if row[7] is not None]) < 2:
                    if globals()[f'{var}MeterOnOffval'].get() == False:
                        if metercomms > compare_time:
                            if any(meter_data[f'{site} Meter Data'][i][j] > 5 for i in range(voltage_check) for j in range(3)):
                                status = "currently within parameters, but may have been lost briefly"
                                device = "Meter kW"
                            else:
                                status = "Lost"
                                device = "Meter kW"
                        else:
                            status = "Unknown, Lost Comms with Meter"
                            device = "Meter kW"
                        globals()[f'{var}MeterOnOff'].select()
                        globals()[f'{var}MeterOnOff'].config(bg='Red')
                        if device == "Meter kW" and status == "currently within parameters, but may have been lost briefly":
                            if poa > 100:
                                email_notification(site, status, device, poa, None)
                        else:
                            email_notification(site, status, device, poa, None)
                else:
                    globals()[f'{var}MeterOnOff'].deselect()
                    globals()[f'{var}MeterOnOff'].config(bg='Green')
            else:
                globals()[f'{var}MeterOnOff'].select()
                globals()[f'{var}MeterOnOff'].config(bg='Red')
                if globals()[f'{var}MeterOnOffval'].get() == False:
                    status = "Unknown, Comms consistently reporting last good data Upload as 4+ hrs ago."
                    device = "Meter"
                    email_notification(site, status, device, poa, None)

        if site in has_breaker: #Breaker Check
            if all(not breaker_data[f'{site} Breaker Data'][i][0] for i in range(breaker_pulls)):
                if globals()[f'{var}BreakerOnOffval'].get() == False:
                    if metercomms > compare_time:
                        print(meter_data[f'{site} Meter Data'][i][3] for i in range(5))
                        if any(meter_data[f'{site} Meter Data'][i][j] > 5 for i in range(voltage_check) for j in range(3)):
                            status = "currently within parameters, but may have been lost briefly"
                            device = "Breaker"
                        else:
                            status = "Lost"
                            device = "Breaker"
                    else:
                        status = "Unknown, Lost Comms with Meter"
                        device = "Breaker"
                    email_notification(site, status, device, poa, None)
                    globals()[f'{var}BreakerOnOff'].select()
                    globals()[f'{var}BreakerOnOff'].config(bg='Red')

            else:
                globals()[f'{var}BreakerOnOff'].deselect()  
                globals()[f'{var}BreakerOnOff'].config(bg='Green')

    print("Finished")
    ctime = datetime.now()
    hh_mm = ctime.strftime('%H:%M')
    timeLabel.config(text=f"Updated: {hh_mm}", font=("_TkDefaultFont", 10, 'bold'))
    global gui_update_timer
    gui_update_timer = PausableTimer(300, db_to_dict)
    gui_update_timer.start()


def db_to_dict():
    time.sleep(5)
    print("Starting")
    connect_db()

    # Calculate the time 15 minutes ago from the current time
    current_time = datetime.now()
    time_1_hr_ago = current_time - timedelta(hours=1, minutes=30)

    # Format the datetime for SQL query
    formatted_time = time_1_hr_ago.strftime('%m/%d/%Y %H:%M:%S')

    for tb in c.tables(tableType='TABLE'):
        tables.append(tb)
    #ic(tables)
    excluded_tables = ["1)Sites", "2)Breakers", "3)Meters", "4)Inverters", "5)POA"]
    
    for table in tables:
        table_name = table.table_name
        if "Breaker" in table_name and table_name not in excluded_tables:
            c.execute(f"SELECT TOP {breaker_pulls} [Status] FROM [{table_name}] ORDER BY [Date & Time] DESC")
            breaker_rows = c.fetchall()
            breaker_data[table_name] = breaker_rows
        elif "Meter" in table_name and table_name not in excluded_tables and 'Wellons' not in table_name:
            c.execute(f"SELECT TOP {meter_pulls} [Volts A], [Volts B], [Volts C], [Amps A], [Amps B], [Amps C], [lastUpload], kW FROM [{table_name}] ORDER BY [Date & Time] DESC")
            meter_rows = c.fetchall()
            meter_data[table_name] = meter_rows
        elif "Meter" in table_name and 'Wellons' in table_name and table_name not in excluded_tables:
            c.execute(f"SELECT TOP 60 [Volts A], [Volts B], [Volts C], [Amps A], [Amps B], [Amps C], [lastUpload], kW FROM [{table_name}] ORDER BY [Date & Time] DESC")
            meter_rows = c.fetchall()
            meter_data[table_name] = meter_rows
        elif "POA" in table_name and table_name not in excluded_tables:
            c.execute(f"SELECT TOP 3 [W/M²] FROM [{table_name}] WHERE lastUpload >= ? ORDER BY [Date & Time] DESC", formatted_time)
            poadatap = c.fetchall()
            poa_data[table_name] = poadatap

    #ic(breaker_data)
    comptime = meter_data['Freight Line Meter Data'][0][6]
    comptime2 = meter_data['Harding Meter Data'][0][6]
    db_update_time = 15
    timecompare = current_time - timedelta(minutes=db_update_time)
    print(f"Times: {timecompare} | {comptime} | {comptime2}")
    if timecompare > comptime:
        if timecompare > comptime2:
            os.startfile(r"G:\Shared drives\O&M\NCC Automations\Notification System\API Data Pull, Multi.py")
            time.sleep(120)
    print("Pulled Data calling check to send")
    update_breaker_status()


myappid = 'AE.API.Data.GUI'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

root = Tk()
root.title("Emailing Admin")
try:
    root.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
root.wm_attributes("-topmost", True)

infoframe = Frame(root)
infoframe.pack()

infoLabel = Label(infoframe, text= "I check every 5 minutes for Site Outages based on the AE API DB.acc")
resultLabel = Label(infoframe, text = "If I find one, then I'll notify Brandon, Jayme, and Newman")
ctime = datetime.now()
hh_mm = ctime.strftime('%H:%M')
timeLabel = Label(infoframe, text= f"Updated: {hh_mm}", font=("_TkDefaultFont", 10, 'bold'))


infoLabel.grid(row=0, column=0, columnspan=2)
resultLabel.grid(row=1, column=0, columnspan=2)
timeLabel.grid(row=2, column=0)




guiframe = Frame(root)
guiframe.pack()

num_columns = 4
# Initialize row and column counters
row = 0
column = 0

for site, inv, var in master_List_Sites:
    if site != "Violet":
        # Create a Label for the site
        site_label = Label(guiframe, text=site)
        site_label.grid(row=row, column=column)
        
        # Create BooleanVars for Meter and Breaker Checkbuttons
        globals()[f'{var}MeterOnOffval'] = BooleanVar(value=True)
        globals()[f'{var}BreakerOnOffval'] = BooleanVar(value=True)
        
        # Create Meter Checkbutton
        globals()[f'{var}MeterOnOff'] = Checkbutton(guiframe, text='M', variable=globals()[f'{var}MeterOnOffval'])
        globals()[f'{var}MeterOnOff'].grid(row=row+1, column=column)
        all_CBs.append(globals()[f'{var}MeterOnOffval'])
        
        # Create Breaker Checkbutton
        if site in has_breaker:
            globals()[f'{var}BreakerOnOff'] = Checkbutton(guiframe, text='B', variable=globals()[f'{var}BreakerOnOffval'])
            globals()[f'{var}BreakerOnOff'].grid(row=row+2, column=column)
            all_CBs.append(globals()[f'{var}BreakerOnOffval'])

        
        
        # Update row and column counters
        row += 3  # Move to the next set of rows for the next site
        if row >= len(master_List_Sites) // num_columns * 3:
            row = 0
            column += 1

# Handle the special case for Violet
violet2_label = Label(guiframe, text="Violet 2")
violet2_label.grid(row=28, column=1, sticky=W)

violet2BreakerOnOffval = BooleanVar(value=True)
all_CBs.append(violet2BreakerOnOffval)


violet2BreakerOnOff = Checkbutton(guiframe, text="B", variable=violet2BreakerOnOffval)
violet2BreakerOnOff.grid(row=29, column=1)

violet_label = Label(guiframe, text="Violet")
violet_label.grid(row=28, column=0)

violetBreakerOnOffval = BooleanVar(value=True)
all_CBs.append(violetBreakerOnOffval)

violetBreakerOnOff = Checkbutton(guiframe, text="B", variable=violet2BreakerOnOffval)
violetBreakerOnOff.grid(row=29, column=0)

violetMeterOnOffval = BooleanVar(value=True)
all_CBs.append(violetMeterOnOffval)
violetMeterOnOff = Checkbutton(guiframe, text='Meter', variable=violetMeterOnOffval)
violetMeterOnOff.grid(row=30, column=0, columnspan=2)


root.after(1000, db_to_dict)

def destroy_window():
    root.destroy()
#root.after(20000, destroy_window)

root.mainloop()

