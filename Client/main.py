# Chatapp Main page (all the cilent side code)
# By Sam Marinovich 2022
# Only github repostry is need (won't when compiled)
from tkinter import *
from tkinter import messagebox
from tkinter.font import *
import socket
import errno
import sys
import webbrowser
from github import Github

# Global variables and Primary Setup 
uNameFile = open('username.txt', 'r')
global username
username = str(uNameFile.read())
uNameFile.close()
HEADER_LENGTH = 10
PORT = 5001
global connection
connection = True 
defaultValueUNEntry = 'Enter your username...'
defaultValueMsg = 'Enter your message...'
# Assume the conntection will happen, this will change in below function

# Get IP Using stored file in Github
githubLink = '' # GitHub link has been removed, such that directory can not be found
try:
    g = Github(githubLink)
    githubUser = g.get_user()
    repository = githubUser.get_repo('IP')
    fileContent = repository.get_contents('IP.txt')
    IP = fileContent.decoded_content.decode()
except:
    IP = '0.0.0.0' # Dummy IP, or else program will have a fit


# Establish Connection to the server
def connetionProcess():
    global connection
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((IP, PORT))
        client_socket.setblocking(False)
        extUsername = username.encode('utf-8')
        username_header = f'{len(extUsername):<{HEADER_LENGTH}}'.encode('utf-8')
        client_socket.send(username_header + extUsername)
        connection = True
    except socket.error as e:
        connection = False


