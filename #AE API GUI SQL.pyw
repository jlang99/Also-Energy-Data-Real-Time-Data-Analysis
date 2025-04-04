#AE API GUI
import warnings
import pyodbc
from datetime import datetime, date, time, timedelta
from tkinter import *
from tkinter import messagebox, filedialog
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

#Underperformance Analysis Packages
import pandas as pd
from sklearn.linear_model import LinearRegression

breaker_pulls = 6
meter_pulls = 8
mvi_percent = .70

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
timeW_notes.grid(row=0, column= 0, columnspan= 3)

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


underperfdatalbl= Label(timeW, text= "% Params", font= ("Calibiri", 16))
underperfdatalbl.grid(row=0, column=3)

underperf_range = IntVar()
underperf_range.set(30)
underperfdatalbl= Label(timeW, text= "Date Rng Today()-___:")
underperfdatalbl.grid(row=1, column=3)
underperfdaterng = Entry(timeW, width=10, textvariable=underperf_range)
underperfdaterng.grid(row=2, column=3)

underperf_hourlimit = IntVar()
underperf_hourlimit.set(10)
underperfhourstartlbl= Label(timeW, text= "Hour Start Limitation:")
underperfhourstartlbl.grid(row=3, column=3)
underperfhourstart = Entry(timeW, width=10, textvariable=underperf_hourlimit)
underperfhourstart.grid(row=4, column=3)

underperf_hourend = IntVar()
underperf_hourend.set(15)
underperfhourlbl= Label(timeW, text= "Hour End Limitation:")
underperfhourlbl.grid(row=5, column=3)
underperfhour = Entry(timeW, width=10, textvariable=underperf_hourend)
underperfhour.grid(row=6, column=3)


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
soltage.wm_attributes("-topmost", True)
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
                        9900000, 'bishopvilleII', inv, None),

                    ('Bluebird', {
    1: "A1", 2: "A2", 3: "A3", 4: "A4", 5: "A5", 6: "A6",
    7: "A7", 8: "A8", 9: "A9", 10: "A10", 11: "A11", 12: "A12",
    13: "B13", 14: "B14", 15: "B15", 16: "B16", 17: "B17", 18: "B18",
    19: "B19", 20: "B20", 21: "B21", 22: "B22", 23: "B23", 24: "B24"}, 
                    3000000, 'bluebird', narenco, 'BLUEBIRD'),

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
                    7080000, 'cardinal', narenco, 'CARDINAL'),

                    ('CDIA', {1:"1"}, 192000, 'cdia', narenco, None),

                    ('Cherry Blossom', {1: "1", 2: "2", 3: "3", 4: "4"},
                     10000000, 'cherryblossom', narenco, 'CHERRY BLOSSOM'),

                    ('Cougar', {
    1: "1-1", 2: "1-2", 3: "1-3", 4: "1-4", 5: "1-5", 6: "2-1",
    7: "2-2", 8: "2-3", 9: "2-4", 10: "2-5", 11: "2-6", 12: "3-1",
    13: "3-2", 14: "3-3", 15: "3-4", 16: "3-5", 17: "4-1", 18: "4-2",
    19: "4-3", 20: "4-4", 21: "4-5", 22: "5-1", 23: "5-2", 24: "5-3",
    25: "5-4", 26: "5-5", 27: "6-1", 28: "6-2", 29: "6-3", 30: "6-4", 31:"6-5"},
                     2670000, 'cougar', narenco, 'COUGAR'),

                    ('Conetoe', {
    1: "1-1", 2: "1-2", 3: "1-3", 4: "1-4",
    5: "2-1", 6: "2-2", 7: "2-3", 8: "2-4",
    9: "3-1", 10: "3-2", 11: "3-3", 12: "3-4",
    13: "4-1", 14: "4-2", 15: "4-3", 16: "4-4"},
                     5000000, 'conetoe1', soltage, None),

                    ('Duplin', {
    1: "C1", 2: "C2", 3: "C3", 4: "S1", 5: "S2", 6: "S3",
    7: "S4", 8: "S5", 9: "S6", 10: "S7", 11: "S8", 12: "S9",
    13: "S10", 14: "S11", 15: "S12", 16: "S13", 17: "S14", 18: "S15",
    19: "S16", 20: "S17", 21: "S18"},
                     5040000, 'duplin', soltage, None),

                    ('Elk', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "11", 12: "12", 13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18", 19: "19", 20: "20",
    21: "21", 22: "22", 23: "23", 24: "24", 25: "25", 26: "26", 27: "27", 28: "28", 29: "29", 30: "30",
    31: "31", 32: "32", 33: "33", 34: "34", 35: "35", 36: "36", 37: "37", 38: "38", 39: "39", 40: "40",
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
                    5380000, 'harrison', narenco, 'HARRISON'),

                    ('Hayes', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18",
    19: "19", 20: "20", 21: "21", 22: "22", 23: "23", 24: "24", 25: "25", 26: "26"},
                     3240000, 'hayes', narenco, 'HAYES'),

                    ('Hickory', {1:"1", 2:"2"}, 5000000, 'hickory', narenco, 'HICKORY'),
                    
                    ('Hickson', {
    1: "1-1", 2: "1-2", 3: "1-3", 4: "1-4", 5: "1-5", 6: "1-6",
    7: "1-7", 8: "1-8", 9: "1-9", 10: "1-10", 11: "1-11", 12: "1-12",
    13: "1-13", 14: "1-14", 15: "1-15", 16: "1-16"},
                     2000000, 'hickson', inv, None),

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
                     8000000, 'jefferson', inv, None),

                    ('Marshall', {
    1: "1.1", 2: "1.2", 3: "1.3", 4: "1.4", 5: "1.5", 6: "1.6",
    7: "1.7", 8: "1.8", 9: "1.9", 10: "1.10", 11: "1.11", 12: "1.12",
    13: "1.13", 14: "1.14", 15: "1.15", 16: "1.16"},
                    2000000, 'marshall', inv, None),

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
                    2000000, 'ogburn', inv, None),
                    
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
                    3000000, 'richmond', solrvr, 'RICHMOND'),
                    
                    ('Shorthorn', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "11", 12: "12", 13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18", 19: "19", 20: "20",
    21: "21", 22: "22", 23: "23", 24: "24", 25: "25", 26: "26", 27: "27", 28: "28", 29: "29", 30: "30",
    31: "31", 32: "32", 33: "33", 34: "34", 35: "35", 36: "36", 37: "37", 38: "38", 39: "39", 40: "40",
    41: "41", 42: "42", 43: "43", 44: "44", 45: "45", 46: "46", 47: "47", 48: "48", 49: "49", 50: "50",
    51: "51", 52: "52", 53: "53", 54: "54", 55: "55", 56: "56", 57: "57", 58: "58", 59: "59", 60: "60",
    61: "61", 62: "62", 63: "63", 64: "64", 65: "65", 66: "66", 67: "67", 68: "68", 69: "69", 70: "70",
    71: "71", 72: "72"},
                    9000000, 'shorthorn', solrvr, 'SHORTHORN'),

                    ('Sunflower', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "11", 12: "12", 13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18", 19: "19", 20: "20",
    21: "21", 22: "22", 23: "23", 24: "24", 25: "25", 26: "26", 27: "27", 28: "28", 29: "29", 30: "30",
    31: "31", 32: "32", 33: "33", 34: "34", 35: "35", 36: "36", 37: "37", 38: "38", 39: "39", 40: "40",
    41: "41", 42: "42", 43: "43", 44: "44", 45: "45", 46: "46", 47: "47", 48: "48", 49: "49", 50: "50",
    51: "51", 52: "52", 53: "53", 54: "54", 55: "55", 56: "56", 57: "57", 58: "58", 59: "59", 60: "60",
    61: "61", 62: "62", 63: "63", 64: "64", 65: "65", 66: "66", 67: "67", 68: "68", 69: "69", 70: "70",
    71: "71", 72: "72", 73: "73", 74: "74", 75: "75", 76: "76", 77: "77", 78: "78", 79: "79", 80: "80"},
                    10000000, 'sunflower', solrvr, 'SUNFLOWER'), 
                    
                    ('Tedder', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16"},
                    2000000, 'tedder', inv, None),

                    ('Thunderhead', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16"},
                    2000000, 'thunderhead', inv, None),
                    ('Upson', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18",
    19: "19", 20: "20", 21: "21", 22: "22", 23: "23", 24: "24"},
                    3000000, 'upson', solrvr, None), 
                    
                    ('Van Buren', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16", 17: "17"},
                    2000000, 'vanburen', inv, 'VAN BUREN'), 
                    
                    ('Warbler', {
    1: "A1", 2: "A2", 3: "A3", 4: "A4", 5: "A5", 6: "A6",
    7: "A7", 8: "A8", 9: "A9", 10: "A10", 11: "A11", 12: "A12",
    13: "A13", 14: "A14", 15: "A15", 16: "A16",
    17: "B17", 18: "B18", 19: "B19", 20: "B20", 21: "B21", 22: "B22",
    23: "B23", 24: "B24", 25: "B25", 26: "B26", 27: "B27", 28: "B28",
    29: "B29", 30: "B30", 31: "B31", 32: "B32"},
                    4000000, 'warbler', solrvr, 'WARBLER'),
                    
                    ('Washington', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "11", 12: "12", 13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18", 19: "19", 20: "20",
    21: "21", 22: "22", 23: "23", 24: "24", 25: "25", 26: "26", 27: "27", 28: "28", 29: "29", 30: "30",
    31: "31", 32: "32", 33: "33", 34: "34", 35: "35", 36: "36", 37: "37", 38: "38", 39: "39", 40: "40"},
                    5000000, 'washington', solrvr, None), 
                    
                    ('Wayne 1', {1: "1", 2: "2", 3: "3", 4: "4"}, 5000000, 'wayne1', soltage, None), 
                    
                    ('Wayne 2', {1: "1", 2: "2", 3: "3", 4: "4"}, 5000000, 'wayne2', soltage, None), 
                    
                    ('Wayne 3', {1: "1", 2: "2", 3: "3", 4: "4"}, 5000000, 'wayne3', soltage, None), 
                    
                    ('Wellons', {1: "1-1", 2: "1-2", 3: "2-1", 4: "2-2", 5:"3-1", 6:"3-2"}, 5000000, 'wellons', narenco, 'WELLONS'), 
                    
                    ('Whitehall', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16"},
                    2000000, 'whitehall', solrvr, 'WHITEHALL'), 
                    
                    ('Whitetail', {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "11", 12: "12", 13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18", 19: "19", 20: "20",
    21: "21", 22: "22", 23: "23", 24: "24", 25: "25", 26: "26", 27: "27", 28: "28", 29: "29", 30: "30",
    31: "31", 32: "32", 33: "33", 34: "34", 35: "35", 36: "36", 37: "37", 38: "38", 39: "39", 40: "40",
    41: "41", 42: "42", 43: "43", 44: "44", 45: "45", 46: "46", 47: "47", 48: "48", 49: "49", 50: "50",
    51: "51", 52: "52", 53: "53", 54: "54", 55: "55", 56: "56", 57: "57", 58: "58", 59: "59", 60: "60",
    61: "61", 62: "62", 63: "63", 64: "64", 65: "65", 66: "66", 67: "67", 68: "68", 69: "69", 70: "70",
    71: "71", 72: "72", 73: "73", 74: "74", 75: "75", 76: "76", 77: "77", 78: "78", 79: "79", 80: "80"},
                    10000000, 'whitetail', solrvr, None),
                    
                    ('Violet', {1:"1", 2:"2"}, 5000000, 'violet', narenco, 'VIOLET')]

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



sites_WObreakers = ['Bluebird', 'Bulloch 1A', 'Bulloch 1B', 'Conetoe', 'CDIA', 'Cougar', 'Duplin', 'Freightliner', 'Holly Swamp', 'PG', 'Richmond', 'Upson', 'Van Buren', 'Wayne 1', 'Wayne 2', 'Wayne 3', 'Wellons']
#I Don't Need both, Don't know why I still have both, but I do.
has_breaker = ['Bishopville II', 'Cardinal', 'Cherry Blossom', 'Elk', 'Gray Fox', 'Harding', 'Harrison', 'Hayes', 'Hickory', 'Hickson', 'Jefferson', 'Marshall', 'McLean', 'Ogburn', 
               'Shorthorn', 'Sunflower', 'Tedder', 'Thunderhead', 'Warbler', 'Washington', 'Whitehall', 'Whitetail', 'Violet']

