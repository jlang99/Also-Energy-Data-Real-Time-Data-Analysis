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
import ctypes, socket
from icecream import ic
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import os, sys

# Add the parent directory ('NCC Automations') to the Python path
# This allows us to import the 'PythonTools' package from there.
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from PythonTools import CREDS, EMAILS, AE_HARDWARE_MAP, PausableTimer #Both of these Variables are Dictionaries with a single layer that holds Personnel data or app passwords



#Number of Data points to check
breaker_pulls = 10
meter_pulls = 15
voltage_check = 5

master_List_Sites = {site for site in AE_HARDWARE_MAP.keys() if site != 'CDIA'}
has_breaker = {site for site, data in AE_HARDWARE_MAP.items() if 'breakers' in data}



tables = []
breaker_data = {}
meter_data = {}
poa_data = {}
all_CBs = []
site_widgets = {}



def notification_period():
    now = datetime.now()
    # weekday() returns 5 for Saturday and 6 for Sunday
    is_weekend = now.weekday() in {5, 6}

    # Check if the time is after 3 PM (15:00) or before 7 AM (07:00)
    is_after_hours = now.hour >= 15 or now.hour < 7

    if is_weekend and is_after_hours:
        return True
    return False

def email_notification(SiteName, status, device, poa, amps):
    sender_email = EMAILS['NCC Desk']
    admin = [EMAILS['Newman Segars'],  EMAILS['Brandon Arrowood'], EMAILS['Jayme Orrock'], EMAILS['Joseph Lang']]
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    smtp_password = CREDS['remoteMonitoring']

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ' , '.join(admin)
    #msg['To'] = test

    msg['Subject'] = f"{SiteName}, Outage"

    if poa == 9999 or poa == -1:
        poa = "No Comms"
    if amps:
        # Determine the maximum width needed for any number in all phases
        max_width = max(len(str(value)) for phase in amps for value in phase)
        
        # Format the amp data with the determined maximum width
        amp_data_str = '\n'.join([
            ' '.join(f"{value:>{max_width}}" for value in phase)
            for phase in amps  
        ])
        html_body_breaker = f"""<div style="color:black;">
                                <p>Hello Admins,</p>
                                
                                <p>{SiteName} is OFFLINE according to the {device}! Utility Voltage {status}. This Message is Auto-Generated.
                                <br>POA: {poa} W/M²
                                <br>Please Investigate the Outage on Also Energy remotely!</p>
                                <p>Amp Data: 
                                <br>A: {amp_data_str.splitlines()[0]}
                                <br>B: {amp_data_str.splitlines()[1]}
                                <br>C: {amp_data_str.splitlines()[2]}</p>

                                
                                <p>Thank you,
                                <br>NCC AE API</p>
                                </div>"""
    else:
        html_body_breaker = f"""<div style="color:black;">
                        <p>Hello Admins,</p>
                        
                        <p>{SiteName} is OFFLINE according to the {device}! Utility Voltage {status}. This Message is Auto-Generated.
                        <br>POA: {poa} W/M²
                        <br>Please Investigate the Outage on Also Energy remotely!</p>
                        

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
    global c, dbconn_str, dbconnection
    hostname = socket.gethostname()
    if hostname == "NAR-OMOps-SQL":
        dbconn_str = (
            r'DRIVER={ODBC Driver 18 for SQL Server};'
            r'SERVER=localhost\SQLEXPRESS;'
            r'DATABASE=NARENCO_O&M_AE;'
            r'Trusted_Connection=yes;'
            r'Encrypt=no;'
        )
    else:
        dbconn_str = (
            r'DRIVER={ODBC Driver 18 for SQL Server};'
            fr'SERVER={CREDS['DB_IP']}\SQLEXPRESS;'
            r'DATABASE=NARENCO_O&M_AE;'
            fr'UID={CREDS['DB_UID']};'
            fr'PWD={CREDS['DB_PWD']};'
            r'Encrypt=no;'
        )
    dbconnection = pyodbc.connect(dbconn_str)
    c = dbconnection.cursor()


def update_breaker_status():    
    period_check = notification_period()
    #ic(breaker_data)
    curtime = datetime.now()
    compare_time = curtime - timedelta(hours=4)   
    h_time = curtime.hour
    for site, site_data_dict in site_widgets.items():
        if site == 'Violet 2':
            continue
        try: #Defining POA for meter KW notification
            poa = max(poa_data[f'{site} POA Data'])[0]
        except Exception:
            if 8 < h_time < 15:
                poa = 9999
            else:
                poa = -1
        site_meter_data = meter_data.get(f'{site} Meter Data', [])
        metercomms = max(row[6] for row in site_meter_data) if site_meter_data else None
        if site == "Violet":
            #Meter Check
            data = np.array(meter_data[f'{site} Meter Data'])
            if data.ndim < 2:
                continue
            lastUpload_col = data[:, 6]
            amps_columns = data[:, 3:6]  # Extract Amps Columns
            if all(tim > compare_time for tim in lastUpload_col):
                if any(np.all(amps_columns[:, j] == 0) for j in range(amps_columns.shape[1])):
                    amp_data = [amps_columns[:,j] for j in range(amps_columns.shape[1])]
                    if not site_data_dict['meter_var'].get():
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
                        site_data_dict['meter_cb'].select()
                        site_data_dict['meter_cb'].config(bg='Red')
                        if period_check:
                            email_notification(site, status, device, poa, amp_data)
                elif np.mean([row[7] for row in data if row[7] is not None]) < 2:
                    if not site_data_dict['meter_var'].get():
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
                        site_data_dict['meter_cb'].select()
                        site_data_dict['meter_cb'].config(bg='Red')
                        if device == "Meter kW" and status == "currently within parameters, but may have been lost briefly":
                            if poa > 100:
                                if period_check:
                                    email_notification(site, status, device, poa, None)
                        else:
                            if period_check:
                                email_notification(site, status, device, poa, None)
                else:
                    site_data_dict['meter_cb'].deselect()
                    site_data_dict['meter_cb'].config(bg='Green')
            else:
                site_data_dict['meter_cb'].select()
                site_data_dict['meter_cb'].config(bg='Red')
                if not site_data_dict['meter_var'].get():
                    status = "Unknown, Comms consistently reporting last good data Upload as 4+ hrs ago."
                    device = "Meter"
                    if period_check:
                        email_notification(site, status, device, poa, None)

            #Breaker Check
            if all(not breaker_data['Violet Breaker Data 1'][i][0] for i in range(breaker_pulls)):
                if 'breaker_var' in site_widgets.get('Violet', {}) and not site_widgets['Violet']['breaker_var'].get():
                    device = "Breaker"
                    if period_check:
                        email_notification("Violet 1", status, device, poa, None)
                    if 'breaker_cb' in site_widgets.get('Violet', {}):
                        site_widgets['Violet']['breaker_cb'].select()
                        site_widgets['Violet']['breaker_cb'].config(bg='Red')
            else:
                if 'breaker_cb' in site_widgets.get('Violet', {}):
                    site_widgets['Violet']['breaker_cb'].deselect()
                    site_widgets['Violet']['breaker_cb'].config(bg='Green')
            #Breaker 2 Check
            if all(not breaker_data['Violet Breaker Data 2'][i][0] for i in range(breaker_pulls)):
                if 'breaker_var' in site_widgets.get('Violet 2', {}) and not site_widgets['Violet 2']['breaker_var'].get():
                    device = "Breaker"
                    if period_check:
                        email_notification("Violet 2", status, device, poa, None)
                    if 'breaker_cb' in site_widgets.get('Violet 2', {}):
                        site_widgets['Violet 2']['breaker_cb'].select()
                        site_widgets['Violet 2']['breaker_cb'].config(bg='Red')

            else:
                if 'breaker_cb' in site_widgets.get('Violet 2', {}):
                    site_widgets['Violet 2']['breaker_cb'].deselect()
                    site_widgets['Violet 2']['breaker_cb'].config(bg='Green')

        else: #Meter Check for all other Sites besides Violet
            data = np.array(meter_data[f'{site} Meter Data'])
            if data.ndim < 2:
                continue
            lastUpload_col = data[:, 6]
            amps_columns = data[:, 3:6]  # Extract Amps Columns
            if all(tim > compare_time for tim in lastUpload_col):
                if any(np.all(amps_columns[:, j] == 0) for j in range(amps_columns.shape[1])):
                    amp_data = [amps_columns[:,j] for j in range(amps_columns.shape[1])]
                    if not site_data_dict['meter_var'].get():
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
                        site_data_dict['meter_cb'].select()
                        site_data_dict['meter_cb'].config(bg='Red')
                        if period_check:
                            email_notification(site, status, device, poa, amp_data)
                elif np.mean([row[7] for row in data if row[7] is not None]) < 2:
                    if not site_data_dict['meter_var'].get():
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
                        site_data_dict['meter_cb'].select()
                        site_data_dict['meter_cb'].config(bg='Red')
                        if device == "Meter kW" and status == "currently within parameters, but may have been lost briefly":
                            if poa > 100:
                                if period_check:
                                    email_notification(site, status, device, poa, None)
                        else:
                            if period_check:
                                email_notification(site, status, device, poa, None)
                else:
                    site_data_dict['meter_cb'].deselect()
                    site_data_dict['meter_cb'].config(bg='Green')
            else:
                site_data_dict['meter_cb'].select()
                site_data_dict['meter_cb'].config(bg='Red')
                if not site_data_dict['meter_var'].get():
                    status = "Unknown, Comms consistently reporting last good data Upload as 4+ hrs ago."
                    device = "Meter"
                    if period_check:
                        email_notification(site, status, device, poa, None)

        if site in has_breaker and site != "Violet": #Breaker Check
            if all(not breaker_data[f'{site} Breaker Data'][i][0] for i in range(breaker_pulls)):
                if 'breaker_var' in site_data_dict and not site_data_dict['breaker_var'].get():
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
                    if period_check:
                        email_notification(site, status, device, poa, None)
                    site_data_dict['breaker_cb'].select()
                    site_data_dict['breaker_cb'].config(bg='Red')

            else:
                if 'breaker_cb' in site_data_dict:
                    site_data_dict['breaker_cb'].deselect()
                    site_data_dict['breaker_cb'].config(bg='Green')

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
            c.execute(f"SELECT TOP {breaker_pulls} [Status] FROM [{table_name}] ORDER BY [Timestamp] DESC")
            breaker_rows = c.fetchall()
            breaker_data[table_name] = breaker_rows
        elif "Meter" in table_name and table_name not in excluded_tables and 'Wellons' not in table_name:
            c.execute(f"SELECT TOP {meter_pulls} [Volts A], [Volts B], [Volts C], [Amps A], [Amps B], [Amps C], [Last Upload], Watts FROM [{table_name}] ORDER BY [Timestamp] DESC")
            meter_rows = c.fetchall()
            meter_data[table_name] = meter_rows
        elif "Meter" in table_name and 'Wellons' in table_name and table_name not in excluded_tables:
            c.execute(f"SELECT TOP 60 [Volts A], [Volts B], [Volts C], [Amps A], [Amps B], [Amps C], [Last Upload], Watts FROM [{table_name}] ORDER BY [Timestamp] DESC")
            meter_rows = c.fetchall()
            meter_data[table_name] = meter_rows
        elif "POA" in table_name and table_name not in excluded_tables:
            c.execute(f"SELECT TOP 3 [W/M²] FROM [{table_name}] WHERE [Last Upload] >= ? ORDER BY [Timestamp] DESC", formatted_time)
            poadatap = c.fetchall()
            poa_data[table_name] = poadatap

    #ic(breaker_data)
    comptime = meter_data['Freightliner Meter Data'][0][6]
    comptime2 = meter_data['Harding Meter Data'][0][6]
    db_update_time = 15
    timecompare = current_time - timedelta(minutes=db_update_time)
    print(f"Times: {timecompare} | {comptime} | {comptime2}")
    if timecompare > comptime:
        if timecompare > comptime2:
            os.startfile(r"G:\Shared drives\O&M\NCC Automations\Notification System\API Data Pull, Multi SQL.py")
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

# Create a list of sites to display, excluding 'Violet' which is handled separately
sites_to_display = sorted([site for site in master_List_Sites if site != "Violet"])

for i, site_name in enumerate(sites_to_display):
    # Use divmod to elegantly calculate row and column
    row, col = divmod(i, (len(sites_to_display) + num_columns - 1) // num_columns)

    # Each site's widgets will occupy 3 rows, so we multiply the base row by 3
    base_row = row * 3

    # Store all widgets and variables for a site in a dictionary
    site_widgets[site_name] = {}

    # --- Site Label ---
    site_label = Label(guiframe, text=site_name)
    site_label.grid(row=base_row, column=col)
    site_widgets[site_name]['label'] = site_label

    # --- Meter Checkbutton ---
    meter_var = BooleanVar(value=True)
    meter_cb = Checkbutton(guiframe, text='M', variable=meter_var)
    meter_cb.grid(row=base_row + 1, column=col)
    all_CBs.append(meter_var)
    site_widgets[site_name]['meter_var'] = meter_var
    site_widgets[site_name]['meter_cb'] = meter_cb

    # --- Breaker Checkbutton (if applicable) ---
    if site_name in has_breaker:
        breaker_var = BooleanVar(value=True)
        breaker_cb = Checkbutton(guiframe, text='B', variable=breaker_var)
        breaker_cb.grid(row=base_row + 2, column=col)
        all_CBs.append(breaker_var)
        site_widgets[site_name]['breaker_var'] = breaker_var
        site_widgets[site_name]['breaker_cb'] = breaker_cb

# Handle the special case for Violet
# This logic remains separate as it has a unique layout
violet_label = Label(guiframe, text="Violet 1")
violet_label.grid(row=28, column=0, sticky=W)
violet2_label = Label(guiframe, text="Violet 2")
violet2_label.grid(row=28, column=1, sticky=W)

# --- Violet 1 Breaker ---
site_widgets['Violet'] = {}
v1_breaker_var = BooleanVar(value=True)
v1_breaker_cb = Checkbutton(guiframe, text="B", variable=v1_breaker_var)
v1_breaker_cb.grid(row=29, column=0)
all_CBs.append(v1_breaker_var)
site_widgets['Violet']['breaker_var'] = v1_breaker_var
site_widgets['Violet']['breaker_cb'] = v1_breaker_cb

# --- Violet 2 Breaker ---
site_widgets['Violet 2'] = {}
v2_breaker_var = BooleanVar(value=True)
v2_breaker_cb = Checkbutton(guiframe, text="B", variable=v2_breaker_var)
v2_breaker_cb.grid(row=29, column=1)
all_CBs.append(v2_breaker_var)
site_widgets['Violet 2']['breaker_var'] = v2_breaker_var
site_widgets['Violet 2']['breaker_cb'] = v2_breaker_cb

# --- Violet Meter (shared) ---
v_meter_var = BooleanVar(value=True)
v_meter_cb = Checkbutton(guiframe, text='Meter', variable=v_meter_var)
v_meter_cb.grid(row=30, column=0, columnspan=2)
all_CBs.append(v_meter_var)
site_widgets['Violet']['meter_var'] = v_meter_var
site_widgets['Violet']['meter_cb'] = v_meter_cb



root.after(1000, db_to_dict)

def destroy_window():
    root.destroy()
#root.after(20000, destroy_window)

root.mainloop()
