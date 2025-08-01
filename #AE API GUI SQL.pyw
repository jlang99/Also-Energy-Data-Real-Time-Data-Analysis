#AE API GUI
import warnings
import pyodbc
from datetime import datetime, date, time, timedelta
from tkinter import *
from tkinter import messagebox, filedialog, ttk
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
import glob
import json
import re
from bs4 import BeautifulSoup

from PythonTools import CREDS, EMAILS, PausableTimer #Both of these Variables are Dictionaries with a single layer that holds Personnel data or app passwords

#Underperformance Analysis Packages
import pandas as pd
from sklearn.linear_model import LinearRegression
from PIL import Image, ImageDraw, ImageTk

def date_validation(dvalue):
    """Validates that the input is in mm/dd/yyyy format."""
    # An empty entry is a valid state
    if not dvalue:
        return True
    # The final format is 10 characters long
    if len(dvalue) > 10:
        return False

    # Check the characters as they are typed
    for i, char in enumerate(dvalue):
        if i in [0, 1, 3, 4, 6, 7, 8, 9]:  # Positions for digits
            if not char.isdigit():
                return False
        if i in [2, 5]:  # Positions for slashes
            if char != '/':
                return False

    # Check the semantic value of the month and day
    if len(dvalue) >= 2:
        # Month must be between 01 and 12
        month = int(dvalue[0:2])
        if month < 1 or month > 12:
            return False
    if len(dvalue) >= 5:
        # Day must be between 01 and 31
        day = int(dvalue[3:5])
        if day < 1 or day > 31:
            return False
        

breaker_pulls = 6
meter_pulls = 8

start = ty.perf_counter()
myappid = 'AE.API.Data.GUI'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

main_color = '#ADD8E6'
root = Tk()
root.title("Site Data")
try:
    root.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
root.wm_attributes("-topmost", True)
root.configure(bg="#ADD8E6") 

#Date Validation Registration
vcmd_date = (root.register(date_validation), '%P')

checkIns= Toplevel(root)
try:
    checkIns.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
checkIns.title("Personnel On-Site")

checkIns.wm_attributes("-topmost", True)


timeWin= Toplevel(root)
try:
    timeWin.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
timeWin.title("Timestamps")
timeWin.wm_attributes("-topmost", True)
timeW = Frame(timeWin)
timeW.pack(side=LEFT)
timeW_notes= Label(timeW, text= "Data Pull Timestamps", font= ("Calibiri", 14))
timeW_notes.grid(row=0, column= 0, columnspan= 3)

# Fit in another 2 columns and make them sticky to eeach other like these below.
time1= Label(timeW, text= "First:", font= ("Calibiri", 12))
time2= Label(timeW, text= "Second:", font= ("Calibiri", 12))
time3= Label(timeW, text= "Third:", font= ("Calibiri", 12))
time4= Label(timeW, text= "Fourth:", font= ("Calibiri", 12))
time5= Label(timeW, text= "Tenth:", font= ("Calibiri", 12))
timeL= Label(timeW, text= "Fifteenth:", font= ("Calibiri", 12))
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



datalbl= Label(timeW, text= "MsgBox Data:", font= ("Calibiri", 14))
datalbl.grid(row=1, column=2)
inverterT = Label(timeW, text= "Inverters:", font= ("Calibiri", 12))
inverterT.grid(row=2, column=2)
spread15 = Label(timeW, text= "Time")
spread15.grid(row=3, column=2)
breakermeter = Label(timeW, text= """Breakers &
Meters:""", font= ("Calibiri", 12))
breakermeter.grid(row=4, column=2)
spread10 = Label(timeW, text= "Time")
spread10.grid(row=5, column=2)


underperf_frame = Frame(timeWin)
underperf_frame.pack(side=RIGHT)
#Underperformance Settings
underperf_Maincbvar = BooleanVar()
underperf_Maincb = Checkbutton(underperf_frame, text="Select to turn on the Inverter\nUnderperformance check\nBelow is the parameters\nfor the data", cursor='hand2', variable=underperf_Maincbvar)
underperf_Maincb.grid(row=0, column=0, columnspan=2)
underperf_Maincb.select()


underperf_range = StringVar()
underperf_range.set((datetime.now().date() - timedelta(days=30)).strftime("%m/%d/%Y"))
underperf_range2 = StringVar()
underperf_range2.set((datetime.now().date()).strftime("%m/%d/%Y"))
underperfdatalbl= Label(underperf_frame, text= "Days of Data\nStart - End")
underperfdatalbl.grid(row=1, column=0, columnspan=2)
underperfdaterng = Entry(underperf_frame, width=10, textvariable=underperf_range, validate='all', validatecommand=vcmd_date)
underperfdaterng.grid(row=2, column=0)
underperfdaterng2 = Entry(underperf_frame, width=10, textvariable=underperf_range2, validate='all', validatecommand=vcmd_date)
underperfdaterng2.grid(row=2, column=1)

underperf_hourlimit = IntVar()
underperf_hourlimit.set(10)
underperfhourstartlbl= Label(underperf_frame, text= "Hour Start Limit:")
underperfhourstartlbl.grid(row=3, column=0, columnspan=2)
underperfhourstart = Entry(underperf_frame, width=10, textvariable=underperf_hourlimit)
underperfhourstart.grid(row=4, column=0, columnspan=2)

underperf_hourend = IntVar()
underperf_hourend.set(15)
underperfhourlbl= Label(underperf_frame, text= "Hour End Limit:")
underperfhourlbl.grid(row=5, column=0, columnspan=2)
underperfhour = Entry(underperf_frame, width=10, textvariable=underperf_hourend)
underperfhour.grid(row=6, column=0, columnspan=2)
# Underperformance Settings end

alertW = Toplevel(root)
alertW.title("Alert Windows Info")
alertW.wm_attributes("-topmost", True)
try:
    alertW.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")

#Top Labels Main Window
siteLabel = Label(root, bg="#ADD8E6", text= "Sites", font=('Tk_defaultFont', 10, 'bold'))
siteLabel.grid(row=0, column= 0, sticky=W)
breakerstatusLabel= Label(root, bg="#ADD8E6", text= "Breaker Status", font=('Tk_defaultFont', 10, 'bold'))
breakerstatusLabel.grid(row=0, column=1)
meterVLabel = Label(root, bg="#ADD8E6", text= "Utility V", font=('Tk_defaultFont', 10, 'bold'))
meterVLabel.grid(row= 0, column=2)
meterkWLabel = Label(root, bg="#ADD8E6", text="Meter kW", font=('Tk_defaultFont', 10, 'bold'))
meterkWLabel.grid(row=0, column=4)
meterratioLabel = Label(root, bg="#ADD8E6", text= "% of Max", font=('Tk_defaultFont', 10, 'bold'))
meterratioLabel.grid(row=0, column= 5)
meterpvsystLabel = Label(root, bg="#ADD8E6", text= "% of PvSyst", font=('Tk_defaultFont', 10, 'bold'))
meterpvsystLabel.grid(row=0, column= 6)
POALabel = Label(root, bg="#ADD8E6", text= "POA", font=('Tk_defaultFont', 10, 'bold'))
POALabel.grid(row=0, column= 7)

#Windows with multiple pages of Site inv data
solrvr_win = Toplevel(root)
solrvr_win.title("Sol River's Portfolio")
try:
    solrvr_win.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
solrvrnotebook = ttk.Notebook(solrvr_win)
style = ttk.Style(root)
style.configure("TNotebook.Tab", padding=[90, 2], font=('Tk_defaultFont', 12, 'bold'))
solrvr = ttk.Frame(solrvrnotebook)
solrvr2 = ttk.Frame(solrvrnotebook)
solrvr3 = ttk.Frame(solrvrnotebook)
solrvrnotebook.add(solrvr, text="Bulloch 1A - McLean")
solrvrnotebook.add(solrvr2, text="Richmond - Warbler")
solrvrnotebook.add(solrvr3, text="Washington - Whitetail")
solrvrnotebook.pack(expand=True, fill='both')

hst_win = Toplevel(root)
hst_win.title("Harrison Street's Portfolio")
try:
    hst_win.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
hstnotebook = ttk.Notebook(hst_win)
hst = ttk.Frame(hstnotebook)
hst2 = ttk.Frame(hstnotebook)
hstnotebook.add(hst, text="Bishopville II - Tedder")
hstnotebook.add(hst2, text="Thunderhead - Van Buren")
hstnotebook.pack(expand=True, fill='both')

nar_win = Toplevel(root)
nar_win.title("NARENCO's Portfolio")
try:
    nar_win.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
narnotebook = ttk.Notebook(nar_win)
nar = ttk.Frame(narnotebook)
nar2 = ttk.Frame(narnotebook)
narnotebook.add(nar, text="Bluebird - Hayes")
narnotebook.add(nar2, text="Hickory - Violet")
narnotebook.pack(expand=True, fill='both')

#Static Inv Windows
soltage = Toplevel(root)
soltage.title("Soltage")
try:
    soltage.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
ncemc = Toplevel(root)
ncemc.title("NCEMC")
ncemc.wm_attributes("-topmost", True)
try:
    ncemc.iconbitmap(r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico")
except Exception as e:
    print(f"Error loading icon: {e}")
#Inverter Windows created
''' Data Structure for master_List_Sites
(Site Name, {
Inv Dict}, 
Max Meter Value W's, varname, window group var, PVSYST Site Name)
'''

master_List_Sites = [('Bishopville II', {
    1: "1-1", 2: "1-2", 3: "1-3", 4: "1-4", 5: "1-5", 6: "1-6",
    7: "1-7", 8: "1-8", 9: "1-9", 10: "2-1", 11: "2-2", 12: "2-3",
    13: "2-4", 14: "2-5", 15: "2-6", 16: "2-7", 17: "2-8", 18: "2-9",
    19: "3-1", 20: "3-2", 21: "3-3", 22: "3-4", 23: "3-5", 24: "3-6",
    25: "3-7", 26: "3-8", 27: "3-9", 28: "4-1", 29: "4-2", 30: "4-3",
    31: "4-4", 32: "4-5", 33: "4-6", 34: "4-7", 35: "4-8", 36: "4-9"},
                        9900000, 'bishopvilleII', hst, None),

                    ('Bluebird', {
    1: "A1", 2: "A2", 3: "A3", 4: "A4", 5: "A5", 6: "A6",
    7: "A7", 8: "A8", 9: "A9", 10: "A10", 11: "A11", 12: "A12",
    13: "B13", 14: "B14", 15: "B15", 16: "B16", 17: "B17", 18: "B18",
    19: "B19", 20: "B20", 21: "B21", 22: "B22", 23: "B23", 24: "B24"}, 
                    3000000, 'bluebird', nar, 'BLUEBIRD'),

                    ('Bulloch 1A', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18",
    19: "19", 20: "20", 21: "21", 22: "22", 23: "23", 24: "24"}, 
                    3000000, 'bulloch1a', solrvr, 'BULLOCH1A'),

                    ('Bulloch 1B', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18",
    19: "19", 20: "20", 21: "21", 22: "22", 23: "23", 24: "24"}, 
                    3000000, 'bulloch1b', solrvr, 'BULLOCH1B'),

                    ('Cardinal', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "11", 12: "12", 13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18", 19: "19", 20: "20",
    21: "21", 22: "22", 23: "23", 24: "24", 25: "25", 26: "26", 27: "27", 28: "28", 29: "29", 30: "30",
    31: "31", 32: "32", 33: "33", 34: "34", 35: "35", 36: "36", 37: "37", 38: "38", 39: "39", 40: "40",
    41: "41", 42: "42", 43: "43", 44: "44", 45: "45", 46: "46", 47: "47", 48: "48", 49: "49", 50: "50",
    51: "51", 52: "52", 53: "53", 54: "54", 55: "55", 56: "56", 57: "57", 58: "58", 59: "59"}, 
                    7080000, 'cardinal', nar, 'CARDINAL'),

                    ('CDIA', {1:"1"}, 192000, 'cdia', nar, None),

                    ('Cherry Blossom', {1: "1", 2: "2", 3: "3", 4: "4"},
                     10000000, 'cherryblossom', nar, 'CHERRY BLOSSOM'),

                    ('Cougar', {
    1: "1-1", 2: "1-2", 3: "1-3", 4: "1-4", 5: "1-5", 6: "2-1",
    7: "2-2", 8: "2-3", 9: "2-4", 10: "2-5", 11: "2-6", 12: "3-1",
    13: "3-2", 14: "3-3", 15: "3-4", 16: "3-5", 17: "4-1", 18: "4-2",
    19: "4-3", 20: "4-4", 21: "4-5", 22: "5-1", 23: "5-2", 24: "5-3",
    25: "5-4", 26: "5-5", 27: "6-1", 28: "6-2", 29: "6-3", 30: "6-4", 31:"6-5"},
                     2670000, 'cougar', nar, 'COUGAR'),

                    ('Conetoe', {
    1: "1-1", 2: "1-2", 3: "1-3", 4: "1-4",
    5: "2-1", 6: "2-2", 7: "2-3", 8: "2-4",
    9: "3-1", 10: "3-2", 11: "3-3", 12: "3-4",
    13: "4-1", 14: "4-2", 15: "4-3", 16: "4-4"},
                     5000000, 'conetoe1', soltage, None),

                    ('Duplin', {
    1: "C-1", 2: "C-2", 3: "C-3", 4: "S-1", 5: "S-2", 6: "S-3",
    7: "S-4", 8: "S-5", 9: "S-6", 10: "S-7", 11: "S-8", 12: "S-9",
    13: "S-10", 14: "S-11", 15: "S-12", 16: "S-13", 17: "S-14", 18: "S-15",
    19: "S-16", 20: "S-17", 21: "S-18"},
                     5040000, 'duplin', soltage, None),

                    ('Elk', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "1-3", 10: "10",
    11: "11", 12: "12", 13: "13", 14: "14", 15: "3-3", 16: "16", 17: "17", 18: "18", 19: "19", 20: "20",
    21: "21", 22: "22", 23: "23", 24: "24", 25: "25", 26: "26", 27: "27", 28: "28", 29: "2-8", 30: "30",
    31: "31", 32: "32", 33: "2-13", 34: "34", 35: "3-7", 36: "3-8", 37: "37", 38: "38", 39: "3-11", 40: "40",
    41: "41", 42: "42", 43: "43"},
                    5380000, 'elk', solrvr, 'ELK'),

                    ('Freightliner', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "11", 12: "12", 13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18"},
                     2250000, 'freightliner', ncemc, 'FREIGHTLINE'), 

                    ('Gray Fox', {
    1: "1.1", 2: "1.2", 3: "1.3", 4: "1.4", 5: "1.5", 6: "1.6", 7: "1.7", 8: "1.8", 9: "1.9", 10: "1.10",
    11: "1.11", 12: "1.12", 13: "1.13", 14: "1.14", 15: "1.15", 16: "1.16", 17: "1.17", 18: "1.18", 19: "1.19", 20: "1.20",
    21: "2.1", 22: "2.2", 23: "2.3", 24: "2.4", 25: "2.5", 26: "2.6", 27: "2.7", 28: "2.8", 29: "2.9", 30: "2.10",
    31: "2.11", 32: "2.12", 33: "2.13", 34: "2.14", 35: "2.15", 36: "2.16", 37: "2.17", 38: "2.18", 39: "2.19", 40: "2.20"},
                     5000000, 'grayfox', solrvr, 'GRAYFOX'),

                    ('Harding', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18",
    19: "19", 20: "20", 21: "21", 22: "22", 23: "23", 24: "24"},
                     3000000, 'harding', solrvr, 'HARDING'),

                    ('Harrison', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "11", 12: "12", 13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18", 19: "19", 20: "20",
    21: "21", 22: "22", 23: "23", 24: "24", 25: "25", 26: "26", 27: "27", 28: "28", 29: "29", 30: "30",
    31: "31", 32: "32", 33: "33", 34: "34", 35: "35", 36: "36", 37: "37", 38: "38", 39: "39", 40: "40",
    41: "41", 42: "42", 43: "43"},
                    5380000, 'harrison', nar, 'HARRISON'),

                    ('Hayes', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18",
    19: "19", 20: "20", 21: "21", 22: "22", 23: "23", 24: "24", 25: "25", 26: "26"},
                     3240000, 'hayes', nar, 'HAYES'),

                    ('Hickory', {1:"1", 2:"2"}, 5000000, 'hickory', nar2, 'HICKORY'),
                    
                    ('Hickson', {
    1: "1-1", 2: "1-2", 3: "1-3", 4: "1-4", 5: "1-5", 6: "1-6",
    7: "1-7", 8: "1-8", 9: "1-9", 10: "1-10", 11: "1-11", 12: "1-12",
    13: "1-13", 14: "1-14", 15: "1-15", 16: "1-16"},
                     2000000, 'hickson', hst, None),

                    ('Holly Swamp', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16"},
                     2000000, 'hollyswamp', ncemc, 'HOLLYSWAMP'),
                    
                    ('Jefferson', {
    1: "1.1", 2: "1.2", 3: "1.3", 4: "1.4", 5: "1.5", 6: "1.6", 7: "1.7", 8: "1.8", 9: "1.9", 10: "1.10",
    11: "1.11", 12: "1.12", 13: "1.13", 14: "1.14", 15: "1.15", 16: "1.16",
    17: "2.1", 18: "2.2", 19: "2.3", 20: "2.4", 21: "2.5", 22: "2.6", 23: "2.7", 24: "2.8", 25: "2.9", 26: "2.10",
    27: "2.11", 28: "2.12", 29: "2.13", 30: "2.14", 31: "2.15", 32: "2.16",
    33: "3.1", 34: "3.2", 35: "3.3", 36: "3.4", 37: "3.5", 38: "3.6", 39: "3.7", 40: "3.8", 41: "3.9", 42: "3.10",
    43: "3.11", 44: "3.12", 45: "3.13", 46: "3.14", 47: "3.15", 48: "3.16",
    49: "4.1", 50: "4.2", 51: "4.3", 52: "4.4", 53: "4.5", 54: "4.6", 55: "4.7", 56: "4.8", 57: "4.9", 58: "4.10",
    59: "4.11", 60: "4.12", 61: "4.13", 62: "4.14", 63: "4.15", 64: "4.16"},
                     8000000, 'jefferson', hst, None),

                    ('Marshall', {
    1: "1.1", 2: "1.2", 3: "1.3", 4: "1.4", 5: "1.5", 6: "1.6",
    7: "1.7", 8: "1.8", 9: "1.9", 10: "1.10", 11: "1.11", 12: "1.12",
    13: "1.13", 14: "1.14", 15: "1.15", 16: "1.16"},
                    2000000, 'marshall', hst, None),

                    ('McLean', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "11", 12: "12", 13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18", 19: "19", 20: "20",
    21: "21", 22: "22", 23: "23", 24: "24", 25: "25", 26: "26", 27: "27", 28: "28", 29: "29", 30: "30",
    31: "31", 32: "32", 33: "33", 34: "34", 35: "35", 36: "36", 37: "37", 38: "38", 39: "39", 40: "40"},
                     5000000, 'mclean', solrvr, 'MCLEAN'), 
                    
                    ('Ogburn', {
    1: "1-1", 2: "1-2", 3: "1-3", 4: "1-4", 5: "1-5", 6: "1-6",
    7: "1-7", 8: "1-8", 9: "1-9", 10: "1-10", 11: "1-11", 12: "1-12",
    13: "1-13", 14: "1-14", 15: "1-15", 16: "1-16"},
                    2000000, 'ogburn', hst, None),
                    
                    ('PG', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18"},
                    2210000, 'pg', ncemc, 'PG'),
                    
                    ('Richmond', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18",
    19: "19", 20: "20", 21: "21", 22: "22", 23: "23", 24: "24"},
                    3000000, 'richmond', solrvr2, 'RICHMOND'),
                    
                    ('Shorthorn', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "11", 12: "12", 13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18", 19: "19", 20: "20",
    21: "21", 22: "22", 23: "23", 24: "24", 25: "25", 26: "26", 27: "27", 28: "28", 29: "29", 30: "30",
    31: "31", 32: "32", 33: "33", 34: "34", 35: "35", 36: "36", 37: "37", 38: "38", 39: "39", 40: "40",
    41: "41", 42: "42", 43: "43", 44: "44", 45: "45", 46: "46", 47: "47", 48: "48", 49: "49", 50: "50",
    51: "51", 52: "52", 53: "53", 54: "54", 55: "55", 56: "56", 57: "57", 58: "58", 59: "59", 60: "60",
    61: "61", 62: "62", 63: "63", 64: "64", 65: "65", 66: "66", 67: "67", 68: "68", 69: "69", 70: "70",
    71: "71", 72: "72"},
                    9000000, 'shorthorn', solrvr2, 'SHORTHORN'),

                    ('Sunflower', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "11", 12: "12", 13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18", 19: "19", 20: "20",
    21: "21", 22: "22", 23: "23", 24: "24", 25: "25", 26: "26", 27: "27", 28: "28", 29: "29", 30: "30",
    31: "31", 32: "32", 33: "33", 34: "34", 35: "35", 36: "36", 37: "37", 38: "38", 39: "39", 40: "40",
    41: "41", 42: "42", 43: "43", 44: "44", 45: "45", 46: "46", 47: "47", 48: "48", 49: "49", 50: "50",
    51: "51", 52: "52", 53: "53", 54: "54", 55: "55", 56: "56", 57: "57", 58: "58", 59: "59", 60: "60",
    61: "61", 62: "62", 63: "63", 64: "64", 65: "65", 66: "66", 67: "67", 68: "68", 69: "69", 70: "70",
    71: "71", 72: "72", 73: "73", 74: "74", 75: "75", 76: "76", 77: "77", 78: "78", 79: "79", 80: "80"},
                    10000000, 'sunflower', solrvr2, 'SUNFLOWER'), 
                    
                    ('Tedder', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16"},
                    2000000, 'tedder', hst, None),

                    ('Thunderhead', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16"},
                    2000000, 'thunderhead', hst2, None),
                    ('Upson', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18",
    19: "19", 20: "20", 21: "21", 22: "22", 23: "23", 24: "24"},
                    3000000, 'upson', solrvr2, None), 
                    
                    ('Van Buren', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16", 17: "17"},
                    2000000, 'vanburen', hst2, 'VAN BUREN'), 
                    
                    ('Warbler', {
    1: "A1", 2: "A2", 3: "A3", 4: "A4", 5: "A5", 6: "A6",
    7: "A7", 8: "A8", 9: "A9", 10: "A10", 11: "A11", 12: "A12",
    13: "A13", 14: "A14", 15: "A15", 16: "A16",
    17: "B17", 18: "B18", 19: "B19", 20: "B20", 21: "B21", 22: "B22",
    23: "B23", 24: "B24", 25: "B25", 26: "B26", 27: "B27", 28: "B28",
    29: "B29", 30: "B30", 31: "B31", 32: "B32"},
                    4000000, 'warbler', solrvr2, 'WARBLER'),
                    
                    ('Washington', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "11", 12: "12", 13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18", 19: "19", 20: "20",
    21: "21", 22: "22", 23: "23", 24: "24", 25: "25", 26: "26", 27: "27", 28: "28", 29: "29", 30: "30",
    31: "31", 32: "32", 33: "33", 34: "34", 35: "35", 36: "36", 37: "37", 38: "38", 39: "39", 40: "40"},
                    5000000, 'washington', solrvr3, None), 
                    
                    ('Wayne 1', {1: "1", 2: "2", 3: "3", 4: "4"}, 5000000, 'wayne1', soltage, None), 
                    
                    ('Wayne 2', {1: "1", 2: "2", 3: "3", 4: "4"}, 5000000, 'wayne2', soltage, None), 
                    
                    ('Wayne 3', {1: "1", 2: "2", 3: "3", 4: "4"}, 5000000, 'wayne3', soltage, None), 
                    
                    ('Wellons', {1: "1-1", 2: "1-2", 3: "2-1", 4: "2-2", 5:"3-1", 6:"3-2"}, 5000000, 'wellons', nar2, 'WELLONS'), 
                    
                    ('Whitehall', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16"},
                    2000000, 'whitehall', solrvr3, 'WHITEHALL'), 
                    
                    ('Whitetail', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "11", 12: "12", 13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18", 19: "19", 20: "20",
    21: "21", 22: "22", 23: "23", 24: "24", 25: "25", 26: "26", 27: "27", 28: "28", 29: "29", 30: "30",
    31: "31", 32: "32", 33: "33", 34: "34", 35: "35", 36: "36", 37: "37", 38: "38", 39: "39", 40: "40",
    41: "41", 42: "42", 43: "43", 44: "44", 45: "45", 46: "46", 47: "47", 48: "48", 49: "49", 50: "50",
    51: "51", 52: "52", 53: "53", 54: "54", 55: "55", 56: "56", 57: "57", 58: "58", 59: "59", 60: "60",
    61: "61", 62: "62", 63: "63", 64: "64", 65: "65", 66: "66", 67: "67", 68: "68", 69: "69", 70: "70",
    71: "71", 72: "72", 73: "73", 74: "74", 75: "75", 76: "76", 77: "77", 78: "78", 79: "79", 80: "80"},
                    10000000, 'whitetail', solrvr3, None),
                    
                    ('Violet', {1:"1", 2:"2"}, 5000000, 'violet', nar2, 'VIOLET')]

