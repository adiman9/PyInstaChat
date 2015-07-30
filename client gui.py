


#LOOK INTO THE LOG FILE NOT BEING GENERATED





##import cn_Fn
from Tkinter import *
from socket import *
import time, threading, Queue, time

Info1 = 'Input the user name and port you want to use in chat room.'
Info2 = 'Name length should at least one letter and no more than 16 letters.'
Info3 = 'Port number should be integar and over 2000'
Info3_1 = 'Port number should be integar'
Info4 = 'Not valid IPv4 address format. Example 192.168.2.1'


def pkg(Type, IPaddr, port, ID=""):
    """
    Package the clients (IP, Port):ID information in string for 
    transmit. 'Type' indicates the purpose of the package: 
    'R'(Requesting Information Package)
    'K'(Offline Information Package)
    """
    if not ID:
        info = Type+':'+IPaddr + ':' + str(port)
    else:
        info = Type+':'+IPaddr + ':' + str(port) + ':' + ID
    return info
    
def dpkg(info):
    """
    depackage the packed received string to (IP, Port):ID format. 
    """
    n = info.split(':')
    if len(n)==4:
        return (n[0], n[1], int(n[2]), n[3])
    else:
        return (n[0], n[1], int(n[2]))



#---------------------------------------------------#
#----------------Quest GUI Window ------------------#
#---------------------------------------------------#

class Quest_GUI_Win(Tk):
    """ 
    Creating the Quest GUi window where asking client to input username
    and port number they want to use for communicate. It also request client
    to input the server IP address for accessing the latest client list
    """
    def __init__(self):
        
        Tk.__init__(self)
        self.title('Quest')
        questWindow = Frame(self)
        questWindow.grid()
        info1_lbl = Label(questWindow, text=Info1)
        info2_lbl = Label(questWindow, text=Info2)
        info3_lbl = Label(questWindow, text=Info3)
        user_lbl = Label(questWindow, text='user name')
        self.user_ent = Entry(questWindow)
        port_lbl = Label(questWindow, text='UDP port')
        self.port_ent = Entry(questWindow)
        server_add_lbl = Label(questWindow, text='server IP address')
        self.server_add_ent = Entry(questWindow)
        confirm_bttn = Button(questWindow, text='Confirm', command=self.reveal)
        quit_bttn = Button(questWindow, text='Cancel', command=self.destroy)
        
    ##  place wedges
        info1_lbl.grid(row=0, column=0, columnspan=3, sticky=W,padx=10)
        info2_lbl.grid(row=1, column=0,columnspan=3, sticky=W,padx=10)
        info3_lbl.grid(row=2, column=0,columnspan=3, sticky=W,padx=10)
        user_lbl.grid(row=3, column=0,sticky=W,padx=10)
        self.user_ent.grid(row=4, column=0,sticky=W,padx=10)
        port_lbl.grid(row=3, column=1,sticky=W)
        self.port_ent.grid(row=4, column=1, sticky=W)
        server_add_lbl.grid(row=5, column=0,sticky=W,padx=10)
        self.server_add_ent.grid(row=6, column=0,sticky=W,padx=10)
        confirm_bttn.grid(row=7, column=0, pady=10)
        quit_bttn.grid(row=7, column=1)

    def reveal(self):
        """ 
        Check the input information follows the instruction and create the
        first connection with server. Then start server_refresh thread and 
        open the user defined UDP socket listening thread
        """
        global myID
        global myIP
        global serverIP
        global myPort
        global sock
        global server_refresh
        global re
        myID = self.user_ent.get()
        myPort = self.port_ent.get()
        serverIP = self.server_add_ent.get()
        if (len(myID)<1) or (len(myID)>18):
            showerror("Name Length Error", Info2)
        else:
            try:
                val = int(myPort)
                if val<2000: #2048 check it later?
                    showerror("Port Number Error", Info3)
                else:
                    self.destroy()
                    NewTitle = 'Chat_dic v1.0:' +' '+myID+' (' + myIP + ':' + myPort+' )'
                    chat_win = Chat_GUI_Win(NewTitle)  
                    myAddress = (myIP, int(myPort))
                    sock = socket(AF_INET, SOCK_DGRAM)
                    sock.bind(myAddress)
                    connect_server(myID, myPort, serverIP, 2002, 'R','[ Succesfully connected with server]\n')
                    server_refresh=Server_Alive()
                    re =  Receiving(sock)

                    server_refresh.start()
                    re.start()

##                    host_socket.bind((myIPaddr, val))
##                    host_socket.listen(5)
##                    waitconnect.start()
            except ValueError:
                showerror("Port Number Error", Info3)
                

#---------------------------------------------------#
#------------------ Chat Window  -------------------#
#---------------------------------------------------#            
class Chat_GUI_Win(Tk):
    """ 
    GUI for client communicate with each other. There are three main block 
    in layout: Chatlog, where show the communicate information including 
    chating content and connection information; EntryBox, where for user to
    input the message for sending to other clients; FriList, where show the 
    online friends.
    """
    def __init__(self,newtitle):
        global chat_Chatlog
        global chat_EntryBox
        global chat_FriList
        Tk.__init__(self)
        self.title(newtitle)
        self.protocol("WM_DELETE_WINDOW", self.cls_chat_win)
        self.geometry("410x500")
        #-----Chat Window---------------- 
        chat_Chatlog = Text(self, bd=0, bg="white", height="8", width="50", font="Arial")
