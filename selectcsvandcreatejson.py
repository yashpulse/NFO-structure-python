import os
import csv
import time
import datetime
import calendar
import json
import math
import os


dir_name = '.'
extension = ".csv"


def writefile(res, keycount):

    keycount = keycount
    res = res
    res2 = json.loads(res)   
    expire = res2["expiry"]
    expdt = expire.split("-")
    filenametowrite = res2["today"] + res2["inst"] + res2["sym"] + expdt[2] + expdt[1] + str(keycount) + ".txt"
    print(filenametowrite)
    fw = open(filenametowrite, "a")
    fw.write(res)
    fw.close()


def createJSON(a, uniqexp, keycount):
    x = []
    y = []
    fut = []
    opt = []
    tocpy = []
    uniqexp = uniqexp
    keycount = keycount
    for row in a:
        if row["INSTRUMENT"] == "FUTIDX" or row["INSTRUMENT"] == "FUTSTK":
            x.append(row)
        elif row["EXPIRY_DT"] == uniqexp:
            y.append(row)

    today1 = x[0]["TIMESTAMP"]
    today = today1.upper()
    expiry1 = y[0]["EXPIRY_DT"]
    expiry = expiry1.upper()
    isExpiry = (today == expiry)
    date = datetime.datetime.strptime(today1, "%d-%b-%Y")
    dayofwk = calendar.day_name[date.weekday()]
    instrument = y[0]["INSTRUMENT"][-3:]
    symbol = y[0]["SYMBOL"]
    for row in x:
        fut.append({
            "futExpiry": row["EXPIRY_DT"],
            "open": row["OPEN"],
            "high": row["HIGH"],
            "low": row["LOW"],
            "close": row["CLOSE"],
            "settlePr": row["SETTLE_PR"]
        })

    ceopt = []
    peopt = []
    for row in y:
        if row["OPTION_TYP"] == "CE" or row["OPTION_TYP"] == "CA":
            ceopt.append({
            "strikePrice": row["STRIKE_PR"],
            "open": row["OPEN"],
            "high": row["HIGH"],
            "low": row["LOW"],
            "close": row["CLOSE"],
            "settlePr": row["SETTLE_PR"]
            })
        elif row["OPTION_TYP"] == "PE" or row["OPTION_TYP"] == "PA":
            peopt.append({
            "strikePrice": row["STRIKE_PR"],
            "open": row["OPEN"],
            "high": row["HIGH"],
            "low": row["LOW"],
            "close": row["CLOSE"],
            "settlePr": row["SETTLE_PR"]
            })
    
    optcpy = []

    strikeDiff = float(ceopt[5]["strikePrice"])-float(ceopt[4]["strikePrice"])
    atmc = float((math.ceil(float(fut[0]["open"]) / strikeDiff)) * strikeDiff)
    atmf = float((math.floor(float(fut[0]["open"]) / strikeDiff)) * strikeDiff)

    optcpy.append({
        "CE": ceopt,
        "PE": peopt
    })  
    optstr = json.dumps(optcpy)
    optstrrem = (optstr[:-1])[1:]  
    opt = json.loads(optstrrem)
    

    tocpy.append({
        "today": today,
        "expiry": expiry,
        "isExpiry": isExpiry,
        "dayofwk": dayofwk,
        "inst": instrument,
        "sym": symbol,
        "atmc": atmc,
        "atmf": atmf,
        "fut": fut,
        "opt":opt

    })
    resstr = json.dumps(tocpy)
    res = (resstr[:-1])[1:]
    writefile(res, keycount)

     
    



def selectid(uniqexp, sym, a, toINST, keycount):
    y = []
    uniqexp = uniqexp
    toINST = toINST
    sym = sym
    keycount = keycount
    hjs = []
    for row in a:
        if row["INSTRUMENT"] == "FUTIDX" or row["INSTRUMENT"] == "FUTSTK":
            y.append(row)
        elif row["EXPIRY_DT"] == uniqexp:
            y.append(row)
            hjs.append(row["INSTRUMENT"])

    lenofjs = len(hjs)
    if lenofjs != 0:
        createJSON(y, uniqexp, keycount)





def selectexpiry(toINST, sym, csv_reader):
    y = []
    a = []
    toINST = toINST
    sym = sym
    for row in csv_reader:
        if row["SYMBOL"] == sym:
            y.append(row)
            a.append(row["EXPIRY_DT"])
    
    uniqEXP = list(dict.fromkeys(a))
    dates = [datetime.datetime.strptime(ts, "%d-%b-%Y") for ts in uniqEXP]
    dates.sort()
    sorteddates = [datetime.datetime.strftime(ts, "%d-%b-%Y") for ts in dates]
    key = list(map(lambda x: str(x.rsplit('-',2)[1]), sorteddates)) 
    i = 0
    keycount = 0
    while i < len(sorteddates):
        uniqexp = sorteddates[i]
        if i >= 0:
            if key[i] == key[i-1]:
                keycount += 1
            else:
                keycount = 1
        i += 1

        selectid(uniqexp, sym, y, toINST, keycount)

 


def selectsymbol(toINST, csv_reader):
    y = []
    z = []
    hj = []
    toINST = toINST
    for row in csv_reader:
        z.append(row)
        y.append(row["SYMBOL"])
        hj.append(row["INSTRUMENT"])
    UNIQSYM = list(dict.fromkeys(y))

    for sym in UNIQSYM:      
        if toINST == "OPTIDX":            
            selectexpiry(toINST, sym, z)
        elif toINST == "OPTSTK":
            selectexpiry(toINST, sym, z)
        
        
  


def selecttype(csv_reader):
    z = []
    x = []
    fkey = []
    for row in csv_reader:
        if row["INSTRUMENT"] == "OPTIDX" or row["INSTRUMENT"] == "FUTIDX":
            z.append(row)
            fkey.append(row["INSTRUMENT"])
        elif row["INSTRUMENT"] == "OPTSTK" or row["INSTRUMENT"] == "FUTSTK":
            x.append(row)
            fkey.append(row["INSTRUMENT"])

    UNIQINST = list(dict.fromkeys(fkey))
    for inst in UNIQINST:  
        if inst == "OPTIDX":
            toINST = inst
            selectsymbol(toINST, z)
        elif inst == "OPTSTK":
            toINST = inst
            selectsymbol(toINST, x)


def selectcsv(file_name):
    f = open(file_name)
    csv_reader = csv.DictReader(f)
    selecttype(csv_reader)
    f.close()

for item in os.listdir(dir_name): # loop through items in dir
    if item.endswith(extension): # check for ".zip" extension
        file_name = os.path.abspath(item)
        print(file_name)
        selectcsv(file_name)
        os.remove(file_name)      
