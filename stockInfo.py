from alpha_vantage.timeseries import TimeSeries
import ConfigLoader
import csv
import time, datetime
import os
import sys

system = sys.platform
if system == 'win32':
    import msvcrt
elif system == 'linux':
    import linuxvcrt


class stockInfo:

    def __init__(self):
        config = ConfigLoader.configImport("config")
        self.AlphaVantageAccounts = config.getAccountsByAPI("AlphaVantage")
        self.AlphaVantageKey = config.getAPIKey("AlphaVantage")
        self.numKeys = len(self.AlphaVantageKey)
        self.DailyUsage = {val: 0 for val in range(self.numKeys)}
        self.MinuteUsage = {val: 0 for val in range(self.numKeys)}
        self.Time = {val: 0 for val in range(self.numKeys)}
        self.quit = False
        self.acctIndex = 0

        self.loadDailyUsage()

    def loadDailyUsage(self):
        if not os.path.isfile('./tempFiles/dailyUsage.txt'):
            return False

        with open('./tempFiles/dailyUsage.txt', 'r') as myFile:
            date = myFile.readline()
            try:
                date = datetime.datetime.strptime(date.strip(), '%Y-%m-%d %H:%M:%S.%f')
            except:
                return False

            if (datetime.datetime.now() - date).days > 0:
                return False
            else:
                for line in myFile:
                    vals = line.strip().split(" ")
                    api, key, n = vals
                    self.DailyUsage[self.AlphaVantageKey.index(key)] = int(n)

    def get_historical_data(self, symbol: str, key: str, path: str = ""):
        ts = TimeSeries(key=key, output_format='csv')
        data = None
        metadata = None
        try:
            data, metadata = ts.get_daily(symbol=symbol, outputsize='full')
            self.MinuteUsage[self.AlphaVantageKey.index(key)] += 1
            self.DailyUsage[self.AlphaVantageKey.index(key)] += 1
        except Exception as e:
            print("could not get Historical data")
            print("Exception is: %s"%(e))
            #print("API calls per minute:")
            #for i in range(self.numKeys):
            #    print("%d : %s" % (i, self.MinuteUsage[i]))
            print("API calls per day:")
            for i in range(self.numKeys):
                print("%d : %s" % (i, self.DailyUsage[i]))
            return False

        iterable = []
        for row in data:
            iterable.append(row)

        if len(iterable) <= 3:
            print("used token but exceeded limits")
            print(iterable)
            return False

        try:
            path += "daily_" + symbol + ".csv"
            print(path)
            myFile = open(path, 'w', newline='')
            with myFile:
                writer = csv.writer(myFile)
                writer.writerows(iterable)
        except:
            print("could not write to file")
            return False

        return True

    def nonThreadedKillSwitch(self):
        machine = system[:3]
        if machine == 'win':
            if msvcrt.kbhit():
                ch = ord(msvcrt.getch())
                if ch == 27:
                    self.quit = True
        elif machine == 'lin':

            if linuxvcrt.kbhit():
                ch = ord(linuxvcrt.getch())
                if ch == 27:
                    print("Stoping Program...")
                    self.quit = True

    def get_all_historical_data(self, stockSymbolsFile: str, path: str = ""):
        failed = []
        success = []
        index = 0
        stockSymbols = []

        with open(stockSymbolsFile, 'r') as myFile:
            for line in myFile:
                symbol = line.strip()
                stockSymbols.append(symbol)

        for symbol in stockSymbols:
            self.nonThreadedKillSwitch()
            if self.quit:
                break

            key = self.selectKey()
            if (not key):
                print("You do not have any API calls left for today")
                break
            else:
                idx = self.AlphaVantageKey.index(key)
                if self.Time[idx] == 0:
                    self.Time[idx] = time.time()

                if self.get_historical_data(symbol, key, path):
                    index += 1
                    success.append(symbol)
                    # stockSymbols.remove(symbol)
                else:
                    print(symbol + " failed to get data")
                    failed.append(symbol)
            time.sleep(6)
        # remove successfuly created stocks
        for s in success:
            stockSymbols.remove(s)

        print(index)  # print number of calls
        print("success List: %s"%(success))  # print success list
        print("failed List : %s"%(failed))  # print failed list
        with open("./tempFiles/remainingSymbols.txt", 'w') as myFile:
            for symbol in stockSymbols:
                myFile.write(symbol + "\n")

        with open("failedStocks","a")as tempFile:
            for element in failed:
                tempFile.write(element + "\n")

        with open("dailyUsage.txt", 'w') as myFile:
            myFile.write(str(datetime.datetime.now()) + "\n")
            for acct in self.AlphaVantageAccounts:
                myFile.write(str(acct.API) + " " + str(acct.key) + " " + str(
                    self.DailyUsage[self.AlphaVantageKey.index(acct.key)]) + "\n")

    def selectKey(self):
        for index, account in enumerate(self.AlphaVantageAccounts):
            if self.DailyUsage[index] >= int(account.limits["daily"]):
                rmvKey = account.key
                self.AlphaVantageAccounts.remove(account)
                self.AlphaVantageKey.remove(rmvKey)
                self.numKeys = len(self.AlphaVantageKey)
                self.acctIndex = (index+1)%self.numKeys

        if self.numKeys < 1:
            return None

        key = self.AlphaVantageKey[self.acctIndex]
        self.acctIndex  = (self.acctIndex +1)%self.numKeys
        delay = (60/self.numKeys)/int(self.AlphaVantageAccounts[self.acctIndex].limits["minute"])
        time.sleep(delay+3)
        #print ("The key being used is: %s"%(key))
        return key


def main():
    si = stockInfo()
    si.get_all_historical_data("./tempFiles/remainingSymbols.txt", path="./historical_stock_data/")
    # si.testingStop()
    # si.updateList()


main()
