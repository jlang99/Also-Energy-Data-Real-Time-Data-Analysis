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
    is_after_weekend_hours = now.hour >= 15 or now.hour < 7

    # For September, October, November, December, and January
    if now.month in {11, 12, 1}:
        weekday_hours = now.hour >= 17 or now.hour < 7
    # For February, March, and April
    elif now.month in {2, 9, 10}:
        weekday_hours = now.hour >= 18 or now.hour < 7
    # For May, June, July, and August
    else:
        weekday_hours = now.hour >= 19 or now.hour < 7

    # Return True if it's off-hours on a weekend OR off-hours on a weekday
    if (is_weekend and is_after_weekend_hours) or (not is_weekend and weekday_hours):
        return True
    return False

def email_notification(SiteName, status, device, poa, amps):
    sender_email = EMAILS['NCC Desk']
    admin = EMAILS['Administrators + NCC']
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    smtp_password = CREDS['remoteMonitoring']

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ', '.join(admin)
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

def check_null_columns(data_rows, col_map):
    """
    Helper function to identify if specific data columns are entirely NULL
    across the pulled data rows.
    Returns a tuple: (boolean for total loss, list of column names that are NULL)
    """
    if not data_rows:
        return False, []
    
    null_cols = []
    for col_idx, col_name in col_map.items():
        # Check if every single row has a None (NULL) in this column index
        if all(row[col_idx] is None for row in data_rows):
            null_cols.append(col_name)
            
    # Total loss if the number of completely NULL columns equals the number of mapped data columns
    is_total_loss = len(null_cols) == len(col_map)
    return is_total_loss, null_cols


