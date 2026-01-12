import requests
from requests.auth import HTTPBasicAuth
import time
import datetime
import json, os
import pyodbc
import re
import sys
import subprocess
from tkinter import messagebox
import tkinter as tk
import multiprocessing
from multiprocessing import Manager
from icecream import ic
import urllib3
import ctypes

# Add the parent directory ('NCC Automations') to the Python path
# This allows us to import the 'PythonTools' package from there.
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from PythonTools import CREDS, EMAILS, AE_HARDWARE_MAP, PausableTimer, get_hostname


urllib3.disable_warnings()

# Set the title of the console window
ctypes.windll.kernel32.SetConsoleTitleW("AE API Data Pull")
#Attmepted
#os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
#os.environ['SSL_CERT_FILE'] = certifi.where()
dataPullTime = 1

HOSTNAME = get_hostname()

if HOSTNAME not in {"NAR-OMOPSXPS", "NAR-OMOps-SQL"}:
    messagebox.showwarning(message="Make sure to be connected to the NARENCO Office VPN if you are not on the nar-wifi network.")

email = EMAILS['NCC Desk']
password = CREDS['AlsoEnergy']
base_url = "https://api.alsoenergy.com"
token_endpoint = "/Auth/token"

sites_endpoint = "/Sites"


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

def token_management():
    if 'access_token' in globals():
        pass
    else:
        print("Requesting Access Token")
        get_access_token()

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
    globals()['initial_response'] = requests.post(access_token_url, headers=headers, data=data, verify=False) #I know that I shouldn't set verify to false for security reasons. But the Code worked flawlessly for over a year being set to True by Default and this was the only thing out of 10 things I tried that worked. 🤷‍♂️ Adivce is welcomed to joseph.lang@narenco.com. If you message me, please include 'Found on GitHub, looking to help', so that I know it's not spam.
    print("Starting response", initial_response.status_code)
    if initial_response.status_code == 200:
        globals()['access_token'] = initial_response.json().get('access_token')
    else:
        new_value = counting_fails(auth_file)
        print(f"Failed Attempts: {new_value}")


# Function to make API request with authentication
def make_api_request(get_hardware_url, access_token):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    headers['Authorization'] = f"Bearer {access_token}"
    return requests.get(get_hardware_url, headers=headers, verify=False) #I know that I shouldn't set verify to false for security reasons. But the Code worked flawlessly for over a year being set to True by Default and this was the only thing out of 10 things I tried that worked. 🤷‍♂️ Adivce is welcomed to joseph.lang@narenco.com. If you message me, please include 'Found on GitHub, looking to help', so that I know it's not spam.

