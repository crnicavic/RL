from blackjack import *
"""
gQ-learning that learns after episode is over
The agent plays a game of blackjack, takes the experience
and updates gQ
"""
def init_Q():
    gQ = [[[-np.inf, -np.inf] for dt in range(12)] for pt in range(22)]
    return gQ


""" Poor planning lead to this hacked piece of mess"""
prev_state = None
gQ = np.zeros((22, 12, len(ACTIONS))).tolist()
prev_a = None
def learn(state: State, result=None):
    global gQ, prev_state, prev_a 
    random_a = lambda s: int(np.random.rand() < 0.5) if s.total < 21 else 1
    if prev_state is None: #init state
        if np.random.rand() < g_epsilon:
            a = random_a(state)
        else:
            a = np.argmax(gQ[state.total][state.optotal])
    elif result is not None: #term state
        #next state doesn't really exist
        q = result - gQ[prev_state.total][prev_state.optotal][prev_a]
        q *= g_alpha
        gQ[prev_state.total][prev_state.optotal][prev_a] += q
        a = None
    else:
        q = g_gamma * max(gQ[state.total][state.optotal])
        q -= gQ[prev_state.total][prev_state.optotal][prev_a]
        q *= g_alpha
        gQ[prev_state.total][prev_state.optotal][prev_a] += q
        if np.random.rand() < g_epsilon:
            a = random_a(state)
        else:
            a = np.argmax(gQ[state.total][state.optotal])
    prev_state = copy.copy(state)
    prev_a = a 
    return a 

def create_testing_policy():
    global gQ
    Q = copy.copy(gQ)    
    def policy(state: State):
        if state.total >= 21:
            return 1
        if -np.inf in Q[state.total][state.optotal]:
            return int(np.random.rand() < 0.5) if state.total < 21 else 1
        return np.argmax(Q[state.total][state.optotal])
    #anuul gQ when It is no longer needed to avoid further errors
    gQ = None
    return policy

g_alpha = 0
g_gamma = 0
g_epsilon = 0
#this doesn't just play thousands of games, now theres active learning
def Q_learning(maxiter=20, deckcount=9, gamecount=10, alpha=0.1, gamma=1, epsilon=0.05):
    global g_alpha, g_gamma, g_epsilon
    g_alpha = alpha
    g_gamma = gamma
    g_epsilon = epsilon
    deck = deck_init(deckcount)
    scores = []
    for __ in range(maxiter):
        score = 0
        for _ in range(gamecount):
            result, plog, dlog = episode(deck, learn)
            score += result
            #natural blackjacks causing problems again
            if plog:
                learn(None, result)
        score /= gamecount
        scores.append(score)
    return create_testing_policy(), scores


fig, ax = plt.subplots(2)
policy, scores = Q_learning(gamma=0.9, gamecount=5000)
visualize_policy(policy, ax[0])
ax[1].plot(scores)
plt.show()


