import numpy as np
import matplotlib.pyplot as plt

import itertools
from random import shuffle
from random import randint

import csv
import copy

from computeAvailableActions import computeAvailableActions
from rewards import *

################################################################
## INITIALIZE GAME
################################################################
def initializeGame(numTeamMembers, difficultyLevel, numStartingCards, debugLevel):
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
        placeDiseaseCubes(tmpCityIndex, 3, diseaseCubesPiles, cityDiseaseCubes, indexedCities, mapCityColorIndexed, debugLevel)

    # Draw next 3 infection cards 
    for iDRAW in range(3):
        # get the top card of infectionDeck, tmpCityIndex
        tmpCityIndex,infectionDeck = getTopCard(infectionDeck)
        # Add that card to the infection discard pile
        infectionDiscardDeck = np.append(infectionDiscardDeck,tmpCityIndex)
        # place 2 disease cubes on that city
        placeDiseaseCubes(tmpCityIndex, 2, diseaseCubesPiles, cityDiseaseCubes, indexedCities, mapCityColorIndexed, debugLevel)

    # Draw next 3 infection cards 
    for iDRAW in range(3):
        # get the top card of infectionDeck, tmpCityIndex
        tmpCityIndex,infectionDeck = getTopCard(infectionDeck)
        # Add that card to the infection discard pile
        infectionDiscardDeck = np.append(infectionDiscardDeck,tmpCityIndex)
        # place 1 disease cubes on that city
        placeDiseaseCubes(tmpCityIndex, 1, diseaseCubesPiles, cityDiseaseCubes, indexedCities, mapCityColorIndexed, debugLevel)

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
    if (debugLevel >= 2):
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

    iTurnSeq = 0
    gameMechanicsSeqList = ['action1','action2','action3','action4','drawPlayerCards','forecast','discard','infectCities']
    nextMechanicsSeqDict = {'action1':'action2','action2':'action3','action3':'action4','action4':'drawPlayerCards','drawPlayerCards':'forecast','forecast':'discard','discard':'infectCities','infectCities':'action1'}

    gameMechanicsSeqsDict = {'action1':1, 'action2':2, 'action3':3, 'action4':4, 'drawPlayerCards':5, 'forecast':6, 'discard':7, 'infectCities':8}
    indexedGameMechanicsSeqs = {1:'action1', 2:'action2', 3:'action3', 4:'action4', 5:'drawPlayerCards', 6:'forecast', 7:'discard', 8:'infectCities'}

    mechanicsSeq = gameMechanicsSeqsDict['action1']

    forecastTypes = {'simpleForecast':0, 'randomForecast':1}
    indexedForecastTypes = dict((v,k) for k,v in forecastTypes.iteritems())

    forecastType = 0
    playForecastOnEpidemic = True

    playerActionTypes = ['airlift', 'build', 'charterFlight', 'cure', 'directFlight', 'forecast', 'give', 'governmentGrant', 'move', 'oneQuietNight', 'passTurn', 'reclaim', 'remove', 'resilientPopulation', 'shuttle', 'take', 'treat']

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
        'gameFinished': gameFinished, \
        'iTurnSeq': iTurnSeq, \
        'mechanicsSeq': mechanicsSeq, \
        'forecastType': forecastType, \
        'playForecastOnEpidemic': playForecastOnEpidemic}

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
        'indexedActions' : indexedActions, \
        'gameMechanicsSeqsDict' : gameMechanicsSeqsDict, \
        'gameMechanicsSeqList' : gameMechanicsSeqList, \
        'nextMechanicsSeqDict' : nextMechanicsSeqDict, \
        'indexedGameMechanicsSeqs' : indexedGameMechanicsSeqs, \
        'forecastTypes': forecastTypes, \
        'indexedForecastTypes': indexedForecastTypes, \
        'playerActionTypes': playerActionTypes, \
        'debugLevel': debugLevel}

    return instantStateVector0, instantStateVector, gameMechanics

################################################################
## SHOW STATE (instantStateVector)
################################################################
def vizBoard(boardViz,isv,gm):
    if boardViz:
        # SHOW MAP
        showMap(isv, gm)
        plt.draw()
        raw_input("Press Enter to continue...")

def showMap(isv, gm):
    # Show map
    plt.close("all")
    fig = plt.figure()
    fig.set_size_inches(26.4, 19.0)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    im = plt.imread("pandemicMap.jpg")
    implot = plt.imshow(im)
    for k in gm['indexedCities'].keys():
        # Plot all cities with circles
        plt.scatter(x=[gm['mapXYs'][k-1][1]], y=[gm['mapXYs'][k-1][2]], c=gm['mapHexColors'][k], s=300, alpha=0.5)
        # Name all cities
        t=plt.text(gm['mapXYs'][k-1][1]-15, gm['mapXYs'][k-1][2]-25, gm['mapCityNames'][k], color=gm['mapHexColors'][k])
        t.set_bbox(dict(facecolor='#bbbbbb', alpha=0.9, edgecolor='white'))
    # Plot all city connections
    cityConns = np.transpose(np.where(gm['mapAdj'])) + 1
    for cci in np.arange(0,len(cityConns)):
        connXY = gm['mapXYs'][cityConns[cci]-1]
        plt.plot(connXY[:,1],connXY[:,2],'k',linewidth=5)
    # Plot all cubes (from instant state vector)
    isvblue = isv['blueCubesByCity']
    for ic in range(len(isvblue)):
        if isvblue[ic] > 0:
            nC = int(isvblue[ic])
            xyC = gm['mapXYs'][gm['mapXYs'][:,0]==ic,1:3][0]
            plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='^', c='blue', s=1500, alpha=0.5, edgecolor='white', linewidth='2')
        if isvblue[ic] > 1:
            plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='^', c='blue', s=3000, alpha=0.7, edgecolor='white', linewidth='4')
        if isvblue[ic] > 2:
            plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='^', c='blue', s=4500, alpha=0.9, edgecolor='white', linewidth='7')
    isvyellow = isv['yellowCubesByCity']
    for ic in range(len(isvyellow)):
        if isvyellow[ic] > 0:
            nC = int(isvyellow[ic])
            xyC = gm['mapXYs'][gm['mapXYs'][:,0]==ic,1:3][0]
            plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='>', c='yellow', s=1500, alpha=0.5, edgecolor='white', linewidth='2')
        if isvyellow[ic] > 1:
            plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='>', c='yellow', s=3000, alpha=0.7, edgecolor='white', linewidth='4')
        if isvyellow[ic] > 2:
            plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='>', c='yellow', s=4500, alpha=0.9, edgecolor='white', linewidth='7')
    isvblack = isv['blackCubesByCity']
    for ic in range(len(isvblack)):
        if isvblack[ic] > 0:
            nC = int(isvblack[ic])
            xyC = gm['mapXYs'][gm['mapXYs'][:,0]==ic,1:3][0]
            plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='v', c='black', s=1500, alpha=0.5, edgecolor='white', linewidth='2')
        if isvblack[ic] > 1:
            plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='v', c='black', s=3000, alpha=0.7, edgecolor='white', linewidth='4')
        if isvblack[ic] > 2:
            plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='v', c='black', s=4500, alpha=0.9, edgecolor='white', linewidth='7')
    isvred = isv['redCubesByCity']
    for ic in range(len(isvred)):
        if isvred[ic] > 0:
            nC = int(isvred[ic])
            xyC = gm['mapXYs'][gm['mapXYs'][:,0]==ic,1:3][0]
            plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='<', c='red', s=1500, alpha=0.5, edgecolor='white', linewidth='2')
        if isvred[ic] > 1:
            plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='<', c='red', s=3000, alpha=0.7, edgecolor='white', linewidth='4')
        if isvred[ic] > 2:
            plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='<', c='red', s=4500, alpha=0.9, edgecolor='white', linewidth='7')
    # Plot all player locations (from instant state vector)
    teamLocs = np.fliplr(np.transpose(np.where(np.transpose(isv['teamMemberCities']))))
    playerThetaOffs = 3.0*np.pi/4.0
    dTheta = 2*np.pi / gm['numTeamMembers']
    rPlayer = 12 # radius offset of player token from center of city
    for teami in range(gm['numTeamMembers']):
        thetaOffs = playerThetaOffs + teami*dTheta
        xyOffs = np.array([rPlayer*np.cos(thetaOffs),rPlayer*np.sin(thetaOffs)])
        xyTm = gm['mapXYs'][gm['mapXYs'][:,0]==teamLocs[teami][0],1:3][0]
        # Plot all team members with colored circles
        plt.scatter(x=[xyTm[0]+xyOffs[0]], y=[xyTm[1]+xyOffs[1]], c=gm['teamColors'][isv['teamSequence'][teami]], s=500, alpha=0.9, edgecolor='white')
    # SHOW RESEARCH FACILITIES
    researchFacilityCities = np.where(isv['researchFacilitiesByCity'])[0]
    for iRF in researchFacilityCities:
        plt.scatter(x=[gm['mapXYs'][iRF-1][1]], y=[gm['mapXYs'][iRF-1][2]], marker='s', facecolors='none', s=6000, alpha=0.9, edgecolors='white', linewidth='4')
    plt.show()
    fig.savefig('pandemicInit.png', dpi=100)

