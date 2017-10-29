import sys
import numpy as np
import matplotlib.pyplot as plt

import csv
import copy
import argparse
import itertools

from random import randint

################################################################
## GET COMMAND LINE ARGUMENTS
################################################################
parser = argparse.ArgumentParser(description="map")
parser.add_argument("--numTeamMembers")
parser.add_argument("--difficultyLevel")
args, leftovers = parser.parse_known_args()
if args.numTeamMembers is not None:
	numTeamMembers = int(args.numTeamMembers)
	print('Setting up game for ' + str(numTeamMembers) + ' players.')
	# Check that numTeamMembers in [2,3,4]
	if numTeamMembers not in [2,3,4]:
		raise ValueError('Only 2, 3 or 4 players supported.')
else:
	print('Defaulting to 3 players.')
	numTeamMembers = 3

if args.difficultyLevel is not None:
	difficultyLevel = args.difficultyLevel
	print('Setting up game for ' + difficultyLevel + ' difficulty level.')
else:
	print('Defaulting to introductory difficulty (4 epidemic cards).')
	difficultyLevel = 'introductory'

################################################################
## SET NUMEPIDEMICS FROM DIFFICULTY LEVEL
################################################################
# Choose difficulty
difficultyLevels = {'test1':1, 'test2':2, 'test3':3, 'introductory':4,'standard':5, 'heroic':6, 'test7':7, 'test8':8,}
# introductory : 4 epidemics
# standard     : 5 epidemics
# heroic       : 6 epidemics
try:
	numEpidemics = difficultyLevels[difficultyLevel]
except:
	raise ValueError('input difficultyLevel must be in ' + str(difficultyLevels.keys()) )

################################################################
## DEFINE CITIES
################################################################
cityNames = {'SanFrancisco':1,'Chicago':2, 'Atlanta':3, 'Montreal':4, 'Washington':5, 'NewYork':6, 'Madrid':7, 'London':8, 'Paris':9, 'Essen':10, 'Milan':11, 'StPetersburg':12,'LosAngeles':13, 'MexicoCity':14, 'Lima':15, 'Santiago':16, 'Bogota':17, 'Miami':18, 'BuenosAires': 19, 'SaoPaulo':20, 'Lagos':21, 'Kinsasha':22, 'Khartoum':23, 'Johannesburg':24, 'Algiers': 25, 'Cairo':26, 'Istanbul':27, 'Moscow':28, 'Baghdad': 29, 'Riyadh': 30, 'Tehran': 31, 'Karachi':32, 'Mumbai': 33, 'Delhi':34, 'Chennai':35, 'Kolkata':36, 'Bangkok': 37, 'Jakarta': 38, 'Beijing': 39, 'HongKong': 40, 'HoChiMinhCity': 41, 'Shanghai': 42, 'Taipei': 43, 'Manila': 44, 'Seoul': 45, 'Osaka': 46, 'Tokyo': 47, 'Sydney': 48}
indexedCities = dict((v,k) for k,v in cityNames.iteritems())
numCities = len(cityNames)
# cities are indexed 1-48
unshuffledCities = np.arange(numCities) + 1

################################################################
## MAP CITY LOCATIONS AND CONNECTIONS
################################################################
mapAdj=np.genfromtxt('cityMapAdjIndexed.csv', delimiter=',')
mapXYs=np.genfromtxt('cityMapXYIndexed.csv', delimiter=',')
mapColors=np.genfromtxt('cityColorsIndexed.csv', delimiter=',')

################################################################
## COLOR CITY LOCATIONS
################################################################
hexcolorreader = csv.reader(open('cityHexColorsIndexed.csv', 'r'))
mapHexColors = {}
for row in hexcolorreader: # note hex colors are strings
    k, v = row
    mapHexColors[int(k)] = v.strip()

citynamereader = csv.reader(open('cityNamesIndexed.csv', 'r'))
mapCityNames = {}
for row in citynamereader: # note hex colors are strings
    k, v = row
    mapCityNames[int(k)] = v.strip()

citycolorreader = csv.reader(open('cityColorStrsIndexed.csv', 'r'))
mapCityColorIndexed = {}
for row in citycolorreader: # note hex colors are strings
    k, v = row
    mapCityColorIndexed[int(k)] = v.strip()

diseaseColorIndex = {'blue':0, 'yellow':1, 'black':2, 'red':3}
diseaseIndexes = np.zeros((49))
for di in range(1,49):
	diseaseIndexes[di] = diseaseColorIndex[mapCityColorIndexed[di]]

################################################################
## DEFINE SOME DECK AND DISEASE CUBES HELPER FUNCTIONS
################################################################
def getTopCard(deck):
	topCard = deck[0]
	# Remove that card from the deck
	deck = np.delete(deck, 0)
	return topCard, deck

def decrementDiseasePile(diseaseCubesPiles, color2decrement):
    diseaseCubesPiles[color2decrement] = diseaseCubesPiles[color2decrement] - 1
    return diseaseCubesPiles

def incrementDiseasePile(diseaseCubesPiles, color2decrement):
    diseaseCubesPiles[color2increment] = diseaseCubesPiles[color2increment] + 1
    return diseaseCubesPiles

def decrementCityDisease(cityDiseaseCubes, cityIndex, color2decrement):
    cityDiseaseCubes[cityIndex][color2decrement] = cityDiseaseCubes[cityIndex][color2decrement] - 1
    return cityDiseaseCubes

def incrementCityDisease(cityDiseaseCubes, cityIndex, color2increment):
    cityDiseaseCubes[cityIndex][color2increment] = cityDiseaseCubes[cityIndex][color2increment] + 1
    return cityDiseaseCubes

def placeDiseaseCubes(cityIndex, numCubes, diseaseCubesPiles, cityDiseaseCubes, indexedCities):
    # Determine color of cityIndex
    placeColor = mapCityColorIndexed[cityIndex]
    print('Placing ' + str(numCubes) + ' ' + placeColor + ' cubes on ' + indexedCities[cityIndex] + '.')
    for iCUBES in range(numCubes):
        # remove cube from diseaseCubesPiles
        decrementDiseasePile(diseaseCubesPiles, placeColor)
        incrementCityDisease(cityDiseaseCubes, cityIndex, placeColor) 
        if cityDiseaseCubes[cityIndex][placeColor] > 3:
        	print("Outbreak at " + str(cityIndex) + "," + indexedCities[cityIndex] + " not implemented.")
        	print("Outbreaks impossible on board setup.")

