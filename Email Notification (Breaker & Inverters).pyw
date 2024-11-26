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
import os
import json

master_List_Sites = [('Bishopville II', 36, 'bishopvilleII'), ('Bluebird', 24, 'bluebird'), ('Bulloch 1A', 24, 'bulloch1a'), ('Bulloch 1B', 24, 'bulloch1b'), ('Cardinal', 59, 'cardinal'),
                     ('Cherry', 4, 'cherry'), ('Conetoe', 4, 'conetoe'), ('Duplin', 21, 'duplin'), ('Freight Line', 18, 'freightline'), ('Gray Fox', 40, 'grayfox'),
                      ('Harding', 24, 'harding'), ('Harrison', 43, 'harrison'), ('Hayes', 26, 'hayes'), ('Hickory', 2, 'hickory'), ('Hickson', 16, 'hickson'), ('Holly Swamp', 16, 'hollyswamp'),
                       ('Jefferson', 64, 'jefferson'), ('Marshall', 16, 'marshall'), ('McLean', 40, 'mcLean'), ('Ogburn', 16, 'ogburn'), ('PG', 18, 'pg'), ('Richmond', 24, 'richmond'),
                        ('Shorthorn', 72, 'shorthorn'), ('Sunflower', 80, 'sunflower'), ('Tedder', 16, 'tedder'), ('Thunderhead', 16, 'thunderhead'), ('Upson', 24, 'upson'), 
                        ('Van Buren', 17, 'vanburen'), ('Violet', 2, 'violet'), ('Warbler', 32, 'warbler'), ('Washington', 40, 'washington'), ('Wayne 1', 4, 'wayne1'),
                        ('Wayne 2', 4, 'wayne2'), ('Wayne 3', 4, 'wayne3'), ('Wellons', 6, 'wellons'), ('Whitehall', 16, 'whitehall'), ('Whitetail', 80, 'whitetail')]
has_breaker = ['Bishopville II', 'Cardinal', 'Cherry', 'Gray Fox', 'Harding', 'Harrison', 'Hayes', 'Hickory', 'Hickson', 'Jefferson', 'Marshall', 'McLean', 'Ogburn', 
               'Shorthorn', 'Sunflower', 'Tedder', 'Thunderhead', 'Warbler', 'Washington', 'Whitehall', 'Whitetail']
all_CBs = []
comm_data = {}
inv_data = {}
POA_data = {}
breaker_data = {}
meter_data = {}
tables = []
STATE_FILE = r"G:\Shared drives\O&M\NCC Automations\Notification System\EmailCheckBoxState.json"
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

def save_cb_state():
    state = [var.get() for var in all_CBs]
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def load_cb_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            for var, value in zip(all_CBs, state):
                var.set(value)

def destroy_window():
    root.destroy()