################################################################
## DEFINE SOME DECK AND DISEASE CUBES HELPER FUNCTIONS
################################################################
def getTopCard(deck):
    topCard = deck[0]
    # Remove that card from the deck
    deck = np.delete(deck, 0)
    return topCard, deck

def getBottomCard(deck):
    bottomCard = deck[-1]
    # Remove that card from the deck
    deck = np.delete(deck, -1)
    return bottomCard, deck

def decrementDiseasePile(diseaseCubesPiles, color2decrement):
    diseaseCubesPiles[color2decrement] = diseaseCubesPiles[color2decrement] - 1
    return diseaseCubesPiles

def incrementDiseasePile(diseaseCubesPiles, color2decrement):
    diseaseCubesPiles[color2increment] = diseaseCubesPiles[color2increment] + 1
    return diseaseCubesPiles

def decrementInitialCityDisease(cityDiseaseCubes, cityIndex, color2decrement):
    cityDiseaseCubes[cityIndex][color2decrement] = cityDiseaseCubes[cityIndex][color2decrement] - 1
    return cityDiseaseCubes

def incrementInitialCityDisease(cityDiseaseCubes, cityIndex, color2increment):
    cityDiseaseCubes[cityIndex][color2increment] = cityDiseaseCubes[cityIndex][color2increment] + 1
    return cityDiseaseCubes

def incrementCityDisease(cityDiseaseCubes, cityIndex, numCubes):
    cityDiseaseCubes[cityIndex] = cityDiseaseCubes[cityIndex] + numCubes
    return cityDiseaseCubes

def placeDiseaseCubes(cityIndex, numCubes, diseaseCubesPiles, cityDiseaseCubes, indexedCities, mapCityColorIndexed, debugLevel=5):
    # Determine color of cityIndex
    placeColor = mapCityColorIndexed[cityIndex]
    if (debugLevel >= 2):
        print('Placing ' + str(numCubes) + ' ' + placeColor + ' cubes on ' + indexedCities[cityIndex] + '.')
    for iCUBES in range(numCubes):
        # remove cube from diseaseCubesPiles
        decrementDiseasePile(diseaseCubesPiles, placeColor)
        incrementInitialCityDisease(cityDiseaseCubes, cityIndex, placeColor) 
        if cityDiseaseCubes[cityIndex][placeColor] > 3:
            if (debugLevel >= 1):
                print("Outbreak at " + str(cityIndex) + "," + indexedCities[cityIndex] + " not implemented.")
                print("Outbreaks impossible on board setup.")

def infectCity(cityIndex, isv, gm):
    numCubes = 1
    # Determine color of cityIndex
    placeColor = gm['mapCityColorIndexed'][cityIndex]
    # DO NOT INFECT ANY QUARANTINED CITIES
    if ( isv['quarantinedCities'][cityIndex] < 1.0 ):
        if (gm['debugLevel'] >= 3):
            print('Placing ' + str(numCubes) + ' ' + placeColor + ' cube on ' + gm['indexedCities'][cityIndex] + '.')
        for iCUBES in range(numCubes):
            decrementDiseasePile(isv['diseaseCubesPiles'], placeColor)
            # remove cube from diseaseCubesPiles
            if ( placeColor == 'blue'):
                incrementCityDisease(isv['blueCubesByCity'], cityIndex, numCubes)
            elif ( placeColor == 'yellow'):
                incrementCityDisease(isv['yellowCubesByCity'], cityIndex, numCubes)
            elif ( placeColor == 'black'):
                incrementCityDisease(isv['blackCubesByCity'], cityIndex, numCubes)
            else:
                incrementCityDisease(isv['redCubesByCity'], cityIndex, numCubes)
    else:
        quarantineSpecialistCity = np.where(isv['teamMemberCities'].T[isv['teamSequence'].index('QuarantineSpecialist')])[0][0]
        if (gm['debugLevel'] >= 3):
            print('Not placing ' + str(numCubes) + ' ' + placeColor + ' cube on quarantined ' + gm['indexedCities'][cityIndex] + ' (QS@' + gm['indexedCities'][quarantineSpecialistCity] + ').')
    return isv

def intensify(isv):
    np.random.shuffle(isv['infectionDiscardDeck'])
    isv['infectionDeck']=np.concatenate((isv['infectionDiscardDeck'],isv['infectionDeck']))
    isv['infectionDiscardDeck'] = np.array([],'int')
    return isv

def visitEpidemicOnCity(cityIndex, isv, gm):
    numCubes = 3
    # Determine color of cityIndex
    placeColor = gm['mapCityColorIndexed'][cityIndex]
    # DO NOT VISIT EPIDEMIC ON ANY QUARANTINED CITIES
    if ( isv['quarantinedCities'][cityIndex] < 1.0 ):
        if (gm['debugLevel'] >= 3):
            print('Placing ' + str(numCubes) + ' ' + placeColor + ' cubes on ' + gm['indexedCities'][cityIndex] + '.')
        # remove 3 cubes from diseaseCubesPiles
        decrementDiseasePile(isv['diseaseCubesPiles'], placeColor)
        decrementDiseasePile(isv['diseaseCubesPiles'], placeColor)
        decrementDiseasePile(isv['diseaseCubesPiles'], placeColor)
        if ( placeColor == 'blue'):
            incrementCityDisease(isv['blueCubesByCity'], cityIndex, numCubes)
        elif ( placeColor == 'yellow'):
            incrementCityDisease(isv['yellowCubesByCity'], cityIndex, numCubes)
        elif ( placeColor == 'black'):
            incrementCityDisease(isv['blackCubesByCity'], cityIndex, numCubes)
        else:
            incrementCityDisease(isv['redCubesByCity'], cityIndex, numCubes)
    else:
        quarantineSpecialistCity = np.where(isv['teamMemberCities'].T[isv['teamSequence'].index('QuarantineSpecialist')])[0][0]
        if (gm['debugLevel'] >= 3):
            print('Not visiting epidemic of ' + str(numCubes) + ' ' + placeColor + ' cubes on quarantined ' + gm['indexedCities'][cityIndex] + ' (QS@' + gm['indexedCities'][quarantineSpecialistCity] + ').')        
    return isv

