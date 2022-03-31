# Author: Jim Cooper originally
# Edited by:  Nathaniel Fisher
# Purpose: This application serves as a nlp script that will take client's emails and
# prossess the emails to determine the organizations and the ammount of investments each will recieve
# Date: November 27, 2020
import spacy
import re
from re import sub

class client:
	def __init__(self):
		self.clientEmail = ""
		self.investments = {}

# formatting the string from the document and removing any troublesome characters
# will then return an array of strings based on the <<End>> portion of the text
def stringProcessing(textString):
	firstPassString = re.sub("â€™", "'", textString)
	return firstPassString.split("<<End>>")

# will attempt to convert the string of the 
def processCurrency(currencyString):
	# dictionary that will be used to determine if someone used a word version of a number
	# not elegant in the slightest but should get the job done for processing numbers
	numDictionary = {
		"zero": 0,
		"one": 1,
		"two": 2,
		"three": 3,
		"four": 4,
		"five": 5,
		"six": 6,
		"seven": 7,
		"eight": 8,
		"nine": 9,
		"ten": 10,
		"eleven": 11,
		"twelve": 12,
		"thirteen": 13,
		"fourteen": 14,
		"fifteen": 15,
		"sixteen": 16,
		"seventeen": 17,
		"eighteen": 18,
		"nineteen": 19,
		"twenty" : 20,
		"thirty": 30,
		"fourty": 40,
		"fifty": 50,
		"sixty": 60,
		"seventy": 70,
		"eighty": 80,
		"ninety": 90,
		"hundred": 100,
		"thousand": 1000,
		"million": 1000000,
		"billion": 1000000000
		}
	#if there is a space in the word then attempt different form of processing
	if " " in currencyString:
		currencyNum = 1.0
		stringArray = currencyString.split()
		# will no check to see if the string in the array is a number or the 
		for moneyString in stringArray:
			if moneyString in numDictionary:
				currencyNum *= numDictionary[moneyString]
			elif any(chr.isdigit() for chr in moneyString):
				currencyNum *= float(sub(r'[^\d.]', '', moneyString))
		return currencyNum
	# if there is no space then this will attempt to remove any currency modifcations of the money ammount and treat it as a float or Decimal
	else:
		return float(sub(r'[^\d.]', '', currencyString))


nlp = spacy.load('en')
#doc = nlp(u'Hi Dave, I’d like to invest $10,000 with Microsoft and another $15,000 with Amazon. Thanks, Tom.')
textdoc = open('emaillog.txt', 'r').read()
emails = stringProcessing(textdoc)

clientsList = []
# save spaCy data to a text file
f = open('demo.txt', mode='wt', encoding='utf-8')

for email in emails:
	# this check is being used in case thet the email line only has a newline character as it will cause problems.
	if email != "\n":
		doc = nlp(email)
		#beginning to build the client class here with assigning the client's name
		currentClient = client()
		for token in doc:
			if(token.like_email):
				currentClient.clientEmail = token.text

		currency = ""
		organization = ""
		#processing the strings for the organization here this is assuming the the organization will follow the
		#currency ammount will probably break if the organization exists befor the ammount for that organization
		for ents in doc.ents:
			if ents.label_ == "ORG":
				organization = ents.text
				currentClient.investments[organization] = currency
			elif ents.label_ == "MONEY":
				currency = processCurrency(ents.text)
		clientsList.append(currentClient)

#initializing variable in case it causes problems
totalTransaction = 0.0
#building strings to better represent the data in the console and texxt file
for clientLine in clientsList:
	clientInfo = clientLine.clientEmail + ": "
	isFirstInvesment = True
	investmentCount = 1
	for investmentKey in clientLine.investments:
		totalTransaction += clientLine.investments[investmentKey]
		#if the item is the first item then it will not add a comma at the start of the string
		if isFirstInvesment == True:
			clientInfo += '${:,.2f}'.format(clientLine.investments[investmentKey]) + " to " + investmentKey
			isFirstInvesment = False
			# if the item in the list is only item that exists then just write to the file here
			if investmentCount == len(clientLine.investments):
				f.write(clientInfo + "\n")
			investmentCount += 1
			
		elif investmentCount < len(clientLine.investments):
			clientInfo += ", " + '${:,.2f}'.format(clientLine.investments[investmentKey]) + " to " + investmentKey
			investmentCount += 1
		else:
			clientInfo += " and " + '${:,.2f}'.format(clientLine.investments[investmentKey]) + " to " + investmentKey + "\n"
			f.write(clientInfo)

finalLine = "\nTotal Requests: " + '${:,.2f}'.format(totalTransaction)
f.write(finalLine)
f.close()

# read spaCy data from a text file and display the text document contents into the console.
f = open('demo.txt', mode='r', encoding='utf-8')
for line in f:
	line = line.strip('\n')
	print(line)

f.close()