################################################################
## DEFINE DISEASE CUBE PILES
################################################################
# Define all disease cube piles. 
diseaseCubesPiles = {'blue': 24, 'yellow': 24, 'black': 24, 'red': 24}
class printcolors:
    BLUE = '\033[1;34;47m'      # BLUE
    GREEN = '\033[1;32;47m'     # GREEN
    GRAY = '\033[1;30;47m' # GRAY
    YELLOW = '\033[93m'    # YELLOW
    RED = '\033[1;31;47m'       # RED
    BOLD = '\033[1m'       # BOLD
    ENDC = '\033[0m'       # RETURN TO WHITE

# Set up the initial state of the board
################################################################
## INITIALIZE MAP WITH NO DISEASE MARKERS OR RESEARCH STATIONS
################################################################
# Initialize all city disease markers to 0. 
emptyCity = {'blue': 0, 'yellow': 0, 'black': 0, 'red': 0}
cityDiseaseCubes = {}
for iCITY in xrange(1,numCities+1):
    cityDiseaseCubes[iCITY] = copy.deepcopy(emptyCity)

# Initialize all cities with 0 research stations 
cityResearchStations = {}
for iCITY in xrange(1,numCities+1):
    cityResearchStations[iCITY] = 0
# Add a research station to Atlanta
cityResearchStations[cityNames['Atlanta']] = 1

################################################################
## DEFINE INFECTION DECK AND INFECTION DISCARD DECK
################################################################
# Define all infection cards. 
infectionDeck = np.copy(unshuffledCities)
# Sequence them.
np.random.shuffle(infectionDeck)
# Define infectionDeckDiscard pile
infectionDiscardDeck = np.array([],'int')

################################################################
## DISTRIBUTE INITIAL DISEASE CUBES ON MAP
################################################################
# Draw first 3 infection cards 
for iDRAW in range(3):
    # get the top card of infectionDeck, tmpCityIndex
    tmpCityIndex,infectionDeck = getTopCard(infectionDeck)
    # Add that card to the infection discard pile
    infectionDiscardDeck = np.append(infectionDiscardDeck,tmpCityIndex)
    # place 3 disease cubes on that city
    placeDiseaseCubes(tmpCityIndex, 3, diseaseCubesPiles, cityDiseaseCubes, indexedCities)

# Draw next 3 infection cards 
for iDRAW in range(3):
    # get the top card of infectionDeck, tmpCityIndex
    tmpCityIndex,infectionDeck = getTopCard(infectionDeck)
    # Add that card to the infection discard pile
    infectionDiscardDeck = np.append(infectionDiscardDeck,tmpCityIndex)
    # place 2 disease cubes on that city
    placeDiseaseCubes(tmpCityIndex, 2, diseaseCubesPiles, cityDiseaseCubes, indexedCities)

# Draw next 3 infection cards 
for iDRAW in range(3):
    # get the top card of infectionDeck, tmpCityIndex
    tmpCityIndex,infectionDeck = getTopCard(infectionDeck)
    # Add that card to the infection discard pile
    infectionDiscardDeck = np.append(infectionDiscardDeck,tmpCityIndex)
    # place 1 disease cubes on that city
    placeDiseaseCubes(tmpCityIndex, 1, diseaseCubesPiles, cityDiseaseCubes, indexedCities)

################################################################
## DEFINE THE PLAYER SEQUENCE AND INITIAL CARDS PER PLAYER
################################################################
# Set the number of cards per team member count
cardsPerTeamMember = {2:4, 3:3, 4:2}
cardsPerTeamMember = {2:12, 3:12, 4:12}
cardsPerTeamMember = {2:24, 3:16, 4:12}

# List team roles
teamRoles = {0:'Dispatcher',1:'OperationsExpert',2:'Scientist',3:'QuarantineSpecialist',4:'Medic',5:'Researcher',6:'ContingencyPlanner'}
indexedRoles = dict((v,k) for k,v in teamRoles.iteritems())
# List team colors
teamColors = {'Dispatcher':'#551a8b','OperationsExpert':'#32cd32','Scientist':'#FFFFFF','QuarantineSpecialist':'#228b22','Medic':'#ffa500','Researcher':'#614126','ContingencyPlanner':'#00a4a4'}

# make a deck of role indices
teamRoleDeck = np.arange(len(teamRoles))
# shuffle the role deck
np.random.shuffle(teamRoleDeck)
# Choose team members and turn sequence
teamSequence = []
for iTEAM in range(numTeamMembers):
    teamSequence.append(teamRoles[teamRoleDeck[iTEAM]])
#     is any player the researcher?
teamHasResearcher = False
seqResearcher = []
for iSeq in range(numTeamMembers):
	if indexedRoles[teamSequence[iSeq]] == indexedRoles['Researcher']:
		teamHasResearcher = True
		seqResearcher = iSeq

################################################################
## DEFINE EVENT CARDS
################################################################
eventCardNames = {'Airlift':49,'GovernmentGrant':50,'OneQuietNight':51,'ResilientPopulation':52,'Forecast':53}
indexedEventCards = dict((v,k) for k,v in eventCardNames.iteritems())
eventCardMask = np.zeros(54)
eventCardMask[49:] = 1
eventCardMask = eventCardMask > 0

################################################################
## DEFINE PLAYER DECK BEFORE ADDING EPIDEMIC CARDS
################################################################
# Create the player card deck
allPlayerCards = dict(indexedCities, **indexedEventCards)
indexedActionEventPlayerCards = {}
for key in range(len(indexedCities)+1):
    indexedActionEventPlayerCards[key] = 'Action'
for key in range(49,54):
    indexedActionEventPlayerCards[key] = 'Event'

# Create all cards in the player card deck
unshuffledPlayerCards = np.array(allPlayerCards.keys())
# (Epidemics labeled 0s -- all other appPlayerCards indexed 1-53)
allPlayerCards[0] = 'Epidemic'

# Define all player cards. 
playerCardDeck = np.copy(unshuffledPlayerCards)
# Sequence them.
np.random.shuffle(playerCardDeck)