def resolveOutbreak(isv, gm, outbrokenCities):
    # outbrokenCities is a list of cities to exclude because they have already had an outbreak during resolution of the current outbreak
    outbreakCity = np.where( ~( outbrokenCities ) & ( ( isv['blueCubesByCity'] > 3 ) | ( isv['yellowCubesByCity'] > 3 ) | ( isv['blackCubesByCity'] > 3 ) | ( isv['redCubesByCity'] > 3 ) ) )[0]
    if ( outbreakCity.shape[0] > 1 ):
        if (gm['debugLevel'] >= 1):
            print('TOO MANY OUTBREAKS')
            for iOC in outbreakCity:
                print('Outbreak found in: ' + gm['indexedCities'][iOC] + '(' + str(iOC) + ')' )
    elif ( outbreakCity.shape[0] < 1 ):
        # print('WARNING! TOO FEW OUTBREAKS... reset revisited outbrokenCities')
        revisitedOutbrokenCities = np.where( ( outbrokenCities ) & ( ( isv['blueCubesByCity'] > 3 ) | ( isv['yellowCubesByCity'] > 3 ) | ( isv['blackCubesByCity'] > 3 ) | ( isv['redCubesByCity'] > 3 ) ) )[0]
        if ( revisitedOutbrokenCities.shape[0] > 0 ):
            for iROBC in revisitedOutbrokenCities:
                outbreakColor = gm['mapCityColorIndexed'][iROBC]
                # print('Resetting revisitedOutbrokenCities: ' + str(gm['indexedCities'][iROBC]) + '(' + str(iROBC) + ') to 3 ' + outbreakColor + ' cubes')
                if ( outbreakColor == 'blue'):
                    isv['blueCubesByCity'][iROBC] = 3
                elif ( outbreakColor == 'yellow'):
                    isv['yellowCubesByCity'][iROBC] = 3
                elif ( outbreakColor == 'black'):
                    isv['blackCubesByCity'][iROBC] = 3
                else:
                    isv['redCubesByCity'][iROBC] = 3
    elif ( outbreakCity.shape[0]==1 ):
        if (gm['debugLevel'] >= 3):
            print('Outbreak developing at : ' + str(gm['indexedCities'][outbreakCity[0]]) + '(' + str(outbreakCity[0]) + ')' )
        outbreakColor = gm['mapCityColorIndexed'][outbreakCity[0]]
        if ( isv['quarantinedCities'][outbreakCity[0]] < 0.5 ):
            if ( outbreakColor == 'blue'):
                isv['blueCubesByCity'][outbreakCity[0]] = 3
            elif ( outbreakColor == 'yellow'):
                isv['yellowCubesByCity'][outbreakCity[0]] = 3
            elif ( outbreakColor == 'black'):
                isv['blackCubesByCity'][outbreakCity[0]] = 3
            else:
                isv['redCubesByCity'][outbreakCity[0]] = 3
            isv['outbreakCount'] = isv['outbreakCount'] + 1
            outbrokenCities[outbreakCity[0]] = True  # mark the original outbreak city as outbroken before spreading
            if (gm['debugLevel'] >= 3):
                print('Spreading ' + outbreakColor + ' outbreak from ' + gm['indexedCities'][outbreakCity[0]] + '(' + str(outbreakCity[0]) + ') to neighboring cities... ')
            #for iOBC in np.where( outbrokenCities )[0]:
            #    print('Outbroken cities prior to spreading include ' + gm['indexedCities'][iOBC] + '(' + str(iOBC) + ')' )
            isv, outbrokenCities = spreadOutbreak(isv, gm, outbrokenCities, outbreakColor, outbreakCity)
        else:
            quarantineSpecialistCity = np.where(isv['teamMemberCities'].T[isv['teamSequence'].index('QuarantineSpecialist')])[0][0]
            if (gm['debugLevel'] >= 3):
                print('Outbreak quarantined at ' + gm['indexedCities'][cityIndex] + ' (QS@' + gm['indexedCities'][quarantineSpecialistCity] + ').')
    return isv

def spreadOutbreak(isv, gm, outbrokenCities, outbreakColor, outbreakCity):
    spreadToCities = np.where(gm['mapAdj'][outbreakCity[0]-1])[0] + 1
    # REMOVE OUTBROKEN CITIES FROM spreadToCities
    spreadToCities = np.array(list(set(spreadToCities) - set(np.where(outbrokenCities)[0])))
    # REMOVE QUARANTINED CITIES FROM spreadToCities
    spreadToCities = np.array(list(set(spreadToCities) - set(np.where(isv['quarantinedCities'])[0])))
    for iSTC in spreadToCities:
        if ( outbreakColor == 'blue'):
            if (gm['debugLevel'] >= 3):
                print('Adding a blue cube to: ' + gm['indexedCities'][iSTC] + '(' + str(iSTC) + ')' )
            isv['blueCubesByCity'][iSTC] = isv['blueCubesByCity'][iSTC] + 1
            if ( isv['blueCubesByCity'][iSTC] > 3 ):
                if (gm['debugLevel'] >= 3):
                    print(gm['indexedCities'][iSTC] + '(' + str(iSTC) + ') has ' + str(int(isv['blueCubesByCity'][iSTC][0])) + ' blue cubes...resolving its outbreak... ' )
                isv = resolveOutbreak(isv, gm, outbrokenCities)
        elif ( outbreakColor == 'yellow'):
            if (gm['debugLevel'] >= 3):
                print('Adding a yellow cube to: ' + gm['indexedCities'][iSTC] + '(' + str(iSTC) + ')' )
            isv['yellowCubesByCity'][iSTC] = isv['yellowCubesByCity'][iSTC] + 1
            if ( isv['yellowCubesByCity'][iSTC] > 3 ):
                if (gm['debugLevel'] >= 3):
                    print(gm['indexedCities'][iSTC] + '(' + str(iSTC) + ') has ' + str(int(isv['yellowCubesByCity'][iSTC][0])) + ' yellow cubes...resolving its outbreak... ' )
                isv = resolveOutbreak(isv, gm, outbrokenCities)
        elif ( outbreakColor == 'black'):
            if (gm['debugLevel'] >= 3):
                print('Adding a black cube to: ' + gm['indexedCities'][iSTC] + '(' + str(iSTC) + ')' )
            isv['blackCubesByCity'][iSTC] = isv['blackCubesByCity'][iSTC] + 1
            if ( isv['blackCubesByCity'][iSTC] > 3 ):
                if (gm['debugLevel'] >= 3):
                    print(gm['indexedCities'][iSTC] + '(' + str(iSTC) + ') has ' + str(int(isv['blackCubesByCity'][iSTC][0])) + ' black cubes...resolving its outbreak... ' )
                isv = resolveOutbreak(isv, gm, outbrokenCities)
        else:
            if (gm['debugLevel'] >= 3):
                print('Adding a red cube to: ' + gm['indexedCities'][iSTC] + '(' + str(iSTC) + ')' )
            isv['redCubesByCity'][iSTC] = isv['redCubesByCity'][iSTC] + 1
            if ( isv['redCubesByCity'][iSTC] > 3 ):
                if (gm['debugLevel'] >= 3):
                    print(gm['indexedCities'][iSTC] + '(' + str(iSTC) + ') has ' + str(int(isv['redCubesByCity'][iSTC][0])) + ' red cubes...resolving its outbreak... ' )
                isv = resolveOutbreak(isv, gm, outbrokenCities)
    return isv, outbrokenCities

# listActionEventMechanics only used in emulatePandemic.py
def listActionEventMechanics(isv,gm):
    actionEvents = computeAvailableActions(isv, gm)
    showActionOptions(actionEvents, isv, gm)
    return actionEvents

# chooseActionEventMechanics only used in emulatePandemic.py
def chooseActionEventMechanics(actionEvents, debugLevel=5):
    randomActIndex = randint(0,len(actionEvents['actionEventList'])-1)
    a = actionEvents['actionEventList'][randomActIndex]
    if (debugLevel >= 2):
        print('Executing ' + str(randomActIndex) + ': ' + a[1][0])
    return a

def executeActionEventMechanics(isv,gm,a):
    isv, actionCost = updateGameWithActionEvent(a, isv, gm)
    isv = updateEradications(isv, gm)
    return isv,a,actionCost

