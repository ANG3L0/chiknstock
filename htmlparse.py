from bs4 import BeautifulSoup
import urllib2
import time

'''
This module parses symbols for yahoo stocks.
'''


'''
Return values of printGainers/Losers/parseSymbols ought to be useful for users.

These are mostly private and useless to users:
	readTable(page) can only read the two URLs /gainers?e=us and /losers?e=us
	printGainers() prints the gainer page and returns a bunch of info on it 
	printLoser() prints the loser page and returns a bunch of info on it 
	parseSymbols(symbol list) will return a bunch of data from yahoo stocks given a symbol list.
'''
def parseSymbols(symbols):
	#symbolDict stores symbol -> attributes
	symbolDict = {}
	for symbol in symbols:
		#attrDict stores attribute -> value
		attrDict = {}
		url = urllib2.urlopen("http://finance.yahoo.com/q?s="+symbol)
		soup = BeautifulSoup(url)

		#parse the first table
		print symbol
		table1 = None
		while (table1==None):
			table1 = soup.find(lambda tag: tag.name=='table' and tag.has_key('id') and tag['id']=="table1")
			if (table1==None):
				url = urllib2.urlopen("http://finance.yahoo.com/q?s="+symbol)
				soup = BeautifulSoup(url)
				print "retrying..."
				time.sleep(1) #retry query after one second.

		names = table1.findAll(lambda tag: tag.name=='th' and tag.has_key('scope') and tag['scope']=="row")
		data = table1.findAll(lambda tag: tag.name=='td' and tag.has_key('class'))
		for i in range(len(names)):
			name1Content = names[i].contents[0]
			data1Content = data[i].contents[0]
			if ("Tag" in str(type(data1Content))):
				attrDict[name1Content] = data1Content.contents[0]
			else:
				attrDict[name1Content] = data1Content

		#parse the other table
		table2 = None
		while(table2==None):
			table2 = soup.find(lambda tag: tag.name=='table' and tag.has_key('id') and tag['id']=="table2")
			if (table2==None):
				url = urllib2.urlopen("http://finance.yahoo.com/q?s="+symbol)
				soup = BeautifulSoup(url)
				print "retrying..."
				time.sleep(1)

		names = table2.findAll(lambda tag: tag.name=='th' and tag.has_key('scope') and tag['scope']=="row")
		data = table2.findAll(lambda tag: tag.name=='td' and tag.has_key('class'))
		for i in range(len(names)):
			namestr=''
			datastr=''
			for el in names[i].contents:
				if ("NavigableString" in str(type(el))):
					namestr += ''.join(el).encode('utf-8')
				else:
					namestr += ''.join(el.contents[0]).encode('utf-8')
			for datum in data[i].contents:
				if ("NavigableString" in str(type(datum))):
					datastr += ''.join(datum).encode('utf-8')
				else:
					datastr += ''.join(datum.contents[0]).encode('utf-8')
			# print namestr + "   " + datastr
			attrDict[namestr] = datastr
		symbolDict[symbol] = attrDict
	# print symbolDict
	return symbolDict

def readTable(page):
	soup = BeautifulSoup(page)
	table = soup.find(lambda tag: tag.name=='div' and tag.has_key('id') and tag['id']=="yfitp")
	rows = table.findAll(lambda tag: tag.name=='tr')
	symbol = []
	name = []
	last_trade = []
	change = []
	percentChange = []
	vol = []
	x = soup.prettify()
	#print x.encode('utf-8')
	for row in rows:
		cols = row.findAll(lambda tag: tag.name=='td')
		for col in cols:
			if (col.has_key('class')):
				classname = col['class'][0]
				# print classname
				if (classname=="first"):
					if (col.contents!=[]):
						symbol.append(col.contents[0].contents[0].contents[0])
				elif (classname=="second"):
					if (col.contents!=[]):
						name.append(col.contents[0])
					else:
						name.append(" ")
				elif (classname=="last_trade"):
					if (col.contents!=[]):
						last_trade.append(col.b.span.contents[0])
			else:
				spanners = col.findChildren('span')
				if (spanners!=[]):
					percent = spanners[-1].b
					tempContent = col.span.b
					if ("v00" in spanners[0]['id']):
						vol.append(spanners[0].contents[0])
					if (percent!=None):
						#green is usually + and red is usually - 
						if (percent['style']=="color:#008800;"):
							percentChange.append("+" + percent.contents[0][1:])
						elif(percent['style']=="color:#cc0000;"):
							percentChange.append("-" + percent.contents[0][1:])
						else:
							percentChange.append(percent.contents[0][1:])
					if (tempContent!=None):
						
						#green is usually + and red is usually - 
						if (tempContent['style']=="color:#008800;"):
							change.append("+" + tempContent.contents[0])
						elif(tempContent['style']=="color:#cc0000;"):
							change.append("-" + tempContent.contents[0])
						else:
							change.append(tempContent.contents[0]+"\t") #no change
	
	print "Sym\tVal\tChange\t%change \tVolume"
	print "-"*50
	for i in range(len(symbol)):
		print symbol[i] + "\t" + last_trade[i] + "\t" + change[i] + "   " + percentChange[i] + "\t" + vol[i]
	print
	print

	return symbol, last_trade, change, percentChange, vol

def printGainers():
	url =  urllib2.urlopen("http://finance.yahoo.com/gainers?e=us").read()
	print "GAINERS"
	gSymbol, gLast, gChange, gpChange, gVol = readTable(url)
	return gSymbol, gLast, gChange, gpChange, gVol 

def printLosers():
	url =  urllib2.urlopen("http://finance.yahoo.com/losers?e=us").read()
	print "LOSERS"
	lSymbol, lLast, lChange, lpChange, lVol = readTable(url)
	return lSymbol, lLast, lChange, lpChange, lVol


if __name__ == '__main__':
	gSymbol, gLast, gChange, gpChange, gVol = printGainers()
	lSymbol, lLast, lChange, lpChange, lVol = printLosers()
	#parseSymbols must have input as a list, so
	#parseSymbols(["APPL"]) is valid but
	#parseSymbols("APPL") will look at stocks A, P, P again, and L
	parseSymbols(lSymbol)