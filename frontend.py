import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

import pandas as pd
import xlsxwriter

import threading
import time
import requests

from lib_TableReader import TableReader
import verimail

__title = "Verimail"

inputFileTypes = [('Valid files', ['*.xlsx', '*.csv']),]
saveAsFileTypes = [('XLSX', ['*.XLSX']),('CSV', ['*.csv']),]

currentTable = None
thread = None
def listToListBox(l, listBox):
    listBox.delete(0, tk.END)
    for i in range(len(l)):
        listBox.insert(i+1, l[i])
        
def uploadAction(event=None):
    global currentTable
    filename = filedialog.askopenfilename(filetypes = inputFileTypes)
    if(filename==''):
        return
    filenameText.set(filename)
    currentTable = TableReader(filename)
    print(currentTable.getDf())
    listToListBox(list(currentTable.getDfNames()), tableSelectorListBox)
    listToListBox([], columnSelectorListBox)
    
    
def tableSelectorListBoxSelectMethod(event=None):
    global currentTable
    value = tableSelectorListBox.get(tableSelectorListBox.curselection())
    listToListBox(currentTable.getDf(value).columns, columnSelectorListBox)

def GO(event=None):
    global thread
    tableIndex = tableSelectorListBox.curselection()
    columnIndex = columnSelectorListBox.curselection()
    if(len(columnIndex)<=0 or len(tableIndex)<=0):
        return
    outputPath = filedialog.asksaveasfilename(filetypes = saveAsFileTypes, initialfile = 'results.xlsx')
    if(outputPath==''):
        return
    
    columnName = columnSelectorListBox.get(columnIndex)
    tableName = tableSelectorListBox.get(tableIndex)
    emailList = list(currentTable.getDf(tableName)[columnName])
    thread = threading.Thread(target=reallyGO, args=((emailList, outputPath, progressBar)))
    thread.start()
    
    
def reallyGO(emailList, outputPath, percentageVar = None):
        print('in go')
        thread = threading.currentThread()
        count = 0
        total = len(emailList)
        result = {}
        print(emailList)
        for email in emailList:
            if not getattr(thread, "do_run", True):
                messagebox.showinfo(title="Stopped", message="Stopped")
                statusText.set("Stopped")
                return
            result[email] = verimail.check(email)
            if(percentageVar is not None):
                count = count + 1
                print(count)
                print(email)
                print(result[email])
                print("")
                percentageVar['value'] = 100*count/total
            resultDf = pd.DataFrame.from_dict(result, orient='index')
            resultDf.index.name = 'email'
            while(True):
                try:
                    if(outputPath.endswith('.csv')):
                        resultDf.to_csv(outputPath)
                    else:
                        resultDf.to_excel(outputPath)
                    break
                except (PermissionError, xlsxwriter.exceptions.FileCreateError):
                    messagebox.showerror(title="Close file", message="Please close output file to continue")
        statusText.set("Saved to " + outputPath)    
        messagebox.showinfo(title="Done", message="Done")
            
        
def STOP(event=None):
    global thread
    if(thread is not None):
        thread.do_run = False

window = tk.Tk()
window.title(__title)
window.resizable(0,0)
window.minsize(600,250)




mainFrame = tk.Frame(window)
topRow = tk.Frame(mainFrame)
fileRow = tk.Frame(mainFrame)
selectorLabelRow = tk.Frame(mainFrame)
selectorRow = tk.Frame(mainFrame)
progressRow = tk.Frame(mainFrame)


filenameText = tk.StringVar()
filenameLabel = tk.Label(fileRow, textvariable=filenameText)
statusPreLabel = tk.Label(topRow, text="Status:")
statusText = tk.StringVar()
statusLabel = tk.Label(topRow, textvariable=statusText)
tableSelectorLabel = tk.Label(selectorLabelRow, text="2. Select Table")
tableSelectorListBox = tk.Listbox(selectorRow, exportselection=0)
tableSelectorListBox.bind('<<ListboxSelect>>',tableSelectorListBoxSelectMethod)
columnSelectorLabel = tk.Label(selectorLabelRow, text="3. Select Column")
columnSelectorListBox = tk.Listbox(selectorRow, exportselection=0)
openButton = tk.Button(fileRow, text='1. Open Source File', command=uploadAction)
goButton = tk.Button(progressRow, text='GO', command=GO)
stopButton = tk.Button(progressRow, text='STOP', command=STOP)
progressBar = ttk.Progressbar(progressRow, orient = tk.HORIZONTAL, length = 100, mode = 'determinate')

statusLabel.pack(side=tk.RIGHT)
statusPreLabel.pack(side=tk.RIGHT)
topRow.pack(fill='x', expand=tk.YES)

openButton.pack(side=tk.LEFT)
filenameLabel.pack(expand=tk.YES)
fileRow.pack(fill='x', expand=tk.YES)

tableSelectorLabel.pack(side=tk.LEFT, expand=tk.YES)
columnSelectorLabel.pack(side=tk.RIGHT, expand=tk.YES)
selectorLabelRow.pack(fill='x', expand=tk.YES)

tableSelectorListBox.pack(side=tk.LEFT, fill='x', expand=tk.YES)
columnSelectorListBox.pack(side=tk.RIGHT, fill='x', expand=tk.YES)
selectorRow.pack(fill='x', expand=tk.YES)

goButton.pack(side=tk.LEFT)
stopButton.pack(side=tk.LEFT)
progressBar.pack(side=tk.RIGHT, fill='x', expand=tk.YES)
progressRow.pack(fill='x', expand=tk.YES)

goButton.pack()
stopButton.pack()

mainFrame.pack(fill='x', expand=tk.YES)

window.mainloop()