##        chat_Chatlog.insert(END, "Waiting for your friend to connect..\n")
        chat_Chatlog.config(state=DISABLED)

        #Bind a scrollbar to the Chat window
        chat_scrollbar = Scrollbar(self, command=chat_Chatlog.yview, cursor="heart")
        chat_Chatlog['yscrollcommand']=chat_scrollbar.set

        #Create the box to enter message
        chat_EntryBox = Text(self,bd=0, bg="white", width="29", height="5", font="Arial")
        chat_EntryBox.bind("<Return>", DisableEntry)
        chat_EntryBox.bind("<KeyRelease-Return>", PressAction)
                        
        # Create Online Friend List
        chat_FriLIst_lbl = Label(self, font=22, text='Friend List')
        chat_FriList = Listbox(self, selectmode=MULTIPLE)

        # Create the Button to send message
        chat_Sendbttn = Button(self, font=30, text="Send", width="12", height="5", command=ClickAction)
        
        chat_Chatlog.place(x=6,y=6, height=386, width=265)
        chat_scrollbar.place(x=6,y=6, height=386, width=266)
        chat_EntryBox.place(x=6, y=401, height=90, width=265)
        chat_FriLIst_lbl.place(x=280, y=8, height=12, width=120)
        chat_FriList.place(x=280, y=22, height=200, width=120)
        chat_Sendbttn.place(x=280, y=401, height=90)
        


    def cls_chat_win(self):
        """
        close the Chat_GUI_Win trigger function to stop the rest threads
        """
        self.destroy()
        cls_connect()


def updateFriendsli():
    global chat_FriList
    global neighbor_list
    
    for y in neighbor_list:
        if len(y) > 2:
            equal = False
            
            for x in range(0, chat_FriList.size()):
                if chat_FriList.get(x) == y[2]:
                    equal = True

            if not equal:
                chat_FriList.insert(END, y[2])

    for y in range(0, chat_FriList.size()):
        equal = False
        for x in neighbor_list:
        
            if len(x) > 2:
                if chat_FriList.get(y) == x[2] :
                    equal = True

        if not equal:
            chat_FriList.delete(y)


#---------------------------------------------------#
#----------------- KEYBOARD EVENTS -----------------#
#---------------------------------------------------#
def PressAction(event):
    global chat_EntryBox
    chat_EntryBox.config(state=NORMAL)
    ClickAction()
def DisableEntry(event):
    global chat_EntryBox
    chat_EntryBox.config(state=DISABLED)

#---------------------------------------------------#
#------------------ MOUSE EVENTS -------------------#
#---------------------------------------------------#
def ClickAction():
    global chat_EntryBox
    global neighbor_list
    global chat_FriList
    selectionmade = False

    for x in range(0, chat_FriList.size()):
        selection = chat_FriList.selection_includes(x)

        if selection:
            selectionmade = True
    
    

    if selectionmade:
        #Write message to chat window
        EntryText = FilteredMessage(chat_EntryBox.get("0.0",END))
        LoadMyEntry(EntryText)

        #Scroll to the bottom of chat windows
        #chat_Chatlog.yview(END)

        #Erace previous message in Entry Box
        chat_EntryBox.delete("0.0",END)

        for x in range(0, chat_FriList.size()):
            selection = chat_FriList.selection_includes(x)
            
            if selection:
                selectionName = chat_FriList.get(x)

                for y in neighbor_list:
                    if y[2] == selectionName:
                        friendID = y
                        sendMessage(friendID, EntryText + '\: ' + myIP + '\: ' + myPort + '\: ' + myID)
                        break





#Send my mesage to all others
def sendMessage(sendTo, message):

    s = socket(AF_INET, SOCK_DGRAM)

    s.connect((sendTo[0],sendTo[1]))

    s.send(message)

    s.close

    """
    student need to create the function for sending the message themselves
    here
    """

#---------------------------------------------------#
#------------------ Load Entris  -------------------#
#---------------------------------------------------#
def FilteredMessage(EntryText):
    """
    Filter out all useless white lines at the end of a string,
    returns a new, beautifully filtered string.
    """
    EndFiltered = ''
    for i in range(len(EntryText)-1,-1,-1):
        if EntryText[i]!='\n':
            EndFiltered = EntryText[0:i+1]
            break
    for i in range(0,len(EndFiltered), 1):
            if EndFiltered[i] != "\n":
                    return EndFiltered[i:]+'\n'
    return ''

def LoadconnectInfo(EntryText):
    """ 
    Load the connection information and put them on Chatlog
    """
    global chat_Chatlog
    if EntryText != '':
        chat_Chatlog.config(state=NORMAL)
        if chat_Chatlog.index('end') != None:
            chat_Chatlog.insert(END, EntryText+'\n')
            chat_Chatlog.config(state=DISABLED)
            chat_Chatlog.yview(END)