################################################################
## DISTRIBUTE PLAYER DECK CARDS TO TEAM MEMBERS
################################################################
# initialize each teamMemberHand as an empty array
teamMemberHand = []
for iTEAM in range(numTeamMembers):
    teamMemberHand.append(np.array([]))

# Deal starting cards to team members' hands
for numCards in range(cardsPerTeamMember[numTeamMembers]):
    # Distribute cards to players
    for iTEAM in range(numTeamMembers):
        # get the top card of playerCardDeck, tmpPlayerCardIndex
        tmpPlayerCardIndex, playerCardDeck = getTopCard(playerCardDeck)
        # Add that card to the player's hand
        teamMemberHand[iTEAM] = np.append(teamMemberHand[iTEAM],tmpPlayerCardIndex)

################################################################
## PLACE ALL TEAM MEMBERS IN ATLANTA
################################################################
# Represent team members' locations
# Put all team members in Atlanta
teamMemberLocations = cityNames['Atlanta'] * np.ones(numTeamMembers)

################################################################
## DISTRIBUTE EPIDEMIC CARDS ACROSS PLAYER DECK PILES
################################################################
# shuffle in epidemic cards (Epidemics labeled 0s -- all other appPlayerCards indexed 1-53)
epidemicCardIndex = 0

# initialize numEpidemics piles with one epidemic card (index 0) each
epidemicSubDecks = []
for iSUBDECK in range(numEpidemics):
    epidemicSubDecks.append(np.array([0]))

for iCARD in range(playerCardDeck.shape[0]):
	iSUBDECK = np.mod(iCARD, numEpidemics)
	# get the top card of playerCardDeck, tmpPlayerCardIndex
	tmpPlayerCardIndex,playerCardDeck = getTopCard(playerCardDeck)
	# Add that card to the ith playerSubDeck
	epidemicSubDecks[iSUBDECK] = np.append(epidemicSubDecks[iSUBDECK],tmpPlayerCardIndex)

# shuffle all the cards in each of the individual epidemicSubDecks
for iSUBDECK in range(numEpidemics):
	np.random.shuffle(epidemicSubDecks[iSUBDECK])
# shuffle the order of the epidemicSubDecks
deckSeq = np.random.permutation(numEpidemics)
# deal the epidemicSubDecks back into the playerDeck
for iSUBDECK in range(numEpidemics):
	playerCardDeck = np.append(playerCardDeck,epidemicSubDecks[deckSeq[iSUBDECK]])

################################################################
## DEFINE THE CURE STATE
################################################################
# Define all disease cure markers. 
diseaseStates = {0:'active', 1:'cured', 2:'eradicated'}
diseaseCureMarkers = {'blue': 0, 'yellow': 0, 'black': 0, 'red': 0}

################################################################
## DEFINE THE OUTBREAK STATE
################################################################
# initialize outbreak count
outbreakCount = 0

################################################################
## DEFINE THE INFECTION RATE AND ESCALATION
################################################################
infectionRates = [2,2,2,3,3,4,4]
infectionRateMarker = 0
infectionRate = infectionRates[infectionRateMarker]

################################################################
## CREATE AN INITIAL "STATE VECTOR" FOR THE GAME INSTANCE
################################################################
# The player cards seen are all the player cards the team has seen
playerCardsSeen = np.zeros((len(allPlayerCards.keys()),1))
# The player cards held are all the player cards the team has in their hands (in 2, 3 or 4 of 4 columns)
playerCardsHeld = np.zeros((len(allPlayerCards.keys()),4))
for iHAND in range(len(teamMemberHand)):
	for iCARD in range(len(teamMemberHand[iHAND])):
		playerCardsHeld[int(teamMemberHand[iHAND][iCARD]), iHAND] = True
		playerCardsSeen[int(teamMemberHand[iHAND][iCARD])] = True
playerCardsSeen = playerCardsSeen > 0.5
playerCardsHeld = playerCardsHeld > 0.5
# The player cards not seen are those that haven't been seen by the team yet
playerCardsNotSeen = playerCardsSeen < 0.5
# The player cards removed are those discarded from charter/direct flights, cures, and discards to 7 cards
playerCardsRemoved = playerCardsSeen > 2.0
## The player cards removed are those discarded  Tracks how many total cards have come up (like a timer)
numPlayerCardsDealt = sum(playerCardsSeen)
# Tracks which cities have been seen in the infection deck
infectionCardsNotYetSeen = np.zeros((numCities+1,1))
for iCARD in range(len(infectionDeck)):
	infectionCardsNotYetSeen[int(infectionDeck[iCARD])] = True
# Tracks which cities have been moved to the infection discard deck
infectionCardsDiscarded = np.zeros((numCities+1,1))
for iCARD in range(len(infectionDiscardDeck)):
	infectionCardsDiscarded[int(infectionDiscardDeck[iCARD])] = True
# The infection buffer is the list of cities that you've seen infected, but haven't yet come up in the infection discard pile
infectionBuffer = np.zeros((numCities+1,1))
# This only happens when a resilient population card is played to remove the city
infectionCardsRemoved = np.zeros((numCities+1,1))
# Initialize disease cubes by city
blueCubesByCity = np.zeros((numCities+1,1))
yellowCubesByCity = np.zeros((numCities+1,1))
blackCubesByCity = np.zeros((numCities+1,1))
redCubesByCity = np.zeros((numCities+1,1))
for iCITY in cityDiseaseCubes.keys():
	tmpCubes = cityDiseaseCubes[iCITY]
	blueCubesByCity[iCITY] = tmpCubes['blue']
	yellowCubesByCity[iCITY] = tmpCubes['yellow']
	blackCubesByCity[iCITY] = tmpCubes['black']
	redCubesByCity[iCITY] = tmpCubes['red']
# Initialize research facility by city
researchFacilitiesByCity = np.zeros((numCities+1,1))
for iCITY in cityResearchStations.keys():
	researchFacilitiesByCity[iCITY] = cityResearchStations[iCITY]
# Initialize where each team member is at the beginning of the game
teamMemberCities = np.zeros((numCities+1,4))
for iHAND in range(teamMemberLocations.shape[0]):
	teamMemberCities[int(teamMemberLocations[iHAND]),iHAND] = 1 # 3 is 'Atlanta'