# Main Window of the app, with the chatting functionality
class main: 
    def __init__(self, parent):
        #Setting up the Main, or root window
        self.myParent = parent      
        self.myParent.title('ChatApp')
        self.myParent.geometry('502x402')
        self.myParent.resizable(False, False)
        self.myParent.iconbitmap('msgicon.ico')
        self.defaultFont = nametofont("TkDefaultFont")
        self.defaultFont.configure(family="Arial")
        self.firstMsg = True
        #Information bar, for user Info
        self.infoBar = Frame(parent, height=300, width=150, relief=SUNKEN, borderwidth=1)
        self.infoBar.pack_propagate(0)
        self.infoBar.config(highlightbackground='black', highlightthickness=1)

        self.uNameLabel = Label(self.infoBar, text='Current Username:\n' + username)
        self.uNameLabel.grid(row=0, column=0, pady=(10,0)) # have to put this line seperateely, so it is recognised and can be edited elsewhere
        self.changeUNameButton = Button(self.infoBar, text='Change Username', cursor='hand2', command=self.changeUName)
        self.changeUNameButton.grid(row=1, column=0)
        if connection:
            self.connectionStatus = Label(self.infoBar, text='Connected to Chatroom', fg='#00D100')
        else:
            self.connectionStatus = Label(self.infoBar, text='NO CONNECTION', fg='#FF0000')
        self.connectionStatus.grid(row=2, column=0)
        self.reconnectButton = Button(self.infoBar, text='Reconnect', cursor='hand2', command=self.reconnect)
        self.reconnectButton.grid(row=3, column=0)
        self.spacer1 = Frame(self.infoBar, height=26, width=146)
        self.spacer2 = Frame(self.infoBar, height=205, width=146).grid(row=4, column=0) #This exists to create space between the 2 elements, and seperate them
        if connection:
            self.reconnectButton.grid_forget()
            self.spacer1.grid(row=3, column=0)
        self.helpLabel = Label(self.infoBar, text='For help, check out \nthe help page below', anchor=CENTER).grid(row=5, column=0)
        self.helpButton = Button(self.infoBar, text='Help Page', cursor='hand2', command=self.openHelpPage)
        self.helpButton.grid(row=6, column=0, pady=(3,7))

        self.infoBar.place(x=1, y=1, height=400, width=150)

        # Setting up the message box
        self.msgBox = Label(parent, text='Welcome to Chatroom, all messages will be posted here.', bd=1, bg='#DCDCDC', wraplength=340, anchor=N+W, padx=10, justify=LEFT)
        self.msgBox.place(x=151,y=1, height=375, width=350)

        # Set up for the user interactions, message entry and sen
        self. msg = StringVar()
        self.userEntry = Entry(parent, textvariable=self.msg)
        self.userEntry.bind('<FocusIn>', lambda e: self.on_entry_click(e, self.userEntry, defaultValueMsg, self.msg))
        self.userEntry.bind('<FocusOut>', lambda e: self.on_focusout(e, self.userEntry, defaultValueMsg, self.msg))
        self.userEntry.insert(0, defaultValueMsg)
        self.userEntry.config(fg='grey')
        self.userEntry.place(x=152, y=376, width=275, height=25)
        self.sendBtn = Button(parent, cursor='hand2', text='Send', command=lambda: self.sendMsg(self.msg.get())).place(x=428, y=376, height=25, width=73)
        if connection == False:
            self.errorMsg(1, '')

    # On command of the reconnect button, will attempt to recconect to server
    def reconnect(self):
       connetionProcess()
       if connection:
           # If the connection is successful, then the screen elements will be updated, and the main process will run
           self.connectionStatus.config(text='Connected to Chatroom', fg='#00D100')
           self.reconnectButton.grid_forget()
           self.spacer1.grid(row=3, column=0)
           self.myParent.after(2000, self.mainFn)
    
    # If error number 2 occurs (disconnected will app is opne), this will update all the screen elements, so the program doesn't is in NO CONNECTION mode
    def disconnect(self):
        self.connectionStatus.config(text='NO CONNECTION', fg='#FF0000')
        self.spacer1.grid_forget()
        self.reconnectButton.grid(row=3, column=0)
        global connection
        connection = False

    # Func will occur when the button is pushed.
    def changeUName(self):
        # Disactive button, and create popup
        self.changeUNameButton.config(state=DISABLED, cursor='')
        self.uNamePage = Toplevel()
        self.uNamePage.title('Change Username')
        self.uNamePage.iconbitmap('msgicon.ico')
        self.changeInfo = Label(self.uNamePage, text='Enter your new username (It must be 10 or less characters):' , height=1).grid(row=0, column=0)
        self.newUname = StringVar()
        self.newUserEntry = Entry(self.uNamePage, width=50,textvariable=self.newUname)
        self.newUserEntry.bind('<FocusIn>', lambda e: self.on_entry_click(e, self.newUserEntry, defaultValueUNEntry, self.newUname))
        self.newUserEntry.bind('<FocusOut>', lambda e: self.on_focusout(e, self.newUserEntry, defaultValueUNEntry, self.newUname))
        self.newUserEntry.insert(0, defaultValueUNEntry)
        self.newUserEntry.config(fg='grey')
        self.newUserEntry.grid(row=1, column=0, sticky='nesw')
        self.confirmNewEntry = Button(self.uNamePage, text='Confirm', cursor='hand2', command=lambda: self.newUnameChange(self.newUname.get())).grid(row=1, column=1, sticky='nesw')
        # Change what happens when the window close button is pushed. 
        self.uNamePage.protocol('WM_DELETE_WINDOW', lambda: self.onClose(self.uNamePage, self.changeUNameButton))

    def on_entry_click(self, event, entry, defaultValue, currentValue):
    #function that gets called whenever entry is clicked
        if currentValue.get() == defaultValue:
            entry.delete(0, "end") # delete all the text in the entry
            entry.insert(0, '') #Insert blank for user input
            entry.config(fg = 'black')

    def on_focusout(self, event, entry, defaultValue, currentValue):
        if currentValue.get() == '':
            entry.insert(0, defaultValue)
            entry.config(fg = 'grey')

    def newUnameChange(self, newUserName):
        # Runs the closing command on the submision button push
        self.onClose(self.uNamePage, self.changeUNameButton)
        if newUserName != '' and newUserName.lower() != 'Webmaster'.lower() and len(newUserName) <= 10 and newUserName != defaultValueUNEntry:
            # If a valid name is enterd, change the var & update the screen
            global username
            username = newUserName
            self.uNameLabel.configure(text = 'Current Username:\n' + username)
            # Update the username file
            uNameFile = open('username.txt', 'w+')
            uNameFile.truncate(0)
            uNameFile.write(username)
            uNameFile.close()
            # Disconnect from server, and reconnect with new name
            if connection:
                client_socket.close()
                connetionProcess()

    def openHelpPage(self):
        # Set up for the help Page
        self.helpButton.config(state=DISABLED, cursor='')
        self.helpPage = Toplevel()
        self.helpPage.title('Help')
        self.helpPage.iconbitmap('msgicon.ico')
        self.helpPage.resizable(False, False)

        qFont = Font(family='Helvetica', size=10, weight='bold') #Question Font
        # All the help page text (all questions and answers are refered to as qx and ax)
        self.title = Label(self.helpPage, text='ChatApp - Help Page', font=Font(size=25)).pack()
        self.q1 = Label(self.helpPage, font=qFont, justify=LEFT, text='What is ChatApp?').pack(anchor=W)
        self.a1 = Label(self.helpPage, wraplength=700, justify=LEFT, text='ChatApp is an chatroom, which allows mutple users to connect and talk to other users. All a user has to do is turn on the app, and they can freely talk to others. To disconnect, simply close the app.').pack(anchor=W)
        self.q2 = Label(self.helpPage, font=qFont, justify=LEFT, text='How do I send a message?').pack(anchor=W)
        self.a2 = Label(self.helpPage, wraplength=700, justify=LEFT, text='On the bottom of the main screen, there is a text box. Fill this with your message, and push the send button to send your messages to other.').pack(anchor=W)
        self.q3 = Label(self.helpPage, font=qFont, justify=LEFT, text='How do I change my username?').pack(anchor=W)
        self.a3 = Label(self.helpPage, wraplength=700, justify=LEFT, text='At the top left side of the screen, underneath where your username is the "Change Username" button. Pushing this will open the Change Username Menu.').pack(anchor=W)
        self.q4 = Label(self.helpPage, font=qFont, justify=LEFT, text='What does NO CONNECTION mean on the side of the screen?').pack(anchor=W)
        self.a4 = Label(self.helpPage, wraplength=700, justify=LEFT, text='NO CONNECTION means that you can not connect to the Chatroom Server. Often there will be an error along with this, and here are some common errors and their fixes below. There is also the "reconnect", which will attempt to connect the user back to the server. This will not always work, but is a good attempt to see if the connection can be remade. Try an option below if this does not work.').pack(anchor=W)
        self.q41 = Label(self.helpPage, font=Font(family='Helvetica', size=8, weight='bold'), justify=LEFT, text='Connection Error 1').pack(anchor=W)
        self.a41 = Label(self.helpPage, wraplength=700, justify=LEFT, text='This occurs when you can not connect to the server upon launch of the program. This can occur because of either the connection to the chat room is down, or it is blocked by your wifi. Possible fixes for this include changing your network, either to a hotspot or a personal conenction, with less website blocking and restrcitions.').pack(anchor=W)
        self.q42 = Label(self.helpPage, font=Font(family='Helvetica', size=8, weight='bold'), justify=LEFT, text='Connection Error 2').pack(anchor=W)
        self.a42 = Label(self.helpPage, wraplength=700, justify=LEFT, text='This occurs when the server closes while the app is open. This can either be from your network disconnecting and dropping out, or due to the server being turned off. Push the reconnect button, to test to see if the server was just quickly being restarted, then check your connection.').pack(anchor=W)
        self.q43 = Label(self.helpPage, font=Font(family='Helvetica', size=8, weight='bold'), justify=LEFT, text='General Error').pack(anchor=W)
        self.a43 = Label(self.helpPage, wraplength=700, justify=LEFT, text='This occurs when the program faces an error, it does not know how to handle, and it closes. Often, it is fine when it is turned back on. A key examples is changing networks, or closing and turning back on the computer. If the error persisits, please contact the developer (info below).').pack(anchor=W)
        self.q5 = Label(self.helpPage, font=qFont, justify=LEFT, text='Who is Webmaster?').pack(anchor=W)
        self.a5 = Label(self.helpPage, wraplength=700, justify=LEFT, text='Webmaster is the server, and it will notify everyone of anyone who has recently joined or left the chatroom. You can not set your name to Webmaster, but if you see a message from Webmaster, it tells you that there is someone else out their to chat with.').pack(anchor=W)
        self.q6 = Label(self.helpPage, font=qFont, justify=LEFT, text='Any other questions?').pack(anchor=W)
        self.a6 = Label(self.helpPage, wraplength=700, justify=LEFT, text='Check out the User Documentation, for more info, including a tutorial and more indepth troubleshooting. Link is below:').pack(anchor=W)
        self.a61 = Label(self.helpPage, text='User Documentation', fg='#0000FF', cursor='hand2', font=Font(underline=True, size=10, family='Helvctica'))
        self.a61.pack(anchor=W)
        self.a61.bind("<Button-1>", lambda e: webbrowser.open_new("https://docs.google.com/document/d/1ReU2hCJBA60_aMuTNeq1AXUTXAiQDdeeX3akK_C_bIA/edit?usp=sharing")) # in 3 parts, so the text can be hypertext and redirect to user documentation
        self.dev = Label(self.helpPage, text='\xa9 Samuel Marinovich 2022. Email: samuelm2022@student.stlukes.nsw.edu.au').pack()
        # Change what happens when the window is closed
        self.helpPage.protocol('WM_DELETE_WINDOW', lambda: self.onClose(self.helpPage, self.helpButton))

    # This will run when a Toplevel window is closed, which reactives the button, and closes the window
    def onClose(self, window, button):
        window.destroy()
        button.config(state=ACTIVE)


    def sendMsg(self, msg):
        # If there is a connection, and a valid message was entered
        if msg != '' and connection:
            # Encode and send message
            message = msg.encode('utf-8')
            message_header = f'{len(message) :< {HEADER_LENGTH}}'.encode('utf-8')
            client_socket.send(message_header + message)
            if self.firstMsg == True:
                # Update the message display (if first time delete the current contents)
                self.msgBox.config(text = f'{username} > {msg}')
                self.msgBox.config(anchor=S+W)
                self.firstMsg = False
            else:
                # Update the screen contents
                self.msgBox.config(text = self.msgBox.cget('text') + f'\n{username} > {msg}' )
        self.userEntry.delete(0, END)

    def mainFn(self):
        try: 
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                self.errorMsg(2, '')
                self.disconnect()
                return                

            username_length = int(username_header.decode("utf-8").strip())
            recvUsername = client_socket.recv(username_length).decode('utf-8')

            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            if self.firstMsg == True:
                self.msgBox.config(text = f'{recvUsername} > {message}')
                self.msgBox.config(anchor=S+W)
                self.firstMsg = False
            else:
                self.msgBox.config(text = self.msgBox.cget('text') + f'\n{recvUsername} > {message}' )

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                self.errorMsg(3, e)
                sys.exit()

        except Exception as e:
            # General System error, will cause a restart
            self.errorMsg(3, e)
            sys.exit()
        self.myParent.after(2000, self.mainFn)

    # Any major errors that appear, are all identified here (so less strings all over the place)
    def errorMsg(self, msgNum, e):
        eMsg = ''
        if msgNum == 1:
            eMsg = 'Connection Error 1: Not able to connect to Chatroom - Check Connection'
        elif msgNum == 2:
            eMsg ='Connection Error 2: Chatroom has been shut down'
        elif msgNum == 3:
            eMsg = 'Reading Error, the app will now close. Please connect the develop (info found on help page). More info: ' + str(e)
        messagebox.showerror(title='Error', message=eMsg)

