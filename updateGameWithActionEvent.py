from pandemicUtils import *

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
		isv = passTurn(a[2], isv)
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
		isv = reclaim(a[2], isv)
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
		print('Not a valid action: ' + a[2][1])
	isv = updateQuarantine(isv, gm)

	return isv, actionCost