print infectionRate
print infectionRateMarker
print outbreakCount

indexedDiseaseColors = {0: 'blue', 1:'yellow', 2:'black', 3:'red'}
diseaseCures = np.zeros((4,1))
diseaseEradications = np.zeros((4,1))

# Track which player is currently choosing actions
playerCurrentTurn = 0

instantStateVector = {'playerCurrentTurn': playerCurrentTurn, \
    'teamRoles': teamSequence,\
    'playerCardsSeen': playerCardsSeen,\
    'playerCardsHeld': playerCardsHeld, \
    'playerCardsNotSeen': playerCardsNotSeen, \
    'playerCardsRemoved': playerCardsRemoved, \
    'numPlayerCardsDealt': numPlayerCardsDealt, \
    'infectionCardsNotYetSeen': infectionCardsNotYetSeen, \
    'infectionCardsDiscarded': infectionCardsDiscarded, \
    'infectionBuffer': infectionBuffer, \
    'infectionCardsRemoved': infectionCardsRemoved, \
    'blueCubesByCity': blueCubesByCity, \
    'yellowCubesByCity': yellowCubesByCity, \
    'blackCubesByCity': blackCubesByCity, \
    'redCubesByCity': redCubesByCity, \
    'researchFacilitiesByCity': researchFacilitiesByCity, \
    'teamMemberCities': teamMemberCities, \
    'infectionRate': infectionRate, \
    'infectionRateMarker': infectionRateMarker, \
    'outbreakCount': outbreakCount, \
    'diseaseCures': diseaseCures, \
    'diseaseEradications': diseaseEradications}

################################################################
## SHOW STATE (instantStateVector)
################################################################
# Show map
plt.close("all")
fig = plt.gcf()
fig.set_size_inches(27.5, 20.0)

im = plt.imread("pandemicMap.jpg")
implot = plt.imshow(im)
for k in indexedCities.keys():
	# Plot all cities with circles
	plt.scatter(x=[mapXYs[k-1][1]], y=[mapXYs[k-1][2]], c=mapHexColors[k], s=300, alpha=0.5)
	# Name all cities
	t=plt.text(mapXYs[k-1][1]-15, mapXYs[k-1][2]-25, mapCityNames[k], color=mapHexColors[k])
	t.set_bbox(dict(facecolor='#bbbbbb', alpha=0.9, edgecolor='white'))

# Plot all city connections
cityConns = np.transpose(np.where(mapAdj)) + 1
for cci in np.arange(0,len(cityConns)):
	connXY = mapXYs[cityConns[cci]-1]
	plt.plot(connXY[:,1],connXY[:,2],'k',linewidth=5)

# Plot all cubes (from instant state vector)
isvblue = instantStateVector['blueCubesByCity']
for ic in range(len(isvblue)):
	if isvblue[ic] > 0:
		nC = int(isvblue[ic])
		xyC = mapXYs[mapXYs[:,0]==ic,1:3][0]
		plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='^', c='blue', s=1500, alpha=0.5, edgecolor='white', linewidth='2')
	if isvblue[ic] > 1:
		plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='^', c='blue', s=3000, alpha=0.7, edgecolor='white', linewidth='4')
	if isvblue[ic] > 2:
		plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='^', c='blue', s=4500, alpha=0.9, edgecolor='white', linewidth='7')
isvyellow = instantStateVector['yellowCubesByCity']
for ic in range(len(isvyellow)):
	if isvyellow[ic] > 0:
		nC = int(isvyellow[ic])
		xyC = mapXYs[mapXYs[:,0]==ic,1:3][0]
		plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='>', c='yellow', s=1500, alpha=0.5, edgecolor='white', linewidth='2')
	if isvyellow[ic] > 1:
		plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='>', c='yellow', s=3000, alpha=0.7, edgecolor='white', linewidth='4')
	if isvyellow[ic] > 2:
		plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='>', c='yellow', s=4500, alpha=0.9, edgecolor='white', linewidth='7')
isvblack = instantStateVector['blackCubesByCity']
for ic in range(len(isvblack)):
	if isvblack[ic] > 0:
		nC = int(isvblack[ic])
		xyC = mapXYs[mapXYs[:,0]==ic,1:3][0]
		plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='v', c='black', s=1500, alpha=0.5, edgecolor='white', linewidth='2')
	if isvblack[ic] > 1:
		plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='v', c='black', s=3000, alpha=0.7, edgecolor='white', linewidth='4')
	if isvblack[ic] > 2:
		plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='v', c='black', s=4500, alpha=0.9, edgecolor='white', linewidth='7')
isvred = instantStateVector['redCubesByCity']
for ic in range(len(isvred)):
	if isvred[ic] > 0:
		nC = int(isvred[ic])
		xyC = mapXYs[mapXYs[:,0]==ic,1:3][0]
		plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='<', c='red', s=1500, alpha=0.5, edgecolor='white', linewidth='2')
	if isvred[ic] > 1:
		plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='<', c='red', s=3000, alpha=0.7, edgecolor='white', linewidth='4')
	if isvred[ic] > 2:
		plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='<', c='red', s=4500, alpha=0.9, edgecolor='white', linewidth='7')

# Plot all player locations (from instant state vector)
teamLocs = np.transpose(np.where(instantStateVector['teamMemberCities']))
playerThetaOffs = 3.0*np.pi/4.0
dTheta = 2*np.pi / numTeamMembers
rPlayer = 12
for teami in range(numTeamMembers):
	thetaOffs = playerThetaOffs + teami*dTheta
	xyOffs = np.array([rPlayer*np.cos(thetaOffs),rPlayer*np.sin(thetaOffs)])
	xyTm = mapXYs[mapXYs[:,0]==teamLocs[teami][0],1:3][0]
	# Plot all team members with colored circles
	plt.scatter(x=[xyTm[0]+xyOffs[0]], y=[xyTm[1]+xyOffs[1]], c=teamColors[teamSequence[teami]], s=500, alpha=0.9, edgecolor='white')
plt.show()
fig.savefig('pandemicInit.png', dpi=100)