all_CBs = []


normal_numbering = ['Bluebird', 'Cardinal', 'Cherry Blossom', 'Cougar', 'Harrison', 'Hayes', 'Hickory', 'Violet', 'HICKSON',
                    'JEFFERSON', 'Marshall', 'OGBURN', 'Tedder', 'Thunderhead', 'Van Buren', 'Bulloch 1A', 'Bulloch 1B', 'Elk', 'Duplin',
                    'Harding', 'Mclean', 'Richmond Cadle', 'Shorthorn', 'Sunflower', 'Upson', 'Warbler', 'Washington', 'Whitehall', 'Whitetail',
                    'Conetoe 1', 'Wayne I', 'Wayne II', 'Wayne III', 'Freight Line', 'Holly Swamp', 'PG']

number20set = ['Gray Fox']
number9set = ['BISHOPVILLE']
number2set = ['Wellons Farm']

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
    if name != 'CDIA':
        if invnum > 74:
            span_col = 6
        else:
            span_col = 3

        globals()[f'{varname}invsLabel'] = Button(custid, text=name, command=lambda name=varname: open_wo_tracking(name), bg=main_color, font=("Tk_defaultFont", 12, 'bold'), cursor='hand2')
        globals()[f'{varname}invsLabel'].grid(row= 0, column= ro*3, columnspan= span_col, sticky='ew')
    for num in range(1, invnum+1):
        column_offset = 0 if num <= 74 else 3  # Adjust column for inverters over 74
        row_offset = num if num <= 74 else num - 74  # Reset row for inverters over 74
        if name != 'CDIA':
            if num in invdict:  # Check if the key exists in the dictionary
                inv_val = invdict[num]
            else:
                inv_val = str(num)

            globals()[f'{varname}inv{inv_val}cbval'] = IntVar()
            all_CBs.append(globals()[f'{varname}inv{inv_val}cbval'])
            globals()[f'{varname}inv{inv_val}cb'] = Checkbutton(custid, text=str(inv_val), variable=globals()[f'{varname}inv{inv_val}cbval'], cursor='hand2')
            globals()[f'{varname}inv{inv_val}cb'].grid(row= row_offset, column= (ro*3)+column_offset)

            globals()[f'{varname}inv{num}WOLabel'] = Label(custid, text='⬜') #intial Setup of WO Placeholder. 
            globals()[f'{varname}inv{num}WOLabel'].grid(row= row_offset, column= (ro*3)+1+column_offset)

            globals()[f'{varname}invup{num}cbval'] = IntVar()
            all_CBs.append(globals()[f'{varname}invup{num}cbval'])
            globals()[f'{varname}invup{num}cb'] = Checkbutton(custid, variable=globals()[f'{varname}invup{num}cbval'], cursor='hand2')
            globals()[f'{varname}invup{num}cb'].grid(row= row_offset, column= (ro*3)+2+column_offset)

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
            messagebox.showinfo(title="Comm Outage", parent=alertW, message="Call Conetoe Utilities:\nWO 29980, 35307\n757-857-2888\nID: 710R41")
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
    save_cb_state()
    update_data_start = ty.perf_counter()

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
                messagebox.showwarning(parent= alertW, title=f"{name}, POA Comms Error", message=f"{name} lost comms with POA sensor at {strtime_poa}")
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
                    if any(meter_data[f'{name} Meter Data'][i][j] == 0 for i in range(meter_pulls) for j in range(3, 6)):
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
                                        messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Inverter Offline, Good DC Voltage | {online_last}")
                                else:
                                    online_last = last_online(name, r, duplin_except)
                                    messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Inverter Offline, Good DC Voltage | {online_last}")

                            globals()[f'{var_name}meterkWLabel'].config(text="X✓", bg='orange')
                            globals()[f'{var_name}Label'].config(bg='orange')

                        else:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 100)) and cbval == 0 and master_cb_skips_INV_check:
                                var_key = f'{var_name}statusLabel'
                                if var_key in globals():
                                    if globals()[var_key].cget("bg") == 'green':
                                        online_last = last_online(name, r, duplin_except)
                                        messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Inverter Offline, Bad DC Voltage | {online_last}")
                                else:
                                    online_last = last_online(name, r, duplin_except)
                                    messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Inverter Offline, Bad DC Voltage | {online_last}")

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
                                messagebox.showerror(parent= alertW, title=f"{name}, Inverter Comms Loss", message=f"INV Comms lost {inv_Ltime} with Inverter {r} at {name}! Please Investigate!")
                        else:
                            messagebox.showerror(parent= alertW, title=f"{name}, Inverter Comms Loss", message=f"INV Comms lost {inv_Ltime} with Inverter {r} at {name}! Please Investigate!")

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
                                        messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Inverter {inv_val} Offline, Good DC Voltage | {online_last}")
                                else:
                                    online_last = last_online(name, inv_num, duplin_except)
                                    messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Inverter {inv_val} Offline, Good DC Voltage | {online_last}")

                            globals()[f'{var_name}inv{inv_val}cb'].config(bg='orange')
                        else:
                            if current_config not in ["orange", "red"] and ((poa > 250 and begin) or (h_tm_now >= 10 and poa > 100)) and cbval == 0 and master_cb_skips_INV_check:
                                var_key = f'{var_name}statusLabel'
                                if var_key in globals():
                                    if globals()[var_key].cget("bg") == 'green':
                                        online_last = last_online(name, inv_num, duplin_except)
                                        messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Inverter {inv_val} Offline, Bad DC Voltage | {online_last}")
                                else:
                                    online_last = last_online(name, inv_num, duplin_except)
                                    messagebox.showwarning(title=f"{name}", parent= alertW, message= f"Inverter {inv_val} Offline, Bad DC Voltage | {online_last}")

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
                                messagebox.showerror(parent= alertW, title=f"{name}, Inverter Comms Loss", message=f"INV Comms lost {inv_Ltime} with Inverter {inv_val} at {name}! Please Investigate!")
                        else:
                            messagebox.showerror(parent= alertW, title=f"{name}, Inverter Comms Loss", message=f"INV Comms lost {inv_Ltime} with Inverter {inv_val} at {name}! Please Investigate!")
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

                if name == "Wellons":
                    dif = 9
                else:
                    dif = 5

                if meterdataVA < val and meterdataVB < val and meterdataVC < val:
                    meterVstatus= '❌❌'
                    meterVstatuscolor= 'red'
                    if meterVconfig != '❌❌':
                        online = meter_last_online(name)
                        messagebox.showerror(parent=alertW, title= f"{name} Meter", message= f"Loss of Utility Voltage or Lost Comms with Meter. {online}")
                elif meterdataVA < val:
                    meterVstatus= 'X✓✓'
                    meterVstatuscolor= 'orange'
                    if meterVconfig != 'X✓✓':
                        messagebox.showerror(parent=alertW, title= f"{name} Meter", message= f"Loss of Utility Phase A Voltage or Lost Comms with Meter.")
                elif meterdataVB < val:
                    meterVstatus= '✓X✓'
                    meterVstatuscolor= 'orange'
                    if meterVconfig != '✓X✓':
                        messagebox.showerror(parent=alertW, title= f"{name} Meter", message= f"Loss of Utility Phase B Voltage or Lost Comms with Meter.")
                elif meterdataVC < val:
                    meterVstatus= '✓✓X'
                    meterVstatuscolor= 'orange'
                    if meterVconfig != '✓✓X':
                        messagebox.showerror(parent=alertW, title= f"{name} Meter", message= f"Loss of Utility Phase C Voltage or Lost Comms with Meter.")
                elif percent_difference_AB >= dif or percent_difference_AC >= dif or percent_difference_BC >= dif:
                    meterVstatus= '???'
                    meterVstatuscolor= 'orange'
                    if meterVconfig != '???':
                        messagebox.showerror(parent=alertW, title= f"{name} Meter", message= f"Voltage Imbalance greater than {dif}%")
                else:
                    meterVstatus= '✓✓✓'
                    meterVstatuscolor= 'green'
                    if meterVconfig not in  ['✓✓✓', 'V']:
                        messagebox.showinfo(parent=alertW, title=f"{name} Meter", message= "Utility Voltage Restored!!! Close the Breaker")

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
                            messagebox.showerror(parent= alertW, title=f"{name}, Power Loss", message=f"Site: {name}\nMeter Production: {round(meterdataKW, 2)}\nMeter Amps:\nA: {round(meterdataavgAA, 2)}\nB: {round(meterdataavgAB, 2)}\nC: {round(meterdataavgAC, 2)}\n{online}")
                
                    elif meterdataAC or meterdataAB or meterdataKW < 2: #This is a continuation of the above 'Juke' The Elif below is yet another continuation as Vanburen gets trapped by the very first if statement
                        meterkWstatus= '❌❌'
                        meterkWstatuscolor= 'red'
                        meterlbl = globals()[f'{var_name}meterkWLabel'].cget('bg')
                        if meterlbl != 'red' and master_cb_skips_INV_check and poa > 10:
                            online = meter_last_online(name)
                            messagebox.showerror(parent= alertW, title=f"{name}, Meter Power Loss", message=f"Site: {name}\nMeter Production: {round(meterdataKW, 2)}\nMeter Amps:\nA: {round(meterdataavgAA, 2)}\nB: {round(meterdataavgAB, 2)}\nC: {round(meterdataavgAC, 2)}\n{online}")
                    elif meterdatakWM < total_invkW * mvi_percent and name != "CDIA": #Less than XX% of total INV's
                        print(f'{name}:  {meterdatakWM} | {total_invkW*mvi_percent} ~ {mvi_percent*100}% | {total_invkW}')
                        print(allinv_kW)
                        if poa != 9999:
                            if globals()[f'{var_name}meterkWLabel'].cget('text') != '???' and poa >= 250:
                                messagebox.showwarning(parent= alertW, title=name, message=f'{name} experiencing Meter vs. Inv kW discrepancy\nPlease investigate the meter and look for Phase Issue')
                        elif globals()[f'{var_name}meterkWLabel'].cget('text') != '???' and 9 <= h_tm_now < 15:
                            messagebox.showwarning(parent= alertW, title=name, message=f'{name} experiencing Meter vs. Inv kW discrepancy\nPlease investigate the meter and look for Phase Issue')
                        meterkWstatus= '???'
                        meterkWstatuscolor= 'orange'

                elif meterdatakWM < total_invkW * mvi_percent and name != "CDIA": #Less than XX% of total INV's
                    #print(f'{name}:  {meterdatakWM} | {total_invkW*mvi_percent} ~ {mvi_percent*100}% | {total_invkW}')
                    #print(allinv_kW)
                    if poa != 9999:
                        if globals()[f'{var_name}meterkWLabel'].cget('text') != '???' and poa >= 250: #Might should change this so that we check the INV groups poa values for each data entry. 
                            messagebox.showwarning(parent= alertW, title=name, message=f'{name} experiencing Meter vs. Inv kW discrepancy\nPlease investigate the meter and look for Phase Issue')
                    elif globals()[f'{var_name}meterkWLabel'].cget('text') != '???' and 9 <= h_tm_now < 15:
                        messagebox.showwarning(parent= alertW, title=name, message=f'{name} experiencing Meter vs. Inv kW discrepancy\nPlease investigate the meter and look for Phase Issue')
                    meterkWstatus= '???'
                    meterkWstatuscolor= 'orange'
                        
                else:
                    meterkWstatus= '✓✓✓'
                    meterkWstatuscolor= 'green'
                #Below we update the GUI with the above defined text and color
                globals()[f'{var_name}meterkWLabel'].config(text= meterkWstatus, bg= meterkWstatuscolor)
                
                #PVSYST Ratio Update
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


            else:
                meterlbl = globals()[f'{var_name}meterkWLabel'].cget('bg')
                if meterlbl != 'pink' and master_cb_skips_INV_check:
                    messagebox.showerror(parent= alertW, title=f"{name}, Meter Comms Loss", message=f"Meter Comms lost {meter_Ltime} with the Meter at {name}! Please Investigate!")
                globals()[f'{var_name}meterkWLabel'].config(bg='pink')
                globals()[f'{var_name}meterVLabel'].config(bg='pink')
                globals()[f'{var_name}meterRatioLabel'].config(bg='pink')
            
    underperformance_data_update() #Inverter Comparison Type Underperformance Check
    #conetoe_offline()


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
        name, invdict, metermax, var_name, custid, pvsyst_name = site_info
        inverters = len(invdict)
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

    notes_button.config(state=NORMAL)