site_INV_groups = {
    "Cardinal": {
        "cardinal96daykwList": [
            "cardinal_INV_1_Watts", "cardinal_INV_2_Watts", "cardinal_INV_3_Watts",
            "cardinal_INV_4_Watts", "cardinal_INV_5_Watts", "cardinal_INV_6_Watts",
            "cardinal_INV_7_Watts", "cardinal_INV_22_Watts", "cardinal_INV_23_Watts",
            "cardinal_INV_24_Watts", "cardinal_INV_25_Watts", "cardinal_INV_26_Watts",
            "cardinal_INV_27_Watts", "cardinal_INV_28_Watts", "cardinal_INV_43_Watts",
            "cardinal_INV_44_Watts", "cardinal_INV_45_Watts", "cardinal_INV_46_Watts",
            "cardinal_INV_47_Watts"
        ],
        "cardinal952daykwList": [
            "cardinal_INV_8_Watts", "cardinal_INV_9_Watts", "cardinal_INV_10_Watts",
            "cardinal_INV_11_Watts", "cardinal_INV_12_Watts", "cardinal_INV_13_Watts",
            "cardinal_INV_14_Watts", "cardinal_INV_29_Watts", "cardinal_INV_30_Watts",
            "cardinal_INV_31_Watts", "cardinal_INV_32_Watts", "cardinal_INV_33_Watts",
            "cardinal_INV_34_Watts", "cardinal_INV_35_Watts", "cardinal_INV_48_Watts",
            "cardinal_INV_49_Watts", "cardinal_INV_50_Watts", "cardinal_INV_51_Watts",
            "cardinal_INV_52_Watts", "cardinal_INV_53_Watts"
        ],
        "cardinal944daykwList": [
            "cardinal_INV_15_Watts", "cardinal_INV_16_Watts", "cardinal_INV_17_Watts",
            "cardinal_INV_18_Watts", "cardinal_INV_19_Watts", "cardinal_INV_20_Watts",
            "cardinal_INV_21_Watts", "cardinal_INV_36_Watts", "cardinal_INV_37_Watts",
            "cardinal_INV_38_Watts", "cardinal_INV_39_Watts", "cardinal_INV_40_Watts",
            "cardinal_INV_41_Watts", "cardinal_INV_42_Watts", "cardinal_INV_54_Watts",
            "cardinal_INV_55_Watts", "cardinal_INV_56_Watts", "cardinal_INV_57_Watts",
            "cardinal_INV_58_Watts", "cardinal_INV_59_Watts"
        ]
    },
    "Bluebird": {
        "bluebirddaykwList": [
            "bluebird_INV_1_Watts", "bluebird_INV_2_Watts", "bluebird_INV_3_Watts",
            "bluebird_INV_4_Watts", "bluebird_INV_5_Watts", "bluebird_INV_6_Watts",
            "bluebird_INV_7_Watts", "bluebird_INV_8_Watts", "bluebird_INV_9_Watts",
            "bluebird_INV_10_Watts", "bluebird_INV_11_Watts", "bluebird_INV_12_Watts",
            "bluebird_INV_13_Watts", "bluebird_INV_14_Watts", "bluebird_INV_15_Watts",
            "bluebird_INV_16_Watts", "bluebird_INV_17_Watts", "bluebird_INV_18_Watts",
            "bluebird_INV_19_Watts", "bluebird_INV_20_Watts", "bluebird_INV_21_Watts",
            "bluebird_INV_22_Watts", "bluebird_INV_23_Watts", "bluebird_INV_24_Watts"
        ]
    },
    "Cherry Blossom": {
        "cherryblossomdaykwList": [
            "cherryblossominv_INV_1_Watts", "cherryblossominv_INV_2_Watts",
            "cherryblossominv_INV_3_Watts", "cherryblossominv_INV_4_Watts"
        ]
    },
    "Harrison": {
        "harrisondaykwList": [
            "harrison_INV_2_Watts", "harrison_INV_3_Watts", "harrison_INV_4_Watts",
            "harrison_INV_5_Watts", "harrison_INV_6_Watts", "harrison_INV_7_Watts",
            "harrison_INV_9_Watts", "harrison_INV_11_Watts", "harrison_INV_12_Watts",
            "harrison_INV_13_Watts", "harrison_INV_14_Watts", "harrison_INV_15_Watts",
            "harrison_INV_16_Watts", "harrison_INV_18_Watts", "harrison_INV_19_Watts",
            "harrison_INV_20_Watts", "harrison_INV_22_Watts", "harrison_INV_23_Watts",
            "harrison_INV_24_Watts", "harrison_INV_25_Watts", "harrison_INV_26_Watts",
            "harrison_INV_27_Watts", "harrison_INV_28_Watts", "harrison_INV_31_Watts",
            "harrison_INV_32_Watts", "harrison_INV_33_Watts", "harrison_INV_34_Watts",
            "harrison_INV_35_Watts", "harrison_INV_36_Watts", "harrison_INV_37_Watts",
            "harrison_INV_38_Watts", "harrison_INV_39_Watts", "harrison_INV_42_Watts",
            "harrison_INV_43_Watts"
        ],
        "harrison92daykwList": [
            "harrison_INV_1_Watts", "harrison_INV_8_Watts", "harrison_INV_10_Watts",
            "harrison_INV_17_Watts", "harrison_INV_21_Watts", "harrison_INV_29_Watts",
            "harrison_INV_30_Watts", "harrison_INV_40_Watts", "harrison_INV_41_Watts"
        ]
    },
    "Hayes": {
        "hayesdaykwList": [
            "hayes_INV_1_Watts", "hayes_INV_2_Watts", "hayes_INV_3_Watts",
            "hayes_INV_4_Watts", "hayes_INV_5_Watts", "hayes_INV_6_Watts",
            "hayes_INV_7_Watts", "hayes_INV_8_Watts", "hayes_INV_9_Watts",
            "hayes_INV_10_Watts", "hayes_INV_11_Watts", "hayes_INV_12_Watts",
            "hayes_INV_13_Watts", "hayes_INV_14_Watts", "hayes_INV_15_Watts",
            "hayes_INV_16_Watts", "hayes_INV_17_Watts", "hayes_INV_19_Watts",
            "hayes_INV_20_Watts", "hayes_INV_21_Watts", "hayes_INV_23_Watts",
            "hayes_INV_24_Watts", "hayes_INV_25_Watts", "hayes_INV_26_Watts"
        ],
        "hayes96daykwList": [
            "hayes_INV_22_Watts", "hayes_INV_18_Watts"
        ]
    },
    "Hickory": {
        "hickorydaykwList": [
            "hickory_INV_1_Watts", "hickory_INV_2_Watts"
        ]
    },
    "Vanburen": {
        "vanburendaykwList": [
            "vanburen_INV_7_Watts", "vanburen_INV_8_Watts", "vanburen_INV_9_Watts",
            "vanburen_INV_10_Watts", "vanburen_INV_11_Watts", "vanburen_INV_12_Watts",
            "vanburen_INV_13_Watts", "vanburen_INV_14_Watts", "vanburen_INV_15_Watts",
            "vanburen_INV_16_Watts", "vanburen_INV_17_Watts"
        ],
        "vanburen93daykwList": [
            "vanburen_INV_1_Watts", "vanburen_INV_2_Watts", "vanburen_INV_3_Watts",
            "vanburen_INV_4_Watts", "vanburen_INV_5_Watts", "vanburen_INV_6_Watts"
        ]
    },
    "Violet": {
        "violetdaykwList": [
            "violet_INV_1_Watts", "violet_INV_2_Watts"
        ]
    },
    "Wellons": {
        "wellonsdaykwList": [
            "wellons_INV_1_Watts", "wellons_INV_2_Watts", "wellons_INV_3_Watts",
            "wellons_INV_4_Watts", "wellons_INV_5_Watts", "wellons_INV_6_Watts"
        ]
    },
    "Bishopville II": {
        "bishopvilleIIdaykwList": [
            "bishopvilleII_INV_6_Watts", "bishopvilleII_INV_7_Watts",
            "bishopvilleII_INV_8_Watts", "bishopvilleII_INV_9_Watts",
            "bishopvilleII_INV_10_Watts", "bishopvilleII_INV_13_Watts",
            "bishopvilleII_INV_15_Watts", "bishopvilleII_INV_19_Watts",
            "bishopvilleII_INV_20_Watts", "bishopvilleII_INV_21_Watts",
            "bishopvilleII_INV_22_Watts", "bishopvilleII_INV_23_Watts",
            "bishopvilleII_INV_26_Watts", "bishopvilleII_INV_27_Watts",
            "bishopvilleII_INV_28_Watts", "bishopvilleII_INV_29_Watts",
            "bishopvilleII_INV_30_Watts", "bishopvilleII_INV_32_Watts",
            "bishopvilleII_INV_34_Watts"
        ],
        "bishopvilleII34strdaykwList": [
            "bishopvilleII_INV_1_Watts", "bishopvilleII_INV_2_Watts",
            "bishopvilleII_INV_3_Watts", "bishopvilleII_INV_4_Watts",
            "bishopvilleII_INV_5_Watts", "bishopvilleII_INV_11_Watts",
            "bishopvilleII_INV_12_Watts", "bishopvilleII_INV_14_Watts",
            "bishopvilleII_INV_16_Watts", "bishopvilleII_INV_17_Watts",
            "bishopvilleII_INV_18_Watts", "bishopvilleII_INV_31_Watts",
            "bishopvilleII_INV_33_Watts", "bishopvilleII_INV_35_Watts",
            "bishopvilleII_INV_36_Watts"
        ],
        "bishopvilleII36strdaykwList": [
            "bishopvilleII_INV_24_Watts", "bishopvilleII_INV_25_Watts"
        ]
    },
    "Hickson": {
        "hicksondaykwList": [
            "hickson_INV_7_Watts", "hickson_INV_8_Watts", "hickson_INV_9_Watts",
            "hickson_INV_12_Watts", "hickson_INV_13_Watts", "hickson_INV_14_Watts",
            "hickson_INV_15_Watts", "hickson_INV_16_Watts"
        ],
        "hickson17strdaykwList": [
            "hickson_INV_1_Watts", "hickson_INV_2_Watts", "hickson_INV_3_Watts",
            "hickson_INV_4_Watts", "hickson_INV_5_Watts", "hickson_INV_6_Watts",
            "hickson_INV_10_Watts", "hickson_INV_11_Watts"
        ]
    },
    "Jefferson": {
        "jeffersondaykwList": [
            "jefferson_INV_5_Watts", "jefferson_INV_7_Watts",
            "jefferson_INV_8_Watts", "jefferson_INV_9_Watts",
            "jefferson_INV_10_Watts", "jefferson_INV_11_Watts",
            "jefferson_INV_12_Watts", "jefferson_INV_15_Watts",
            "jefferson_INV_16_Watts", "jefferson_INV_19_Watts",
            "jefferson_INV_24_Watts", "jefferson_INV_26_Watts",
            "jefferson_INV_27_Watts", "jefferson_INV_28_Watts",
            "jefferson_INV_29_Watts", "jefferson_INV_30_Watts",
            "jefferson_INV_31_Watts", "jefferson_INV_32_Watts",
            "jefferson_INV_33_Watts", "jefferson_INV_34_Watts",
            "jefferson_INV_35_Watts", "jefferson_INV_36_Watts",
            "jefferson_INV_37_Watts", "jefferson_INV_38_Watts",
            "jefferson_INV_39_Watts", "jefferson_INV_48_Watts",
            "jefferson_INV_57_Watts", "jefferson_INV_58_Watts",
            "jefferson_INV_59_Watts", "jefferson_INV_60_Watts",
            "jefferson_INV_61_Watts", "jefferson_INV_62_Watts",
            "jefferson_INV_63_Watts", "jefferson_INV_64_Watts"
        ],
        "jefferson18strdaykwList": [
            "jefferson_INV_1_Watts", "jefferson_INV_2_Watts",
            "jefferson_INV_3_Watts", "jefferson_INV_4_Watts",
            "jefferson_INV_6_Watts", "jefferson_INV_13_Watts",
            "jefferson_INV_14_Watts", "jefferson_INV_17_Watts",
            "jefferson_INV_18_Watts", "jefferson_INV_20_Watts",
            "jefferson_INV_21_Watts", "jefferson_INV_22_Watts",
            "jefferson_INV_23_Watts", "jefferson_INV_25_Watts",
            "jefferson_INV_40_Watts", "jefferson_INV_41_Watts",
            "jefferson_INV_42_Watts", "jefferson_INV_43_Watts",
            "jefferson_INV_44_Watts", "jefferson_INV_45_Watts",
            "jefferson_INV_46_Watts", "jefferson_INV_47_Watts",
            "jefferson_INV_49_Watts", "jefferson_INV_50_Watts",
            "jefferson_INV_51_Watts", "jefferson_INV_52_Watts",
            "jefferson_INV_53_Watts", "jefferson_INV_54_Watts",
            "jefferson_INV_55_Watts", "jefferson_INV_56_Watts"
        ]
    },
    "Marshall": {
        "marshalldaykwList": [
            "marshall_INV_1_Watts", "marshall_INV_2_Watts", "marshall_INV_3_Watts",
            "marshall_INV_4_Watts", "marshall_INV_5_Watts", "marshall_INV_6_Watts",
            "marshall_INV_7_Watts", "marshall_INV_8_Watts", "marshall_INV_9_Watts",
            "marshall_INV_10_Watts", "marshall_INV_11_Watts", "marshall_INV_12_Watts",
            "marshall_INV_13_Watts", "marshall_INV_14_Watts", "marshall_INV_15_Watts",
            "marshall_INV_16_Watts"
        ]
    },
    "Ogburn": {
        "ogburndaykwList": [
            "ogburn_INV_1_Watts", "ogburn_INV_2_Watts", "ogburn_INV_3_Watts",
            "ogburn_INV_4_Watts", "ogburn_INV_5_Watts", "ogburn_INV_6_Watts",
            "ogburn_INV_7_Watts", "ogburn_INV_8_Watts", "ogburn_INV_9_Watts",
            "ogburn_INV_10_Watts", "ogburn_INV_11_Watts", "ogburn_INV_12_Watts",
            "ogburn_INV_13_Watts", "ogburn_INV_14_Watts", "ogburn_INV_15_Watts",
            "ogburn_INV_16_Watts"
        ]
    },
    "Tedder": {
        "tedderdaykwList": [
            "tedder_INV_5_Watts", "tedder_INV_6_Watts", "tedder_INV_7_Watts",
            "tedder_INV_9_Watts", "tedder_INV_10_Watts", "tedder_INV_11_Watts",
            "tedder_INV_12_Watts", "tedder_INV_13_Watts", "tedder_INV_14_Watts"
        ],
        "tedder15strdaykwList": [
            "tedder_INV_1_Watts", "tedder_INV_2_Watts", "tedder_INV_3_Watts",
            "tedder_INV_4_Watts", "tedder_INV_8_Watts", "tedder_INV_15_Watts",
            "tedder_INV_16_Watts"
        ]
    },
    "Thunderhead": {
        "thunderheaddaykwList": [
            "thunderhead_INV_1_Watts", "thunderhead_INV_2_Watts",
            "thunderhead_INV_3_Watts", "thunderhead_INV_4_Watts",
            "thunderhead_INV_5_Watts", "thunderhead_INV_6_Watts",
            "thunderhead_INV_7_Watts", "thunderhead_INV_8_Watts",
            "thunderhead_INV_9_Watts", "thunderhead_INV_10_Watts",
            "thunderhead_INV_11_Watts", "thunderhead_INV_12_Watts",
            "thunderhead_INV_14_Watts", "thunderhead_INV_16_Watts"
        ],
        "thunderhead14strdaykwList": [
            "thunderhead_INV_15_Watts", "thunderhead_INV_13_Watts"
        ]
    },
    "Bulloch 1A": {
        "bulloch1adaykwList": [
            "bulloch1a_INV_7_Watts", "bulloch1a_INV_8_Watts",
            "bulloch1a_INV_9_Watts", "bulloch1a_INV_10_Watts",
            "bulloch1a_INV_11_Watts", "bulloch1a_INV_12_Watts",
            "bulloch1a_INV_13_Watts", "bulloch1a_INV_14_Watts",
            "bulloch1a_INV_15_Watts", "bulloch1a_INV_16_Watts",
            "bulloch1a_INV_17_Watts", "bulloch1a_INV_18_Watts",
            "bulloch1a_INV_19_Watts", "bulloch1a_INV_20_Watts",
            "bulloch1a_INV_21_Watts", "bulloch1a_INV_22_Watts",
            "bulloch1a_INV_23_Watts", "bulloch1a_INV_24_Watts"
        ],
        "bulloch1a10strdaykwList": [
            "bulloch1a_INV_1_Watts", "bulloch1a_INV_2_Watts",
            "bulloch1a_INV_3_Watts", "bulloch1a_INV_4_Watts",
            "bulloch1a_INV_5_Watts", "bulloch1a_INV_6_Watts"
        ]
    },
    "Bulloch 1B": {
        "bulloch1bdaykwList": [
            "bulloch1b_INV_2_Watts", "bulloch1b_INV_3_Watts",
            "bulloch1b_INV_4_Watts", "bulloch1b_INV_5_Watts",
            "bulloch1b_INV_6_Watts", "bulloch1b_INV_7_Watts",
            "bulloch1b_INV_8_Watts", "bulloch1b_INV_13_Watts",
            "bulloch1b_INV_14_Watts", "bulloch1b_INV_15_Watts",
            "bulloch1b_INV_16_Watts", "bulloch1b_INV_18_Watts",
            "bulloch1b_INV_19_Watts", "bulloch1b_INV_20_Watts",
            "bulloch1b_INV_21_Watts", "bulloch1b_INV_22_Watts",
            "bulloch1b_INV_23_Watts", "bulloch1b_INV_24_Watts"
        ],
        "bulloch1b10strdaykwList": [
            "bulloch1b_INV_1_Watts", "bulloch1b_INV_9_Watts",
            "bulloch1b_INV_10_Watts", "bulloch1b_INV_11_Watts",
            "bulloch1b_INV_12_Watts", "bulloch1b_INV_17_Watts"
        ]
    },
    "Gray Fox": {
        "grayfoxdaykwList": [
            "grayfox_INV_1_Watts", "grayfox_INV_2_Watts", "grayfox_INV_3_Watts",
            "grayfox_INV_4_Watts", "grayfox_INV_5_Watts", "grayfox_INV_6_Watts",
            "grayfox_INV_7_Watts", "grayfox_INV_8_Watts", "grayfox_INV_9_Watts",
            "grayfox_INV_10_Watts", "grayfox_INV_11_Watts", "grayfox_INV_12_Watts",
            "grayfox_INV_13_Watts", "grayfox_INV_14_Watts", "grayfox_INV_15_Watts",
            "grayfox_INV_16_Watts", "grayfox_INV_17_Watts", "grayfox_INV_18_Watts",
            "grayfox_INV_19_Watts", "grayfox_INV_20_Watts", "grayfox_INV_21_Watts",
            "grayfox_INV_22_Watts", "grayfox_INV_23_Watts", "grayfox_INV_24_Watts",
            "grayfox_INV_25_Watts", "grayfox_INV_26_Watts", "grayfox_INV_27_Watts",
            "grayfox_INV_28_Watts", "grayfox_INV_29_Watts", "grayfox_INV_30_Watts",
            "grayfox_INV_31_Watts", "grayfox_INV_32_Watts", "grayfox_INV_33_Watts",
            "grayfox_INV_34_Watts", "grayfox_INV_35_Watts", "grayfox_INV_36_Watts",
            "grayfox_INV_37_Watts", "grayfox_INV_38_Watts", "grayfox_INV_39_Watts",
            "grayfox_INV_40_Watts"
        ]
    },
    "Harding": {
        "hardingdaykwList": [
            "harding_INV_4_Watts", "harding_INV_5_Watts", "harding_INV_6_Watts",
            "harding_INV_10_Watts", "harding_INV_11_Watts", "harding_INV_12_Watts",
            "harding_INV_13_Watts", "harding_INV_14_Watts", "harding_INV_15_Watts",
            "harding_INV_17_Watts", "harding_INV_18_Watts", "harding_INV_19_Watts"
        ],
        "harding12strdaykwList": [
            "harding_INV_1_Watts", "harding_INV_2_Watts", "harding_INV_3_Watts",
            "harding_INV_7_Watts", "harding_INV_8_Watts", "harding_INV_9_Watts",
            "harding_INV_16_Watts", "harding_INV_20_Watts", "harding_INV_21_Watts",
            "harding_INV_22_Watts", "harding_INV_23_Watts", "harding_INV_24_Watts"
        ]
    },
    "McLean": {
        "mcleandaykwList": [
            "mclean_INV_2_Watts",  "mclean_INV_3_Watts",  "mclean_INV_4_Watts",
            "mclean_INV_5_Watts",  "mclean_INV_6_Watts",  "mclean_INV_7_Watts",
            "mclean_INV_8_Watts",  "mclean_INV_9_Watts",  "mclean_INV_10_Watts",
            "mclean_INV_11_Watts", "mclean_INV_12_Watts", "mclean_INV_13_Watts",
            "mclean_INV_14_Watts", "mclean_INV_15_Watts", "mclean_INV_16_Watts",
            "mclean_INV_18_Watts", "mclean_INV_20_Watts",  "mclean_INV_22_Watts",
            "mclean_INV_24_Watts", "mclean_INV_25_Watts", "mclean_INV_26_Watts",
            "mclean_INV_30_Watts"
        ],
        "mclean10strdaykwList": [
            "mclean_INV_1_Watts",  "mclean_INV_17_Watts", "mclean_INV_19_Watts",
            "mclean_INV_21_Watts", "mclean_INV_23_Watts", "mclean_INV_27_Watts",
            "mclean_INV_28_Watts", "mclean_INV_29_Watts", "mclean_INV_31_Watts",
            "mclean_INV_32_Watts", "mclean_INV_33_Watts", "mclean_INV_34_Watts",
            "mclean_INV_35_Watts", "mclean_INV_36_Watts", "mclean_INV_37_Watts",
            "mclean_INV_38_Watts", "mclean_INV_39_Watts", "mclean_INV_40_Watts"
        ]
    },
    "Richmond": {
        "richmonddaykwList": [
            "richmond_INV_1_Watts", "richmond_INV_2_Watts", "richmond_INV_3_Watts",
            "richmond_INV_4_Watts", "richmond_INV_5_Watts", "richmond_INV_6_Watts",
            "richmond_INV_7_Watts", "richmond_INV_11_Watts", "richmond_INV_12_Watts",
            "richmond_INV_13_Watts", "richmond_INV_14_Watts", "richmond_INV_15_Watts",
            "richmond_INV_16_Watts", "richmond_INV_17_Watts", "richmond_INV_18_Watts",
            "richmond_INV_19_Watts", "richmond_INV_20_Watts", "richmond_INV_21_Watts"
        ],
        "richmond10strdaykwList": [
            "richmond_INV_8_Watts", "richmond_INV_9_Watts", "richmond_INV_10_Watts",
            "richmond_INV_22_Watts", "richmond_INV_23_Watts", "richmond_INV_24_Watts"
        ]
    },
    "Shorthorn": {
        "shorthorndaykwList": [
            "shorthorn_INV_1_Watts", "shorthorn_INV_2_Watts", "shorthorn_INV_3_Watts",
            "shorthorn_INV_4_Watts", "shorthorn_INV_5_Watts", "shorthorn_INV_6_Watts",
            "shorthorn_INV_7_Watts", "shorthorn_INV_8_Watts", "shorthorn_INV_9_Watts",
            "shorthorn_INV_10_Watts", "shorthorn_INV_11_Watts", "shorthorn_INV_12_Watts",
            "shorthorn_INV_13_Watts", "shorthorn_INV_14_Watts", "shorthorn_INV_15_Watts",
            "shorthorn_INV_16_Watts", "shorthorn_INV_17_Watts", "shorthorn_INV_18_Watts",
            "shorthorn_INV_19_Watts", "shorthorn_INV_20_Watts", "shorthorn_INV_22_Watts",
            "shorthorn_INV_23_Watts", "shorthorn_INV_24_Watts",  "shorthorn_INV_26_Watts",
            "shorthorn_INV_27_Watts", "shorthorn_INV_28_Watts",  "shorthorn_INV_32_Watts",
            "shorthorn_INV_33_Watts",  "shorthorn_INV_37_Watts", "shorthorn_INV_38_Watts",
            "shorthorn_INV_39_Watts", "shorthorn_INV_40_Watts", "shorthorn_INV_41_Watts",
            "shorthorn_INV_42_Watts", "shorthorn_INV_43_Watts", "shorthorn_INV_45_Watts",
            "shorthorn_INV_46_Watts", "shorthorn_INV_47_Watts", "shorthorn_INV_48_Watts",
            "shorthorn_INV_52_Watts", "shorthorn_INV_53_Watts", "shorthorn_INV_57_Watts",
            "shorthorn_INV_58_Watts", "shorthorn_INV_59_Watts", "shorthorn_INV_60_Watts",
            "shorthorn_INV_61_Watts", "shorthorn_INV_62_Watts", "shorthorn_INV_63_Watts",
            "shorthorn_INV_64_Watts", "shorthorn_INV_65_Watts", "shorthorn_INV_66_Watts"
        ],
        "shorthorn13strdaykwList": [
            "shorthorn_INV_21_Watts", "shorthorn_INV_25_Watts", "shorthorn_INV_29_Watts",
            "shorthorn_INV_30_Watts", "shorthorn_INV_31_Watts", "shorthorn_INV_34_Watts",
            "shorthorn_INV_35_Watts", "shorthorn_INV_36_Watts",  "shorthorn_INV_44_Watts",
            "shorthorn_INV_49_Watts", "shorthorn_INV_50_Watts", "shorthorn_INV_51_Watts",
            "shorthorn_INV_54_Watts", "shorthorn_INV_55_Watts", "shorthorn_INV_56_Watts",
            "shorthorn_INV_67_Watts", "shorthorn_INV_68_Watts", "shorthorn_INV_69_Watts",
            "shorthorn_INV_70_Watts", "shorthorn_INV_71_Watts", "shorthorn_INV_72_Watts"
        ]
    },
    "Sunflower": {
        "sunflowerdaykwList": [
            "sunflower_INV_3_Watts", "sunflower_INV_4_Watts", "sunflower_INV_5_Watts",
            "sunflower_INV_6_Watts", "sunflower_INV_7_Watts", "sunflower_INV_8_Watts",
            "sunflower_INV_9_Watts", "sunflower_INV_10_Watts", "sunflower_INV_11_Watts",
            "sunflower_INV_12_Watts", "sunflower_INV_13_Watts", "sunflower_INV_14_Watts",
            "sunflower_INV_15_Watts", "sunflower_INV_16_Watts", "sunflower_INV_17_Watts",
            "sunflower_INV_18_Watts", "sunflower_INV_19_Watts", "sunflower_INV_20_Watts",
            "sunflower_INV_34_Watts",  "sunflower_INV_62_Watts",
            "sunflower_INV_63_Watts", "sunflower_INV_64_Watts", "sunflower_INV_65_Watts",
            "sunflower_INV_66_Watts", "sunflower_INV_67_Watts", "sunflower_INV_68_Watts",
            "sunflower_INV_69_Watts", "sunflower_INV_70_Watts", "sunflower_INV_71_Watts",
            "sunflower_INV_72_Watts", "sunflower_INV_73_Watts", "sunflower_INV_74_Watts",
            "sunflower_INV_75_Watts", "sunflower_INV_76_Watts", "sunflower_INV_77_Watts"
        ],
        "sunflower12strdaykwList": [
            "sunflower_INV_1_Watts", "sunflower_INV_2_Watts", "sunflower_INV_21_Watts",
            "sunflower_INV_22_Watts", "sunflower_INV_23_Watts", "sunflower_INV_24_Watts",
            "sunflower_INV_25_Watts", "sunflower_INV_26_Watts",  "sunflower_INV_27_Watts",
            "sunflower_INV_28_Watts", "sunflower_INV_29_Watts", "sunflower_INV_30_Watts",
            "sunflower_INV_31_Watts", "sunflower_INV_32_Watts",  "sunflower_INV_33_Watts",
            "sunflower_INV_35_Watts", "sunflower_INV_36_Watts", "sunflower_INV_37_Watts",
            "sunflower_INV_38_Watts", "sunflower_INV_39_Watts", "sunflower_INV_40_Watts",
            "sunflower_INV_41_Watts", "sunflower_INV_42_Watts", "sunflower_INV_43_Watts",
            "sunflower_INV_44_Watts", "sunflower_INV_45_Watts", "sunflower_INV_46_Watts",
            "sunflower_INV_47_Watts", "sunflower_INV_48_Watts", "sunflower_INV_49_Watts",
            "sunflower_INV_50_Watts", "sunflower_INV_51_Watts", "sunflower_INV_52_Watts",
            "sunflower_INV_53_Watts", "sunflower_INV_54_Watts", "sunflower_INV_55_Watts",
            "sunflower_INV_56_Watts", "sunflower_INV_57_Watts", "sunflower_INV_58_Watts",
            "sunflower_INV_59_Watts", "sunflower_INV_60_Watts", "sunflower_INV_61_Watts",
            "sunflower_INV_78_Watts", "sunflower_INV_79_Watts", "sunflower_INV_80_Watts"
        ]
    },
    "Upson": {
        "upsondaykwList": [
            "upson_INV_1_Watts", "upson_INV_2_Watts", "upson_INV_3_Watts",
            "upson_INV_4_Watts", "upson_INV_5_Watts", "upson_INV_9_Watts",
            "upson_INV_10_Watts", "upson_INV_11_Watts", "upson_INV_12_Watts",
            "upson_INV_13_Watts", "upson_INV_14_Watts", "upson_INV_15_Watts",
            "upson_INV_16_Watts", "upson_INV_17_Watts", "upson_INV_21_Watts",
            "upson_INV_22_Watts", "upson_INV_23_Watts", "upson_INV_24_Watts"
        ],
        "upson10strdaykwList": [
            "upson_INV_6_Watts", "upson_INV_7_Watts", "upson_INV_8_Watts",
            "upson_INV_18_Watts", "upson_INV_19_Watts", "upson_INV_20_Watts"
        ]
    },
    "Warbler": {
        "warblerdaykwList": [
            "warbler_INV_1_Watts", "warbler_INV_2_Watts", "warbler_INV_3_Watts",
            "warbler_INV_4_Watts", "warbler_INV_5_Watts", "warbler_INV_6_Watts",
            "warbler_INV_7_Watts", "warbler_INV_8_Watts", "warbler_INV_9_Watts",
            "warbler_INV_10_Watts", "warbler_INV_11_Watts", "warbler_INV_12_Watts",
            "warbler_INV_13_Watts", "warbler_INV_14_Watts", "warbler_INV_15_Watts",
            "warbler_INV_16_Watts", "warbler_INV_17_Watts", "warbler_INV_18_Watts",
            "warbler_INV_19_Watts", "warbler_INV_20_Watts", "warbler_INV_21_Watts",
            "warbler_INV_22_Watts", "warbler_INV_23_Watts", "warbler_INV_24_Watts",
            "warbler_INV_25_Watts", "warbler_INV_26_Watts", "warbler_INV_27_Watts",
            "warbler_INV_28_Watts", "warbler_INV_29_Watts", "warbler_INV_30_Watts",
            "warbler_INV_31_Watts", "warbler_INV_32_Watts"
        ]
    },
    "Washington": {
        "washingtondaykwList": [
            "washington_INV_4_Watts", "washington_INV_5_Watts",
            "washington_INV_6_Watts", "washington_INV_7_Watts",
            "washington_INV_8_Watts", "washington_INV_9_Watts",
            "washington_INV_10_Watts", "washington_INV_11_Watts",
            "washington_INV_12_Watts", "washington_INV_15_Watts",
            "washington_INV_16_Watts", "washington_INV_17_Watts",
            "washington_INV_18_Watts", "washington_INV_19_Watts",
            "washington_INV_21_Watts", "washington_INV_22_Watts",
            "washington_INV_23_Watts", "washington_INV_24_Watts",
            "washington_INV_40_Watts"
        ],
        "washington12strdaykwList": [
            "washington_INV_1_Watts", "washington_INV_2_Watts",
            "washington_INV_3_Watts", "washington_INV_13_Watts",
            "washington_INV_14_Watts", "washington_INV_20_Watts",
            "washington_INV_25_Watts", "washington_INV_26_Watts",
            "washington_INV_27_Watts", "washington_INV_28_Watts",
            "washington_INV_29_Watts", "washington_INV_30_Watts",
            "washington_INV_31_Watts", "washington_INV_32_Watts",
            "washington_INV_33_Watts", "washington_INV_34_Watts",
            "washington_INV_35_Watts", "washington_INV_36_Watts",
            "washington_INV_37_Watts", "washington_INV_38_Watts",
            "washington_INV_39_Watts"
        ]
    },
    "Whitehall": {
        "whitehalldaykwList": [
            "whitehall_INV_1_Watts", "whitehall_INV_3_Watts",
            "whitehall_INV_4_Watts", "whitehall_INV_5_Watts",
            "whitehall_INV_13_Watts", "whitehall_INV_14_Watts",
            "whitehall_INV_15_Watts", "whitehall_INV_16_Watts"
        ],
        "whitehall13strdaykwList": [
            "whitehall_INV_2_Watts", "whitehall_INV_6_Watts",
            "whitehall_INV_7_Watts", "whitehall_INV_8_Watts",
            "whitehall_INV_9_Watts", "whitehall_INV_10_Watts",
            "whitehall_INV_11_Watts", "whitehall_INV_12_Watts"
        ]
    },
    "Whitetail": {
        "whitetaildaykwList": [
            "whitetail_INV_1_Watts", "whitetail_INV_2_Watts", "whitetail_INV_3_Watts",
            "whitetail_INV_5_Watts", "whitetail_INV_6_Watts", "whitetail_INV_7_Watts",
            "whitetail_INV_8_Watts", "whitetail_INV_9_Watts", "whitetail_INV_10_Watts",
            "whitetail_INV_11_Watts", "whitetail_INV_12_Watts",  "whitetail_INV_22_Watts",
            "whitetail_INV_23_Watts", "whitetail_INV_24_Watts", "whitetail_INV_25_Watts",
            "whitetail_INV_32_Watts", "whitetail_INV_33_Watts",  "whitetail_INV_35_Watts",
            "whitetail_INV_36_Watts", "whitetail_INV_37_Watts", "whitetail_INV_38_Watts",
            "whitetail_INV_39_Watts", "whitetail_INV_40_Watts", "whitetail_INV_41_Watts",
            "whitetail_INV_42_Watts",  "whitetail_INV_49_Watts", "whitetail_INV_50_Watts",
            "whitetail_INV_51_Watts",  "whitetail_INV_57_Watts",  "whitetail_INV_61_Watts",
            "whitetail_INV_62_Watts", "whitetail_INV_63_Watts", "whitetail_INV_65_Watts",
            "whitetail_INV_66_Watts", "whitetail_INV_67_Watts", "whitetail_INV_68_Watts",
            "whitetail_INV_69_Watts", "whitetail_INV_70_Watts", "whitetail_INV_71_Watts",
            "whitetail_INV_72_Watts", "whitetail_INV_73_Watts", "whitetail_INV_74_Watts",
            "whitetail_INV_75_Watts", "whitetail_INV_76_Watts", "whitetail_INV_77_Watts",
            "whitetail_INV_78_Watts", "whitetail_INV_79_Watts", "whitetail_INV_80_Watts"
        ],
        "whitetail17strdaykwList": [
            "whitetail_INV_4_Watts",  "whitetail_INV_13_Watts",
            "whitetail_INV_14_Watts", "whitetail_INV_15_Watts",
            "whitetail_INV_16_Watts", "whitetail_INV_17_Watts",
            "whitetail_INV_18_Watts", "whitetail_INV_19_Watts",
            "whitetail_INV_20_Watts", "whitetail_INV_21_Watts",
            "whitetail_INV_26_Watts", "whitetail_INV_27_Watts",
            "whitetail_INV_28_Watts", "whitetail_INV_29_Watts",
            "whitetail_INV_30_Watts", "whitetail_INV_31_Watts",
            "whitetail_INV_34_Watts", "whitetail_INV_43_Watts",
            "whitetail_INV_44_Watts", "whitetail_INV_45_Watts",
            "whitetail_INV_46_Watts", "whitetail_INV_47_Watts",
            "whitetail_INV_48_Watts", "whitetail_INV_52_Watts",
            "whitetail_INV_53_Watts", "whitetail_INV_54_Watts",
            "whitetail_INV_55_Watts", "whitetail_INV_56_Watts",
            "whitetail_INV_58_Watts", "whitetail_INV_59_Watts",
            "whitetail_INV_60_Watts", "whitetail_INV_64_Watts"
        ]
    },
    "Conetoe": {
        "conetoe1daykwList": [
            "conetoe1_INV_1_Watts", "conetoe1_INV_2_Watts", "conetoe1_INV_3_Watts",
            "conetoe1_INV_4_Watts", "conetoe1_INV_5_Watts", "conetoe1_INV_6_Watts",
            "conetoe1_INV_7_Watts", "conetoe1_INV_8_Watts", "conetoe1_INV_9_Watts",
            "conetoe1_INV_10_Watts", "conetoe1_INV_11_Watts", "conetoe1_INV_12_Watts",
            "conetoe1_INV_13_Watts", "conetoe1_INV_14_Watts", "conetoe1_INV_15_Watts",
            "conetoe1_INV_16_Watts"
        ]
    },
    "Duplin": {
        "duplindaykwList": [
            "duplins_INV_1_Watts",  "duplins_INV_2_Watts",  "duplins_INV_3_Watts",
            "duplins_INV_8_Watts",  "duplins_INV_5_Watts",  "duplins_INV_6_Watts",
            "duplins_INV_7_Watts",  "duplins_INV_8_Watts",  "duplins_INV_9_Watts",
            "duplins_INV_10_Watts", "duplins_INV_11_Watts", "duplins_INV_12_Watts",
            "duplins_INV_13_Watts", "duplins_INV_14_Watts", "duplins_INV_15_Watts",
            "duplins_INV_16_Watts", "duplins_INV_17_Watts", "duplins_INV_18_Watts"
        ],
        "duplinCentraldaykwList": [
            "duplin_INV_1_Watts",  "duplin_INV_2_Watts",  "duplin_INV_3_Watts"
        ]
    },
    "Wayne 1": {
        "wayne1daykwList": [
            "wayne1_INV_2_Watts", "wayne1_INV_3_Watts"
        ],
        "wayne11000daykwList": [
            "wayne1_INV_1_Watts", "wayne1_INV_4_Watts"
        ]
    },
    "Wayne 2": {
        "wayne2daykwList": [
            "wayne2_INV_1_Watts", "wayne2_INV_2_Watts"
        ],
        "wayne21000daykwList": [
            "wayne2_INV_3_Watts",  "wayne2_INV_4_Watts"
        ]
    },
    "Wayne 3": {
        "wayne3daykwList": [
            "wayne3_INV_3_Watts", "wayne3_INV_4_Watts"
        ],
        "wayne31000daykwList": [
            "wayne3_INV_1_Watts", "wayne3_INV_2_Watts"
        ]
    },
    "Freightliner": {
        "freightlinedaykwList": [
            "freightliner_INV_1_Watts",  "freightliner_INV_3_Watts",
            "freightliner_INV_4_Watts",  "freightliner_INV_5_Watts",
            "freightliner_INV_8_Watts",  "freightliner_INV_9_Watts",
            "freightliner_INV_10_Watts", "freightliner_INV_11_Watts",
            "freightliner_INV_12_Watts", "freightliner_INV_15_Watts",
            "freightliner_INV_16_Watts", "freightliner_INV_17_Watts",
            "freightliner_INV_18_Watts"
        ],
        "freightline66daykwList": [
            "freightliner_INV_2_Watts",  "freightliner_INV_6_Watts",
            "freightliner_INV_7_Watts",  "freightliner_INV_13_Watts",
            "freightliner_INV_14_Watts"
        ]
    },
    "Holly Swamp": {
        "hollyswampdaykwList": [
            "hollyswamp_INV_1_Watts", "hollyswamp_INV_2_Watts",
            "hollyswamp_INV_3_Watts", "hollyswamp_INV_4_Watts",
            "hollyswamp_INV_5_Watts", "hollyswamp_INV_6_Watts",
            "hollyswamp_INV_7_Watts", "hollyswamp_INV_8_Watts",
            "hollyswamp_INV_9_Watts", "hollyswamp_INV_10_Watts",
            "hollyswamp_INV_11_Watts", "hollyswamp_INV_12_Watts",
            "hollyswamp_INV_14_Watts", "hollyswamp_INV_16_Watts"
        ],
        "hollyswamp18strdaykwList": [
            "hollyswamp_INV_15_Watts", "hollyswamp_INV_13_Watts"
        ]
    },
    "PG": {
        "pgdaykwList": [
            "pg_INV_7_Watts",  "pg_INV_8_Watts",  "pg_INV_9_Watts",
            "pg_INV_10_Watts", "pg_INV_11_Watts", "pg_INV_12_Watts",
            "pg_INV_13_Watts", "pg_INV_14_Watts", "pg_INV_15_Watts",
            "pg_INV_16_Watts", "pg_INV_17_Watts", "pg_INV_18_Watts"
        ],
        "pg66daykwList": [
            "pg_INV_1_Watts", "pg_INV_2_Watts", "pg_INV_3_Watts",
            "pg_INV_4_Watts", "pg_INV_5_Watts", "pg_INV_6_Watts"
        ]
    },
}