def showActionOptions(actionEvents,isv,gm):
    printcolors = gm['printcolors']
    pCHeld = np.transpose(isv['playerCardsHeld'])[isv['playerCurrentTurn']]
    playerStr = isv['teamSequence'][isv['playerCurrentTurn']] + '(' + str(isv['playerCurrentTurn']) + ')'
    if (gm['debugLevel'] >= 3):
        print( playerStr + ' holds cards: ' )
        print('------------------------------------')
    for iCH in np.where(pCHeld)[0]:
        if ( gm['indexedActionEventPlayerCards'][iCH] == 'Action' ):
            if gm['indexedDiseaseColors'][gm['diseaseIndexes'][iCH]] == 'blue':
                if (gm['debugLevel'] >= 3):
                    print printcolors.BLUE + gm['indexedActionEventPlayerCards'][iCH] + ': (' + gm['allPlayerCards'][iCH] + '-' + gm['indexedDiseaseColors'][gm['diseaseIndexes'][iCH]] + ')' + printcolors.ENDC
            if gm['indexedDiseaseColors'][gm['diseaseIndexes'][iCH]] == 'yellow':
                if (gm['debugLevel'] >= 3):
                    print printcolors.YELLOW + gm['indexedActionEventPlayerCards'][iCH] + ': (' + gm['allPlayerCards'][iCH] + '-' + gm['indexedDiseaseColors'][gm['diseaseIndexes'][iCH]] + ')' + printcolors.ENDC
            if gm['indexedDiseaseColors'][gm['diseaseIndexes'][iCH]] == 'black':
                if (gm['debugLevel'] >= 3):
                    print printcolors.GRAY + gm['indexedActionEventPlayerCards'][iCH] + ': (' + gm['allPlayerCards'][iCH] + '-' + gm['indexedDiseaseColors'][gm['diseaseIndexes'][iCH]] + ')' + printcolors.ENDC
            if gm['indexedDiseaseColors'][gm['diseaseIndexes'][iCH]] == 'red':
                if (gm['debugLevel'] >= 3):
                    print printcolors.RED + gm['indexedActionEventPlayerCards'][iCH] + ': (' + gm['allPlayerCards'][iCH] + '-' + gm['indexedDiseaseColors'][gm['diseaseIndexes'][iCH]] + ')' + printcolors.ENDC
        else:
            if (gm['debugLevel'] >= 3):
                print(gm['indexedActionEventPlayerCards'][iCH] + ': (' + gm['allPlayerCards'][iCH] + ')' )
    if (gm['debugLevel'] >= 3):
        print('====================================')
    for iAEC in actionEvents['actionEventList']:
        if (gm['debugLevel'] >= 3):
            print( str(iAEC[0]) + ": " + iAEC[1][0] )

# UPDATE GAME STATE WITH ACTION
def move(moveAdjacentAction, isv):
    currentCityIndex = moveAdjacentAction[2]
    destinationCityIndex = moveAdjacentAction[3]
    isvTMC=isv['teamMemberCities']
    np.transpose(isvTMC)[isv['playerCurrentTurn']][currentCityIndex] = 0
    np.transpose(isvTMC)[isv['playerCurrentTurn']][destinationCityIndex] = 1
    isv['teamMemberCities'] = isvTMC
    return isv

def directFlight(directFlightAction, isv):
    currentCityIndex = directFlightAction[2]
    destinationCityIndex = directFlightAction[3]
    isvTMC=isv['teamMemberCities']
    np.transpose(isvTMC)[isv['playerCurrentTurn']][currentCityIndex] = 0
    np.transpose(isvTMC)[isv['playerCurrentTurn']][destinationCityIndex] = 1
    isv['teamMemberCities'] = isvTMC
    # remove destinationCityCard from player hand to playerDiscardPile
    np.transpose(isv['playerCardsHeld'])[isv['playerCurrentTurn']][destinationCityIndex] = False
    isv['playerCardsRemoved'][destinationCityIndex] = True
    return isv

def charterFlight(charterFlightAction, isv):
    currentCityIndex = charterFlightAction[2]
    destinationCityIndex = charterFlightAction[3]
    isvTMC=isv['teamMemberCities']
    np.transpose(isvTMC)[isv['playerCurrentTurn']][currentCityIndex] = 0
    np.transpose(isvTMC)[isv['playerCurrentTurn']][destinationCityIndex] = 1
    isv['teamMemberCities'] = isvTMC
    # remove currentCityCard from player hand to playerDiscardPile
    np.transpose(isv['playerCardsHeld'])[isv['playerCurrentTurn']][currentCityIndex] = False
    isv['playerCardsRemoved'][currentCityIndex] = True
    return isv

def shuttle(shuttleFlightAction, isv):
    currentCityIndex = shuttleFlightAction[2]
    destinationCityIndex = shuttleFlightAction[3]
    isvTMC=isv['teamMemberCities']
    np.transpose(isvTMC)[isv['playerCurrentTurn']][currentCityIndex] = 0
    np.transpose(isvTMC)[isv['playerCurrentTurn']][destinationCityIndex] = 1
    isv['teamMemberCities'] = isvTMC
    return isv

def treat(treatAction, isv, gm):
    cityToTreatDisease = treatAction[2]
    diseaseIndexToTreat = treatAction[3]
    if ( isv['diseaseEradications'][diseaseIndexToTreat][0] > 0 ) | ( gm['indexedRoles'][isv['teamSequence'][isv['playerCurrentTurn']]] == gm['indexedRoles']['Medic'] ):
        # TREAT ALL CUBES OF 
        if (gm['debugLevel'] >= 3):
            print('removing all cubes')
        if ( gm['indexedDiseaseColors'][diseaseIndexToTreat] == 'blue' ):
            isv['blueCubesByCity'][cityToTreatDisease] = 0
        elif ( gm['indexedDiseaseColors'][diseaseIndexToTreat] == 'yellow' ):
            isv['yellowCubesByCity'][cityToTreatDisease] = 0
        elif ( gm['indexedDiseaseColors'][diseaseIndexToTreat] == 'black' ):
            isv['blackCubesByCity'][cityToTreatDisease] = 0
        elif ( gm['indexedDiseaseColors'][diseaseIndexToTreat] == 'red' ):
            isv['redCubesByCity'][cityToTreatDisease] = 0
        else:
            if (gm['debugLevel'] >= 1):
                print('Disease index not recognized')
    else:
        if (gm['debugLevel'] >= 3):
            print('removing one cube')
        if ( gm['indexedDiseaseColors'][diseaseIndexToTreat] == 'blue' ):
            isv['blueCubesByCity'][cityToTreatDisease] = isv['blueCubesByCity'][cityToTreatDisease] - 1
        elif ( gm['indexedDiseaseColors'][diseaseIndexToTreat] == 'yellow' ):
            isv['yellowCubesByCity'][cityToTreatDisease] = isv['yellowCubesByCity'][cityToTreatDisease] - 1
        elif ( gm['indexedDiseaseColors'][diseaseIndexToTreat] == 'black' ):
            isv['blackCubesByCity'][cityToTreatDisease] = isv['blackCubesByCity'][cityToTreatDisease] - 1
        elif ( gm['indexedDiseaseColors'][diseaseIndexToTreat] == 'red' ):
            isv['redCubesByCity'][cityToTreatDisease] = isv['redCubesByCity'][cityToTreatDisease] - 1
        else:
            if (gm['debugLevel'] >= 1):
                print('Disease index not recognized')
    return isv

def build(buildAction, isv):
    cityToBuildResearchFacility = buildAction[2]
    cardForResearchFacility = buildAction[3]
    np.transpose(isv['playerCardsHeld'])[isv['playerCurrentTurn']][cardForResearchFacility] = False
    isv['playerCardsRemoved'][cardForResearchFacility] = True
    isv['researchFacilitiesByCity'][cityToBuildResearchFacility] = True
    return isv

def cure(cureAction, isv):
    cureColorIndex = cureAction[2]
    cardsToCure = cureAction[3]
    nToCure = cureAction[4]
    for iCC in cardsToCure:
        np.transpose(isv['playerCardsHeld'])[isv['playerCurrentTurn']][iCC] = False
        isv['playerCardsRemoved'][iCC] = True
    isv['diseaseCures'][cureColorIndex] = 1.0
    return isv

def give(giveCardAction, isv):
    playerToGiveTo = giveCardAction[2]
    cityCardToGive = giveCardAction[3]
    np.transpose(isv['playerCardsHeld'])[isv['playerCurrentTurn']][cityCardToGive] = False
    np.transpose(isv['playerCardsHeld'])[playerToGiveTo][cityCardToGive] = True
    return isv

def take(takeCardAction, isv):
    playerToTakeCardFrom = takeCardAction[2]
    cityCardToTake = takeCardAction[3]
    np.transpose(isv['playerCardsHeld'])[playerToTakeCardFrom][cityCardToTake] = False
    np.transpose(isv['playerCardsHeld'])[isv['playerCurrentTurn']][cityCardToTake] = True
    return isv

def passTurn(passAction, isv, debugLevel=5):
    if (debugLevel >= 3):
        print("Passing action.")
    return isv

def reclaim(reclaimAction, isv, debugLevel=5):
    if (debugLevel >= 3):
        print("Reclaiming action.")
    isv['contingencyPlannerReclaimedCard'] = reclaimAction[2]
    return isv