def pysyst_connect():
    global cursor_p, connect_pvsystdb
    #Connect to PV Syst DB for Performance expectations
    pvsyst_db = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=G:\Shared drives\O&M\NCC Automations\Performance Reporting\PVsyst (Josephs Edits).accdb;'
    connect_pvsystdb = pyodbc.connect(pvsyst_db)
    cursor_p = connect_pvsystdb.cursor()

def pvsyst_est(meterval, poa_val, pvsyst_name):
    if pvsyst_name == None:
        return (0,0,0)
    if poa_val == 9999:
        return (0,0,0)



    pysyst_connect()
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
    connect_pvsystdb.close()
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
    dateend = underperf_range.get()



    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=dateend)
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

            if table_name == "Duplin String INV 17 Data":
                ic(df)

            underperformance_data[table_name] = df
    


    grouped_data = {}
    for site, invdict, metermax, var, custid, pvsyst_name in master_List_Sites:
        inv_count = len(invdict)
        if site == "CDIA":
            continue
        # Initialize a dictionary to store dataframes for each group for the current site
        site_grouped_data = {}
        for i in range(1, inv_count + 1):
            if site == "Duplin":
                if i <= 3:
                    strVcent = 'Central'
                    num = i
                else:
                    strVcent = 'String'
                    num = i - 3
                table_name = f'{site} {strVcent} INV {i} Data'
                df = underperformance_data.get(table_name, pd.DataFrame(columns=['Timestamp', 'Watts']))
                df.rename(columns={'Watts': f'{var}_{strVcent}_INV_{num}_Watts'}, inplace=True)
            else:
                table_name = f'{site} INV {i} Data'
                df = underperformance_data.get(table_name, pd.DataFrame(columns=['Timestamp', 'Watts']))
                df.rename(columns={'Watts': f'{var}_INV_{i}_Watts'}, inplace=True)

            # Determine the group for the current inverter
            found_group = False
            if site in site_INV_groups:
                for group_name, group_cols in site_INV_groups[site].items():
                    if f'{var}_INV_{i}_Watts' in [col for col in group_cols]:
                        if group_name not in site_grouped_data:
                            site_grouped_data[group_name] = []
                        site_grouped_data[group_name].append(df)
                        found_group = True
                        break
            if not found_group:
                if site not in site_grouped_data:
                    site_grouped_data[site] = []
                site_grouped_data[site].append(df)
            #Add Site Data to Main Data Dictionary    
            grouped_data[site] = site_grouped_data
        # Concatenate dataframes for each group and store them
        for site, dfs in grouped_data.items():
            for inverter_group, watts_data in dfs.items():
                if dfs:
                    combined_df = pd.concat(watts_data, ignore_index=True)
                    # Drop rows where *any* column containing 'Watts' is 0
                    cols_to_check = [col for col in combined_df.columns if 'Watts' in col]
                    combined_df = combined_df[~(combined_df[cols_to_check] < 1).any(axis=1)]
                    if site == 'Duplin':
                        ic(combined_df)

                    # Calculate and assign the mean for each 'Watts' column
                    for col in cols_to_check:
                        mean_value = combined_df[col].mean()
                        # Assign the mean to the appropriate global variable
                        if site == "Duplin":
                            if "Central" in col:
                                replace1 = col.replace(f'duplin_Central_INV_', '')
                                inv_number = replace1.replace('_Watts', '')
                                globals()[f'duplininv{inv_number}daykwavg'] = mean_value
                            elif "String" in col:
                                replace1 = col.replace(f'duplin_String_INV_', '')
                                inv_number = int(replace1.replace('_Watts', ''))
                                globals()[f'duplinsinv{inv_number}daykwavg'] = mean_value
                            
                        else:
                            replace1 = col.replace(f'{var}_INV_', '')
                            inv_number = replace1.replace('_Watts', '')
                            globals()[f'{var}inv{inv_number}daykwavg'] = mean_value

    
    bluebirddaykwList = [(bluebirdinv1daykwavg, bluebirdinvup1cb), (bluebirdinv2daykwavg, bluebirdinvup2cb), (bluebirdinv3daykwavg, bluebirdinvup3cb), (bluebirdinv4daykwavg, bluebirdinvup4cb), (bluebirdinv5daykwavg, bluebirdinvup5cb), (bluebirdinv6daykwavg, bluebirdinvup6cb), (bluebirdinv7daykwavg, bluebirdinvup7cb), (bluebirdinv8daykwavg, bluebirdinvup8cb), (bluebirdinv9daykwavg, bluebirdinvup9cb), (bluebirdinv10daykwavg, bluebirdinvup10cb), (bluebirdinv11daykwavg, bluebirdinvup11cb), (bluebirdinv12daykwavg, bluebirdinvup12cb), (bluebirdinv13daykwavg, bluebirdinvup13cb), (bluebirdinv14daykwavg, bluebirdinvup14cb), (bluebirdinv15daykwavg, bluebirdinvup15cb), (bluebirdinv16daykwavg, bluebirdinvup16cb), (bluebirdinv17daykwavg, bluebirdinvup17cb), (bluebirdinv18daykwavg, bluebirdinvup18cb), (bluebirdinv19daykwavg, bluebirdinvup19cb), (bluebirdinv20daykwavg, bluebirdinvup20cb), (bluebirdinv21daykwavg, bluebirdinvup21cb), (bluebirdinv22daykwavg, bluebirdinvup22cb), (bluebirdinv23daykwavg, bluebirdinvup23cb), (bluebirdinv24daykwavg, bluebirdinvup24cb)]
    cardinal96daykwList = [(cardinalinv1daykwavg, cardinalinvup1cb), (cardinalinv2daykwavg, cardinalinvup2cb), (cardinalinv3daykwavg, cardinalinvup3cb), (cardinalinv4daykwavg, cardinalinvup4cb), (cardinalinv5daykwavg, cardinalinvup5cb), (cardinalinv6daykwavg, cardinalinvup6cb), (cardinalinv7daykwavg, cardinalinvup7cb), (cardinalinv22daykwavg, cardinalinvup22cb), (cardinalinv23daykwavg, cardinalinvup23cb), (cardinalinv24daykwavg, cardinalinvup24cb), (cardinalinv25daykwavg, cardinalinvup25cb), (cardinalinv26daykwavg, cardinalinvup26cb), (cardinalinv27daykwavg, cardinalinvup27cb), (cardinalinv28daykwavg, cardinalinvup28cb), (cardinalinv43daykwavg, cardinalinvup43cb), (cardinalinv44daykwavg, cardinalinvup44cb), (cardinalinv45daykwavg, cardinalinvup45cb), (cardinalinv46daykwavg, cardinalinvup46cb), (cardinalinv47daykwavg, cardinalinvup47cb)]
    cardinal952daykwList = [(cardinalinv8daykwavg, cardinalinvup8cb), (cardinalinv9daykwavg, cardinalinvup9cb), (cardinalinv10daykwavg, cardinalinvup10cb), (cardinalinv11daykwavg, cardinalinvup11cb), (cardinalinv12daykwavg, cardinalinvup12cb), (cardinalinv13daykwavg, cardinalinvup13cb), (cardinalinv14daykwavg, cardinalinvup14cb), (cardinalinv29daykwavg, cardinalinvup29cb), (cardinalinv30daykwavg, cardinalinvup30cb), (cardinalinv31daykwavg, cardinalinvup31cb), (cardinalinv32daykwavg, cardinalinvup32cb), (cardinalinv33daykwavg, cardinalinvup33cb), (cardinalinv34daykwavg, cardinalinvup34cb), (cardinalinv35daykwavg, cardinalinvup35cb), (cardinalinv48daykwavg, cardinalinvup48cb), (cardinalinv49daykwavg, cardinalinvup49cb), (cardinalinv50daykwavg, cardinalinvup50cb), (cardinalinv51daykwavg, cardinalinvup51cb), (cardinalinv52daykwavg, cardinalinvup52cb), (cardinalinv53daykwavg, cardinalinvup53cb)]
    cardinal944daykwList = [(cardinalinv15daykwavg, cardinalinvup15cb), (cardinalinv16daykwavg, cardinalinvup16cb), (cardinalinv17daykwavg, cardinalinvup17cb), (cardinalinv18daykwavg, cardinalinvup18cb), (cardinalinv19daykwavg, cardinalinvup19cb), (cardinalinv20daykwavg, cardinalinvup20cb), (cardinalinv21daykwavg, cardinalinvup21cb), (cardinalinv36daykwavg, cardinalinvup36cb), (cardinalinv37daykwavg, cardinalinvup37cb), (cardinalinv38daykwavg, cardinalinvup38cb), (cardinalinv39daykwavg, cardinalinvup39cb), (cardinalinv40daykwavg, cardinalinvup40cb), (cardinalinv41daykwavg, cardinalinvup41cb), (cardinalinv42daykwavg, cardinalinvup42cb), (cardinalinv54daykwavg, cardinalinvup54cb), (cardinalinv55daykwavg, cardinalinvup55cb), (cardinalinv56daykwavg, cardinalinvup56cb), (cardinalinv57daykwavg, cardinalinvup57cb), (cardinalinv58daykwavg, cardinalinvup58cb), (cardinalinv59daykwavg, cardinalinvup59cb)]
    cherryblossomdaykwList = [(cherryblossominv1daykwavg, cherryblossominvup1cb), (cherryblossominv2daykwavg, cherryblossominvup2cb), (cherryblossominv3daykwavg, cherryblossominvup3cb), (cherryblossominv4daykwavg, cherryblossominvup4cb)]
    harrisondaykwList = [(harrisoninv2daykwavg, harrisoninvup2cb), (harrisoninv3daykwavg, harrisoninvup3cb), (harrisoninv4daykwavg, harrisoninvup4cb), (harrisoninv5daykwavg, harrisoninvup5cb), (harrisoninv6daykwavg, harrisoninvup6cb), (harrisoninv7daykwavg, harrisoninvup7cb), (harrisoninv9daykwavg, harrisoninvup9cb), (harrisoninv11daykwavg, harrisoninvup11cb), (harrisoninv12daykwavg, harrisoninvup12cb), (harrisoninv13daykwavg, harrisoninvup13cb), (harrisoninv14daykwavg, harrisoninvup14cb), (harrisoninv15daykwavg, harrisoninvup15cb), (harrisoninv16daykwavg, harrisoninvup16cb), (harrisoninv18daykwavg, harrisoninvup18cb), (harrisoninv19daykwavg, harrisoninvup19cb), (harrisoninv20daykwavg, harrisoninvup20cb), (harrisoninv22daykwavg, harrisoninvup22cb), (harrisoninv23daykwavg, harrisoninvup23cb), (harrisoninv24daykwavg, harrisoninvup24cb), (harrisoninv25daykwavg, harrisoninvup25cb), (harrisoninv26daykwavg, harrisoninvup26cb), (harrisoninv27daykwavg, harrisoninvup27cb), (harrisoninv28daykwavg, harrisoninvup28cb), (harrisoninv31daykwavg, harrisoninvup31cb), (harrisoninv32daykwavg, harrisoninvup32cb), (harrisoninv33daykwavg, harrisoninvup33cb), (harrisoninv34daykwavg, harrisoninvup34cb), (harrisoninv35daykwavg, harrisoninvup35cb), (harrisoninv36daykwavg, harrisoninvup36cb), (harrisoninv37daykwavg, harrisoninvup37cb), (harrisoninv38daykwavg, harrisoninvup38cb), (harrisoninv39daykwavg, harrisoninvup39cb), (harrisoninv42daykwavg, harrisoninvup42cb), (harrisoninv43daykwavg, harrisoninvup43cb)]
    harrison92daykwList = [(harrisoninv1daykwavg, harrisoninvup1cb), (harrisoninv8daykwavg, harrisoninvup8cb), (harrisoninv10daykwavg, harrisoninvup10cb), (harrisoninv17daykwavg, harrisoninvup17cb), (harrisoninv21daykwavg, harrisoninvup21cb), (harrisoninv29daykwavg, harrisoninvup29cb), (harrisoninv30daykwavg, harrisoninvup30cb), (harrisoninv40daykwavg, harrisoninvup40cb), (harrisoninv41daykwavg, harrisoninvup41cb)]
    hayesdaykwList = [(hayesinv1daykwavg, hayesinvup1cb), (hayesinv2daykwavg, hayesinvup2cb), (hayesinv3daykwavg, hayesinvup3cb), (hayesinv4daykwavg, hayesinvup4cb), (hayesinv5daykwavg, hayesinvup5cb), (hayesinv6daykwavg, hayesinvup6cb), (hayesinv7daykwavg, hayesinvup7cb), (hayesinv8daykwavg, hayesinvup8cb), (hayesinv9daykwavg, hayesinvup9cb), (hayesinv10daykwavg, hayesinvup10cb), (hayesinv11daykwavg, hayesinvup11cb), (hayesinv12daykwavg, hayesinvup12cb), (hayesinv13daykwavg, hayesinvup13cb), (hayesinv14daykwavg, hayesinvup14cb), (hayesinv15daykwavg, hayesinvup15cb), (hayesinv16daykwavg, hayesinvup16cb), (hayesinv17daykwavg, hayesinvup17cb), (hayesinv19daykwavg, hayesinvup19cb), (hayesinv20daykwavg, hayesinvup20cb), (hayesinv21daykwavg, hayesinvup21cb), (hayesinv23daykwavg, hayesinvup23cb), (hayesinv24daykwavg, hayesinvup24cb), (hayesinv25daykwavg, hayesinvup25cb), (hayesinv26daykwavg, hayesinvup26cb)]
    hayes96daykwList = [(hayesinv22daykwavg, hayesinvup22cb), (hayesinv18daykwavg, hayesinvup18cb)]
    hickorydaykwList = [(hickoryinv1daykwavg, hickoryinvup1cb), (hickoryinv2daykwavg, hickoryinvup2cb)]
    vanburendaykwList = [(vanbureninv7daykwavg, vanbureninvup7cb), (vanbureninv8daykwavg, vanbureninvup8cb), (vanbureninv9daykwavg, vanbureninvup9cb), (vanbureninv10daykwavg, vanbureninvup10cb), (vanbureninv11daykwavg, vanbureninvup11cb), (vanbureninv12daykwavg, vanbureninvup12cb), (vanbureninv13daykwavg, vanbureninvup13cb), (vanbureninv14daykwavg, vanbureninvup14cb), (vanbureninv15daykwavg, vanbureninvup15cb), (vanbureninv16daykwavg, vanbureninvup16cb), (vanbureninv17daykwavg, vanbureninvup17cb)]
    vanburen93daykwList = [(vanbureninv1daykwavg, vanbureninvup1cb), (vanbureninv2daykwavg, vanbureninvup2cb), (vanbureninv3daykwavg, vanbureninvup3cb), (vanbureninv4daykwavg, vanbureninvup4cb), (vanbureninv5daykwavg, vanbureninvup5cb), (vanbureninv6daykwavg, vanbureninvup6cb)]
    violetdaykwList = [(violetinv1daykwavg, violetinvup1cb), (violetinv2daykwavg, violetinvup2cb)]
    wellonsdaykwList = [(wellonsinv1daykwavg, wellonsinvup1cb), (wellonsinv2daykwavg, wellonsinvup2cb), (wellonsinv3daykwavg, wellonsinvup3cb), (wellonsinv4daykwavg, wellonsinvup4cb), (wellonsinv5daykwavg, wellonsinvup5cb), (wellonsinv6daykwavg, wellonsinvup6cb)]
    bishopvilleIIdaykwList = [(bishopvilleIIinv6daykwavg, bishopvilleIIinvup6cb), (bishopvilleIIinv7daykwavg, bishopvilleIIinvup7cb), (bishopvilleIIinv8daykwavg, bishopvilleIIinvup8cb), (bishopvilleIIinv9daykwavg, bishopvilleIIinvup9cb), (bishopvilleIIinv10daykwavg, bishopvilleIIinvup10cb), (bishopvilleIIinv13daykwavg, bishopvilleIIinvup13cb),  (bishopvilleIIinv15daykwavg, bishopvilleIIinvup15cb),  (bishopvilleIIinv19daykwavg, bishopvilleIIinvup19cb), (bishopvilleIIinv20daykwavg, bishopvilleIIinvup20cb), (bishopvilleIIinv21daykwavg, bishopvilleIIinvup21cb), (bishopvilleIIinv22daykwavg, bishopvilleIIinvup22cb), (bishopvilleIIinv23daykwavg, bishopvilleIIinvup23cb),  (bishopvilleIIinv26daykwavg, bishopvilleIIinvup26cb), (bishopvilleIIinv27daykwavg, bishopvilleIIinvup27cb), (bishopvilleIIinv28daykwavg, bishopvilleIIinvup28cb), (bishopvilleIIinv29daykwavg, bishopvilleIIinvup29cb), (bishopvilleIIinv30daykwavg, bishopvilleIIinvup30cb), (bishopvilleIIinv32daykwavg, bishopvilleIIinvup32cb),  (bishopvilleIIinv34daykwavg, bishopvilleIIinvup34cb)]
    bishopvilleII34strdaykwList = [(bishopvilleIIinv1daykwavg, bishopvilleIIinvup1cb), (bishopvilleIIinv2daykwavg, bishopvilleIIinvup2cb), (bishopvilleIIinv3daykwavg, bishopvilleIIinvup3cb), (bishopvilleIIinv4daykwavg, bishopvilleIIinvup4cb), (bishopvilleIIinv5daykwavg, bishopvilleIIinvup5cb), (bishopvilleIIinv11daykwavg, bishopvilleIIinvup11cb), (bishopvilleIIinv12daykwavg, bishopvilleIIinvup12cb), (bishopvilleIIinv14daykwavg, bishopvilleIIinvup14cb), (bishopvilleIIinv16daykwavg, bishopvilleIIinvup16cb), (bishopvilleIIinv17daykwavg, bishopvilleIIinvup17cb), (bishopvilleIIinv18daykwavg, bishopvilleIIinvup18cb), (bishopvilleIIinv31daykwavg, bishopvilleIIinvup31cb), (bishopvilleIIinv33daykwavg, bishopvilleIIinvup33cb), (bishopvilleIIinv35daykwavg, bishopvilleIIinvup35cb), (bishopvilleIIinv36daykwavg, bishopvilleIIinvup36cb)]
    bishopvilleII36strdaykwList = [(bishopvilleIIinv24daykwavg, bishopvilleIIinvup24cb), (bishopvilleIIinv25daykwavg, bishopvilleIIinvup25cb)]
    hicksondaykwList = [(hicksoninv7daykwavg, hicksoninvup7cb), (hicksoninv8daykwavg, hicksoninvup8cb), (hicksoninv9daykwavg, hicksoninvup9cb), (hicksoninv12daykwavg, hicksoninvup12cb), (hicksoninv13daykwavg, hicksoninvup13cb), (hicksoninv14daykwavg, hicksoninvup14cb), (hicksoninv15daykwavg, hicksoninvup15cb), (hicksoninv16daykwavg, hicksoninvup16cb)]
    hickson17strdaykwList = [(hicksoninv1daykwavg, hicksoninvup1cb), (hicksoninv2daykwavg, hicksoninvup2cb), (hicksoninv3daykwavg, hicksoninvup3cb), (hicksoninv4daykwavg, hicksoninvup4cb), (hicksoninv5daykwavg, hicksoninvup5cb), (hicksoninv6daykwavg, hicksoninvup6cb), (hicksoninv10daykwavg, hicksoninvup10cb), (hicksoninv11daykwavg, hicksoninvup11cb)]
    jeffersondaykwList = [(jeffersoninv5daykwavg, jeffersoninvup5cb),  (jeffersoninv7daykwavg, jeffersoninvup7cb), (jeffersoninv8daykwavg, jeffersoninvup8cb), (jeffersoninv9daykwavg, jeffersoninvup9cb), (jeffersoninv10daykwavg, jeffersoninvup10cb), (jeffersoninv11daykwavg, jeffersoninvup11cb), (jeffersoninv12daykwavg, jeffersoninvup12cb), (jeffersoninv15daykwavg, jeffersoninvup15cb), (jeffersoninv16daykwavg, jeffersoninvup16cb), (jeffersoninv19daykwavg, jeffersoninvup19cb), (jeffersoninv24daykwavg, jeffersoninvup24cb), (jeffersoninv26daykwavg, jeffersoninvup26cb), (jeffersoninv27daykwavg, jeffersoninvup27cb), (jeffersoninv28daykwavg, jeffersoninvup28cb), (jeffersoninv29daykwavg, jeffersoninvup29cb), (jeffersoninv30daykwavg, jeffersoninvup30cb), (jeffersoninv31daykwavg, jeffersoninvup31cb), (jeffersoninv32daykwavg, jeffersoninvup32cb), (jeffersoninv33daykwavg, jeffersoninvup33cb), (jeffersoninv34daykwavg, jeffersoninvup34cb), (jeffersoninv35daykwavg, jeffersoninvup35cb), (jeffersoninv36daykwavg, jeffersoninvup36cb), (jeffersoninv37daykwavg, jeffersoninvup37cb), (jeffersoninv38daykwavg, jeffersoninvup38cb), (jeffersoninv39daykwavg, jeffersoninvup39cb),  (jeffersoninv48daykwavg, jeffersoninvup48cb), (jeffersoninv57daykwavg, jeffersoninvup57cb), (jeffersoninv58daykwavg, jeffersoninvup58cb), (jeffersoninv59daykwavg, jeffersoninvup59cb), (jeffersoninv60daykwavg, jeffersoninvup60cb), (jeffersoninv61daykwavg, jeffersoninvup61cb), (jeffersoninv62daykwavg, jeffersoninvup62cb), (jeffersoninv63daykwavg, jeffersoninvup63cb), (jeffersoninv64daykwavg, jeffersoninvup64cb)]
    jefferson18strdaykwList = [(jeffersoninv1daykwavg, jeffersoninvup1cb), (jeffersoninv2daykwavg, jeffersoninvup2cb), (jeffersoninv3daykwavg, jeffersoninvup3cb), (jeffersoninv4daykwavg, jeffersoninvup4cb), (jeffersoninv6daykwavg, jeffersoninvup6cb), (jeffersoninv13daykwavg, jeffersoninvup13cb), (jeffersoninv14daykwavg, jeffersoninvup14cb), (jeffersoninv17daykwavg, jeffersoninvup17cb), (jeffersoninv18daykwavg, jeffersoninvup18cb), (jeffersoninv20daykwavg, jeffersoninvup20cb), (jeffersoninv21daykwavg, jeffersoninvup21cb), (jeffersoninv22daykwavg, jeffersoninvup22cb), (jeffersoninv23daykwavg, jeffersoninvup23cb), (jeffersoninv25daykwavg, jeffersoninvup25cb), (jeffersoninv40daykwavg, jeffersoninvup40cb), (jeffersoninv41daykwavg, jeffersoninvup41cb), (jeffersoninv42daykwavg, jeffersoninvup42cb), (jeffersoninv43daykwavg, jeffersoninvup43cb), (jeffersoninv44daykwavg, jeffersoninvup44cb),  (jeffersoninv45daykwavg, jeffersoninvup45cb), (jeffersoninv46daykwavg, jeffersoninvup46cb), (jeffersoninv47daykwavg, jeffersoninvup47cb), (jeffersoninv49daykwavg, jeffersoninvup49cb), (jeffersoninv50daykwavg, jeffersoninvup50cb), (jeffersoninv51daykwavg, jeffersoninvup51cb), (jeffersoninv52daykwavg, jeffersoninvup52cb), (jeffersoninv53daykwavg, jeffersoninvup53cb), (jeffersoninv54daykwavg, jeffersoninvup54cb), (jeffersoninv55daykwavg, jeffersoninvup55cb), (jeffersoninv56daykwavg, jeffersoninvup56cb)]
    marshalldaykwList = [(marshallinv1daykwavg, marshallinvup1cb), (marshallinv2daykwavg, marshallinvup2cb), (marshallinv3daykwavg, marshallinvup3cb), (marshallinv4daykwavg, marshallinvup4cb), (marshallinv5daykwavg, marshallinvup5cb), (marshallinv6daykwavg, marshallinvup6cb), (marshallinv7daykwavg, marshallinvup7cb), (marshallinv8daykwavg, marshallinvup8cb), (marshallinv9daykwavg, marshallinvup9cb), (marshallinv10daykwavg, marshallinvup10cb), (marshallinv11daykwavg, marshallinvup11cb), (marshallinv12daykwavg, marshallinvup12cb), (marshallinv13daykwavg, marshallinvup13cb), (marshallinv14daykwavg, marshallinvup14cb), (marshallinv15daykwavg, marshallinvup15cb), (marshallinv16daykwavg, marshallinvup16cb)]
    ogburndaykwList = [(ogburninv1daykwavg, ogburninvup1cb), (ogburninv2daykwavg, ogburninvup2cb), (ogburninv3daykwavg, ogburninvup3cb), (ogburninv4daykwavg, ogburninvup4cb), (ogburninv5daykwavg, ogburninvup5cb), (ogburninv6daykwavg, ogburninvup6cb), (ogburninv7daykwavg, ogburninvup7cb), (ogburninv8daykwavg, ogburninvup8cb), (ogburninv9daykwavg, ogburninvup9cb), (ogburninv10daykwavg, ogburninvup10cb), (ogburninv11daykwavg, ogburninvup11cb), (ogburninv12daykwavg, ogburninvup12cb), (ogburninv13daykwavg, ogburninvup13cb), (ogburninv14daykwavg, ogburninvup14cb), (ogburninv15daykwavg, ogburninvup15cb), (ogburninv16daykwavg, ogburninvup16cb)]
    tedderdaykwList = [(tedderinv5daykwavg, tedderinvup5cb), (tedderinv6daykwavg, tedderinvup6cb), (tedderinv7daykwavg, tedderinvup7cb), (tedderinv9daykwavg, tedderinvup9cb), (tedderinv10daykwavg, tedderinvup10cb), (tedderinv11daykwavg, tedderinvup11cb), (tedderinv12daykwavg, tedderinvup12cb), (tedderinv13daykwavg, tedderinvup13cb), (tedderinv14daykwavg, tedderinvup14cb)]
    tedder15strdaykwList = [(tedderinv1daykwavg, tedderinvup1cb), (tedderinv2daykwavg, tedderinvup2cb), (tedderinv3daykwavg, tedderinvup3cb), (tedderinv4daykwavg, tedderinvup4cb), (tedderinv8daykwavg, tedderinvup8cb), (tedderinv15daykwavg, tedderinvup15cb), (tedderinv16daykwavg, tedderinvup16cb)]
    thunderheaddaykwList = [(thunderheadinv1daykwavg, thunderheadinvup1cb), (thunderheadinv2daykwavg, thunderheadinvup2cb), (thunderheadinv3daykwavg, thunderheadinvup3cb), (thunderheadinv4daykwavg, thunderheadinvup4cb), (thunderheadinv5daykwavg, thunderheadinvup5cb), (thunderheadinv6daykwavg, thunderheadinvup6cb), (thunderheadinv7daykwavg, thunderheadinvup7cb), (thunderheadinv8daykwavg, thunderheadinvup8cb), (thunderheadinv9daykwavg, thunderheadinvup9cb), (thunderheadinv10daykwavg, thunderheadinvup10cb), (thunderheadinv11daykwavg, thunderheadinvup11cb), (thunderheadinv12daykwavg, thunderheadinvup12cb), (thunderheadinv14daykwavg, thunderheadinvup14cb), (thunderheadinv16daykwavg, thunderheadinvup16cb)]
    thunderhead14strdaykwList = [(thunderheadinv15daykwavg, thunderheadinvup15cb), (thunderheadinv13daykwavg, thunderheadinvup13cb)]
    bulloch1adaykwList = [(bulloch1ainv7daykwavg, bulloch1ainvup7cb), (bulloch1ainv8daykwavg, bulloch1ainvup8cb), (bulloch1ainv9daykwavg, bulloch1ainvup9cb), (bulloch1ainv10daykwavg, bulloch1ainvup10cb), (bulloch1ainv11daykwavg, bulloch1ainvup11cb), (bulloch1ainv12daykwavg, bulloch1ainvup12cb), (bulloch1ainv13daykwavg, bulloch1ainvup13cb), (bulloch1ainv14daykwavg, bulloch1ainvup14cb), (bulloch1ainv15daykwavg, bulloch1ainvup15cb), (bulloch1ainv16daykwavg, bulloch1ainvup16cb), (bulloch1ainv17daykwavg, bulloch1ainvup17cb), (bulloch1ainv18daykwavg, bulloch1ainvup18cb), (bulloch1ainv19daykwavg, bulloch1ainvup19cb), (bulloch1ainv20daykwavg, bulloch1ainvup20cb), (bulloch1ainv21daykwavg, bulloch1ainvup21cb), (bulloch1ainv22daykwavg, bulloch1ainvup22cb), (bulloch1ainv23daykwavg, bulloch1ainvup23cb), (bulloch1ainv24daykwavg, bulloch1ainvup24cb)]
    bulloch1a10strdaykwList = [(bulloch1ainv1daykwavg, bulloch1ainvup1cb), (bulloch1ainv2daykwavg, bulloch1ainvup2cb), (bulloch1ainv3daykwavg, bulloch1ainvup3cb), (bulloch1ainv4daykwavg, bulloch1ainvup4cb), (bulloch1ainv5daykwavg, bulloch1ainvup5cb), (bulloch1ainv6daykwavg, bulloch1ainvup6cb)]
    bulloch1bdaykwList = [(bulloch1binv2daykwavg, bulloch1binvup2cb), (bulloch1binv3daykwavg, bulloch1binvup3cb), (bulloch1binv4daykwavg, bulloch1binvup4cb), (bulloch1binv5daykwavg, bulloch1binvup5cb), (bulloch1binv6daykwavg, bulloch1binvup6cb), (bulloch1binv7daykwavg, bulloch1binvup7cb), (bulloch1binv8daykwavg, bulloch1binvup8cb), (bulloch1binv13daykwavg, bulloch1binvup13cb), (bulloch1binv14daykwavg, bulloch1binvup14cb), (bulloch1binv15daykwavg, bulloch1binvup15cb), (bulloch1binv16daykwavg, bulloch1binvup16cb), (bulloch1binv18daykwavg, bulloch1binvup18cb), (bulloch1binv19daykwavg, bulloch1binvup19cb), (bulloch1binv20daykwavg, bulloch1binvup20cb), (bulloch1binv21daykwavg, bulloch1binvup21cb), (bulloch1binv22daykwavg, bulloch1binvup22cb), (bulloch1binv23daykwavg, bulloch1binvup23cb), (bulloch1binv24daykwavg, bulloch1binvup24cb)]
    bulloch1b10strdaykwList = [(bulloch1binv1daykwavg, bulloch1binvup1cb), (bulloch1binv9daykwavg, bulloch1binvup9cb), (bulloch1binv10daykwavg, bulloch1binvup10cb), (bulloch1binv11daykwavg, bulloch1binvup11cb), (bulloch1binv12daykwavg, bulloch1binvup12cb), (bulloch1binv17daykwavg, bulloch1binvup17cb)]
    grayfoxdaykwList = [(grayfoxinv1daykwavg, grayfoxinvup1cb), (grayfoxinv2daykwavg, grayfoxinvup2cb), (grayfoxinv3daykwavg, grayfoxinvup3cb), (grayfoxinv4daykwavg, grayfoxinvup4cb), (grayfoxinv5daykwavg, grayfoxinvup5cb), (grayfoxinv6daykwavg, grayfoxinvup6cb), (grayfoxinv7daykwavg, grayfoxinvup7cb), (grayfoxinv8daykwavg, grayfoxinvup8cb), (grayfoxinv9daykwavg, grayfoxinvup9cb), (grayfoxinv10daykwavg, grayfoxinvup10cb), (grayfoxinv11daykwavg, grayfoxinvup11cb), (grayfoxinv12daykwavg, grayfoxinvup12cb), (grayfoxinv13daykwavg, grayfoxinvup13cb), (grayfoxinv14daykwavg, grayfoxinvup14cb), (grayfoxinv15daykwavg, grayfoxinvup15cb), (grayfoxinv16daykwavg, grayfoxinvup16cb), (grayfoxinv17daykwavg, grayfoxinvup17cb), (grayfoxinv18daykwavg, grayfoxinvup18cb), (grayfoxinv19daykwavg, grayfoxinvup19cb), (grayfoxinv20daykwavg, grayfoxinvup20cb), (grayfoxinv21daykwavg, grayfoxinvup21cb), (grayfoxinv22daykwavg, grayfoxinvup22cb), (grayfoxinv23daykwavg, grayfoxinvup23cb), (grayfoxinv24daykwavg, grayfoxinvup24cb), (grayfoxinv25daykwavg, grayfoxinvup25cb), (grayfoxinv26daykwavg, grayfoxinvup26cb), (grayfoxinv27daykwavg, grayfoxinvup27cb), (grayfoxinv28daykwavg, grayfoxinvup28cb), (grayfoxinv29daykwavg, grayfoxinvup29cb), (grayfoxinv30daykwavg, grayfoxinvup30cb), (grayfoxinv31daykwavg, grayfoxinvup31cb), (grayfoxinv32daykwavg, grayfoxinvup32cb), (grayfoxinv33daykwavg, grayfoxinvup33cb), (grayfoxinv34daykwavg, grayfoxinvup34cb), (grayfoxinv35daykwavg, grayfoxinvup35cb), (grayfoxinv36daykwavg, grayfoxinvup36cb), (grayfoxinv37daykwavg, grayfoxinvup37cb), (grayfoxinv38daykwavg, grayfoxinvup38cb), (grayfoxinv39daykwavg, grayfoxinvup39cb), (grayfoxinv40daykwavg, grayfoxinvup40cb)]
    hardingdaykwList = [(hardinginv4daykwavg, hardinginvup4cb), (hardinginv5daykwavg, hardinginvup5cb), (hardinginv6daykwavg, hardinginvup6cb),  (hardinginv10daykwavg, hardinginvup10cb), (hardinginv11daykwavg, hardinginvup11cb), (hardinginv12daykwavg, hardinginvup12cb), (hardinginv13daykwavg, hardinginvup13cb), (hardinginv14daykwavg, hardinginvup14cb), (hardinginv15daykwavg, hardinginvup15cb),  (hardinginv17daykwavg, hardinginvup17cb), (hardinginv18daykwavg, hardinginvup18cb), (hardinginv19daykwavg, hardinginvup19cb)]
    harding12strdaykwList = [(hardinginv1daykwavg, hardinginvup1cb), (hardinginv2daykwavg, hardinginvup2cb), (hardinginv3daykwavg, hardinginvup3cb), (hardinginv7daykwavg, hardinginvup7cb), (hardinginv8daykwavg, hardinginvup8cb), (hardinginv9daykwavg, hardinginvup9cb), (hardinginv16daykwavg, hardinginvup16cb), (hardinginv20daykwavg, hardinginvup20cb), (hardinginv21daykwavg, hardinginvup21cb), (hardinginv22daykwavg, hardinginvup22cb), (hardinginv23daykwavg, hardinginvup23cb), (hardinginv24daykwavg, hardinginvup24cb)]
    mcleandaykwList = [ (mcleaninv2daykwavg, mcleaninvup2cb), (mcleaninv3daykwavg, mcleaninvup3cb), (mcleaninv4daykwavg, mcleaninvup4cb), (mcleaninv5daykwavg, mcleaninvup5cb), (mcleaninv6daykwavg, mcleaninvup6cb), (mcleaninv7daykwavg, mcleaninvup7cb), (mcleaninv8daykwavg, mcleaninvup8cb), (mcleaninv9daykwavg, mcleaninvup9cb), (mcleaninv10daykwavg, mcleaninvup10cb), (mcleaninv11daykwavg, mcleaninvup11cb), (mcleaninv12daykwavg, mcleaninvup12cb), (mcleaninv13daykwavg, mcleaninvup13cb), (mcleaninv14daykwavg, mcleaninvup14cb), (mcleaninv15daykwavg, mcleaninvup15cb), (mcleaninv16daykwavg, mcleaninvup16cb), (mcleaninv18daykwavg, mcleaninvup18cb), (mcleaninv20daykwavg, mcleaninvup20cb),  (mcleaninv22daykwavg, mcleaninvup22cb),  (mcleaninv24daykwavg, mcleaninvup24cb), (mcleaninv25daykwavg, mcleaninvup25cb), (mcleaninv26daykwavg, mcleaninvup26cb), (mcleaninv30daykwavg, mcleaninvup30cb)]
    mclean10strdaykwList = [(mcleaninv1daykwavg, mcleaninvup1cb), (mcleaninv17daykwavg, mcleaninvup17cb), (mcleaninv19daykwavg, mcleaninvup19cb), (mcleaninv21daykwavg, mcleaninvup21cb), (mcleaninv23daykwavg, mcleaninvup23cb), (mcleaninv27daykwavg, mcleaninvup27cb), (mcleaninv28daykwavg, mcleaninvup28cb), (mcleaninv29daykwavg, mcleaninvup29cb), (mcleaninv31daykwavg, mcleaninvup31cb), (mcleaninv32daykwavg, mcleaninvup32cb), (mcleaninv33daykwavg, mcleaninvup33cb), (mcleaninv34daykwavg, mcleaninvup34cb), (mcleaninv35daykwavg, mcleaninvup35cb), (mcleaninv36daykwavg, mcleaninvup36cb), (mcleaninv37daykwavg, mcleaninvup37cb), (mcleaninv38daykwavg, mcleaninvup38cb), (mcleaninv39daykwavg, mcleaninvup39cb), (mcleaninv40daykwavg, mcleaninvup40cb)]
    richmonddaykwList = [(richmondinv1daykwavg, richmondinvup1cb), (richmondinv2daykwavg, richmondinvup2cb), (richmondinv3daykwavg, richmondinvup3cb), (richmondinv4daykwavg, richmondinvup4cb), (richmondinv5daykwavg, richmondinvup5cb), (richmondinv6daykwavg, richmondinvup6cb), (richmondinv7daykwavg, richmondinvup7cb), (richmondinv11daykwavg, richmondinvup11cb), (richmondinv12daykwavg, richmondinvup12cb), (richmondinv13daykwavg, richmondinvup13cb), (richmondinv14daykwavg, richmondinvup14cb), (richmondinv15daykwavg, richmondinvup15cb), (richmondinv16daykwavg, richmondinvup16cb), (richmondinv17daykwavg, richmondinvup17cb), (richmondinv18daykwavg, richmondinvup18cb), (richmondinv19daykwavg, richmondinvup19cb), (richmondinv20daykwavg, richmondinvup20cb), (richmondinv21daykwavg, richmondinvup21cb)]
    richmond10strdaykwList = [(richmondinv8daykwavg, richmondinvup8cb), (richmondinv9daykwavg, richmondinvup9cb), (richmondinv10daykwavg, richmondinvup10cb), (richmondinv22daykwavg, richmondinvup22cb), (richmondinv23daykwavg, richmondinvup23cb), (richmondinv24daykwavg, richmondinvup24cb)]
    shorthorndaykwList = [(shorthorninv1daykwavg, shorthorninvup1cb), (shorthorninv2daykwavg, shorthorninvup2cb), (shorthorninv3daykwavg, shorthorninvup3cb), (shorthorninv4daykwavg, shorthorninvup4cb), (shorthorninv5daykwavg, shorthorninvup5cb), (shorthorninv6daykwavg, shorthorninvup6cb), (shorthorninv7daykwavg, shorthorninvup7cb), (shorthorninv8daykwavg, shorthorninvup8cb), (shorthorninv9daykwavg, shorthorninvup9cb), (shorthorninv10daykwavg, shorthorninvup10cb), (shorthorninv11daykwavg, shorthorninvup11cb), (shorthorninv12daykwavg, shorthorninvup12cb), (shorthorninv13daykwavg, shorthorninvup13cb), (shorthorninv14daykwavg, shorthorninvup14cb), (shorthorninv15daykwavg, shorthorninvup15cb), (shorthorninv16daykwavg, shorthorninvup16cb), (shorthorninv17daykwavg, shorthorninvup17cb), (shorthorninv18daykwavg, shorthorninvup18cb), (shorthorninv19daykwavg, shorthorninvup19cb), (shorthorninv20daykwavg, shorthorninvup20cb), (shorthorninv22daykwavg, shorthorninvup22cb), (shorthorninv23daykwavg, shorthorninvup23cb), (shorthorninv24daykwavg, shorthorninvup24cb),  (shorthorninv26daykwavg, shorthorninvup26cb), (shorthorninv27daykwavg, shorthorninvup27cb), (shorthorninv28daykwavg, shorthorninvup28cb),  (shorthorninv32daykwavg, shorthorninvup32cb), (shorthorninv33daykwavg, shorthorninvup33cb),  (shorthorninv37daykwavg, shorthorninvup37cb), (shorthorninv38daykwavg, shorthorninvup38cb), (shorthorninv39daykwavg, shorthorninvup39cb), (shorthorninv40daykwavg, shorthorninvup40cb), (shorthorninv41daykwavg, shorthorninvup41cb), (shorthorninv42daykwavg, shorthorninvup42cb), (shorthorninv43daykwavg, shorthorninvup43cb), (shorthorninv45daykwavg, shorthorninvup45cb), (shorthorninv46daykwavg, shorthorninvup46cb), (shorthorninv47daykwavg, shorthorninvup47cb), (shorthorninv48daykwavg, shorthorninvup48cb), (shorthorninv52daykwavg, shorthorninvup52cb), (shorthorninv53daykwavg, shorthorninvup53cb), (shorthorninv57daykwavg, shorthorninvup57cb), (shorthorninv58daykwavg, shorthorninvup58cb), (shorthorninv59daykwavg, shorthorninvup59cb), (shorthorninv60daykwavg, shorthorninvup60cb), (shorthorninv61daykwavg, shorthorninvup61cb), (shorthorninv62daykwavg, shorthorninvup62cb), (shorthorninv63daykwavg, shorthorninvup63cb), (shorthorninv64daykwavg, shorthorninvup64cb), (shorthorninv65daykwavg, shorthorninvup65cb), (shorthorninv66daykwavg, shorthorninvup66cb)]
    shorthorn13strdaykwList = [(shorthorninv21daykwavg, shorthorninvup21cb), (shorthorninv25daykwavg, shorthorninvup25cb), (shorthorninv29daykwavg, shorthorninvup29cb), (shorthorninv30daykwavg, shorthorninvup30cb), (shorthorninv31daykwavg, shorthorninvup31cb), (shorthorninv34daykwavg, shorthorninvup34cb), (shorthorninv35daykwavg, shorthorninvup35cb), (shorthorninv36daykwavg, shorthorninvup36cb),  (shorthorninv44daykwavg, shorthorninvup44cb), (shorthorninv49daykwavg, shorthorninvup49cb), (shorthorninv50daykwavg, shorthorninvup50cb), (shorthorninv51daykwavg, shorthorninvup51cb), (shorthorninv54daykwavg, shorthorninvup54cb), (shorthorninv55daykwavg, shorthorninvup55cb), (shorthorninv56daykwavg, shorthorninvup56cb), (shorthorninv67daykwavg, shorthorninvup67cb), (shorthorninv68daykwavg, shorthorninvup68cb), (shorthorninv69daykwavg, shorthorninvup69cb), (shorthorninv70daykwavg, shorthorninvup70cb), (shorthorninv71daykwavg, shorthorninvup71cb), (shorthorninv72daykwavg, shorthorninvup72cb)]
    sunflowerdaykwList = [(sunflowerinv3daykwavg, sunflowerinvup3cb), (sunflowerinv4daykwavg, sunflowerinvup4cb), (sunflowerinv5daykwavg, sunflowerinvup5cb), (sunflowerinv6daykwavg, sunflowerinvup6cb), (sunflowerinv7daykwavg, sunflowerinvup7cb), (sunflowerinv8daykwavg, sunflowerinvup8cb), (sunflowerinv9daykwavg, sunflowerinvup9cb), (sunflowerinv10daykwavg, sunflowerinvup10cb), (sunflowerinv11daykwavg, sunflowerinvup11cb), (sunflowerinv12daykwavg, sunflowerinvup12cb), (sunflowerinv13daykwavg, sunflowerinvup13cb), (sunflowerinv14daykwavg, sunflowerinvup14cb), (sunflowerinv15daykwavg, sunflowerinvup15cb), (sunflowerinv16daykwavg, sunflowerinvup16cb), (sunflowerinv17daykwavg, sunflowerinvup17cb), (sunflowerinv18daykwavg, sunflowerinvup18cb), (sunflowerinv19daykwavg, sunflowerinvup19cb), (sunflowerinv20daykwavg, sunflowerinvup20cb),  (sunflowerinv34daykwavg, sunflowerinvup34cb),  (sunflowerinv62daykwavg, sunflowerinvup62cb), (sunflowerinv63daykwavg, sunflowerinvup63cb), (sunflowerinv64daykwavg, sunflowerinvup64cb), (sunflowerinv65daykwavg, sunflowerinvup65cb), (sunflowerinv66daykwavg, sunflowerinvup66cb), (sunflowerinv67daykwavg, sunflowerinvup67cb), (sunflowerinv68daykwavg, sunflowerinvup68cb), (sunflowerinv69daykwavg, sunflowerinvup69cb), (sunflowerinv70daykwavg, sunflowerinvup70cb), (sunflowerinv71daykwavg, sunflowerinvup71cb), (sunflowerinv72daykwavg, sunflowerinvup72cb), (sunflowerinv73daykwavg, sunflowerinvup73cb), (sunflowerinv74daykwavg, sunflowerinvup74cb), (sunflowerinv75daykwavg, sunflowerinvup75cb), (sunflowerinv76daykwavg, sunflowerinvup76cb), (sunflowerinv77daykwavg, sunflowerinvup77cb)]
    sunflower12strdaykwList = [(sunflowerinv1daykwavg, sunflowerinvup1cb), (sunflowerinv2daykwavg, sunflowerinvup2cb), (sunflowerinv21daykwavg, sunflowerinvup21cb), (sunflowerinv22daykwavg, sunflowerinvup22cb), (sunflowerinv23daykwavg, sunflowerinvup23cb), (sunflowerinv24daykwavg, sunflowerinvup24cb), (sunflowerinv25daykwavg, sunflowerinvup25cb), (sunflowerinv26daykwavg, sunflowerinvup26cb),  (sunflowerinv27daykwavg, sunflowerinvup27cb), (sunflowerinv28daykwavg, sunflowerinvup28cb), (sunflowerinv29daykwavg, sunflowerinvup29cb), (sunflowerinv30daykwavg, sunflowerinvup30cb), (sunflowerinv31daykwavg, sunflowerinvup31cb), (sunflowerinv32daykwavg, sunflowerinvup32cb),  (sunflowerinv33daykwavg, sunflowerinvup33cb), (sunflowerinv35daykwavg, sunflowerinvup35cb), (sunflowerinv36daykwavg, sunflowerinvup36cb), (sunflowerinv37daykwavg, sunflowerinvup37cb), (sunflowerinv38daykwavg, sunflowerinvup38cb), (sunflowerinv39daykwavg, sunflowerinvup39cb), (sunflowerinv40daykwavg, sunflowerinvup40cb), (sunflowerinv41daykwavg, sunflowerinvup41cb), (sunflowerinv42daykwavg, sunflowerinvup42cb), (sunflowerinv43daykwavg, sunflowerinvup43cb), (sunflowerinv44daykwavg, sunflowerinvup44cb), (sunflowerinv45daykwavg, sunflowerinvup45cb), (sunflowerinv46daykwavg, sunflowerinvup46cb), (sunflowerinv47daykwavg, sunflowerinvup47cb), (sunflowerinv48daykwavg, sunflowerinvup48cb), (sunflowerinv49daykwavg, sunflowerinvup49cb), (sunflowerinv50daykwavg, sunflowerinvup50cb), (sunflowerinv51daykwavg, sunflowerinvup51cb), (sunflowerinv52daykwavg, sunflowerinvup52cb), (sunflowerinv53daykwavg, sunflowerinvup53cb), (sunflowerinv54daykwavg, sunflowerinvup54cb),(sunflowerinv55daykwavg, sunflowerinvup55cb), (sunflowerinv56daykwavg, sunflowerinvup56cb), (sunflowerinv57daykwavg, sunflowerinvup57cb), (sunflowerinv58daykwavg, sunflowerinvup58cb), (sunflowerinv59daykwavg, sunflowerinvup59cb), (sunflowerinv60daykwavg, sunflowerinvup60cb),(sunflowerinv61daykwavg, sunflowerinvup61cb), (sunflowerinv78daykwavg, sunflowerinvup78cb), (sunflowerinv79daykwavg, sunflowerinvup79cb), (sunflowerinv80daykwavg, sunflowerinvup80cb) ]
    upsondaykwList = [(upsoninv1daykwavg, upsoninvup1cb), (upsoninv2daykwavg, upsoninvup2cb), (upsoninv3daykwavg, upsoninvup3cb), (upsoninv4daykwavg, upsoninvup4cb), (upsoninv5daykwavg, upsoninvup5cb), (upsoninv9daykwavg, upsoninvup9cb), (upsoninv10daykwavg, upsoninvup10cb), (upsoninv11daykwavg, upsoninvup11cb), (upsoninv12daykwavg, upsoninvup12cb), (upsoninv13daykwavg, upsoninvup13cb), (upsoninv14daykwavg, upsoninvup14cb), (upsoninv15daykwavg, upsoninvup15cb), (upsoninv16daykwavg, upsoninvup16cb), (upsoninv17daykwavg, upsoninvup17cb), (upsoninv21daykwavg, upsoninvup21cb), (upsoninv22daykwavg, upsoninvup22cb), (upsoninv23daykwavg, upsoninvup23cb), (upsoninv24daykwavg, upsoninvup24cb)]
    upson10strdaykwList = [(upsoninv6daykwavg, upsoninvup6cb), (upsoninv7daykwavg, upsoninvup7cb), (upsoninv8daykwavg, upsoninvup8cb), (upsoninv18daykwavg, upsoninvup18cb), (upsoninv19daykwavg, upsoninvup19cb), (upsoninv20daykwavg, upsoninvup20cb)]
    warblerdaykwList = [(warblerinv1daykwavg, warblerinvup1cb), (warblerinv2daykwavg, warblerinvup2cb), (warblerinv3daykwavg, warblerinvup3cb), (warblerinv4daykwavg, warblerinvup4cb), (warblerinv5daykwavg, warblerinvup5cb), (warblerinv6daykwavg, warblerinvup6cb), (warblerinv7daykwavg, warblerinvup7cb), (warblerinv8daykwavg, warblerinvup8cb), (warblerinv9daykwavg, warblerinvup9cb), (warblerinv10daykwavg, warblerinvup10cb), (warblerinv11daykwavg, warblerinvup11cb), (warblerinv12daykwavg, warblerinvup12cb), (warblerinv13daykwavg, warblerinvup13cb), (warblerinv14daykwavg, warblerinvup14cb), (warblerinv15daykwavg, warblerinvup15cb), (warblerinv16daykwavg, warblerinvup16cb), (warblerinv17daykwavg, warblerinvup17cb), (warblerinv18daykwavg, warblerinvup18cb), (warblerinv19daykwavg, warblerinvup19cb), (warblerinv20daykwavg, warblerinvup20cb), (warblerinv21daykwavg, warblerinvup21cb), (warblerinv22daykwavg, warblerinvup22cb), (warblerinv23daykwavg, warblerinvup23cb), (warblerinv24daykwavg, warblerinvup24cb), (warblerinv25daykwavg, warblerinvup25cb), (warblerinv26daykwavg, warblerinvup26cb), (warblerinv27daykwavg, warblerinvup27cb), (warblerinv28daykwavg, warblerinvup28cb), (warblerinv29daykwavg, warblerinvup29cb), (warblerinv30daykwavg, warblerinvup30cb), (warblerinv31daykwavg, warblerinvup31cb), (warblerinv32daykwavg, warblerinvup32cb)]
    washingtondaykwList = [(washingtoninv4daykwavg, washingtoninvup4cb), (washingtoninv5daykwavg, washingtoninvup5cb), (washingtoninv6daykwavg, washingtoninvup6cb), (washingtoninv7daykwavg, washingtoninvup7cb), (washingtoninv8daykwavg, washingtoninvup8cb), (washingtoninv9daykwavg, washingtoninvup9cb), (washingtoninv10daykwavg, washingtoninvup10cb), (washingtoninv11daykwavg, washingtoninvup11cb), (washingtoninv12daykwavg, washingtoninvup12cb), (washingtoninv15daykwavg, washingtoninvup15cb), (washingtoninv16daykwavg, washingtoninvup16cb), (washingtoninv17daykwavg, washingtoninvup17cb), (washingtoninv18daykwavg, washingtoninvup18cb), (washingtoninv19daykwavg, washingtoninvup19cb),  (washingtoninv21daykwavg, washingtoninvup21cb), (washingtoninv22daykwavg, washingtoninvup22cb), (washingtoninv23daykwavg, washingtoninvup23cb), (washingtoninv24daykwavg, washingtoninvup24cb), (washingtoninv40daykwavg, washingtoninvup40cb)]
    washington12strdaykwList = [(washingtoninv1daykwavg, washingtoninvup1cb), (washingtoninv2daykwavg, washingtoninvup2cb), (washingtoninv3daykwavg, washingtoninvup3cb), (washingtoninv13daykwavg, washingtoninvup13cb), (washingtoninv14daykwavg, washingtoninvup14cb), (washingtoninv20daykwavg, washingtoninvup20cb), (washingtoninv25daykwavg, washingtoninvup25cb), (washingtoninv26daykwavg, washingtoninvup26cb), (washingtoninv27daykwavg, washingtoninvup27cb), (washingtoninv28daykwavg, washingtoninvup28cb), (washingtoninv29daykwavg, washingtoninvup29cb), (washingtoninv30daykwavg, washingtoninvup30cb), (washingtoninv31daykwavg, washingtoninvup31cb), (washingtoninv32daykwavg, washingtoninvup32cb), (washingtoninv33daykwavg, washingtoninvup33cb), (washingtoninv34daykwavg, washingtoninvup34cb), (washingtoninv35daykwavg, washingtoninvup35cb), (washingtoninv36daykwavg, washingtoninvup36cb), (washingtoninv37daykwavg, washingtoninvup37cb), (washingtoninv38daykwavg, washingtoninvup38cb), (washingtoninv39daykwavg, washingtoninvup39cb)]
    whitehalldaykwList = [(whitehallinv1daykwavg, whitehallinvup1cb), (whitehallinv3daykwavg, whitehallinvup3cb), (whitehallinv4daykwavg, whitehallinvup4cb), (whitehallinv5daykwavg, whitehallinvup5cb),  (whitehallinv13daykwavg, whitehallinvup13cb), (whitehallinv14daykwavg, whitehallinvup14cb), (whitehallinv15daykwavg, whitehallinvup15cb), (whitehallinv16daykwavg, whitehallinvup16cb)]
    whitehall13strdaykwList = [(whitehallinv2daykwavg, whitehallinvup2cb), (whitehallinv6daykwavg, whitehallinvup6cb), (whitehallinv7daykwavg, whitehallinvup7cb), (whitehallinv8daykwavg, whitehallinvup8cb), (whitehallinv9daykwavg, whitehallinvup9cb), (whitehallinv10daykwavg, whitehallinvup10cb), (whitehallinv11daykwavg, whitehallinvup11cb), (whitehallinv12daykwavg, whitehallinvup12cb)]
    whitetaildaykwList = [(whitetailinv1daykwavg, whitetailinvup1cb), (whitetailinv2daykwavg, whitetailinvup2cb), (whitetailinv3daykwavg, whitetailinvup3cb), (whitetailinv5daykwavg, whitetailinvup5cb), (whitetailinv6daykwavg, whitetailinvup6cb), (whitetailinv7daykwavg, whitetailinvup7cb), (whitetailinv8daykwavg, whitetailinvup8cb), (whitetailinv9daykwavg, whitetailinvup9cb), (whitetailinv10daykwavg, whitetailinvup10cb), (whitetailinv11daykwavg, whitetailinvup11cb), (whitetailinv12daykwavg, whitetailinvup12cb),  (whitetailinv22daykwavg, whitetailinvup22cb), (whitetailinv23daykwavg, whitetailinvup23cb), (whitetailinv24daykwavg, whitetailinvup24cb), (whitetailinv25daykwavg, whitetailinvup25cb),  (whitetailinv32daykwavg, whitetailinvup32cb), (whitetailinv33daykwavg, whitetailinvup33cb),  (whitetailinv35daykwavg, whitetailinvup35cb), (whitetailinv36daykwavg, whitetailinvup36cb), (whitetailinv37daykwavg, whitetailinvup37cb), (whitetailinv38daykwavg, whitetailinvup38cb), (whitetailinv39daykwavg, whitetailinvup39cb), (whitetailinv40daykwavg, whitetailinvup40cb), (whitetailinv41daykwavg, whitetailinvup41cb), (whitetailinv42daykwavg, whitetailinvup42cb),  (whitetailinv49daykwavg, whitetailinvup49cb), (whitetailinv50daykwavg, whitetailinvup50cb), (whitetailinv51daykwavg, whitetailinvup51cb),  (whitetailinv57daykwavg, whitetailinvup57cb),  (whitetailinv61daykwavg, whitetailinvup61cb), (whitetailinv62daykwavg, whitetailinvup62cb), (whitetailinv63daykwavg, whitetailinvup63cb), (whitetailinv65daykwavg, whitetailinvup65cb), (whitetailinv66daykwavg, whitetailinvup66cb), (whitetailinv67daykwavg, whitetailinvup67cb), (whitetailinv68daykwavg, whitetailinvup68cb), (whitetailinv69daykwavg, whitetailinvup69cb), (whitetailinv70daykwavg, whitetailinvup70cb), (whitetailinv71daykwavg, whitetailinvup71cb), (whitetailinv72daykwavg, whitetailinvup72cb), (whitetailinv73daykwavg, whitetailinvup73cb), (whitetailinv74daykwavg, whitetailinvup74cb), (whitetailinv75daykwavg, whitetailinvup75cb), (whitetailinv76daykwavg, whitetailinvup76cb), (whitetailinv77daykwavg, whitetailinvup77cb), (whitetailinv78daykwavg, whitetailinvup78cb), (whitetailinv79daykwavg, whitetailinvup79cb), (whitetailinv80daykwavg, whitetailinvup80cb)]
    whitetail17strdaykwList = [(whitetailinv4daykwavg, whitetailinvup4cb), (whitetailinv13daykwavg, whitetailinvup13cb), (whitetailinv14daykwavg, whitetailinvup14cb), (whitetailinv15daykwavg, whitetailinvup15cb), (whitetailinv16daykwavg, whitetailinvup16cb), (whitetailinv17daykwavg, whitetailinvup17cb), (whitetailinv18daykwavg, whitetailinvup18cb), (whitetailinv19daykwavg, whitetailinvup19cb), (whitetailinv20daykwavg, whitetailinvup20cb), (whitetailinv21daykwavg, whitetailinvup21cb), (whitetailinv26daykwavg, whitetailinvup26cb), (whitetailinv27daykwavg, whitetailinvup27cb), (whitetailinv28daykwavg, whitetailinvup28cb), (whitetailinv29daykwavg, whitetailinvup29cb), (whitetailinv30daykwavg, whitetailinvup30cb), (whitetailinv31daykwavg, whitetailinvup31cb), (whitetailinv34daykwavg, whitetailinvup34cb), (whitetailinv43daykwavg, whitetailinvup43cb), (whitetailinv44daykwavg, whitetailinvup44cb), (whitetailinv45daykwavg, whitetailinvup45cb), (whitetailinv46daykwavg, whitetailinvup46cb), (whitetailinv47daykwavg, whitetailinvup47cb), (whitetailinv48daykwavg, whitetailinvup48cb), (whitetailinv52daykwavg, whitetailinvup52cb), (whitetailinv53daykwavg, whitetailinvup53cb), (whitetailinv54daykwavg, whitetailinvup54cb), (whitetailinv55daykwavg, whitetailinvup55cb), (whitetailinv56daykwavg, whitetailinvup56cb), (whitetailinv58daykwavg, whitetailinvup58cb), (whitetailinv59daykwavg, whitetailinvup59cb), (whitetailinv60daykwavg, whitetailinvup60cb), (whitetailinv64daykwavg, whitetailinvup64cb)]
    conetoe1daykwList = [(conetoe1inv1daykwavg, conetoe1invup1cb), (conetoe1inv2daykwavg, conetoe1invup2cb), (conetoe1inv3daykwavg, conetoe1invup3cb), (conetoe1inv4daykwavg, conetoe1invup4cb), (conetoe1inv5daykwavg, conetoe1invup5cb), (conetoe1inv6daykwavg, conetoe1invup6cb), (conetoe1inv7daykwavg, conetoe1invup7cb), (conetoe1inv8daykwavg, conetoe1invup8cb), (conetoe1inv9daykwavg, conetoe1invup9cb), (conetoe1inv10daykwavg, conetoe1invup10cb), (conetoe1inv11daykwavg, conetoe1invup11cb), (conetoe1inv12daykwavg, conetoe1invup12cb), (conetoe1inv13daykwavg, conetoe1invup13cb), (conetoe1inv14daykwavg, conetoe1invup14cb), (conetoe1inv15daykwavg, conetoe1invup15cb), (conetoe1inv16daykwavg, conetoe1invup16cb)]
    duplindaykwList = [(duplinsinv1daykwavg, duplininvup4cb), (duplinsinv2daykwavg, duplininvup5cb), (duplinsinv3daykwavg, duplininvup6cb), (duplinsinv4daykwavg, duplininvup7cb), (duplinsinv5daykwavg, duplininvup8cb), (duplinsinv6daykwavg, duplininvup9cb), (duplinsinv7daykwavg, duplininvup10cb), (duplinsinv8daykwavg, duplininvup11cb), (duplinsinv9daykwavg, duplininvup12cb), (duplinsinv10daykwavg, duplininvup13cb), (duplinsinv11daykwavg, duplininvup14cb), (duplinsinv12daykwavg, duplininvup15cb), (duplinsinv13daykwavg, duplininvup16cb), (duplinsinv14daykwavg, duplininvup17cb), (duplinsinv15daykwavg, duplininvup18cb), (duplinsinv16daykwavg, duplininvup19cb), (duplinsinv17daykwavg, duplininvup20cb), (duplinsinv18daykwavg, duplininvup21cb)]
    duplinCentraldaykwList = [(duplininv1daykwavg, duplininvup1cb), (duplininv2daykwavg, duplininvup2cb), (duplininv3daykwavg, duplininvup3cb)]
    wayne11000daykwList = [(wayne1inv1daykwavg, wayne1invup1cb), (wayne1inv4daykwavg, wayne1invup4cb)]
    wayne1daykwList = [(wayne1inv2daykwavg, wayne1invup2cb), (wayne1inv3daykwavg, wayne1invup3cb)]
    wayne21000daykwList = [(wayne2inv3daykwavg, wayne2invup3cb), (wayne2inv4daykwavg, wayne2invup4cb)]
    wayne2daykwList = [(wayne2inv1daykwavg, wayne2invup1cb), (wayne2inv2daykwavg, wayne2invup2cb)]
    wayne31000daykwList = [(wayne3inv1daykwavg, wayne3invup1cb), (wayne3inv2daykwavg, wayne3invup2cb)]
    wayne3daykwList = [(wayne3inv3daykwavg, wayne3invup3cb), (wayne3inv4daykwavg, wayne3invup4cb)]
    freightlinedaykwList = [(freightlinerinv1daykwavg, freightlinerinvup1cb), (freightlinerinv3daykwavg, freightlinerinvup3cb), (freightlinerinv4daykwavg, freightlinerinvup4cb), (freightlinerinv5daykwavg, freightlinerinvup5cb), (freightlinerinv8daykwavg, freightlinerinvup8cb), (freightlinerinv9daykwavg, freightlinerinvup9cb), (freightlinerinv10daykwavg, freightlinerinvup10cb), (freightlinerinv11daykwavg, freightlinerinvup11cb), (freightlinerinv12daykwavg, freightlinerinvup12cb), (freightlinerinv15daykwavg, freightlinerinvup15cb), (freightlinerinv16daykwavg, freightlinerinvup16cb), (freightlinerinv17daykwavg, freightlinerinvup17cb), (freightlinerinv18daykwavg, freightlinerinvup18cb)]
    freightline66daykwList = [(freightlinerinv2daykwavg, freightlinerinvup2cb), (freightlinerinv6daykwavg, freightlinerinvup6cb), (freightlinerinv7daykwavg, freightlinerinvup7cb), (freightlinerinv13daykwavg, freightlinerinvup13cb), (freightlinerinv14daykwavg, freightlinerinvup14cb)]
    hollyswampdaykwList = [(hollyswampinv1daykwavg, hollyswampinvup1cb), (hollyswampinv2daykwavg, hollyswampinvup2cb), (hollyswampinv3daykwavg, hollyswampinvup3cb), (hollyswampinv4daykwavg, hollyswampinvup4cb), (hollyswampinv5daykwavg, hollyswampinvup5cb), (hollyswampinv6daykwavg, hollyswampinvup6cb), (hollyswampinv7daykwavg, hollyswampinvup7cb), (hollyswampinv8daykwavg, hollyswampinvup8cb), (hollyswampinv9daykwavg, hollyswampinvup9cb), (hollyswampinv10daykwavg, hollyswampinvup10cb), (hollyswampinv11daykwavg, hollyswampinvup11cb), (hollyswampinv12daykwavg, hollyswampinvup12cb), (hollyswampinv14daykwavg, hollyswampinvup14cb), (hollyswampinv16daykwavg, hollyswampinvup16cb)]
    hollyswamp18strdaykwList = [(hollyswampinv15daykwavg, hollyswampinvup15cb), (hollyswampinv13daykwavg, hollyswampinvup13cb)]
    pgdaykwList = [(pginv7daykwavg, pginvup7cb), (pginv8daykwavg, pginvup8cb), (pginv9daykwavg, pginvup9cb), (pginv10daykwavg, pginvup10cb), (pginv11daykwavg, pginvup11cb), (pginv12daykwavg, pginvup12cb), (pginv13daykwavg, pginvup13cb), (pginv14daykwavg, pginvup14cb), (pginv15daykwavg, pginvup15cb), (pginv16daykwavg, pginvup16cb), (pginv17daykwavg, pginvup17cb), (pginv18daykwavg, pginvup18cb)]
    pg66daykwList = [(pginv1daykwavg, pginvup1cb), (pginv2daykwavg, pginvup2cb), (pginv3daykwavg, pginvup3cb), (pginv4daykwavg, pginvup4cb), (pginv5daykwavg, pginvup5cb), (pginv6daykwavg, pginvup6cb)]

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
        if inv_group_name == "Duplin String Inverters":
            print(len(underperformance_list))
            print(underperformance_list)
            values = [value for value, _ in underperformance_list]
            max_val = max(values)
            print([val/max_val * 100 for val in values])

        calculate_percentages(underperformance_list) #Updates GUI widgets with new percentages
    


