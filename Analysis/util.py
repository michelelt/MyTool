import pandas as pd
import datetime
import matplotlib.pyplot as plt

class Utility (object):
    
    def __init__ (self):
        return
        
        
    def get_color(self, df):
        provider = self.get_provider(df)
        if provider == "enjoy" :
            return "red"
        else:
            return "blue"
        
    def get_provider(self, df):
        return df.iloc[0].vendor
    
    #return a df with the valid date with entries and #parkings/#bookings
    def get_valid_days(self,df,start,end):
        year = start.year
        month = start.month
        day = start.day
        
        delta = end -start
        
        df = pd.DataFrame(df['init_date'])
        df['date'] = df.init_date.apply(lambda x : x.date())
        df = df.groupby('date').count()
        
        datelist = pd.date_range(pd.datetime(year,month,day), periods=delta.days).tolist()
        dfdays = pd.DataFrame(datelist)
        dfdays['count'] = [0]*len(datelist)
        dfdays.set_index(0, inplace=True)
        df2= dfdays['count'] +  df['init_date']
        df2 = pd.DataFrame(df2)
        df2.fillna(0, inplace=True)
        df2 = df2.rename(columns={0:'entries'})

        return df2
            