# This menu will load if a user has never been on the app (and has no username)
class firstTimeMenu:
    def __init__(self, parent, failedUNameEntry):
        # Setup of the window
        self.myParent = parent
        self.myParent.title('Chat App')
        self.myParent.iconbitmap('msgicon.ico')
        self.myParent.resizable(False, False)
        self.defaultFont = nametofont("TkDefaultFont")
        self.defaultFont.configure(family="Helvetica")

        self.title = Label(self.myParent, text='Welcome to ChatApp', font=(25)).grid(row=0, column=0, columnspan=2)
        self.mainInfo = Label(self.myParent, justify=LEFT, wraplength=500, text='ChatApp is a chatroom, which can allow multiple users to connect and talk to each on different devices. Please enter a username into the box, then push the submit button.\nIf a name is not properly entered, you will have 3 attempts, before the app closes.\nUsernames must be 10 or less characters.').grid(row=1, column=0, columnspan=2)
        # Adds a warning if a failed username attempt occured
        if failedUNameEntry < 3:
            self.warningLabel = Label(self.myParent, text='Username Entry Attempts left: ' + str(failedUNameEntry), fg='#FF0000').grid(row=2, column=0, columnspan=2)
        
        # Similar setup as with the name change window
        self.newUname = StringVar()
        self.newUserEntry = Entry(self.myParent, width=50, textvariable=self.newUname)
        self.newUserEntry.bind('<FocusIn>', self.on_entry_click)
        self.newUserEntry.bind('<FocusOut>', self.on_focusout)
        self.newUserEntry.insert(0, defaultValueUNEntry)
        self.newUserEntry.config(fg='grey')
        self.newUserEntry.grid(row=3, column=0, sticky='nesw')
        self.confirmNewEntry = Button(self.myParent, text='Confirm', cursor='hand2', command=lambda: self.createUName(self.newUname.get())).grid(row=3, column=1, sticky='nesw')

    def on_entry_click(self, event):
    #function that gets called whenever entry is clicked
        if self.newUname.get() == defaultValueUNEntry:
            self.newUserEntry.delete(0, "end") # delete all the text in the entry
            self.newUserEntry.insert(0, '') #Insert blank for user input
            self.newUserEntry.config(fg = 'black')

    def on_focusout(self, event):
        if self.newUname.get() == '':
            self.newUserEntry.insert(0, defaultValueUNEntry)
            self.newUserEntry.config(fg = 'grey')
    
    def createUName(self, newUsername):
        # Similar function to the other name change, except doesn't need to connect and reconnect (as there is no connection yet)
        global username
        username = newUsername
        uNameFile = open('username.txt', 'w+')
        uNameFile.truncate(0)
        uNameFile.write(username)
        uNameFile.close()
        self.myParent.destroy()


# Main logic flow
usernameFailure = 3
while (username == '' and  usernameFailure > 0) or len(username) > 10 or username.lower() == 'Webmaster'.lower() or username == defaultValueUNEntry:
    # Will give 3 attempts to setup a username, before closing the app
    startup = Tk()
    startupScreen = firstTimeMenu(startup, usernameFailure)
    startup.mainloop()
    usernameFailure -= 1 # Will only be needed if the username was not entered
    if usernameFailure <= 0:
        break

if username != '' and username.lower() != 'Webmaster'.lower() and len(username) <= 10 and username != defaultValueUNEntry:
    connetionProcess()
    mainPage = Tk()
    mainWindow = main(mainPage)
    if connection:
        # If connected to the chatroom the run the recieve command
        mainPage.after(5000, mainWindow.mainFn)
    mainPage.mainloop()