def update_breaker_status():    
    period_check = notification_period()
    curtime = datetime.now()
    compare_time = curtime - timedelta(hours=4)   
    h_time = curtime.hour
    
    # Maps of column indexes to their human-readable names for data columns (Excludes ID/Timestamps)
    meter_col_map = {0: 'Volts A', 1: 'Volts B', 2: 'Volts C', 3: 'Amps A', 4: 'Amps B', 5: 'Amps C', 7: 'Watts'}
    breaker_col_map = {0: 'Status'}

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
        # Safely get max time, ignoring any None values
        metercomms = max((row[6] for row in site_meter_data if row[6] is not None), default=None)
        
        # --- Perform NULL Checks for Meter ---
        is_total_meter_null, null_meter_cols = check_null_columns(site_meter_data, meter_col_map)

        if site == "Violet":
            # --- Violet Meter Check ---
            if is_total_meter_null or null_meter_cols:
                site_data_dict['meter_cb'].select()
                site_data_dict['meter_cb'].config(bg='Red')
                if not site_data_dict['meter_var'].get():
                    status = "Total Data Loss (All data columns reporting NULL)" if is_total_meter_null else f"Partial Data Loss (Column(s) stopped reporting: {', '.join(null_meter_cols)})"
                    if period_check:
                        email_notification(site, status, "Meter", poa, None)
            else:
                data = np.array(site_meter_data)
                if data.ndim >= 2:
                    lastUpload_col = data[:, 6]
                    amps_columns = data[:, 3:6]  # Extract Amps Columns
                    
                    # Filter out Nones for time comparison
                    valid_times = [tim for tim in lastUpload_col if tim is not None]
                    
                    if valid_times and all(tim > compare_time for tim in valid_times):
                        if any(np.all(amps_columns[:, j] == 0) for j in range(amps_columns.shape[1])):
                            phases_to_check = []
                            if not site_widgets['Violet']['amp_a_var'].get(): phases_to_check.append(0)
                            if not site_widgets['Violet']['amp_b_var'].get(): phases_to_check.append(1)
                            if not site_widgets['Violet']['amp_c_var'].get(): phases_to_check.append(2)

                            amp_data = [amps_columns[:,j] for j in range(amps_columns.shape[1])]
                            if not site_data_dict['meter_var'].get():
                                if metercomms and metercomms > compare_time:
                                    # Safe comparison avoiding None
                                    if any(val > 5 for i in range(min(voltage_check, len(site_meter_data))) for j in range(3) if (val := site_meter_data[i][j]) is not None):
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
                        elif np.mean([row[7] for row in data if row[7] is not None] or [0]) < 2:
                            if not site_data_dict['meter_var'].get():
                                if metercomms and metercomms > compare_time:
                                    if any(val > 5 for i in range(min(voltage_check, len(site_meter_data))) for j in range(3) if (val := site_meter_data[i][j]) is not None):
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
                                    if poa is not None and poa > 100:
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

            # --- Violet Breaker 1 Check ---
            v1_breaker_data = breaker_data.get('Violet Breaker Data 1', [])
            is_total_b1, _ = check_null_columns(v1_breaker_data, breaker_col_map)
            
            if is_total_b1:
                if 'breaker_var' in site_widgets.get('Violet', {}) and not site_widgets['Violet']['breaker_var'].get():
                    if period_check:
                        email_notification("Violet 1", "Total Data Loss (Status reporting NULL)", "Breaker", poa, None)
                    if 'breaker_cb' in site_widgets.get('Violet', {}):
                        site_widgets['Violet']['breaker_cb'].select()
                        site_widgets['Violet']['breaker_cb'].config(bg='Red')
            else:
                if len(v1_breaker_data) >= breaker_pulls and all(not v1_breaker_data[i][0] for i in range(breaker_pulls)):
                    if 'breaker_var' in site_widgets.get('Violet', {}) and not site_widgets['Violet']['breaker_var'].get():
                        if any(val > 5 for i in range(min(voltage_check, len(site_meter_data))) for j in range(3) if (val := site_meter_data[i][j]) is not None):
                            status = "currently within parameters, but may have been lost briefly"
                        else:
                            status = "Lost"
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

            # --- Violet Breaker 2 Check ---
            v2_breaker_data = breaker_data.get('Violet Breaker Data 2', [])
            is_total_b2, _ = check_null_columns(v2_breaker_data, breaker_col_map)
            
            if is_total_b2:
                if 'breaker_var' in site_widgets.get('Violet 2', {}) and not site_widgets['Violet 2']['breaker_var'].get():
                    if period_check:
                        email_notification("Violet 2", "Total Data Loss (Status reporting NULL)", "Breaker", poa, None)
                    if 'breaker_cb' in site_widgets.get('Violet 2', {}):
                        site_widgets['Violet 2']['breaker_cb'].select()
                        site_widgets['Violet 2']['breaker_cb'].config(bg='Red')
            else:
                if len(v2_breaker_data) >= breaker_pulls and all(not v2_breaker_data[i][0] for i in range(breaker_pulls)):
                    if 'breaker_var' in site_widgets.get('Violet 2', {}) and not site_widgets['Violet 2']['breaker_var'].get():
                        if any(val > 5 for i in range(min(voltage_check, len(site_meter_data))) for j in range(3) if (val := site_meter_data[i][j]) is not None):
                            status = "currently within parameters, but may have been lost briefly"
                        else:
                            status = "Lost"
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

        else: 
            # --- Meter Check for all other Sites besides Violet ---
            if is_total_meter_null or null_meter_cols:
                site_data_dict['meter_cb'].select()
                site_data_dict['meter_cb'].config(bg='Red')
                if not site_data_dict['meter_var'].get():
                    status = "Total Data Loss (All data columns reporting NULL)" if is_total_meter_null else f"Partial Data Loss (Column(s) stopped reporting: {', '.join(null_meter_cols)})"
                    if period_check:
                        email_notification(site, status, "Meter", poa, None)
            else:
                data = np.array(site_meter_data)
                if data.ndim >= 2:
                    lastUpload_col = data[:, 6]
                    amps_columns = data[:, 3:6]  # Extract Amps Columns
                    
                    valid_times = [tim for tim in lastUpload_col if tim is not None]
                    
                    if valid_times and all(tim > compare_time for tim in valid_times):
                        phases_to_check = []
                        if not site_data_dict['amp_a_var'].get(): phases_to_check.append(0)
                        if not site_data_dict['amp_b_var'].get(): phases_to_check.append(1)
                        if not site_data_dict['amp_c_var'].get(): phases_to_check.append(2)

                        if any(np.all(amps_columns[:, j] == 0) for j in phases_to_check):
                            amp_data = [amps_columns[:,j] for j in range(amps_columns.shape[1])]
                            if not site_data_dict['meter_var'].get():
                                if metercomms and metercomms > compare_time:
                                    if any(val > 5 for i in range(min(voltage_check, len(site_meter_data))) for j in range(3) if (val := site_meter_data[i][j]) is not None):
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
                        elif np.mean([row[7] for row in data if row[7] is not None] or [0]) < 2:
                            if not site_data_dict['meter_var'].get():
                                if metercomms and metercomms > compare_time:
                                    if any(val > 5 for i in range(min(voltage_check, len(site_meter_data))) for j in range(3) if (val := site_meter_data[i][j]) is not None):
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
                                    if poa is not None and poa > 100:
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

        # --- Breaker Check for all other Sites ---
        if site in has_breaker and site != "Violet": 
            site_breaker_data = breaker_data.get(f'{site} Breaker Data', [])
            is_total_breaker, _ = check_null_columns(site_breaker_data, breaker_col_map)
            
            if is_total_breaker:
                if 'breaker_var' in site_data_dict and not site_data_dict['breaker_var'].get():
                    site_data_dict['breaker_cb'].select()
                    site_data_dict['breaker_cb'].config(bg='Red')
                    if period_check:
                        email_notification(site, "Total Data Loss (Status reporting NULL)", "Breaker", poa, None)
            else:
                if len(site_breaker_data) >= breaker_pulls and all(not site_breaker_data[i][0] for i in range(breaker_pulls)):
                    if 'breaker_var' in site_data_dict and not site_data_dict['breaker_var'].get():
                        if metercomms and metercomms > compare_time:
                            if any(val > 5 for i in range(min(voltage_check, len(site_meter_data))) for j in range(3) if (val := site_meter_data[i][j]) is not None):
                                status = "currently within parameters, but may have been lost briefly"
                                device = "Breaker"
                            else:
                                status = "Lost"
                                device = "Breaker"
                        else:
                            status = "Unknown, Lost Comms with Meter"
                            device = "Breaker"
                        
                        site_data_dict['breaker_cb'].select()
                        site_data_dict['breaker_cb'].config(bg='Red')
                        if period_check:
                            email_notification(site, status, device, poa, None)
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
        elif "Meter" in table_name and table_name not in excluded_tables and 'Wellons' not in table_name and "CDIA" not in table_name:
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

