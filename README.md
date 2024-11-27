The API, Data Pull Multi file is a mutlithreaded pull of all the data from each device we defined in the large dictionary in the file. 
Line 153 to 158 is where I am trying to account for when my credentials expire, I just want the entire script to close and then reopen, which is proving quite difficult. 
Attempts:
sys.exit() only exits the single thread
os.exit(0) Stops the script form continuing, but the program is still running as evident by the command prompt window still being open. 
Current Attempt
Utilizing AHK WinClose() Function to close the command prompt window and therefore the main process. Reopening is currently done by the #AE API GUI script when it detects that the M Access DB has not been updated in 10 minutes. 
