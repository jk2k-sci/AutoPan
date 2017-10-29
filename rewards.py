import numpy as np
from random import shuffle
import itertools

# 1. Learn health indicator: reward for surviving to end of player cards
# 2. Learn to build a hand of a cureable disease color (5 or more cards of one color): reward for holding more cards of 1 color

# 3. Learn cure mission:
# . Learn to gather one color
# . Learn to coordinate gathering one color per player
# . Learn to get the researcher and scientist to fill scientist's hand with 4 of one color
# . Learn to go to research facility
# . Learn to go to research facility with a cureable hand
# 2. Learn to cure a disease
# 3. Learn to cure 2 diseases
# 4. Learn to cure 3 diseases
# 5. Learn to cure 4 diseases

# . Value to surviving to state: 100*exp(-numStates/40)
# . Value finishing without 7 outbreaks: exp(4-numOutbreaks)
# . Value treating a 1: 1
# . Value treating a 2: 5
# . Value treating a 3: 20
# . Value treating a 3 next to a 3: 50

def computeSurvivalReward(numStates):
	# survivalReward = 100*np.exp(numStates/40)
	survivalReward = numStates
	# higher reward for more total states
	return survivalReward

def healthyCitiesReward(numOutbreaks):
	#healthyCitiesReward = 100*np.exp(4-numOutbreaks)
	healthyCitiesReward = 8-numOutbreaks
	# higher reward for fewer outbreaks
	return healthyCitiesReward

def treatReward(nCubes):
	# treatReward = 40*(1+nCubes)
	treatReward = nCubes
	# reward for treating
	return treatReward

def diseaseCubesPilesReward(diseaseCubesPiles):
	#bluePileReward = 100*np.exp(diseaseCubesPiles['blue']/40)
	#yellowPileReward = 100*np.exp(diseaseCubesPiles['yellow']/40)
	#blackPileReward = 100*np.exp(diseaseCubesPiles['black']/40)
	#redPileReward = 100*np.exp(diseaseCubesPiles['red']/40)
	# higher reward for greater disease cubes pile sizes
	#pileReward = bluePileReward + yellowPileReward + blackPileReward + redPileReward
	bluePileReward = diseaseCubesPiles['blue']
	yellowPileReward = diseaseCubesPiles['yellow']
	blackPileReward = diseaseCubesPiles['black']
	redPileReward = diseaseCubesPiles['red']
	pileReward = np.min((bluePileReward,yellowPileReward,blackPileReward,redPileReward))
	return pileReward

def rewardMechanics(isv,gm,s,s1,a):
	sR = computeSurvivalReward(isv['numGameStates'])
	hCR = healthyCitiesReward(isv['outbreakCount'])
	dCP = diseaseCubesPilesReward(isv['diseaseCubesPiles'])

	# if ( a=='treat' ):
	if ( a==gm['actionTypes']['treat'] ):
		tR = treatReward(1.0) # hard coding number of cubes treated = 1 (ignores medic and eradications)
	else:
		tR = 0.0
	#risv = sR + hCR + dCP + tR
	risv = [sR, hCR, dCP, tR, sR + hCR + dCP + tR]
	return risv
