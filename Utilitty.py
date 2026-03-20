import re, os, socket
from google.auth.transport.requests import Request
import tkinter as tk
import pyodbc
from google.oauth2.credentials import Credentials
from google.auth import exceptions as auth_exceptions
from google_auth_oauthlib.flow import InstalledAppFlow

def find_last_digit(text_to_search):
    """
    Finds the first number in a string when searching from right to left.
    Args:
        text_to_search: The string to search.
    Returns:
        The number found, or None if no digits are in the string.
    """
    # The pattern .*\d finds the last digit in the string.
    # .* is greedy and consumes the whole string.
    # This pattern finds the last sequence of one or more digits in the string.
    pattern = r'.*?(\d+)[^\d]*$'   
    match = re.search(pattern, text_to_search)
    
    if match:
        number = match.group(1)
        #print(text_to_search, number) #Debugging
        return int(number)
        
    return None





def get_hostname():
    """
    Identifies the Hostname of the PC running the file.
    Returns:
        str: The hostname of the local machine.
    """
    try:
        hostname = socket.gethostname()
        return hostname
    except Exception as e:
        print(f"Error getting hostname: {e}")
        return None


# --- Google API Authentication ---
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

def get_google_credentials():
    """Handles Google API authentication."""
    creds = None
    token_path = r"G:\Shared drives\O&M\NCC Automations\Auth\token.json"
    creds_path = r"G:\Shared drives\O&M\NCC Automations\Auth\NCC-AutomationCredentials.json"
    print("Start!")
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif creds and creds.refresh_token: # Handle cases where token might be invalid due to scope changes but not expired
            try:
                creds.refresh(Request())
            except auth_exceptions.RefreshError:
                os.remove(token_path) # Delete invalid token to force re-authentication
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds



#Force Restart PC
def restart_pc():
    os.system("shutdown /r /t 1")



def time_validation(tvalue):
    """Validates that the input is in HH:MM format."""
    # An empty entry is a valid state
    if not tvalue:
        return True
    # The final format is 5 characters long (e.g., "23:59")
    if len(tvalue) > 5:
        return False
        
    # Check the characters as they are typed
    for i, char in enumerate(tvalue):
        if i in [0, 1, 3, 4]:  # Positions for digits
            if not char.isdigit():
                return False
        if i == 2:  # Position for the colon
            if char != ':':
                return False
                
    # Check the semantic value of the hour and minute
    if len(tvalue) >= 2:
        # Hour must be between 00 and 23
        if int(tvalue[0:2]) > 23:
            return False
    if len(tvalue) == 5:
        # Minute must be between 00 and 59
        if int(tvalue[3:5]) > 59:
            return False
            
    return True



def sql_date_validation(dvalue):
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
        


def legible_date_validation(dvalue):
    """
    Validates a date string for m/d/yy or mm/dd/yyyy format during entry.
    It allows for partial input and ensures the structure and values are logical.
    """
    # An empty entry is a valid state
    if not dvalue:
        return True

    # --- Basic structural checks ---
    # 1. Ensure only digits and slashes are used.
    # 2. Prevent more than two slashes or consecutive slashes ('//').
    # 3. A date cannot start with a slash.
    # 4. The total length cannot exceed 10 characters (for mm/dd/yyyy).
    if any(c not in '0123456789/' for c in dvalue) or \
       dvalue.count('/') > 2 or '//' in dvalue or \
       dvalue.startswith('/') or len(dvalue) > 10:
        return False

    # Split the input into parts to validate month, day, and year individually
    parts = dvalue.split('/')

    # --- Part-by-part validation ---
    
    # Validate month (part 1)
    if len(parts) >= 1:
        month = parts[0]
        # Month can't be longer than 2 digits or have a value > 12.
        if len(month) > 2 or (month and int(month) > 12):
            return False
        # A two-digit month can't be '00'.
        if len(month) == 2 and int(month) == 0:
            return False

    # Validate day (part 2)
    if len(parts) >= 2:
        day = parts[1]
        # Day can't be longer than 2 digits or have a value > 31.
        if len(day) > 2 or (day and int(day) > 31):
            return False
        # A two-digit day can't be '00'.
        if len(day) == 2 and int(day) == 0:
            return False

    # Validate year (part 3)
    if len(parts) == 3:
        year = parts[2]
        # Year can be 2 (yy) or 4 (yyyy) digits, so max length is 4.
        if len(year) > 4:
            return False
            
    # --- Semantic checks for partial input ---

    # A single-digit month or day cannot be '0' if it's complete (i.e., followed by a slash)
    # This prevents invalid dates like '0/5/24' or '4/0/24'.
    if len(parts) > 1 and parts[0] == '0':
        return False
    if len(parts) > 2 and parts[1] == '0':
        return False

    # If all checks pass, the input is valid so far
    return True


class ToolTip(object):
    """
    Create a tooltip for a given tkinter widget.
    """
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)
        self.tipwindow = None

    def enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        # Creates a toplevel window
        self.tipwindow = tk.Toplevel(self.widget)
        self.tipwindow.wm_attributes("-topmost", True)

        # Leaves only the label and removes the app window
        self.tipwindow.wm_overrideredirect(True)
        self.tipwindow.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tipwindow, text=self.text, justify='left',
                       background="#ffffe0", relief='solid', borderwidth=1,
                       font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def close(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
