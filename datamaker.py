from htmlparse import *
from datetime import datetime
import time
import re

'''
This module makes a bunch of files with data pertaining to stocks of interest.
'''

#create a watchlist of stocks and track their progress over a period of time.
#returns symbol list.
'''
watchlist format:
			stockname1	stockname2	... 	stockname n
datetime1	val11		val21		... 	val n1
datetime2	val12		val22		... 	val n2
for m rows
'''
def watchlist(outname,symbols,period):
	#parse watchlist
	f = fopen(outname)

	#get new symbols to append to watchlist
	#update watchlist, but only ones that haven't expired
	print "watchlist"

#dump data for specific stocks into a lcal directory at a given frequency
'''
datadump(output directory, stock symbols (list of), frequency (how many per day))
day in frequency refers to stock trading time in PST (should make more flexible later) M-F 6am-1pm.
'''
#append data to data/symbol.dump
def datadump(outdir, symbols, frequency):
	while(True):
		t = datetime.now()
		hr = t.hour
		wkday = t.isoweekday #1 for mon, 7 for sun
		if (hr>=5 and hr<=13 and wkday<=5 and wkday>=1):
			symtable = parseSymbols(symbols)
			for sym in symtable:
				print "writing to:\t" + outdir+"/"+sym+".dump"
				f = open(outdir+"/"+sym+".dump",'a')
				f.write(str(t)[0:-7]+"\t")
				for symkey in symtable[sym]:
					#encoding to utf-8 allows me to actually pipe the data to files. 
					#Good for debuggin too.
					key = symkey.encode('utf-8')
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
	datadump("data",gSymbol,1000)
	watchlist("watchlist/watchlist_gainers.txt",gSymbol,10)
	print datetime.time(datetime.now())