################################################################
## COMPUTE AVAILABLE ACTIONS TO currentPlayerTurn
################################################################
turn = {}
turn['numActions'] = 4
turn['currentActionCounter'] = 1
# 5 for the generalist
turn['teamHasResearcher'] = teamHasResearcher
turn['seqResearcher'] = seqResearcher
isv = instantStateVector
pCTurn = isv['playerCurrentTurn']
pCHeld = np.transpose(isv['playerCardsHeld'])[pCTurn]
pCityCards = pCHeld[:49]
#   where is current player?
turn['currentCityIndex'] = np.where(np.transpose(isv['teamMemberCities'])[pCTurn])[0][0]
#   is player in a city without a research facility?
turn['cityHasResearchFacility'] = isv['researchFacilitiesByCity'][turn['currentCityIndex']][0]

# MOVE
#!   is player the dispatcher?
#!     if so, repeat for all players:
#   what moves are available to current player?
#     from adjacency
turn['possibleAdjMoves'] = np.where(mapAdj[turn['currentCityIndex']-1])[0] + 1
#     from cards
#       city cards
turn['directFlightMoves'] = np.where(pCityCards)[0]
#       is player in city of held card? -> Anywhere
turn['canCharter'] = any(np.where(pCityCards)[0] == turn['currentCityIndex'])
#   -> list possible moves
destinations = np.zeros((3,49))
destinations[0][turn['possibleAdjMoves']] = True
destinations[1][turn['directFlightMoves']] = True
destinations[2][:] = turn['canCharter']
turn['destinations'] = destinations

# TREAT
#   is player in a city with any disease cubes?
#     what color are the disease cubes?
disease = np.zeros((4,49))
disease[0,:] = np.transpose(isv['blueCubesByCity'])
disease[1,:] = np.transpose(isv['yellowCubesByCity'])
disease[2,:] = np.transpose(isv['blackCubesByCity'])
disease[3,:] = np.transpose(isv['redCubesByCity'])
turn['disease'] = disease
turn['diseaseStrength'] = np.transpose(disease)[turn['currentCityIndex']]
#     determine how many disease cubes are removed by treatment
#   -> list treat color options
turn['treatOptions'] = turn['diseaseStrength']>0.5
turn['canTreat'] = any(turn['treatOptions'])

# BUILD
#   does player have ability to build a facility? (i.e. is operations expert with a card or has city card)
if not(turn['cityHasResearchFacility']):
#   -> list build research facility card options
	if ( indexedRoles[teamSequence[pCTurn]] == indexedRoles['OperationsExpert'] ) & ( any(pCityCards) ):
		turn['buildResearchFacilityWithCard'] = pCityCards
	else:
		if any( turn['directFlightMoves'] == turn['currentCityIndex'] ):
			turn['buildResearchFacilityWithCard'] = np.array(turn['currentCityIndex'])
else:
	turn['buildResearchFacilityWithCard'] = np.array([])

# CURE
#   is player in a city with a research facility?
if ( indexedRoles[teamSequence[pCTurn]] == indexedRoles['Scientist'] ):
	turn['nToCure'] = 4
else:
	turn['nToCure'] = 5
if turn['cityHasResearchFacility']:
    #   does the player have sufficient number of cards of one color to cure?
	pCityColors = diseaseIndexes[pCityCards]
	nByColor = np.histogram(pCityColors,bins=[0,1,2,3,4])[0]
	cureable = nByColor >= turn['nToCure']
	if any( cureable ):
		turn['canCure'] = True
		turn['cureColorIndex'] = np.where(cureable)[0][0] # there will only ever be one cureable disease
		turn['cardsToCure'] = np.where((diseaseIndexes == turn['cureColorIndex']) & pCityCards)[0]
	else:
		turn['canCure'] = False
		turn['cureColorIndex'] = [] # can't cure without enough cards
		turn['cardsToCure'] = []
else:
	turn['canCure'] = False
	turn['cureColorIndex'] = [] # can't cure without a research facility
	turn['cardsToCure'] = []
#   -> list cure that color

# SHARE
turn['giveCityCardTo'] = np.array([])
turn['takeCityCardFrom'] = np.array([])	
#   is player in a city with at least one other player?
playersInCurrentCity = np.where(isv['teamMemberCities'][turn['currentCityIndex']])[0]
otherPlayersInCurrentCity = playersInCurrentCity[playersInCurrentCity != pCTurn]
#     do any of the players have the card of the city they're in?
playersHoldingCurrentCity = np.where(isv['playerCardsHeld'][turn['currentCityIndex']])[0]

otherPlayerHoldingCurrentCity = np.intersect1d(playersHoldingCurrentCity, otherPlayersInCurrentCity)
# other player holds city card to give
if ( otherPlayerHoldingCurrentCity.shape[0] > 0 ):
	#   -> list possible take shares
	# otherPlayersInCurrentCity can give current city to pCTurn player
	turn['takeCityCardFrom'] = np.array([otherPlayerHoldingCurrentCity[0], turn['currentCityIndex']])
else:
	# current player holds city card to give
	if ( np.intersect1d(playersHoldingCurrentCity, pCTurn).shape[0] > 0 ):
		# current player can give currentCity to otherPlayersInCurrentCity
		for otherPlayer in otherPlayersInCurrentCity: #   -> list possible give shares
			appendGivePair = np.array([otherPlayer, turn['currentCityIndex']])
			if turn['giveCityCardTo'].shape[0] > 0:
				turn['giveCityCardTo'] = np.vstack([turn['giveCityCardTo'], appendGivePair])
			else:
				turn['giveCityCardTo'] = appendGivePair