def email_notification(SiteName, issue, inv, utility_status):
    sender_email = 'omops@narenco.com'
    test = 'joseph.lang@narenco.com'
    one = 'brandon.arrowood@narenco.com'
    two = 'jayme.orrock@narenco.com'
    three = 'newman.segars@narenco.com'
    admin = ['newman.segars@narenco.com', 'brandon.arrowood@narenco.com', 'jayme.orrock@narenco.com']
    opsTeam = ['newman.segars@narenco.com', 'brandon.arrowood@narenco.com', 'jayme.orrock@narenco.com', 'joseph.lang@narenco.com', 'jacob.budd@narenco.com']
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_password = 'txkc xaxd wihf gfdc'

    msg = MIMEMultipart()
    msg['From'] = sender_email
    #msg['To'] = ' , '.join(opsTeam)
    msg['To'] = one
    if issue == "Breaker":
        msg['Subject'] = f"{SiteName}, Breaker Open"

        html_body = f"""<div style="color:black;">
                                <p>Hello Admins,</p>
                                
                                <p>{SiteName} breaker is OPEN! Utility Voltage {utility_status}. This Message is Auto-Generated.
                                <br>Please Investigate the Outage!<br></p>
                                
                                <p>Thank you,
                                <br>NCC AE API<br></p>
                                </div>"""
    elif issue == "Meter":
        msg['Subject'] = f"{SiteName}, Meter Outage"

        html_body = f"""<div style="color:black;">
                                <p>Hello Admins,</p>
                                
                                <p>{SiteName} Meter is OFFLINE! Utility Voltage {utility_status}. This Message is Auto-Generated.
                                <br>Please Investigate the Outage!<br></p>
                                
                                <p>Thank you,
                                <br>NCC AE API<br></p>
                                </div>"""
    elif issue == "Inverter Comms":
        msg['Subject'] = f"{SiteName}, Inverter {inv} Lost Comms"

        html_body = f"""<div style="color:black;">
                                <p>Hello Admins,</p>
                                
                                <p>{SiteName} Inverter {inv} Lost All Comms 4 Hours ago! This Message is Auto-Generated.
                                <br>Please Investigate the Outage!<br></p>
                                
                                <p>Thank you,
                                <br>NCC AE API<br></p>
                                </div>"""
    elif issue == "Inverter Good":
        msg['Subject'] = f"{SiteName}, Inverter {inv} Offline"

        html_body = f"""<div style="color:black;">
                                <p>Hello Admins,</p>
                                
                                <p>{SiteName} Inverter {inv} is Offline with Good DC Voltage! This Message is Auto-Generated.
                                <br>Please Investigate the Outage!<br></p>
                                
                                <p>Thank you,
                                <br>NCC AE API<br></p>
                                </div>"""
    elif issue == "Inverter Bad":
        msg['Subject'] = f"{SiteName}, Inverter {inv} Offline"

        html_body = f"""<div style="color:black;">
                                <p>Hello Admins,</p>
                                
                                <p>{SiteName} Inverter {inv} is Offline with Bad DC Voltage! This Message is Auto-Generated.
                                <br>Please Investigate the Outage!<br></p>
                                
                                <p>Thank you,
                                <br>NCC AE API<br></p>
                                </div>"""

    # Create a MIMEText object with HTML content
    text = MIMEText(html_body, 'html')
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
    #Save because we may forget to.
    save_cb_state()
    # Get the current hour
    time_date_compare = (datetime.now() - timedelta(hours=4))
    current_hour = datetime.now().hour
    ic(breaker_data)
      
    for site, inv_num, var in master_List_Sites:
        if globals()[f'{var}poacbval'].get() == True:
            if 10 <= current_hour < 18:
                poa = 9999
            else:
                poa = 50
        else:
            poa = POA_data[f'{site} POA Data'][0]

        compare_time = datetime.now() - timedelta(hours=4)   
        r = 1 
        issue = "Breaker"
        if site == "Violet":
            if meter_data['Violet Meter Data'][0][6] > compare_time:
                if all(meter_data['Violet Meter Data'][i][j] > 5 for i in range(10) for j in range(3)):
                    status = "currently within parameters, but may have been lost briefly"
                else:
                    status = "Lost"
            else:
                status = "Unknown, Lost Comms with Meter"
            if all(not breaker_data['Violet Breaker Data 1'][i][0] for i in range(10)):
                if violetOnOffcbval.get() == False:
                    email_notification("Violet 1", issue, r, status)
                    violetOnOffcb.select()
            else:
                violetOnOffcb.deselect()
            if all(not breaker_data['Violet Breaker Data 2'][i][0] for i in range(10)):
                if violet2OnOffcbval.get() == False:
                    email_notification("Violet 2", issue, r, status)
                    violet2OnOffcb.select()
            else:
                violet2OnOffcb.deselect()
        elif site in ['Cardinal', 'Harrison', 'Hayes', 'Warbler']:
            issue = "Meter"
            data = np.array(meter_data[f'{site} Meter Data'])
            lastUpload_col = data[:, 6]
            amps_columns = data[:, 3:6]  # Extract Amps Columns
            if all(tim > compare_time for tim in lastUpload_col):
                if any(np.all(amps_columns[:, j] == 0) for j in range(amps_columns.shape[1])):
                    if globals()[f'{var}OnOffval'].get() == False:
                        if meter_data[f'{site} Meter Data'][0][6] > compare_time:
                            if all(meter_data[f'{site} Meter Data'][i][j] > 5 for i in range(10) for j in range(3)):
                                status = "currently within parameters, but may have been lost briefly"
                            else:
                                status = "Lost"
                        else:
                            status = "Unknown, Lost Comms with Meter"
                        globals()[f'{var}OnOff'].select()
                        email_notification(site, issue, r, status)
                else:
                    globals()[f'{var}OnOff'].deselect()
            else:
                globals()[f'{var}OnOff'].select()
                if globals()[f'{var}OnOffval'].get() == False:
                    status = "Unknown, Lost Comms with Meter"
                    email_notification(site, issue, r, status)
        elif site in has_breaker:
            issue = "Breaker"
            if all(not breaker_data[f'{site} Breaker Data'][i][0] for i in range(10)):
                if globals()[f'{var}OnOffcbval'].get() == False:
                    if meter_data[f'{site} Meter Data'][0][6] > compare_time:
                        if all(meter_data[f'{site} Meter Data'][i][j] > 5 for i in range(10) for j in range(3)):
                            status = "currently within parameters, but may have been lost briefly"
                        else:
                            status = "Lost"
                    else:
                        status = "Unknown, Lost Comms with Meter"
                    globals()[f'{var}OnOffcb'].select()
                    email_notification(site, issue, r, status)
            else:
                globals()[f'{var}OnOffcb'].deselect()  

        #INV Update
        timenow = datetime.now()
        utility_status = "Used only in Breaker Notification. Unused Variable from now on. Simply a place holder in the Email notification Function."
        if site == "Violet":
            if violetOnOffcbval.get() == False and violet2OnOffcbval.get() == False:
                siteStatus = False
            else:
                siteStatus = True
        else:
            if globals()[f'{var}OnOffcbval'].get() == False:
                siteStatus = False
            else:
                siteStatus = True
        if siteStatus == False and 18 > timenow.hour >= 10:
            if site == "Duplin":
                for r in range(1, 4):
                    data = inv_data[f'{site} Central INV {r} Data']
                    total_dcv = sum(row[4] for row in data)
                    avg_dcv = total_dcv / len(data)
                    if comm_data[f'{site} Central INV {r} Data'][0] > time_date_compare:
                        if all(point[3] <= 1 for point in data):
                            if avg_dcv > 100:
                                if poa > 250 and globals()[f'{var}inv{r}OnOffcbval'].get() == False:
                                    globals()[f'{var}inv{r}OnOffcb'].select()
                                    issue = "Inverter Good"
                                    email_notification(site, issue, r, utility_status)
                            else:
                                if poa > 250 and globals()[f'{var}inv{r}OnOffcbval'].get() == False:
                                    issue = "Inverter Bad"
                                    globals()[f'{var}inv{r}OnOffcb'].select()
                                    email_notification(site, issue, r, utility_status)
                        else:
                            globals()[f'{var}inv{r}OnOffcb'].deselect()    
                    elif globals()[f'{var}inv{r}OnOffcbval'].get() == False:
                        issue = "Inverter Comms"
                        globals()[f'{var}inv{r}OnOffcb'].select()
                        email_notification(site, issue, r, utility_status)
                        #Email Notification Comm Outage 4 hrs
                for r in range(1, 19):
                    data = inv_data[f'{site} String INV {r} Data']
                    total_dcv = sum(row[4] for row in data)
                    avg_dcv = total_dcv / len(data)
                    if comm_data[f'{site} String INV {r} Data'][0] > time_date_compare:
                        if all(point[3] <= 1 for point in data):
                            if avg_dcv > 100:
                                if poa > 250 and globals()[f'{var}inv{r+3}OnOffcbval'].get() == False:
                                    globals()[f'{var}inv{r+3}OnOffcb'].select()
                                    issue = "Inverter Good"
                                    email_notification(site, issue, r, utility_status)
                            else:
                                if poa > 250 and globals()[f'{var}inv{r+3}OnOffcbval'].get() == False:
                                    issue = "Inverter Bad"
                                    globals()[f'{var}inv{r+3}OnOffcb'].select()
                                    email_notification(site, issue, r, utility_status)
                        else:
                            globals()[f'{var}inv{r+3}OnOffcb'].deselect()
                    elif globals()[f'{var}inv{r+3}OnOffcbval'].get() == False:
                        issue = "Inverter Comms"
                        email_notification(site, issue, r, utility_status)
                        globals()[f'{var}inv{r+3}OnOffcb'].select()
            else:
                for r in range(1, inv_num + 1):
                    data = inv_data[f'{site} INV {r} Data']
                    total_dcv = sum(row[4] for row in data)
                    avg_dcv = total_dcv / len(data)
                    if comm_data[f'{site} INV {r} Data'][0] > time_date_compare:
                        if all(point[3] <= 1 for point in data):
                            if avg_dcv > 100:
                                if poa > 250 and globals()[f'{var}inv{r}OnOffcbval'].get() == False:
                                    globals()[f'{var}inv{r}OnOffcb'].select()
                                    issue = "Inverter Good"
                                    email_notification(site, issue, r, utility_status)
                            else:
                                if poa > 250 and globals()[f'{var}inv{r}OnOffcbval'].get() == False:
                                    issue = "Inverter Bad"
                                    globals()[f'{var}inv{r}OnOffcb'].select()
                                    email_notification(site, issue, r, utility_status)
                        else:
                            globals()[f'{var}inv{r}OnOffcb'].deselect()
                    elif globals()[f'{var}inv{r}OnOffcbval'].get() == False:
                        issue = "Inverter Comms"
                        email_notification(site, issue, r, utility_status)
                        globals()[f'{var}inv{r}OnOffcb'].select() #Email Notification Comm Outage 4 hrs




    print("Finished")
    ctime = datetime.now()
    hh_mm = ctime.strftime('%H:%M')
    timeLabel.config(text=f"Updated: {hh_mm}", font=("_TkDefaultFont", 12, 'bold'))
    global gui_update_timer
    gui_update_timer = PausableTimer(300, db_to_dict)

    gui_update_timer.start()