def get_data_for_site(site, site_data, api_data, AE_HARDWARE_MAP, start, base_url, access_token):
    troubleshooting_file = r"C:\Users\omops\Documents\Automations\Troubleshooting.txt"
    
    current = time.perf_counter()
    #print("Start Processing:", site, round(current-start, 2))
    for category, hardware_data in site_data.items():
        for hardware_id, hdname in hardware_data.items():
            get_hardware_url = f"{base_url}/Hardware/{hardware_id}"
            hardware_response = make_api_request(get_hardware_url, access_token)
            #print(f"Hardware Response {site} | {hdname}: {hardware_response.status_code}")

            if hardware_response.status_code == 200:
                register_values = {}
                hardware_data_response = hardware_response.json()
                #with open(troubleshooting_file, "a") as tbfile: 
                #    json.dump(hardware_data_response, tbfile, indent=2)

                hdtimestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


                # AE Register Names
                breaker_register_names = {'Status', 'Breaker Open/Closed', 'Status Closed'}
                inverterKW_register_names = {'Grid power', 'Line kW', 'AC Real Power', '3phase Power', 'Active Power', 'Total Active Power', 'Pac', 'AC Power'}
                inverterDC_register_names = {'DC Power Total', 'DC Voltage1', 'DC Input Voltage', 'DC voltage (average)', 'DC Voltage Average', 'Bus Voltage', 'Total DC Power', 'DC Voltage', 'Input Voltage', 'Vpv'}
                amps_a_register_names = {'Phase current, A', 'AC Current A', 'Current A', 'Amps A', 'AC Phase A Current'}
                amps_b_register_names = {'Phase current, B', 'AC Current B', 'Current B', 'Amps B', 'AC Phase B Current'}
                amps_c_register_names = {'Phase current, C', 'AC Current C', 'Current C', 'Amps C', 'AC Phase C Current'}

                volts_a_register_names = {'Volts A-N', 'Volts A', 'AC Voltage A', 'Voltage AN', 'AC Voltage A (Line-Neutral)', 'Voltage, A-N', 'AC Phase A Voltage', 'AC Voltage AN'}
                volts_b_register_names = {'Volts B-N', 'Volts B', 'AC Voltage B', 'Voltage BN', 'AC Voltage B (Line-Neutral)', 'Voltage, B-N', 'AC Phase B Voltage', 'AC Voltage BN'}
                volts_c_register_names = {'Volts C-N', 'Volts C', 'AC Voltage C', 'Voltage CN', 'AC Voltage C (Line-Neutral)', 'Voltage, C-N', 'AC Phase C Voltage', 'AC Voltage CN'}
                meterkw_register_names = {'Active Power', 'Real power', 'Real Power', 'Total power'}    #Real Power is probably not used but lowercase power is.            
                
                weather_station_register_names = {'POA Irradiance', 'Plane of Array Irradiance',  'GHI Irradiance', 'Sun (GHI)', 'Sun (POA Temp comp)', 'GHI', 'POA', 'POA irradiance', 'Sun (POA)'}

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
                    dvtimestamp = hardware_data_response.get('lastUpload')
                    if dvtimestamp:
                        datetime_obj = datetime.datetime.strptime(dvtimestamp, "%Y-%m-%dT%H:%M:%S%z")
                        aetimestamp = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
                        if aetimestamp == '0001-01-01 00:00:00': #This Value Errors out the SQL Input
                            aetimestamp = '1999-01-01 00:00:00'
                        register_values['aetimestamp'] = aetimestamp
                    else:
                        # If lastUpload is missing, use None. This becomes NULL in the database,
                        # which is the correct way to represent a missing value and avoids
                        # potential "out of range" errors from database constraints.
                        print(f"lastUpload is missing. {site} | {hdname}    | Hardware ID: {hardware_id}")
                        register_values['aetimestamp'] = '1999-01-01 00:00:00'
                except Exception as e:
                    print("Error parsing timestamp:", e)
                    print("Timestamp value:", dvtimestamp)
                    # Fallback to None here as well for consistency.
                    register_values['aetimestamp'] = '1999-01-01 00:00:00'
                api_data[hardware_id] = register_values

                #Added to reduce strain on AE API server
                time.sleep(.01)

                #with open(troubleshooting_file, 'a') as tfile:
                #    json.dump(register_values, tfile, indent=2)

            elif hardware_response.status_code == 401: # Unauthorized or Forbidden
                print(f"Failed to retrieve hardware data for {hardware_id}. Status Code: {hardware_response.status_code}")
                sys.exit() #Also Energy has been locking our account so I hope this will prevent that from happening as often. 
            elif hardware_response.status_code > 401:
                print(f"Failed to retrieve hardware data for {hardware_id} at {site} in {category}. Status code: {hardware_response.status_code}")
 
    end = time.perf_counter()
    print(f"Pulled Data: {site:<15}| Time Taken: {round(end-current, 2)}")