def airlift(airliftEvent, isv, gm):
    # NOTE: THIS CURRENTLY ONLY IMPLEMENTS MOVING THE CURRENT PLAYER TO ANY CITY
    currentCityIndex = airliftEvent[2]
    destinationCityIndex = airliftEvent[3]
    isvTMC=isv['teamMemberCities']
    np.transpose(isvTMC)[isv['playerCurrentTurn']][currentCityIndex] = 0
    np.transpose(isvTMC)[isv['playerCurrentTurn']][destinationCityIndex] = 1
    isv['teamMemberCities'] = isvTMC
    # remove airlift event card from player hand to eventDiscardPile (this removes from all hands)
    isv['playerCardsHeld'][gm['eventCardNames']['Airlift']] = False
    isv['playerCardsRemoved'][gm['eventCardNames']['Airlift']] = True
    return isv

def governmentGrant(governmentGrantEvent, isv, gm):
    cityToBuildResearchFacility = governmentGrantEvent[2]
    isv['researchFacilitiesByCity'][cityToBuildResearchFacility] = True
    # remove government grant event card from player hand to eventDiscardPile (this removes from all hands)
    isv['playerCardsHeld'][gm['eventCardNames']['GovernmentGrant']] = False
    isv['playerCardsRemoved'][gm['eventCardNames']['GovernmentGrant']] = True
    return isv

def resilientPopulation(resilientPopulationEvent, isv, gm):
    cityToRemove = resilientPopulationEvent[2]
    # remove city from infection discard deck
    isv['infectionDiscardDeck'] = np.setdiff1d(isv['infectionDiscardDeck'], cityToRemove)
    isv['infectionCardsRemoved'][cityToRemove] = True
    # remove resilient population event card from player hand to eventDiscardPile (this removes from all hands)
    isv['playerCardsHeld'][gm['eventCardNames']['ResilientPopulation']] = False
    isv['playerCardsRemoved'][gm['eventCardNames']['ResilientPopulation']] = True
    return isv

def oneQuietNight(oneQuietNightEvent, isv, gm):
    isv['oneQuietNight'] = True
    # remove one quiet night event card from player hand to eventDiscardPile (this removes from all hands)
    isv['playerCardsHeld'][gm['eventCardNames']['OneQuietNight']] = False
    isv['playerCardsRemoved'][gm['eventCardNames']['OneQuietNight']] = True
    return isv

def forecast(forecastEvent, isv, gm):
    if (gm['debugLevel'] >= 3):
        print('Forecast is not played until immediately before infection')
    return isv

def checkForUnresolvedOutbreaks(isv, gm):
    # CHECK FOR UNRESOLVED OUTBREAKS AND WARN ONLY IF THEY EXIST
    if ( any( isv['blueCubesByCity'] > 3 ) | any( isv['yellowCubesByCity'] > 3 ) | any( isv['blackCubesByCity'] > 3 ) | any(isv['redCubesByCity'] > 3) ):
        if (gm['debugLevel'] >= 1):
            print('TURN STARTED WITH AN UNRESOLVED OUTBREAK')
            print('----------------------------------------')

def updateEradications(isv, gm):
    # UPDATE ERADICATIONS
    isv['diseaseEradications'][gm['diseaseColorIndex']['blue']] = ( all(isv['blueCubesByCity'] == 0) ) & ( (isv['diseaseCures'][gm['diseaseColorIndex']['blue']] > 0)[0] )
    isv['diseaseEradications'][gm['diseaseColorIndex']['yellow']] = ( all(isv['yellowCubesByCity'] == 0) ) & ( (isv['diseaseCures'][gm['diseaseColorIndex']['yellow']] > 0)[0] )
    isv['diseaseEradications'][gm['diseaseColorIndex']['black']] = ( all(isv['blackCubesByCity'] == 0) ) & ( (isv['diseaseCures'][gm['diseaseColorIndex']['black']] > 0)[0] )
    isv['diseaseEradications'][gm['diseaseColorIndex']['red']] = ( all(isv['redCubesByCity'] == 0) ) & ( (isv['diseaseCures'][gm['diseaseColorIndex']['red']] > 0)[0] )
    return isv

def drawPlayerCardsMechanics(isv, gm):
    if ( isv['playerCardDeck'].shape[0] >= 2 ):
        for iIC in range(2):
            drawnPlayerCard, playerCardDeck = getTopCard(isv['playerCardDeck'])
            isv['playerCardDeck'] = playerCardDeck
            if (gm['debugLevel'] >= 3):
                print(isv['teamSequence'][isv['playerCurrentTurn']] + '(' + str(isv['playerCurrentTurn']) + ') drew ' + gm['allPlayerCards'][drawnPlayerCard] )
            #   RESOLVE PLAYER CARD EPIDEMICS
            if ( drawnPlayerCard == 0 ):  # 0 is an epidemic
                if ( isv['infectionDeck'].shape[0] > 0 ):
                    epidemicCity, infectionDeck = getBottomCard(isv['infectionDeck'])
                    isv['infectionDeck'] = infectionDeck
                    # if not eradicated, visit epidemic on city
                    if ( isv['diseaseEradications'][gm['diseaseColorIndex'][gm['mapCityColorIndexed'][epidemicCity]]][0] == 0 ):
                        visitEpidemicOnCity(epidemicCity, isv, gm)
                        isv = intensify(isv)
                        epidemicOutbreakCounts = np.concatenate((isv['blueCubesByCity'][epidemicCity],isv['yellowCubesByCity'][epidemicCity],isv['blackCubesByCity'][epidemicCity],isv['redCubesByCity'][epidemicCity]))
                        if any( epidemicOutbreakCounts > 3):
                            if (gm['debugLevel'] >= 3):
                                print('Resolving epidemic outbreak in ' + gm['indexedCities'][epidemicCity])
                            isv = resolveOutbreak(isv, gm, np.zeros((49,1))>0.5 )
                else:
                    if (gm['debugLevel'] >= 3):
                        print('Infection Deck exhausted')
                    isv['infectionDeckExhausted'] = True
            else:
                isv = addPlayerCardToHand(drawnPlayerCard,isv,gm)
            if (gm['debugLevel'] >= 3):
                print('-------------------------------------')
    else:
        isv['playerCardsExhausted'] = True
    return isv

def addPlayerCardToHand(drawnCard, isv, gm):
    np.transpose(isv['playerCardsHeld'])[isv['playerCurrentTurn']][drawnCard] = True
    # Add card to player's hand, mark it seen (True), mark it unseen (False) 
    isv['playerCardsSeen'][drawnCard] = True
    isv['playerCardsNotSeen'][drawnCard] = False
    return isv

def getForecastDeck(isv,gm):
    # Get top 6 cards to forecast
    forecastDeck = []
    for iFC in range(6):
        forecastCard, infectionDeck = getTopCard(isv['infectionDeck'])
        isv['infectionDeck'] = infectionDeck
        forecastDeck.append(forecastCard)
    return forecastDeck, isv

def playForecast(isv, gm):
    # remove forecast from team hand to discard pile
    isv['playerCardsHeld'][gm['eventCardNames']['Forecast']] = False
    isv['playerCardsRemoved'][gm['eventCardNames']['Forecast']] = True
    if ( isv['contingencyPlannerReclaimedCard'] == gm['eventCardNames']['Forecast'] ):
        # Mark forecast replayed by contingency planner
        isv['contingencyPlannerEventsReplayed'][isv['contingencyPlannerReclaimedCard']] = True
        isv['contingencyPlannerReclaimedCard'] = 0
    forecastDeck, isv = getForecastDeck(isv,gm)
    return forecastDeck, isv

def randomForecast(forecastDeck):
    # Randomly choose top 6 sequence of infection deck
    forecastSeq = range(6)
    shuffle(forecastSeq)
    forecastedDeckAssigned = np.array([forecastDeck[i] for i in forecastSeq])
    return forecastedDeckAssigned

def simpleForecast(forecastDeck,isv,gm):
    # choose increasing sequence of cubes on forecast deck
    maxDiseaseCubesPerCity = np.array([isv['blueCubesByCity'][forecastDeck].T, \
        isv['yellowCubesByCity'][forecastDeck].T, \
        isv['blackCubesByCity'][forecastDeck].T, \
        isv['redCubesByCity'][forecastDeck].T]).max(axis=0)[0]
    forecastSeq = list(np.argsort(maxDiseaseCubesPerCity))
    forecastedDeckAssigned = np.array([forecastDeck[i] for i in forecastSeq])
    return forecastedDeckAssigned

