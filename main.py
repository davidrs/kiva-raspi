# Debug flag set to True if running on Raspi else False
RASPI = True

import json
import urllib2
import datetime
import time

if RASPI:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)

# Tnterval in seconds between polls
POLL_INTERVAL = 1 * 60

# Max Time LED is turned on in seconds.
MAX_LED_ON_TIME = 3

# region Gpio pins
PIN_NORTH_AMERICA = 2
PIN_SOUTH_AMERICA = 3
PIN_AFRICA = 18
PIN_MIDDLE_EAST = 4
PIN_EAST_ASIA = 14

ALL_PINS = [PIN_NORTH_AMERICA, PIN_SOUTH_AMERICA, PIN_AFRICA, PIN_MIDDLE_EAST, PIN_EAST_ASIA]


# country code to region mapping
countryGpio = { 
    'Albania': PIN_MIDDLE_EAST,
    'Georgia': PIN_MIDDLE_EAST,
    'Iran': PIN_MIDDLE_EAST,
    'Jordan': PIN_MIDDLE_EAST,
    'Kyrgyzstan': PIN_MIDDLE_EAST,
    'Lebanon': PIN_MIDDLE_EAST,
    'Moldova': PIN_MIDDLE_EAST,
    'Pakistan': PIN_MIDDLE_EAST,
    'Tajikistan': PIN_MIDDLE_EAST,
    'Yemen': PIN_MIDDLE_EAST,

    'Cameroon': PIN_AFRICA,
    'Egypt': PIN_AFRICA,
    'Ghana': PIN_AFRICA,
    'Kenya': PIN_AFRICA,
    'Lesotho': PIN_AFRICA,
    'Malawi': PIN_AFRICA,
    'Mali': PIN_AFRICA,
    'Mozambique': PIN_AFRICA,
    'Nigeria': PIN_AFRICA,
    'Rwanda': PIN_AFRICA,
    'South Africa': PIN_AFRICA,
    'Tanzania': PIN_AFRICA,
    'Uganda': PIN_AFRICA,
    'Zambia': PIN_AFRICA,

    'Cambodia': PIN_EAST_ASIA,
    'Myanmar (Burma)': PIN_EAST_ASIA,
    'Philippines': PIN_EAST_ASIA,
    'Timor-Leste': PIN_EAST_ASIA,

    'Costa Rica': PIN_NORTH_AMERICA,
    'Haiti': PIN_NORTH_AMERICA,
    'Nicaragua': PIN_NORTH_AMERICA,

    'Brazil': PIN_SOUTH_AMERICA,
    'Ecuador': PIN_SOUTH_AMERICA,
    'El Salvador': PIN_SOUTH_AMERICA,
    'Guatemala': PIN_SOUTH_AMERICA,
    'Mexico': PIN_SOUTH_AMERICA,
    'Peru': PIN_SOUTH_AMERICA,
}

# start lastTime as now.
lastID = 0

# Setup all pins to output voltage ie be HIGH. 
# Also turn them all on for a second then off, good for testing LEDs.
def initializePins():
    if RASPI:
        for pin in ALL_PINS:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin,True)
            print('Turn on: ' + str(pin))
            time.sleep(2)
            GPIO.output(pin, False)

def scrapeLatest():
    global lastID
    try:
        response = urllib2.urlopen('http://api.kivaws.org/v1/lending_actions/recent.json', None, 100)
        recentLoans = json.load(response)
        recentLoans = recentLoans['lending_actions']
	    #print recentLoans
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
            # lightUpLoans is blocking so it won't return for aprox POLL_INTERVAL
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
        if lastID == 0 and len(simpleList) > 8:
            print "Got enough for first round."
            break

        if action['loan']['location']['country'] in countryGpio:
            print "in list! "+ action['loan']['location']['country'] + "  "+ action['date']
            simpleList.append({'country': action['loan']['location']['country'] , 
            'date': action['date']})
        else :
            print "Missing region in code: " +  action['loan']['location']['country']

    
    return simpleList

# Take a list of loans, and light each one up in order.
# The function sleeps and is blocking.
def lightUpLoans(simpleList):
    timePerLoan = POLL_INTERVAL / len(simpleList)
    print "timeperLoan: " + str(timePerLoan)
    
    # reverse list so it 'plays it forward in time'
    for loan in reversed(simpleList):
        print loan['country'] + "   " +loan['date']
        lightUpCountry(loan['country'], timePerLoan)
        # sleep for gap inbetween countries
        time.sleep(max(0,timePerLoan - MAX_LED_ON_TIME))
        

def lightUpCountry(country, timePerLoan):
    print "gpio on "+  str(countryGpio[country])
    if RASPI:
        GPIO.output(countryGpio[country], True)
    
    time.sleep(min(timePerLoan, MAX_LED_ON_TIME))
    
    print "gpio off "+  str(countryGpio[country])
    if RASPI:
        GPIO.output(countryGpio[country], False)

        
# start the app
initializePins()
scrapeLatest()