if __name__ == '__main__': #This is absolutely necessary due to running the async pool.
    def my_main():
        global AE_HARDWARE_MAP, sites_endpoint, dataPullTime, today_date, start, api_data, access_token
        def error_callback(e):
            """A callback function to handle and print errors from worker processes."""
            print(f"ERROR in worker process: {e}")
   
        
        # Get today's date
        today_date = datetime.date.today()

        # Your existing code for obtaining the access token and initializing dictionaries
        start = time.perf_counter()

        api_data = multiprocessing.Manager().dict()
        
        #Calls get access token if access token is not already defined. Hopoing this avoid multiple authentications and therefor AE locking out our account. 
        token_management()


        if access_token:
            pool = multiprocessing.Pool()

            for site, site_data in AE_HARDWARE_MAP.items():
                if site == "CDIA":
                    continue
                pool.apply_async(get_data_for_site, args=(site, site_data, api_data, AE_HARDWARE_MAP, start, base_url, access_token), error_callback=error_callback)
                time.sleep(0.5) #Again added to reduce strain on AE API Server
            pool.close()
            pool.join()

            api_data_dict = dict(api_data)
            # This was temporary just so I could visualize the output
            json_loop_exit_file = r"G:\Shared drives\O&M\NCC Automations\Notification System\api_data_visualized.json"
            # Convert and write JSON object to file
            #with open(json_loop_exit_file, "w+") as outfile: 
            #    json.dump(api_data_dict, outfile, indent=2)
            
            #print(api_data_dict)
            if api_data_dict:
                if HOSTNAME == "NAR-OMOps-SQL":
                    connection_string = (
                        r'DRIVER={ODBC Driver 18 for SQL Server};'
                        r'SERVER=localhost\SQLEXPRESS;'
                        r'DATABASE=NARENCO_O&M_AE;'
                        r'Trusted_Connection=yes;'
                        r'Encrypt=no;'
                    )
                else:
                    connection_string = (
                        r'DRIVER={ODBC Driver 18 for SQL Server};'
                        fr'SERVER={CREDS['DB_IP']}\SQLEXPRESS;'
                        r'DATABASE=NARENCO_O&M_AE;'
                        fr'UID={CREDS['DB_UID']};'
                        fr'PWD={CREDS['DB_PWD']};'
                        r'Encrypt=no;'
                    )
                dbconnection = pyodbc.connect(connection_string)
                cursor = dbconnection.cursor()

                data_start = time.perf_counter()

                inserts = {}

                for site, site_data in AE_HARDWARE_MAP.items():
                    for device_category, devices in site_data.items():
                        inv_num = 1
                        for hardwareid, device_name in devices.items():
                            if hardwareid in api_data_dict:
                                data = api_data_dict[hardwareid]
                                if device_category == "breakers":
                                    violet_Exception = " 2" if hardwareid == "390118" else " 1" if hardwareid == "390117" else ""
                                    table_name = f"[{site} Breaker Data{violet_Exception}]"
                                    sql = f"INSERT INTO {table_name} (Timestamp, [Last Upload], Status, HardwareId) VALUES (?, ?, ?, ?)"
                                    if table_name not in inserts: inserts[table_name] = {'sql': sql, 'params': []}
                                    
                                    relay_stat = data.get('Status', '')
                                    openClose = True if str(relay_stat).lower().strip() in ['1', '240', 'closed'] else False
                                    params = (data['pytimestamp'], data['aetimestamp'], openClose, hardwareid)
                                    inserts[table_name]['params'].append(params)

                                elif device_category == "meters":
                                    table_name = f"[{site} Meter Data]"
                                    sql = f"INSERT INTO {table_name} (Timestamp, [Last Upload], [Volts A], [Volts B], [Volts C], [Amps A], [Amps B], [Amps C], Watts, HardwareId) VALUES (?,?,?,?,?,?,?,?,?,?)"
                                    if table_name not in inserts: inserts[table_name] = {'sql': sql, 'params': []}

                                    def parse_float(value_str):
                                        if not value_str: return 0.0
                                        match = re.search(r'(\d+\.?\d*)', str(value_str))
                                        return float(match.group(1)) if match else 0.0

                                    meterkw_str = data.get('KW', '0')
                                    meterkw = parse_float(meterkw_str)
                                    if "kw" in str(meterkw_str).lower(): meterkw *= 1000
                                    elif "mw" in str(meterkw_str).lower(): meterkw *= 1000000

                                    params = (data['pytimestamp'],
                                              data['aetimestamp'],
                                              parse_float(data.get('Volts A')), parse_float(data.get('Volts B')), parse_float(data.get('Volts C')),
                                              parse_float(data.get('Amps A')), parse_float(data.get('Amps B')), parse_float(data.get('Amps C')),
                                              meterkw,
                                              hardwareid)
                                    inserts[table_name]['params'].append(params)

                                elif device_category == "weather_stations":
                                    table_name = f"[{site} POA Data]"
                                    sql = f"INSERT INTO {table_name} (Timestamp, [Last Upload], [W/M²], HardwareId) VALUES (?, ?, ?, ?)"
                                    if table_name not in inserts: inserts[table_name] = {'sql': sql, 'params': []}
                                    
                                    poa_str = data.get('POA', '0')
                                    poa = float(re.search(r'\d+', str(poa_str)).group()) if re.search(r'\d+', str(poa_str)) else 0
                                    params = (data['pytimestamp'], data['aetimestamp'], poa, hardwareid)
                                    inserts[table_name]['params'].append(params)

                                elif device_category == "inverters":
                                    duplin_exception = ""
                                    if hardwareid in ["94056", "94057", "94058", "94059", "94060", "94061", "94062", "94063", "94064", "94065", "94066", "94067", "94068", "94069", "94070", "94071", "94072", "94073"]:
                                        duplin_exception = " String"
                                    elif hardwareid in ["94053", "94055", "94054"]:
                                        duplin_exception = " Central"

                                    table_name = f"[{site}{duplin_exception} INV {inv_num-3 if duplin_exception == " String" else inv_num} Data]"
                                    sql = f"INSERT INTO {table_name} (Timestamp, [Last Upload], Watts, [dc V], HardwareID) VALUES (?, ?, ?, ?, ?)"
                                    if table_name not in inserts: inserts[table_name] = {'sql': sql, 'params': []}

                                    invkw_str = data.get('KW', '0')
                                    invkW = 0
                                    if not str(invkw_str).startswith('-'):
                                        invkW = float(re.search(r'\d+', str(invkw_str)).group()) if re.search(r'\d+', str(invkw_str)) else 0
                                        if "kw" in str(invkw_str).lower(): invkW *= 1000
                                        elif "mw" in str(invkw_str).lower(): invkW *= 1000000
                                    
                                    invDCV_str = data.get('DC V', '0')
                                    invDCV = float(re.search(r'\d+', str(invDCV_str)).group()) if re.search(r'\d+', str(invDCV_str)) else 0

                                    params = (data['pytimestamp'], data['aetimestamp'], invkW, invDCV, hardwareid)
                                    inserts[table_name]['params'].append(params)
                                    inv_num += 1

                for table_name, insert_data in inserts.items():
                    if insert_data['params']:
                        try:
                            cursor.executemany(insert_data['sql'], insert_data['params'])
                        except Exception as e:
                            print(f"Error inserting into {table_name}: {e}")

                dbconnection.commit()
                finish = time.perf_counter()
                print("Data Injection Time:", round(finish - data_start, 5))
                dbconnection.close()

                end = time.perf_counter()
                dataPullTime = round((end - start)/60, 3)
                print("Total Time:", round((end - start)/60, 3), "Minutes")
                reset_count(auth_file)


    loop_exit_file = r"G:\Shared drives\O&M\NCC Automations\Notification System\APISiteStat\Exiting Loop due to Failed Authentications.txt"
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
            if wait <= 10:
                wait = 10  
            print(f"Waiting {round(wait, 2)} Seconds then pulling data again")
            time.sleep(wait)

        print("Looping")
        my_main()
        auth_file.close()