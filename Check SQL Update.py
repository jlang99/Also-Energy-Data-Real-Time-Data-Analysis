import pyodbc
import datetime
import os
import sys
import time as ty

# Add the parent directory ('NCC Automations') to the Python path
# This allows us to import the 'PythonTools' package from there.
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from PythonTools import CREDS, get_hostname, AE_HARDWARE_MAP


def has_recent_writes(minutes=5):
    """
    Checks if the database has received any writes within the last few minutes.

    Args:
        minutes (int): The number of minutes to check back for recent writes.

    Returns:
        bool: True if there was a write within the specified time, False otherwise.
    """
    #print(f"Checking for database writes in the last {minutes} minutes...")
    HOSTNAME = get_hostname()
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
    with pyodbc.connect(connection_string) as dbconnection:
        with dbconnection.cursor() as cursor:
            time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
            
            for site in AE_HARDWARE_MAP.keys():
                if "meters" in AE_HARDWARE_MAP[site]:
                    table_name = f"[{site} Meter Data]"
                    query = f"SELECT TOP 1 Timestamp FROM {table_name} ORDER BY Timestamp DESC"
                    most_recent_write = cursor.execute(query).fetchval()
                    if most_recent_write and most_recent_write >= time_threshold:
                        return True
        return False

if __name__ == '__main__':
    if has_recent_writes(5):
        print(True)
        ty.sleep(5)
    else:
        print(False)
        ty.sleep(5)