def forecastMechanics(isv,gm):
    if ( ( gm['eventCardNames']['Forecast'] in np.where(isv['playerCardsHeld'])[0]) | ( isv['contingencyPlannerReclaimedCard'] == gm['eventCardNames']['Forecast'] ) ):
        if (gm['debugLevel'] >= 3):
            print('team could play forecast')
        # TEAM AI API -> CHOOSE TO PLAY FORECAST
        if isv['playForecastOnEpidemic']:
            playingForecast = True
        else:
            playingForecast = randint(0,100) > 30 # play forecast 30% of time team holds it
        if playingForecast:
            forecastDeck, isv = playForecast(isv, gm)
            # TEAM AI API -> CHOOSE SEQUENCE OF FORECASTED DECK ASSIGNED
            if (gm['indexedForecastTypes'][isv['forecastType']] == 'simpleForecast'):
                forecastedDeckAssigned = simpleForecast(forecastDeck,isv,gm)
            elif (gm['indexedForecastTypes'][isv['forecastType']] == 'randomForecast'):
                forecastedDeckAssigned = randomForecast(forecastDeck)
            isv = restackInfectionDeckWithForecastDeck(isv, forecastedDeckAssigned)
    return isv

def restackInfectionDeckWithForecastDeck(isv, forecastedDeckAssigned):
    # put forecast deck back on infection deck
    isv['infectionDeck'] = np.concatenate((forecastedDeckAssigned,isv['infectionDeck']))
    return isv

def infectCities(isv, gm):
    # DRAW 'infectionRate' INFECTION CARDS
    for iIC in range(isv['infectionRate']):
        tmpCityIndex, infectionDeck = getTopCard(isv['infectionDeck'])
        # get the top card of infectionDeck, tmpCityIndex
        isv['infectionDeck'] = infectionDeck
        # Add that card to the infection discard pile
        isv['infectionDiscardDeck'] = np.append(isv['infectionDiscardDeck'],tmpCityIndex)
        # if not eradicated, infect
        if ( isv['diseaseEradications'][gm['diseaseColorIndex'][gm['mapCityColorIndexed'][tmpCityIndex]]][0] == 0 ):
            isv = infectCity(tmpCityIndex, isv, gm)
            infectedCounts = np.concatenate((isv['blueCubesByCity'][tmpCityIndex],isv['yellowCubesByCity'][tmpCityIndex],isv['blackCubesByCity'][tmpCityIndex],isv['redCubesByCity'][tmpCityIndex]))
            if any( infectedCounts > 3):
                if (gm['debugLevel'] >= 3):
                    print('Resolving infection outbreak in ' + gm['indexedCities'][tmpCityIndex])
                # RESOLVE ANY OUTBREAKS
                isv = resolveOutbreak(isv, gm, np.zeros((49,1))>0.5 )
            if (gm['debugLevel'] >= 3):
                print('-------------------------------------')
    return isv

def infectionMechanics(isv,gm):
    if not( isv['oneQuietNight'] ):
        if ( isv['infectionDeck'].shape[0] >= isv['infectionRate'] ):
            isv = infectCities(isv, gm)
        else:
            if (gm['debugLevel'] >= 3):
                print('Infection Deck exhausted')
            infectionDeckExhausted = True
    else:
        if (gm['debugLevel'] >= 3):
            print('Skipping infect cities because one quiet night was played...')
        # And then turn off the oneQuietNightState for next round
        isv['oneQuietNight'] = False
    return isv

def listDiscardActions(isv,gm):
    playerCardsBeforeDiscard = np.transpose(isv['playerCardsHeld'])[isv['playerCurrentTurn']]
    if ( np.sum(playerCardsBeforeDiscard) > 7 ):
        cardKeepOptions = listAllDiscardOptions(playerCardsBeforeDiscard)
    else:
        cardKeepOptions = [0,np.where(playerCardsBeforeDiscard)[0]]
    return cardKeepOptions

def chooseDiscardOptionMechanics(discardOptions):
    # TEAM AI API -> CHOOSE FROM RANDOMKEEP
    if len(discardOptions) == 2:
        a = discardOptions[1]
    else:
        randomKeep = randint(0,len(discardOptions)-1)
        a = discardOptions[randomKeep][1]
    return a

def playerDiscardMechanics(isv,gm,cardsToKeep):
    isv = discardPlayerCardsToSeven(isv, cardsToKeep)
    return isv

def listAllDiscardOptions(playerCardsBeforeDiscard):
    keepCardsOptionCount = 0
    # TEAM AI API -> CHOOSE CARDS TO KEEP       
    cardsAfterDraw = np.where(playerCardsBeforeDiscard)[0]
    cardKeepOptions = []
    for iX in itertools.combinations(cardsAfterDraw, 7):
        cardKeepOptions.append([keepCardsOptionCount, iX])
        keepCardsOptionCount = keepCardsOptionCount + 1
    return cardKeepOptions

def discardPlayerCardsToSeven(isv, cardsToKeep):
    cardsToDiscard = tuple(set(np.where(np.transpose(isv['playerCardsHeld'])[isv['playerCurrentTurn']])[0]) - set(cardsToKeep))
    cardsKept = np.zeros((54))
    cardsDiscarded = np.zeros((54))
    for iKEEP in cardsToKeep:
        cardsKept[iKEEP] = 1
    for iDISCARD in cardsToDiscard:
        cardsDiscarded[iDISCARD] = 1
    np.transpose(isv['playerCardsHeld'])[isv['playerCurrentTurn']] = cardsKept > 0.5
    np.transpose(isv['playerCardsRemoved'])[0] = cardsDiscarded > 0.5
    return isv

def featureVectorizeFromBool(isv, iKL):
    isvVec = np.array([float(isv[iKL])])
    numDVec = isvVec.shape[0]
    fVecNames = [iKL]
    return isvVec, numDVec, fVecNames

def featureVectorizeFromInt(isv, iKL):
    isvVec = np.array([float(isv[iKL])])
    numDVec = isvVec.shape[0]
    fVecNames = [iKL]
    return isvVec, numDVec, fVecNames

def featureVectorizeFromArray(isv, iKL, debugLevel=5):
    if ( iKL == 'infectionDeck' ) | ( iKL == 'infectionDiscardDeck' ):
        tmpVec = np.zeros(48)
        tmpVec[:isv[iKL].shape[0]] = isv[iKL]
    elif ( iKL == 'playerCardDeck' ):
        tmpVec = np.zeros(58)
        tmpVec[:isv[iKL].shape[0]] = isv[iKL]
    else:
        tmpVec = isv[iKL]
    if tmpVec.dtype == np.dtype('float64'):
        isvVec = tmpVec.astype('float').flatten()
    elif tmpVec.dtype == np.dtype('bool'):
        isvVec = tmpVec.astype('float').flatten()
    elif tmpVec.dtype == np.dtype('int'):
        isvVec = tmpVec.astype('float').flatten()
    else:
        if (debugLevel >= 1):
            print('array type not recognized')
    numDVec = isvVec.shape[0]
    fVecNames = [iKL + '_' + str(s) for s in map(int,range(numDVec))]
    return isvVec, numDVec, fVecNames

def featureVectorizeFromDict(isv, iKL):
    tmpKeyVals = isv[iKL].items()
    isvVec = np.zeros(len(tmpKeyVals),'float')
    numDVec = len(tmpKeyVals)
    fVecNames = []
    for iKeyVal in range(numDVec):
        isvVec[iKeyVal] = float(tmpKeyVals[iKeyVal][1])
        fVecNames.append(iKL + '_' + tmpKeyVals[iKeyVal][0])
    return isvVec, numDVec, fVecNames

def featureVectorizeFromList(isv, iKL, gm):
    if ( iKL == 'teamSequence' ):
        isvVec = np.zeros(4) + 10 # 10 is an index offset that doesnt correspond to a role
        numDVec = 4
        for iTeamSeq in range(len(isv[iKL])):
            isvVec[iTeamSeq] = gm['indexedRoles'][isv[iKL][iTeamSeq]]
        fVecNames = [iKL + '_' + str(s) for s in map(int,range(numDVec))]
    return isvVec, numDVec, fVecNames

