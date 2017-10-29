import numpy as np

def showActionOptions(actionEvents,isv,gm):
	printcolors = gm['printcolors']
	pCHeld = np.transpose(isv['playerCardsHeld'])[isv['playerCurrentTurn']]
	playerStr = isv['teamSequence'][isv['playerCurrentTurn']] + '(' + str(isv['playerCurrentTurn']) + ')'
	print( playerStr + ' holds cards: ' )
	print('------------------------------------')
	for iCH in np.where(pCHeld)[0]:
		if ( gm['indexedActionEventPlayerCards'][iCH] == 'Action' ):
			if gm['indexedDiseaseColors'][gm['diseaseIndexes'][iCH]] == 'blue':
				print printcolors.BLUE + gm['indexedActionEventPlayerCards'][iCH] + ': (' + gm['allPlayerCards'][iCH] + '-' + gm['indexedDiseaseColors'][gm['diseaseIndexes'][iCH]] + ')' + printcolors.ENDC
			if gm['indexedDiseaseColors'][gm['diseaseIndexes'][iCH]] == 'yellow':
				print printcolors.YELLOW + gm['indexedActionEventPlayerCards'][iCH] + ': (' + gm['allPlayerCards'][iCH] + '-' + gm['indexedDiseaseColors'][gm['diseaseIndexes'][iCH]] + ')' + printcolors.ENDC
			if gm['indexedDiseaseColors'][gm['diseaseIndexes'][iCH]] == 'black':
				print printcolors.GRAY + gm['indexedActionEventPlayerCards'][iCH] + ': (' + gm['allPlayerCards'][iCH] + '-' + gm['indexedDiseaseColors'][gm['diseaseIndexes'][iCH]] + ')' + printcolors.ENDC
			if gm['indexedDiseaseColors'][gm['diseaseIndexes'][iCH]] == 'red':
				print printcolors.RED + gm['indexedActionEventPlayerCards'][iCH] + ': (' + gm['allPlayerCards'][iCH] + '-' + gm['indexedDiseaseColors'][gm['diseaseIndexes'][iCH]] + ')' + printcolors.ENDC
		else:
			print(gm['indexedActionEventPlayerCards'][iCH] + ': (' + gm['allPlayerCards'][iCH] + ')' )
	print('====================================')
	for iAEC in actionEvents['actionEventList']:
		print( str(iAEC[0]) + ": " + iAEC[1][0] )
