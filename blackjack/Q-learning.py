from blackjack import *
"""
Q-learning that learns after episode is over
The agent plays a game of blackjack, takes the experience
and updates Q
"""
def init_Q():
    Q = [[[-np.inf, -np.inf] for dt in range(12)] for pt in range(22)]
    return Q


""" Poor planning lead to this hacked piece of mess"""
prev_state = None
Q = init_Q()
prev_a = None
def policy(state: State, result=None):
    global Q 
    global prev_state
    global prev_a
    if prev_state is None: #init state
        random_a = np.random.rand() < g_epsilon
        if -np.inf in Q[state.total][state.optotal] or random_a:
            a = int(np.random.rand() < 0.5) if state.total < 21 else 1
        else:
            a = np.argmax(Q[state.total][state.optotal])
    elif result is not None: #term state
        #next state doesn't really exist
        if Q[prev_state.total][prev_state.optotal][prev_a] == -np.inf:
            Q[prev_state.total][prev_state.optotal][prev_a] = 0
        q = result - Q[prev_state.total][prev_state.optotal][prev_a]
        q *= g_alpha
        Q[prev_state.total][prev_state.optotal][prev_a] += q
        prev_state = None
        a = None
    elif -np.inf in Q[state.total][state.optotal]:
        a = int(np.random.rand() < 0.5) if state.total < 21 else 1
    else:
        if Q[prev_state.total][prev_state.optotal][prev_a] == -np.inf:
            Q[prev_state.total][prev_state.optotal][prev_a] = 0
        q = g_gamma * max(Q[state.total][state.optotal]) 
        q -= Q[prev_state.total][prev_state.optotal][prev_a]
        q *= g_alpha
        Q[prev_state.total][prev_state.optotal][prev_a] += q
        random_a = np.random.rand() < g_epsilon
        if random_a:
            a = int(np.random.rand() < 0.5) if state.total < 21 else 1
        else:
            a = np.argmax(Q[state.total][state.optotal])
    prev_state = copy.copy(state)
    prev_a = copy.copy(a)
    return a 

g_alpha = 0
g_gamma = 0
g_epsilon = 0
#this doesn't just play thousands of games, now theres active learning
def Q_learning(deckcount=9, gamecount=10, alpha=0.1, gamma=1, epsilon=0.05):
    global g_alpha
    g_alpha = alpha
    global g_gamma
    g_gamma = gamma
    global g_epsilon
    g_epsilon = epsilon
    deck = deck_init(deckcount)
    wins = 0
    score = 0
    for i in range(gamecount):
        result, plog, dlog = episode(deck, policy)
        wins += int(result == 1)
        score += result
        if plog:
            policy(None, result)
        if i % 5000 == 0:
            print(wins / 5000)
            wins = 0
    winrate = wins / gamecount * 100      
    score /= gamecount
    return winrate, score


Q_learning(gamma=0.9, gamecount=200000)
#print(*Q, sep="\n")


