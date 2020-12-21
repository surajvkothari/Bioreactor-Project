"""
Bioreactor UI
UI designed by Suraj, Iason, Arslan, Arnas
Copyright 2020
"""

import tkinter as tk
import tkinter.ttk
import datetime
import time
import serial

class Colours:
    WHITE = "#F4F4F4"
    BLACK = "#000000"
    BLUE = "#4F87A4"
    DARK_BLUE = "#3E687D"
    RED = "#EF5350"

class ButtonStyles:
    HEATING_BTN = {
        "bg": "#E53935",
        "activebackground": "#F44336",
        "fg": "#FFF",
        "activeforeground": "#FFF",
        "width": 10,
        "relief": "flat",
        "font": ("Arial", '12', 'bold'),
        "cursor": "hand2"
    }

    STIRRING_BTN = {
        "bg": "#1E88E5",
        "activebackground": "#2196F3",
        "fg": "#FFF",
        "activeforeground": "#FFF",
        "width": 10,
        "relief": "flat",
        "font": ("Arial", '12', 'bold'),
        "cursor": "hand2"
    }

    PH_BTN = {
        "bg": "#43A047",
        "activebackground": "#4CAF50",
        "fg": "#FFF",
        "activeforeground": "#FFF",
        "width": 10,
        "relief": "flat",
        "font": ("Arial", '12', 'bold'),
        "cursor": "hand2"
    }

class BioreactorUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Bioreactor Interface")
        self.sizeX, self.sizeY = 1200, 650
        self.geometry(f"{self.sizeX}x{self.sizeY}")
        self.resizable(False, False)
        self.configure(background=Colours.BLUE)

        """ Responsive UI """
        top = self.winfo_toplevel()  # Gets the top level window to resize

        # # Makes the rows and columns of the window responsive by scale factor 1
        top.columnconfigure(0, weight=1)
        top.rowconfigure(0, weight=1)
        top.rowconfigure(1, weight=100)

        self.currentTemp, self.currentRPM, self.currentpH = None, None, None

        """ Initialised setpoints """
        self.heatingSetpoint, self.stirringSetpoint, \
            self.pHSetpoint = 25, 500, 5

        """ Create Header """

        self.header = tk.Frame(self, bg=Colours.WHITE)
        self.homeText = tk.Label(self.header, text="BIOREACTOR INTERFACE", bg=Colours.WHITE,
            fg=Colours.BLACK, font=('Calibri', '18', 'bold'))

        self.header.grid(sticky="new")
        self.homeText.grid(sticky="ns", ipadx=40, pady=15)

        """ Create main UI frame """
        self.mainFrame = tk.Frame(self, bg=Colours.BLUE)
        self.mainFrame.grid(row=1, sticky="nesw", padx=40, pady=15)

        """ Create setpoint frame """
        self.setpointFrame = tk.Frame(self.mainFrame, bg=Colours.DARK_BLUE)
        self.setpointFrame.grid(row=0, column=0, sticky="ns", ipadx=10,
            ipady=20, padx=(0,50))

        self.heatingText = tk.Label(self.setpointFrame, text="Heating Subsystem",
            fg=Colours.WHITE, bg=Colours.DARK_BLUE, font=('Arial', '14', 'bold'))
        self.heatingText.grid(row=0, columnspan=3, pady=10)
        self.heatingSendBtn = tk.Button(self.setpointFrame, text="SEND",
            **ButtonStyles.HEATING_BTN, command= lambda: self.setSetpoint('H'))
        self.heatingSendBtn.grid(row=1, column=0, padx=(20, 0))
        self.heatingSetpointVar = tk.StringVar()  # Setpoint
        self.heatingSetpointVar.set("25.0")
        # The command rounds the setpoint to 1 decimal place
        self.heatingSlider = tk.ttk.Scale(self.setpointFrame, length=200,
            from_=25, to=35, variable=self.heatingSetpointVar,
            command=lambda s:self.heatingSetpointVar.set('%0.1f' % float(s)))
        self.heatingSlider.grid(row=1, column=1, padx=10)
        self.heatingEntry = tk.ttk.Entry(self.setpointFrame, width=5,
            text=self.heatingSetpointVar, justify="center", font=('Arial', 8, 'bold'))
        self.heatingEntry.grid(row=1, column=2, ipady=5)

        self.stirringText = tk.Label(self.setpointFrame, text="Stirring Subsystem",
            fg=Colours.WHITE, bg=Colours.DARK_BLUE, font=('Arial', '14', 'bold'))
        self.stirringText.grid(row=2, columnspan=3, pady=10)
        self.stirringSendBtn = tk.Button(self.setpointFrame, text="SEND",
            **ButtonStyles.STIRRING_BTN, command= lambda: self.setSetpoint('S'))
        self.stirringSendBtn.grid(row=3, column=0, padx=(20, 0))
        self.stirringSetpointVar = tk.StringVar()  # Setpoint
        self.stirringSetpointVar.set("750")
        self.stirringSlider = tk.ttk.Scale(self.setpointFrame, length=200,
            from_=500, to=1500, variable=self.stirringSetpointVar,
            command=lambda s:self.stirringSetpointVar.set('%0.0f' % float(s)))
        self.stirringSlider.grid(row=3, column=1, padx=10)
        self.stirringEntry = tk.ttk.Entry(self.setpointFrame, width=5,
            text=self.stirringSetpointVar, justify="center", font=('Arial', 8, 'bold'))
        self.stirringEntry.grid(row=3, column=2, ipady=5)

        self.pHText = tk.Label(self.setpointFrame, text="pH Subsystem",
            fg=Colours.WHITE, bg=Colours.DARK_BLUE, font=('Arial', '14', 'bold'))
        self.pHText.grid(row=4, columnspan=3, padx=10, pady=10)
        self.pHSendBtn = tk.Button(self.setpointFrame, text="SEND",
            **ButtonStyles.PH_BTN, command= lambda: self.setSetpoint('P'))
        self.pHSendBtn.grid(row=5, column=0, padx=(20, 0))
        self.pHSetpointVar = tk.StringVar()  # Setpoint
        self.pHSetpointVar.set("5.0")
        self.pHSlider = tk.ttk.Scale(self.setpointFrame, length=200,
            from_=3, to=7, variable=self.pHSetpointVar,
            command=lambda s:self.pHSetpointVar.set('%0.1f' % float(s)))
        self.pHSlider.grid(row=5, column=1, padx=10)
        self.pHEntry = tk.ttk.Entry(self.setpointFrame, width=5,
                text=self.pHSetpointVar, justify="center", font=('Arial', 8, 'bold'))
        self.pHEntry.grid(row=5, column=2, ipady=5)

        """ Create log display """
        self.logFrame = tk.Frame(self.mainFrame)
        self.logFrame.grid(row=1, column=0, sticky="nsw", 
            padx=(0, 40), pady=(20, 0))

        self.logText = tk.Label(self.logFrame, text="DATA LOG",
            bg=Colours.DARK_BLUE, fg=Colours.WHITE,
            font=("Calibri", '16', 'bold'), width=29)
        self.logText.grid(row=0, ipadx=2)

        self.logOutput = tk.Text(self.logFrame, bg=Colours.WHITE, fg="#000",
            state="disabled", wrap="none", height=9, width=45, relief="flat",
            padx=0, pady=10, font=('Consolas', '11'))
        self.logOutput.grid(row=1, column=0)
        self.logScrollbar = tk.Scrollbar(self.logFrame, command=self.logOutput.yview)
        self.logOutput['yscrollcommand'] = self.logScrollbar.set
        self.logScrollbar.grid(row=1, column=0, sticky='nse')

        """ Create temperature display """
        self.tempFrame = tk.Frame(self.mainFrame, bg=Colours.DARK_BLUE)
        self.tempFrame.grid(row=0, column=1, sticky="nsew", padx=(0, 30))
        self.tempText = tk.Label(self.tempFrame, text="Temperature (°C)",
            fg=Colours.WHITE, bg=Colours.DARK_BLUE, font=('Arial', '14', 'bold'))
        self.tempText.grid(row=0, padx=30, pady=10)

        self.currentTempVal = tk.Label(self.tempFrame, text="",
            fg=Colours.WHITE, bg=Colours.DARK_BLUE, font=('Calibri', '30', 'bold'))
        self.currentTempVal.grid(row=1, pady=50)

        self.setpointTempVal = tk.Label(self.tempFrame, text="Setpoint: 25",
            fg=Colours.WHITE, bg=Colours.DARK_BLUE, font=('Calibri', '14', 'bold'))
        self.setpointTempVal.grid(row=2)

        """ Create RPM display """
        self.RPMFrame = tk.Frame(self.mainFrame, bg=Colours.DARK_BLUE)
        self.RPMFrame.grid(row=0, column=2, sticky="ns")
        self.RPMText = tk.Label(self.RPMFrame, text="RPM (per min)",
            fg=Colours.WHITE, bg=Colours.DARK_BLUE, font=('Arial', '14', 'bold'))
        self.RPMText.grid(row=0, padx=40, pady=10)

        self.currentRPMVal = tk.Label(self.RPMFrame, text="",
            fg=Colours.WHITE, bg=Colours.DARK_BLUE, font=('Calibri', '30', 'bold'))
        self.currentRPMVal.grid(row=1, pady=46)

        self.setpointRPMVal = tk.Label(self.RPMFrame, text="Setpoint: 0",
            fg=Colours.WHITE, bg=Colours.DARK_BLUE, font=('Calibri', '14', 'bold'))
        self.setpointRPMVal.grid(row=2)

        """ Create pH display """
        self.pHFrame = tk.Frame(self.mainFrame, bg=Colours.DARK_BLUE)
        self.pHFrame.grid(row=1, column=1, sticky="nsw", pady=(20, 0), ipady=0)
        self.pHText = tk.Label(self.pHFrame, text="pH (log[H+])",
            fg=Colours.WHITE, bg=Colours.DARK_BLUE, font=('Arial', '14', 'bold'))
        self.pHText.grid(row=0, padx=51, pady=10)

        self.currentpHVal = tk.Label(self.pHFrame, text="",
            fg=Colours.WHITE, bg=Colours.DARK_BLUE, font=('Calibri', '30', 'bold'))
        self.currentpHVal.grid(row=1, pady=20)

        self.setpointpHVal = tk.Label(self.pHFrame, bg=Colours.DARK_BLUE,
            text="Setpoint: 5", fg=Colours.WHITE, font=('Calibri', '14', 'bold'))
        self.setpointpHVal.grid(row=2)

        """ Create Time display """
        self.timeFrame = tk.Frame(self.mainFrame, bg=Colours.DARK_BLUE)
        self.timeFrame.grid(row=1, column=2, sticky="nsw", pady=(20, 0))
        self.timeText = tk.Label(self.timeFrame, text="Time (h:m:s)",
            fg=Colours.WHITE, bg=Colours.DARK_BLUE, font=("Arial", "14", "bold"))
        self.timeText.grid(row=0, padx=46, pady=10)

        self.currentTimeVal = tk.Label(self.timeFrame, text="0:00:00",
            fg=Colours.WHITE, bg=Colours.DARK_BLUE, font=("Calibri", "30", "bold"))
        self.currentTimeVal.grid(row=1, pady=25)


        """ Create footer """

        self.footer = tk.Frame(self, bg=Colours.WHITE)
        self.copyrightMessage = "Copyright © 2020 Bioreactor." \
            "All Rights Reserved. Team: Suraj, Iason, Arslan, Arnas"

        self.copyrightText = tk.Label(self.footer, text=self.copyrightMessage,
            bg=Colours.WHITE, fg=Colours.BLACK, font=("Arial", "10"))
        self.footer.grid(row=2, sticky="we")
        self.copyrightText.grid()

        """ Start timer """
        self.runTimeStart = datetime.datetime.now()
        
        """ Run main UI loop """
        self.ser = serial.Serial("/tmp/simavr-uart0", 9600)
        log_timestamp = time.ctime(time.time())
        self.data_log_file = f"data_log_{log_timestamp}.txt"
        with open(self.data_log_file, "a") as f:
            f.write("Temp  RPM  pH   Time\n")
        
        #self.moving_avg_heating = []
        self.cumulative_sum, self.counter, self.move = [0], 1, 15
            
        self.bioreactorLoop()
      
     
    def add_log(self, line):       
        self.logOutput.configure(state="normal")
        self.logOutput.insert("1.0", line+"\n")
        self.logOutput.configure(state="disabled")



    def setSetpoint(self, ID):
        if ID == 'H':
            self.heatingSetpoint = float(self.heatingEntry.get())
            if self.heatingSetpoint >= 25 and self.heatingSetpoint <= 35:                
                self.setpointTempVal.config(text=f"Setpoint:  {self.heatingSetpoint}")
                self.writeData("HW", self.heatingSetpoint)                

        elif ID == 'S':
            self.stirringSetpoint = int(self.stirringEntry.get())
            if self.stirringSetpoint >= 500 and self.stirringSetpoint <= 1500:
                self.setpointRPMVal.config(text=f"Setpoint:  {self.stirringSetpoint}")
                self.writeData("SW", self.stirringSetpoint)

        elif ID == 'P':
            self.pHSetpoint = float(self.pHEntry.get())
            if self.pHSetpoint >= 3 and self.pHSetpoint <= 7:
                self.setpointpHVal.config(text=f"Setpoint:  {self.pHSetpoint}")
                self.writeData("PW", self.pHSetpoint)                


    def updateCurrentValues(self, ID, data):
        if ID == "HR":
            self.currentTemp = data
            self.currentTempVal.config(text=data)

        elif ID == "SR":
            self.currentRPM = data
            self.currentRPMVal.config(text=data)

        elif ID == "PR":
            self.currentpH = data
            self.currentpHVal.config(text=data)



    def writeData(self, ID, data):
        if ID == "HW":
            setpoint = self.heatingSetpoint

        elif ID == "SW":
            setpoint = self.stirringSetpoint

        elif ID == "PW":
            setpoint = self.pHSetpoint
        
        
        with serial.Serial("/tmp/simavr-uart0", 9600) as ser:
            bytes = f"{ID}{data}".encode()
            
            ser.write(bytes)


    def readData(self):
        bytes = self.ser.readline() # read until a new line
        
        try:
            decoded = bytes.decode().strip()  # decode n return
            # Ignore initial print statement from arduino
            if decoded[0] == "H":
                # Get data for each subsystem
                subsystem_data = decoded.split(";")
                
                H_data = subsystem_data[0][2:]
                S_data = int(float(subsystem_data[1][2:]))
                P_data = subsystem_data[2][2:]
                
                
                self.cumulative_sum.append(self.cumulative_sum[self.counter-1] + S_data)
                if self.counter>=self.move:
	                RPM_avg = str(int((self.cumulative_sum[self.counter] - self.cumulative_sum[self.counter-self.move])/self.move))
                else:
    	            RPM_avg = str(S_data)
    	            
                self.counter += 1
                
                self.updateCurrentValues("HR", H_data)
                self.updateCurrentValues("SR", RPM_avg)
                self.updateCurrentValues("PR", P_data)
                

                log_data = f"Temp:{H_data} RPM:{RPM_avg} pH:{P_data} Time:{self.runTimeString}"
                log_data_for_file = f"{H_data},{RPM_avg},{P_data},{self.runTimeString}"
                self.add_log(log_data)
                # Add to text file as well
                with open(self.data_log_file, "a") as f:
                    f.write(log_data_for_file + "\n")
                    
        except Exception as e:
            print(e)


    def bioreactorLoop(self):
        # Update time on display
        self.runTimeCurrent = datetime.datetime.now()
        self.runTime = self.runTimeCurrent - self.runTimeStart
        self.runTimeString = str(self.runTime).split(".")[0] # Removes microseconds
        self.currentTimeVal.config(text=self.runTimeString)
        
        display_every = 1 # number of seconds to wait before displaying
        if int(self.runTimeString[5:]) % display_every == 0:
            self.readData()

        self.after(100, self.bioreactorLoop)  # Run function every 0.5 seconds
        

app = BioreactorUI()

app.mainloop()
