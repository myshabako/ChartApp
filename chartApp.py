#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 16:51:13 2018

@author: Thomas Atta-Fosu (attafosu@yahoo.com)
"""

from tkinter import StringVar, Label, Button, TOP, BOTH, Tk, ttk, filedialog, messagebox, N, W, E, S
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2TkAgg)

import chartAppPlots as po
import sys

class chartGui(object):
    def __init__(self,spreadsheet=None):
        self.data_path = spreadsheet
        self.root = Tk()
        self.root.title("Charts")
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.plotCommands = {1: 'createGraphs.plotConfidenceScores()', 2: 'createGraphs.plotCPIvCapacityUtil()',
                     3: 'createGraphs.plotCPIvsGDP()', 4: 'createGraphs.plotCPIvsNYFED()',
                     5: 'createGraphs.plotCPIvsPMI()', 6: 'createGraphs.plotHighYeild()',
                     7: 'createGraphs.plotLEI()', 8: 'createGraphs.plotPMItoRecession()'}        
        
        self.createFrame()
        self.getFileButton()
        self.createDropMenu()
        if self.data_path is not None:
            self.createGraphs = po.DoubleLineGraphs(self.data_path)
            self.initializeCanvas()
        
    def initializeCanvas(self):
        self.fig = eval('self.{}'.format(self.plotCommands[2]))
        self.createCanvas()
        
    def plotSelection(self,*args):
        self.plotTitle = self.plotNameVar.get()
        key = self.comboKeys[self.plotTitle]
        fig = eval('self.{}'.format(self.plotCommands[key]))
        self.updateCanvas(fig)
    
    def createFrame(self):
        self.frame = ttk.Frame(self.root, width=500, height=500)
        self.frame['padding'] = 4
        self.frame['borderwidth'] = 2
        self.frame.grid(column=2, row=1, sticky=(N,W,E,S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
    def getFileButton(self):
        self.pushbutton = Button(master=self.frame, text='Load Spreadsheet', command=self.loadFile)
        self.pushbutton.grid(row=1, column=4, sticky=E)
        self.pushbutton.configure(font=('times', 20, 'bold'))
        self.pushbutton.pack()
        
        
    def loadFile(self):
        self.data_path = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("excel files","*.xlsx"),("all files","*.*")))
        
        if not isinstance(self.data_path, str):
            self.loadfileFail()
            return
        
        self.createGraphs = po.DoubleLineGraphs(self.data_path)
        self.initializeCanvas()
        
    def loadfileFail(self):
        messagebox.showwarning("Warning","No File Selected")

    def createDropMenu(self):
        # Indicate 
        self.dropMenuLabel = Label(self.frame, text="Select Chart")
#        self.dropMenuLabel.grid(column=1, row=1, sticky=E)
        self.labelfont = ('times',15,'bold')
        self.dropMenuLabel.config(font=self.labelfont)
        self.dropMenuLabel.pack()
    
    #%%
        self.plotNameVar = StringVar()
        self.plotNames = ttk.Combobox(self.frame, textvariable=self.plotNameVar)
#        self.plotNames.grid(column=2,row=1, sticky=E)
        self.plotNames.state = 'readonly'
        self.plotNames.config(font=('times',15,'bold'))
        self.plotNames.pack()
        
        if self.data_path is not None:
            self.plotNameVar.set("Confidence Scores")
            
        self.plotNames['values'] = ('Confidence Scores', 'Core CPI vs Cap. Util', 'Core CPI vs GDP',
                 'Core CPI vs Underlying Inflation', 'Core CPI vs ISM-PMI', 'High Yeild trajector',
                 'Leading Economic Indicator Trajectories', 'ISM-PMI trajectory')
        self.comboKeys = dict(zip(self.plotNames['values'], range(1,9)))
        self.plotNames.bind('<<ComboboxSelected>>', self.plotSelection)
        self.plotNames.focus()
        
    def createCanvas(self):
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        
    def updateCanvas(self, fig):
        self.canvas.figure = fig
        self.canvas.draw()
        
    def runGui(self):
        Button(self.root, text="Quit", command=self.on_closing)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            sys.exit(1)
        
if __name__ == '__main__':
    gui = chartGui()
    gui.runGui()