def vectorizeInstantStateVector(isv, gm):
    isvKeyList = sorted(isv.keys())
    allFvecNames = []
    totalDVec = 0
    fVec = []
    fVecSizes = []
    for iKL in isvKeyList:
        #print iKL, isv[iKL]
        if isinstance(isv[iKL],bool):
            isvVec, numDVec, fVecNames = featureVectorizeFromBool(isv, iKL)
        if isinstance(isv[iKL],int):
            isvVec, numDVec, fVecNames = featureVectorizeFromInt(isv, iKL)
        elif isinstance(isv[iKL], np.ndarray):
            isvVec, numDVec, fVecNames = featureVectorizeFromArray(isv, iKL, gm['debugLevel'])
        elif isinstance(isv[iKL], dict):
            isvVec, numDVec, fVecNames = featureVectorizeFromDict(isv, iKL)
        elif isinstance(isv[iKL], list):
            isvVec, numDVec, fVecNames = featureVectorizeFromList(isv, iKL, gm)
        else:
            if (gm['debugLevel'] >= 1):
                print( iKL + ' not vectorized')
        allFvecNames = allFvecNames + fVecNames 
        totalDVec = totalDVec + numDVec
        fVec.append(isvVec)
        fVecSizes.append(numDVec)
        checksum = [np.array(fVecSizes).sum(), len(allFvecNames)]
        if not(checksum[0] == checksum[1]) & (checksum[0] == totalDVec):
            if (gm['debugLevel'] >= 1):
                print('vectorized shape divergence happened at ' + iKL + ' : ' + str(checksum[0]) + ',' + str(checksum[1]))
        if not(np.prod(isvVec.shape) == numDVec):
            if (gm['debugLevel'] >= 1):
                print('shape product difference at ' + iKL + ' : ' + str(np.prod(isvVec.shape)) + ',' + str(numDVec))
    vectorizedState = np.array([item for sublist in fVec for item in sublist])
    return vectorizedState, allFvecNames

def archiveGameState(actionSummaryLabel,gameStates,actionDescriptors,actionSummaries,rewardsISV,isv,gm):
    sVec, sVecNames = vectorizeInstantStateVector(isv, gm)
    if len(gameStates) > 0:
        aVec = sVec - gameStates[-1] # s(t) = s(t-1) + a(t)
        actionDescriptors.append(list(aVec))
        risv = rewardMechanics(isv,gm,sVec,gameStates[-1],actionSummaryLabel)
    else:
        risv = rewardMechanics(isv,gm,sVec,[],actionSummaryLabel)
    aSummaryVec = [actionSummaryLabel, gm['indexedRoles'][isv['teamSequence'][isv['playerCurrentTurn']]]]
    gameStates.append(list(sVec))
    actionSummaries.append(list(aSummaryVec))
    rewardsISV.append(risv)
    return gameStates,actionDescriptors,actionSummaries,rewardsISV

def updateGameOverStatus(isv, gm):
    isv['allDiseasesCured'] = all(isv['diseaseCures'])
    isv['eightOrMoreOutbreaks'] = isv['outbreakCount'] >= 8
    isv['diseaseCubesExhausted'] = ( isv['diseaseCubesPiles']['blue'] < 0 ) | ( isv['diseaseCubesPiles']['yellow'] < 0 ) | ( isv['diseaseCubesPiles']['black'] < 0 ) | ( isv['diseaseCubesPiles']['red'] < 0 )
    isv['gameFinished'] = ( isv['playerCardsExhausted'] | isv['allDiseasesCured'] | isv['eightOrMoreOutbreaks'] | isv['diseaseCubesExhausted'] | isv['infectionDeckExhausted'] )
    return isv

def markContingencyReplayed(eventStr, isv, gm):
    if isv['contingencyPlannerReclaimedCard'] == gm['eventCardNames'][eventStr]:
        isv['contingencyPlannerEventsReplayed'][isv['contingencyPlannerReclaimedCard']] = True
        isv['contingencyPlannerReclaimedCard'] = 0
    return isv

def updateQuarantine(isv, gm):
    if isv['teamHasQuarantineSpecialist']:
        quarantinedCities = np.zeros((49))
        quarantineSpecialistCity = np.where(isv['teamMemberCities'].T[isv['teamSequence'].index('QuarantineSpecialist')])[0][0]
        quarantinedCities[quarantineSpecialistCity] = True
        quarantineCityIndexList = np.where(gm['mapAdj'][quarantineSpecialistCity-1])[0] + 1
        for iQC in quarantineCityIndexList:
            quarantinedCities[iQC] = True
            isv['quarantinedCities'] = quarantinedCities
    return isv

def updateGameWithActionEvent(a, isv, gm):
    actionCost = 0
    if ( a[2][1] == 'passTurn' ):
        isv = passTurn(a[2], isv, gm['debugLevel'])
        actionCost = 1
    elif ( a[2][1] == 'move' ):
        isv = move(a[2], isv)
        actionCost = 1
    elif ( a[2][1] == 'directFlight' ):
        isv = directFlight(a[2], isv)
        actionCost = 1
    elif ( a[2][1] == 'charterFlight' ):
        isv = charterFlight(a[2], isv)
        actionCost = 1
    elif ( a[2][1] == 'shuttle' ):
        isv = shuttle(a[2], isv)
        actionCost = 1
    elif ( a[2][1] == 'treat' ):
        isv = treat(a[2], isv, gm)
        actionCost = 1
    elif ( a[2][1] == 'build' ):
        isv = build(a[2], isv)
        actionCost = 1
    elif ( a[2][1] == 'cure' ):
        isv = cure(a[2], isv)
        actionCost = 1
    elif ( a[2][1] == 'give' ):
        isv = give(a[2], isv)
        actionCost = 1
    elif ( a[2][1] == 'take' ):
        isv = take(a[2], isv)
        actionCost = 1
    elif ( a[2][1] == 'reclaim' ):
        isv = reclaim(a[2], isv, gm['debugLevel'])
        actionCost = 1
    elif ( a[2][1] == 'airlift' ):
        isv = airlift(a[2], isv, gm)
        isv = markContingencyReplayed('Airlift', isv, gm)
    elif ( a[2][1] == 'governmentGrant' ):
        isv = governmentGrant(a[2], isv, gm)
        isv = markContingencyReplayed('GovernmentGrant', isv, gm)
    elif ( a[2][1] == 'oneQuietNight' ):
        isv = oneQuietNight(a[2], isv, gm)
        isv = markContingencyReplayed('OneQuietNight', isv, gm)
    elif ( a[2][1] == 'resilientPopulation' ):
        isv = resilientPopulation(a[2], isv, gm)
        isv = markContingencyReplayed('ResilientPopulation', isv, gm)
    elif ( a[2][1] == 'forecast' ):
        isv = forecast(a[2], isv, gm)
        isv = markContingencyReplayed('Forecast', isv, gm)
    else:
        if (gm['debugLevel'] >= 1):
            print('Not a valid action: ' + a[2][1])
    isv = updateQuarantine(isv, gm)

    return isv, actionCost

def pandemicInit(numTeamMembers, difficultyLevel, numStartingCards, debugLevel):
    # SETUP BOARD AND COMPUTE INITIAL AND CURRENT STATE VECTORS
    isv0, isv, gm = initializeGame(numTeamMembers, difficultyLevel, numStartingCards, debugLevel)
    sVec, sVecNames = vectorizeInstantStateVector(isv, gm)
    ### NEED TO TURN PANDEMIC EMULATOR INTO AN ENV-LIKE CALL... Something like:
    # observation = env.reset() functions like game.initialize()
    return isv, gm, sVec, sVecNames # observation = env.reset() in Karpathy pong example

