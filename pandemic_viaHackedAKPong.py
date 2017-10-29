""" Trains an agent with (stochastic) Policy Gradients on Pong. Uses pandemicUtils. """
import numpy as np
import cPickle as pickle
# import gym
from pandemicUtils import *

# DEFINE GAME PARAMETERS
numTeamMembers = 3
difficultyLevel = 'introductory'
numStartingCards = 3
boardViz = False
computeSAVecs = True

# learning hyperparameters
H = 200 # number of hidden layer neurons
batch_size = 10 # every how many episodes to do a param update?
learning_rate = 1e-4
gamma = 0.99 # discount factor for reward
decay_rate = 0.99 # decay factor for RMSProp leaky sum of grad^2
resume = False # resume from previous checkpoint?
render = False

# model initialization
#D = 80 * 80 # input dimensionality: 80x80 grid
D = 1315 # input dimensionality: size of Pandemic state
if resume:
  model = pickle.load(open('save.p', 'rb'))
else:
  model = {}
  model['W1'] = np.random.randn(H,D) / np.sqrt(D) # "Xavier" initialization
  model['W2'] = np.random.randn(H) / np.sqrt(H)
  
grad_buffer = { k : np.zeros_like(v) for k,v in model.iteritems() } # update buffers that add up gradients over a batch
rmsprop_cache = { k : np.zeros_like(v) for k,v in model.iteritems() } # rmsprop memory

def sigmoid(x): 
  return 1.0 / (1.0 + np.exp(-x)) # sigmoid "squashing" function to interval [0,1]

# def prepro(I):
#   """ prepro 210x160x3 uint8 frame into 6400 (80x80) 1D float vector """
#   I = I[35:195] # crop
#   I = I[::2,::2,0] # downsample by factor of 2
#   I[I == 144] = 0 # erase background (background type 1)
#   I[I == 109] = 0 # erase background (background type 2)
#   I[I != 0] = 1 # everything else (paddles, ball) just set to 1
#   return I.astype(np.float).ravel()

def discount_rewards(r):
  """ take 1D float array of rewards and compute discounted reward """
  discounted_r = np.zeros_like(r)
  running_add = 0
  for t in reversed(xrange(0, r.size)):
    if r[t] != 0: running_add = 0 # reset the sum, since this was a game boundary (pong specific!)
    running_add = running_add * gamma + r[t]
    discounted_r[t] = running_add
  return discounted_r

def policy_forward(x):
  h = np.dot(model['W1'], x)
  h[h<0] = 0 # ReLU nonlinearity
  logp = np.dot(model['W2'], h)
  
  # This is implicitly a binary state of action 2 or not. Need a bigger list of states to choose among.
  # I think I need many actions to sample over. And every time an action is sampled, it should _mean_ the
  # same thing. Like if you're in Atlanta city, action index 4 might _mean_ move scientist from Atlanta to
  # Washington, but many turns later action index 4 might _mean_ move researcher from Paris to Milan.
  # The complete action space is LARGE--seems like a similar dimensionality as the state (1304 length)
  p = sigmoid(logp)
  return p, h # return probability of taking action 2, and hidden state

def policy_backward(eph, epdlogp):
  """ backward pass. (eph is array of intermediate hidden states) """
  dW2 = np.dot(eph.T, epdlogp).ravel()
  dh = np.outer(epdlogp, model['W2'])
  dh[eph <= 0] = 0 # backpro prelu
  dW1 = np.dot(dh.T, epx)
  return {'W1':dW1, 'W2':dW2}

def computeAvailableActionProbs(AB, sVec, isv, gm):
  """ returns the probability of taking any action in the action list """
  # ISSUE: The number of actions and their type depend on the state
  # and there are effectively 2*numPandemicWorldEdges moves + 1 treat that matter in a subgame with rewards only for treating
  # so the vector of nonzero probabilities for the simplified game is small (<100)
  # NOTE AB's getActionCode always has the action taken in the 3rd index (2 for move, 3 for direct flight, 4 for charter, 5 for shuttle, 12 for airlift, 13 for gov't grant, and 6 for treat)
  # If the action is a movement, the AB[i][4] is the destination city index, and AB[i][2] is the origin city
  return aprob, h

def computeAvailableActionProbs(actionList, aprob):
  return action
# env = gym.make("Pong-v0")
# observation = env.reset()

### NEED TO TURN PANDEMIC EMULATOR INTO AN ENV-LIKE CALL... Something like:
# env.reset() functions like game.initialize()
# action = env.action_space.sample()
# observation, reward, done, info = env.step(action)