#Researcher can give any city card to otherPlayersInCurrentCity
if ( turn['teamHasResearcher'] ):
	turn['researcherCityCardsHeld'] = np.where(np.transpose(isv['playerCardsHeld'])[turn['seqResearcher']][:49])[0]
	researcherInCurrentCity = np.where(np.transpose(isv['teamMemberCities'])[turn['seqResearcher']])[0][0] == turn['currentCityIndex']
	if researcherInCurrentCity:
		if ( turn['seqResearcher'] == pCTurn ):
			#   -> list possible Researcher give shares
			for researcherCardToGive in turn['directFlightMoves']:
				for otherPlayer in otherPlayersInCurrentCity:
					appendGivePair = np.array([otherPlayer, researcherCardToGive])
					if turn['giveCityCardTo'].shape[0] > 0:
						turn['giveCityCardTo'] = np.vstack([turn['giveCityCardTo'], appendGivePair])
					else:
						turn['giveCityCardTo'] = appendGivePair
		else:
			otherPlayerResearcher = turn['seqResearcher']
			#   -> list possible take from Researcher shares
			for researcherCardToTake in turn['researcherCityCardsHeld']:
				appendTakePair = np.array([otherPlayerResearcher, researcherCardToTake])
				if turn['takeCityCardFrom'].shape[0] > 0:
					turn['takeCityCardFrom'] = np.vstack([turn['takeCityCardFrom'], appendTakePair])
				else:
					turn['takeCityCardFrom'] = appendTakePair

# PASS
#    -> list do nothing as an action

# EVENT (does not use a turn)
#    -> list event cards of all players
turn['teamEventCardsHeld'] = np.where(np.any(isv['playerCardsHeld'], axis=1) & eventCardMask)[0]

################################################################
# LIST ALL ACTIONS AVAILABLE TO CURRENT PLAYER
################################################################
actionList = []
playerStr = teamSequence[pCTurn] + '(' + str(pCTurn) + ')'
currentCityStr = indexedCities[turn['currentCityIndex']]

actionEventOptionCount = 0
passStr = ['Pass turn']
pM = ['pCTurn', 'passTurn']
actionList.append([actionEventOptionCount, passStr, pM])

for iPAM in turn['possibleAdjMoves']:
	adjMoveStr = ['Move ' + playerStr + ' from ' + currentCityStr + ' to ' + indexedCities[iPAM]]
	pAM = [pCTurn, 'move', turn['currentCityIndex'], iPAM]
	actionEventOptionCount = actionEventOptionCount + 1
	actionList.append([actionEventOptionCount, adjMoveStr, pAM])

for iDFM in turn['directFlightMoves']:
	directFlightStr = ['Direct flight ' + playerStr + ' from ' + currentCityStr + ' to ' + indexedCities[iDFM]]
	dFM = [pCTurn, 'directFlight', turn['currentCityIndex'], iDFM]
	actionEventOptionCount = actionEventOptionCount + 1
	actionList.append([actionEventOptionCount, directFlightStr, dFM])

if turn['canCharter']:
	for iCFM in range(1,49):
		charterFlightStr = ['Charter flight ' + playerStr + ' from ' + currentCityStr + ' to ' + indexedCities[iCFM]]
		cFM = [pCTurn, 'charterFlight', turn['currentCityIndex'], iCFM]
		actionEventOptionCount = actionEventOptionCount + 1
		actionList.append([actionEventOptionCount, charterFlightStr, cFM])

if turn['cityHasResearchFacility']:
	if ( np.sum(isv['researchFacilitiesByCity']) > 1.0 ):
		# loop over research facility options
		shuttleDestinationOptions = np.setdiff1d(np.where(isv['researchFacilitiesByCity'])[0], turn['currentCityIndex'])
		for iSDO in shuttleDestinationOptions:
			shuttleFlightStr = ['Shuttle flight ' + playerStr + ' from ' + currentCityStr + ' to ' + indexedCities[iSDO]]
			sDO = [pCTurn, 'shuttle', turn['currentCityIndex'], iSDO]
			actionEventOptionCount = actionEventOptionCount + 1
			actionList.append([actionEventOptionCount, shuttleFlightStr, sDO])

if turn['canTreat']:
	for iTO in np.where(turn['treatOptions'])[0]:
		treatStr = ['Treat ' + indexedDiseaseColors[iTO] + ' (' + str(turn['diseaseStrength'][iTO]) + ' cubes) disease in ' + currentCityStr ]
		tAct = [pCTurn, 'treat', turn['currentCityIndex'], iTO]
		actionEventOptionCount = actionEventOptionCount + 1
		actionList.append([actionEventOptionCount, treatStr, tAct])

if len(turn['buildResearchFacilityWithCard']) > 0:
	for iBRF in turn['buildResearchFacilityWithCard']:
		buildStr = ['Build research facility in ' + currentCityStr + ' with ' + indexedCities[iBRF] + ' city card.']
		bRF = [pCTurn, 'build', turn['currentCityIndex'], iBRF]
		actionEventOptionCount = actionEventOptionCount + 1
		actionList.append([actionEventOptionCount, buildStr, bRF])

if turn['canCure']:
	if ( len(turn['cardsToCure']) >= turn['nToCure'] ):
		pickCardCombination = [list(x) for x in itertools.combinations(turn['cardsToCure'], turn['nToCure'])]
		for iPCC in pickCardCombination:
			cardSubsetToCure = np.array(iPCC)
			cureStr = 'Cure ' + indexedDiseaseColors[turn['cureColorIndex']] + ' with cards '
			for iCL in range(turn['nToCure']):
				cureStr = cureStr + indexedCities[iPCC[iCL]] + "+"
			#cureStr = cureStr[:-1]
			print cureStr
			cureStr = [cureStr[:-1]]
			cD = [pCTurn, 'cure', turn['cureColorIndex'], cardSubsetToCure, turn['nToCure']]
			actionEventOptionCount = actionEventOptionCount + 1
			actionList.append([actionEventOptionCount, cureStr, cD])
			print actionList

if ( turn['giveCityCardTo'].ndim == 1 ) & ( turn['giveCityCardTo'].shape[0] > 1 ):
	iGCC = turn['giveCityCardTo']
	gC = [pCTurn, 'give', iGCC[0], iGCC[1]]
	actionEventOptionCount = actionEventOptionCount + 1
	actionList.append([actionEventOptionCount, giveStr, gC])
else:
	for iGCC in turn['giveCityCardTo']:
		giveStr = ['Give player ' + str(iGCC[0]) + ' (' + teamSequence[iGCC[0]] + ') ' + indexedCities[iGCC[1]] + ' card.']
		gC = [pCTurn, 'give', iGCC[0], iGCC[1]]
		actionEventOptionCount = actionEventOptionCount + 1
		actionList.append([actionEventOptionCount, giveStr, gC])

