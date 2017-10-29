import sys
import numpy as np
import matplotlib.pyplot as plt

import csv
import copy
import argparse
import itertools

from random import randint

#from pandemicUtils import getTopCard, decrementDiseasePile, incrementDiseasePile, decrementInitialCityDisease, incrementInitialCityDisease, placeDiseaseCubes

################################################################
## GET COMMAND LINE ARGUMENTS
################################################################
parser = argparse.ArgumentParser(description="map")
parser.add_argument("--numTeamMembers")
parser.add_argument("--difficultyLevel")
parser.add_argument("--numStartingCards")
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

if args.numStartingCards is not None:
    numStartingCards = args.numStartingCards
    print('Setting up game with ' + str(numStartingCards) + ' cards per player.')
else:
    print('Defaulting to standard card counts (4 epidemic cards for 2 players, 3 for 3 players, and 2 for 4 players).')
    # Set the number of cards per team member count
    cardsPerTeamMember = {2:4, 3:3, 4:2}
    numStartingCards = cardsPerTeamMember[numTeamMembers]

def initializeGame(numTeamMembers, difficultyLevel, numStartingCards):
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
        placeDiseaseCubes(tmpCityIndex, 3, diseaseCubesPiles, cityDiseaseCubes, indexedCities, mapCityColorIndexed)

    # Draw next 3 infection cards 
    for iDRAW in range(3):
        # get the top card of infectionDeck, tmpCityIndex
        tmpCityIndex,infectionDeck = getTopCard(infectionDeck)
        # Add that card to the infection discard pile
        infectionDiscardDeck = np.append(infectionDiscardDeck,tmpCityIndex)
        # place 2 disease cubes on that city
        placeDiseaseCubes(tmpCityIndex, 2, diseaseCubesPiles, cityDiseaseCubes, indexedCities, mapCityColorIndexed)

    # Draw next 3 infection cards 
    for iDRAW in range(3):
        # get the top card of infectionDeck, tmpCityIndex
        tmpCityIndex,infectionDeck = getTopCard(infectionDeck)
        # Add that card to the infection discard pile
        infectionDiscardDeck = np.append(infectionDiscardDeck,tmpCityIndex)
        # place 1 disease cubes on that city
        placeDiseaseCubes(tmpCityIndex, 1, diseaseCubesPiles, cityDiseaseCubes, indexedCities, mapCityColorIndexed)

    ################################################################
    ## DEFINE THE PLAYER SEQUENCE AND INITIAL CARDS PER PLAYER
    ################################################################
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
    seqResearcher = 5 # 5 is not a valid sequence--placeholder for vectorization
    for iSeq in range(numTeamMembers):
    	if indexedRoles[teamSequence[iSeq]] == indexedRoles['Researcher']:
    		teamHasResearcher = True
    		seqResearcher = iSeq

    #     is any player the contingency planner?
    teamHasContingencyPlanner = False
    seqContingencyPlanner = 5 # 5 is not a valid sequence--placeholder for vectorization
    for iSeq in range(numTeamMembers):
        if indexedRoles[teamSequence[iSeq]] == indexedRoles['ContingencyPlanner']:
            teamHasContingencyPlanner = True
            seqContingencyPlanner = iSeq

    #     is any player the contingency planner?
    teamHasQuarantineSpecialist = False
    seqQuarantineSpecialist = 5 # 5 is not a valid sequence--placeholder for vectorization
    for iSeq in range(numTeamMembers):
        if indexedRoles[teamSequence[iSeq]] == indexedRoles['QuarantineSpecialist']:
            teamHasQuarantineSpecialist = True
            seqQuarantineSpecialist = iSeq

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
    for numCards in range(numStartingCards):
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

    contingencyPlannerEventsReplayed = np.zeros(54) > 0.5 # initialize all replayed cards as false
    contingencyPlannerReclaimedCard = 0

    print('infectionRate is: ' + str(infectionRate)) 
    print('infectionRateMarker set at: ' + str(infectionRateMarker)) 
    print('outbreakCount is: ' + str(outbreakCount)) 
    print('teamSequence is: ' + str(teamSequence))

    indexedDiseaseColors = {0: 'blue', 1:'yellow', 2:'black', 3:'red'}
    diseaseCures = np.zeros((4,1))
    diseaseEradications = np.zeros((4,1))
    gameFinished = False
    oneQuietNight = False
    forecast = False
    blueEradicated = False
    yellowEradicated = False
    blackEradicated = False
    redEradicated = False

    # Track which player is currently choosing actions
    playerCurrentTurn = 0
    numActionsPerTeamMember = 4

    # Quarantine cities near quarantine specialist
    quarantinedCities = np.zeros((49))
    if teamHasQuarantineSpecialist:
        quarantineSpecialistCity = np.where(teamMemberCities.T[seqQuarantineSpecialist])[0]
        quarantinedCities[quarantineSpecialistCity] = True
        quarantineCityIndexList = np.where(mapAdj[quarantineSpecialistCity-1][0])[0] + 1
        for iQC in quarantineCityIndexList:
            quarantinedCities[iQC] = True

    actionTypes = {'passTurn':1,'move':2, 'directFlight':3, 'charterFlight':4, 'shuttle':5, 'treat':6, 'build':7, 'cure':8, 'give':9, 'take':10, 'remove':11, 'airlift':12,'governmentGrant':13,'oneQuietNight':14,'resilientPopulation':15,'forecast':16,'reclaim':17,'discard':18,'drawPlayerCards':19,'infect':20}
    indexedActions = dict((v,k) for k,v in actionTypes.iteritems())

    # Iniitalize end game states
    playerCardsExhausted = False
    infectionDeckExhausted = False
    allDiseasesCured = False
    eightOrMoreOutbreaks = False
    diseaseCubesExhausted = False

    # INITIALIZE state/action STATE
    numGameStates = 0
    numActionTransitions = 0

    # Store the beginning game state
    # SHOULD USE copy.deepcopy() IN THE FUTURE... NOT TESTED
    instantStateVector0 = {'playerCurrentTurn': playerCurrentTurn, \
        'teamSequence': teamSequence,\
        'teamHasResearcher': teamHasResearcher,\
        'seqResearcher': seqResearcher,\
        'teamHasContingencyPlanner': teamHasContingencyPlanner,\
        'teamHasQuarantineSpecialist': teamHasQuarantineSpecialist,\
        'quarantinedCities': quarantinedCities,\
        'playerCardDeck': playerCardDeck,\
        'playerCardsSeen': playerCardsSeen,\
        'playerCardsHeld': playerCardsHeld, \
        'playerCardsNotSeen': playerCardsNotSeen, \
        'playerCardsRemoved': playerCardsRemoved, \
        'contingencyPlannerEventsReplayed': contingencyPlannerEventsReplayed, \
        'contingencyPlannerReclaimedCard': contingencyPlannerReclaimedCard, \
        'infectionDeck': infectionDeck, \
        'infectionDiscardDeck': infectionDiscardDeck, \
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
        'diseaseEradications': diseaseEradications, \
        'diseaseCubesPiles': diseaseCubesPiles, \
        'oneQuietNight': oneQuietNight, \
        'forecast': forecast, \
        'blueEradicated': blueEradicated, \
        'yellowEradicated': yellowEradicated, \
        'blackEradicated': blackEradicated, \
        'redEradicated': redEradicated, \
        'numGameStates': numGameStates, \
        'numActionTransitions': numActionTransitions, \
        'playerCardsExhausted': playerCardsExhausted, \
        'infectionDeckExhausted': infectionDeckExhausted, \
        'allDiseasesCured': allDiseasesCured, \
        'eightOrMoreOutbreaks': eightOrMoreOutbreaks, \
        'diseaseCubesExhausted': diseaseCubesExhausted, \
        'gameFinished': gameFinished}

    instantStateVector = copy.deepcopy(instantStateVector0)

    gameMechanics = {'cityNames' : cityNames ,\
        'indexedCities' : indexedCities, \
        'numCities' : numCities, \
        'numActionsPerTeamMember' : numActionsPerTeamMember, \
        'mapAdj' : mapAdj, \
        'mapXYs' : mapXYs, \
        'mapColors' : mapColors, \
        'mapHexColors' : mapHexColors, \
        'mapCityNames' : mapCityNames, \
        'mapCityColorIndexed' : mapCityColorIndexed, \
        'diseaseColorIndex' : diseaseColorIndex, \
        'indexedDiseaseColors' : indexedDiseaseColors, \
        'diseaseIndexes' : diseaseIndexes, \
        'teamRoles' : teamRoles, \
        'indexedRoles' : indexedRoles, \
        'teamColors' : teamColors, \
        'eventCardNames' : eventCardNames, \
        'indexedEventCards' : indexedEventCards, \
        'eventCardMask' : eventCardMask, \
        'diseaseStates' : diseaseStates, \
        'diseaseCureMarkers' : diseaseCureMarkers, \
        'infectionRates' : infectionRates, \
        'allPlayerCards' : allPlayerCards, \
        'indexedActionEventPlayerCards' : indexedActionEventPlayerCards, \
        'numTeamMembers' : numTeamMembers, \
        'printcolors' : printcolors, \
        'actionTypes' : actionTypes, \
        'indexedActions' : indexedActions}

    return instantStateVector0, instantStateVector, gameMechanics