def db_to_dict():
    connect_db()
    for tb in c.tables(tableType='TABLE'):
        tables.append(tb)
    #ic(tables)
    excluded_tables = ["1)Sites", "2)Breakers", "3)Meters", "4)Inverters", "5)POA"]


    for table in tables:
        table_name = table.table_name
        if "Breaker" in table_name and table_name not in excluded_tables:
            #Select 8 = 15 Mins
            c.execute(f"SELECT TOP 10 [Status] FROM [{table_name}] ORDER BY [Date & Time] DESC")
            breaker_rows = c.fetchall()
            breaker_data[table_name] = breaker_rows
        elif "Meter" in table_name and table_name not in excluded_tables:
            #Select 5 = 10 Mins
            c.execute(f"SELECT TOP 10 [Volts A], [Volts B], [Volts C], [Amps A], [Amps B], [Amps C], [lastUpload] FROM [{table_name}] ORDER BY [Date & Time] DESC")
            meter_rows = c.fetchall()
            meter_data[table_name] = meter_rows
        elif "INV" in table_name and table_name not in excluded_tables:
            #SELECT 15 = 30 Mins
            c.execute(f"SELECT TOP 20 * FROM [{table_name}] ORDER BY [Date & Time] DESC")
            inv_rows = c.fetchall()
            inv_data[table_name] = inv_rows
        elif "POA" in table_name and table_name not in excluded_tables:
            c.execute(f"SELECT TOP 1 [W/M²] FROM [{table_name}] ORDER BY [Date & Time] DESC")
            POA_rows = c.fetchone()
            POA_data[table_name] = POA_rows
    #ic(breaker_data)

    for table in tables:
        table_name = table.table_name
        if table_name not in excluded_tables:
            c.execute(f"SELECT TOP 1 lastUpload FROM [{table_name}] ORDER BY [Date & Time] DESC")
            comm_value = c.fetchone()
            comm_data[table_name] = comm_value

    print("Pulled Data calling check to send")
    update_breaker_status()