if ( turn['takeCityCardFrom'].ndim == 1 ) & ( turn['takeCityCardFrom'].shape[0] > 1 ):
	iTCC = turn['takeCityCardFrom']
	takeStr = ['Take ' + indexedCities[iTCC[1]] + ' city card from ' + str(iTCC[0]) + ' (' + teamSequence[iTCC[0]] + ') ']
	tC = [pCTurn, 'take', iTCC[0], iTCC[1]]
	actionEventOptionCount = actionEventOptionCount + 1
	actionList.append([actionEventOptionCount, takeStr, tC])
else:
    for iTCC in turn['takeCityCardFrom']: 
    	takeStr = ['Take ' + indexedCities[iTCC[1]] + ' city card from ' + str(iTCC[0]) + ' (' + teamSequence[iTCC[0]] + ') ']
    	tC = [pCTurn, 'take', iTCC[0], iTCC[1]]
    	actionEventOptionCount = actionEventOptionCount + 1
    	actionList.append([actionEventOptionCount, takeStr, tC])
turn['actionList'] = actionList

# LIST ALL EVENTS
eventList = []
for iEC in turn['teamEventCardsHeld']:
	eventStr = ['Play the ' + indexedEventCards[iEC] + ' event card by player ' + playerStr + '.']
	eC = [pCTurn, 'event', iEC]
	actionEventOptionCount = actionEventOptionCount + 1
	eventList.append([actionEventOptionCount, eventStr, eC])
turn['eventList'] = eventList

# LIST COMBINED ACTION & EVENT OPTIONS
turn['actionEventList'] = actionList
if (len(eventList) > 0):
	for iEL in eventList:
		turn['actionEventList'].append(iEL)

################################################################
# PROVIDE CARDS HELD AND COLORS CONTEXT FOR CURRENT PLAYER
################################################################
print('====================================')
print(playerStr + ' holds cards: ')
for iCH in np.where(pCHeld)[0]:
	if ( indexedActionEventPlayerCards[iCH] == 'Action' ):
		if indexedDiseaseColors[diseaseIndexes[iCH]] == 'blue':
			print printcolors.BLUE + indexedActionEventPlayerCards[iCH] + ': (' + allPlayerCards[iCH] + '-' + indexedDiseaseColors[diseaseIndexes[iCH]] + ')' + printcolors.ENDC
		if indexedDiseaseColors[diseaseIndexes[iCH]] == 'yellow':
			print printcolors.YELLOW + indexedActionEventPlayerCards[iCH] + ': (' + allPlayerCards[iCH] + '-' + indexedDiseaseColors[diseaseIndexes[iCH]] + ')' + printcolors.ENDC
		if indexedDiseaseColors[diseaseIndexes[iCH]] == 'black':
			print printcolors.GRAY + indexedActionEventPlayerCards[iCH] + ': (' + allPlayerCards[iCH] + '-' + indexedDiseaseColors[diseaseIndexes[iCH]] + ')' + printcolors.ENDC
		if indexedDiseaseColors[diseaseIndexes[iCH]] == 'red':
			print printcolors.RED + indexedActionEventPlayerCards[iCH] + ': (' + allPlayerCards[iCH] + '-' + indexedDiseaseColors[diseaseIndexes[iCH]] + ')' + printcolors.ENDC
	else:
		print(indexedActionEventPlayerCards[iCH] + ': (' + allPlayerCards[iCH] + ')' )
print('====================================')

for iAEC in turn['actionEventList']:
	print( str(iAEC[0]) + ": " + iAEC[1][0] )

# UPDATE GAME STATE WITH ACTION
def move(moveAdjacentAction, pCTurn=pCTurn, isv=isv):
	currentCityIndex = moveAdjacentAction[2]
	destinationCityIndex = moveAdjacentAction[3]
	isvTMC=isv['teamMemberCities']
	np.transpose(isvTMC)[pCTurn][currentCityIndex] = 0
	np.transpose(isvTMC)[pCTurn][destinationCityIndex] = 1
	isv['teamMemberCities'] = isvTMC
	return isv

def directFlight(directFlightAction, pCTurn=pCTurn, isv=isv):
	currentCityIndex = directFlightAction[2]
	destinationCityIndex = directFlightAction[3]
	isvTMC=isv['teamMemberCities']
	np.transpose(isvTMC)[pCTurn][currentCityIndex] = 0
	np.transpose(isvTMC)[pCTurn][destinationCityIndex] = 1
	isv['teamMemberCities'] = isvTMC
	# remove destinationCityCard from player hand to playerDiscardPile
	np.transpose(isv['playerCardsHeld'])[pCTurn][destinationCityIndex] = False
	isv['playerCardsRemoved'][destinationCityIndex] = True
	return isv

def charterFlight(charterFlightAction, pCTurn=pCTurn, isv=isv):
	currentCityIndex = charterFlightAction[2]
	destinationCityIndex = charterFlightAction[3]
	isvTMC=isv['teamMemberCities']
	np.transpose(isvTMC)[pCTurn][currentCityIndex] = 0
	np.transpose(isvTMC)[pCTurn][destinationCityIndex] = 1
	isv['teamMemberCities'] = isvTMC
	# remove currentCityCard from player hand to playerDiscardPile
	np.transpose(isv['playerCardsHeld'])[pCTurn][currentCityIndex] = False
	isv['playerCardsRemoved'][currentCityIndex] = True
	return isv

def shuttle(shuttleFlightAction, pCTurn=pCTurn, isv=isv):
	currentCityIndex = shuttleFlightAction[2]
	destinationCityIndex = shuttleFlightAction[3]
	isvTMC=isv['teamMemberCities']
	np.transpose(isvTMC)[pCTurn][currentCityIndex] = 0
	np.transpose(isvTMC)[pCTurn][destinationCityIndex] = 1
	isv['teamMemberCities'] = isvTMC
	return isv

