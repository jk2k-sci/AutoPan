import sys
import numpy as np
import matplotlib.pyplot as plt

import csv
import copy
import argparse
import itertools

from random import randint
from random import shuffle
from pandemicUtils import *

# ToDo:
# =====================================
# o. implement dispatcher
# gameState = initialize()
# gameState = playAction(gameState)

# DEFINE GAME PARAMETERS
numTeamMembers = 3
difficultyLevel = 'introductory'
numStartingCards = 3
debugLevel = 4
if debugLevel >= 5:
	boardViz = True
else:
	boardViz = False
computeSAVecs = True

# SETUP BOARD AND COMPUTE INITIAL AND CURRENT STATE VECTORS
isv0, isv, gm = initializeGame(numTeamMembers, difficultyLevel, numStartingCards, debugLevel)
vizBoard(boardViz,isv,gm)

# INITIALIZE GAME STATE & ACTION CACHE

gameStates = []
actionDescriptors = []
actionSummaries = []
rewardsISV = []
#gameStates.append(list(sVec)) 
sVec, sVecNames = vectorizeInstantStateVector(isv, gm)
# cache initial game state
actionSummaryLabel = gm['actionTypes']['infect']
if computeSAVecs:
	gameStates,actionDescriptors,actionSummaries,rewardsISV = archiveGameState(actionSummaryLabel,gameStates,actionDescriptors,actionSummaries,rewardsISV,isv,gm)

while not(isv['gameFinished']):
	isv['playerCurrentTurn'] = np.mod(isv['iTurnSeq'], gm['numTeamMembers'])
	print(isv['teamSequence'][isv['playerCurrentTurn']] + '(' + str(isv['playerCurrentTurn']) + ') taking turn...')
	print('=====================================')
	iActionEventCount = 0
	while ( iActionEventCount < gm['numActionsPerTeamMember'] ):
		print(isv['teamSequence'][isv['playerCurrentTurn']] + ', action ' + str(iActionEventCount+1) + '...')
		print('-------------------------------------')
		# TAKE PLAYER ACTIONS
		actionEvents = listActionEventMechanics(isv,gm)
		a = chooseActionEventMechanics(actionEvents)
		isv,a,actionCost = executeActionEventMechanics(isv,gm,a)
		iActionEventCount = iActionEventCount + actionCost
		print('-------------------------------------')
		vizBoard(boardViz,isv,gm)
		checkForUnresolvedOutbreaks(isv, gm)
		actionSummaryLabel = gm['actionTypes'][a[2][1]]
		if computeSAVecs:
			gameStates,actionDescriptors,actionSummaries,rewardsISV = archiveGameState(actionSummaryLabel,gameStates,actionDescriptors,actionSummaries,rewardsISV,isv,gm)

	# DRAW 2 PLAYER CARDS -> EPIDEMICS TRIGGER DRAWING FROM infectionDeck
	isv = drawPlayerCardsMechanics(isv, gm) # passive action of player card draw game mechanics can be captured as a state diff
	actionSummaryLabel = gm['actionTypes']['drawPlayerCards']
	if computeSAVecs:
		gameStates,actionDescriptors,actionSummaries,rewardsISV = archiveGameState(actionSummaryLabel,gameStates,actionDescriptors,actionSummaries,rewardsISV,isv,gm)

	# IF ANY TEAM MEMBER HAS FORECAST CARD (CHECK FOR CONTINGENCY PLANNER HOLDING FORECAST CARD AS WELL), THIS IS THE PREINFECTION OPPORTUNITY TO PLAY IT
	isv = forecastMechanics(isv,gm) # choice of whether to play forecast can be encoded as a state diff every round of play
	actionSummaryLabel = gm['actionTypes']['forecast']
	if computeSAVecs:
		gameStates,actionDescriptors,actionSummaries,rewardsISV = archiveGameState(actionSummaryLabel,gameStates,actionDescriptors,actionSummaries,rewardsISV,isv,gm)

	# RESOLVE PLAYER DISCARDS
	discardOptions = listDiscardActions(isv,gm)
	a = chooseDiscardOptionMechanics(discardOptions)
	isv = playerDiscardMechanics(isv,gm,a) # player discards can be encoded as a state diff every round of play
	actionSummaryLabel = gm['actionTypes']['discard']
	if computeSAVecs:
		gameStates,actionDescriptors,actionSummaries,rewardsISV = archiveGameState(actionSummaryLabel,gameStates,actionDescriptors,actionSummaries,rewardsISV,isv,gm)

	# INFECT CITIES
	isv = infectionMechanics(isv,gm) # infect cities can be encoded as a state diff every round of play
	actionSummaryLabel = gm['actionTypes']['infect']
	if computeSAVecs:
		gameStates,actionDescriptors,actionSummaries,rewardsISV = archiveGameState(actionSummaryLabel,gameStates,actionDescriptors,actionSummaries,rewardsISV,isv,gm)
	vizBoard(boardViz,isv,gm)

	# UPDATE gameOver STATE
	isv = updateGameOverStatus(isv,gm)
	isv['iTurnSeq'] = isv['iTurnSeq'] + 1

endState = {'playerCardsExhausted': isv['playerCardsExhausted'], 'allDiseasesCured': isv['allDiseasesCured'], 'eightOrMoreOutbreaks': isv['eightOrMoreOutbreaks'], 'diseaseCubesExhausted': isv['diseaseCubesExhausted'], 'infectionDeckExhausted': isv['infectionDeckExhausted']}

################################################################
## PLAY GAME UNTIL END STATE
################################################################
print(endState)
vizBoard(boardViz,isv,gm)