def calculate_percentages(data_list):
    """
    Calculates percentages based on the maximum value in the input list
    and assigns these percentages to the 'text' attribute of the Tkinter variable.

    Args:
        data_list: A list of tuples, where each tuple contains:
            - The data value (float).
            - The string identifier (e.g., inverter number). Unused feature deprecated, data retained
            - The Tkinter Checkbutton variable to update.
    """
    if not data_list:
        return  # Handle empty list case
    values = [value for value, _ in data_list]
    max_value = max(values)
    if max_value == 0 or np.isnan(max_value):
        for _, var in data_list:
            try:
                var.config(text="0%", bg='red')  # Update the 'text' attribute
            except AttributeError:
                pass #  The variable does not have a text attribute.
        return

    for value, var in data_list:
        percentage = (value / max_value) * 100
        if np.isnan(value):
            var.config(text="0%", bg='red')
            continue

        if round(percentage, 0) == 100:
            bg_color = "#90EE90"  
        elif percentage < 50:
            bg_color = "red"  
        elif 50 <= percentage < 75:
            bg_color = "orange"  
        elif 75 <= percentage < 85:
            bg_color = "yellow"  
        elif 85 <= percentage < 95:
            bg_color = "#FEEAA5"  # paleyellow
        elif percentage >= 95:
            bg_color = "SystemButtonFace"
        else:
            bg_color = "#EE82EE"  # violet

        try:
            var.config(text=f"{percentage:.0f}%", bg=bg_color)  # Update the 'text' attribute
        except AttributeError:
             pass #  The variable does not have a text attribute.


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

    global timecurrent
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

    time1v.config(text=hm_firsttime, font=("Calibri", 20))
    time2v.config(text=hm_secondtime, font=("Calibri", 20))
    time3v.config(text=hm_thirdtime, font=("Calibri", 20))
    time4v.config(text=hm_fourthtime, font=("Calibri", 20))
    time10v.config(text=hm_tenthtime, font=("Calibri", 20))
    timeLv.config(text=hm_lasttime, font=("Calibri", 20))

    pulls5TD = firsttime - fifthtime
    pulls5TDmins = round(pulls5TD.total_seconds() / 60, 2)
    pulls15TD = firsttime - lasttime
    pulls15TDmins = round(pulls15TD.total_seconds() / 60, 2)
    spread10.config(text=f"5 Pulls | {pulls5TDmins} Minutes")
    spread15.config(text=f"15 Pulls | {pulls15TDmins} Minutes")
    
    timecurrent = datetime.now()
    db_update_time = 10
    timecompare = timecurrent - timedelta(minutes=db_update_time)
    recent_update = last_update()
    if recent_update < timecompare:
        os.startfile(r"G:\Shared drives\O&M\NCC Automations\Notification System\API Data Pull, Multi SQL.py")
        messagebox.showerror(parent=timeW, title="Notification System/GUI", message= f"The Database has not been updated in {str(db_update_time)} Minutes and usually updates every 2\nLaunching Data Pull Script in response.")
        ty.sleep(180)

    tupdate = timecurrent.strftime('%H:%M')

    timmytimeLabel.config(text= tupdate, font= ("Calibiri", 30))
    
    checkin() 