def treat(treatAction, pCTurn=pCTurn, isv=isv):
	cityToTreatDisease = treatAction[2]
	diseaseIndexToTreat = treatAction[3]
	if ( isv['diseaseEradications'][diseaseIndexToTreat][0] > 0 ) | ( indexedRoles[teamSequence[pCTurn]] == indexedRoles['Medic'] ):
		# TREAT ALL CUBES OF 
		print('remove all cubes')
		if ( indexedDiseaseColors[diseaseIndexToTreat] == 'blue' ):
			isv['blueCubesByCity'][cityToTreatDisease] = 0
		elif ( indexedDiseaseColors[diseaseIndexToTreat] == 'yellow' ):
			isv['yellowCubesByCity'][cityToTreatDisease] = 0
		elif ( indexedDiseaseColors[diseaseIndexToTreat] == 'black' ):
			isv['blackCubesByCity'][cityToTreatDisease] = 0
		elif ( indexedDiseaseColors[diseaseIndexToTreat] == 'red' ):
			isv['redCubesByCity'][cityToTreatDisease] = 0
		else:
			print('Disease index not recognized')
	else:
		print('remove one cube')
		if ( indexedDiseaseColors[diseaseIndexToTreat] == 'blue' ):
			isv['blueCubesByCity'][cityToTreatDisease] = isv['blueCubesByCity'][cityToTreatDisease] - 1
		elif ( indexedDiseaseColors[diseaseIndexToTreat] == 'yellow' ):
			isv['yellowCubesByCity'][cityToTreatDisease] = isv['yellowCubesByCity'][cityToTreatDisease] - 1
		elif ( indexedDiseaseColors[diseaseIndexToTreat] == 'black' ):
			isv['blackCubesByCity'][cityToTreatDisease] = isv['blackCubesByCity'][cityToTreatDisease] - 1
		elif ( indexedDiseaseColors[diseaseIndexToTreat] == 'red' ):
			isv['redCubesByCity'][cityToTreatDisease] = isv['redCubesByCity'][cityToTreatDisease] - 1
		else:
			print('Disease index not recognized')
	return isv

def build(buildAction, pCTurn=pCTurn, isv=isv):
	cityToBuildResearchFacility = buildAction[2]
	cardForResearchFacility = buildAction[3]
	np.transpose(isv['playerCardsHeld'])[pCTurn][cardForResearchFacility] = False
	isv['playerCardsRemoved'][cardForResearchFacility] = True
	isv['researchFacilitiesByCity'][cityToBuildResearchFacility] = True
	return isv

def cure(cureAction, pCTurn=pCTurn, isv=isv, indexedCities=indexedCities):
	cureColorIndex = cureAction[2]
	cardsToCure = cureAction[3]
	nToCure = cureAction[4]
	if ( len(cardsToCure) > nToCure ):
		# update cardsToCure if player holds more than nToCure for that player
		cardsToCure = chooseCardsToCure(cardsToCure, nToCure, indexedCities)
	for iCC in cardsToCure:
		np.transpose(isv['playerCardsHeld'])[pCTurn][iCC] = False
		isv['playerCardsRemoved'][iCC] = True
	isv['diseaseCures'][cureColorIndex] = 1.0
	return isv

def give(giveCardAction, pCTurn=pCTurn, isv=isv):
	playerToGiveTo = giveCardAction[2]
	cityCardToGive = giveCardAction[3]
	np.transpose(isv['playerCardsHeld'])[pCTurn][cityCardToGive] = False
	np.transpose(isv['playerCardsHeld'])[playerToGiveTo][cityCardToGive] = True
	return isv

def take(takeCardAction, pCTurn=pCTurn, isv=isv):
	playerToTakeCardFrom = takeCardAction[2]
	cityCardToTake = takeCardAction[3]
	np.transpose(isv['playerCardsHeld'])[playerToTakeCardFrom][cityCardToTake] = False
	np.transpose(isv['playerCardsHeld'])[pCTurn][cityCardToTake] = True
	return isv

def passTurn(passAction, pCTurn=pCTurn, isv=isv):
	print("Passing action.")
	return isv

################################################################
# EXECUTE CURRENT PLAYER ACTION
################################################################
actionEventChoice = 70
toExecuteActionEvent = turn['actionEventList'][actionEventChoice]
turn['toExecuteActionEvent'] = toExecuteActionEvent

print('Executing ' + str(actionEventChoice) + ': ' + toExecuteActionEvent[1][0])
if ( toExecuteActionEvent[2][1] == 'passTurn' ):
	isv = passTurn(toExecuteActionEvent[2], pCTurn, isv)
	actionCost = 1
elif ( toExecuteActionEvent[2][1] == 'move' ):
	isv = move(toExecuteActionEvent[2], pCTurn, isv)
	actionCost = 1
elif ( toExecuteActionEvent[2][1] == 'directFlight' ):
	isv = directFlight(toExecuteActionEvent[2], pCTurn, isv)
	actionCost = 1
elif ( toExecuteActionEvent[2][1] == 'charterFlight' ):
	isv = charterFlight(toExecuteActionEvent[2], pCTurn, isv)
	actionCost = 1
elif ( toExecuteActionEvent[2][1] == 'shuttle' ):
	isv = shuttle(toExecuteActionEvent[2], pCTurn, isv)
	actionCost = 1
elif ( toExecuteActionEvent[2][1] == 'treat' ):
	isv = treat(toExecuteActionEvent[2], pCTurn, isv)
	actionCost = 1
elif ( toExecuteActionEvent[2][1] == 'build' ):
	isv = build(toExecuteActionEvent[2], pCTurn, isv)
	actionCost = 1
elif ( toExecuteActionEvent[2][1] == 'cure' ):
	isv = cure(toExecuteActionEvent[2], pCTurn, isv)
	actionCost = 1
elif ( toExecuteActionEvent[2][1] == 'give' ):
	isv = give(toExecuteActionEvent[2], pCTurn, isv)
	actionCost = 1
elif ( toExecuteActionEvent[2][1] == 'take' ):
	isv = take(toExecuteActionEvent[2], pCTurn, isv)
	actionCost = 1
else:
	print('Not a valid action: ' + toExecuteActionEvent[2][1])

# DECREMENT numActions BY actionCost

# SHOW BOARD

# UNTIL numActions TAKEN

# DRAW 2 player cards

# DRAW 2 'infectionRate' infection deck cards

# UPDATE board

# INCREMENT player in sequence

################################################################
## PLAY GAME UNTIL END STATE
################################################################

# End game
# ++++ all 4 diseases cured!
# - 8 outbreaks occur
# - no disease cubes left when one is needed
# - no player cards are left when needed
# Consider end state of + number cures found