sites_WObreakers = {'Bluebird', 'Bulloch 1A', 'Bulloch 1B', 'Conetoe', 'CDIA', 'Cougar', 'Duplin', 'Freightliner', 'Holly Swamp', 'PG', 'Richmond', 'Upson', 'Van Buren', 'Wayne 1', 'Wayne 2', 'Wayne 3', 'Wellons'}
#I Don't Need both, Don't know why I still have both, but I do.
has_breaker = {'Bishopville II', 'Cardinal', 'Cherry Blossom', 'Elk', 'Gray Fox', 'Harding', 'Harrison', 'Hayes', 'Hickory', 'Hickson', 'Jefferson', 'Marshall', 'McLean', 'Ogburn', 
               'Shorthorn', 'Sunflower', 'Tedder', 'Thunderhead', 'Warbler', 'Washington', 'Whitehall', 'Whitetail', 'Violet'}

all_CBs = []


normal_numbering = {'Bluebird', 'Cardinal', 'Cherry Blossom', 'Cougar', 'Harrison', 'Hayes', 'Hickory', 'Violet', 'HICKSON',
                    'JEFFERSON', 'Marshall', 'OGBURN', 'Tedder', 'Thunderhead', 'Van Buren', 'Bulloch 1A', 'Bulloch 1B', 'Elk', 'Duplin',
                    'Harding', 'Mclean', 'Richmond Cadle', 'Shorthorn', 'Sunflower', 'Upson', 'Warbler', 'Washington', 'Whitehall', 'Whitetail',
                    'Conetoe 1', 'Wayne I', 'Wayne II', 'Wayne III', 'Freight Line', 'Holly Swamp', 'PG'}

number20set = {'Gray Fox'}
number9set = {'BISHOPVILLE'}
number2set = {'Wellons Farm'}

def define_inv_num(site, group, num):
    group = int(group)
    num = int(num)

    if site in normal_numbering:
        return num
    elif site in number20set:
        inv = num+((20*group)-20)
        return inv
    elif site in number9set:
        inv = num+((9*group)-9)
        return inv
    elif site in number2set:
        inv = num+((2*group)-2)
        return inv


def open_wo_tracking(name):
    os.startfile(f"G:\\Shared drives\\O&M\\NCC Automations\\Notification System\\WO Tracking\\{name} Open WO's.txt")


#Start looping through the dictionary at the top to create what is Below. 
#This one shall create the Sites Breaker/Meter/POA window
for ro, (name, invdict, metermax, varname, custid, pvsyst_name) in enumerate(master_List_Sites, start=1):
    invnum = len(invdict)
    #Site Info
    #Main Color
    globals()[f'{varname}Label'] = Label(root, bg=main_color, text=name, fg= 'black', font=('Tk_defaultFont', 10, 'bold'))
    globals()[f'{varname}Label'].grid(row=ro, column= 0, sticky=W)
    if name in has_breaker:
        if name == 'Violet':
            vio_excep = 1
        else:
            vio_excep = ''
        globals()[f'{varname}{vio_excep}statusLabel'] = Label(root, bg=main_color, text='❌', fg= 'black')
        globals()[f'{varname}{vio_excep}statusLabel'].grid(row=ro, column= 1)
        if name == 'Violet':
            violet2statusLabel = Label(root, bg=main_color, text='❌', fg= 'black')
            violet2statusLabel.grid(row=ro+1, column= 1)

    if name != 'CDIA':
        #Site Voltage Boolean
        globals()[f'{varname}meterVLabel'] = Label(root, bg=main_color, text='V', fg= 'black')
        globals()[f'{varname}meterVLabel'].grid(row=ro, column= 2)

    globals()[f'{varname}metercbval'] = IntVar()
    all_CBs.append(globals()[f'{varname}metercbval'])
    globals()[f'{varname}metercb'] = Checkbutton(root, bg=main_color, variable=globals()[f'{varname}metercbval'], fg= 'black', cursor='hand2')
    globals()[f'{varname}metercb'].grid(row=ro, column= 3)
    #Meter Producing Boolean
    globals()[f'{varname}meterkWLabel'] = Label(root, bg=main_color, text='kW', fg= 'black')
    globals()[f'{varname}meterkWLabel'].grid(row=ro, column= 4)
    #Meter % of Max capability
    globals()[f'{varname}meterRatioLabel'] = Label(root, bg=main_color, text='Ratio', fg= 'black')
    globals()[f'{varname}meterRatioLabel'].grid(row=ro, column= 5)
    #PVSyst Value
    globals()[f'{varname}meterPvSystLabel'] = Label(root, bg=main_color, text='Ratio', fg= 'black')
    globals()[f'{varname}meterPvSystLabel'].grid(row=ro, column= 6)

    globals()[f'{varname}POAcbval'] = IntVar()
    all_CBs.append(globals()[f'{varname}POAcbval'])
    globals()[f'{varname}POAcb'] = Checkbutton(root, bg=main_color, text='X', variable=globals()[f'{varname}POAcbval'], fg= 'black', cursor='hand2')
    globals()[f'{varname}POAcb'].grid(row=ro, column= 7)
    #End
    #INVERTER INFO
    length_limit = 73
    if name != 'CDIA':
        if invnum > length_limit:
            span_col = 6
        else:
            span_col = 3

        globals()[f'{varname}invsLabel'] = Button(custid, text=name, command=lambda name=varname: open_wo_tracking(name), bg=main_color, font=("Tk_defaultFont", 12, 'bold'), cursor='hand2')
        globals()[f'{varname}invsLabel'].grid(row= 0, column= ro*3, columnspan= span_col, sticky='ew')
    for num in range(1, invnum+1):
        column_offset = 0 if num <= length_limit else 3
        row_offset = num if num <= length_limit else num - length_limit
        if name != 'CDIA':
            if num in invdict:  # Check if the key exists in the dictionary
                inv_val = invdict[num]
            else:
                inv_val = str(num)

            globals()[f'{varname}inv{inv_val}cbval'] = IntVar()
            all_CBs.append(globals()[f'{varname}inv{inv_val}cbval'])
            globals()[f'{varname}inv{inv_val}cb'] = Checkbutton(custid, text=str(inv_val), variable=globals()[f'{varname}inv{inv_val}cbval'], cursor='hand2')
            globals()[f'{varname}inv{inv_val}cb'].grid(row= row_offset, column= (ro*3)+column_offset, sticky=W)

            globals()[f'{varname}inv{num}WOLabel'] = Label(custid, text='⬜') #intial Setup of WO Placeholder. 
            globals()[f'{varname}inv{num}WOLabel'].grid(row= row_offset, column= (ro*3)+1+column_offset)

            if name != "Conetoe":
                globals()[f'{varname}invup{num}cbval'] = IntVar()
                all_CBs.append(globals()[f'{varname}invup{num}cbval'])
                globals()[f'{varname}invup{num}cb'] = Checkbutton(custid, variable=globals()[f'{varname}invup{num}cbval'], cursor='hand2')
                globals()[f'{varname}invup{num}cb'].grid(row= row_offset, column= (ro*3)+2+column_offset, sticky=W)
            else:
                if num < 5:
                    globals()[f'{varname}invup{num}cbval'] = IntVar()
                    all_CBs.append(globals()[f'{varname}invup{num}cbval'])
                    globals()[f'{varname}invup{num}cb'] = Checkbutton(custid, variable=globals()[f'{varname}invup{num}cbval'], cursor='hand2')
                    globals()[f'{varname}invup{num}cb'].grid(row= (4*row_offset-3), rowspan= 4, column= (ro*3)+2+column_offset, sticky=W)


##########
##########
##########
##########
##########
#TEMPORARY CHECKS TO BE REMOVED WHEN DEVICE IS REPIARED
# check if False then call function to implement
conetoe_check = False
def conetoe_offline():
    global conetoe_check
    try:
        if int(hardingPOAcb.cget("text")) >= 400 and datetime.now().hour >= 9:
            msg= "Call Conetoe Utilities:\nWO 29980, 35307\n757-857-2888\nID: 710R41"
            if not textOnly.get():
                messagebox.showinfo(title="Comm Outage", parent=alertW, message=msg)
            else:
                text_update_Table.append("<br>" + str(msg))
            conetoe_check = True
    except ValueError:
        print("POA Value is not a valid Integer")


##########
##########
##########
##########
##########
##########
def connect_Logbook():
    global cur, lbconnection

    lbconn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=G:\Shared drives\Narenco Projects\O&M Projects\NCC\NCC\NCC 039.accdb;'
    lbconnection = pyodbc.connect(lbconn_str)
    cur = lbconnection.cursor()


def connect_db():
    # Create a connection to the Access database
    globals()['dbconn_str'] = (
                r'DRIVER={ODBC Driver 18 for SQL Server};'
                r'SERVER=localhost\SQLEXPRESS01;'
                r'DATABASE=NARENCO_O&M_AE;'
                r'Trusted_Connection=yes;'
                r'Encrypt=no;'
            )
    globals()['dbconnection'] = pyodbc.connect(dbconn_str)
    globals()['c'] = dbconnection.cursor()

def launch_check():
    tday = datetime.now()
    format_date = tday.strftime('%m/%d/%Y')
    query = """
    SELECT TOP 16 [Timestamp] FROM [Whitetail Meter Data]
    WHERE FORMAT([Timestamp], 'MM/DD/YYYY') = ?
    """
    c.execute(query, (format_date,))
    data = c.fetchall()
    if len(data) == 16:
        #ic(data)
        return True
    else:
        #ic(data)
        return False
    