def db_to_dict():
    query_start = ty.perf_counter()
    notes_button.config(state=DISABLED)

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
        if pd.isna(site) or site in  ["Charter GM", "Charter RM", "Charter Roof"]:
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
    gui_update_timer.pause()
    messagebox.showinfo(parent=alertW, title="Checkbutton Info", message= """The First column of CheckButtons in the Site Data Window turns off all notifications associated with that Site.
                        \nThe POA CB will change the value to 9999 so that no inv outages are filtered by the POA
                        \nThe colored INV CheckButtons are to be selected when a WO is open for that device and will turn off notifications of outages with INV
                        \nThe Box in the middle Represents the Status of that device in Emaint. | ⬜ = NO WO | Black BG = Offline WO Open | Blue BG = Underperformance WO Open | Pink BG = Comms Outage WO Open | Yellow BG = Unknown WO Found |
                        \nThe 3rd Column is a CB for Underperformance tracking the '%' is based off of the last 7 days of data excluding mornings and evenings as well as times when device was offline.""")
    gui_update_timer.resume()

def open_file():
    os.startfile(r"G:\Shared drives\Narenco Projects\O&M Projects\NCC\Procedures\Also Energy GUI Interactions.docx")
    

cur_time = datetime.now()
tupdate =  cur_time.strftime('%H:%M')
notesFrame = Frame(alertW, height= 5, bd= 3, relief= 'groove')
notesFrame.pack(fill='x')
alertwnotes = Label(notesFrame, text= "1st Checkbox: ✓ = Open WO\n& pauses inv notifications", font= ("Calibiri", 12))
alertwnotes.pack()
tupdateLabel = Label(alertW, text= "GUI Last Updated", font= ("Calibiri", 18))
tupdateLabel.pack()
timmytimeLabel = Label(alertW, text= tupdate, font= ("Calibiri", 30))
timmytimeLabel.pack()
notes_button = Button(alertW, command= lambda: check_button_notes(), text= "Checkbutton Notes", font=("Calibiri", 14), bg=main_color, cursor='hand2')
notes_button.pack(padx= 2, pady= 2, fill=X)
proc_button = Button(alertW, command= lambda: open_file(), text= "Procedure Doc", font=("Calibiri", 14), cursor='hand2')
proc_button.pack(padx= 2, pady= 2, fill=X)
wo_button = Button(alertW, command= lambda: parse_wo(), text= "Assess Open WO's", font=("Calibiri", 14), cursor='hand2')
wo_button.pack(padx= 2, pady= 2, fill=X)

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