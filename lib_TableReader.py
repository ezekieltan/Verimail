import pandas as pd
import os
class TableReader:
    TAG = 'TableReader: '
    def __init__(self, name, autoDate = False):
        self.__name = os.path.basename(name)
        self.__fullname = name
        self.__dfs = {}
        self.__properties = {}
        self.__isdir = os.path.isdir(self.__fullname)
        self.__read__(autoDate = autoDate)
    def __read__(self, autoDate):
        print(self.TAG, 'reading: ', self.__fullname)
        if (self.__isdir):
            for filename in os.listdir(self.__fullname):
                csvName = os.path.splitext(os.path.basename(filename))[0]
                self.__dfs[csvName] = pd.read_csv(os.path.join(self.__fullname, filename), parse_dates=autoDate)
                if(autoDate):
                    self.__dfs[csvName] = self.csvAutoDate(self.__dfs[csvName])
                #print(self.TAG, 'loaded: ', csvName)
                #print(self.__dfs[csvName])
        elif (self.__name.endswith('.xlsx') or self.__name.endswith('.xls')):
            xl = pd.read_excel(self.__fullname,None, engine = 'openpyxl')
            print(xl)
            self.__dfs = xl
            #self.__dfs = xl
            #print(self.TAG, 'loaded: ', sheetName)
            #print(self.__dfs[sheetName])
        elif (self.__name.endswith('.csv')):
            self.__dfs[self.__name] = pd.read_csv(self.__fullname, parse_dates=autoDate)
            if(autoDate):
                self.__dfs[self.__name] = self.csvAutoDate(self.__dfs[self.__name])
            #print(self.TAG, 'loaded: ', self.__name)                
        print(self.TAG, 'loaded')
    def csvAutoDate(self,df):
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                except (ValueError, TypeError):
                    pass
        return df
    def getProperty(self, propertyName):
        return self.__properties[propertyName]
    def setProperty(self, propertyName, propertyValue):
        self.__properties[propertyName] = propertyValue
        print(self.TAG, 'set: ', ': ', propertyName)
    def getDf(self, dfName = None):
        if(len(self.__dfs) == 0):
            return None
        if(dfName == None):
            dfName = self.getDfNames()[0]
        return self.__dfs[dfName]
    def transpose(self, dfName = None):
        if(len(self.__dfs) == 0):
            return None
        if(dfName == None):
            dfName = self.getDfNames()[0]
        self.__dfs[dfName].transpose()
    def getDfNames(self):
        return list(self.__dfs.keys())