def pandemicSampleAvailableAction(isv,gm):
    if gm['indexedGameMechanicsSeqs'][isv['mechanicsSeq']] in ['action1','action2','action3','action4']:
        actionEvents = computeAvailableActions(isv, gm)
        showActionOptions(actionEvents, isv, gm)
        # TEAM AI API -> CHOOSE AN ACTION FROM CURRENT PLAYER ACTIONS
        randomActIndex = randint(0,len(actionEvents['actionEventList'])-1)
        action = actionEvents['actionEventList'][randomActIndex]
        if (gm['debugLevel'] >= 3):
            print('Executing ' + str(randomActIndex) + ': ' + action[1][0])
        #isv, actionCost = updateGameWithActionEvent(action, isv, gm)
    elif gm['indexedGameMechanicsSeqs'][isv['mechanicsSeq']] in ['drawPlayerCards']:
        # passive action
        action = ['drawPlayerCards']
    elif gm['indexedGameMechanicsSeqs'][isv['mechanicsSeq']] in ['forecast']:
        # need to represent and take forecast options here
        action = ['forecast']
    elif gm['indexedGameMechanicsSeqs'][isv['mechanicsSeq']] in ['discard']:
        # need to represent and take discard options here
        discardOptions = listDiscardActions(isv,gm)
        action = chooseDiscardOptionMechanics(discardOptions)
    elif gm['indexedGameMechanicsSeqs'][isv['mechanicsSeq']] in ['infectCities']:
        action = ['infect']
        # passive action
    return action

def pandemicStep(isv,gm,action):
    ### NEED TO TURN PANDEMIC EMULATOR INTO AN ENV-LIKE CALL... Something like:
    # env.reset() functions like game.initialize()
    # action = env.action_space.sample()
    # observation, reward, done, info = env.step(action)

    # COMPUTE INPUT STATE VECTORS
    sVec, sVecNames = vectorizeInstantStateVector(isv, gm)
    # TAKE PLAYER ACTIONS BASED ON mechanicsSeq
    isv,a,actionSummaryLabel = pandemicTurnMechanics(isv,gm,action)
    # COMPUTE UPDATED STATE VECTORS
    s1, sVecNames = vectorizeInstantStateVector(isv, gm)
    risv = rewardMechanics(isv,gm,sVec,s1,actionSummaryLabel)

    # UPDATE gameOver STATE
    isv = updateGameOverStatus(isv, gm)
    done = isv['gameFinished']
    reward = risv[3] # hard coded to be the treat reward
    info = {'debugLevel':gm['debugLevel'], 'isv': isv}
    return sVec, reward, done, info

def pandemicTurnMechanics(isv,gm,action):
    if not(isv['gameFinished']):
        tookAction = True
        actionCost = 0
        if gm['indexedGameMechanicsSeqs'][isv['mechanicsSeq']] in ['action1','action2','action3','action4']:
            if (gm['debugLevel'] >= 2):
                print(isv['teamSequence'][isv['playerCurrentTurn']] + '(' + str(isv['playerCurrentTurn']) + ') taking turn... (on ' + gm['indexedGameMechanicsSeqs'][isv['mechanicsSeq']] + ')...')
            if (gm['debugLevel'] >= 3):
                print('=====================================')
            # # TAKE PLAYER ACTION
            # actionEvents = listActionEventMechanics(isv,gm)
            # TEAM AI API -> CHOOSE AN ACTION FROM CURRENT PLAYER ACTIONS
            # a = chooseActionEventMechanics(actionEventList)
            isv,a,actionCost = executeActionEventMechanics(isv,gm,action)
            if actionCost < 1:
                tookAction = False # don't update game mechanics sequence if an event was played
            if (gm['debugLevel'] >= 3):
                print('-------------------------------------')
            checkForUnresolvedOutbreaks(isv, gm)
            actionSummaryLabel = gm['actionTypes'][a[2][1]]
        elif gm['indexedGameMechanicsSeqs'][isv['mechanicsSeq']] in ['drawPlayerCards']:
            # DRAW 2 PLAYER CARDS -> EPIDEMICS TRIGGER DRAWING FROM infectionDeck
            isv = drawPlayerCardsMechanics(isv, gm) # passive action of player card draw game mechanics can be captured as a state diff
            actionSummaryLabel = gm['actionTypes']['drawPlayerCards']
            a = 0
        elif gm['indexedGameMechanicsSeqs'][isv['mechanicsSeq']] in ['forecast']:
            # IF ANY TEAM MEMBER HAS FORECAST CARD (CHECK FOR CONTINGENCY PLANNER HOLDING FORECAST CARD AS WELL), THIS IS THE PREINFECTION OPPORTUNITY TO PLAY IT
            isv = forecastMechanics(isv,gm) # choice of whether to play forecast can be encoded as a state diff every round of play
            actionSummaryLabel = gm['actionTypes']['forecast']
            a = 0
        elif gm['indexedGameMechanicsSeqs'][isv['mechanicsSeq']] in ['discard']:
            # RESOLVE PLAYER DISCARDS
            isv = playerDiscardMechanics(isv,gm,action) # player discards can be encoded as a state diff every round of play
            actionSummaryLabel = gm['actionTypes']['discard']
            # NEED TO ENCODE a AS AN ACTION
            a = action
        elif gm['indexedGameMechanicsSeqs'][isv['mechanicsSeq']] in ['infectCities']:
            # INFECT CITIES
            isv = infectionMechanics(isv,gm) # infect cities can be encoded as a state diff every round of play
            actionSummaryLabel = gm['actionTypes']['infect']
            # infect cities is the last phase of a turn, so increment the turn sequence when infect cities is finished
            isv['iTurnSeq'] = np.mod(isv['iTurnSeq'] + 1, gm['numTeamMembers'])
            isv['playerCurrentTurn'] = np.mod(isv['iTurnSeq'], gm['numTeamMembers'])
            a = 0
        else:
            if (gm['debugLevel'] >= 1):
                print('ERROR: GAME MECHANICS ' + gm['indexedGameMechanicsSeqs'][isv['mechanicsSeq']] + ' NOT RECOGNIZED')
            return None
        if tookAction: # only advance action counter in player action/event choices if action was taken
            isv['mechanicsSeq'] = gm['gameMechanicsSeqsDict'][gm['nextMechanicsSeqDict'][gm['indexedGameMechanicsSeqs'][isv['mechanicsSeq']]]]

    return isv, a, actionSummaryLabel

def getActionCode(action,isv,gm):
    playerNum = isv['playerCurrentTurn']
    playerRole = gm['indexedRoles'][isv['teamSequence'][isv['playerCurrentTurn']]]
    playerCity = np.where(isv['teamMemberCities'].T[isv['playerCurrentTurn']])[0][0]
    # if an action is a single list of all integer items, it's what card indexes to keep on discard
    if isinstance(action, np.ndarray) and (action.dtype == np.dtype('int64')):
        playerAction = gm['actionTypes']['discard']
        fromLocation = action.shape[0]
        toLocation = 0 
        # IF GOAL DIRECTED: could code for "color to keep" by simple greedy approach across players for uncured disease cards
        # IF HEALTH DIRECTED: could code for city to aim for by simple greedy minimization of "action count" to treatable cubes
        if (gm['debugLevel'] == 1):                                   # ONLY REPORTS ON debugLevel = 1
            print('skipped discards not really represented yet')
    elif isinstance(action, tuple):
        playerAction = gm['actionTypes']['discard']
        fromLocation = 0
        toLocation = 0 
        # IF GOAL DIRECTED: could code for "color to keep" by simple greedy approach across players for uncured disease cards
        # IF HEALTH DIRECTED: could code for city to aim for by simple greedy minimization of "action count" to treatable cubes        
        if (gm['debugLevel'] >= 1):
            print('discards to 7 cards not really represented yet')
    elif (len(action) == 1):
        playerAction = gm['actionTypes'][action[0]]
        fromLocation = 0
        toLocation = 0
    elif (len(action) == 2):
        if (gm['debugLevel'] == 1):                                   # ONLY REPORTS ON debugLevel = 1
            print('no actions except discards should be length 2')
        return None
    elif (len(action) == 3) and isinstance(action[2],list):
        # player actions have 3 fields, with index 2 having the code
        if (action[2][1] in gm['playerActionTypes']):
            playerAction = gm['actionTypes'][action[2][1]]
            try:
                fromLocation = action[2][2]
            except IndexError:
                fromLocation = 0
            try:
                toLocation = action[2][3]
            except IndexError:
                toLocation = 0
    else: 
        if (gm['debugLevel'] >= 1):
            print('unrecognized action type')
        return None
    playerActionCode = [playerNum, playerRole, playerCity, playerAction, fromLocation, toLocation] # complex action code with large action space
    #playerActionCode = [playerAction]                                                              # simple action code with small action space
    return playerActionCode
