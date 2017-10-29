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
from setupPandemicGame import initializeGame
from showMap import showMap
from computeAvailableActions import computeAvailableActions
from updateGameWithActionEvent import updateGameWithActionEvent
from showActionOptions import showActionOptions

# ToDo:
# =====================================
# o. implement dispatcher

# 1. Learn health indicator: reward for surviving to end of player cards
# . Value getting to end of player cards: 2^(7-numOutbreaks)
# . Value treating a 3 next to a 3: 50
# . Value treating a 3: 20
# . Value treating a 2: 5
# . Value treating a 1: 1

# 2. Learn to build a hand of a cureable disease color (5 or more cards of one color): reward for holding more cards of 1 color

# 3. Learn cure mission:
# . Learn to gather one color
# . Learn to coordinate gathering one color per player
# . Learn to get the researcher and scientist to fill scientist's hand with 4 of one color
# . Learn to go to research facility
# . Learn to go to research facility with a cureable hand
# 4. Learn to cure a disease
# 5. Learn to cure 2 diseases
# 6. Learn to cure 3 diseases
# 7. Learn to cure 4 diseases

# DEFINE GAME PARAMETERS
numTeamMembers = 3
difficultyLevel = 'introductory'
numStartingCards = 3
# SETUP BOARD AND COMPUTE INITIAL AND CURRENT STATE VECTORS
isv0, isv, gm = initializeGame(numTeamMembers, difficultyLevel, numStartingCards)


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

def featureVectorizeFromArray(isv, iKL):
	if ( iKL == 'infectionDeck' ) | ( iKL == 'infectionDiscardDeck' ):
		tmpVec = np.zeros(48)
		tmpVec[:isv[iKL].shape[0]] = isv[iKL]
	elif ( iKL == 'playerCardDeck' ):
		tmpVec = np.zeros(58)
		tmpVec[:isv[iKL].shape[0]] = isv[iKL]
	else:
		tmpVec = isv[iKL]

	if tmpVec.dtype == dtype('float64'):
		isvVec = tmpVec.astype('float').flatten()
	elif tmpVec.dtype == dtype('bool'):
		isvVec = tmpVec.astype('float').flatten()
	elif tmpVec.dtype == dtype('int'):
		isvVec = tmpVec.astype('float').flatten()
	else:
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
			isvVec, numDVec, fVecNames = featureVectorizeFromArray(isv, iKL)
		elif isinstance(isv[iKL], dict):
			isvVec, numDVec, fVecNames = featureVectorizeFromDict(isv, iKL)
		elif isinstance(isv[iKL], list):
			isvVec, numDVec, fVecNames = featureVectorizeFromList(isv, iKL, gm)
		else:
			print( iKL + ' not vectorized')
		allFvecNames = allFvecNames + fVecNames	
		totalDVec = totalDVec + numDVec
		fVec.append(isvVec)
		fVecSizes.append(numDVec)
		checksum = [np.array(fVecSizes).sum(), len(allFvecNames)]
		if not(checksum[0] == checksum[1]) & (checksum[0] == totalDVec):
			print('vectorized shape divergence happened at ' + iKL + ' : ' + str(checksum[0]) + ',' + str(checksum[1]))
		if not(np.prod(isvVec.shape) == numDVec):
			print('shape product difference at ' + iKL + ' : ' + str(np.prod(isvVec.shape)) + ',' + str(numDVec))

	vectorizedState = np.array([item for sublist in fVec for item in sublist])
	return vectorizedState, allFvecNames
