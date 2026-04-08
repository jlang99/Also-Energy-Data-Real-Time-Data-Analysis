import warnings
import pyodbc
from datetime import datetime, time, timedelta
from tkinter import *
from tkinter import messagebox, filedialog, ttk
import atexit
import time as ty
import threading
import numpy as np
import ctypes
import smtplib
import os
import sys
import glob
import json
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from sklearn.linear_model import LinearRegression
import pandas as pd

# External Imports (Assumed environment setup)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from PythonTools import CREDS, EMAILS, MAP_SITES_HARDWARE_GUI, restart_pc, get_hostname, ToolTip

myappid = 'AE.API.Data.GUI'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# --- Constants ---
MAIN_COLOR = '#ADD8E6'
BUTTON_STATE_FILE = r"G:\Shared drives\O&M\NCC Automations\Notification System\CheckBoxState.json"
ICON_PATH = r"G:\Shared drives\O&M\NCC Automations\Icons\favicon.ico"

# Helper for WO Parser
NORMAL_NUMBERING = {'Bluebird', 'Cardinal', 'Cherry Blossom', 'Cougar', 'Harrison', 'Hayes', 'Hickory', 'Violet', 'HICKSON',
                    'JEFFERSON', 'Marshall', 'OGBURN', 'Tedder', 'Thunderhead', 'Van Buren', 'Bulloch 1A', 'Bulloch 1B', 'Elk', 'Duplin',
                    'Harding', 'Mclean', 'Richmond', 'Shorthorn', 'Sunflower', 'Upson', 'Warbler', 'Washington', 'Whitehall', 'Whitetail',
                    'Conetoe', 'Wayne 1', 'Wayne 2', 'Wayne 3', 'Freightliner', 'Holly Swamp', 'PG'}

def define_inv_num(site, group, num):
    group, num = int(group), int(num)
    if site in NORMAL_NUMBERING: return num
    elif site in {'Gray Fox'}: return num + ((20 * group) - 20)
    elif site in {'Bishopville II'}: return num + ((9 * group) - 9)
    elif site in {'Wellons'}: return num + ((2 * group) - 2)
    return num

def fast_mean(iterable):
    valid = [x for x in iterable if x is not None]
    return sum(valid) / len(valid) if valid else 0

class AEDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Site Data")
        self.root.configure(bg=MAIN_COLOR)
        self._set_window_icon(self.root)
        
        # Determine Hostname and Database Target
        self.sql_pc = True if get_hostname() == "NAR-OMOPSXPS" else False
        if not self.sql_pc:
            self.local_db = messagebox.askyesno(
                title="SQL Server Selection", 
                message="Yes for Localhost, No for VPN and Office Server Connection."
            )
        else:
            self.local_db = False
            
        # State Variables
        self.is_fetching = False # Synchronization flag for background thread
        self.site_widgets = {}
        self.all_cbs = []
        self.cached_table_names = []
        self.device_states = {}
        self.raw_ghi_data = {}
        self.last_online_cache = {}
        self.inv_online_since = {}
        self.last_closed_cache = {}
        self.last_good_comm_cache = {}
        self.meter_last_online_cache = {}
        self.pvsyst_model_cache = {}
        self.pvsyst_results = {} # Computed in background thread
        self.text_update_table = []
        
        # Site Configuration Map
        self.MAP_SITES = MAP_SITES_HARDWARE_GUI
        self.sites_per_col = 21
        
        # UI Setup
        self._setup_main_window()
        self._setup_peripheral_windows()
        self._setup_inverter_windows()
        self._populate_inverter_checkboxes()
        
        # Start lifecycle
        self.load_checkbox_states()
        self.root.after(500, self.run_data_cycle)

    def _check_null_states(self, data):
        all_null = False
        watts_null_other_has_value = False
        if data and len(data[0]) > 0:
            excluded_cols = {'timestamp', 'last upload', 'hardwareid'}
            data_cols = [i for i, col in enumerate(data[0].cursor_description) if col[0].lower() not in excluded_cols]
            watts_col = next((i for i, col in enumerate(data[0].cursor_description) if col[0].lower() == 'watts'), -1)
            if data_cols:
                all_null = all(data[0][i] is None for i in data_cols)
                if watts_col != -1:
                    watts_null_other_has_value = (data[0][watts_col] is None and any(data[0][i] is not None for i in data_cols if i != watts_col))
        return all_null, watts_null_other_has_value

    def _set_window_icon(self, window):
        """Helper to apply the program icon to a window."""
        try:
            window.iconbitmap(ICON_PATH)
        except Exception:
            pass

    def _setup_main_window(self):
        """Builds the main grid headers and site rows dynamically."""
        headers = ["Sites", "Breaker", "Utility V", "Meter kW", "% Max", "% PvSyst", "W/S", "Site Overview"]
        
        # Calculate how many column blocks are needed
        total_sites = len(self.MAP_SITES)
        num_blocks = (total_sites - 1) // self.sites_per_col + 1
        
        # Draw headers for each block
        for block in range(num_blocks):
            col_offset = block * 8
            for i, h in enumerate(headers):
                Label(self.root, bg=MAIN_COLOR, text=h, font=('Tk_defaultFont', 10, 'bold')).grid(row=0, column=col_offset + i, padx=5)

            # Tell Tkinter to let the Snapshot column absorb all extra horizontal space
            self.root.grid_columnconfigure(col_offset + 7, weight=1)

        for i, (name, config) in enumerate(self.MAP_SITES.items(), 1):
            self._create_site_row(i, name, config)

    def _create_site_row(self, index, name, config):
        # Calculate which block (column group) this site belongs to (0-indexed)
        block = (index - 1) // self.sites_per_col
        
        # Calculate the actual grid row (1-indexed to account for headers at row 0)
        row = ((index - 1) % self.sites_per_col) + 1
        
        # Calculate the column offset (each block is 8 columns wide)
        col_offset = block * 8
        
        var_name = config['VAR_NAME']
        self.site_widgets[var_name] = {'inverters': {}, 'config': config}
        
        # Site Name
        site_suppress_var = IntVar()
        self.all_cbs.append(site_suppress_var)
        Checkbutton(self.root, bg=MAIN_COLOR, text=name, font=('Tk_defaultFont', 12, 'bold'), anchor='w', variable=site_suppress_var, command=self.save_checkbox_states).grid(row=row, column=col_offset, sticky='w')
        self.site_widgets[var_name]['site_suppress_var'] = site_suppress_var
        
        # Breaker Status
        if config['BREAKER']:
            if name == 'Violet':
                bf = Frame(self.root, bg=MAIN_COLOR)
                bf.grid(row=row, column=col_offset + 1, sticky='nsew')
                self.site_widgets[var_name]['status_label_1'] = Label(bf, bg=MAIN_COLOR, text='❌', fg='black')
                self.site_widgets[var_name]['status_label_1'].grid(row=0, column=0, sticky='nsew')
                self.site_widgets[var_name]['status_label_2'] = Label(bf, bg=MAIN_COLOR, text='❌', fg='black')
                self.site_widgets[var_name]['status_label_2'].grid(row=1, column=0, sticky='nsew')
                
                # Attach ToolTips
                self.site_widgets[var_name]['breaker_tt_1'] = ToolTip(self.site_widgets[var_name]['status_label_1'], "Pending Update...")
                self.site_widgets[var_name]['breaker_tt_2'] = ToolTip(self.site_widgets[var_name]['status_label_2'], "Pending Update...")
            else:
                lbl = Label(self.root, bg=MAIN_COLOR, text='❌')
                lbl.grid(row=row, column=col_offset + 1)
                self.site_widgets[var_name]['breaker_label'] = lbl
                
                # Attach ToolTip
                self.site_widgets[var_name]['breaker_tt'] = ToolTip(lbl, "Pending Update...")

        # Utility Voltage
        v_lbl = Label(self.root, bg=MAIN_COLOR, text='V')
        v_lbl.grid(row=row, column=col_offset + 2)
        self.site_widgets[var_name]['v_label'] = v_lbl
        self.site_widgets[var_name]['v_tt'] = ToolTip(v_lbl, "Pending Update...")

        # Suppress Alerts Checkbox + Meter kW (Combined)
        meter_suppress_var = IntVar()
        self.all_cbs.append(meter_suppress_var)
        kw_lbl = Checkbutton(self.root, bg=MAIN_COLOR, text='kW', font=('Tk_defaultFont', 10, 'bold'), variable=meter_suppress_var, command=self.save_checkbox_states, selectcolor=MAIN_COLOR)
        kw_lbl.grid(row=row, column=col_offset + 3)
        self.site_widgets[var_name]['meter_suppress_var'] = meter_suppress_var
        self.site_widgets[var_name]['kw_label'] = kw_lbl
        self.site_widgets[var_name]['kw_tt'] = ToolTip(kw_lbl, "Pending Update...")

        # % Max & % PvSyst
        self.site_widgets[var_name]['ratio_label'] = Label(self.root, bg=MAIN_COLOR, text='0%', font=('Tk_defaultFont', 10, 'bold'))
        self.site_widgets[var_name]['ratio_label'].grid(row=row, column=col_offset + 4)
        self.site_widgets[var_name]['pvsyst_label'] = Label(self.root, bg=MAIN_COLOR, text='--', font=('Tk_defaultFont', 10, 'bold'))
        self.site_widgets[var_name]['pvsyst_label'].grid(row=row, column=col_offset + 5)

        # POA Weather
        poa_var = IntVar()
        self.all_cbs.append(poa_var)
        poa_btn = Checkbutton(self.root, bg=MAIN_COLOR, text='0', font=( 'Tk_defaultFont', 10, 'bold'), variable=poa_var)
        poa_btn.grid(row=row, column=col_offset + 6)
        self.site_widgets[var_name]['poa_btn'] = poa_btn
        self.site_widgets[var_name]['poa_var'] = poa_var
        self.site_widgets[var_name]['poa_tt'] = ToolTip(poa_btn, "Pending Update...")

        # Snapshot Frame Setup
        snap = Frame(self.root, bg=MAIN_COLOR, bd=1, relief="solid")
        self.site_widgets[var_name]['snap_tt'] = ToolTip(snap, "INV kW  |  Meter-INVs  |  # INVs ✅\nMeter kW  |  No Comms  |  Total INVs")
        snap.grid(row=row, column=col_offset + 7, sticky='ew')
        snap.columnconfigure(0, weight=1)
        snap.columnconfigure(1, weight=1)
        snap.columnconfigure(2, weight=1)
        self.site_widgets[var_name]['snap_frame'] = snap
        self.site_widgets[var_name]['inv_kw_total'] = Label(snap, bg=MAIN_COLOR, text='INV kW', font=('Tk_defaultFont', 9, 'bold'))
        self.site_widgets[var_name]['inv_kw_total'].grid(row=0, column=0, sticky='ew')
        self.site_widgets[var_name]['meter_inv_diff'] = Label(snap, bg=MAIN_COLOR, text='Meter-INVs', font=('Tk_defaultFont', 9, 'bold'))
        self.site_widgets[var_name]['meter_inv_diff'].grid(row=0, column=1, sticky='ew')
        self.site_widgets[var_name]['invs_online'] = Label(snap, bg=MAIN_COLOR, text='# INVs ✅', font=('Tk_defaultFont', 9, 'bold'))
        self.site_widgets[var_name]['invs_online'].grid(row=0, column=2, sticky='ew')
        self.site_widgets[var_name]['meter_kw_snap'] = Label(snap, bg=MAIN_COLOR, text='Meter kW', font=('Tk_defaultFont', 9, 'bold'))
        self.site_widgets[var_name]['meter_kw_snap'].grid(row=1, column=0, sticky='ew')
        self.site_widgets[var_name]['invs_no_comms'] = Label(snap, bg=MAIN_COLOR, text='No Comms', font=('Tk_defaultFont', 9, 'bold'))
        self.site_widgets[var_name]['invs_no_comms'].grid(row=1, column=1, sticky='ew')
        self.site_widgets[var_name]['invs_total'] = Label(snap, bg=MAIN_COLOR, text='Total INVs', font=('Tk_defaultFont', 9, 'bold'))
        self.site_widgets[var_name]['invs_total'].grid(row=1, column=2, sticky='ew')

    def _setup_peripheral_windows(self):
        # Alert Window
        self.alert_win = Toplevel(self.root)
        self.alert_win.title("Alert Windows Info")
        self._set_window_icon(self.alert_win)
        
        notesFrame = Frame(self.alert_win)
        notesFrame.grid(row=0, column=0, sticky=EW)
        Label(notesFrame, text="1st Checkbox: ✓ = Open WO\n& pauses inv notifications", font=("Calibri", 12)).pack()
        Label(notesFrame, text="GUI Last Updated", font=("Calibri", 18)).pack()
        self.timmy_label = Label(notesFrame, text="--:--", font=("Calibri", 30))
        self.timmy_label.pack()
        Button(notesFrame, command=self.check_button_notes, text="Checkbutton Notes", font=("Calibri", 14), bg=MAIN_COLOR, cursor='hand2').pack(padx=2, pady=2, fill=X)
        Button(notesFrame, command=self.open_file, text="Procedure Doc", font=("Calibri", 14), cursor='hand2').pack(padx=2, pady=2, fill=X)
        Button(notesFrame, command=self.parse_wo, text="Assess Open WO's", font=("Calibri", 14), cursor='hand2').pack(padx=2, pady=2, fill=X)

        notificationFrame = Frame(self.alert_win)
        notificationFrame.grid(row=0, column=1, sticky=N)
        Label(notificationFrame, text="Notification Settings", font=("Calibri", 14)).pack()
        self.text_only_var = IntVar()
        self.all_cbs.append(self.text_only_var)
        Checkbutton(notificationFrame, text="Send Emails\n(Disable Local MsgBox's)", variable=self.text_only_var, cursor='hand2', command=self.save_checkbox_states).pack(padx=2)
        self.admin_var = StringVar(value="Joseph Lang")
        self.admin_box = ttk.Combobox(notificationFrame, textvariable=self.admin_var, values=["Joseph Lang", "Brandon Arrowood", "Jacob Budd", "Administrators + NCC", "Administrators Only"], state="readonly")
        self.admin_box.pack()
        self.admin_box.current(0)
        Label(notificationFrame, text="\nSelect from the Dropdown\nBefore turning the function on\nwith the Checkbox\n").pack()

        # Time Window
        self.time_win = Toplevel(self.root)
        self.time_win.title("Timestamps")
        self._set_window_icon(self.time_win)
        
        timeW = Frame(self.time_win)
        timeW.pack(side=LEFT)
        Label(timeW, text="Data Pull Timestamps", font=("Calibri", 14)).grid(row=0, column=0, columnspan=3)
        Label(timeW, text="First:", font=("Calibri", 12)).grid(row=1, column=0, sticky=E)
        Label(timeW, text="Second:", font=("Calibri", 12)).grid(row=2, column=0, sticky=E)
        Label(timeW, text="Third:", font=("Calibri", 12)).grid(row=3, column=0, sticky=E)
        Label(timeW, text="Fourth:", font=("Calibri", 12)).grid(row=4, column=0, sticky=E)
        Label(timeW, text="Tenth:", font=("Calibri", 12)).grid(row=5, column=0, sticky=E)
        Label(timeW, text="Fifteenth:", font=("Calibri", 12)).grid(row=6, column=0, sticky=E)

        self.time1v = Label(timeW, text="Time", font=("Calibri", 12, 'bold')); self.time1v.grid(row=1, column=1, sticky=W)
        self.time2v = Label(timeW, text="Time", font=("Calibri", 12, 'bold')); self.time2v.grid(row=2, column=1, sticky=W)
        self.time3v = Label(timeW, text="Time", font=("Calibri", 12, 'bold')); self.time3v.grid(row=3, column=1, sticky=W)
        self.time4v = Label(timeW, text="Time", font=("Calibri", 12, 'bold')); self.time4v.grid(row=4, column=1, sticky=W)
        self.time10v = Label(timeW, text="Time", font=("Calibri", 12, 'bold')); self.time10v.grid(row=5, column=1, sticky=W)
        self.timeLv = Label(timeW, text="Time", font=("Calibri", 12, 'bold')); self.timeLv.grid(row=6, column=1, sticky=W)

        Label(timeW, text="MsgBox Data:", font=("Calibri", 14)).grid(row=1, column=2)
        Label(timeW, text="Inverters:", font=("Calibri", 12)).grid(row=2, column=2)
        self.spread15 = Label(timeW, text="Time")
        self.spread15.grid(row=3, column=2)
        Label(timeW, text="Breakers &\nMeters:", font=("Calibri", 12)).grid(row=4, column=2)
        self.spread10 = Label(timeW, text="Time")
        self.spread10.grid(row=5, column=2)

        # Checkin Window
        self.checkins_win = Toplevel(self.root)
        self.checkins_win.title("Personnel On-Site")
        self._set_window_icon(self.checkins_win)

        # Create a custom ttk style for the checkins Treeview
        style = ttk.Style()
        style.configure("Checkin.Treeview.Heading", font=('TkDefaultFont', 11, 'bold'))
        # Adjust rowheight, borderwidth, and relief to experiment with spacing and outer borders
        style.configure("Checkin.Treeview", font=('TkDefaultFont', 10, 'bold'), rowheight=30, borderwidth=1, relief="solid")

        self.checkins_tree = ttk.Treeview(self.checkins_win, columns=("Location", "Company", "Employee"), show='headings', style="Checkin.Treeview")
        self.checkins_tree.heading("Location", text="Location")
        self.checkins_tree.heading("Company", text="Company")
        self.checkins_tree.heading("Employee", text="Employee")
        
        self.checkins_tree.column("Location", width=250, anchor=CENTER)
        self.checkins_tree.column("Company", width=300, anchor=CENTER)
        self.checkins_tree.column("Employee", width=200, anchor=CENTER)
        
        tree_scroll = ttk.Scrollbar(self.checkins_win, orient="vertical", command=self.checkins_tree.yview)
        self.checkins_tree.configure(yscrollcommand=tree_scroll.set)
        
        tree_scroll.pack(side=RIGHT, fill=Y)
        self.checkins_tree.pack(side=LEFT, expand=True, fill=BOTH)
        
        self.checkins_tree.tag_configure('even', background='#ADD8E6')
        self.checkins_tree.tag_configure('odd', background='#90EE90')

    def _are_all_values_null(self, data, indices_to_check):
        """Checks if all specified indices in the first row of data are None."""
        if not data or not data[0]:
            return False
        return all(data[0][i] is None for i in indices_to_check)


    def _setup_inverter_windows(self):
        """Builds separate portfolio windows or a combined tabbed window depending on host."""
        self.customer_frames = {}
        
        if self.sql_pc:
            solrvr_win = Toplevel(self.root)
            solrvr_win.title("Sol River's Portfolio")
            self._set_window_icon(solrvr_win)
            solrvr_nb = ttk.Notebook(solrvr_win)
            self.customer_frames['solrvr'] = ttk.Frame(solrvr_nb)
            self.customer_frames['solrvr2'] = ttk.Frame(solrvr_nb)
            solrvr_nb.add(self.customer_frames['solrvr'], text="Bulloch 1A - Sunflower")
            solrvr_nb.add(self.customer_frames['solrvr2'], text="Upson - Williams")
            solrvr_nb.pack(expand=True, fill='both')
            
            hst_win = Toplevel(self.root)
            hst_win.title("Harrison Street's Portfolio")
            self._set_window_icon(hst_win)
            hst_nb = ttk.Notebook(hst_win)
            self.customer_frames['hst'] = ttk.Frame(hst_nb)
            hst_nb.add(self.customer_frames['hst'], text="Bishopville II - Van Buren")
            hst_nb.pack(expand=True, fill='both')
            
            nar_win = Toplevel(self.root)
            nar_win.title("NARENCO's Portfolio")
            self._set_window_icon(nar_win)
            nar_nb = ttk.Notebook(nar_win)
            self.customer_frames['nar'] = ttk.Frame(nar_nb)
            nar_nb.add(self.customer_frames['nar'], text="Bluebird - Violet")
            nar_nb.pack(expand=True, fill='both')
            
            soltage_win = Toplevel(self.root)
            soltage_win.title("Soltage")
            self._set_window_icon(soltage_win)
            self.customer_frames['soltage'] = ttk.Frame(soltage_win)
            self.customer_frames['soltage'].pack(expand=True, fill='both')
            
            ncemc_win = Toplevel(self.root)
            ncemc_win.title("NCEMC")
            self._set_window_icon(ncemc_win)
            self.customer_frames['ncemc'] = ttk.Frame(ncemc_win)
            self.customer_frames['ncemc'].pack(expand=True, fill='both')
        else:
            inv_win = Toplevel(self.root)
            inv_win.title("Inverter's Portfolio")
            self._set_window_icon(inv_win)
            notebook = ttk.Notebook(inv_win)
            
            self.customer_frames['nar'] = ttk.Frame(notebook)
            self.customer_frames['hst'] = ttk.Frame(notebook)
            self.customer_frames['soltage'] = ttk.Frame(notebook)
            self.customer_frames['ncemc'] = ttk.Frame(notebook)
            self.customer_frames['solrvr'] = ttk.Frame(notebook)
            self.customer_frames['solrvr2'] = ttk.Frame(notebook)
            
            notebook.add(self.customer_frames['nar'], text="NARENCO")
            notebook.add(self.customer_frames['hst'], text="Harrison Street")
            notebook.add(self.customer_frames['soltage'], text="Soltage")
            notebook.add(self.customer_frames['ncemc'], text="NCEMC")
            notebook.add(self.customer_frames['solrvr'], text="Bulloch 1A - Shorthorn")
            notebook.add(self.customer_frames['solrvr2'], text="Sunflower - Whitetail")
            notebook.pack(expand=True, fill='both')

    def _populate_inverter_checkboxes(self):
        """Grids the specific checkboxes/status blocks into the assigned customer windows/frames."""
        col_trackers = {k: 1 for k in self.customer_frames.keys()}
        
        for name, config in self.MAP_SITES.items():
            var_name = config['VAR_NAME']
            cust_key = config.get('CUST_ID', 'nar')
            parent_frame = self.customer_frames[cust_key]
            invdict = config['INV_DICT']
            invnum = len(invdict)
            
            if name == 'CDIA': continue
                
            col = col_trackers[cust_key]
            if self.sql_pc:
                length_limit = 73
                span_col = 6 if invnum > length_limit else 3
            else:
                length_limit = 38
                span_col = 9 if invnum > length_limit * 2 else (6 if invnum > length_limit else 3)
                
            btn = Button(parent_frame, text=name, bg=MAIN_COLOR, font=("Tk_defaultFont", 12, 'bold'))
            btn.grid(row=0, column=col, columnspan=span_col, sticky='ew')
            
            for num in range(1, invnum + 1):
                inv_val = str(invdict.get(num, num))
                
                if self.sql_pc:
                    column_offset = 0 if num <= length_limit else 3
                    row_offset = num if num <= length_limit else num - length_limit
                else:
                    block_number = (num - 1) // length_limit
                    column_offset = block_number * 3
                    row_offset = (num - 1) % length_limit + 1
                    
                cb_var = IntVar()
                self.all_cbs.append(cb_var)
                cb = Checkbutton(parent_frame, text=str(inv_val), variable=cb_var, command=self.save_checkbox_states)
                cb.grid(row=row_offset, column=col + column_offset, sticky=W)
                
                cb_tt = ToolTip(cb, "Pending Update...")
                
                wo_label = Label(parent_frame, text='⬜')
                wo_label.grid(row=row_offset, column=col + 1 + column_offset)
                
                if str(inv_val) not in self.site_widgets[var_name]['inverters']:
                    self.site_widgets[var_name]['inverters'][str(inv_val)] = {}
                    
                self.site_widgets[var_name]['inverters'][str(inv_val)].update({
                    'cb_val': cb_var,
                    'cb': cb,
                    'cb_tt': cb_tt,
                    'wo_label': wo_label
                })
                
                if name != "Conetoe":
                    up_cb_var = IntVar()
                    self.all_cbs.append(up_cb_var)
                    Checkbutton(parent_frame, variable=up_cb_var, command=self.save_checkbox_states).grid(row=row_offset, column=col + 2 + column_offset, sticky=W)
                else:
                    if num < 5:
                        up_cb_var = IntVar()
                        self.all_cbs.append(up_cb_var)
                        Checkbutton(parent_frame, variable=up_cb_var, command=self.save_checkbox_states).grid(row=(4 * row_offset - 3), rowspan=4, column=col + 2 + column_offset, sticky=W)
            
            col_trackers[cust_key] += span_col

    # --- UI Helpers for Alert Window ---
    def check_button_notes(self):
        msg = ("The First column of CheckButtons in the Site Data Window turns off all notifications associated with that Site.\n\n"
               "The POA CB will change the value to 9999 so that no inv outages are filtered by the POA.\n\n"
               "The colored INV CheckButtons are to be selected when a WO is open for that device and will turn off notifications of outages with INV.\n\n"
               "The Box in the middle Represents the Status of that device in Emaint. | ⬜ = NO WO | Black BG = Offline WO Open | Blue BG = Underperformance WO Open | Pink BG = Comms Outage WO Open | Yellow BG = Unknown WO Found |\n\n"
               "The 3rd Column is a CB for Underperformance tracking.")
        messagebox.showinfo(parent=self.alert_win, title="Checkbutton Info", message=msg)

    def open_file(self):
        try:
            os.startfile(r"G:\Shared drives\Narenco Projects\O&M Projects\NCC\Procedures\NCC Tools - Joseph\Also Energy GUI Interactions - How To.docx")
        except Exception as e:
            print(f"Could not open file: {e}")

    def parse_wo(self):
        dir_path = r"G:\Shared drives\O&M\NCC Automations\Notification System\WO Tracking\\"
        for f in glob.glob(os.path.join(dir_path, "*.txt")):
            try: os.remove(f)
            except: pass
        
        file_path = filedialog.askopenfilename(parent=self.alert_win, title="Select WO Excel", filetypes=[("Excel", "*.xlsx *.xls")], initialdir="C:\\Users\\OMOPS\\Downloads")
        if not file_path: return
        
        df = pd.read_excel(file_path)
        inv_pat = re.compile(r"(?:inverter|inv)\s*(\d+)?(?:-|\.)?(\d+)?")
        
        for _, row in df.iterrows():
            site = str(row['Site'])
            if pd.isna(site) or site in {"Charter GM", "Charter RM", "Charter Roof"}: continue
            
            vn = site.lower().replace(", llc", "").replace("farm", "").replace("cadle", "").replace("solar", "").replace(" ", "").replace("freightline", "freightliner")
            if site == "BISHOPVILLE": vn = 'bishopvilleII'
            
            if 'inv' in str(row['Asset Description']).lower() or 'inv' in str(row['Brief Description']).lower():
                m = inv_pat.search(str(row['Brief Description']).lower())
                if m:
                    g = int(m.group(1)) if m.group(1) else None
                    n = int(m.group(2)) if m.group(2) else g
                    if g is None or n is None: continue
                    
                    inv_num = define_inv_num(site, g, n)
                    if inv_num and vn in self.site_widgets:
                        inv_val = self.MAP_SITES.get(site, {}).get('INV_DICT', {}).get(inv_num)
                        if inv_val and str(inv_val) in self.site_widgets[vn]['inverters']:
                            lbl = self.site_widgets[vn]['inverters'][str(inv_val)]['wo_label']
                            err = row['Fault Code Category']
                            
                            clr = 'gray' if lbl.cget('bg') in ['black', 'blue'] else 'blue' if err == 'Underperformance' else 'black' if err == 'Equipment Outage' else 'pink' if err == 'COMMs Outage' else 'yellow'
                            lbl.config(bg=clr)
                            
                        with open(os.path.join(dir_path, f"{vn} Open WO's.txt"), 'a+') as f:
                            f.write(f"{inv_num:<5}| WO: {row['WO No.']:<8}| {row['WO Date']} | {row['Brief Description']}\n")

    def _trigger_alert(self, title, msg):
        #print(msg)
        if self.text_only_var.get():
            self.text_update_table.append(f"<br><b>{title}</b>: {msg}")
            #print(self.text_update_table)
        else:
            messagebox.showwarning(parent=self.alert_win, title=title, message=msg)


    # =========================================================================
    # --- Multithreading Background Tasks & DB Connectivity ---
    # =========================================================================

    def connect_db(self):
        if self.local_db:
            conn_str = (r"DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost\SQLEXPRESS;"
                        r"DATABASE=NARENCO_O&M_AE;Trusted_Connection=yes;Encrypt=no;")
        else:
            conn_str = (f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={CREDS['DB_IP']}\\SQLEXPRESS;"
                        f"DATABASE=NARENCO_O&M_AE;UID={CREDS['DB_UID']};PWD={CREDS['DB_PWD']};Encrypt=no;")
        db = pyodbc.connect(conn_str)
        return db.cursor(), db
    
    def _get_last_closed_bg(self, cursor, site, breaker_num=None, trigger='breaker'):
        try:
            last_online = None
            if trigger == 'meter':
                # Query for last time meter had production (non-zero amps)
                meter_q = f"SELECT TOP 1 [Timestamp] FROM [{site} Meter Data] WHERE [Amps A] <> 0 AND [Amps B] <> 0 AND [Amps C] <> 0 ORDER BY [Timestamp] DESC"
                cursor.execute(meter_q)
                meter_data = cursor.fetchone()
                last_online = meter_data[0] if meter_data else None
            else:  # Default to 'breaker' trigger
                brk_ts = None
                if site == "Violet" and breaker_num:
                    cursor.execute(f"SELECT TOP 1 [Timestamp] FROM [{site} Breaker Data {breaker_num}] WHERE [Status] = 1 ORDER BY [Timestamp] DESC")
                    brk_data = cursor.fetchone()
                    brk_ts = brk_data[0] if brk_data else None
                else:
                    try:
                        cursor.execute(f"SELECT TOP 1 [Timestamp] FROM [{site} Breaker Data] WHERE [Status] = 1 ORDER BY [Timestamp] DESC")
                        brk_data = cursor.fetchone()
                        brk_ts = brk_data[0] if brk_data else None
                    except pyodbc.ProgrammingError:
                        pass # Table doesn't exist, which is fine.
                last_online = brk_ts

            return f"{last_online}" if last_online else "Unknown"
        except Exception as e:
            print(f"Error in _get_last_closed_bg for {site} (trigger: {trigger}): {e}")
            return "Unknown"

    def _get_last_non_null_timestamp_bg(self, cursor, table_name):
        """Finds the timestamp of the last row with non-null data."""
        try:
            q = f"SELECT TOP 1 [Timestamp] FROM [{table_name}] WHERE [Watts] IS NOT NULL AND [dc V] IS NOT NULL ORDER BY [Timestamp] DESC"
            cursor.execute(q)
            data = cursor.fetchone()
            return data[0] if data else None
        except Exception as e:
            print(f"Error getting last non-null timestamp for {table_name}: {e}")
            return None

    def _get_meter_last_online_bg(self, cursor, site):
        try:
            q = f"SELECT TOP 1 [Timestamp] FROM (SELECT [Timestamp], [Watts], LEAD([Watts], 1) OVER(ORDER BY [Timestamp] DESC) as Watts_1, LEAD([Watts], 2) OVER(ORDER BY [Timestamp] DESC) as Watts_2 FROM [{site} Meter Data]) sub WHERE [Watts] > 2 AND Watts_1 > 2 AND Watts_2 > 2 ORDER BY [Timestamp] DESC"
            cursor.execute(q)
            data = cursor.fetchone()
            return f"{data[0]}" if data else "Unknown"
        except Exception:
            return "Unknown"

    def _get_last_online_bg(self, cursor, site, inv_n, duplin_except):
        try:
            q = f"SELECT TOP 1 [Timestamp] FROM (SELECT [Timestamp], [Watts], LEAD([Watts], 1) OVER(ORDER BY [Timestamp] DESC) as Watts_1, LEAD([Watts], 2) OVER(ORDER BY [Timestamp] DESC) as Watts_2 FROM [{site}{duplin_except} INV {inv_n} Data]) sub WHERE [Watts] > 2 AND Watts_1 > 2 AND Watts_2 > 2 ORDER BY [Timestamp] DESC"
            cursor.execute(q)
            data = cursor.fetchone()
            return f"{data[0]}" if data else "Unknown"
        except Exception as e:
            print(f"Error fetching last online for {site} INV {inv_n}: {e}")
            return "Unknown"

    def _fetch_raw_data_bg(self, cursor):
        raw_inv, raw_meter, raw_poa, raw_ghi, raw_breaker = {}, {}, {}, {}, {}
        if not self.cached_table_names:
            self.cached_table_names = [t.table_name for t in cursor.tables(tableType='TABLE') if 'Data' in t.table_name]

        for table in self.cached_table_names:
            if "INV" in table:
                # ADDED [Last Upload] to the SQL query
                cursor.execute(f"SELECT TOP 16 [dc V], Watts, [Last Upload] FROM [{table}] ORDER BY Timestamp DESC")
                raw_inv[table] = cursor.fetchall()
            elif "Meter" in table:
                cursor.execute(f"SELECT TOP 16 [Volts A], [Volts B], [Volts C], [Amps A], [Amps B], [Amps C], Watts, [Last Upload] FROM [{table}] ORDER BY Timestamp DESC")
                raw_meter[table] = cursor.fetchall()
            elif "POA" in table:
                cursor.execute(f"SELECT TOP 1 [W/M²], [Last Upload] FROM [{table}] ORDER BY Timestamp DESC")
                raw_poa[table] = cursor.fetchone()
            elif "GHI" in table:
                cursor.execute(f"SELECT TOP 1 [W/M²], [Last Upload] FROM [{table}] ORDER BY Timestamp DESC")
                raw_ghi[table] = cursor.fetchone()
            elif "Breaker" in table:
                cursor.execute(f"SELECT TOP 6 [Status], [Last Upload] FROM [{table}] ORDER BY Timestamp DESC")
                raw_breaker[table] = cursor.fetchall()

        return raw_inv, raw_meter, raw_poa, raw_ghi, raw_breaker

    def _fetch_timestamps_bg(self, cursor):
        try:
            cursor.execute("SELECT TOP 16 [Timestamp] FROM [Ogburn Meter Data] ORDER BY [Timestamp] DESC")
            return [r[0] for r in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching timestamps: {e}")
            return []

    def _fetch_checkins_bg(self):
        data = []
        try:
            lbconn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=G:\Shared drives\O&M\NCC\NCC 039.accdb;'
            conn = pyodbc.connect(lbconn_str)
            cur = conn.cursor()
            cur.execute("SELECT Location, Company, Employee FROM [Checked In]")
            data = [list(row) for row in cur.fetchall()]
            conn.close()
        except Exception as e:
            print(f"Logbook access DB error: {e}")
        return data

    def _calculate_pvsyst_bg(self, meterval, poa_val, pvsyst_name):
        """Fetches PVsyst data from Access DB in the Background, calculates expected production."""
        if not pvsyst_name or poa_val == 9999 or poa_val <= 0:
            return 0
            
        if pvsyst_name not in ["WELLONS", "FREIGHTLINE", "WARBLER", "PG", "HOLLYSWAMP"]:
            meterval = meterval / 1000.0

        if pvsyst_name not in self.pvsyst_model_cache:
            pvsyst_db = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=G:\Shared drives\O&M\NCC Automations\Notification System\PVsyst (Josephs Edits).accdb;'
            try:
                conn = pyodbc.connect(pvsyst_db)
                cursor = conn.cursor()
                query = "SELECT [GlobInc_WHSQM], [EGrid_KWH] FROM [PVsystHourly] WHERE [PlantName] = ?"
                
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    slope_df = pd.read_sql_query(query, conn, params=[pvsyst_name])
                
                if slope_df.empty:
                    conn.close()
                    return 0

                X = slope_df['GlobInc_WHSQM'].values.reshape(-1, 1)
                y = slope_df['EGrid_KWH'].values
                model = LinearRegression().fit(X, y)
                
                cursor.execute("SELECT TOP 1 [SimulationDate] FROM [PVsystHourly] WHERE [PlantName] = ?", pvsyst_name)
                sim_date_row = cursor.fetchone()
                sim_date = sim_date_row[0] if sim_date_row else datetime.now()
                
                self.pvsyst_model_cache[pvsyst_name] = (model.coef_[0], model.intercept_, sim_date)
                conn.close()
            except Exception as e:
                print(f"PVsyst Error for {pvsyst_name}: {e}")
                return 0

        slope, intercept, sim_date = self.pvsyst_model_cache[pvsyst_name]
        meter_est = slope * poa_val + intercept

        if meter_est <= 0: return 0

        try:
            degrad = ((datetime.now() - sim_date).days / 365.25) * 0.005
            meter_estdegrad = meter_est * (1 - degrad)
            performance = (meterval / meter_estdegrad) * 100
            return performance
        except Exception:
            return 0

    def _background_fetch_task(self, poa_states):
        """Executed entirely in a background thread to prevent Tkinter freezing."""
        self.is_fetching = True
        success = False
        try:
            cursor, conn = self.connect_db()

            # 1. Fetch raw data
            raw_inv, raw_meter, raw_poa, raw_ghi, raw_breaker = self._fetch_raw_data_bg(cursor)

            # 2. Fetch Timestamps
            timestamps_data = self._fetch_timestamps_bg(cursor)

            # 3. Fetch Checkins
            checkins_data = self._fetch_checkins_bg()

            # 4. Pre-calculate metrics that require DB (PVsyst and Offline checks)
            pvsyst_results = {}
            fetched_offline = {'breakers': {}, 'meters': {}, 'invs': {}, 'last_good_comms': {}}

            for name, config in self.MAP_SITES.items():
                var_name = config['VAR_NAME']
                poa_btn_val = poa_states.get(name, 0)

                # POA
                poa_data = raw_poa.get(f"{name} POA Data")
                poa_val = poa_data[0] if poa_data and poa_data[0] is not None else 0
                if poa_btn_val == 1: poa_val = 9999

                # Meter Avg
                meter_data = raw_meter.get(f"{name} Meter Data", [])
                avg_w = fast_mean(row[6] for row in meter_data if row[6] is not None and row[6] < 760000000)

                # PVsyst Ratio Precomputation
                pvsyst_name = config.get('PVSYST')
                perf_ratio = self._calculate_pvsyst_bg(avg_w, poa_val, pvsyst_name)
                pvsyst_results[name] = perf_ratio

                # Evaluate Database requirements for device offline times
                # Breakers
                if config['BREAKER']:
                    # Check for meter-indicated open state, mirroring _update_breakers logic
                    meter_data_for_breaker = raw_meter.get(f"{name} Meter Data", [])
                    meter_indicates_open = False
                    if meter_data_for_breaker:
                        # Check if at least 2 of the last 8 readings have a zero amp phase
                        zero_amp_rows = sum(1 for row in meter_data_for_breaker[:8] if row and len(row) > 5 and any(row[i] == 0 for i in (3, 4, 5)))
                        if zero_amp_rows >= 2:
                            meter_indicates_open = True

                    if name == 'Violet':
                        for i in (1, 2):
                            breaker_data = raw_breaker.get(f"{name} Breaker Data {i}", [])
                            physically_closed = any(row[0] for row in breaker_data) if breaker_data else False
                            
                            is_open_by_breaker = not physically_closed
                            is_open_by_meter = physically_closed and meter_indicates_open
                            
                            cache_key = f"{name}_{i}"
                            if (is_open_by_breaker or is_open_by_meter) and cache_key not in self.last_closed_cache:
                                trigger = 'breaker' if is_open_by_breaker else 'meter'
                                fetched_offline['breakers'][cache_key] = self._get_last_closed_bg(cursor, name, breaker_num=i, trigger=trigger)
                    else:
                        breaker_data = raw_breaker.get(f"{name} Breaker Data", [])
                        physically_closed = any(row[0] for row in breaker_data) if breaker_data else False
                        
                        is_open_by_breaker = not physically_closed
                        is_open_by_meter = physically_closed and meter_indicates_open

                        if (is_open_by_breaker or is_open_by_meter) and name not in self.last_closed_cache:
                            trigger = 'breaker' if is_open_by_breaker else 'meter'
                            fetched_offline['breakers'][name] = self._get_last_closed_bg(cursor, name, trigger=trigger)

                # Meters
                if avg_w < 2 and (poa_val >= 100 or (poa_val == 9999 and datetime.now().hour >= 8)) and name not in self.meter_last_online_cache:
                    fetched_offline['meters'][name] = self._get_meter_last_online_bg(cursor, name)

                # Inverters
                invdict = config['INV_DICT']
                for inv_num, inv_label in invdict.items():
                    duplin_except = (' Central' if inv_num <= 3 else ' String') if name == 'Duplin' else ''
                    inv_n = inv_num if name != 'Duplin' else (inv_num if inv_num <= 3 else inv_num - 3)
                    table_name = f'{name}{duplin_except} INV {inv_n} Data'
                    data = raw_inv.get(table_name, [])

                    # Check for sustained NULL data
                    if self._are_all_values_null(data, [0, 1]):
                        cache_key = f"{name}_{inv_num}"
                        fetched_offline['last_good_comms'][cache_key] = self._get_last_non_null_timestamp_bg(cursor, table_name)

                    last_comm_ts = data[0][2] if data and len(data[0]) > 2 else None
                    is_offline_or_null = all(row[1] is None or row[1] < 1 for row in data) if data else True
                    if is_offline_or_null:
                        cache_key = f"{name}_{inv_num}"
                        if cache_key not in self.last_online_cache:
                            fetched_offline['invs'][cache_key] = self._get_last_online_bg(cursor, name, inv_n, duplin_except)
            # Package all gathered data for main thread
            bg_data = {
                'raw_inv': raw_inv, 'raw_meter': raw_meter, 'raw_poa': raw_poa, 'raw_ghi': raw_ghi, 'raw_breaker': raw_breaker,
                'timestamps': timestamps_data, 'checkins': checkins_data, 'pvsyst_results': pvsyst_results,
                'fetched_offline': fetched_offline
            }

            # Ship back to main thread safely
            self.root.after(0, self._apply_ui_updates, bg_data)
            success = True
            
        except Exception as e:
            print(f"Background Fetch Thread Error: {e}")
        finally:
            if 'conn' in locals() and conn: 
                try: conn.close()
                except: pass
            
            # Failsafe loop restart if something fatally breaks inside background thread
            if not success:
                self.root.after(60000, self.run_data_cycle)
                
            self.is_fetching = False

    def run_data_cycle(self):
        """Timer entry point -> Spawns background thread."""
        if get_hostname() != "NAR-JosephLang":
            now = datetime.now()
            day_of_week = now.weekday()
            if (day_of_week > 4 and now.hour > 15) or now.hour > 20:
                restart_pc()

        if self.is_fetching:
            print("Background process is currently running. Skipping this cycle execution.")
            return

        print("Initiating Background Fetch Cycle...")
        # Gather states that are needed before creating the thread (Safest practice)
        poa_states = {name: self.site_widgets[config['VAR_NAME']]['poa_var'].get() for name, config in self.MAP_SITES.items()}
        
        threading.Thread(target=self._background_fetch_task, args=(poa_states,), daemon=True).start()

    # =========================================================================
    # --- Main Thread UI Applicators ---
    # =========================================================================

    def _apply_ui_updates(self, bg_data):
        """Runs on main thread via root.after(), applies fetched background data to the UI."""
        # 1. Update Instance Data dicts
        self.raw_inv_data = bg_data['raw_inv']
        self.raw_meter_data = bg_data['raw_meter']
        self.raw_poa_data = bg_data['raw_poa']
        self.raw_ghi_data = bg_data['raw_ghi']
        self.raw_breaker_data = bg_data['raw_breaker']
        
        self.pvsyst_results = bg_data['pvsyst_results']

        # 2. Add any newly fetched offline timestamps to caches
        self.last_closed_cache.update(bg_data['fetched_offline']['breakers'])
        self.meter_last_online_cache.update(bg_data['fetched_offline']['meters'])
        self.last_online_cache.update(bg_data['fetched_offline']['invs'])
        self.last_good_comm_cache.update(bg_data['fetched_offline']['last_good_comms'])

        # 3. Apply individual frame pieces
        self._apply_timestamps(bg_data['timestamps'])
        self._apply_checkins(bg_data['checkins'])

        # 4. Trigger UI component updates
        self.refresh_ui()
        
        # 5. Schedule Next Cycle
        now = datetime.now()
        target_time = time(8, 30)
        if self.text_only_var.get(): delay_ms = 420000
        elif now.time() < target_time: delay_ms = 300000
        else: delay_ms = 60000
            
        self.root.after(delay_ms, self.run_data_cycle)

    def _apply_timestamps(self, ts):
        if len(ts) >= 16:
            for i, lbl in enumerate([self.time1v, self.time2v, self.time3v, self.time4v, None, None, None, None, None, self.time10v, None, None, None, None, self.timeLv]):
                if lbl: lbl.config(text=ts[i].strftime('%H:%M'))
            self.spread10.config(text=f"5 Pulls\n{round((ts[0]-ts[4]).total_seconds()/60, 2)} Minutes")
            self.spread15.config(text=f"15 Pulls\n{round((ts[0]-ts[14]).total_seconds()/60, 2)} Minutes")

    def _apply_checkins(self, data):
        for item in self.checkins_tree.get_children():
            self.checkins_tree.delete(item)
        for row_idx, row in enumerate(data):
            formatted_row = []
            for val in row:
                formatted_row.append(val.strftime('%m/%d/%y') if isinstance(val, datetime) else val)
            tag = 'even' if row_idx % 2 == 0 else 'odd'
            self.checkins_tree.insert('', 'end', values=formatted_row, tags=(tag,))

    def refresh_ui(self):
        """Processes the synchronized data directly to UI widgets."""
        self.text_update_table = ["<html><body><h2>GUI Update</h2>"]
        now = datetime.now()
        
        for name, config in self.MAP_SITES.items():
            var_name = config['VAR_NAME']
            poa = self._update_poa(name, var_name)
            
            if config['BREAKER']: 
                self._update_breakers(name, var_name)
                
            meter_w = self._update_meters(name, var_name, poa)
            
            if name == "Conetoe":
                self._update_conetoe_inverters(name, var_name, poa)
            else:
                self._update_inverters(name, var_name, poa)
            self._update_snapshots(name, var_name, meter_w)
            
        self.text_update_table.append("</body></html>")
        self.timmy_label.config(text=now.strftime("%H:%M"))
        
        if self.text_only_var.get(): 
            self._handle_notifications()

    def _update_poa(self, site, var):
        poa_data = self.raw_poa_data.get(f"{site} POA Data")
        ghi_data = self.raw_ghi_data.get(f"{site} GHI Data")

        val = 0
        ts = None
        source = "N/A"

        poa_ts = poa_data[1] if poa_data and len(poa_data) > 1 else None
        
        use_ghi = False
        if poa_ts:
            if (datetime.now() - poa_ts).total_seconds() > 7200: # 2 hours
                use_ghi = True
        else: # No POA data at all
            use_ghi = True

        if use_ghi and ghi_data:
            val = ghi_data[0] if ghi_data and ghi_data[0] is not None else 0
            ts = ghi_data[1] if ghi_data else None
            source = "GHI"
        elif poa_data:
            val = poa_data[0] if poa_data[0] is not None else 0
            ts = poa_ts
            source = "POA"

        color = 'gray' if val < 100 else '#ADD8E6' if val > 800 else '#1E90FF'
        
        current_state = "ONLINE"
        if ts is None or (datetime.now() - ts).total_seconds() > 7200:
            color = 'pink'
            current_state = "NO_COMMS"
            
        is_suppressed = self.site_widgets[var]['poa_var'].get() == 1
        if is_suppressed:
            val = 9999
            color = 'pink'
            source = "MANUAL OVERRIDE"
            
        self.site_widgets[var]['poa_btn'].config(text=str(int(val)), bg=color)
        
        last_comm_str = ts.strftime('%m/%d/%Y %H:%M') if ts else "Unknown"
        self.site_widgets[var]['poa_tt'].text = f"Source: {source}\nLast Comm: {last_comm_str}"

        # Notifications
        site_suppress = self.site_widgets[var]['site_suppress_var'].get() == 1
        last_state = self.device_states.get(f"{site}_poa", "ONLINE")
        if current_state == "NO_COMMS" and not is_suppressed and not site_suppress:
            if not self.text_only_var.get() or current_state != last_state:
                self._trigger_alert(f"{site} POA", f"POA/GHI Lost Communications | Last comm: {last_comm_str}")
        elif current_state == "ONLINE" and not is_suppressed and not site_suppress:
            if last_state == "NO_COMMS":
                if not self.text_only_var.get() or current_state != last_state:
                    self._trigger_alert(f"{site} POA", "POA/GHI Communications Restored")
        self.device_states[f"{site}_poa"] = current_state

        return val

    def _update_breakers(self, site, var):
        suppress_alerts = self.site_widgets[var]['site_suppress_var'].get() == 1
        time_now = datetime.now()
        lost_comm_threshold = time_now - timedelta(hours=2)
        
        # Universal Meter Amps Check (0 Amps = Open Breaker/Grid Loss)
        meter_data = self.raw_meter_data.get(f"{site} Meter Data", [])
        meter_indicates_open = False
        if meter_data:
            # Indices 3, 4, 5 correspond to Amps A, B, C. Check the 8 most recent pulls.
            zero_amp_rows = sum(1 for row in meter_data[:8] if any(row[i] == 0 for i in (3, 4, 5)))
            if zero_amp_rows >= 2:
                meter_indicates_open = True
        
        if site == 'Violet':
            for i in (1, 2):
                data = self.raw_breaker_data.get(f"{site} Breaker Data {i}", [])
                last_comm_ts = data[0][1] if data and len(data[0]) > 1 and data[0][1] else None
                last_comm_str = last_comm_ts.strftime('%m/%d/%Y %H:%M') if last_comm_ts else "Unknown"
                
                state_key = f"{site}_breaker_{i}"
                last_state = self.device_states.get(state_key, "ONLINE")
                current_state = "ONLINE"
                
                if not data or not last_comm_ts or last_comm_ts < lost_comm_threshold:
                    current_state = "NO_COMMS"
                    self.site_widgets[var][f'status_label_{i}'].config(bg='pink')
                    self.site_widgets[var][f'breaker_tt_{i}'].text = f"Breaker Lost Communications\nLast Comm: {last_comm_str}"
                    if not suppress_alerts and (not self.text_only_var.get() or current_state != last_state):
                        self._trigger_alert(f"{site} Breaker {i}", f"Breaker Lost Communications | Last comm: {last_comm_str}")
                    self.device_states[state_key] = current_state
                    continue
                else:
                    if last_state == "NO_COMMS" and not suppress_alerts:
                        if not self.text_only_var.get() or current_state != last_state:
                            self._trigger_alert(f"{site} Breaker {i}", "Breaker Communications Restored")
                
                # Closed ONLY if physical telemetry says closed AND the meter is registering amps
                physically_closed = any(row[0] for row in data) if data else True
                is_closed = physically_closed and not meter_indicates_open
                
                cache_key = f"{site}_{i}"
                
                if is_closed:
                    self.last_closed_cache.pop(cache_key, None)
                    self.site_widgets[var][f'status_label_{i}'].config(text='✓✓✓', bg='green')
                    self.site_widgets[var][f'breaker_tt_{i}'].text = f"Breaker Operational\nLast Comm: {last_comm_str}"
                else:
                    last_op = self.last_closed_cache.get(cache_key, "Unknown")
                    current_state = "OPEN"
                    
                    self.site_widgets[var][f'status_label_{i}'].config(text='❌❌', bg='red')
                    self.site_widgets[var][f'breaker_tt_{i}'].text = f"Breaker Open\nLast closed: {last_op}\nLast Comm: {last_comm_str}"
                    
                    if not suppress_alerts:
                        self._trigger_alert(f"{site} Breaker {i}", f"Breaker Tripped Open! Last closed: {last_op}")
                
                self.device_states[state_key] = current_state
        else:
            data = self.raw_breaker_data.get(f"{site} Breaker Data", [])
            last_comm_ts = data[0][1] if data and len(data[0]) > 1 and data[0][1] else None
            last_comm_str = last_comm_ts.strftime('%m/%d/%Y %H:%M') if last_comm_ts else "Unknown"
            
            state_key = f"{site}_breaker"
            last_state = self.device_states.get(state_key, "ONLINE")
            current_state = "ONLINE"
            
            if not data or not last_comm_ts or last_comm_ts < lost_comm_threshold:
                current_state = "NO_COMMS"
                self.site_widgets[var]['breaker_label'].config(bg='pink')
                self.site_widgets[var]['breaker_tt'].text = f"Breaker Lost Communications\nLast Comm: {last_comm_str}"
                if not suppress_alerts and (not self.text_only_var.get() or current_state != last_state):
                    self._trigger_alert(f"{site} Breaker", f"Breaker Lost Communications | Last comm: {last_comm_str}")
                self.device_states[state_key] = current_state
                return
            else:
                if last_state == "NO_COMMS" and not suppress_alerts:
                    if not self.text_only_var.get() or current_state != last_state:
                        self._trigger_alert(f"{site} Breaker", "Breaker Communications Restored")
            
            # Closed ONLY if physical telemetry says closed AND the meter is registering amps
            physically_closed = any(row[0] for row in data) if data else True
            is_closed = physically_closed and not meter_indicates_open
            
            if is_closed:
                self.last_closed_cache.pop(site, None)
                self.site_widgets[var]['breaker_label'].config(text='✓✓✓', bg='green')
                self.site_widgets[var]['breaker_tt'].text = f"Breaker Operational\nLast Comm: {last_comm_str}"
            else:
                last_op = self.last_closed_cache.get(site, "Unknown")
                current_state = "OPEN"
                    
                self.site_widgets[var]['breaker_label'].config(text='❌❌', bg='red')
                self.site_widgets[var]['breaker_tt'].text = f"Breaker Open\nLast closed: {last_op}\nLast Comm: {last_comm_str}"
                
                if not suppress_alerts and (not self.text_only_var.get() or current_state != last_state):
                    self._trigger_alert(f"{site} Breaker", f"Breaker Tripped Open! Last closed: {last_op}")
            
            self.device_states[state_key] = current_state

    def _update_meters(self, site, var, poa):
        if not hasattr(self, 'null_comms_since'):
            self.null_comms_since = {}
        if not hasattr(self, 'watts_null_since'):
            self.watts_null_since = {}
            
        state_key = f"{site}_meter"
        all_null = self._are_all_values_null(self.raw_meter_data.get(f"{site} Meter Data", []), [0, 1, 2, 3, 4, 5, 6])
        if all_null:
            if state_key not in self.null_comms_since:
                self.null_comms_since[state_key] = datetime.now()
        time_now = datetime.now()
        lost_comm_threshold = time_now - timedelta(hours=2)   
        site_suppress = self.site_widgets[var]['site_suppress_var'].get() == 1
        meter_suppress = self.site_widgets[var]['meter_suppress_var'].get() == 1
        suppress_alerts = site_suppress or meter_suppress
        if site == "CDIA":
            data = self.raw_inv_data.get(f"{site} INV 1 Data", [])
            last_comm_ts = data[0][2] if data and len(data[0]) > 2 else None
            last_state = self.device_states.get(f"{site}_meter", "ONLINE")

            if not data or not last_comm_ts or last_comm_ts < lost_comm_threshold or (all_null and state_key in self.null_comms_since and (datetime.now() - self.null_comms_since[state_key]).total_seconds() > 7200):
                last_comm_str = last_comm_ts.strftime('%m/%d/%Y %H:%M') if last_comm_ts else "Unknown"
                current_state = "NO_COMMS"
                self.site_widgets[var]['kw_label'].config(bg='pink')
                self.site_widgets[var]['kw_tt'].text = f"Inverter Lost Communications\nLast Comm: {last_comm_str}"
                if not suppress_alerts and (not self.text_only_var.get() or current_state != last_state):
                    self._trigger_alert(f"{site} Inverter", f"Inverter Lost Communications | Last comm: {last_comm_str}")
                self.device_states[f"{site}_meter"] = current_state
                return 0
            else:
                current_state = "ONLINE"
                if last_state == "NO_COMMS" and not suppress_alerts:
                    if not self.text_only_var.get() or current_state != last_state:
                        self._trigger_alert(f"{site} Inverter", "Inverter Communications Restored")
                self.device_states[f'{site}_meter'] = current_state
                w = fast_mean(row[1] for row in data if row[1] is not None and row[1] < 760000000)
                kw = round(w/1000, 1)
                ui_color = 'green' if kw > 0 else 'black'
                if ui_color == 'black':
                    self.site_widgets[var]['label'].config(bg='red')

                self.site_widgets[var]['kw_label'].config(text=kw, bg=ui_color)
                self.site_widgets[var]['kw_tt'].text = "Meter Online" if ui_color == 'green' else "Meter Offline"

                dc_v = fast_mean(row[0] for row in data)
                self.site_widgets[var]['v_label'].config(text="✓✓✓" if dc_v > 100 else "❌❌", bg="green" if dc_v > 100 else "red")
                self.site_widgets[var]['v_tt'].text = f"DC Voltage {round(dc_v, 1)}"

                cdiaRatio = round(w/self.MAP_SITES[site]['METER_MAX']*100, 1)
                if cdiaRatio > 90: ratio_color = '#ADD8E6'
                elif cdiaRatio > 80: ratio_color = '#87CEEB'
                elif cdiaRatio > 70: ratio_color = '#1E90FF'
                elif cdiaRatio > 60: ratio_color = '#4682B4'
                elif cdiaRatio > 50: ratio_color = '#4169E1'
                elif cdiaRatio < 0.1: ratio_color = 'black'
                else: ratio_color = 'gray'

                self.site_widgets[var]['ratio_label'].config(text=f"{cdiaRatio}%", bg=ratio_color)
                
                return kw
        else:        
            data = self.raw_meter_data.get(f"{site} Meter Data", [])
            last_comm_ts = data[0][7] if data and len(data[0]) > 7 and data[0][7] else None
            last_comm_str = last_comm_ts.strftime('%m/%d/%Y %H:%M') if last_comm_ts else "Unknown"
            
            last_state = self.device_states.get(state_key, "ONLINE")
            current_state = "ONLINE"
            
            if not data or not last_comm_ts or last_comm_ts < lost_comm_threshold:
                current_state = "NO_COMMS"
                self.site_widgets[var]['kw_label'].config(bg='pink')
                self.site_widgets[var]['v_label'].config(bg='pink')
                self.site_widgets[var]['ratio_label'].config(bg='pink')
                self.site_widgets[var]['kw_tt'].text = f"Meter Lost Communications\nLast Comm: {last_comm_str}"
                self.site_widgets[var]['v_tt'].text = f"Meter Lost Communications\nLast Comm: {last_comm_str}"
                
                if not suppress_alerts and (not self.text_only_var.get() or current_state != last_state):
                    self._trigger_alert(f"{site} Meter", f"Meter Lost Communications | Last comm: {last_comm_str}")
                
                self.device_states[state_key] = current_state
                return 0
            else:
                if last_state == "NO_COMMS" and not suppress_alerts:
                    if not self.text_only_var.get() or current_state != last_state:
                        self._trigger_alert(f"{site} Meter", "Meter Communications Restored")
                
            v_a = fast_mean(row[0] for row in data)
            v_b = fast_mean(row[1] for row in data)
            v_c = fast_mean(row[2] for row in data)
            avg_w = fast_mean(row[6] for row in data if row[6] is not None and row[6] < 760000000)
            
            val_thresh = 5 if site == "Hickory" else 5000
            dif_thresh = 9 if site in ["Wellons", "Cherry Blossom"] else 5

            pct_diff_ab = ((max(v_a, v_b) - min(v_a, v_b)) / fast_mean([v_a, v_b])) * 100 if fast_mean([v_a, v_b]) else 0
            pct_diff_ac = ((max(v_a, v_c) - min(v_a, v_c)) / fast_mean([v_a, v_c])) * 100 if fast_mean([v_a, v_c]) else 0
            pct_diff_bc = ((max(v_b, v_c) - min(v_b, v_c)) / fast_mean([v_b, v_c])) * 100 if fast_mean([v_b, v_c]) else 0

            # Refactored Phase Text Logic
            if v_a < val_thresh and v_b < val_thresh and v_c < val_thresh:
                current_state = "ALL_PHASES_LOST"
                self.site_widgets[var]['v_label'].config(text='❌❌', bg='red')
                self.site_widgets[var]['v_tt'].text = f"Loss of Utility Voltage across all phases.\nLast Comm: {last_comm_str}"
                if not suppress_alerts and (not self.text_only_var.get() or current_state != last_state): self._trigger_alert(f"{site} Meter", "Loss of Utility Voltage across all phases.")
            elif v_a < val_thresh:
                current_state = "PHASE_A_LOST"
                self.site_widgets[var]['v_label'].config(text='X✓✓', bg='orange')
                self.site_widgets[var]['v_tt'].text = f"Loss of Phase A Voltage.\nLast Comm: {last_comm_str}"
                if not suppress_alerts and (not self.text_only_var.get() or current_state != last_state): self._trigger_alert(f"{site} Meter", "Loss of Utility Phase A Voltage.")
            elif v_b < val_thresh:
                current_state = "PHASE_B_LOST"
                self.site_widgets[var]['v_label'].config(text='✓X✓', bg='orange')
                self.site_widgets[var]['v_tt'].text = f"Loss of Phase B Voltage.\nLast Comm: {last_comm_str}"
                if not suppress_alerts and (not self.text_only_var.get() or current_state != last_state): self._trigger_alert(f"{site} Meter", "Loss of Utility Phase B Voltage.")
            elif v_c < val_thresh:
                current_state = "PHASE_C_LOST"
                self.site_widgets[var]['v_label'].config(text='✓✓X', bg='orange')
                self.site_widgets[var]['v_tt'].text = f"Loss of Phase C Voltage.\nLast Comm: {last_comm_str}"
                if not suppress_alerts and (not self.text_only_var.get() or current_state != last_state): self._trigger_alert(f"{site} Meter", "Loss of Utility Phase C Voltage.")
            elif pct_diff_ab >= dif_thresh or pct_diff_ac >= dif_thresh or pct_diff_bc >= dif_thresh:
                current_state = "PHASE_IMBALANCE"
                self.site_widgets[var]['v_label'].config(text='???', bg='orange')
                self.site_widgets[var]['v_tt'].text = f"Voltage Imbalance greater than {dif_thresh}%\nLast Comm: {last_comm_str}"
                if not suppress_alerts and (not self.text_only_var.get() or current_state != last_state): self._trigger_alert(f"{site} Meter", f"Voltage Imbalance greater than {dif_thresh}%")
            else:
                self.site_widgets[var]['v_label'].config(text='✓✓✓', bg='green')
                self.site_widgets[var]['v_tt'].text = f"Voltage levels operational\nLast Comm: {last_comm_str}"

            # Check Production / Power Loss
            if (avg_w < 2 and (poa >= 100 or (poa == 9999 and datetime.now().hour >= 8))):
                current_state = "POWER_LOSS"
                if not suppress_alerts:
                    online = self.meter_last_online_cache.get(site, "Unknown")
                    self.site_widgets[var]['kw_label'].config(text='❌❌', bg='red')
                    self.site_widgets[var]['kw_tt'].text = f"Offline. Last online: {online}\nLast Comm: {last_comm_str}"
                    if not self.text_only_var.get() or current_state != last_state:
                        self._trigger_alert(f"{site} Power Loss", f"Meter reading ~0kW while POA is active. Last online: {online}")
            else:
                self.meter_last_online_cache.pop(site, None)
                self.site_widgets[var]['kw_label'].config(text=f"{round(avg_w/1000, 1)}", bg='green' if avg_w > 0 else 'gray')
                self.site_widgets[var]['kw_tt'].text = f"Meter Online\nLast Comm: {last_comm_str}"
            
            self.device_states[state_key] = current_state

            # --- Ratio / % of Max Calculation with Color Sequencing ---
            ratio_pct = (avg_w / self.MAP_SITES[site]['METER_MAX']) * 100 if self.MAP_SITES[site]['METER_MAX'] else 0
            meterRatio = ratio_pct / 100.0
            
            if meterRatio > .90: ratio_color = '#ADD8E6'
            elif meterRatio > .80: ratio_color = '#87CEEB'
            elif meterRatio > .70: ratio_color = '#1E90FF'
            elif meterRatio > .60: ratio_color = '#4682B4'
            elif meterRatio > .50: ratio_color = '#4169E1'
            elif meterRatio < 0.001: ratio_color = 'black'
            else: ratio_color = 'gray'
            
            self.site_widgets[var]['ratio_label'].config(text=f"{round(ratio_pct, 1)}%", bg=ratio_color)

            # --- PVsyst Application with Color Sequencing ---
            perf_ratio = self.pvsyst_results.get(site, 0)
            
            if perf_ratio > 0:
                if perf_ratio > 90: pv_color = '#ADD8E6'
                elif perf_ratio > 80: pv_color = '#87CEEB'
                elif perf_ratio > 70: pv_color = '#1E90FF'
                elif perf_ratio > 60: pv_color = '#4682B4'
                elif perf_ratio > 50: pv_color = '#4169E1'
                else: pv_color = 'gray'
                self.site_widgets[var]['pvsyst_label'].config(text=f'{round(perf_ratio, 1)}%', bg=pv_color)
            else:
                self.site_widgets[var]['pvsyst_label'].config(text='N/A', bg=MAIN_COLOR, font=('Tk_defaultFont', 10,))

            return avg_w
    
    def _update_inverters(self, site, var, poa):
        if not hasattr(self, 'null_comms_since'):
            self.null_comms_since = {}
        if not hasattr(self, 'watts_null_since'):
            self.watts_null_since = {}
            
        invdict = self.MAP_SITES[site]['INV_DICT']
        suppress_alerts = self.site_widgets[var]['site_suppress_var'].get() == 1
        
        # --- PASS 1: Evaluate raw data and gather site-wide metrics ---
        site_statuses = {}
        total_expected = 0
        total_online_expected = 0
        any_expected_inv_over_2_hours = False
        
        for inv_num, inv_label in invdict.items():
            duplin_except = (' Central' if inv_num <= 3 else ' String') if site == 'Duplin' else ''
            inv_n = inv_num if site != 'Duplin' else (inv_num if inv_num <= 3 else inv_num - 3)
            
            cache_key = f"{site}_{inv_num}"

            table_name = f'{site}{duplin_except} INV {inv_n} Data'
            data = self.raw_inv_data.get(table_name, [])
            
            inv_widget = self.site_widgets[var]['inverters'].get(str(inv_label))
            is_manually_suppressed = inv_widget['cb_val'].get() == 1 if inv_widget else False
            
            # --- Track Last Communication ---
            last_comm_ts = "Unknown"
            is_no_comms = False
            
            if data and len(data[0]) > 2 and data[0][2]:
                upload_time = data[0][2]
                # Using the full timestamp format as requested previously
                last_comm_ts = upload_time.strftime('%m/%d/%Y %H:%M:%S') 
                
                if (datetime.now() - upload_time).total_seconds() > 7200:
                    is_no_comms = True
            else:
                is_no_comms = True 

            # --- Track Production & DC Voltage ---
            consecutive = 0
            is_online = False
            is_completely_offline = all(row[1] is None or row[1] < 1 for row in data) if data else False
            # Grab average DC Voltage for the 'Orange' status check
            avg_dcv = fast_mean(row[0] for row in data) if data else 0
            
            if not is_completely_offline and not is_no_comms:
                for row in data:
                    if row[1] is not None and row[1] > 0:
                        consecutive += 1
                        if consecutive >= 3:
                            is_online = True
                            break
                    else:
                        consecutive = 0
            
            if is_online:
                if cache_key not in self.inv_online_since:
                    self.inv_online_since[cache_key] = datetime.now()
                self.null_comms_since.pop(cache_key, None) # Clear null timer if it's online
            else:
                self.inv_online_since.pop(cache_key, None) 
                
            if not is_manually_suppressed:
                total_expected += 1
                if is_online:
                    total_online_expected += 1
                    if cache_key in self.inv_online_since and (datetime.now() - self.inv_online_since[cache_key]).total_seconds() > 7200:
                        any_expected_inv_over_2_hours = True
                        
            site_statuses[inv_num] = {
                'is_online': is_online,
                'is_completely_offline': is_completely_offline,
                'is_no_comms': is_no_comms,
                'avg_dcv': avg_dcv,
                'cache_key': cache_key,
                'inv_label': inv_label,
                'is_manually_suppressed': is_manually_suppressed,
                'last_comm_ts': last_comm_ts
            }

        # --- PASS 2: Update UI ---
        for inv_num, status in site_statuses.items():
            inv_label = status['inv_label']
            inv_widget = self.site_widgets[var]['inverters'].get(str(inv_label))
            if not inv_widget: continue
                
            cache_key = status['cache_key']
            last_state = self.device_states.get(cache_key, "ONLINE")
            
            # Logic for color coding including the Orange Voltage check
            all_null = self._are_all_values_null(self.raw_inv_data.get(f'{site}{duplin_except} INV {inv_n} Data', []), [0, 1])

            if status['is_no_comms'] or (all_null and cache_key in self.null_comms_since and (datetime.now() - self.null_comms_since[cache_key]).total_seconds() > 7200):
                current_state = "NO_COMMS"
                ui_color = 'pink' 
            elif status['is_online']:
                current_state = "ONLINE"
                ui_color = 'green'
            elif not status['is_completely_offline']:
                current_state = "STARTING"
                ui_color = 'yellow'
            else:
                # Inverter is production-offline. Check DC Voltage:
                if status['avg_dcv'] > 100:
                    current_state = "OFFLINE_WITH_VOLTAGE"
                    ui_color = 'orange'
                else:
                    current_state = "OFFLINE_NO_VOLTAGE"
                    ui_color = 'red'

            if all_null:
                last_good_comm = self.last_good_comm_cache.get(cache_key)
                if last_good_comm and (datetime.now() - last_good_comm).total_seconds() > 7200:
                    if current_state in {"OFFLINE_WITH_VOLTAGE", "OFFLINE_NO_VOLTAGE"}:
                        current_state, ui_color = "NO_COMMS", 'pink'

            # Build tooltip and alert message
            online_last = self.last_online_cache.get(cache_key, "Unknown")
            comm_last = status['last_comm_ts']
            
            msg = f"Inv {inv_label}\nLast Online: {online_last}\nLast Comm: {comm_last}"
            
            if status['is_completely_offline'] or status['is_no_comms']:
                inv_widget['cb'].config(bg=ui_color)
                inv_widget['cb_tt'].text = msg 
                
                # Notification Logic
                all_others_online = (total_expected > 1) and (total_online_expected >= total_expected - 1)
                suppression_lifted = (poa > 400) or any_expected_inv_over_2_hours or all_others_online
                
                if (suppression_lifted or status['is_no_comms']) and not suppress_alerts and not status['is_manually_suppressed']:
                    if not self.text_only_var.get() or current_state != last_state:
                        self._trigger_alert(f"{site} Device Issue", msg.replace('\n', ' | '))
            else:
                # Device is online or starting
                self.last_online_cache.pop(cache_key, None)
                inv_widget['cb'].config(bg=ui_color)
                inv_widget['cb_tt'].text = f"Status: {current_state}\nLast Comm: {comm_last}"
                
                if last_state == "NO_COMMS" and not suppress_alerts and not status['is_manually_suppressed']:
                    if not self.text_only_var.get() or current_state != last_state:
                        self._trigger_alert(f"{site} Device Issue", f"Inv {inv_label} Communications Restored")

            self.device_states[cache_key] = current_state

    def _update_conetoe_inverters(self, site, var, poa):
        if not hasattr(self, 'null_comms_since'):
            self.null_comms_since = {}
        if not hasattr(self, 'watts_null_since'):
            self.watts_null_since = {}
            
        invdict = self.MAP_SITES[site]['INV_DICT']
        suppress_alerts = self.site_widgets[var]['site_suppress_var'].get() == 1
        
        # Inverter groupings: Inverter 1 (1-4), Inverter 2 (5-8), Inverter 3 (9-12), Inverter 4 (13-16)
        groups = {
            1: [1, 2, 3, 4],
            2: [5, 6, 7, 8],
            3: [9, 10, 11, 12],
            4: [13, 14, 15, 16]
        }
        
        # --- PASS 1: Evaluate raw data and gather module-level metrics ---
        module_statuses = {}
        
        for inv_num, inv_label in invdict.items():
            table_name = f'{site} INV {inv_num} Data'
            data = self.raw_inv_data.get(table_name, [])

            cache_key = f"{site}_{inv_num}"
            
            inv_widget = self.site_widgets[var]['inverters'].get(str(inv_label))
            is_manually_suppressed = inv_widget['cb_val'].get() == 1 if inv_widget else False
            
            last_comm_ts = "Unknown"
            is_no_comms = False
            
            if data and len(data[0]) > 2 and data[0][2]:
                upload_time = data[0][2]
                last_comm_ts = upload_time.strftime('%m/%d/%Y %H:%M:%S') 
                if (datetime.now() - upload_time).total_seconds() > 7200:
                    is_no_comms = True
            else:
                is_no_comms = True 

            consecutive = 0
            is_online = False
            is_completely_offline = all(row[1] is None or row[1] < 1 for row in data) if data else False
            avg_dcv = fast_mean(row[0] for row in data) if data else 0
            
            if not is_completely_offline and not is_no_comms:
                for row in data:
                    if row[1] is not None and row[1] > 0:
                        consecutive += 1
                        if consecutive >= 3:
                            is_online = True
                            break
                    else:
                        consecutive = 0
            if is_online:
                if cache_key not in self.inv_online_since:
                    self.inv_online_since[cache_key] = datetime.now()
            else:
                self.inv_online_since.pop(cache_key, None) 
                
            module_statuses[inv_num] = {
                'is_online': is_online,
                'is_completely_offline': is_completely_offline,
                'is_no_comms': is_no_comms,
                'avg_dcv': avg_dcv,
                'cache_key': cache_key,
                'inv_label': inv_label,
                'is_manually_suppressed': is_manually_suppressed,
                'last_comm_ts': last_comm_ts
            }

        # --- PASS 2: Apply grouping logic for notifications and UI updates ---
        any_module_online_site_wide = any(not m['is_completely_offline'] for m in module_statuses.values())
        for group_id, module_ids in groups.items():
            group_modules = [module_statuses[mod_id] for mod_id in module_ids if mod_id in module_statuses]
            
            # Identify group level conditions
            all_offline_bad_dcv = all(m['is_completely_offline'] and m['avg_dcv'] <= 100 for m in group_modules)
            all_offline = all(m['is_completely_offline'] for m in group_modules)
            for mod_id in module_ids:
                if mod_id not in module_statuses: continue
                status = module_statuses[mod_id]
                
                inv_label = status['inv_label']
                inv_widget = self.site_widgets[var]['inverters'].get(str(inv_label))
                if not inv_widget: continue
                    
                cache_key = status['cache_key']
                last_state = self.device_states.get(cache_key, "ONLINE")
                
                all_null = self._are_all_values_null(self.raw_inv_data.get(f'{site} INV {mod_id} Data', []), [0, 1])

                if status['is_no_comms'] or (all_null and cache_key in self.null_comms_since and (datetime.now() - self.null_comms_since[cache_key]).total_seconds() > 7200):
                    current_state = "NO_COMMS"
                    ui_color = 'pink'
                elif status['is_online']:
                    current_state = "ONLINE"
                    ui_color = 'green'
                elif not status['is_completely_offline']:
                    current_state = "STARTING"
                    ui_color = 'yellow'
                else:
                    if status['avg_dcv'] > 100:
                        current_state = "OFFLINE_WITH_VOLTAGE"
                        ui_color = 'orange'
                    else:
                        current_state = "OFFLINE_NO_VOLTAGE"
                        ui_color = 'red'

                if all_null:
                    last_good_comm = self.last_good_comm_cache.get(cache_key)
                    if last_good_comm and (datetime.now() - last_good_comm).total_seconds() > 7200:
                        if current_state in {"OFFLINE_WITH_VOLTAGE", "OFFLINE_NO_VOLTAGE"}:
                            current_state, ui_color = "NO_COMMS", 'pink'

                online_last = self.last_online_cache.get(cache_key, "Unknown")
                comm_last = status['last_comm_ts']

                msg = f"Inv {inv_label}\nLast Online: {online_last}\nLast Comm: {comm_last}"

                if status['is_completely_offline'] or status['is_no_comms']:
                    inv_widget['cb'].config(bg=ui_color)
                    inv_widget['cb_tt'].text = msg 
                    
                    # Conetoe specific notification logic
                    should_notify = False
                    
                    if status['is_no_comms']:
                        should_notify = True
                    elif current_state == "OFFLINE_WITH_VOLTAGE":
                        # Any module offline with good DC V is normal behavior
                        if all_offline_bad_dcv and poa > 400: 
                            should_notify = True
                        elif all_offline and any_module_online_site_wide:
                            should_notify = True
                        else:
                            should_notify = False
                    elif current_state == "OFFLINE_NO_VOLTAGE":
                        should_notify = True

                            
                    if should_notify and not suppress_alerts and not status['is_manually_suppressed']:
                        if not self.text_only_var.get() or current_state != last_state:
                            self._trigger_alert(f"{site} Device Issue", msg.replace('\n', ' | '))
                else:
                    self.last_online_cache.pop(cache_key, None)
                    inv_widget['cb'].config(bg=ui_color)
                    inv_widget['cb_tt'].text = f"Status: {current_state}\nLast Comm: {comm_last}"
                    
                    if last_state == "NO_COMMS" and not suppress_alerts and not status['is_manually_suppressed']:
                        if not self.text_only_var.get() or current_state != last_state:
                            self._trigger_alert(f"{site} Device Issue", f"Inv {inv_label} Communications Restored")

                self.device_states[cache_key] = current_state

    def _update_snapshots(self, site, var, meter_w):
        inv_dict = self.MAP_SITES[site]['INV_DICT']
        inv_count = len(inv_dict)
        communicating_invs = 0
        total_inv_kw = 0
        active_inv_count = 0
        
        if 'inverters' in self.site_widgets[var]:
            for inv_widget in self.site_widgets[var]['inverters'].values():
                if inv_widget.get('cb') and inv_widget['cb'].cget('bg') == 'green':
                    communicating_invs += 1

        for inv_num, inv_label in inv_dict.items():
            duplin_except = (' Central' if inv_num <= 3 else ' String') if site == 'Duplin' else ''
            inv_n = inv_num if site != 'Duplin' else (inv_num if inv_num <= 3 else inv_num - 3)
            
            table_name = f'{site}{duplin_except} INV {inv_n} Data'
            data = self.raw_inv_data.get(table_name, [])
            
            if data:
                max_w = max((row[1] for row in data[:8] if row[1] is not None), default=0)
                if max_w > 0:
                    total_inv_kw += max_w
                    active_inv_count += 1

        color = MAIN_COLOR
        if total_inv_kw == 0 and meter_w <= 0:
            color = 'black'
        elif communicating_invs < inv_count and active_inv_count > 0:
            avg_inv_prod = total_inv_kw / active_inv_count
            non_comm_invs = inv_count - communicating_invs
            estimated_prod = total_inv_kw + (avg_inv_prod * 0.75) * non_comm_invs
            color = 'green' if meter_w >= estimated_prod else 'yellow'

        text_color = 'white' if color == 'black' else 'black'

        self.site_widgets[var]['snap_frame'].config(bg=color)
        self.site_widgets[var]['inv_kw_total'].config(text=f"{total_inv_kw/1000:.1f} kW", bg=color, fg=text_color)
        self.site_widgets[var]['meter_inv_diff'].config(text=f"{round((meter_w - total_inv_kw)/1000, 1)} kW", bg=color, fg=text_color)
        self.site_widgets[var]['invs_online'].config(text=f"{communicating_invs}", bg=color, fg=text_color)
        self.site_widgets[var]['meter_kw_snap'].config(text=f"{meter_w/1000:.1f} kW", bg=color, fg=text_color)
        self.site_widgets[var]['invs_no_comms'].config(text=f"{inv_count - communicating_invs}", bg=color, fg=text_color)
        self.site_widgets[var]['invs_total'].config(text=f"{inv_count}", bg=color, fg=text_color)

    def save_checkbox_states(self):
        state = {
            "GLOBAL": {
                "text_only_var": self.text_only_var.get()
            }
        }
        for name, config in self.MAP_SITES.items():
            var_name = config['VAR_NAME']
            if var_name not in self.site_widgets:
                continue
                
            widgets = self.site_widgets[var_name]
            site_state = {
                "site_suppress": widgets['site_suppress_var'].get() if 'site_suppress_var' in widgets else 0,
                "meter_suppress": widgets['meter_suppress_var'].get() if 'meter_suppress_var' in widgets else 0,
                "poa_suppress": widgets['poa_var'].get() if 'poa_var' in widgets else 0,
                "inverters": {}
            }
            
            for inv_val, inv_widgets in widgets.get('inverters', {}).items():
                inv_state = {}
                if 'cb_val' in inv_widgets:
                    inv_state['cb_val'] = inv_widgets['cb_val'].get()
                if 'up_cb_val' in inv_widgets:
                    inv_state['up_cb_val'] = inv_widgets['up_cb_val'].get()
                site_state["inverters"][inv_val] = inv_state
                
            state[var_name] = site_state
            
        with open(BUTTON_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=4)

    def load_checkbox_states(self):
        if os.path.exists(BUTTON_STATE_FILE):
            with open(BUTTON_STATE_FILE, 'r') as f:
                try:
                    state = json.load(f)
                        
                    if "GLOBAL" in state:
                        self.text_only_var.set(state["GLOBAL"].get("text_only_var", 0))
                        
                    for name, config in self.MAP_SITES.items():
                        var_name = config['VAR_NAME']
                        if var_name in state and var_name in self.site_widgets:
                            site_state = state[var_name]
                            widgets = self.site_widgets[var_name]
                            
                            if 'site_suppress_var' in widgets:
                                widgets['site_suppress_var'].set(site_state.get('site_suppress', 0))
                            if 'meter_suppress_var' in widgets:
                                widgets['meter_suppress_var'].set(site_state.get('meter_suppress', 0))
                            if 'poa_var' in widgets:
                                widgets['poa_var'].set(site_state.get('poa_suppress', 0))
                                
                            for inv_val, inv_state in site_state.get('inverters', {}).items():
                                if inv_val in widgets.get('inverters', {}):
                                    inv_widgets = widgets['inverters'][inv_val]
                                    if 'cb_val' in inv_widgets:
                                        inv_widgets['cb_val'].set(inv_state.get('cb_val', 0))
                                    if 'up_cb_val' in inv_widgets:
                                        inv_widgets['up_cb_val'].set(inv_state.get('up_cb_val', 0))
                except Exception as e:
                    print(f"Error loading checkbox states: {e}")

    def _handle_notifications(self):
        """Prepares an email and dispatches it onto another lightweight thread to prevent freezing."""
        if len(self.text_update_table) <= 2:
            return
            
        html_content = "".join(self.text_update_table)
        admin_user = self.admin_var.get()
        
        # Dispatch SMTP functionality to a separate thread
        threading.Thread(target=self._send_email_bg, args=(html_content, admin_user), daemon=True).start()

    def _send_email_bg(self, html_content, admin_user):
        """Worker function for SMTP dispatches."""
        try:
            message = MIMEMultipart()
            message["Subject"] = f"AE API Update {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            message["From"] = EMAILS['NCC Desk']
            message["To"] = EMAILS.get(admin_user, EMAILS['NCC Desk'])
            password = CREDS['remoteMonitoring']
            
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(message["From"], password)
                soup = BeautifulSoup(html_content, 'html.parser')
                message.attach(MIMEText(soup.prettify(), 'html'))
                server.send_message(message)
                print(f"Alert payload successfully dispatched to {message['To']}")
        except Exception as e:
            print(f"Error during email dispatch: {e}")

if __name__ == "__main__":
    root = Tk()
    app = AEDataApp(root)
    root.mainloop()