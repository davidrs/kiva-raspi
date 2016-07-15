# debug flag turn on if running on Raspi
RASPI = True

import json
import urllib2
import datetime
import time

if RASPI:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)

# interval in seconds between polls
POLL_INTERVAL = 5 * 60

# Time LED is turned on in seconds.
LED_ON_TIME = 3

# country code to GPIO pin mapping
countryGpio = { 
    'Peru': 2,
    'Tajikistan': 3,
    'Kenya': 4,
    'Philippines': 14,
    'El Salvador': 18,
}

# start lastTime as now.
lastID = 0

# Setup all pins to output voltage ie be HIGH. 
# Also turn them all on for a second then off, good for testing LEDs.
def initializePins():
    if RASPI:
        for country in countryGpio:
            GPIO.setup(countryGpio[country], GPIO.OUT)
            GPIO.output(countryGpio[country],True)
	    time.sleep(1)
            GPIO.output(countryGpio[country], False)

def scrapeLatest():
    global lastID
    try:
        #req = urllib2.Request('http://api.kivaws.org/v1/lending_actions/recent.json')
	#resp = urllib2.urlopen(req).read()
        response = urllib2.urlopen('http://api.kivaws.org/v1/lending_actions/recent.json', None, 100)
	#print response
        recentLoans = json.load(response)
        recentLoans = recentLoans['lending_actions']
    except Exception as inst:
        print "Error on loan api call"
	print type(inst)
	print inst
        recentLoans = []

    # Error check
    if len(recentLoans) < 1:
        print "No new loans :("
        time.sleep(POLL_INTERVAL)
    else :
        print "Old lastId " + str(lastID)
        filteredLoans = filterLoans(recentLoans)
        if len(filteredLoans) > 0:
            lightUpLoans(filteredLoans)
            lastID = recentLoans[0]['id']
        else :
            time.sleep(POLL_INTERVAL)
        print "Set lastId " + str(lastID)
        
    # Start the cycle again
    scrapeLatest()
    
# iterate over loans, filtering out ones that don't apply.
def filterLoans(loanList):
    simpleList = []
    for action in loanList:
        if action['id'] <= lastID:
            print "break, found old id"
            break
        if lastID == 0 and len(simpleList) > 5:
            print "Got enough for first round."
            break
        if action['loan']['location']['country'] in countryGpio:
            print "in list! "+ action['loan']['location']['country'] + "  "+ action['date']
            simpleList.append({'country': action['loan']['location']['country'] , 
            'date': action['date']})
    
    return simpleList

# take a list of loans, and light each one up.
def lightUpLoans(simpleList):
    timePerLoan = POLL_INTERVAL / len(simpleList)
    print "timeperLoan: " + str(timePerLoan)
    
    # reverse list so it 'plays it forward in time'
    for loan in reversed(simpleList):
        print loan['country'] +"   "+loan['date']
        lightUpCountry(loan['country'])
        time.sleep(timePerLoan - LED_ON_TIME)
        

def lightUpCountry(country):
    print "gpio on "+  str(countryGpio[country])
    if RASPI:
        GPIO.output(countryGpio[country], True)
    
    time.sleep(LED_ON_TIME)
    
    print "gpio off "+  str(countryGpio[country])
    if RASPI:
        GPIO.output(countryGpio[country], False)

        
# start the app
initializePins()
scrapeLatest()