myappid = 'AE.API.Data.EMAIL'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

root = Tk()
root.title("Emailing Admin")
try:
    root.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
root.wm_attributes("-topmost", True)
infoLabel = Label(root, text= "I check for INV and Breaker Outages every 5 minutes")
resultLabel = Label(root, text = "If I find one, then I'll notify Brandon")
ctime = datetime.now()
hh_mm = ctime.strftime('%H:%M')
timeLabel = Label(root, text= f"Updated: {hh_mm}", font=("_TkDefaultFont", 12, 'bold'))
cb_button = Button(root, text= "Save CB Selections", command= lambda: save_cb_state())
destroy_butt = Button(root, text= "Destroy", command= lambda: destroy_window())



infoLabel.pack()
timeLabel.pack()
resultLabel.pack()
cb_button.pack()
destroy_butt.pack()

gui = Toplevel()
gui.title("CB Pauses Email Notification for listed device")
try:
    gui.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")



for ro, (site, num, var) in enumerate(master_List_Sites):
    #Breakers
    if site != "Violet":
        globals()[f'{var}poacbval'] = BooleanVar() 
        globals()[f'{var}poacb'] = Checkbutton(gui, text= "POA", variable= globals()[f'{var}poacbval'])
        globals()[f'{var}poacb'].grid(row=ro, column= 1, sticky='w')
        all_CBs.append(globals()[f'{var}poacbval'])

        globals()[f'{var}OnOffcbval'] = BooleanVar() 
        globals()[f'{var}OnOffcb'] = Checkbutton(gui, text=site, variable= globals()[f'{var}OnOffcbval'])
        globals()[f'{var}OnOffcb'].grid(row=ro, column= 0, sticky='w')
        all_CBs.append(globals()[f'{var}OnOffcbval'])
        #Inverters
        for inv in range(1, num+1):
            if site != "Duplin":
                globals()[f'{var}inv{inv}OnOffcbval'] = BooleanVar() 
                globals()[f'{var}inv{inv}OnOffcb'] = Checkbutton(gui, text=inv, variable= globals()[f'{var}inv{inv}OnOffcbval'])
                globals()[f'{var}inv{inv}OnOffcb'].grid(row=ro, column=inv+1)
                all_CBs.append(globals()[f'{var}inv{inv}OnOffcbval'])
            else:
                if inv < 4:
                    globals()[f'{var}inv{inv}OnOffcbval'] = BooleanVar() 
                    globals()[f'{var}inv{inv}OnOffcb'] = Checkbutton(gui, text=inv, variable= globals()[f'{var}inv{inv}OnOffcbval'])
                    globals()[f'{var}inv{inv}OnOffcb'].grid(row=ro, column=inv+1)
                    all_CBs.append(globals()[f'{var}inv{inv}OnOffcbval'])
                else:
                    globals()[f'{var}inv{inv}OnOffcbval'] = BooleanVar() 
                    globals()[f'{var}inv{inv}OnOffcb'] = Checkbutton(gui, text=f"S.{(inv-3)}", variable= globals()[f'{var}inv{inv}OnOffcbval'])
                    globals()[f'{var}inv{inv}OnOffcb'].grid(row=ro, column=inv+1)
                    all_CBs.append(globals()[f'{var}inv{inv}OnOffcbval'])