debugLevel = 2

# env.reset() functions like game.initialize()
isv, gm, sVec, sVecNames = pandemicInit(numTeamMembers, difficultyLevel, numStartingCards, debugLevel)
observation = sVec

prev_x = None # used in computing the difference frame
xs,hs,dlogps,drs = [],[],[],[]
running_reward = None
reward_sum = 0
episode_number = 0
while True:
  #if render: env.render()

  # preprocess the observation, set input to network to be difference image
  # cur_x = prepro(observation)
  cur_x = observation
  #x = cur_x - prev_x if prev_x is not None else np.zeros(D)
  #prev_x = cur_x

  ### NEED TO TURN PANDEMIC EMULATOR INTO AN ENV-LIKE CALL... Something like:
  # action = env.action_space.sample()
  actionList = computeAvailableActions(isv, gm) # This is really a sparse sampling of all "actions" available at all states
  AB = []
  for iAL in actionList['actionList']:
    AB.append(getActionCode(iAL,isv,gm))
    # NOTE AB's getActionCode always has the action taken in the 3rd index (2 for move, 3 for direct flight, 4 for charter, 5 for shuttle, 12 for airlift, 13 for gov't grant, and 6 for treat)
  aprob, h = computeAvailableActionProbs(AB, sVec, isv, gm) # only compute the subset of aprob corresponding to actionList
  action = sampleAvailableAction(actionList, aprob) # only need the subset of aprob corresponding to actionList

  # forward the policy network and sample an action from the returned probability
  aprob, h = policy_forward(sVec)
  action = 2 if np.random.uniform() < aprob else 3 # roll the dice!

  # record various intermediates (needed later for backprop)
  xs.append(sVec) # observation
  hs.append(h) # hidden state
  y = 1 if action == 2 else 0 # a "fake label"
  dlogps.append(y - aprob) # grad that encourages the action that was taken to be taken (see http://cs231n.github.io/neural-networks-2/#losses if confused)

  ### NEED TO TURN PANDEMIC EMULATOR INTO AN ENV-LIKE CALL... Something like:
  # observation, reward, done, info = env.step(action)
  observation, reward, done, info = pandemicStep(isv,gm,action)
  # update state vector used with game mechanics
  isv = info['isv']
  sVec, sVecNames = vectorizeInstantStateVector(isv, gm)

  # # step the environment and get new measurements <- KARPATHY'S ORIGINAL EXAMPLE -- reward is the reward for that specific action
  # observation, reward, done, info = env.step(action)
  reward_sum += reward

  drs.append(reward) # record reward (has to be done after we call step() to get reward for previous action)

  if done: # an episode finished
    episode_number += 1

    # stack together all inputs, hidden states, action gradients, and rewards for this episode
    epx = np.vstack(xs)
    eph = np.vstack(hs)
    epdlogp = np.vstack(dlogps)
    epr = np.vstack(drs)
    xs,hs,dlogps,drs = [],[],[],[] # reset array memory

    # compute the discounted reward backwards through time
    discounted_epr = discount_rewards(epr)
    # standardize the rewards to be unit normal (helps control the gradient estimator variance)
    discounted_epr -= np.mean(discounted_epr)
    discounted_epr /= np.std(discounted_epr)

    epdlogp *= discounted_epr # modulate the gradient with advantage (PG magic happens right here.)
    grad = policy_backward(eph, epdlogp)
    for k in model: grad_buffer[k] += grad[k] # accumulate grad over batch

    # perform rmsprop parameter update every batch_size episodes
    if episode_number % batch_size == 0:
      for k,v in model.iteritems():
        g = grad_buffer[k] # gradient
        rmsprop_cache[k] = decay_rate * rmsprop_cache[k] + (1 - decay_rate) * g**2
        model[k] += learning_rate * g / (np.sqrt(rmsprop_cache[k]) + 1e-5)
        grad_buffer[k] = np.zeros_like(v) # reset batch gradient buffer

    # boring book-keeping
    running_reward = reward_sum if running_reward is None else running_reward * 0.99 + reward_sum * 0.01
    print 'resetting env. episode reward total was %f. running mean: %f' % (reward_sum, running_reward)
    if episode_number % 100 == 0: pickle.dump(model, open('save.p', 'wb'))
    reward_sum = 0
    observation = env.reset() # reset env
    prev_x = None

  if reward != 0: # Pong has either +1 or -1 reward exactly when game ends.
    print ('ep %d: game finished, reward: %f' % (episode_number, reward)) + ('' if reward == -1 else ' !!!!!!!!')