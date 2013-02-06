from bs4 import BeautifulSoup
import urllib2

def parseSymbols(symbols):
	#symbolDict stores symbol -> attributes
	symbolDict = {}
	for symbol in symbols:
		#attrDict stores attribute -> value
		attrDict = {}
		url = urllib2.urlopen("http://finance.yahoo.com/q?s="+symbol)
		soup = BeautifulSoup(url)

		#parse the first table
		table1 = soup.find(lambda tag: tag.name=='table' and tag.has_key('id') and tag['id']=="table1")
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
		table2 = soup.find(lambda tag: tag.name=='table' and tag.has_key('id') and tag['id']=="table2")
		names = table2.findAll(lambda tag: tag.name=='th' and tag.has_key('scope') and tag['scope']=="row")
		data = table2.findAll(lambda tag: tag.name=='td' and tag.has_key('class'))
		for i in range(len(names)):
			name2Content = names[i].contents[0]
			data2Content = data[i].contents[0]
			if ("Tag" in str(type(data2Content))):
				if ("Tag" in str(type(data2Content.contents[0]))):
					attrDict[name2Content] = data2Content.contents[0].contents[0]
				else:
					attrDict[name2Content] = data2Content.contents[0]
			else:
				attrDict [name2Content] = data[i].contents[0]
		symbolDict[symbol] = attrDict
	print symbolDict
	return symbolDict


'''
Return values of printGainers/Losers/parseSymbols ought to be useful for users.

These are mostly private and useless to users:
	readTable(page) can only read the two URLs /gainers?e=us and /losers?e=us
	printGainers() prints the gainer page and returns a bunch of info on it 
	printLoser() prints the loser page and returns a bunch of info on it 
	parseSymbols(symbol list) will return a bunch of data from yahoo stocks given a symbol list.
'''

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
	for row in rows:
		cols = row.findAll(lambda tag: tag.name=='td')
		for col in cols:
			if (col.has_key('class')):
				classname = col['class'][0]
				# print classname
				if (classname=="first"):
					symbol.append(col.contents[0].contents[0].contents[0])
				elif (classname=="second"):
					name.append(col.contents[0])
				elif (classname=="last_trade"):
					last_trade.append(col.b.span.contents[0])
			else:
				spanners = col.findChildren('span')
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
				if (tempContent!=None):
					
					#green is usually + and red is usually - 
					if (tempContent['style']=="color:#008800;"):
						change.append("+" + tempContent.contents[0])
					elif(tempContent['style']=="color:#cc0000;"):
						change.append("-" + tempContent.contents[0])
	
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

gSymbol, gLast, gChange, gpChange, gVol = printGainers()
lSymbol, lLast, lChange, lpChange, lVol = printLosers()
#parseSymbols must have input as a list, so
#parseSymbols(["APPL"]) is valid but
#parseSymbols("APPL") will look at stocks A, P, P again, and L
parseSymbols(lSymbol)