violetOnOffcbval = BooleanVar()
violet2OnOffcbval = BooleanVar()
violetOnOffcb = Checkbutton(gui, text="Violet", variable= violetOnOffcbval)
violetOnOffcb.grid(row=37, column= 0, sticky='w')
violetpoacbval = BooleanVar()
violetpoacb = Checkbutton(gui, text= "POA", variable=violetpoacbval)
violetpoacb.grid(row=37, column=1)
violet2OnOffcb = Checkbutton(gui, text="Violet 2", variable= violet2OnOffcbval)
violet2OnOffcb.grid(row=38, column= 0, sticky='w')

violetinv1OnOffcbval = BooleanVar()
violetinv1OnOffcb = Checkbutton(gui, text="1", variable= violetinv1OnOffcbval)
violetinv1OnOffcb.grid(row=37, column= 2, sticky='w')
violetinv2OnOffcbval = BooleanVar()
violetinv2OnOffcb = Checkbutton(gui, text="2", variable= violetinv2OnOffcbval)
violetinv2OnOffcb.grid(row=37, column= 3, sticky='w')

all_CBs.append(violetOnOffcbval)
all_CBs.append(violet2OnOffcbval)
all_CBs.append(violetinv1OnOffcbval)
all_CBs.append(violetinv2OnOffcbval)
load_cb_state()



root.after(5000, db_to_dict)

#time_window()

#root.after(20000, destroy_window)

root.mainloop()