num_columns = 7

# Create a list of sites to display, excluding 'Violet' which is handled separately
sites_to_display = sorted([site for site in master_List_Sites])

for i, site_name in enumerate(sites_to_display):
    # Use divmod to elegantly calculate row and column
    # The quotient of the site index and number of columns gives the `row`.
    # The remainder gives the `col`. This creates a grid with `num_columns` columns.
    row, col = divmod(i, num_columns)
    base_row = row * 4

    # Store all widgets and variables for a site in a dictionary
    site_widgets[site_name] = {}

    device_frame = Frame(guiframe, border=2, relief='ridge')
    device_frame.grid(row=base_row + 1, column=col, sticky='n')

    if site_name == 'Violet':
        violet_label = Label(guiframe, text="Violet 1 | Violet 2")
        violet_label.grid(row=base_row, column=col)

        # --- Violet 2 Breaker ---
        site_widgets['Violet 2'] = {}
        v2_breaker_var = BooleanVar(value=True)
        v2_breaker_cb = Checkbutton(device_frame, text="B", variable=v2_breaker_var)
        v2_breaker_cb.grid(row=0, column=1)
        all_CBs.append(v2_breaker_var)
        site_widgets['Violet 2']['breaker_var'] = v2_breaker_var
        site_widgets['Violet 2']['breaker_cb'] = v2_breaker_cb

        col_span_val = 2

    else:
        # --- Site Label ---
        site_label = Label(guiframe, text=site_name)
        site_label.grid(row=base_row, column=col)
        site_widgets[site_name]['label'] = site_label
        col_span_val = 1

    # --- Meter Checkbutton ---
    meter_var = BooleanVar(value=True)
    meter_cb = Checkbutton(device_frame, text='M', variable=meter_var)
    meter_cb.grid(row=1, column=0, columnspan=col_span_val)
    all_CBs.append(meter_var)
    site_widgets[site_name]['meter_var'] = meter_var
    site_widgets[site_name]['meter_cb'] = meter_cb

    # --- Amp Phase Checkbuttons ---
    amp_frame = Frame(device_frame)
    amp_frame.grid(row=2, column=0, columnspan=col_span_val)
    
    amp_a_var = BooleanVar(value=False)
    amp_a_cb = Checkbutton(amp_frame, text='A', variable=amp_a_var)
    amp_a_cb.grid(row=0, column=0)
    site_widgets[site_name]['amp_a_var'] = amp_a_var
    
    amp_b_var = BooleanVar(value=False)
    amp_b_cb = Checkbutton(amp_frame, text='B', variable=amp_b_var)
    amp_b_cb.grid(row=0, column=1)
    site_widgets[site_name]['amp_b_var'] = amp_b_var

    amp_c_var = BooleanVar(value=False)
    amp_c_cb = Checkbutton(amp_frame, text='C', variable=amp_c_var)
    amp_c_cb.grid(row=0, column=2)
    site_widgets[site_name]['amp_c_var'] = amp_c_var

    all_CBs.extend([amp_a_var, amp_b_var, amp_c_var])
    # --- Breaker Checkbutton (if applicable) ---
    if site_name in has_breaker:
        breaker_var = BooleanVar(value=True)
        breaker_cb = Checkbutton(device_frame, text='B', variable=breaker_var)
        breaker_cb.grid(row=0, column=0)
        all_CBs.append(breaker_var)
        site_widgets[site_name]['breaker_var'] = breaker_var
        site_widgets[site_name]['breaker_cb'] = breaker_cb



root.after(1000, db_to_dict)

def destroy_window():
    root.destroy()
#root.after(20000, destroy_window)

root.mainloop()