def LoadMyEntry(EntryText):
    """ 
    Load user input information and put them on Chatlog
    """
    global chat_Chatlog
    if EntryText != '':
        chat_Chatlog.config(state=NORMAL)
        if chat_Chatlog.index('end') != None:
            LineNumber = float(chat_Chatlog.index('end'))-1.0
            chat_Chatlog.insert(END, "You: " + EntryText)
            chat_Chatlog.tag_add("You", LineNumber, LineNumber+0.4)
            chat_Chatlog.tag_config("You", foreground="#FF8000", font=("Arial", 12, "bold"))
            chat_Chatlog.config(state=DISABLED)
            chat_Chatlog.yview(END)


def LoadOtherEntry(otherID, EntryText):
    """ 
    Manage the received information from others and put them on Chatlog
    """
    global chat_Chatlog
    if EntryText != '':
        chat_Chatlog.config(state=NORMAL)
        if chat_Chatlog.index('end') != None:
            try:
                LineNumber = float(chat_Chatlog.index('end'))-1.0
            except:
                pass
            chat_Chatlog.insert(END, otherID + ': '  + str(EntryText))
            chat_Chatlog.tag_add(otherID, LineNumber, LineNumber+0.6)
            chat_Chatlog.tag_config(otherID, foreground="#04B404", font=("Arial", 12, "bold"))
            chat_Chatlog.config(state=DISABLED)
            chat_Chatlog.yview(END)
            
#---------------------------------------------------#
#------------------ Connections  -------------------#
#---------------------------------------------------#
class Server_Alive(threading.Thread):
    """ 
    Thread keep connect with server every 30s, and receive the client_list 
    information saved on server.
    """
    def __init__(self): #, myID, myPort, serverIP):
        threading.Thread.__init__(self)
        self.flag= True
        self.Type= 'R'
    def run(self):
        global myID
        global myPort
        global serverIP
        global serverPort
        while self.flag:
            time.sleep(30)
            connect_server(myID, myPort, serverIP, serverPort, self.Type)          
    def stop(self):
        self.flag = False
        self.Type = 'K'
        self._Thread__stop()

class Receiving(threading.Thread):
    """ 
    Thread keep wacthing the user defined UDP socket and receving the messages
    from other clients. 
    """


    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock
        self.flag = True
    def run(self):

        global neighbor_list

        while self.flag:

            msg, addr = self.sock.recvfrom(1024) 

            msg = msg.split('\: ')

            #receiving request for ID
            if msg[0] == 'IDReq':
                sendAddress = [msg[2], int(msg[3])]
                sendMessage(sendAddress, 'ID\: ' + myID + '\: ' + msg[1])
            #receiving ID from other user
            elif msg[0] == 'ID':
                neighbor_list[int(msg[2])].append(msg[1])
                updateFriendsli()
            else:

                #Load message from other user
                LoadOtherEntry(msg[3], str(msg[0]))

    def stop(self):
        self.flag = False
        self._Thread__stop()
            
def connect_server(myID, myPort, SERVER_ADD, SERVER_PORT,  Type, Info=''):
    """ 
    connect the server. If Type is Requesting('R'), then receive the 
    client_list transmitted from server. If Type is Offline('K'), then
    close down without expecting receive anything from server
    """
    global neighbor_list

    s = socket(AF_INET, SOCK_STREAM)
    s.connect((SERVER_ADD, SERVER_PORT))
    LoadconnectInfo(Info)
    s.send(pkg(Type, myIP, myPort, myID))
    if Type == 'R':
        data = s.recv(1024)
        server_recv=data

        if data:
            if data.split('-')[0] == 'Null':
                print 'no neighbors right now'
            else:
                count = 0
                while (count < int(data.split('-')[0])):
                    info = s.recv(1024)
                    server_recv += info
                    count += 1
                    
                neighbor = server_recv.split('-')
                
                count = 0
                neighbor_list = []
                while (count < int(neighbor[0])):
                    IP_addr = neighbor[count+1].split(':')
                    if (myIP, int(myPort)) != (IP_addr[1],int(IP_addr[2])):
                        neighbor_list.append([IP_addr[1],int(IP_addr[2])])
                    count += 1
                countVal = 0

                for x in neighbor_list:
                    sendMessage(x, "IDReq\: " + str(countVal)  + '\: ' + myIP + '\: ' + str(myPort))

                    countVal += 1
                updateFriendsli()
    s.close()

def client_offline():
    """ 
    send the offline informationm to server
    """
    global myID
    global myPort
    global serverIP
    global serverPort
    connect_server(myID, myPort, serverIP, serverPort,  'K')

def cls_connect():
    """
    close all the threads and socket 
    """
    server_refresh.stop()
    client_offline()
    re.stop()
    sock.close()


    #close socket and close the window
##    Close_connect()
##    host_socket.close()

myID=''
myIP = gethostbyname(gethostname())
myPort=''
chat_Chatlog=''
chat_EntryBox=''
serverIP=''
serverPort=2002
neighbor_list = [] #[(IP,Port),(IP,Port)]
sock=''
server_refresh=''
re=''

app = Quest_GUI_Win()
app.mainloop()