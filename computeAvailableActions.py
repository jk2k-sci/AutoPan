import numpy as np
import itertools

def computeAvailableActions(isv, gm):
	################################################################
	## COMPUTE AVAILABLE ACTIONS TO currentPlayerTurn
	################################################################
	turn = {}
	turn['teamHasResearcher'] = isv['teamHasResearcher']
	turn['seqResearcher'] = isv['seqResearcher']
	pCTurn = isv['playerCurrentTurn']
	pCHeld = np.transpose(isv['playerCardsHeld'])[pCTurn]
	pCityCards = pCHeld[:49]
	turn['eventCardsRemoved'] = isv['playerCardsRemoved'][:,0] & gm['eventCardMask']
	turn['playingContingencyPlanner'] = isv['teamSequence'][isv['playerCurrentTurn']] == 'ContingencyPlanner'

	#   where is current player?
	turn['currentCityIndex'] = np.where(np.transpose(isv['teamMemberCities'])[pCTurn])[0][0]
	#   is player in a city without a research facility?
	turn['cityHasResearchFacility'] = isv['researchFacilitiesByCity'][turn['currentCityIndex']][0]

	# MOVE
	#!   is player the dispatcher?
	#!     if so, repeat for all players:
	#   what moves are available to current player?
	#     from adjacency
	turn['possibleAdjMoves'] = np.where(gm['mapAdj'][turn['currentCityIndex']-1])[0] + 1
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
	#   does player have ability to build a facility? (i.e. is operations expert or has card)
	turn['buildResearchFacilityWithCard'] = np.array([])
	if not(turn['cityHasResearchFacility']):
	#   -> list build research facility card options
		if ( gm['indexedRoles'][isv['teamSequence'][pCTurn]] == gm['indexedRoles']['OperationsExpert'] ) & ( any(pCHeld) ):
			turn['buildResearchFacilityWithCard'] = np.where(pCityCards)[0]
			turn['canBuild'] = True
		else:
			if any( turn['directFlightMoves'] == turn['currentCityIndex'] ):
				turn['buildResearchFacilityWithCard'] = np.array([turn['currentCityIndex']])
				turn['canBuild'] = True
			else:
				turn['buildResearchFacilityWithCard'] = np.array([])
				turn['canBuild'] = False
	else:
		turn['buildResearchFacilityWithCard'] = np.array([])
		turn['canBuild'] = False

	# CURE
	#   is player in a city with a research facility?
	if ( gm['indexedRoles'][isv['teamSequence'][pCTurn]] == gm['indexedRoles']['Scientist'] ):
		turn['nToCure'] = 4
	else:
		turn['nToCure'] = 5
	if turn['cityHasResearchFacility']:
	    #   does the player have sufficient number of cards of one color to cure?
		pCityColors = gm['diseaseIndexes'][pCityCards]
		nByColor = np.histogram(pCityColors,bins=[0,1,2,3,4])[0]
		cureable = nByColor >= turn['nToCure']
		if any( cureable ):
			turn['canCure'] = True
			turn['cureColorIndex'] = np.where(cureable)[0][0] # there will only ever be one cureable disease
			turn['cardsToCure'] = np.where((gm['diseaseIndexes'] == turn['cureColorIndex']) & pCityCards)[0]
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
	turn['teamEventCardsHeld'] = np.where(np.any(isv['playerCardsHeld'], axis=1) & gm['eventCardMask'])[0]

	turn['teamHasAirlift'] = gm['eventCardNames']['Airlift'] in turn['teamEventCardsHeld']
	turn['teamHasGovernmentGrant'] = gm['eventCardNames']['GovernmentGrant'] in turn['teamEventCardsHeld']
	turn['teamHasOneQuietNight'] = gm['eventCardNames']['OneQuietNight'] in turn['teamEventCardsHeld']
	turn['teamHasResilientPopulation'] = gm['eventCardNames']['ResilientPopulation'] in turn['teamEventCardsHeld']
	turn['teamHasForecast'] = gm['eventCardNames']['Forecast'] in turn['teamEventCardsHeld']

	################################################################
	# LIST ALL ACTIONS AVAILABLE TO CURRENT PLAYER
	################################################################
	actionList = []
	playerStr = isv['teamSequence'][pCTurn] + '(' + str(pCTurn) + ')'
	currentCityStr = gm['indexedCities'][turn['currentCityIndex']]

	actionEventOptionCount = 0
	passStr = ['Pass turn']
	pM = ['pCTurn', 'passTurn']
	actionList.append([actionEventOptionCount, passStr, pM])

	for iPAM in turn['possibleAdjMoves']:
		adjMoveStr = ['Move ' + playerStr + ' from ' + currentCityStr + ' to ' + gm['indexedCities'][iPAM]]
		pAM = [pCTurn, 'move', turn['currentCityIndex'], iPAM]
		actionEventOptionCount = actionEventOptionCount + 1
		actionList.append([actionEventOptionCount, adjMoveStr, pAM])

	for iDFM in turn['directFlightMoves']:
		directFlightStr = ['Direct flight ' + playerStr + ' from ' + currentCityStr + ' to ' + gm['indexedCities'][iDFM]]
		dFM = [pCTurn, 'directFlight', turn['currentCityIndex'], iDFM]
		actionEventOptionCount = actionEventOptionCount + 1
		actionList.append([actionEventOptionCount, directFlightStr, dFM])

	if turn['canCharter']:
		for iCFM in range(1,49):
			charterFlightStr = ['Charter flight ' + playerStr + ' from ' + currentCityStr + ' to ' + gm['indexedCities'][iCFM]]
			cFM = [pCTurn, 'charterFlight', turn['currentCityIndex'], iCFM]
			actionEventOptionCount = actionEventOptionCount + 1
			actionList.append([actionEventOptionCount, charterFlightStr, cFM])

	if turn['cityHasResearchFacility']:
		if ( np.sum(isv['researchFacilitiesByCity']) > 1.0 ):
			# loop over research facility options
			shuttleDestinationOptions = np.setdiff1d(np.where(isv['researchFacilitiesByCity'])[0], turn['currentCityIndex'])
			for iSDO in shuttleDestinationOptions:
				shuttleFlightStr = ['Shuttle flight ' + playerStr + ' from ' + currentCityStr + ' to ' + gm['indexedCities'][iSDO]]
				sDO = [pCTurn, 'shuttle', turn['currentCityIndex'], iSDO]
				actionEventOptionCount = actionEventOptionCount + 1
				actionList.append([actionEventOptionCount, shuttleFlightStr, sDO])

	if turn['canTreat']:
		for iTO in np.where(turn['treatOptions'])[0]:
			treatStr = ['Treat ' + gm['indexedDiseaseColors'][iTO] + ' (' + str(turn['diseaseStrength'][iTO]) + ' cubes) disease in ' + currentCityStr ]
			tAct = [pCTurn, 'treat', turn['currentCityIndex'], iTO]
			actionEventOptionCount = actionEventOptionCount + 1
			actionList.append([actionEventOptionCount, treatStr, tAct])

	if ( turn['canBuild'] ):
		for iBRF in turn['buildResearchFacilityWithCard']:
			buildStr = ['Build research facility in ' + currentCityStr + ' with ' + gm['indexedCities'][iBRF] + ' city card.']
			bRF = [pCTurn, 'build', turn['currentCityIndex'], iBRF]
			actionEventOptionCount = actionEventOptionCount + 1
			actionList.append([actionEventOptionCount, buildStr, bRF])

	if turn['canCure']:
		if ( len(turn['cardsToCure']) >= turn['nToCure'] ):
			pickCardCombination = [list(x) for x in itertools.combinations(turn['cardsToCure'], turn['nToCure'])]
			for iPCC in pickCardCombination:
				cardSubsetToCure = np.array(iPCC)
				cureStr = 'Cure ' + gm['indexedDiseaseColors'][turn['cureColorIndex']] + ' with cards '
				for iCL in range(turn['nToCure']):
					cureStr = cureStr + gm['indexedCities'][iPCC[iCL]] + "+"
				cureStr = [cureStr[:-1]]
				cD = [pCTurn, 'cure', turn['cureColorIndex'], cardSubsetToCure, turn['nToCure']]
				actionEventOptionCount = actionEventOptionCount + 1
				actionList.append([actionEventOptionCount, cureStr, cD])

	if ( turn['giveCityCardTo'].ndim == 1 ) & ( turn['giveCityCardTo'].shape[0] > 1 ):
		iGCC = turn['giveCityCardTo']
		giveStr = ['Give player ' + isv['teamSequence'][iGCC[0]] + ' (' + str(iGCC[0]) + ') ' + gm['indexedCities'][iGCC[1]] + ' card.']
		gC = [pCTurn, 'give', iGCC[0], iGCC[1]]
		actionEventOptionCount = actionEventOptionCount + 1
		actionList.append([actionEventOptionCount, giveStr, gC])
	else:
		for iGCC in turn['giveCityCardTo']:
			giveStr = ['Give player ' + isv['teamSequence'][iGCC[0]] + ' (' + str(iGCC[0]) + ') ' + gm['indexedCities'][iGCC[1]] + ' card.']
			gC = [pCTurn, 'give', iGCC[0], iGCC[1]]
			actionEventOptionCount = actionEventOptionCount + 1
			actionList.append([actionEventOptionCount, giveStr, gC])

	if ( turn['takeCityCardFrom'].ndim == 1 ) & ( turn['takeCityCardFrom'].shape[0] > 1 ):
		iTCC = turn['takeCityCardFrom']
		takeStr = ['Take ' + gm['indexedCities'][iTCC[1]] + ' city card from ' + isv['teamSequence'][iTCC[0]] + '(' + str(iTCC[0]) + ') ']
		tC = [pCTurn, 'take', iTCC[0], iTCC[1]]
		actionEventOptionCount = actionEventOptionCount + 1
		actionList.append([actionEventOptionCount, takeStr, tC])
	else:
		for iTCC in turn['takeCityCardFrom']:
			takeStr = ['Take ' + gm['indexedCities'][iTCC[1]] + ' city card from ' + isv['teamSequence'][iTCC[0]] + '(' + str(iTCC[0]) + ') ']
			tC = [pCTurn, 'take', iTCC[0], iTCC[1]]
			actionEventOptionCount = actionEventOptionCount + 1
			actionList.append([actionEventOptionCount, takeStr, tC])

	if turn['playingContingencyPlanner']:
		# Is the contingency planner currently holding a reclaimed event card? (default is card 0, which is not an event card index)
		if not( isv['contingencyPlannerReclaimedCard'] in np.where(gm['eventCardMask'])[0] ):
			# Find all the cards the contingency planner could reclaim
			reclaimEventOptions = np.where( ( isv['playerCardsRemoved'][:,0] & gm['eventCardMask'] ) & np.logical_not( isv['contingencyPlannerEventsReplayed'] ) )[0]
			for iREO in reclaimEventOptions:
				# List the reclaim event option actions
				reclaimStr = ['Reclaim ' + gm['indexedEventCards'][iREO] + ' event card from player discard pile.']
				rEC = [pCTurn, 'reclaim', iREO]
				actionEventOptionCount = actionEventOptionCount + 1
				actionList.append([actionEventOptionCount, reclaimStr, rEC])
		else:
			print('Contingency planner already holding ' + str(gm['indexedEventCards'][isv['contingencyPlannerReclaimedCard']]) + ' so cannot reclaim.')

	turn['actionList'] = actionList

	# LIST ALL EVENTS
	eventList = []

	if turn['playingContingencyPlanner']:
		# If the contingency planner's contingency card is not 0, set the corresponding event's field to team holding that card
		if not( isv['contingencyPlannerReclaimedCard'] == 0 ):
			if isv['contingencyPlannerReclaimedCard'] == gm['eventCardNames']['Airlift']:
				turn['teamHasAirlift'] = True
			elif isv['contingencyPlannerReclaimedCard'] == gm['eventCardNames']['GovernmentGrant']:
				turn['teamHasGovernmentGrant'] = True
			elif isv['contingencyPlannerReclaimedCard'] == gm['eventCardNames']['OneQuietNight']:
				turn['teamHasOneQuietNight'] = True
			elif isv['contingencyPlannerReclaimedCard'] == gm['eventCardNames']['ResilientPopulation']:
				turn['teamHasResilientPopulation'] = True
			elif isv['contingencyPlannerReclaimedCard'] == gm['eventCardNames']['Forecast']:
				turn['teamHasForecast'] = True
			else:
				print('ERROR: Contingency planner not holding a valid event card!')

	if turn['teamHasAirlift']:
		allDestinations = np.where(np.transpose(isv['teamMemberCities'])[isv['playerCurrentTurn']] == 0)[0][1:]
		for iALM in allDestinations:
			airliftFlightStr = ['Airlift ' + playerStr + ' from ' + currentCityStr + ' to ' + gm['indexedCities'][iALM]]
			aLM = [pCTurn, 'airlift', turn['currentCityIndex'], iALM]
			actionEventOptionCount = actionEventOptionCount + 1
			eventList.append([actionEventOptionCount, airliftFlightStr, aLM])

	if turn['teamHasGovernmentGrant']:
		cityIndexesWithoutResearchFacility = np.where(isv['researchFacilitiesByCity'] < 0.5)[0][1:]
		for iGG in cityIndexesWithoutResearchFacility:
			buildStr = ['Build research facility in ' + gm['indexedCities'][iGG] + '(' + str(iGG) + ') with government grant event card.']
			gG = [pCTurn, 'governmentGrant', iGG]
			actionEventOptionCount = actionEventOptionCount + 1
			eventList.append([actionEventOptionCount, buildStr, gG])

	if turn['teamHasOneQuietNight']:
		oneQuietNightStr = ['Prevent infection this turn with one quiet night event card.']
		oQN = [pCTurn, 'oneQuietNight', True]
		actionEventOptionCount = actionEventOptionCount + 1
		eventList.append([actionEventOptionCount, oneQuietNightStr, oQN])

	if turn['teamHasResilientPopulation']:
		for iRP in isv['infectionDiscardDeck']:
			resilientPopulationStr = ['Remove ' + gm['indexedCities'][iRP] + '(' + str(iRP) + ') with resilient population card.']
			rP = [pCTurn, 'resilientPopulation', iRP]
			actionEventOptionCount = actionEventOptionCount + 1
			eventList.append([actionEventOptionCount, resilientPopulationStr, rP])

	if turn['teamHasForecast']:
		forecastStr = ['Forecast and resequence infection cards with forecast event card.']
		fC = [pCTurn, 'forecast', True]
		actionEventOptionCount = actionEventOptionCount + 1
		eventList.append([actionEventOptionCount, forecastStr, fC])

	turn['eventList'] = eventList

	# LIST COMBINED ACTION & EVENT OPTIONS
	turn['actionEventList'] = actionList
	if (len(eventList) > 0):
		for iEL in eventList:
			turn['actionEventList'].append(iEL)

	return turn