def last_online(site, inv_num, duplin_except):
    query = f"""
    SELECT TOP 1 [Timestamp] 
    FROM [{site}{duplin_except} INV {inv_num} Data]
    WHERE [Watts] > 2
    ORDER BY [Timestamp] DESC
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
    SELECT TOP 1 [Timestamp] 
    FROM [{site} Meter Data]
    WHERE [Watts] > 2
    ORDER BY [Timestamp] DESC
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
        SELECT TOP 1 [Timestamp] 
        FROM [{site} Breaker Data 1]
        WHERE [Status] = 1
        ORDER BY [Timestamp] DESC
        """
        c.execute(query1)
        data1 = c.fetchone()
        query2 = f"""
        SELECT TOP 1 [Timestamp] 
        FROM [{site} Breaker Data 2]
        WHERE [Status] = 1
        ORDER BY [Timestamp] DESC
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
        SELECT TOP 1 [Timestamp]
        FROM [{site} Meter Data]
        WHERE [Amps A] <> 0 AND [Amps B] <> 0 AND [Amps C] <> 0
        ORDER BY [Timestamp] DESC 
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
        SELECT TOP 1 [Timestamp] 
        FROM [{site} Breaker Data]
        WHERE [Status] = 1
        ORDER BY [Timestamp] DESC
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
    global text_update_Table
    save_cb_state()
    update_data_start = ty.perf_counter()

    now = datetime.now()
    if textOnly.get():
        # Create the email message
        message = MIMEMultipart()
        message["Subject"] = f"GUI Update {now}"
        message["From"] = EMAILS['NCC Desk']
        user = optionTexts.get()
        message["To"] = EMAILS[f'{user}'] 
        password = CREDS['remoteMonitoring']
        sender = EMAILS['NCC Desk']
    
    #How to Capture the Data from the GUI...
    text_update_Table = []
    html_start = """<html><head><div style="color:black; font-size:14pt; font-weight:bold; font-family:sans-serif;">
    GUI Update</div></head><body>"""
    #Initiate HTML Table Title turn these into an actual table so that each notification is a new row. Atleast for now to make sure that everything gets added
    text_update_Table.append(html_start)



    status_all = {}
    #Retireve Current INV status's and store in lists
    for site_info in master_List_Sites:
        name, invdict, metermax, var_name, custid, pvsyst_name = site_info
        inverters = len(invdict)
        l = []
        if name != "CDIA":
            for i in range(1, inverters + 1):
                if i in invdict:  # Check if the key exists in the dictionary
                    inv_val = invdict[i]
                else:
                    inv_val = str(i)
                checkbox_var = globals()[f'{var_name}inv{inv_val}cbval']
                if not checkbox_var.get():
                    config_color = globals()[f'{var_name}inv{inv_val}cb'].cget("bg")
                    l.append(config_color)
                else:
                    l.append("green") #Checked inverters are known offline, this logs them in this check as 'online' but thats ok since this process is not the one used to check if the inverter is online or not. If we don't do this the message box reports the wrong index.
            status_all[f'{var_name}'] = l



    tm_now = datetime.now()
    str_tm_now = tm_now.strftime('%H')
    h_tm_now = int(str_tm_now)

    for site_info in master_List_Sites:
        name, invdict, metermax, var_name, custid, pvsyst_name = site_info
        inverters = len(invdict)
        if name == "Violet":
            time_date_compare = (timecurrent - timedelta(hours=4))
        else:
            time_date_compare = (timecurrent - timedelta(hours=2))

        one_day_ago = (timecurrent - timedelta(days=1))
        allinv_kW = []

        if name != "CDIA":
            metercomms = max(comm_data[f'{name} Meter Data'])[0]



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
        if 800 < poa < 2000:
            poa_color = '#ADD8E6'  # Light Blue
        elif 800 > poa > 650:
            poa_color = '#87CEEB'  # Sky Blue
        elif 650 > poa > 500:
            poa_color = '#1E90FF'  # Dodger Blue
        elif 500 > poa > 350:
            poa_color = '#4682B4'  # Steel Blue
        elif 350 > poa > 200:
            poa_color = '#4169E1'  # Royal Blue
        elif poa == 0:
            poa_color = 'black'
        else: 
            poa_color = 'gray'
        

        if poa_data < time_date_compare:
            poalbl = globals()[f'{var_name}POAcb'].cget('bg')
            if poalbl != 'pink' and poa_noti:
                msg = f"{name} lost comms with POA sensor at {strtime_poa}"
                if not textOnly.get():
                    messagebox.showwarning(parent= alertW, title=f"{name}, POA Comms Error", message=msg)
                else:
                    text_update_Table.append("<br>" + str(msg))
            globals()[f'{var_name}POAcb'].config(bg='pink', text=poa)
        else:
            globals()[f'{var_name}POAcb'].config(bg=poa_color, text=poa)


        master_cb_skips_INV_check = True if globals()[f'{var_name}metercbval'].get() == 0 else False
        #print(name, master_cb_skips_INV_check)


        #Breaker Update
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
                                msg= f"{name} Breaker Tripped Open, Please Investigate! {last_operational}"
                                if not textOnly.get():
                                    messagebox.showerror(parent= alertW, title= f"{name}", message= msg)
                                else:
                                    text_update_Table.append("<br>" + str(msg))
                            breakerstatus = "❌❌"
                            breakerstatuscolor = 'red'
                        globals()[f'{var_name}{two}statusLabel'].config(text= breakerstatus, bg=breakerstatuscolor)
                    else:
                        bklbl = globals()[f'{var_name}{two}statusLabel'].cget('bg')
                        globals()[f'{var_name}{two}statusLabel'].config(bg='pink')
                        if bklbl != 'pink' and master_cb_skips_INV_check:
                            msg= f"Breaker Comms lost {bk_Ltime} with the Breaker at {name}! Please Investigate!"
                            if not textOnly.get():
                                messagebox.showerror(parent= alertW, title=f"{name}, Breaker Comms Loss", message=msg)
                            else:
                                text_update_Table.append("<br>" + str(msg))
            elif name in {'Cardinal', 'Harrison', 'Hayes', 'Warbler', 'Hickory'}:
                if metercomms > time_date_compare:
                    rows_w_zeros = 0
                    for i in range(meter_pulls):
                        if any(meter_data[f'{name} Meter Data'][i][j] == 0 for j in range(3,6)):
                            rows_w_zeros += 1
                    if rows_w_zeros >= 2:
                        breakerconfig = globals()[f'{var_name}statusLabel'].cget("text")
                        if breakerconfig != "❌❌" and master_cb_skips_INV_check:
                            last_operational = last_closed(name)
                            msg= f"{name} Breaker Tripped Open, Please Investigate! {last_operational}"
                            if not textOnly.get():
                                messagebox.showerror(parent= alertW, title= f"{name}", message= msg)
                            else:
                                text_update_Table.append("<br>" + str(msg))
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
                        msg= f"Meter Comms lost {metercomms_time} with the Meter at {name}! Please Investigate!"
                        if not textOnly.get():
                            messagebox.showerror(parent= alertW, title=f"{name}, Meter Comms Loss", message=msg)   
                        else:
                            text_update_Table.append("<br>" + str(msg))
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
                            msg= f"{name} Breaker Tripped Open, Please Investigate! {last_operational}"
                            if not textOnly.get():
                                messagebox.showerror(parent= alertW, title= f"{name}", message= msg)
                            else:
                                text_update_Table.append("<br>" + str(msg))
                        breakerstatus = "❌❌"
                        breakerstatuscolor = 'red'
                    globals()[f'{var_name}statusLabel'].config(text= breakerstatus, bg=breakerstatuscolor)
                else:
                    bklbl = globals()[f'{var_name}statusLabel'].cget('bg')
                    globals()[f'{var_name}statusLabel'].config(bg='pink')
                    if bklbl != 'pink' and master_cb_skips_INV_check:
                        msg= f"Breaker Comms lost {bk_Ltime} with the Breaker at {name}! Please Investigate!"
                        if not textOnly.get():
                            messagebox.showerror(parent= alertW, title=f"{name}, Breaker Comms Loss", message= msg)
                        else:
                            text_update_Table.append("<br>" + str(msg))
        #INVERTER CHECKS            
        if name == "CDIA":
                data = inv_data[f'{name} INV 1 Data']
                current_config = globals()[f'{var_name}meterkWLabel'].cget("bg")
                cbval = globals()[f'{var_name}metercbval'].get()
                duplin_except = ''
                r = 1
                
                #Meter Ratio Check for CDIA
                avg_kW = np.mean([row[1] for row in data])
                meterRatio = avg_kW/metermax
                if meterRatio > .90:
                    ratio_color = '#ADD8E6'  # Light Blue
                elif .90 > meterRatio > .80:
                    ratio_color = '#87CEEB'  # Sky Blue
                elif .80 > meterRatio > .70:
                    ratio_color = '#1E90FF'  # Dodger Blue
                elif .70 > meterRatio > .60:
                    ratio_color = '#4682B4'  # Steel Blue
                elif .60 > meterRatio > .50:
                    ratio_color = '#4169E1'  # Royal Blue
                elif meterRatio < 0.001:
                    ratio_color = 'black'
                else: 
                    ratio_color = 'gray'
                globals()[f'{var_name}meterRatioLabel'].config(text= f"{round(meterRatio*100, 1)}%", bg= ratio_color)

                avg_dcv = np.mean([row[0] for row in data])
                inv_comm = max(comm_data[f'{name} INV 1 Data'])[0]
                
                inv_Ltime = inv_comm.strftime('%m/%d/%y | %H:%M')
                if inv_comm > time_date_compare:
                    if all(point[1] <= 1 for point in data):
                        if avg_dcv > 100:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 100)) and cbval == 0 and master_cb_skips_INV_check:
                                var_key = f'{var_name}statusLabel'
                                if var_key in globals():
                                    if globals()[var_key].cget("bg") == 'green':
                                        online_last = last_online(name, r, duplin_except)
                                        msg= f"{name} | Inverter Offline, Good DC Voltage | {online_last}"
                                        if not textOnly.get():
                                            messagebox.showwarning(title=f"{name}", parent= alertW, message= msg)
                                        else:
                                            text_update_Table.append("<br>" + str(msg))
                                else:
                                    online_last = last_online(name, r, duplin_except)
                                    msg= f"{name} | Inverter Offline, Good DC Voltage | {online_last}"
                                    if not textOnly.get():
                                        messagebox.showwarning(title=f"{name}", parent= alertW, message= msg)
                                    else:
                                        text_update_Table.append("<br>" + str(msg))

                            globals()[f'{var_name}meterkWLabel'].config(text="X✓", bg='orange')
                            globals()[f'{var_name}Label'].config(bg='orange')

                        else:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 100)) and cbval == 0 and master_cb_skips_INV_check:
                                var_key = f'{var_name}statusLabel'
                                if var_key in globals():
                                    if globals()[var_key].cget("bg") == 'green':
                                        online_last = last_online(name, r, duplin_except)
                                        msg= f"{name} | Inverter Offline, Bad DC Voltage | {online_last}"
                                        if not textOnly.get():
                                            messagebox.showwarning(title=f"{name}", parent= alertW, message= msg)
                                        else:
                                            text_update_Table.append("<br>" + str(msg))
                                else:
                                    online_last = last_online(name, r, duplin_except)
                                    msg= f"{name} | Inverter Offline, Bad DC Voltage | {online_last}"
                                    if not textOnly.get():
                                        messagebox.showwarning(title=f"{name}", parent= alertW, message= msg)
                                    else:
                                        text_update_Table.append("<br>" + str(msg))

                            globals()[f'{var_name}meterkWLabel'].config(text="❌❌", bg='red')
                            globals()[f'{var_name}Label'].config(bg='red')

                    else:
                        if check_inv_consecutively_online(point[1] for point in data):
                            globals()[f'{var_name}meterkWLabel'].config(text="✓✓✓", bg='green')
                            globals()[f'{var_name}Label'].config(bg='#ADD8E6')

                else:
                    invlbl = globals()[f'{var_name}meterkWLabel'].cget('bg')
                    globals()[f'{var_name}meterkWLabel'].config(bg='pink')
                    globals()[f'{var_name}meterRatioLabel'].config(bg='pink')

                    if invlbl != 'pink' and cbval == 0 and master_cb_skips_INV_check:
                        var_key = f'{var_name}statusLabel'
                        if var_key in globals():
                            if globals()[var_key].cget("bg") == 'green':
                                msg= f"INV Comms lost {inv_Ltime} with Inverter {r} at {name}! Please Investigate!"
                                if not textOnly.get():
                                    messagebox.showerror(parent= alertW, title=f"{name}, Inverter Comms Loss", message=msg)
                                else:
                                    text_update_Table.append("<br>" + str(msg))
                        else:
                            msg= f"INV Comms lost {inv_Ltime} with Inverter {r} at {name}! Please Investigate!"
                            if not textOnly.get():
                                messagebox.showerror(parent= alertW, title=f"{name}, Inverter Comms Loss", message=msg)
                            else:
                                text_update_Table.append("<br>" + str(msg))
        else:
            for r in range(1, inverters + 1):
                if r in invdict:  # Check if the key exists in the dictionary
                    inv_val = invdict[r]
                else:
                    inv_val = str(r)
                if name == 'Duplin':
                    if r <= 3:
                        duplin_except = ' Central'
                        inv_num = r
                    else:
                        duplin_except = ' String'
                        inv_num = r -3
                else:
                    duplin_except = ''
                    inv_num = r
                data = inv_data[f'{name}{duplin_except} INV {inv_num} Data']
                invmaxkW = max([row[1] for row in data[:meter_pulls]])
                
                current_config = globals()[f'{var_name}inv{inv_val}cb'].cget("bg")
                cbval = globals()[f'{var_name}inv{inv_val}cbval'].get()
                
                avg_dcv = np.mean([row[0] for row in data])
                inv_comm = max(comm_data[f'{name}{duplin_except} INV {inv_num} Data'])[0]

                allinv_kW.append(invmaxkW if inv_comm > time_date_compare else 0)
                inv_Ltime = inv_comm.strftime('%m/%d/%y | %H:%M')
                if inv_comm > time_date_compare:
                    if all(point[1] < 1 for point in data):
                        if avg_dcv > 100:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 100)) and cbval == 0 and master_cb_skips_INV_check:
                                var_key = f'{var_name}statusLabel'
                                if var_key in globals():
                                    if globals()[var_key].cget("bg") == 'green':
                                        online_last = last_online(name, inv_num, duplin_except)
                                        msg= f"{name} | Inverter {inv_val} Offline, Good DC Voltage | {online_last}"
                                        if not textOnly.get():
                                            messagebox.showwarning(title=f"{name}", parent= alertW, message= msg)
                                        else:
                                            text_update_Table.append("<br>" + str(msg))
                                else:
                                    online_last = last_online(name, inv_num, duplin_except)
                                    msg= f"{name} | Inverter {inv_val} Offline, Good DC Voltage | {online_last}"
                                    if not textOnly.get():
                                        messagebox.showwarning(title=f"{name}", parent= alertW, message= msg)
                                    else:
                                        text_update_Table.append("<br>" + str(msg))
                            globals()[f'{var_name}inv{inv_val}cb'].config(bg='orange')
                        else:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 100)) and cbval == 0 and master_cb_skips_INV_check:
                                var_key = f'{var_name}statusLabel'
                                if var_key in globals():
                                    if globals()[var_key].cget("bg") == 'green':
                                        online_last = last_online(name, inv_num, duplin_except)
                                        msg= f"{name} | Inverter {inv_val} Offline, Bad DC Voltage | {online_last}"
                                        if not textOnly.get():
                                            messagebox.showwarning(title=f"{name}", parent= alertW, message= msg)
                                        else:
                                            text_update_Table.append("<br>" + str(msg))                                            
                                else:
                                    online_last = last_online(name, inv_num, duplin_except)
                                    msg= f"{name} | Inverter {inv_val} Offline, Bad DC Voltage | {online_last}"
                                    if not textOnly.get():
                                        messagebox.showwarning(title=f"{name}", parent= alertW, message= msg)
                                    else:
                                        text_update_Table.append("<br>" + str(msg))                                        

                            globals()[f'{var_name}inv{inv_val}cb'].config(bg='red')
                    else:
                        if check_inv_consecutively_online(point[1] for point in data):
                            globals()[f'{var_name}inv{inv_val}cb'].config(bg='green')
                else:
                    globals()[f'{var_name}inv{inv_val}cb'].config(bg='pink')
                    invlbl = globals()[f'{var_name}inv{inv_val}cb'].cget('bg')
                    if invlbl != 'pink' and cbval == 0 and master_cb_skips_INV_check:
                        var_key = f'{var_name}statusLabel'
                        if var_key in globals():
                            if globals()[var_key].cget("bg") == 'green':
                                msg= f"INV Comms lost {inv_Ltime} with Inverter {inv_val} at {name}! Please Investigate!"
                                if not textOnly.get():
                                    messagebox.showerror(parent= alertW, title=f"{name}, Inverter Comms Loss", message=msg)
                                else:
                                    text_update_Table.append("<br>" + str(msg))                                   
                        else:
                            msg= f"INV Comms lost {inv_Ltime} with Inverter {inv_val} at {name}! Please Investigate!"
                            if not textOnly.get():
                                messagebox.showerror(parent= alertW, title=f"{name}, Inverter Comms Loss", message=msg)
                            else:
                                text_update_Table.append("<br>" + str(msg))
        #Meter Check
        if name != "CDIA":
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
                    meterdataVA = max(meterdataVA, row[0]) if meterdataVA is not None else row[0]
                    meterdataVB = max(meterdataVB, row[1]) if meterdataVB is not None else row[1]
                    meterdataVC = max(meterdataVC, row[2]) if meterdataVC is not None else row[2]
                meterdataavgVA = np.mean([row[0] for row in meterdata if row[0] is not None])
                meterdataavgVB = np.mean([row[1] for row in meterdata if row[1] is not None])
                meterdataavgVC = np.mean([row[2] for row in meterdata if row[2] is not None])

                if meterdataavgVA != 0 and meterdataavgVB != 0 and meterdataavgVC !=0:
                    percent_difference_AB = ((max(meterdataavgVA, meterdataavgVB) - min(meterdataavgVA, meterdataavgVB)) / np.mean([meterdataavgVA, meterdataavgVB]))  * 100
                    percent_difference_AC = ((max(meterdataavgVA, meterdataavgVC) - min(meterdataavgVA, meterdataavgVC)) / np.mean([meterdataavgVA, meterdataavgVC]))  * 100
                    percent_difference_BC = ((max(meterdataavgVC, meterdataavgVB) - min(meterdataavgVC, meterdataavgVB)) / np.mean([meterdataavgVC, meterdataavgVB]))  * 100
                    #print(f'{name} | AB: {percent_difference_AB} AC: {percent_difference_AC} BC: {percent_difference_BC}')
                else:
                    percent_difference_AB = 0
                    percent_difference_AC = 0
                    percent_difference_BC = 0

                meterVconfig = globals()[f'{var_name}meterVLabel'].cget("text")

                meterdataavgAA = np.mean([row[3] for row in meterdata if row[3] is not None])
                meterdataavgAB = np.mean([row[4] for row in meterdata if row[4] is not None])
                meterdataavgAC = np.mean([row[5] for row in meterdata if row[5] is not None])
                meterdataAA = all(row[3] < 1 for row in meterdata if row[3] is not None)
                meterdataAB = all(row[4] < 1 for row in meterdata if row[4] is not None)
                meterdataAC = all(row[5] < 1 for row in meterdata if row[5] is not None)
                meterdataKW = np.mean([row[6] for row in meterdata if row[6] is not None])
                if name == "Wellons":
                    meterdatakWM = max(row[6] for row in meterdata if row[6] is not None and row[6] < 760000000) if max(row[6] for row in meterdata if row[6] is not None and row[6] < 760000000) else 0
                else:
                    meterdatakWM = max(row[6] for row in meterdata if row[6] is not None) if max(row[6] for row in meterdata if row[6] is not None) else 0

                
                #print(f'{name} |  A: {meterdataAA}, B: {meterdataAB}, C: {meterdataAC}')
                #Accounting for Sites reporting Votlage differently
                if name == "Hickory":
                    val = 5
                else:
                    val = 5000

                if name in  ["Wellons", "Cherry Blossom"]:
                    dif = 9
                else:
                    dif = 5

                if meterdataVA < val and meterdataVB < val and meterdataVC < val:
                    meterVstatus= '❌❌'
                    meterVstatuscolor= 'red'
                    if meterVconfig != '❌❌':
                        online = meter_last_online(name)
                        msg= f"Loss of Utility Voltage or Lost Comms with Meter. {online}"
                        if not textOnly.get():
                            messagebox.showerror(parent=alertW, title= f"{name} Meter", message= msg)
                        else:
                            text_update_Table.append("<br>" + str(name) + " | " + str(msg))
                elif meterdataVA < val:
                    meterVstatus= 'X✓✓'
                    meterVstatuscolor= 'orange'
                    if meterVconfig != 'X✓✓':
                        msg= f"Loss of Utility Phase A Voltage or Lost Comms with Meter."
                        if not textOnly.get():
                            messagebox.showerror(parent=alertW, title= f"{name} Meter", message= msg)
                        else:
                            text_update_Table.append("<br>" + str(name) + " | " + str(msg))
                elif meterdataVB < val:
                    meterVstatus= '✓X✓'
                    meterVstatuscolor= 'orange'
                    if meterVconfig != '✓X✓':
                        msg= f"Loss of Utility Phase B Voltage or Lost Comms with Meter."
                        if not textOnly.get():
                            messagebox.showerror(parent=alertW, title= f"{name} Meter", message= msg)
                        else:
                            text_update_Table.append("<br>" + str(name) + " | " + str(msg))
                elif meterdataVC < val:
                    meterVstatus= '✓✓X'
                    meterVstatuscolor= 'orange'
                    if meterVconfig != '✓✓X':
                        msg= f"Loss of Utility Phase C Voltage or Lost Comms with Meter."
                        if not textOnly.get():
                            messagebox.showerror(parent=alertW, title= f"{name} Meter", message= msg)
                        else:
                            text_update_Table.append("<br>" + str(name) + " | " + str(msg))
                elif percent_difference_AB >= dif or percent_difference_AC >= dif or percent_difference_BC >= dif:
                    meterVstatus= '???'
                    meterVstatuscolor= 'orange'
                    if meterVconfig != '???':
                        msg= f"Voltage Imbalance greater than {dif}%"
                        if not textOnly.get():
                            messagebox.showerror(parent=alertW, title= f"{name} Meter", message= msg)
                        else:
                            text_update_Table.append("<br>" + str(name) + " | " + str(msg))
                else:
                    meterVstatus= '✓✓✓'
                    meterVstatuscolor= 'green'
                    if meterVconfig not in  ['✓✓✓', 'V']:
                        msg= "Utility Voltage Restored!!! Close the Breaker"
                        if not textOnly.get():
                            messagebox.showinfo(parent=alertW, title=f"{name} Meter", message= msg)
                        else:
                            text_update_Table.append("<br>" + str(name) + " | " + str(msg))

                globals()[f'{var_name}meterVLabel'].config(text= meterVstatus, bg= meterVstatuscolor)

                total_invkW = sum(allinv_kW)
                #Here is where I would check for meterRatio and set the text of the meterRatiolabel
                meterRatio = meterdatakWM/metermax
                if meterRatio > .90:
                    ratio_color = '#ADD8E6'  # Light Blue
                elif .90 > meterRatio > .80:
                    ratio_color = '#87CEEB'  # Sky Blue
                elif .80 > meterRatio > .70:
                    ratio_color = '#1E90FF'  # Dodger Blue
                elif .70 > meterRatio > .60:
                    ratio_color = '#4682B4'  # Steel Blue
                elif .60 > meterRatio > .50:
                    ratio_color = '#4169E1'  # Royal Blue
                elif meterRatio < 0.001:
                    ratio_color = 'black'
                else: 
                    ratio_color = 'gray'
                print(f"{name:<15} | {round(meterRatio*100, 1):<5} | {meterdatakWM:<9} | {metermax}")

                globals()[f'{var_name}meterRatioLabel'].config(text= f"{round(meterRatio*100, 1)}%", bg= ratio_color)


                if (meterdataKW < 2 or meterdataAA or meterdataAB or meterdataAC) and begin:
                    if name != 'Van Buren': # This if statement and elif pair juke around the VanBuren being down a phase. 
                        meterkWstatus= '❌❌'
                        meterkWstatuscolor= 'red'
                        meterlbl = globals()[f'{var_name}meterkWLabel'].cget('bg')
                        if meterlbl != 'red' and master_cb_skips_INV_check and poa > 10:
                            online = meter_last_online(name)
                            msg= f"Site: {name}\nMeter Production: {round(meterdataKW, 2)}\nMeter Amps:\nA: {round(meterdataavgAA, 2)}\nB: {round(meterdataavgAB, 2)}\nC: {round(meterdataavgAC, 2)}\n{online}"
                            if not textOnly.get():
                                messagebox.showerror(parent= alertW, title=f"{name}, Power Loss", message=msg)
                            else:
                                text_update_Table.append("<br>" + str(msg))  
                    elif meterdataAC or meterdataAB or meterdataKW < 2: #This is a continuation of the above 'Juke' The Elif below is yet another continuation as Vanburen gets trapped by the very first if statement
                        meterkWstatus= '❌❌'
                        meterkWstatuscolor= 'red'
                        meterlbl = globals()[f'{var_name}meterkWLabel'].cget('bg')
                        if meterlbl != 'red' and master_cb_skips_INV_check and poa > 10:
                            online = meter_last_online(name)
                            msg= f"Site: {name}\nMeter Production: {round(meterdataKW, 2)}\nMeter Amps:\nA: {round(meterdataavgAA, 2)}\nB: {round(meterdataavgAB, 2)}\nC: {round(meterdataavgAC, 2)}\n{online}"
                            if not textOnly.get():
                                messagebox.showerror(parent= alertW, title=f"{name}, Meter Power Loss", message=msg)
                            else:
                                text_update_Table.append("<br>" + str(msg))
     
                else:
                    meterkWstatus= '✓✓✓'
                    meterkWstatuscolor= 'green'
                #Below we update the GUI with the above defined text and color
                globals()[f'{var_name}meterkWLabel'].config(text= meterkWstatus, bg= meterkWstatuscolor)
                
                #PVSYST Ratio Update
                try:
                    pysyst_connect()
                    if meterdatakWM and poa and pvsyst_name:
                        performance_ratio, degradation, meter_est = pvsyst_est(meterdatakWM, poa, pvsyst_name)
                        if pvsyst_name is not None:
                            print(f'{pvsyst_name:<15} | {round(performance_ratio, 1)}% | {round(degradation*100, 2)}% Loss | {round(meter_est, 2):<13} W or kW?')
                        
                        if performance_ratio != 0:
                            if performance_ratio > 90:
                                pvSyst_color = '#ADD8E6'  # Light Blue
                            elif 90 > performance_ratio > 80:
                                pvSyst_color = '#87CEEB'  # Sky Blue
                            elif 80 > performance_ratio > 70:
                                pvSyst_color = '#1E90FF'  # Dodger Blue
                            elif 70 > performance_ratio > 60:
                                pvSyst_color = '#4682B4'  # Steel Blue
                            elif 60 > performance_ratio > 50:
                                pvSyst_color = '#4169E1'  # Royal Blue
                            else: 
                                pvSyst_color = 'gray'
                            globals()[f'{var_name}meterPvSystLabel'].config(text=f'{round(performance_ratio, 1)}%', bg=pvSyst_color)
                        else:
                            globals()[f'{var_name}meterPvSystLabel'].config(text='N/A')
                    connect_pvsystdb.close()
                except Exception as erro:
                    print("Error: ", erro)
                    pass


            else:
                meterlbl = globals()[f'{var_name}meterkWLabel'].cget('bg')
                if meterlbl != 'pink' and master_cb_skips_INV_check:
                    msg=f"Meter Comms lost {meter_Ltime} with the Meter at {name}! Please Investigate!"
                    if not textOnly.get():
                        messagebox.showerror(parent= alertW, title=f"{name}, Meter Comms Loss", message=msg)
                    else:
                        text_update_Table.append("<br>" + str(msg))
                globals()[f'{var_name}meterkWLabel'].config(bg='pink')
                globals()[f'{var_name}meterVLabel'].config(bg='pink')
                globals()[f'{var_name}meterRatioLabel'].config(bg='pink')


    if underperf_Maincbvar.get() == True:
        underperformance_data_update() #Inverter Comparison Type Underperformance Check
    #conetoe_offline()

    if textOnly.get():
        text_update_Table.append("</body></html>")
        print("Table: ", text_update_Table)
        if text_update_Table != [html_start, "</body></html>"]:
            # Connect to Gmail SMTP server and send email
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender, password)
                msg_list = "".join(text_update_Table)
                soup = BeautifulSoup(msg_list, 'html.parser')
                message.attach(MIMEText(soup.prettify(), 'html'))
                print("\n", text_update_Table)
                print("\n", soup.prettify())
                print("\n",message.as_string())
                print("\n", textOnly.get())
                server.send_message(message)
        else:
            print("No New Updates | Email Passed")


    dbconnection.close()


    def allinv_message_update(num, state):
        with open(f"C:\\Users\\OMOPS\\OneDrive - Narenco\\Documents\\APISiteStat\\Site {num} All INV Msg Stat.txt", "w+") as outfile:
                outfile.write(str(state))

    def allinv_message_check(num):
        global text_update_Table
        try:
            with open(f"C:\\Users\\OMOPS\\OneDrive - Narenco\\Documents\\APISiteStat\\Site {num} All INV Msg Stat.txt", "r+") as rad:
                allinvstat = rad.read()
                return allinvstat
        except Exception as errorr:
            msg = f"Error Reading Site {num} txt file"
            if not textOnly.get():
                messagebox.showerror(parent= alertW, message= errorr, title=msg)
            else:
                text_update_Table += f"<br>{msg} | {errorr}"
            return '1'


    # Post Update Status of Inverters
    poststatus_all = {}
    #Retireve Current INV status's and store in lists

    for site_info in master_List_Sites:
        name, invdict, metermax, var_name, custid, pvsyst_name = site_info
        inverters = len(invdict)
        l = []
        if name != "CDIA":
            for i in range(1, inverters + 1):
                if i in invdict:  # Check if the key exists in the dictionary
                    inv_val = invdict[i]
                else:
                    inv_val = str(i)
                checkbox_var = globals()[f'{var_name}inv{inv_val}cbval']
                if not checkbox_var.get():
                    config_color = globals()[f'{var_name}inv{inv_val}cb'].cget("bg")
                    l.append(config_color)
                else:
                    l.append("green") #Checked inverters are known offline, this logs them in this check as 'online' but thats ok since this process is not the one used to check if the inverter is online or not. If we don't do this the message box reports the wrong index.
            poststatus_all[f'{var_name}'] = l
    #ic(poststatus_all['vanburen'])
    
    for index, site_info in enumerate(master_List_Sites):
        name, invdict, metermax, var_name, custid, pvsyst_name = site_info
        inverters = len(invdict)
        if name != "CDIA":
            master_cb_skips_INV_checks = True if globals()[f'{var_name}metercbval'].get() == 0 else False
            if poststatus_all[f'{var_name}']:
                if master_cb_skips_INV_checks and all(status in ['red', 'orange', 'pink'] for status in poststatus_all[f'{var_name}']):
                    #Reasons we want to ignore all the Inverters showing offline
                    if allinv_message_check(index + 1) == '1':
                        if ((POA_data[f'{name} POA Data'][0] > 250 and begin) or (h_tm_now >= 10 and POA_data[f'{name} POA Data'][0] > 75)):
                            print(f'{name} Past', status_all[f'{var_name}'])
                            msg= f"All Inverters Offline, Please Investigate!"
                            if not textOnly.get():
                                messagebox.showerror(parent= alertW, title= f"{name}", message=msg)
                            else:
                                text_update_Table.append("<br>" + str(name) + " | " + str(msg))
                            stat = 0
                            allinv_message_update(index + 1, stat)
                else:
                    stat = 1
                    if allinv_message_check(index + 1) == "0":
                        print(f'{name} Trigger Error', poststatus_all[f'{var_name}'])
                        allinv_message_update(index + 1, stat)  



    def compare_lists(site, before, after, inverter_dictionary):
        global text_update_Table
        #Comapres 2 lists of sites inverters to see what remains online
        changed_indices = []  # List to store indices of changed items
        
        # First, identify any change from not "✓" to "✓"
        changes_detected = any(before_item != "green" and after_item == "green" for before_item, after_item in zip(before, after))
        
        if changes_detected:
            # If changes detected, then identify all items that remain "not ✓"
            changed_indices = [i for i, item in enumerate(after) if item != "green"]
        
        if changed_indices:
            # Look up the corresponding values in the inverter dictionary
            offline_inverters = [inverter_dictionary.get(i + 1, f"Index {i + 1}") for i in changed_indices]
            late_starts = ', '.join(offline_inverters)
            msg=f"Some Inverters just came Online. Inverters: {late_starts} remain Offline."
            if not textOnly.get():
                messagebox.showinfo(parent=alertW, title=site, message=msg)
            else:
                text_update_Table += f"<br>{site} | {msg}"

    
    
    #Comapres all lists of sites inverters to see what remains online
    for site_info in master_List_Sites:
        name, invdict, metermax, var_name, custid, pvsyst_name = site_info
        inverters = len(invdict)
        if int(globals()[f'{var_name}POAcb'].cget("text")) > 100:
            if name != "CDIA":
                compare_lists(name, status_all[f'{var_name}'], poststatus_all[f'{var_name}'], invdict)

    update_data_finish = ty.perf_counter()
    print("Update Data Time (secs):", round(update_data_finish - update_data_start, 2))
    global gui_update_timer
    target_time = time(8, 30)
    if textOnly.get():
        gui_update_timer = PausableTimer(420, db_to_dict)
        gui_update_timer.start() 
    elif timecurrent.time() < target_time:
        gui_update_timer = PausableTimer(300, db_to_dict)
        gui_update_timer.start()
    else:
        gui_update_timer = PausableTimer(60, db_to_dict)
        gui_update_timer.start()


    sendTexts.config(state=NORMAL)
    underperfdaterng.config(state=NORMAL)
    underperfdaterng2.config(state=NORMAL)

def pysyst_connect():
    global cursor_p, connect_pvsystdb
    #Connect to PV Syst DB for Performance expectations
    pvsyst_db = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=G:\Shared drives\O&M\NCC Automations\Notification System\PVsyst (Josephs Edits).accdb;'
    connect_pvsystdb = pyodbc.connect(pvsyst_db)
    cursor_p = connect_pvsystdb.cursor()

def pvsyst_est(meterval, poa_val, pvsyst_name):
    if pvsyst_name == None:
        return (0,0,0)
    if poa_val == 9999:
        return (0,0,0)



    
    if pvsyst_name not in ["WELLONS", "FREIGHTLINE", "WARBLER", "PG", "HOLLYSWAMP"]:
        meterval = meterval/1000


    query = "SELECT [GlobInc_WHSQM], [EGrid_KWH] FROM [PVsystHourly] WHERE [PlantName] = ?"
    date_query = "SELECT [SimulationDate] FROM [PVsystHourly] WHERE [PlantName] = ?"

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        # Execute the query and read into a DataFrame
        slope_df = pd.read_sql_query(query, connect_pvsystdb, params=[pvsyst_name])
    
    meter = 'EGrid_KWH'
    poa = 'GlobInc_WHSQM'
    # Reshape the data for sklearn
    X = slope_df[poa].values.reshape(-1, 1)
    y = slope_df[meter].values
    
    # Create and fit the model
    model = LinearRegression()
    model.fit(X, y)
    
    # Get the slope (coefficient) and intercept
    slope = model.coef_[0]
    intercept = model.intercept_
    
    meter_est = slope * poa_val + intercept

    cursor_p.execute(date_query, pvsyst_name)
    simulation_date = cursor_p.fetchone()[0]
    
    try:
        difference_in_days = (datetime.now() - simulation_date).days
        difference_in_years = difference_in_days / 365.25  # Using 365.25 to account for leap years
        degradation_percentage = difference_in_years * 0.005
        if pvsyst_name == 'WELLONS':
            print('Wellons p50: ', meter_est, ' | ', degradation_percentage)

        meter_estdegrad = meter_est * (1 - degradation_percentage)
        performance = (meterval/meter_estdegrad)*100 #%
        return (performance, degradation_percentage, meter_est)
    except TypeError as e:
        print(e)
        print("Moving On...")
        return (0,0,0)


    # Need to import pvsyst data then regression calc for estimated production, then divide into our groups based on strings per inv to get inverter level underperformance. 



def underperformance_data_update(): #Inv Comparison Function
    endhour = underperf_hourend.get()
    starthour = underperf_hourlimit.get()
    end_d = underperf_range2.get()
    start_d = underperf_range.get()
    start_date = datetime.strptime(start_d, '%m/%d/%Y')
    end_date = datetime.strptime(end_d, '%m/%d/%Y')
    timecheck = datetime.now()

    underperformance_data = {}
    for table in tables:
        table_name = table.table_name
        if "INV" in table_name:
            c.execute(f"""
            SELECT [Timestamp], [Watts] 
            FROM [{table_name}] 
            WHERE [Timestamp] >= ? 
            AND [Timestamp] <= ?
            AND DATEPART(HOUR, [Timestamp]) >= ? 
            AND DATEPART(HOUR, [Timestamp]) < ?
            ORDER BY [Timestamp]""", (start_date, end_date, starthour, endhour))
            invkw_rows = c.fetchall()
            data_list = [list(row) for row in invkw_rows]
            df = pd.DataFrame(data_list, columns=['Timestamp', 'Watts'])
            underperformance_data[table_name] = df
    


    coentoe_inv1 = []
    coentoe_inv2 = []
    coentoe_inv3 = []
    coentoe_inv4 = []

    for site, invdict, metermax, var, custid, pvsyst_name in master_List_Sites:
        inv_count = len(invdict)
        if site == "CDIA":
            continue
        for i in range(1, inv_count + 1):
            if site == "Duplin":
                if i <= 3:
                    strVcent = 'Central'
                    num = i
                    alt = ''
                else:
                    strVcent = 'String'
                    alt = 's'
                    num = i - 3
                table_name = f'{site} {strVcent} INV {num} Data'
                df = underperformance_data.get(table_name, pd.DataFrame(columns=['Timestamp', 'Watts']))
                df_filtered = df[df['Watts'] >= 1].copy()
                df_filtered['Timestamp'] = pd.to_datetime(df_filtered['Timestamp'])
                df_grouped = df_filtered.groupby('Timestamp').mean().reset_index()
                df_resampled = df_grouped.set_index('Timestamp').resample('5min').ffill()
                df_resampled['kWh'] = df_resampled['Watts'] * (2 / 60) / 1000
                globals()[f'{var}{alt}inv{num}daykw'] = df_resampled['kWh'].sum()
                globals()[f'{var}{alt}inv{num}daykwavg'] = df_resampled['Watts'].mean()
            elif site == "Conetoe":
                table_name = f'{site} INV {i} Data'
                df = underperformance_data.get(table_name, pd.DataFrame(columns=['Timestamp', 'Watts']))
                df_filtered = df[df['Watts'] >= 1].copy()
                df_filtered['Timestamp'] = pd.to_datetime(df_filtered['Timestamp'])
                df_grouped = df_filtered.groupby('Timestamp').mean().reset_index()
                df_resampled = df_grouped.set_index('Timestamp').resample('5min').ffill()
                df_resampled['kWh'] = df_resampled['Watts'] * (2 / 60) / 1000
                daily_kw = df_resampled['kWh'].sum()
                avg_w = df_resampled['Watts'].mean()
                if i < 5:
                    coentoe_inv1.append((avg_w, daily_kw))
                    if i == 4:
                        globals()[f'{var}inv1daykwavg'] = np.mean([item[0] for item in coentoe_inv1])
                        globals()[f'{var}inv1daykw'] = np.mean([item[1] for item in coentoe_inv1])

                elif 4 < i < 9:
                    coentoe_inv2.append((avg_w, daily_kw))
                    if i == 8:
                        globals()[f'{var}inv2daykwavg'] = np.mean([item[0] for item in coentoe_inv2])
                        globals()[f'{var}inv2daykw'] = np.mean([item[1] for item in coentoe_inv2])

                elif 8 < i < 13:
                    coentoe_inv3.append((avg_w, daily_kw))
                    if i == 12:
                        globals()[f'{var}inv3daykwavg'] = np.mean([item[0] for item in coentoe_inv3])
                        globals()[f'{var}inv3daykw'] = np.mean([item[1] for item in coentoe_inv3])

                else:
                    coentoe_inv4.append((avg_w, daily_kw))
                    if i == 16:
                        globals()[f'{var}inv4daykwavg'] = np.mean([item[0] for item in coentoe_inv4])
                        globals()[f'{var}inv4daykw'] = np.mean([item[1] for item in coentoe_inv4])

                
            else:
                table_name = f'{site} INV {i} Data'
                df = underperformance_data.get(table_name, pd.DataFrame(columns=['Timestamp', 'Watts']))
                df_filtered = df[df['Watts'] >= 1].copy()
                df_filtered['Timestamp'] = pd.to_datetime(df_filtered['Timestamp'])
                df_grouped = df_filtered.groupby('Timestamp').mean().reset_index()
                df_resampled = df_grouped.set_index('Timestamp').resample('5min').ffill()
                df_resampled['kWh'] = df_resampled['Watts'] * (2 / 60) / 1000
                globals()[f'{var}inv{i}daykw'] = df_resampled['kWh'].sum()
                globals()[f'{var}inv{i}daykwavg'] = df_resampled['Watts'].mean()


        
    bluebirddaykwList = [(bluebirdinv1daykwavg, bluebirdinv1daykw, bluebirdinvup1cb), (bluebirdinv2daykwavg, bluebirdinv2daykw, bluebirdinvup2cb), (bluebirdinv3daykwavg, bluebirdinv3daykw, bluebirdinvup3cb), (bluebirdinv4daykwavg, bluebirdinv4daykw, bluebirdinvup4cb), (bluebirdinv5daykwavg, bluebirdinv5daykw, bluebirdinvup5cb), (bluebirdinv6daykwavg, bluebirdinv6daykw, bluebirdinvup6cb), (bluebirdinv7daykwavg, bluebirdinv7daykw, bluebirdinvup7cb), (bluebirdinv8daykwavg, bluebirdinv8daykw, bluebirdinvup8cb), (bluebirdinv9daykwavg, bluebirdinv9daykw, bluebirdinvup9cb), (bluebirdinv10daykwavg, bluebirdinv10daykw, bluebirdinvup10cb), (bluebirdinv11daykwavg, bluebirdinv11daykw, bluebirdinvup11cb), (bluebirdinv12daykwavg, bluebirdinv12daykw, bluebirdinvup12cb), (bluebirdinv13daykwavg, bluebirdinv13daykw, bluebirdinvup13cb), (bluebirdinv14daykwavg, bluebirdinv14daykw, bluebirdinvup14cb), (bluebirdinv15daykwavg, bluebirdinv15daykw, bluebirdinvup15cb), (bluebirdinv16daykwavg, bluebirdinv16daykw, bluebirdinvup16cb), (bluebirdinv17daykwavg, bluebirdinv17daykw, bluebirdinvup17cb), (bluebirdinv18daykwavg, bluebirdinv18daykw, bluebirdinvup18cb), (bluebirdinv19daykwavg, bluebirdinv19daykw, bluebirdinvup19cb), (bluebirdinv20daykwavg, bluebirdinv20daykw, bluebirdinvup20cb), (bluebirdinv21daykwavg, bluebirdinv21daykw, bluebirdinvup21cb), (bluebirdinv22daykwavg, bluebirdinv22daykw, bluebirdinvup22cb), (bluebirdinv23daykwavg, bluebirdinv23daykw, bluebirdinvup23cb), (bluebirdinv24daykwavg, bluebirdinv24daykw, bluebirdinvup24cb)]
    cardinal96daykwList = [(cardinalinv1daykwavg, cardinalinv1daykw, cardinalinvup1cb), (cardinalinv2daykwavg, cardinalinv2daykw, cardinalinvup2cb), (cardinalinv3daykwavg, cardinalinv3daykw, cardinalinvup3cb), (cardinalinv4daykwavg, cardinalinv4daykw, cardinalinvup4cb), (cardinalinv5daykwavg, cardinalinv5daykw, cardinalinvup5cb), (cardinalinv6daykwavg, cardinalinv6daykw, cardinalinvup6cb), (cardinalinv7daykwavg, cardinalinv7daykw, cardinalinvup7cb), (cardinalinv22daykwavg, cardinalinv22daykw, cardinalinvup22cb), (cardinalinv23daykwavg, cardinalinv23daykw, cardinalinvup23cb), (cardinalinv24daykwavg, cardinalinv24daykw, cardinalinvup24cb), (cardinalinv25daykwavg, cardinalinv25daykw, cardinalinvup25cb), (cardinalinv26daykwavg, cardinalinv26daykw, cardinalinvup26cb), (cardinalinv27daykwavg, cardinalinv27daykw, cardinalinvup27cb), (cardinalinv28daykwavg, cardinalinv28daykw, cardinalinvup28cb), (cardinalinv43daykwavg, cardinalinv43daykw, cardinalinvup43cb), (cardinalinv44daykwavg, cardinalinv44daykw, cardinalinvup44cb), (cardinalinv45daykwavg, cardinalinv45daykw, cardinalinvup45cb), (cardinalinv46daykwavg, cardinalinv46daykw, cardinalinvup46cb), (cardinalinv47daykwavg, cardinalinv47daykw, cardinalinvup47cb)]
    cardinal952daykwList = [(cardinalinv8daykwavg, cardinalinv8daykw, cardinalinvup8cb), (cardinalinv9daykwavg, cardinalinv9daykw, cardinalinvup9cb), (cardinalinv10daykwavg, cardinalinv10daykw, cardinalinvup10cb), (cardinalinv11daykwavg, cardinalinv11daykw, cardinalinvup11cb), (cardinalinv12daykwavg, cardinalinv12daykw, cardinalinvup12cb), (cardinalinv13daykwavg, cardinalinv13daykw, cardinalinvup13cb), (cardinalinv14daykwavg, cardinalinv14daykw, cardinalinvup14cb), (cardinalinv29daykwavg, cardinalinv29daykw, cardinalinvup29cb), (cardinalinv30daykwavg, cardinalinv30daykw, cardinalinvup30cb), (cardinalinv31daykwavg, cardinalinv31daykw, cardinalinvup31cb), (cardinalinv32daykwavg, cardinalinv32daykw, cardinalinvup32cb), (cardinalinv33daykwavg, cardinalinv33daykw, cardinalinvup33cb), (cardinalinv34daykwavg, cardinalinv34daykw, cardinalinvup34cb), (cardinalinv35daykwavg, cardinalinv35daykw, cardinalinvup35cb), (cardinalinv48daykwavg, cardinalinv48daykw, cardinalinvup48cb), (cardinalinv49daykwavg, cardinalinv49daykw, cardinalinvup49cb), (cardinalinv50daykwavg, cardinalinv50daykw, cardinalinvup50cb), (cardinalinv51daykwavg, cardinalinv51daykw, cardinalinvup51cb), (cardinalinv52daykwavg, cardinalinv52daykw, cardinalinvup52cb), (cardinalinv53daykwavg, cardinalinv53daykw, cardinalinvup53cb)]
    cardinal944daykwList = [(cardinalinv15daykwavg, cardinalinv15daykw, cardinalinvup15cb), (cardinalinv16daykwavg, cardinalinv16daykw, cardinalinvup16cb), (cardinalinv17daykwavg, cardinalinv17daykw, cardinalinvup17cb), (cardinalinv18daykwavg, cardinalinv18daykw, cardinalinvup18cb), (cardinalinv19daykwavg, cardinalinv19daykw, cardinalinvup19cb), (cardinalinv20daykwavg, cardinalinv20daykw, cardinalinvup20cb), (cardinalinv21daykwavg, cardinalinv21daykw, cardinalinvup21cb), (cardinalinv36daykwavg, cardinalinv36daykw, cardinalinvup36cb), (cardinalinv37daykwavg, cardinalinv37daykw, cardinalinvup37cb), (cardinalinv38daykwavg, cardinalinv38daykw, cardinalinvup38cb), (cardinalinv39daykwavg, cardinalinv39daykw, cardinalinvup39cb), (cardinalinv40daykwavg, cardinalinv40daykw, cardinalinvup40cb), (cardinalinv41daykwavg, cardinalinv41daykw, cardinalinvup41cb), (cardinalinv42daykwavg, cardinalinv42daykw, cardinalinvup42cb), (cardinalinv54daykwavg, cardinalinv54daykw, cardinalinvup54cb), (cardinalinv55daykwavg, cardinalinv55daykw, cardinalinvup55cb), (cardinalinv56daykwavg, cardinalinv56daykw, cardinalinvup56cb), (cardinalinv57daykwavg, cardinalinv57daykw, cardinalinvup57cb), (cardinalinv58daykwavg, cardinalinv58daykw, cardinalinvup58cb), (cardinalinv59daykwavg, cardinalinv59daykw, cardinalinvup59cb)]
    cherryblossomdaykwList = [(cherryblossominv1daykwavg, cherryblossominv1daykw, cherryblossominvup1cb), (cherryblossominv2daykwavg, cherryblossominv2daykw, cherryblossominvup2cb), (cherryblossominv3daykwavg, cherryblossominv3daykw, cherryblossominvup3cb), (cherryblossominv4daykwavg, cherryblossominv4daykw, cherryblossominvup4cb)]
    harrisondaykwList = [(harrisoninv2daykwavg, harrisoninv2daykw, harrisoninvup2cb), (harrisoninv3daykwavg, harrisoninv3daykw, harrisoninvup3cb), (harrisoninv4daykwavg, harrisoninv4daykw, harrisoninvup4cb), (harrisoninv5daykwavg, harrisoninv5daykw, harrisoninvup5cb), (harrisoninv6daykwavg, harrisoninv6daykw, harrisoninvup6cb), (harrisoninv7daykwavg, harrisoninv7daykw, harrisoninvup7cb), (harrisoninv9daykwavg, harrisoninv9daykw, harrisoninvup9cb), (harrisoninv11daykwavg, harrisoninv11daykw, harrisoninvup11cb), (harrisoninv12daykwavg, harrisoninv12daykw, harrisoninvup12cb), (harrisoninv13daykwavg, harrisoninv13daykw, harrisoninvup13cb), (harrisoninv14daykwavg, harrisoninv14daykw, harrisoninvup14cb), (harrisoninv15daykwavg, harrisoninv15daykw, harrisoninvup15cb), (harrisoninv16daykwavg, harrisoninv16daykw, harrisoninvup16cb), (harrisoninv18daykwavg, harrisoninv18daykw, harrisoninvup18cb), (harrisoninv19daykwavg, harrisoninv19daykw, harrisoninvup19cb), (harrisoninv20daykwavg, harrisoninv20daykw, harrisoninvup20cb), (harrisoninv22daykwavg, harrisoninv22daykw, harrisoninvup22cb), (harrisoninv23daykwavg, harrisoninv23daykw, harrisoninvup23cb), (harrisoninv24daykwavg, harrisoninv24daykw, harrisoninvup24cb), (harrisoninv25daykwavg, harrisoninv25daykw, harrisoninvup25cb), (harrisoninv26daykwavg, harrisoninv26daykw, harrisoninvup26cb), (harrisoninv27daykwavg, harrisoninv27daykw, harrisoninvup27cb), (harrisoninv28daykwavg, harrisoninv28daykw, harrisoninvup28cb), (harrisoninv31daykwavg, harrisoninv31daykw, harrisoninvup31cb), (harrisoninv32daykwavg, harrisoninv32daykw, harrisoninvup32cb), (harrisoninv33daykwavg, harrisoninv33daykw, harrisoninvup33cb), (harrisoninv34daykwavg, harrisoninv34daykw, harrisoninvup34cb), (harrisoninv35daykwavg, harrisoninv35daykw, harrisoninvup35cb), (harrisoninv36daykwavg, harrisoninv36daykw, harrisoninvup36cb), (harrisoninv37daykwavg, harrisoninv37daykw, harrisoninvup37cb), (harrisoninv38daykwavg, harrisoninv38daykw, harrisoninvup38cb), (harrisoninv39daykwavg, harrisoninv39daykw, harrisoninvup39cb), (harrisoninv42daykwavg, harrisoninv42daykw, harrisoninvup42cb), (harrisoninv43daykwavg, harrisoninv43daykw, harrisoninvup43cb)]
    harrison92daykwList = [(harrisoninv1daykwavg, harrisoninv1daykw, harrisoninvup1cb), (harrisoninv8daykwavg, harrisoninv8daykw, harrisoninvup8cb), (harrisoninv10daykwavg, harrisoninv10daykw, harrisoninvup10cb), (harrisoninv17daykwavg, harrisoninv17daykw, harrisoninvup17cb), (harrisoninv21daykwavg, harrisoninv21daykw, harrisoninvup21cb), (harrisoninv29daykwavg, harrisoninv29daykw, harrisoninvup29cb), (harrisoninv30daykwavg, harrisoninv30daykw, harrisoninvup30cb), (harrisoninv40daykwavg, harrisoninv40daykw, harrisoninvup40cb), (harrisoninv41daykwavg, harrisoninv41daykw, harrisoninvup41cb)]
    hayesdaykwList = [(hayesinv1daykwavg, hayesinv1daykw, hayesinvup1cb), (hayesinv2daykwavg, hayesinv2daykw, hayesinvup2cb), (hayesinv3daykwavg, hayesinv3daykw, hayesinvup3cb), (hayesinv4daykwavg, hayesinv4daykw, hayesinvup4cb), (hayesinv5daykwavg, hayesinv5daykw, hayesinvup5cb), (hayesinv6daykwavg, hayesinv6daykw, hayesinvup6cb), (hayesinv7daykwavg, hayesinv7daykw, hayesinvup7cb), (hayesinv8daykwavg, hayesinv8daykw, hayesinvup8cb), (hayesinv9daykwavg, hayesinv9daykw, hayesinvup9cb), (hayesinv10daykwavg, hayesinv10daykw, hayesinvup10cb), (hayesinv11daykwavg, hayesinv11daykw, hayesinvup11cb), (hayesinv12daykwavg, hayesinv12daykw, hayesinvup12cb), (hayesinv13daykwavg, hayesinv13daykw, hayesinvup13cb), (hayesinv14daykwavg, hayesinv14daykw, hayesinvup14cb), (hayesinv15daykwavg, hayesinv15daykw, hayesinvup15cb), (hayesinv16daykwavg, hayesinv16daykw, hayesinvup16cb), (hayesinv17daykwavg, hayesinv17daykw, hayesinvup17cb), (hayesinv19daykwavg, hayesinv19daykw, hayesinvup19cb), (hayesinv20daykwavg, hayesinv20daykw, hayesinvup20cb), (hayesinv21daykwavg, hayesinv21daykw, hayesinvup21cb), (hayesinv23daykwavg, hayesinv23daykw, hayesinvup23cb), (hayesinv24daykwavg, hayesinv24daykw, hayesinvup24cb), (hayesinv25daykwavg, hayesinv25daykw, hayesinvup25cb), (hayesinv26daykwavg, hayesinv26daykw, hayesinvup26cb)]
    hayes96daykwList = [(hayesinv22daykwavg, hayesinv22daykw, hayesinvup22cb), (hayesinv18daykwavg, hayesinv18daykw, hayesinvup18cb)]
    hickorydaykwList = [(hickoryinv1daykwavg, hickoryinv1daykw, hickoryinvup1cb), (hickoryinv2daykwavg, hickoryinv2daykw, hickoryinvup2cb)]
    vanburendaykwList = [(vanbureninv7daykwavg, vanbureninv7daykw, vanbureninvup7cb), (vanbureninv8daykwavg, vanbureninv8daykw, vanbureninvup8cb), (vanbureninv9daykwavg, vanbureninv9daykw, vanbureninvup9cb), (vanbureninv10daykwavg, vanbureninv10daykw, vanbureninvup10cb), (vanbureninv11daykwavg, vanbureninv11daykw, vanbureninvup11cb), (vanbureninv12daykwavg, vanbureninv12daykw, vanbureninvup12cb), (vanbureninv13daykwavg, vanbureninv13daykw, vanbureninvup13cb), (vanbureninv14daykwavg, vanbureninv14daykw, vanbureninvup14cb), (vanbureninv15daykwavg, vanbureninv15daykw, vanbureninvup15cb), (vanbureninv16daykwavg, vanbureninv16daykw, vanbureninvup16cb), (vanbureninv17daykwavg, vanbureninv17daykw, vanbureninvup17cb)]
    vanburen93daykwList = [(vanbureninv1daykwavg, vanbureninv1daykw, vanbureninvup1cb), (vanbureninv2daykwavg, vanbureninv2daykw, vanbureninvup2cb), (vanbureninv3daykwavg, vanbureninv3daykw, vanbureninvup3cb), (vanbureninv4daykwavg, vanbureninv4daykw, vanbureninvup4cb), (vanbureninv5daykwavg, vanbureninv5daykw, vanbureninvup5cb), (vanbureninv6daykwavg, vanbureninv6daykw, vanbureninvup6cb)]
    violetdaykwList = [(violetinv1daykwavg, violetinv1daykw, violetinvup1cb), (violetinv2daykwavg, violetinv2daykw, violetinvup2cb)]
    wellonsdaykwList = [(wellonsinv1daykwavg, wellonsinv1daykw, wellonsinvup1cb), (wellonsinv2daykwavg, wellonsinv2daykw, wellonsinvup2cb), (wellonsinv3daykwavg, wellonsinv3daykw, wellonsinvup3cb), (wellonsinv4daykwavg, wellonsinv4daykw, wellonsinvup4cb), (wellonsinv5daykwavg, wellonsinv5daykw, wellonsinvup5cb), (wellonsinv6daykwavg, wellonsinv6daykw, wellonsinvup6cb)]
    bishopvilleIIdaykwList = [(bishopvilleIIinv6daykwavg, bishopvilleIIinv6daykw, bishopvilleIIinvup6cb), (bishopvilleIIinv7daykwavg, bishopvilleIIinv7daykw, bishopvilleIIinvup7cb), (bishopvilleIIinv8daykwavg, bishopvilleIIinv8daykw, bishopvilleIIinvup8cb), (bishopvilleIIinv9daykwavg, bishopvilleIIinv9daykw, bishopvilleIIinvup9cb), (bishopvilleIIinv10daykwavg, bishopvilleIIinv10daykw, bishopvilleIIinvup10cb), (bishopvilleIIinv13daykwavg, bishopvilleIIinv13daykw, bishopvilleIIinvup13cb), (bishopvilleIIinv15daykwavg, bishopvilleIIinv15daykw, bishopvilleIIinvup15cb), (bishopvilleIIinv19daykwavg, bishopvilleIIinv19daykw, bishopvilleIIinvup19cb), (bishopvilleIIinv20daykwavg, bishopvilleIIinv20daykw, bishopvilleIIinvup20cb), (bishopvilleIIinv21daykwavg, bishopvilleIIinv21daykw, bishopvilleIIinvup21cb), (bishopvilleIIinv22daykwavg, bishopvilleIIinv22daykw, bishopvilleIIinvup22cb), (bishopvilleIIinv23daykwavg, bishopvilleIIinv23daykw, bishopvilleIIinvup23cb), (bishopvilleIIinv26daykwavg, bishopvilleIIinv26daykw, bishopvilleIIinvup26cb), (bishopvilleIIinv27daykwavg, bishopvilleIIinv27daykw, bishopvilleIIinvup27cb), (bishopvilleIIinv28daykwavg, bishopvilleIIinv28daykw, bishopvilleIIinvup28cb), (bishopvilleIIinv29daykwavg, bishopvilleIIinv29daykw, bishopvilleIIinvup29cb), (bishopvilleIIinv30daykwavg, bishopvilleIIinv30daykw, bishopvilleIIinvup30cb), (bishopvilleIIinv32daykwavg, bishopvilleIIinv32daykw, bishopvilleIIinvup32cb), (bishopvilleIIinv34daykwavg, bishopvilleIIinv34daykw, bishopvilleIIinvup34cb)]
    bishopvilleII34strdaykwList = [(bishopvilleIIinv1daykwavg, bishopvilleIIinv1daykw, bishopvilleIIinvup1cb), (bishopvilleIIinv2daykwavg, bishopvilleIIinv2daykw, bishopvilleIIinvup2cb), (bishopvilleIIinv3daykwavg, bishopvilleIIinv3daykw, bishopvilleIIinvup3cb), (bishopvilleIIinv4daykwavg, bishopvilleIIinv4daykw, bishopvilleIIinvup4cb), (bishopvilleIIinv5daykwavg, bishopvilleIIinv5daykw, bishopvilleIIinvup5cb), (bishopvilleIIinv11daykwavg, bishopvilleIIinv11daykw, bishopvilleIIinvup11cb), (bishopvilleIIinv12daykwavg, bishopvilleIIinv12daykw, bishopvilleIIinvup12cb), (bishopvilleIIinv14daykwavg, bishopvilleIIinv14daykw, bishopvilleIIinvup14cb), (bishopvilleIIinv16daykwavg, bishopvilleIIinv16daykw, bishopvilleIIinvup16cb), (bishopvilleIIinv17daykwavg, bishopvilleIIinv17daykw, bishopvilleIIinvup17cb), (bishopvilleIIinv18daykwavg, bishopvilleIIinv18daykw, bishopvilleIIinvup18cb), (bishopvilleIIinv31daykwavg, bishopvilleIIinv31daykw, bishopvilleIIinvup31cb), (bishopvilleIIinv33daykwavg, bishopvilleIIinv33daykw, bishopvilleIIinvup33cb), (bishopvilleIIinv35daykwavg, bishopvilleIIinv35daykw, bishopvilleIIinvup35cb), (bishopvilleIIinv36daykwavg, bishopvilleIIinv36daykw, bishopvilleIIinvup36cb)]
    bishopvilleII36strdaykwList = [(bishopvilleIIinv24daykwavg, bishopvilleIIinv24daykw, bishopvilleIIinvup24cb), (bishopvilleIIinv25daykwavg, bishopvilleIIinv25daykw, bishopvilleIIinvup25cb)]
    hicksondaykwList = [(hicksoninv7daykwavg, hicksoninv7daykw, hicksoninvup7cb), (hicksoninv8daykwavg, hicksoninv8daykw, hicksoninvup8cb), (hicksoninv9daykwavg, hicksoninv9daykw, hicksoninvup9cb), (hicksoninv12daykwavg, hicksoninv12daykw, hicksoninvup12cb), (hicksoninv13daykwavg, hicksoninv13daykw, hicksoninvup13cb), (hicksoninv14daykwavg, hicksoninv14daykw, hicksoninvup14cb), (hicksoninv15daykwavg, hicksoninv15daykw, hicksoninvup15cb), (hicksoninv16daykwavg, hicksoninv16daykw, hicksoninvup16cb)]
    hickson17strdaykwList = [(hicksoninv1daykwavg, hicksoninv1daykw, hicksoninvup1cb), (hicksoninv2daykwavg, hicksoninv2daykw, hicksoninvup2cb), (hicksoninv3daykwavg, hicksoninv3daykw, hicksoninvup3cb), (hicksoninv4daykwavg, hicksoninv4daykw, hicksoninvup4cb), (hicksoninv5daykwavg, hicksoninv5daykw, hicksoninvup5cb), (hicksoninv6daykwavg, hicksoninv6daykw, hicksoninvup6cb), (hicksoninv10daykwavg, hicksoninv10daykw, hicksoninvup10cb), (hicksoninv11daykwavg, hicksoninv11daykw, hicksoninvup11cb)]
    jeffersondaykwList = [(jeffersoninv5daykwavg, jeffersoninv5daykw, jeffersoninvup5cb), (jeffersoninv7daykwavg, jeffersoninv7daykw, jeffersoninvup7cb), (jeffersoninv8daykwavg, jeffersoninv8daykw, jeffersoninvup8cb), (jeffersoninv9daykwavg, jeffersoninv9daykw, jeffersoninvup9cb), (jeffersoninv10daykwavg, jeffersoninv10daykw, jeffersoninvup10cb), (jeffersoninv11daykwavg, jeffersoninv11daykw, jeffersoninvup11cb), (jeffersoninv12daykwavg, jeffersoninv12daykw, jeffersoninvup12cb), (jeffersoninv15daykwavg, jeffersoninv15daykw, jeffersoninvup15cb), (jeffersoninv16daykwavg, jeffersoninv16daykw, jeffersoninvup16cb), (jeffersoninv19daykwavg, jeffersoninv19daykw, jeffersoninvup19cb), (jeffersoninv24daykwavg, jeffersoninv24daykw, jeffersoninvup24cb), (jeffersoninv26daykwavg, jeffersoninv26daykw, jeffersoninvup26cb), (jeffersoninv27daykwavg, jeffersoninv27daykw, jeffersoninvup27cb), (jeffersoninv28daykwavg, jeffersoninv28daykw, jeffersoninvup28cb), (jeffersoninv29daykwavg, jeffersoninv29daykw, jeffersoninvup29cb), (jeffersoninv30daykwavg, jeffersoninv30daykw, jeffersoninvup30cb), (jeffersoninv31daykwavg, jeffersoninv31daykw, jeffersoninvup31cb), (jeffersoninv32daykwavg, jeffersoninv32daykw, jeffersoninvup32cb), (jeffersoninv33daykwavg, jeffersoninv33daykw, jeffersoninvup33cb), (jeffersoninv34daykwavg, jeffersoninv34daykw, jeffersoninvup34cb), (jeffersoninv35daykwavg, jeffersoninv35daykw, jeffersoninvup35cb), (jeffersoninv36daykwavg, jeffersoninv36daykw, jeffersoninvup36cb), (jeffersoninv37daykwavg, jeffersoninv37daykw, jeffersoninvup37cb), (jeffersoninv38daykwavg, jeffersoninv38daykw, jeffersoninvup38cb), (jeffersoninv39daykwavg, jeffersoninv39daykw, jeffersoninvup39cb), (jeffersoninv48daykwavg, jeffersoninv48daykw, jeffersoninvup48cb), (jeffersoninv57daykwavg, jeffersoninv57daykw, jeffersoninvup57cb), (jeffersoninv58daykwavg, jeffersoninv58daykw, jeffersoninvup58cb), (jeffersoninv59daykwavg, jeffersoninv59daykw, jeffersoninvup59cb), (jeffersoninv60daykwavg, jeffersoninv60daykw, jeffersoninvup60cb), (jeffersoninv61daykwavg, jeffersoninv61daykw, jeffersoninvup61cb), (jeffersoninv62daykwavg, jeffersoninv62daykw, jeffersoninvup62cb), (jeffersoninv63daykwavg, jeffersoninv63daykw, jeffersoninvup63cb), (jeffersoninv64daykwavg, jeffersoninv64daykw, jeffersoninvup64cb)]
    jefferson18strdaykwList = [(jeffersoninv1daykwavg, jeffersoninv1daykw, jeffersoninvup1cb), (jeffersoninv2daykwavg, jeffersoninv2daykw, jeffersoninvup2cb), (jeffersoninv3daykwavg, jeffersoninv3daykw, jeffersoninvup3cb), (jeffersoninv4daykwavg, jeffersoninv4daykw, jeffersoninvup4cb), (jeffersoninv6daykwavg, jeffersoninv6daykw, jeffersoninvup6cb), (jeffersoninv13daykwavg, jeffersoninv13daykw, jeffersoninvup13cb), (jeffersoninv14daykwavg, jeffersoninv14daykw, jeffersoninvup14cb), (jeffersoninv17daykwavg, jeffersoninv17daykw, jeffersoninvup17cb), (jeffersoninv18daykwavg, jeffersoninv18daykw, jeffersoninvup18cb), (jeffersoninv20daykwavg, jeffersoninv20daykw, jeffersoninvup20cb), (jeffersoninv21daykwavg, jeffersoninv21daykw, jeffersoninvup21cb), (jeffersoninv22daykwavg, jeffersoninv22daykw, jeffersoninvup22cb), (jeffersoninv23daykwavg, jeffersoninv23daykw, jeffersoninvup23cb), (jeffersoninv25daykwavg, jeffersoninv25daykw, jeffersoninvup25cb), (jeffersoninv40daykwavg, jeffersoninv40daykw, jeffersoninvup40cb), (jeffersoninv41daykwavg, jeffersoninv41daykw, jeffersoninvup41cb), (jeffersoninv42daykwavg, jeffersoninv42daykw, jeffersoninvup42cb), (jeffersoninv43daykwavg, jeffersoninv43daykw, jeffersoninvup43cb), (jeffersoninv44daykwavg, jeffersoninv44daykw, jeffersoninvup44cb), (jeffersoninv45daykwavg, jeffersoninv45daykw, jeffersoninvup45cb), (jeffersoninv46daykwavg, jeffersoninv46daykw, jeffersoninvup46cb), (jeffersoninv47daykwavg, jeffersoninv47daykw, jeffersoninvup47cb), (jeffersoninv49daykwavg, jeffersoninv49daykw, jeffersoninvup49cb), (jeffersoninv50daykwavg, jeffersoninv50daykw, jeffersoninvup50cb), (jeffersoninv51daykwavg, jeffersoninv51daykw, jeffersoninvup51cb), (jeffersoninv52daykwavg, jeffersoninv52daykw, jeffersoninvup52cb), (jeffersoninv53daykwavg, jeffersoninv53daykw, jeffersoninvup53cb), (jeffersoninv54daykwavg, jeffersoninv54daykw, jeffersoninvup54cb), (jeffersoninv55daykwavg, jeffersoninv55daykw, jeffersoninvup55cb), (jeffersoninv56daykwavg, jeffersoninv56daykw, jeffersoninvup56cb)]
    marshalldaykwList = [(marshallinv1daykwavg, marshallinv1daykw, marshallinvup1cb), (marshallinv2daykwavg, marshallinv2daykw, marshallinvup2cb), (marshallinv3daykwavg, marshallinv3daykw, marshallinvup3cb), (marshallinv4daykwavg, marshallinv4daykw, marshallinvup4cb), (marshallinv5daykwavg, marshallinv5daykw, marshallinvup5cb), (marshallinv6daykwavg, marshallinv6daykw, marshallinvup6cb), (marshallinv7daykwavg, marshallinv7daykw, marshallinvup7cb), (marshallinv8daykwavg, marshallinv8daykw, marshallinvup8cb), (marshallinv9daykwavg, marshallinv9daykw, marshallinvup9cb), (marshallinv10daykwavg, marshallinv10daykw, marshallinvup10cb), (marshallinv11daykwavg, marshallinv11daykw, marshallinvup11cb), (marshallinv12daykwavg, marshallinv12daykw, marshallinvup12cb), (marshallinv13daykwavg, marshallinv13daykw, marshallinvup13cb), (marshallinv14daykwavg, marshallinv14daykw, marshallinvup14cb), (marshallinv15daykwavg, marshallinv15daykw, marshallinvup15cb), (marshallinv16daykwavg, marshallinv16daykw, marshallinvup16cb)]
    ogburndaykwList = [(ogburninv1daykwavg, ogburninv1daykw, ogburninvup1cb), (ogburninv2daykwavg, ogburninv2daykw, ogburninvup2cb), (ogburninv3daykwavg, ogburninv3daykw, ogburninvup3cb), (ogburninv4daykwavg, ogburninv4daykw, ogburninvup4cb), (ogburninv5daykwavg, ogburninv5daykw, ogburninvup5cb), (ogburninv6daykwavg, ogburninv6daykw, ogburninvup6cb), (ogburninv7daykwavg, ogburninv7daykw, ogburninvup7cb), (ogburninv8daykwavg, ogburninv8daykw, ogburninvup8cb), (ogburninv9daykwavg, ogburninv9daykw, ogburninvup9cb), (ogburninv10daykwavg, ogburninv10daykw, ogburninvup10cb), (ogburninv11daykwavg, ogburninv11daykw, ogburninvup11cb), (ogburninv12daykwavg, ogburninv12daykw, ogburninvup12cb), (ogburninv13daykwavg, ogburninv13daykw, ogburninvup13cb), (ogburninv14daykwavg, ogburninv14daykw, ogburninvup14cb), (ogburninv15daykwavg, ogburninv15daykw, ogburninvup15cb), (ogburninv16daykwavg, ogburninv16daykw, ogburninvup16cb)]
    tedderdaykwList = [(tedderinv5daykwavg, tedderinv5daykw, tedderinvup5cb), (tedderinv6daykwavg, tedderinv6daykw, tedderinvup6cb), (tedderinv7daykwavg, tedderinv7daykw, tedderinvup7cb), (tedderinv9daykwavg, tedderinv9daykw, tedderinvup9cb), (tedderinv10daykwavg, tedderinv10daykw, tedderinvup10cb), (tedderinv11daykwavg, tedderinv11daykw, tedderinvup11cb), (tedderinv12daykwavg, tedderinv12daykw, tedderinvup12cb), (tedderinv13daykwavg, tedderinv13daykw, tedderinvup13cb), (tedderinv14daykwavg, tedderinv14daykw, tedderinvup14cb)]
    tedder15strdaykwList = [(tedderinv1daykwavg, tedderinv1daykw, tedderinvup1cb), (tedderinv2daykwavg, tedderinv2daykw, tedderinvup2cb), (tedderinv3daykwavg, tedderinv3daykw, tedderinvup3cb), (tedderinv4daykwavg, tedderinv4daykw, tedderinvup4cb), (tedderinv8daykwavg, tedderinv8daykw, tedderinvup8cb), (tedderinv15daykwavg, tedderinv15daykw, tedderinvup15cb), (tedderinv16daykwavg, tedderinv16daykw, tedderinvup16cb)]
    thunderheaddaykwList = [(thunderheadinv1daykwavg, thunderheadinv1daykw, thunderheadinvup1cb), (thunderheadinv2daykwavg, thunderheadinv2daykw, thunderheadinvup2cb), (thunderheadinv3daykwavg, thunderheadinv3daykw, thunderheadinvup3cb), (thunderheadinv4daykwavg, thunderheadinv4daykw, thunderheadinvup4cb), (thunderheadinv5daykwavg, thunderheadinv5daykw, thunderheadinvup5cb), (thunderheadinv6daykwavg, thunderheadinv6daykw, thunderheadinvup6cb), (thunderheadinv7daykwavg, thunderheadinv7daykw, thunderheadinvup7cb), (thunderheadinv8daykwavg, thunderheadinv8daykw, thunderheadinvup8cb), (thunderheadinv9daykwavg, thunderheadinv9daykw, thunderheadinvup9cb), (thunderheadinv10daykwavg, thunderheadinv10daykw, thunderheadinvup10cb), (thunderheadinv11daykwavg, thunderheadinv11daykw, thunderheadinvup11cb), (thunderheadinv12daykwavg, thunderheadinv12daykw, thunderheadinvup12cb), (thunderheadinv14daykwavg, thunderheadinv14daykw, thunderheadinvup14cb), (thunderheadinv16daykwavg, thunderheadinv16daykw, thunderheadinvup16cb)]
    thunderhead14strdaykwList = [(thunderheadinv15daykwavg, thunderheadinv15daykw, thunderheadinvup15cb), (thunderheadinv13daykwavg, thunderheadinv13daykw, thunderheadinvup13cb)]
    bulloch1adaykwList = [(bulloch1ainv7daykwavg, bulloch1ainv7daykw, bulloch1ainvup7cb), (bulloch1ainv8daykwavg, bulloch1ainv8daykw, bulloch1ainvup8cb), (bulloch1ainv9daykwavg, bulloch1ainv9daykw, bulloch1ainvup9cb), (bulloch1ainv10daykwavg, bulloch1ainv10daykw, bulloch1ainvup10cb), (bulloch1ainv11daykwavg, bulloch1ainv11daykw, bulloch1ainvup11cb), (bulloch1ainv12daykwavg, bulloch1ainv12daykw, bulloch1ainvup12cb), (bulloch1ainv13daykwavg, bulloch1ainv13daykw, bulloch1ainvup13cb), (bulloch1ainv14daykwavg, bulloch1ainv14daykw, bulloch1ainvup14cb), (bulloch1ainv15daykwavg, bulloch1ainv15daykw, bulloch1ainvup15cb), (bulloch1ainv16daykwavg, bulloch1ainv16daykw, bulloch1ainvup16cb), (bulloch1ainv17daykwavg, bulloch1ainv17daykw, bulloch1ainvup17cb), (bulloch1ainv18daykwavg, bulloch1ainv18daykw, bulloch1ainvup18cb), (bulloch1ainv19daykwavg, bulloch1ainv19daykw, bulloch1ainvup19cb), (bulloch1ainv20daykwavg, bulloch1ainv20daykw, bulloch1ainvup20cb), (bulloch1ainv21daykwavg, bulloch1ainv21daykw, bulloch1ainvup21cb), (bulloch1ainv22daykwavg, bulloch1ainv22daykw, bulloch1ainvup22cb), (bulloch1ainv23daykwavg, bulloch1ainv23daykw, bulloch1ainvup23cb), (bulloch1ainv24daykwavg, bulloch1ainv24daykw, bulloch1ainvup24cb)]
    bulloch1a10strdaykwList = [(bulloch1ainv1daykwavg, bulloch1ainv1daykw, bulloch1ainvup1cb), (bulloch1ainv2daykwavg, bulloch1ainv2daykw, bulloch1ainvup2cb), (bulloch1ainv3daykwavg, bulloch1ainv3daykw, bulloch1ainvup3cb), (bulloch1ainv4daykwavg, bulloch1ainv4daykw, bulloch1ainvup4cb), (bulloch1ainv5daykwavg, bulloch1ainv5daykw, bulloch1ainvup5cb), (bulloch1ainv6daykwavg, bulloch1ainv6daykw, bulloch1ainvup6cb)]
    bulloch1bdaykwList = [(bulloch1binv2daykwavg, bulloch1binv2daykw, bulloch1binvup2cb), (bulloch1binv3daykwavg, bulloch1binv3daykw, bulloch1binvup3cb), (bulloch1binv4daykwavg, bulloch1binv4daykw, bulloch1binvup4cb), (bulloch1binv5daykwavg, bulloch1binv5daykw, bulloch1binvup5cb), (bulloch1binv6daykwavg, bulloch1binv6daykw, bulloch1binvup6cb), (bulloch1binv7daykwavg, bulloch1binv7daykw, bulloch1binvup7cb), (bulloch1binv8daykwavg, bulloch1binv8daykw, bulloch1binvup8cb), (bulloch1binv13daykwavg, bulloch1binv13daykw, bulloch1binvup13cb), (bulloch1binv14daykwavg, bulloch1binv14daykw, bulloch1binvup14cb), (bulloch1binv15daykwavg, bulloch1binv15daykw, bulloch1binvup15cb), (bulloch1binv16daykwavg, bulloch1binv16daykw, bulloch1binvup16cb), (bulloch1binv18daykwavg, bulloch1binv18daykw, bulloch1binvup18cb), (bulloch1binv19daykwavg, bulloch1binv19daykw, bulloch1binvup19cb), (bulloch1binv20daykwavg, bulloch1binv20daykw, bulloch1binvup20cb), (bulloch1binv21daykwavg, bulloch1binv21daykw, bulloch1binvup21cb), (bulloch1binv22daykwavg, bulloch1binv22daykw, bulloch1binvup22cb), (bulloch1binv23daykwavg, bulloch1binv23daykw, bulloch1binvup23cb), (bulloch1binv24daykwavg, bulloch1binv24daykw, bulloch1binvup24cb)]
    bulloch1b10strdaykwList = [(bulloch1binv1daykwavg, bulloch1binv1daykw, bulloch1binvup1cb), (bulloch1binv9daykwavg, bulloch1binv9daykw, bulloch1binvup9cb), (bulloch1binv10daykwavg, bulloch1binv10daykw, bulloch1binvup10cb), (bulloch1binv11daykwavg, bulloch1binv11daykw, bulloch1binvup11cb), (bulloch1binv12daykwavg, bulloch1binv12daykw, bulloch1binvup12cb), (bulloch1binv17daykwavg, bulloch1binv17daykw, bulloch1binvup17cb)]
    grayfoxdaykwList = [(grayfoxinv1daykwavg, grayfoxinv1daykw, grayfoxinvup1cb), (grayfoxinv2daykwavg, grayfoxinv2daykw, grayfoxinvup2cb), (grayfoxinv3daykwavg, grayfoxinv3daykw, grayfoxinvup3cb), (grayfoxinv4daykwavg, grayfoxinv4daykw, grayfoxinvup4cb), (grayfoxinv5daykwavg, grayfoxinv5daykw, grayfoxinvup5cb), (grayfoxinv6daykwavg, grayfoxinv6daykw, grayfoxinvup6cb), (grayfoxinv7daykwavg, grayfoxinv7daykw, grayfoxinvup7cb), (grayfoxinv8daykwavg, grayfoxinv8daykw, grayfoxinvup8cb), (grayfoxinv9daykwavg, grayfoxinv9daykw, grayfoxinvup9cb), (grayfoxinv10daykwavg, grayfoxinv10daykw, grayfoxinvup10cb), (grayfoxinv11daykwavg, grayfoxinv11daykw, grayfoxinvup11cb), (grayfoxinv12daykwavg, grayfoxinv12daykw, grayfoxinvup12cb), (grayfoxinv13daykwavg, grayfoxinv13daykw, grayfoxinvup13cb), (grayfoxinv14daykwavg, grayfoxinv14daykw, grayfoxinvup14cb), (grayfoxinv15daykwavg, grayfoxinv15daykw, grayfoxinvup15cb), (grayfoxinv16daykwavg, grayfoxinv16daykw, grayfoxinvup16cb), (grayfoxinv17daykwavg, grayfoxinv17daykw, grayfoxinvup17cb), (grayfoxinv18daykwavg, grayfoxinv18daykw, grayfoxinvup18cb), (grayfoxinv19daykwavg, grayfoxinv19daykw, grayfoxinvup19cb), (grayfoxinv20daykwavg, grayfoxinv20daykw, grayfoxinvup20cb), (grayfoxinv21daykwavg, grayfoxinv21daykw, grayfoxinvup21cb), (grayfoxinv22daykwavg, grayfoxinv22daykw, grayfoxinvup22cb), (grayfoxinv23daykwavg, grayfoxinv23daykw, grayfoxinvup23cb), (grayfoxinv24daykwavg, grayfoxinv24daykw, grayfoxinvup24cb), (grayfoxinv25daykwavg, grayfoxinv25daykw, grayfoxinvup25cb), (grayfoxinv26daykwavg, grayfoxinv26daykw, grayfoxinvup26cb), (grayfoxinv27daykwavg, grayfoxinv27daykw, grayfoxinvup27cb), (grayfoxinv28daykwavg, grayfoxinv28daykw, grayfoxinvup28cb), (grayfoxinv29daykwavg, grayfoxinv29daykw, grayfoxinvup29cb), (grayfoxinv30daykwavg, grayfoxinv30daykw, grayfoxinvup30cb), (grayfoxinv31daykwavg, grayfoxinv31daykw, grayfoxinvup31cb), (grayfoxinv32daykwavg, grayfoxinv32daykw, grayfoxinvup32cb), (grayfoxinv33daykwavg, grayfoxinv33daykw, grayfoxinvup33cb), (grayfoxinv34daykwavg, grayfoxinv34daykw, grayfoxinvup34cb), (grayfoxinv35daykwavg, grayfoxinv35daykw, grayfoxinvup35cb), (grayfoxinv36daykwavg, grayfoxinv36daykw, grayfoxinvup36cb), (grayfoxinv37daykwavg, grayfoxinv37daykw, grayfoxinvup37cb), (grayfoxinv38daykwavg, grayfoxinv38daykw, grayfoxinvup38cb), (grayfoxinv39daykwavg, grayfoxinv39daykw, grayfoxinvup39cb), (grayfoxinv40daykwavg, grayfoxinv40daykw, grayfoxinvup40cb)]
    hardingdaykwList = [(hardinginv4daykwavg, hardinginv4daykw, hardinginvup4cb), (hardinginv5daykwavg, hardinginv5daykw, hardinginvup5cb), (hardinginv6daykwavg, hardinginv6daykw, hardinginvup6cb), (hardinginv10daykwavg, hardinginv10daykw, hardinginvup10cb), (hardinginv11daykwavg, hardinginv11daykw, hardinginvup11cb), (hardinginv12daykwavg, hardinginv12daykw, hardinginvup12cb), (hardinginv13daykwavg, hardinginv13daykw, hardinginvup13cb), (hardinginv14daykwavg, hardinginv14daykw, hardinginvup14cb), (hardinginv15daykwavg, hardinginv15daykw, hardinginvup15cb), (hardinginv17daykwavg, hardinginv17daykw, hardinginvup17cb), (hardinginv18daykwavg, hardinginv18daykw, hardinginvup18cb), (hardinginv19daykwavg, hardinginv19daykw, hardinginvup19cb)]
    harding12strdaykwList = [(hardinginv1daykwavg, hardinginv1daykw, hardinginvup1cb), (hardinginv2daykwavg, hardinginv2daykw, hardinginvup2cb), (hardinginv3daykwavg, hardinginv3daykw, hardinginvup3cb), (hardinginv7daykwavg, hardinginv7daykw, hardinginvup7cb), (hardinginv8daykwavg, hardinginv8daykw, hardinginvup8cb), (hardinginv9daykwavg, hardinginv9daykw, hardinginvup9cb), (hardinginv16daykwavg, hardinginv16daykw, hardinginvup16cb), (hardinginv20daykwavg, hardinginv20daykw, hardinginvup20cb), (hardinginv21daykwavg, hardinginv21daykw, hardinginvup21cb), (hardinginv22daykwavg, hardinginv22daykw, hardinginvup22cb), (hardinginv23daykwavg, hardinginv23daykw, hardinginvup23cb), (hardinginv24daykwavg, hardinginv24daykw, hardinginvup24cb)]
    mcleandaykwList = [(mcleaninv2daykwavg, mcleaninv2daykw, mcleaninvup2cb), (mcleaninv3daykwavg, mcleaninv3daykw, mcleaninvup3cb), (mcleaninv4daykwavg, mcleaninv4daykw, mcleaninvup4cb), (mcleaninv5daykwavg, mcleaninv5daykw, mcleaninvup5cb), (mcleaninv6daykwavg, mcleaninv6daykw, mcleaninvup6cb), (mcleaninv7daykwavg, mcleaninv7daykw, mcleaninvup7cb), (mcleaninv8daykwavg, mcleaninv8daykw, mcleaninvup8cb), (mcleaninv9daykwavg, mcleaninv9daykw, mcleaninvup9cb), (mcleaninv10daykwavg, mcleaninv10daykw, mcleaninvup10cb), (mcleaninv11daykwavg, mcleaninv11daykw, mcleaninvup11cb), (mcleaninv12daykwavg, mcleaninv12daykw, mcleaninvup12cb), (mcleaninv13daykwavg, mcleaninv13daykw, mcleaninvup13cb), (mcleaninv14daykwavg, mcleaninv14daykw, mcleaninvup14cb), (mcleaninv15daykwavg, mcleaninv15daykw, mcleaninvup15cb), (mcleaninv16daykwavg, mcleaninv16daykw, mcleaninvup16cb), (mcleaninv18daykwavg, mcleaninv18daykw, mcleaninvup18cb), (mcleaninv20daykwavg, mcleaninv20daykw, mcleaninvup20cb), (mcleaninv22daykwavg, mcleaninv22daykw, mcleaninvup22cb), (mcleaninv24daykwavg, mcleaninv24daykw, mcleaninvup24cb), (mcleaninv25daykwavg, mcleaninv25daykw, mcleaninvup25cb), (mcleaninv26daykwavg, mcleaninv26daykw, mcleaninvup26cb), (mcleaninv30daykwavg, mcleaninv30daykw, mcleaninvup30cb)]
    mclean10strdaykwList = [(mcleaninv1daykwavg, mcleaninv1daykw, mcleaninvup1cb), (mcleaninv17daykwavg, mcleaninv17daykw, mcleaninvup17cb), (mcleaninv19daykwavg, mcleaninv19daykw, mcleaninvup19cb), (mcleaninv21daykwavg, mcleaninv21daykw, mcleaninvup21cb), (mcleaninv23daykwavg, mcleaninv23daykw, mcleaninvup23cb), (mcleaninv27daykwavg, mcleaninv27daykw, mcleaninvup27cb), (mcleaninv28daykwavg, mcleaninv28daykw, mcleaninvup28cb), (mcleaninv29daykwavg, mcleaninv29daykw, mcleaninvup29cb), (mcleaninv31daykwavg, mcleaninv31daykw, mcleaninvup31cb), (mcleaninv32daykwavg, mcleaninv32daykw, mcleaninvup32cb), (mcleaninv33daykwavg, mcleaninv33daykw, mcleaninvup33cb), (mcleaninv34daykwavg, mcleaninv34daykw, mcleaninvup34cb), (mcleaninv35daykwavg, mcleaninv35daykw, mcleaninvup35cb), (mcleaninv36daykwavg, mcleaninv36daykw, mcleaninvup36cb), (mcleaninv37daykwavg, mcleaninv37daykw, mcleaninvup37cb), (mcleaninv38daykwavg, mcleaninv38daykw, mcleaninvup38cb), (mcleaninv39daykwavg, mcleaninv39daykw, mcleaninvup39cb), (mcleaninv40daykwavg, mcleaninv40daykw, mcleaninvup40cb)]
    richmonddaykwList = [(richmondinv1daykwavg, richmondinv1daykw, richmondinvup1cb), (richmondinv2daykwavg, richmondinv2daykw, richmondinvup2cb), (richmondinv3daykwavg, richmondinv3daykw, richmondinvup3cb), (richmondinv4daykwavg, richmondinv4daykw, richmondinvup4cb), (richmondinv5daykwavg, richmondinv5daykw, richmondinvup5cb), (richmondinv6daykwavg, richmondinv6daykw, richmondinvup6cb), (richmondinv7daykwavg, richmondinv7daykw, richmondinvup7cb), (richmondinv11daykwavg, richmondinv11daykw, richmondinvup11cb), (richmondinv12daykwavg, richmondinv12daykw, richmondinvup12cb), (richmondinv13daykwavg, richmondinv13daykw, richmondinvup13cb), (richmondinv14daykwavg, richmondinv14daykw, richmondinvup14cb), (richmondinv15daykwavg, richmondinv15daykw, richmondinvup15cb), (richmondinv16daykwavg, richmondinv16daykw, richmondinvup16cb), (richmondinv17daykwavg, richmondinv17daykw, richmondinvup17cb), (richmondinv18daykwavg, richmondinv18daykw, richmondinvup18cb), (richmondinv19daykwavg, richmondinv19daykw, richmondinvup19cb), (richmondinv20daykwavg, richmondinv20daykw, richmondinvup20cb), (richmondinv21daykwavg, richmondinv21daykw, richmondinvup21cb)]
    richmond10strdaykwList = [(richmondinv8daykwavg, richmondinv8daykw, richmondinvup8cb), (richmondinv9daykwavg, richmondinv9daykw, richmondinvup9cb), (richmondinv10daykwavg, richmondinv10daykw, richmondinvup10cb), (richmondinv22daykwavg, richmondinv22daykw, richmondinvup22cb), (richmondinv23daykwavg, richmondinv23daykw, richmondinvup23cb), (richmondinv24daykwavg, richmondinv24daykw, richmondinvup24cb)]
    shorthorndaykwList = [(shorthorninv1daykwavg, shorthorninv1daykw, shorthorninvup1cb), (shorthorninv2daykwavg, shorthorninv2daykw, shorthorninvup2cb), (shorthorninv3daykwavg, shorthorninv3daykw, shorthorninvup3cb), (shorthorninv4daykwavg, shorthorninv4daykw, shorthorninvup4cb), (shorthorninv5daykwavg, shorthorninv5daykw, shorthorninvup5cb), (shorthorninv6daykwavg, shorthorninv6daykw, shorthorninvup6cb), (shorthorninv7daykwavg, shorthorninv7daykw, shorthorninvup7cb), (shorthorninv8daykwavg, shorthorninv8daykw, shorthorninvup8cb), (shorthorninv9daykwavg, shorthorninv9daykw, shorthorninvup9cb), (shorthorninv10daykwavg, shorthorninv10daykw, shorthorninvup10cb), (shorthorninv11daykwavg, shorthorninv11daykw, shorthorninvup11cb), (shorthorninv12daykwavg, shorthorninv12daykw, shorthorninvup12cb), (shorthorninv13daykwavg, shorthorninv13daykw, shorthorninvup13cb), (shorthorninv14daykwavg, shorthorninv14daykw, shorthorninvup14cb), (shorthorninv15daykwavg, shorthorninv15daykw, shorthorninvup15cb), (shorthorninv16daykwavg, shorthorninv16daykw, shorthorninvup16cb), (shorthorninv17daykwavg, shorthorninv17daykw, shorthorninvup17cb), (shorthorninv18daykwavg, shorthorninv18daykw, shorthorninvup18cb), (shorthorninv19daykwavg, shorthorninv19daykw, shorthorninvup19cb), (shorthorninv20daykwavg, shorthorninv20daykw, shorthorninvup20cb), (shorthorninv22daykwavg, shorthorninv22daykw, shorthorninvup22cb), (shorthorninv23daykwavg, shorthorninv23daykw, shorthorninvup23cb), (shorthorninv24daykwavg, shorthorninv24daykw, shorthorninvup24cb), (shorthorninv26daykwavg, shorthorninv26daykw, shorthorninvup26cb), (shorthorninv27daykwavg, shorthorninv27daykw, shorthorninvup27cb), (shorthorninv28daykwavg, shorthorninv28daykw, shorthorninvup28cb), (shorthorninv32daykwavg, shorthorninv32daykw, shorthorninvup32cb), (shorthorninv33daykwavg, shorthorninv33daykw, shorthorninvup33cb), (shorthorninv37daykwavg, shorthorninv37daykw, shorthorninvup37cb), (shorthorninv38daykwavg, shorthorninv38daykw, shorthorninvup38cb), (shorthorninv39daykwavg, shorthorninv39daykw, shorthorninvup39cb), (shorthorninv40daykwavg, shorthorninv40daykw, shorthorninvup40cb), (shorthorninv41daykwavg, shorthorninv41daykw, shorthorninvup41cb), (shorthorninv42daykwavg, shorthorninv42daykw, shorthorninvup42cb), (shorthorninv43daykwavg, shorthorninv43daykw, shorthorninvup43cb), (shorthorninv45daykwavg, shorthorninv45daykw, shorthorninvup45cb), (shorthorninv46daykwavg, shorthorninv46daykw, shorthorninvup46cb), (shorthorninv47daykwavg, shorthorninv47daykw, shorthorninvup47cb), (shorthorninv48daykwavg, shorthorninv48daykw, shorthorninvup48cb), (shorthorninv52daykwavg, shorthorninv52daykw, shorthorninvup52cb), (shorthorninv53daykwavg, shorthorninv53daykw, shorthorninvup53cb), (shorthorninv57daykwavg, shorthorninv57daykw, shorthorninvup57cb), (shorthorninv58daykwavg, shorthorninv58daykw, shorthorninvup58cb), (shorthorninv59daykwavg, shorthorninv59daykw, shorthorninvup59cb), (shorthorninv60daykwavg, shorthorninv60daykw, shorthorninvup60cb), (shorthorninv61daykwavg, shorthorninv61daykw, shorthorninvup61cb), (shorthorninv62daykwavg, shorthorninv62daykw, shorthorninvup62cb), (shorthorninv63daykwavg, shorthorninv63daykw, shorthorninvup63cb), (shorthorninv64daykwavg, shorthorninv64daykw, shorthorninvup64cb), (shorthorninv65daykwavg, shorthorninv65daykw, shorthorninvup65cb), (shorthorninv66daykwavg, shorthorninv66daykw, shorthorninvup66cb)]
    shorthorn13strdaykwList = [(shorthorninv21daykwavg, shorthorninv21daykw, shorthorninvup21cb), (shorthorninv25daykwavg, shorthorninv25daykw, shorthorninvup25cb), (shorthorninv29daykwavg, shorthorninv29daykw, shorthorninvup29cb), (shorthorninv30daykwavg, shorthorninv30daykw, shorthorninvup30cb), (shorthorninv31daykwavg, shorthorninv31daykw, shorthorninvup31cb), (shorthorninv34daykwavg, shorthorninv34daykw, shorthorninvup34cb), (shorthorninv35daykwavg, shorthorninv35daykw, shorthorninvup35cb), (shorthorninv36daykwavg, shorthorninv36daykw, shorthorninvup36cb), (shorthorninv44daykwavg, shorthorninv44daykw, shorthorninvup44cb), (shorthorninv49daykwavg, shorthorninv49daykw, shorthorninvup49cb), (shorthorninv50daykwavg, shorthorninv50daykw, shorthorninvup50cb), (shorthorninv51daykwavg, shorthorninv51daykw, shorthorninvup51cb), (shorthorninv54daykwavg, shorthorninv54daykw, shorthorninvup54cb), (shorthorninv55daykwavg, shorthorninv55daykw, shorthorninvup55cb), (shorthorninv56daykwavg, shorthorninv56daykw, shorthorninvup56cb), (shorthorninv67daykwavg, shorthorninv67daykw, shorthorninvup67cb), (shorthorninv68daykwavg, shorthorninv68daykw, shorthorninvup68cb), (shorthorninv69daykwavg, shorthorninv69daykw, shorthorninvup69cb), (shorthorninv70daykwavg, shorthorninv70daykw, shorthorninvup70cb), (shorthorninv71daykwavg, shorthorninv71daykw, shorthorninvup71cb), (shorthorninv72daykwavg, shorthorninv72daykw, shorthorninvup72cb)]
    sunflowerdaykwList = [(sunflowerinv3daykwavg, sunflowerinv3daykw, sunflowerinvup3cb), (sunflowerinv4daykwavg, sunflowerinv4daykw, sunflowerinvup4cb), (sunflowerinv5daykwavg, sunflowerinv5daykw, sunflowerinvup5cb), (sunflowerinv6daykwavg, sunflowerinv6daykw, sunflowerinvup6cb), (sunflowerinv7daykwavg, sunflowerinv7daykw, sunflowerinvup7cb), (sunflowerinv8daykwavg, sunflowerinv8daykw, sunflowerinvup8cb), (sunflowerinv9daykwavg, sunflowerinv9daykw, sunflowerinvup9cb), (sunflowerinv10daykwavg, sunflowerinv10daykw, sunflowerinvup10cb), (sunflowerinv11daykwavg, sunflowerinv11daykw, sunflowerinvup11cb), (sunflowerinv12daykwavg, sunflowerinv12daykw, sunflowerinvup12cb), (sunflowerinv13daykwavg, sunflowerinv13daykw, sunflowerinvup13cb), (sunflowerinv14daykwavg, sunflowerinv14daykw, sunflowerinvup14cb), (sunflowerinv15daykwavg, sunflowerinv15daykw, sunflowerinvup15cb), (sunflowerinv16daykwavg, sunflowerinv16daykw, sunflowerinvup16cb), (sunflowerinv17daykwavg, sunflowerinv17daykw, sunflowerinvup17cb), (sunflowerinv18daykwavg, sunflowerinv18daykw, sunflowerinvup18cb), (sunflowerinv19daykwavg, sunflowerinv19daykw, sunflowerinvup19cb), (sunflowerinv20daykwavg, sunflowerinv20daykw, sunflowerinvup20cb), (sunflowerinv34daykwavg, sunflowerinv34daykw, sunflowerinvup34cb), (sunflowerinv62daykwavg, sunflowerinv62daykw, sunflowerinvup62cb), (sunflowerinv63daykwavg, sunflowerinv63daykw, sunflowerinvup63cb), (sunflowerinv64daykwavg, sunflowerinv64daykw, sunflowerinvup64cb), (sunflowerinv65daykwavg, sunflowerinv65daykw, sunflowerinvup65cb), (sunflowerinv66daykwavg, sunflowerinv66daykw, sunflowerinvup66cb), (sunflowerinv67daykwavg, sunflowerinv67daykw, sunflowerinvup67cb), (sunflowerinv68daykwavg, sunflowerinv68daykw, sunflowerinvup68cb), (sunflowerinv69daykwavg, sunflowerinv69daykw, sunflowerinvup69cb), (sunflowerinv70daykwavg, sunflowerinv70daykw, sunflowerinvup70cb), (sunflowerinv71daykwavg, sunflowerinv71daykw, sunflowerinvup71cb), (sunflowerinv72daykwavg, sunflowerinv72daykw, sunflowerinvup72cb), (sunflowerinv73daykwavg, sunflowerinv73daykw, sunflowerinvup73cb), (sunflowerinv74daykwavg, sunflowerinv74daykw, sunflowerinvup74cb), (sunflowerinv75daykwavg, sunflowerinv75daykw, sunflowerinvup75cb), (sunflowerinv76daykwavg, sunflowerinv76daykw, sunflowerinvup76cb), (sunflowerinv77daykwavg, sunflowerinv77daykw, sunflowerinvup77cb)]
    sunflower12strdaykwList = [(sunflowerinv1daykwavg, sunflowerinv1daykw, sunflowerinvup1cb), (sunflowerinv2daykwavg, sunflowerinv2daykw, sunflowerinvup2cb), (sunflowerinv21daykwavg, sunflowerinv21daykw, sunflowerinvup21cb), (sunflowerinv22daykwavg, sunflowerinv22daykw, sunflowerinvup22cb), (sunflowerinv23daykwavg, sunflowerinv23daykw, sunflowerinvup23cb), (sunflowerinv24daykwavg, sunflowerinv24daykw, sunflowerinvup24cb), (sunflowerinv25daykwavg, sunflowerinv25daykw, sunflowerinvup25cb), (sunflowerinv26daykwavg, sunflowerinv26daykw, sunflowerinvup26cb), (sunflowerinv27daykwavg, sunflowerinv27daykw, sunflowerinvup27cb), (sunflowerinv28daykwavg, sunflowerinv28daykw, sunflowerinvup28cb), (sunflowerinv29daykwavg, sunflowerinv29daykw, sunflowerinvup29cb), (sunflowerinv30daykwavg, sunflowerinv30daykw, sunflowerinvup30cb), (sunflowerinv31daykwavg, sunflowerinv31daykw, sunflowerinvup31cb), (sunflowerinv32daykwavg, sunflowerinv32daykw, sunflowerinvup32cb), (sunflowerinv33daykwavg, sunflowerinv33daykw, sunflowerinvup33cb), (sunflowerinv35daykwavg, sunflowerinv35daykw, sunflowerinvup35cb), (sunflowerinv36daykwavg, sunflowerinv36daykw, sunflowerinvup36cb), (sunflowerinv37daykwavg, sunflowerinv37daykw, sunflowerinvup37cb), (sunflowerinv38daykwavg, sunflowerinv38daykw, sunflowerinvup38cb), (sunflowerinv39daykwavg, sunflowerinv39daykw, sunflowerinvup39cb), (sunflowerinv40daykwavg, sunflowerinv40daykw, sunflowerinvup40cb), (sunflowerinv41daykwavg, sunflowerinv41daykw, sunflowerinvup41cb), (sunflowerinv42daykwavg, sunflowerinv42daykw, sunflowerinvup42cb), (sunflowerinv43daykwavg, sunflowerinv43daykw, sunflowerinvup43cb), (sunflowerinv44daykwavg, sunflowerinv44daykw, sunflowerinvup44cb), (sunflowerinv45daykwavg, sunflowerinv45daykw, sunflowerinvup45cb), (sunflowerinv46daykwavg, sunflowerinv46daykw, sunflowerinvup46cb), (sunflowerinv47daykwavg, sunflowerinv47daykw, sunflowerinvup47cb), (sunflowerinv48daykwavg, sunflowerinv48daykw, sunflowerinvup48cb), (sunflowerinv49daykwavg, sunflowerinv49daykw, sunflowerinvup49cb), (sunflowerinv50daykwavg, sunflowerinv50daykw, sunflowerinvup50cb), (sunflowerinv51daykwavg, sunflowerinv51daykw, sunflowerinvup51cb), (sunflowerinv52daykwavg, sunflowerinv52daykw, sunflowerinvup52cb), (sunflowerinv53daykwavg, sunflowerinv53daykw, sunflowerinvup53cb), (sunflowerinv54daykwavg, sunflowerinv54daykw, sunflowerinvup54cb), (sunflowerinv55daykwavg, sunflowerinv55daykw, sunflowerinvup55cb), (sunflowerinv56daykwavg, sunflowerinv56daykw, sunflowerinvup56cb), (sunflowerinv57daykwavg, sunflowerinv57daykw, sunflowerinvup57cb), (sunflowerinv58daykwavg, sunflowerinv58daykw, sunflowerinvup58cb), (sunflowerinv59daykwavg, sunflowerinv59daykw, sunflowerinvup59cb), (sunflowerinv60daykwavg, sunflowerinv60daykw, sunflowerinvup60cb), (sunflowerinv61daykwavg, sunflowerinv61daykw, sunflowerinvup61cb), (sunflowerinv78daykwavg, sunflowerinv78daykw, sunflowerinvup78cb), (sunflowerinv79daykwavg, sunflowerinv79daykw, sunflowerinvup79cb), (sunflowerinv80daykwavg, sunflowerinv80daykw, sunflowerinvup80cb)]
    upsondaykwList = [(upsoninv1daykwavg, upsoninv1daykw, upsoninvup1cb), (upsoninv2daykwavg, upsoninv2daykw, upsoninvup2cb), (upsoninv3daykwavg, upsoninv3daykw, upsoninvup3cb), (upsoninv4daykwavg, upsoninv4daykw, upsoninvup4cb), (upsoninv5daykwavg, upsoninv5daykw, upsoninvup5cb), (upsoninv9daykwavg, upsoninv9daykw, upsoninvup9cb), (upsoninv10daykwavg, upsoninv10daykw, upsoninvup10cb), (upsoninv11daykwavg, upsoninv11daykw, upsoninvup11cb), (upsoninv12daykwavg, upsoninv12daykw, upsoninvup12cb), (upsoninv13daykwavg, upsoninv13daykw, upsoninvup13cb), (upsoninv14daykwavg, upsoninv14daykw, upsoninvup14cb), (upsoninv15daykwavg, upsoninv15daykw, upsoninvup15cb), (upsoninv16daykwavg, upsoninv16daykw, upsoninvup16cb), (upsoninv17daykwavg, upsoninv17daykw, upsoninvup17cb), (upsoninv21daykwavg, upsoninv21daykw, upsoninvup21cb), (upsoninv22daykwavg, upsoninv22daykw, upsoninvup22cb), (upsoninv23daykwavg, upsoninv23daykw, upsoninvup23cb), (upsoninv24daykwavg, upsoninv24daykw, upsoninvup24cb)]
    upson10strdaykwList = [(upsoninv6daykwavg, upsoninv6daykw, upsoninvup6cb), (upsoninv7daykwavg, upsoninv7daykw, upsoninvup7cb), (upsoninv8daykwavg, upsoninv8daykw, upsoninvup8cb), (upsoninv18daykwavg, upsoninv18daykw, upsoninvup18cb), (upsoninv19daykwavg, upsoninv19daykw, upsoninvup19cb), (upsoninv20daykwavg, upsoninv20daykw, upsoninvup20cb)]
    warblerdaykwList = [(warblerinv1daykwavg, warblerinv1daykw, warblerinvup1cb), (warblerinv2daykwavg, warblerinv2daykw, warblerinvup2cb), (warblerinv3daykwavg, warblerinv3daykw, warblerinvup3cb), (warblerinv4daykwavg, warblerinv4daykw, warblerinvup4cb), (warblerinv5daykwavg, warblerinv5daykw, warblerinvup5cb), (warblerinv6daykwavg, warblerinv6daykw, warblerinvup6cb), (warblerinv7daykwavg, warblerinv7daykw, warblerinvup7cb), (warblerinv8daykwavg, warblerinv8daykw, warblerinvup8cb), (warblerinv9daykwavg, warblerinv9daykw, warblerinvup9cb), (warblerinv10daykwavg, warblerinv10daykw, warblerinvup10cb), (warblerinv11daykwavg, warblerinv11daykw, warblerinvup11cb), (warblerinv12daykwavg, warblerinv12daykw, warblerinvup12cb), (warblerinv13daykwavg, warblerinv13daykw, warblerinvup13cb), (warblerinv14daykwavg, warblerinv14daykw, warblerinvup14cb), (warblerinv15daykwavg, warblerinv15daykw, warblerinvup15cb), (warblerinv16daykwavg, warblerinv16daykw, warblerinvup16cb), (warblerinv17daykwavg, warblerinv17daykw, warblerinvup17cb), (warblerinv18daykwavg, warblerinv18daykw, warblerinvup18cb), (warblerinv19daykwavg, warblerinv19daykw, warblerinvup19cb), (warblerinv20daykwavg, warblerinv20daykw, warblerinvup20cb), (warblerinv21daykwavg, warblerinv21daykw, warblerinvup21cb), (warblerinv22daykwavg, warblerinv22daykw, warblerinvup22cb), (warblerinv23daykwavg, warblerinv23daykw, warblerinvup23cb), (warblerinv24daykwavg, warblerinv24daykw, warblerinvup24cb), (warblerinv25daykwavg, warblerinv25daykw, warblerinvup25cb), (warblerinv26daykwavg, warblerinv26daykw, warblerinvup26cb), (warblerinv27daykwavg, warblerinv27daykw, warblerinvup27cb), (warblerinv28daykwavg, warblerinv28daykw, warblerinvup28cb), (warblerinv29daykwavg, warblerinv29daykw, warblerinvup29cb), (warblerinv30daykwavg, warblerinv30daykw, warblerinvup30cb), (warblerinv31daykwavg, warblerinv31daykw, warblerinvup31cb), (warblerinv32daykwavg, warblerinv32daykw, warblerinvup32cb)]
    washingtondaykwList = [(washingtoninv4daykwavg, washingtoninv4daykw, washingtoninvup4cb), (washingtoninv5daykwavg, washingtoninv5daykw, washingtoninvup5cb), (washingtoninv6daykwavg, washingtoninv6daykw, washingtoninvup6cb), (washingtoninv7daykwavg, washingtoninv7daykw, washingtoninvup7cb), (washingtoninv8daykwavg, washingtoninv8daykw, washingtoninvup8cb), (washingtoninv9daykwavg, washingtoninv9daykw, washingtoninvup9cb), (washingtoninv10daykwavg, washingtoninv10daykw, washingtoninvup10cb), (washingtoninv11daykwavg, washingtoninv11daykw, washingtoninvup11cb), (washingtoninv12daykwavg, washingtoninv12daykw, washingtoninvup12cb), (washingtoninv15daykwavg, washingtoninv15daykw, washingtoninvup15cb), (washingtoninv16daykwavg, washingtoninv16daykw, washingtoninvup16cb), (washingtoninv17daykwavg, washingtoninv17daykw, washingtoninvup17cb), (washingtoninv18daykwavg, washingtoninv18daykw, washingtoninvup18cb), (washingtoninv19daykwavg, washingtoninv19daykw, washingtoninvup19cb), (washingtoninv21daykwavg, washingtoninv21daykw, washingtoninvup21cb), (washingtoninv22daykwavg, washingtoninv22daykw, washingtoninvup22cb), (washingtoninv23daykwavg, washingtoninv23daykw, washingtoninvup23cb), (washingtoninv24daykwavg, washingtoninv24daykw, washingtoninvup24cb), (washingtoninv40daykwavg, washingtoninv40daykw, washingtoninvup40cb)]
    washington12strdaykwList = [(washingtoninv1daykwavg, washingtoninv1daykw, washingtoninvup1cb), (washingtoninv2daykwavg, washingtoninv2daykw, washingtoninvup2cb), (washingtoninv3daykwavg, washingtoninv3daykw, washingtoninvup3cb), (washingtoninv13daykwavg, washingtoninv13daykw, washingtoninvup13cb), (washingtoninv14daykwavg, washingtoninv14daykw, washingtoninvup14cb), (washingtoninv20daykwavg, washingtoninv20daykw, washingtoninvup20cb), (washingtoninv25daykwavg, washingtoninv25daykw, washingtoninvup25cb), (washingtoninv26daykwavg, washingtoninv26daykw, washingtoninvup26cb), (washingtoninv27daykwavg, washingtoninv27daykw, washingtoninvup27cb), (washingtoninv28daykwavg, washingtoninv28daykw, washingtoninvup28cb), (washingtoninv29daykwavg, washingtoninv29daykw, washingtoninvup29cb), (washingtoninv30daykwavg, washingtoninv30daykw, washingtoninvup30cb), (washingtoninv31daykwavg, washingtoninv31daykw, washingtoninvup31cb), (washingtoninv32daykwavg, washingtoninv32daykw, washingtoninvup32cb), (washingtoninv33daykwavg, washingtoninv33daykw, washingtoninvup33cb), (washingtoninv34daykwavg, washingtoninv34daykw, washingtoninvup34cb), (washingtoninv35daykwavg, washingtoninv35daykw, washingtoninvup35cb), (washingtoninv36daykwavg, washingtoninv36daykw, washingtoninvup36cb), (washingtoninv37daykwavg, washingtoninv37daykw, washingtoninvup37cb), (washingtoninv38daykwavg, washingtoninv38daykw, washingtoninvup38cb), (washingtoninv39daykwavg, washingtoninv39daykw, washingtoninvup39cb)]
    whitehalldaykwList = [(whitehallinv1daykwavg, whitehallinv1daykw, whitehallinvup1cb), (whitehallinv3daykwavg, whitehallinv3daykw, whitehallinvup3cb), (whitehallinv4daykwavg, whitehallinv4daykw, whitehallinvup4cb), (whitehallinv5daykwavg, whitehallinv5daykw, whitehallinvup5cb), (whitehallinv13daykwavg, whitehallinv13daykw, whitehallinvup13cb), (whitehallinv14daykwavg, whitehallinv14daykw, whitehallinvup14cb), (whitehallinv15daykwavg, whitehallinv15daykw, whitehallinvup15cb), (whitehallinv16daykwavg, whitehallinv16daykw, whitehallinvup16cb)]
    whitehall13strdaykwList = [(whitehallinv2daykwavg, whitehallinv2daykw, whitehallinvup2cb), (whitehallinv6daykwavg, whitehallinv6daykw, whitehallinvup6cb), (whitehallinv7daykwavg, whitehallinv7daykw, whitehallinvup7cb), (whitehallinv8daykwavg, whitehallinv8daykw, whitehallinvup8cb), (whitehallinv9daykwavg, whitehallinv9daykw, whitehallinvup9cb), (whitehallinv10daykwavg, whitehallinv10daykw, whitehallinvup10cb), (whitehallinv11daykwavg, whitehallinv11daykw, whitehallinvup11cb), (whitehallinv12daykwavg, whitehallinv12daykw, whitehallinvup12cb)]
    whitetaildaykwList = [(whitetailinv1daykwavg, whitetailinv1daykw, whitetailinvup1cb), (whitetailinv2daykwavg, whitetailinv2daykw, whitetailinvup2cb), (whitetailinv3daykwavg, whitetailinv3daykw, whitetailinvup3cb), (whitetailinv5daykwavg, whitetailinv5daykw, whitetailinvup5cb), (whitetailinv6daykwavg, whitetailinv6daykw, whitetailinvup6cb), (whitetailinv7daykwavg, whitetailinv7daykw, whitetailinvup7cb), (whitetailinv8daykwavg, whitetailinv8daykw, whitetailinvup8cb), (whitetailinv9daykwavg, whitetailinv9daykw, whitetailinvup9cb), (whitetailinv10daykwavg, whitetailinv10daykw, whitetailinvup10cb), (whitetailinv11daykwavg, whitetailinv11daykw, whitetailinvup11cb), (whitetailinv12daykwavg, whitetailinv12daykw, whitetailinvup12cb), (whitetailinv22daykwavg, whitetailinv22daykw, whitetailinvup22cb), (whitetailinv23daykwavg, whitetailinv23daykw, whitetailinvup23cb), (whitetailinv24daykwavg, whitetailinv24daykw, whitetailinvup24cb), (whitetailinv25daykwavg, whitetailinv25daykw, whitetailinvup25cb), (whitetailinv32daykwavg, whitetailinv32daykw, whitetailinvup32cb), (whitetailinv33daykwavg, whitetailinv33daykw, whitetailinvup33cb), (whitetailinv35daykwavg, whitetailinv35daykw, whitetailinvup35cb), (whitetailinv36daykwavg, whitetailinv36daykw, whitetailinvup36cb), (whitetailinv37daykwavg, whitetailinv37daykw, whitetailinvup37cb), (whitetailinv38daykwavg, whitetailinv38daykw, whitetailinvup38cb), (whitetailinv39daykwavg, whitetailinv39daykw, whitetailinvup39cb), (whitetailinv40daykwavg, whitetailinv40daykw, whitetailinvup40cb), (whitetailinv41daykwavg, whitetailinv41daykw, whitetailinvup41cb), (whitetailinv42daykwavg, whitetailinv42daykw, whitetailinvup42cb), (whitetailinv49daykwavg, whitetailinv49daykw, whitetailinvup49cb), (whitetailinv50daykwavg, whitetailinv50daykw, whitetailinvup50cb), (whitetailinv51daykwavg, whitetailinv51daykw, whitetailinvup51cb), (whitetailinv57daykwavg, whitetailinv57daykw, whitetailinvup57cb), (whitetailinv61daykwavg, whitetailinv61daykw, whitetailinvup61cb), (whitetailinv62daykwavg, whitetailinv62daykw, whitetailinvup62cb), (whitetailinv63daykwavg, whitetailinv63daykw, whitetailinvup63cb), (whitetailinv65daykwavg, whitetailinv65daykw, whitetailinvup65cb), (whitetailinv66daykwavg, whitetailinv66daykw, whitetailinvup66cb), (whitetailinv67daykwavg, whitetailinv67daykw, whitetailinvup67cb), (whitetailinv68daykwavg, whitetailinv68daykw, whitetailinvup68cb), (whitetailinv69daykwavg, whitetailinv69daykw, whitetailinvup69cb), (whitetailinv70daykwavg, whitetailinv70daykw, whitetailinvup70cb), (whitetailinv71daykwavg, whitetailinv71daykw, whitetailinvup71cb), (whitetailinv72daykwavg, whitetailinv72daykw, whitetailinvup72cb), (whitetailinv73daykwavg, whitetailinv73daykw, whitetailinvup73cb), (whitetailinv74daykwavg, whitetailinv74daykw, whitetailinvup74cb), (whitetailinv75daykwavg, whitetailinv75daykw, whitetailinvup75cb), (whitetailinv76daykwavg, whitetailinv76daykw, whitetailinvup76cb), (whitetailinv77daykwavg, whitetailinv77daykw, whitetailinvup77cb), (whitetailinv78daykwavg, whitetailinv78daykw, whitetailinvup78cb), (whitetailinv79daykwavg, whitetailinv79daykw, whitetailinvup79cb), (whitetailinv80daykwavg, whitetailinv80daykw, whitetailinvup80cb)]
    whitetail17strdaykwList = [(whitetailinv4daykwavg, whitetailinv4daykw, whitetailinvup4cb), (whitetailinv13daykwavg, whitetailinv13daykw, whitetailinvup13cb), (whitetailinv14daykwavg, whitetailinv14daykw, whitetailinvup14cb), (whitetailinv15daykwavg, whitetailinv15daykw, whitetailinvup15cb), (whitetailinv16daykwavg, whitetailinv16daykw, whitetailinvup16cb), (whitetailinv17daykwavg, whitetailinv17daykw, whitetailinvup17cb), (whitetailinv18daykwavg, whitetailinv18daykw, whitetailinvup18cb), (whitetailinv19daykwavg, whitetailinv19daykw, whitetailinvup19cb), (whitetailinv20daykwavg, whitetailinv20daykw, whitetailinvup20cb), (whitetailinv21daykwavg, whitetailinv21daykw, whitetailinvup21cb), (whitetailinv26daykwavg, whitetailinv26daykw, whitetailinvup26cb), (whitetailinv27daykwavg, whitetailinv27daykw, whitetailinvup27cb), (whitetailinv28daykwavg, whitetailinv28daykw, whitetailinvup28cb), (whitetailinv29daykwavg, whitetailinv29daykw, whitetailinvup29cb), (whitetailinv30daykwavg, whitetailinv30daykw, whitetailinvup30cb), (whitetailinv31daykwavg, whitetailinv31daykw, whitetailinvup31cb), (whitetailinv34daykwavg, whitetailinv34daykw, whitetailinvup34cb), (whitetailinv43daykwavg, whitetailinv43daykw, whitetailinvup43cb), (whitetailinv44daykwavg, whitetailinv44daykw, whitetailinvup44cb), (whitetailinv45daykwavg, whitetailinv45daykw, whitetailinvup45cb), (whitetailinv46daykwavg, whitetailinv46daykw, whitetailinvup46cb), (whitetailinv47daykwavg, whitetailinv47daykw, whitetailinvup47cb), (whitetailinv48daykwavg, whitetailinv48daykw, whitetailinvup48cb), (whitetailinv52daykwavg, whitetailinv52daykw, whitetailinvup52cb), (whitetailinv53daykwavg, whitetailinv53daykw, whitetailinvup53cb), (whitetailinv54daykwavg, whitetailinv54daykw, whitetailinvup54cb), (whitetailinv55daykwavg, whitetailinv55daykw, whitetailinvup55cb), (whitetailinv56daykwavg, whitetailinv56daykw, whitetailinvup56cb), (whitetailinv58daykwavg, whitetailinv58daykw, whitetailinvup58cb), (whitetailinv59daykwavg, whitetailinv59daykw, whitetailinvup59cb), (whitetailinv60daykwavg, whitetailinv60daykw, whitetailinvup60cb), (whitetailinv64daykwavg, whitetailinv64daykw, whitetailinvup64cb)]
    conetoe1daykwList = [(conetoe1inv1daykwavg, conetoe1inv1daykw, conetoe1invup1cb), (conetoe1inv2daykwavg, conetoe1inv2daykw, conetoe1invup2cb), (conetoe1inv3daykwavg, conetoe1inv3daykw, conetoe1invup3cb), (conetoe1inv4daykwavg, conetoe1inv4daykw, conetoe1invup4cb)]
    duplindaykwList = [(duplinsinv1daykwavg, duplinsinv1daykw, duplininvup4cb), (duplinsinv2daykwavg, duplinsinv2daykw, duplininvup5cb), (duplinsinv3daykwavg, duplinsinv3daykw, duplininvup6cb), (duplinsinv4daykwavg, duplinsinv4daykw, duplininvup7cb), (duplinsinv5daykwavg, duplinsinv5daykw, duplininvup8cb), (duplinsinv6daykwavg, duplinsinv6daykw, duplininvup9cb), (duplinsinv7daykwavg, duplinsinv7daykw, duplininvup10cb), (duplinsinv8daykwavg, duplinsinv8daykw, duplininvup11cb), (duplinsinv9daykwavg, duplinsinv9daykw, duplininvup12cb), (duplinsinv10daykwavg, duplinsinv10daykw, duplininvup13cb), (duplinsinv11daykwavg, duplinsinv11daykw, duplininvup14cb), (duplinsinv12daykwavg, duplinsinv12daykw, duplininvup15cb), (duplinsinv13daykwavg, duplinsinv13daykw, duplininvup16cb), (duplinsinv14daykwavg, duplinsinv14daykw, duplininvup17cb), (duplinsinv15daykwavg, duplinsinv15daykw, duplininvup18cb), (duplinsinv16daykwavg, duplinsinv16daykw, duplininvup19cb), (duplinsinv17daykwavg, duplinsinv17daykw, duplininvup20cb), (duplinsinv18daykwavg, duplinsinv18daykw, duplininvup21cb)]
    duplinCentraldaykwList = [(duplininv1daykwavg, duplininv1daykw, duplininvup1cb), (duplininv2daykwavg, duplininv2daykw, duplininvup2cb), (duplininv3daykwavg, duplininv3daykw, duplininvup3cb)]
    wayne11000daykwList = [(wayne1inv1daykwavg, wayne1inv1daykw, wayne1invup1cb), (wayne1inv4daykwavg, wayne1inv4daykw, wayne1invup4cb)]
    wayne1daykwList = [(wayne1inv2daykwavg, wayne1inv2daykw, wayne1invup2cb), (wayne1inv3daykwavg, wayne1inv3daykw, wayne1invup3cb)]
    wayne21000daykwList = [(wayne2inv3daykwavg, wayne2inv3daykw, wayne2invup3cb), (wayne2inv4daykwavg, wayne2inv4daykw, wayne2invup4cb)]
    wayne2daykwList = [(wayne2inv1daykwavg, wayne2inv1daykw, wayne2invup1cb), (wayne2inv2daykwavg, wayne2inv2daykw, wayne2invup2cb)]
    wayne31000daykwList = [(wayne3inv1daykwavg, wayne3inv1daykw, wayne3invup1cb), (wayne3inv2daykwavg, wayne3inv2daykw, wayne3invup2cb)]
    wayne3daykwList = [(wayne3inv3daykwavg, wayne3inv3daykw, wayne3invup3cb), (wayne3inv4daykwavg, wayne3inv4daykw, wayne3invup4cb)]
    freightlinedaykwList = [(freightlinerinv1daykwavg, freightlinerinv1daykw, freightlinerinvup1cb), (freightlinerinv3daykwavg, freightlinerinv3daykw, freightlinerinvup3cb), (freightlinerinv4daykwavg, freightlinerinv4daykw, freightlinerinvup4cb), (freightlinerinv5daykwavg, freightlinerinv5daykw, freightlinerinvup5cb), (freightlinerinv8daykwavg, freightlinerinv8daykw, freightlinerinvup8cb), (freightlinerinv9daykwavg, freightlinerinv9daykw, freightlinerinvup9cb), (freightlinerinv10daykwavg, freightlinerinv10daykw, freightlinerinvup10cb), (freightlinerinv11daykwavg, freightlinerinv11daykw, freightlinerinvup11cb), (freightlinerinv12daykwavg, freightlinerinv12daykw, freightlinerinvup12cb), (freightlinerinv15daykwavg, freightlinerinv15daykw, freightlinerinvup15cb), (freightlinerinv16daykwavg, freightlinerinv16daykw, freightlinerinvup16cb), (freightlinerinv17daykwavg, freightlinerinv17daykw, freightlinerinvup17cb), (freightlinerinv18daykwavg, freightlinerinv18daykw, freightlinerinvup18cb)]
    freightline66daykwList = [(freightlinerinv2daykwavg, freightlinerinv2daykw, freightlinerinvup2cb), (freightlinerinv6daykwavg, freightlinerinv6daykw, freightlinerinvup6cb), (freightlinerinv7daykwavg, freightlinerinv7daykw, freightlinerinvup7cb), (freightlinerinv13daykwavg, freightlinerinv13daykw, freightlinerinvup13cb), (freightlinerinv14daykwavg, freightlinerinv14daykw, freightlinerinvup14cb)]
    hollyswampdaykwList = [(hollyswampinv1daykwavg, hollyswampinv1daykw, hollyswampinvup1cb), (hollyswampinv2daykwavg, hollyswampinv2daykw, hollyswampinvup2cb), (hollyswampinv3daykwavg, hollyswampinv3daykw, hollyswampinvup3cb), (hollyswampinv4daykwavg, hollyswampinv4daykw, hollyswampinvup4cb), (hollyswampinv5daykwavg, hollyswampinv5daykw, hollyswampinvup5cb), (hollyswampinv6daykwavg, hollyswampinv6daykw, hollyswampinvup6cb), (hollyswampinv7daykwavg, hollyswampinv7daykw, hollyswampinvup7cb), (hollyswampinv8daykwavg, hollyswampinv8daykw, hollyswampinvup8cb), (hollyswampinv9daykwavg, hollyswampinv9daykw, hollyswampinvup9cb), (hollyswampinv10daykwavg, hollyswampinv10daykw, hollyswampinvup10cb), (hollyswampinv11daykwavg, hollyswampinv11daykw, hollyswampinvup11cb), (hollyswampinv12daykwavg, hollyswampinv12daykw, hollyswampinvup12cb), (hollyswampinv14daykwavg, hollyswampinv14daykw, hollyswampinvup14cb), (hollyswampinv16daykwavg, hollyswampinv16daykw, hollyswampinvup16cb)]
    hollyswamp18strdaykwList = [(hollyswampinv15daykwavg, hollyswampinv15daykw, hollyswampinvup15cb), (hollyswampinv13daykwavg, hollyswampinv13daykw, hollyswampinvup13cb)]
    pgdaykwList = [(pginv7daykwavg, pginv7daykw, pginvup7cb), (pginv8daykwavg, pginv8daykw, pginvup8cb), (pginv9daykwavg, pginv9daykw, pginvup9cb), (pginv10daykwavg, pginv10daykw, pginvup10cb), (pginv11daykwavg, pginv11daykw, pginvup11cb), (pginv12daykwavg, pginv12daykw, pginvup12cb), (pginv13daykwavg, pginv13daykw, pginvup13cb), (pginv14daykwavg, pginv14daykw, pginvup14cb), (pginv15daykwavg, pginv15daykw, pginvup15cb), (pginv16daykwavg, pginv16daykw, pginvup16cb), (pginv17daykwavg, pginv17daykw, pginvup17cb), (pginv18daykwavg, pginv18daykw, pginvup18cb)]
    pg66daykwList = [(pginv1daykwavg, pginv1daykw, pginvup1cb), (pginv2daykwavg, pginv2daykw, pginvup2cb), (pginv3daykwavg, pginv3daykw, pginvup3cb), (pginv4daykwavg, pginv4daykw, pginvup4cb), (pginv5daykwavg, pginv5daykw, pginvup5cb), (pginv6daykwavg, pginv6daykw, pginvup6cb)]
    cougar14strList = [(cougarinv1daykwavg, cougarinv1daykw, cougarinvup1cb), (cougarinv2daykwavg, cougarinv2daykw, cougarinvup2cb), (cougarinv3daykwavg, cougarinv3daykw, cougarinvup3cb), (cougarinv4daykwavg, cougarinv4daykw, cougarinvup4cb), (cougarinv5daykwavg, cougarinv5daykw, cougarinvup5cb), (cougarinv6daykwavg, cougarinv6daykw, cougarinvup6cb), (cougarinv7daykwavg, cougarinv7daykw, cougarinvup7cb), (cougarinv8daykwavg, cougarinv8daykw, cougarinvup8cb), (cougarinv9daykwavg, cougarinv9daykw, cougarinvup9cb), (cougarinv10daykwavg, cougarinv10daykw, cougarinvup10cb), (cougarinv11daykwavg, cougarinv11daykw, cougarinvup11cb), (cougarinv12daykwavg, cougarinv12daykw, cougarinvup12cb), (cougarinv13daykwavg, cougarinv13daykw, cougarinvup13cb), (cougarinv14daykwavg, cougarinv14daykw, cougarinvup14cb), (cougarinv15daykwavg, cougarinv15daykw, cougarinvup15cb), (cougarinv16daykwavg, cougarinv16daykw, cougarinvup16cb), (cougarinv17daykwavg, cougarinv17daykw, cougarinvup17cb), (cougarinv18daykwavg, cougarinv18daykw, cougarinvup18cb), (cougarinv19daykwavg, cougarinv19daykw, cougarinvup19cb), (cougarinv20daykwavg, cougarinv20daykw, cougarinvup20cb), (cougarinv21daykwavg, cougarinv21daykw, cougarinvup21cb), (cougarinv22daykwavg, cougarinv22daykw, cougarinvup22cb), (cougarinv25daykwavg, cougarinv25daykw, cougarinvup25cb), (cougarinv26daykwavg, cougarinv26daykw, cougarinvup26cb), (cougarinv27daykwavg, cougarinv27daykw, cougarinvup27cb), (cougarinv28daykwavg, cougarinv28daykw, cougarinvup28cb), (cougarinv29daykwavg, cougarinv29daykw, cougarinvup29cb), (cougarinv30daykwavg, cougarinv30daykw, cougarinvup30cb), (cougarinv31daykwavg, cougarinv31daykw, cougarinvup31cb)]
    cougar13strList = [(cougarinv23daykwavg, cougarinv23daykw, cougarinvup23cb), (cougarinv24daykwavg, cougarinv24daykw, cougarinvup24cb)]
    elk10strList = [(elkinv9daykwavg, elkinv9daykw, elkinvup9cb), (elkinv10daykwavg, elkinv10daykw, elkinvup10cb), (elkinv11daykwavg, elkinv11daykw, elkinvup11cb), (elkinv12daykwavg, elkinv12daykw, elkinvup12cb), (elkinv13daykwavg, elkinv13daykw, elkinvup13cb), (elkinv21daykwavg, elkinv21daykw, elkinvup21cb), (elkinv22daykwavg, elkinv22daykw, elkinvup22cb), (elkinv25daykwavg, elkinv25daykw, elkinvup25cb), (elkinv26daykwavg, elkinv26daykw, elkinvup26cb), (elkinv27daykwavg, elkinv27daykw, elkinvup27cb), (elkinv28daykwavg, elkinv28daykw, elkinvup28cb), (elkinv29daykwavg, elkinv29daykw, elkinvup29cb)]
    elk11strList = [(elkinv1daykwavg, elkinv1daykw, elkinvup1cb), (elkinv2daykwavg, elkinv2daykw, elkinvup2cb), (elkinv3daykwavg, elkinv3daykw, elkinvup3cb), (elkinv4daykwavg, elkinv4daykw, elkinvup4cb), (elkinv5daykwavg, elkinv5daykw, elkinvup5cb), (elkinv6daykwavg, elkinv6daykw, elkinvup6cb), (elkinv7daykwavg, elkinv7daykw, elkinvup7cb), (elkinv8daykwavg, elkinv8daykw, elkinvup8cb), (elkinv14daykwavg, elkinv14daykw, elkinvup14cb), (elkinv15daykwavg, elkinv15daykw, elkinvup15cb), (elkinv16daykwavg, elkinv16daykw, elkinvup16cb), (elkinv17daykwavg, elkinv17daykw, elkinvup17cb), (elkinv18daykwavg, elkinv18daykw, elkinvup18cb), (elkinv19daykwavg, elkinv19daykw, elkinvup19cb), (elkinv20daykwavg, elkinv20daykw, elkinvup20cb), (elkinv23daykwavg, elkinv23daykw, elkinvup23cb), (elkinv24daykwavg, elkinv24daykw, elkinvup24cb), (elkinv30daykwavg, elkinv30daykw, elkinvup30cb), (elkinv31daykwavg, elkinv31daykw, elkinvup31cb), (elkinv32daykwavg, elkinv32daykw, elkinvup32cb), (elkinv33daykwavg, elkinv33daykw, elkinvup33cb), (elkinv34daykwavg, elkinv34daykw, elkinvup34cb), (elkinv35daykwavg, elkinv35daykw, elkinvup35cb), (elkinv36daykwavg, elkinv36daykw, elkinvup36cb), (elkinv37daykwavg, elkinv37daykw, elkinvup37cb), (elkinv38daykwavg, elkinv38daykw, elkinvup38cb), (elkinv39daykwavg, elkinv39daykw, elkinvup39cb), (elkinv40daykwavg, elkinv40daykw, elkinvup40cb), (elkinv41daykwavg, elkinv41daykw, elkinvup41cb), (elkinv42daykwavg, elkinv42daykw, elkinvup42cb), (elkinv43daykwavg, elkinv43daykw, elkinvup43cb)]

    site_under_Lists = {
        "Duplin Central Inverters": duplinCentraldaykwList,
        "Bulloch 1A 11 String Inverters": bulloch1adaykwList,
        "Bulloch 1A 10 String Inverters": bulloch1a10strdaykwList,
        "Bulloch 1B 11 String Inverters": bulloch1bdaykwList,
        "Bulloch 1B 10 String Inverters": bulloch1b10strdaykwList,
        "Cougar 13 String Inverters": cougar13strList,
        "Cougar 14 String Inverters": cougar14strList,
        "Elk 10 String Inverters": elk10strList,
        "Elk 11 String Inverters": elk11strList,

        "Gray Fox Inverters": grayfoxdaykwList,
        #Is seperate groups but I don't know how to split them based on As Builts

        "Harding 13 String Inverters": hardingdaykwList,
        "Harding 12 String Inverters": harding12strdaykwList,
        "McLean Inverters": mcleandaykwList,
        "McLean 10 String Inverters": mclean10strdaykwList,
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
        "Conetoe Inverters": conetoe1daykwList,
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
        "Cherry Blossom Inverters": cherryblossomdaykwList,
        "Cardinal 96.6% Inverters": cardinal96daykwList,
        "Cardinal 95.2% Inverters": cardinal952daykwList,
        "Cardinal 94.4% Inverters": cardinal944daykwList
    }


    for inv_group_name, underperformance_list in site_under_Lists.items():
        if inv_group_name in {"Duplin String Inverters", "Cardinal 96.6% Inverters", "Cardinal 95.2% Inverters", "Cardinal 94.4% Inverters"}:
            avgvalues = [value for value, _, _ in underperformance_list]
            totalvalues = [value for _, value, _ in underperformance_list]
            max_val = max(avgvalues)
            total_max_val = max(totalvalues)
            print(inv_group_name, max_val, avgvalues)
            print(inv_group_name, total_max_val, totalvalues)

        calculate_percentages(underperformance_list) #Updates GUI widgets with new percentages
    


def get_color_for_percentage(percentage):
    """Returns a color string based on a percentage value."""
    if np.isnan(percentage) or percentage < 50:
        return "red"
    elif 50 <= percentage < 75:
        return "orange"
    elif 75 <= percentage < 85:
        return "yellow"
    elif 85 <= percentage < 95:
        return "#FEEAA5"  # paleyellow
    elif percentage >= 95:
        return "#90EE90"  # lightgreen
    else:
        return "#EE82EE"  # violet

def create_dual_color_image(c1, c2, width=60, height=15):
    """Creates a PhotoImage with two background colors."""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width // 2, height], fill=c1)
    draw.rectangle([width // 2, 0, width, height], fill=c2)
    return ImageTk.PhotoImage(img)
    
    


def calculate_percentages(data_list):
    """
    Calculates percentages based on the maximum value in the input list
    and assigns these percentages to the 'text' attribute of the Tkinter variable.

    Args:
        data_list: A list of tuples, where each tuple contains:
            - avg kw (float).
            - total kwh (float)
            - The Tkinter Checkbutton variable to update.
    """
    if not data_list:
        return  # Handle empty list case
    avg_values = [value for value, _, _ in data_list]
    total_values = [value for _, value, _ in data_list]
    maxavg_value = max(avg_values)
    maxtotal_value = max(total_values)
    if (maxavg_value == 0 or np.isnan(maxavg_value)) and (maxtotal_value == 0 or np.isnan(maxtotal_value)):
        for _, _, var in data_list:
            try:
                var.config(text="0% | 0%", bg='red')  # Update the 'text' attribute
            except AttributeError:
                pass #  The variable does not have a text attribute.
        return

    for avg, total_kwh, var in data_list:
        avg_percentage = (avg / maxavg_value) * 100
        total_percentage = (total_kwh / maxtotal_value) * 100
        avg_color = get_color_for_percentage(avg_percentage)
        total_color = get_color_for_percentage(total_percentage)

        try:
            # Create the dual-color image
            dual_color_image = create_dual_color_image(avg_color, total_color)
            
            # Configure the checkbutton
            var.config(
                text=f"{avg_percentage:.0f}% | {total_percentage:.0f}%",
                image=dual_color_image,
                compound="center",  # Place text on top of the image
                fg="black" # Set a contrasting text color
            )
            # IMPORTANT: Keep a reference to the image to prevent it from being garbage collected
            var.image = dual_color_image
        except AttributeError:
             pass #  The variable does not have a text attribute.


def checkin():
    try: 
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
                    bg_color = '#90EE90'  # Pale Light Green
                else:
                    bg_color = '#ADD8E6'  # Light Blue of Main Site Data Window
                if col_index == 2:
                    wsize = 24
                elif col_index == 1:
                    wsize = 32
                else:
                    wsize = 23
                label = Label(checkIns, text=value, font=("Calibri", 14), borderwidth=1, relief="solid", width=wsize, bg=bg_color)
                label.grid(row=row_index, column=col_index)

    except pyobdc.Error as err:
        print("Logbook Error: ", err)

    lbconnection.close()
    update_data()


def last_update():
    times = []
    for site, invdict, metermax, var, place, pvsyst_name in master_List_Sites:
        if site != "CDIA":
            c.execute(f"SELECT TOP 1 [Timestamp] FROM [{site} Meter Data] ORDER BY [Timestamp] DESC")
            last_time = c.fetchone()
            times.append(last_time[0])
    most_recent = max(times)
    return most_recent







def time_window():

    global timecurrent, text_update_Table
    #SELECT 15 = 30 Mins
    c.execute("SELECT TOP 16 [Timestamp] FROM [Ogburn Meter Data] ORDER BY [Timestamp] DESC")
    data_timestamps = c.fetchall()
    firsttime = data_timestamps[0][0]
    secondtime = data_timestamps[1][0]
    thirdtime = data_timestamps[2][0]
    fourthtime = data_timestamps[3][0]
    fifthtime = data_timestamps[4][0]
    tenthtime = data_timestamps[9][0]
    lasttime = data_timestamps[14][0]

    hm_firsttime = firsttime.strftime('%H:%M')
    hm_secondtime = secondtime.strftime('%H:%M')
    hm_thirdtime = thirdtime.strftime('%H:%M')
    hm_fourthtime = fourthtime.strftime('%H:%M')
    hm_tenthtime = tenthtime.strftime('%H:%M')
    hm_lasttime = lasttime.strftime('%H:%M')

    time1v.config(text=hm_firsttime, font=("Calibri", 16))
    time2v.config(text=hm_secondtime, font=("Calibri", 16))
    time3v.config(text=hm_thirdtime, font=("Calibri", 16))
    time4v.config(text=hm_fourthtime, font=("Calibri", 16))
    time10v.config(text=hm_tenthtime, font=("Calibri", 16))
    timeLv.config(text=hm_lasttime, font=("Calibri", 16))

    pulls5TD = firsttime - fifthtime
    pulls5TDmins = round(pulls5TD.total_seconds() / 60, 2)
    pulls15TD = firsttime - lasttime
    pulls15TDmins = round(pulls15TD.total_seconds() / 60, 2)
    spread10.config(text=f"5 Pulls\n{pulls5TDmins} Minutes")
    spread15.config(text=f"15 Pulls\n{pulls15TDmins} Minutes")
    
    timecurrent = datetime.now()
    db_update_time = 10
    timecompare = timecurrent - timedelta(minutes=db_update_time)
    recent_update = last_update()
    if recent_update < timecompare and comms_delay.get() == False:
        os.startfile(r"G:\Shared drives\O&M\NCC Automations\Notification System\API Data Pull, Multi SQL.py")
        msg = f"The Database has not been updated in {str(db_update_time)} Minutes and usually updates every 2\nLaunching Data Pull Script in response."
        if not textOnly.get():
            messagebox.showerror(parent=timeW, title="Notification System/GUI", message=msg)
        else:
            try:
                text_update_Table.append("<br>" + str(msg))
            except UnboundLocalError:
                pass
            except NameError:
                pass
        ty.sleep(180)

    tupdate = timecurrent.strftime('%H:%M')

    timmytimeLabel.config(text= tupdate, font= ("Calibiri", 30))
    
    checkin() 

def db_to_dict():
    query_start = ty.perf_counter()
    sendTexts.config(state=DISABLED)
    underperfdaterng.config(state=DISABLED)
    underperfdaterng2.config(state=DISABLED)

    connect_db()
    global tables, inv_data, breaker_data, meter_data, comm_data, POA_data, begin
    tables = []
    for tb in c.tables(tableType='TABLE'):
        if 'Data' in tb.table_name:
            tables.append(tb)
    #ic(tables)
    excluded_tables = ["1)Sites", "2)Breakers", "3)Meters", "4)Inverters", "5)POA"]

    tb_file = r"C:\Users\omops\Documents\Automations\Troubleshooting.txt"
    comm_data = {}
    for table in tables:
        table_name = table.table_name
        if table_name not in excluded_tables:
            c.execute(f"SELECT TOP 10 [Last Upload] FROM [{table_name}] ORDER BY Timestamp DESC")
            comm_value = c.fetchall()
            comm_data[table_name] = comm_value

    #ic(comm_data)
    inv_data = {}
    for table in tables:
        table_name = table.table_name
        if "INV" in table_name and table_name not in excluded_tables:
            #SELECT 15 = 30 Mins
            c.execute(f"SELECT TOP 16 [dc V], Watts FROM [{table_name}] ORDER BY Timestamp DESC")
            inv_rows = c.fetchall()
            #ic(inv_rows)
            inv_data[table_name] = inv_rows
    #ic(inv_data)

    meter_data = {}
    for table in tables:
        table_name = table.table_name
        if any(name in table_name for name in ["Hickory", "Whitehall"]) and "Meter" in table_name:
            #SELECT 13 = 17 Mins of Data
            c.execute(f"SELECT TOP 16 [Volts A], [Volts B], [Volts C], [Amps A], [Amps B], [Amps C], Watts FROM [{table_name}] ORDER BY Timestamp DESC")
            meter_rows = c.fetchall()
            meter_data[table_name] = meter_rows 
        elif any(name in table_name for name in ["Wellons",]) and "Meter" in table_name:
            #SELECT 45 = 60 Mins of Data | Wellons has a severe intermittent comms issue.
            c.execute(f"SELECT TOP 60 [Volts A], [Volts B], [Volts C], [Amps A], [Amps B], [Amps C], Watts FROM [{table_name}] ORDER BY Timestamp DESC")
            meter_rows = c.fetchall()
            meter_data[table_name] = meter_rows 
        elif "Meter" in table_name and table_name not in excluded_tables:
            #SELECT 5 = 5.5 Mins of Data
            c.execute(f"SELECT TOP {meter_pulls} [Volts A], [Volts B], [Volts C], [Amps A], [Amps B], [Amps C], Watts FROM [{table_name}] ORDER BY Timestamp DESC")
            meter_rows = c.fetchall()
            meter_data[table_name] = meter_rows

    #ic(meter_data)
    POA_data = {}
    for table in tables:
        table_name = table.table_name
        if "POA" in table_name and table_name not in excluded_tables:
            c.execute(f"SELECT TOP 1 [W/M²] FROM [{table_name}] ORDER BY [Timestamp] DESC")
            POA_rows = c.fetchone()
            POA_data[table_name] = POA_rows
    

    #ic(POA_data)

    breaker_data = {}
    for table in tables:
        table_name = table.table_name
        if "Breaker" in table_name and table_name not in excluded_tables:
            c.execute(f"SELECT TOP {breaker_pulls} [Status] FROM [{table_name}] ORDER BY [Timestamp] DESC")
            breaker_rows = c.fetchall()
            breaker_data[table_name] = breaker_rows
    #ic(breaker_data)

    begin = launch_check()

    query_end = ty.perf_counter()
    print("Query Time (secs):", round(query_end - query_start, 2))
    time_window()



def parse_wo():
    directory = "G:\\Shared drives\\O&M\\NCC Automations\\Notification System\\WO Tracking\\"
    existing_wo_files = glob.glob(os.path.join(directory, "*.txt"))
    for file in existing_wo_files:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Error: {e}")

    open_wo_file = filedialog.askopenfilename(parent=alertW,
        title="Select a file", 
        filetypes=[("Excel Files", "*.xlsx *.xls")],
        initialdir="C:\\Users\\OMOPS\\Downloads")
    wo_data = pd.read_excel(open_wo_file)
    for index, row in wo_data.iterrows():
        var_adjustment = [", LLC", "Farm", "Cadle", "Solar"]
        site = row['Site']
        if pd.isna(site) or site in  {"Charter GM", "Charter RM", "Charter Roof"}:
            continue
        varname = str(site)
        for phrase in var_adjustment:
            varname = varname.replace(phrase, "")
        if 'Wayne' in site:
            varname = varname.replace("III", "3")
            varname = varname.replace("II", "2")
            varname = varname.replace("I", "1")
        varname = varname.replace(" ", "").lower()
        varname = varname.replace("freightline", "freightliner")
        if site == "BISHOPVILLE":
            varname = 'bishopvilleII'
        
        status = row['Job Status']
        error_type = row['Fault Code Category']
        device_type = row['Asset Description']
        wo_summary = row['Brief Description']
        notes = row['Work Description']
        wo_date = row['WO Date']
        wo_num = row['WO No.']


        if error_type == 'No Issue':
            continue

        #Inverter check
        if 'inv' in device_type.lower() or 'inv' in wo_summary.lower():
            inv_pattern = r"(?:inverter|inv)\s*(\d+)?(?:-|\.)?(\d+)?"
            matchs = re.search(inv_pattern, wo_summary.lower())
            #Reset Variables
            group = None
            num = None
            if matchs is not None:
                group = int(matchs.group(1)) if matchs.group(1) is not None else None
                num = int(matchs.group(2)) if matchs.group(2) is not None else group
            print(f"{site}  |  {group} | {num}")
            
            #Inverter # not Found
            if group == None or num == None:
                print(f"{site} | G:{group} | Num:{num} WO Parse")
                continue

            inv_num = define_inv_num(site, group, num)
            
            if inv_num is None:
                print(f"Num: {inv_num} | {site} | {wo_num} | {wo_summary}\n")
            else:            
                # Construct the file path for the text file
                txt_file_path = os.path.join(directory, f"{varname} Open WO's.txt")
                # Append the row data to the text file
                with open(txt_file_path, 'a+') as file:
                    file.write(f'{inv_num:<3}|  WO: {wo_num:<8}|  {wo_date}  |  {wo_summary}\n')
                

            #Color Assignment Logic
            current_colorstatus = globals()[f'{varname}inv{inv_num}WOLabel'].cget('text')
            if current_colorstatus == 'gray':
                continue
            
            if error_type == 'Underperformance':
                if current_colorstatus == 'black':
                    color = 'gray'
                else:
                    color = 'blue' 
            elif error_type == 'Equipment Outage':
                if current_colorstatus == 'blue':
                    color = 'gray'
                else:
                    color = 'black'
            elif error_type == 'COMMs Outage':
                color = 'pink'
            else: 
                color = 'yellow'


            globals()[f'{varname}inv{inv_num}WOLabel'].config(bg=color)



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
    messagebox.showinfo(parent=alertW, title="Checkbutton Info", message= """The First column of CheckButtons in the Site Data Window turns off all notifications associated with that Site.
                        \nThe POA CB will change the value to 9999 so that no inv outages are filtered by the POA
                        \nThe colored INV CheckButtons are to be selected when a WO is open for that device and will turn off notifications of outages with INV
                        \nThe Box in the middle Represents the Status of that device in Emaint. | ⬜ = NO WO | Black BG = Offline WO Open | Blue BG = Underperformance WO Open | Pink BG = Comms Outage WO Open | Yellow BG = Unknown WO Found |
                        \nThe 3rd Column is a CB for Underperformance tracking. Data range is set by the user but as standard 30 days of data and only between the Hours of 10:00 to 15:00.
                        \nThe first value is calculated by averaging all the values in the data range, then comparing the results to the others in the group.
                        \nThe second value is a total of all the values in the data range, then comparing the results to the others in the group.""")

    
    return True
def open_file():
    os.startfile(r"G:\Shared drives\Narenco Projects\O&M Projects\NCC\Procedures\NCC Tools - Joseph\Also Energy GUI Interactions.docx")
    

cur_time = datetime.now()
tupdate =  cur_time.strftime('%H:%M')
notesFrame = Frame(alertW)
notesFrame.grid(row=0, column=0, sticky=EW)
alertwnotes = Label(notesFrame, text= "1st Checkbox: ✓ = Open WO\n& pauses inv notifications", font= ("Calibiri", 12))
alertwnotes.pack()
tupdateLabel = Label(notesFrame, text= "GUI Last Updated", font= ("Calibiri", 18))
tupdateLabel.pack()
timmytimeLabel = Label(notesFrame, text= tupdate, font= ("Calibiri", 30))
timmytimeLabel.pack()
notes_button = Button(notesFrame, command= lambda: check_button_notes(), text= "Checkbutton Notes", font=("Calibiri", 14), bg=main_color, cursor='hand2')
notes_button.pack(padx= 2, pady= 2, fill=X)
proc_button = Button(notesFrame, command= lambda: open_file(), text= "Procedure Doc", font=("Calibiri", 14), cursor='hand2')
proc_button.pack(padx= 2, pady= 2, fill=X)
wo_button = Button(notesFrame, command= lambda: parse_wo(), text= "Assess Open WO's", font=("Calibiri", 14), cursor='hand2')
wo_button.pack(padx= 2, pady= 2, fill=X)


notificationFrame = Frame(alertW)
notificationFrame.grid(row=0, column=1, sticky=N)
notificationNotes = Label(notificationFrame, text="Notification Settings", font=("Calibiri", 14))
notificationNotes.pack()
textOnly = IntVar()
sendTexts = Checkbutton(notificationFrame, text="Send Emails\n(Disable Local MsgBox's)", cursor='hand2', variable=textOnly)
sendTexts.pack(padx=2)
adminTexts = StringVar()
optionTexts = ttk.Combobox(notificationFrame, textvariable=adminTexts, values=["Joseph Lang", "Brandon Arrowood", "Jacob Budd", "Administrators + NCC", "Administrators Only"], state="readonly")
optionTexts.pack()
optionTexts.current(0)
notes_settings = Label(notificationFrame, text="\nSelect from the Dropdown\nBefore turning the function on\nwith the Checkbox\n")
notes_settings.pack()

comms_delay = BooleanVar()
comms_AE_delay = Checkbutton(notificationFrame, text="Select to pause\nrestart of Data Pull Script\nDo so if AE is in a\nmajor comms delay", variable= comms_delay, cursor='hand2')
comms_AE_delay.pack()



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