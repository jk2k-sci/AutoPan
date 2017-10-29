### API calls modeled to fit into Karpathy's pong RL example

from pandemicUtils import *

# DEFINE GAME PARAMETERS
numTeamMembers = 3
difficultyLevel = 'introductory'
numStartingCards = 3
# DEBUG LEVEL:
# debugLevel = 0                 # silent (no game state output)
# debugLevel = 1                 # warn only (unusual state conditions not fully tested/debugged)
# debugLevel = 2                 # quiet (minimal game state output -- init, actions, rewards, endstate)
# debugLevel = 3                 # human readable, minimal
# debugLevel = 4                 # verbose (all game state output)
# debugLevel = 5                 # verbose and interactive (all game state output with board viz)
debugLevel = 2

# env.reset() functions like game.initialize()
isv, gm, sVec, sVecNames = pandemicInit(numTeamMembers, difficultyLevel, numStartingCards, debugLevel)
print('Debug level is : ' + str(gm['debugLevel']))

done = False
while not(done):
	playerStr = isv['teamSequence'][isv['playerCurrentTurn']] + '(' + str(isv['playerCurrentTurn']) + ')'
	isvMS = isv['mechanicsSeq']
	
	# action = env.action_space.sample()
	action = pandemicSampleAvailableAction(isv,gm)
	actionBookkeeping = getActionCode(action,isv,gm)
	actionID = [actionBookkeeping[3],actionBookkeeping[5]] # actionID captures what action was taken and where a player is moving to if movement occurred
	if ( gm['indexedActions'][actionID[0]] == 'build' ) | ( gm['indexedActions'][actionID[0]] == 'governmentGrant' ):
		actionID[1] = actionBookkeeping[2] # build action only happens in player's current city, no matter how it happened
	# observation, reward, done, info = env.step(action)
	sVec, reward, done, info = pandemicStep(isv,gm,action) # sVec is a numeric state vector derived from isv used in the game mechanics

	if (debugLevel >= 2):
		print(playerStr + ' executing ' + gm['indexedGameMechanicsSeqs'][isvMS] + ' = ' + str(action))
		# print('executed ' + str(actionBookkeeping) + ':' + gm['indexedActions'][actionBookkeeping[3]])
		if ( actionID[1] != 0 ):
			print('coded as ' + str(actionID) + ':' + gm['indexedActions'][actionID[0]] + ' into ' + gm['mapCityNames'][actionID[1]])
		else:
			print('coded as ' + str(actionID) + ':' + gm['indexedActions'][actionID[0]] + ' executed without destination.')
		print('Reward is : ' + str(reward))
		print('-------------------------------------')

	# update state vector used with game mechanics
	isv = info['isv']

	if (debugLevel >= 5):
		vizBoard(True,isv,gm)

	if isv['gameFinished']:
		if (gm['debugLevel'] >= 2):
			print('Game ended with state: [allDiseasesCured: ' + str(isv['allDiseasesCured']) + ', eightOrMoreOutbreaks: ' + str(isv['eightOrMoreOutbreaks']) + ', diseaseCubesExhausted: ' + str(isv['diseaseCubesExhausted']))
