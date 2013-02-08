from htmlparse import *
from datetime import datetime
from datetime import date
import time
import re
import codecs
import urllib
import sys
import os

'''
This module makes a bunch of files with data pertaining to stocks of interest.
'''

#create a watchlist of stocks and track their progress over a period of time.
#returns symbol list.
'''
watchlist format:
stockname1: val1@day1 val2@day2
stockname2: ""
...
stockanme n: ""
'''
def cast2str(syms):
	for i in range(len(syms)):
		syms[i] = str(syms[i])
	return syms

def getYahooStockPics(sym,t,direct):
	urllib.urlretrieve("http://chart.finance.yahoo.com/t?s=" + sym + "&lang=en-US&region=US&width=600&height=360",direct+"/"+sym+"_"+t+".jpg")

def watchlist(outname,symbols,period):
	#### parse watchlist ####
	try:
		f = open(outname,'ra+') #actually read only but a creates new file if it doesn't exist
	except IOError, e:
		f = open(outname,'w+')
	stockinfo = {}
	updatestock = {}
	today = date.today()
	while (True):
		line = f.readline()
		if (line==''):
			break
		#grab info
		stockname = re.findall('\w+',line)
		stockname = stockname[0]
		price = re.findall('([0-9]+\.[0-9]+) @',line)
		startDate = re.findall('@ ([0-9]+-[0-9]+-[0-9]+)',line)
		startDate = startDate[0]
		startDate = datetime.strptime(startDate,'%Y-%m-%d').date()

		#update stockinfo/updatestock dictionaries.
		stockinfo[stockname] = line
		if ((today - startDate).days > period):
			updatestock[stockname]=False
		else:
			updatestock[stockname]=True
	f.close()

	f = open(outname,'w')
	symlist = []
	#### get aggregrate symbols (both old stock symbols and all the new ones) ####
	symbols = cast2str(symbols)
	if (stockinfo.keys()!=[]):
		symlist = set(symbols + stockinfo.keys())
	else:
		symlist = set(symbols)
	allsyms = parseSymbols(symlist)

	#### update watchlist, but only ones that haven't expired yet ####
	for sym in allsyms:
		if sym not in stockinfo:
			f.write(sym+":\t" + allsyms[sym]["Curr Price:"] + " @ " + today.isoformat() + "\n")
		else:
			if (updatestock[sym]):
				f.write(stockinfo[sym][0:-1] + "\t" + allsyms[sym]["Curr Price:"] + " @ " + today.isoformat() +"\n")
			else:
				f.write(stockinfo[sym])
	f.close()
	##### make directories for pics and fill them w/ pics ####
	for stock in updatestock:
		if updatestock[stock]:
			direct = "watchlist/" + stock
			if not os.path.exists(direct):
				os.makedirs(direct)
				getYahooStockPics(stock,today.isoformat(),direct)

#dump data for specific stocks into a lcal directory at a given frequency
'''
datadump(output directory, stock symbols (list of), frequency (how many per day))
day in frequency refers to stock trading time in PST (should make more flexible later) M-F 6am-1pm.
'''
#append data to data/symbol.dump
def datadump(outdir, symbols, frequency):
	reload(sys);
	sys.setdefaultencoding("utf8")
	while(True):
		t = datetime.now()
		hr = t.hour
		wkday = t.isoweekday() #1 for mon, 7 for sun
		if (hr>=6 and hr<13 and wkday<=5 and wkday>=1):
			symtable = parseSymbols(symbols)
			for sym in symtable:
				print "writing to:\t" + outdir+"/"+sym+".dump"
				f = open(outdir+"/"+sym+".dump",'a')
				f.write(str(t)[0:-7]+"\t")
				for symkey in symtable[sym]:
					#encoding to utf-8 allows me to actually pipe the data to files. 
					#Good for debuggin too.
					# key = unicode(symkey.strip(codecs.BOM_UTF8), 'utf-8')
					# key = symkey.encode('utf8')
					key = symkey
					val = symtable[sym][symkey].encode('utf-8')
					f.write(key+" "+val+"\t")
				f.write("\n\n")
				f.close()
		else:
			print "Stock market closed"
			return
		print "sleep time is approx: " + str(7*3600/frequency) + " seconds."			
		time.sleep(7*3600/frequency)


#TODO: some other module to analyse the data.

if __name__ == '__main__':
	gSymbol, gLast, gChange, gpChange, gVol = printGainers()
	# datadump("data",gSymbol,1000)
	#do watchlist updates on non-stock hours
	t = datetime.now()
	hr = t.hour
	wkday = t.isoweekday()
	if (hr<5 or hr>=13 or wkday>5 or wkday<1):
		watchlist("watchlist/watchlist_gainers.txt",gSymbol,10)
