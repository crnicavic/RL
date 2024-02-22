from blackjack import *
import visualize


XP_t = list[(State, int, int)]
def gatherxp \
(deck: list[Card], policy: callable, count=10) -> (XP_t, float):

    def logs2xp(turnlog, result):
        xp = []
        #natural blackjack creates an empty log, nothing to learn from that
        if not turnlog:
            return xp
        rewards = [0 for _ in turnlog]
        rewards[-1] = result
        for (hand, a), r in zip(turnlog, rewards):
            xp.append((hand, a, r))
        return xp

    xp = []
    score = 0
    for _ in range(count):
        result, plog, dlog = episode(deck, policy)
        xp.append(logs2xp(plog, result)) 
        score += result
    score /= count
    return xp, score


#a matrix where every index is 2 lists
gains_matrix = list[list[list[float], list[float]]]
def calculate_gains \
(xp: XP_t, gamma=0.85) -> gains_matrix:
    
    #aces can't be more than 1
    G = np.zeros((22, 12, 2, len(ACTIONS), 0)).tolist()
    for ep in xp:
        g = 0
        for (state, a, r) in reversed(ep):
            #r is 0 if not terminal
            g += r 
            G[state.total][state.optotal][state.aces][a].append(g)
            g *= gamma
    return G


def create_policy \
(G: gains_matrix, epsilon=0.05) -> callable:

    #aces can't be more than 1
    Q = np.zeros((22, 12, 2, len(ACTIONS))).tolist()
    
    for pt in range(len(G)):
        for dt in range(len(G[pt])):
            Q[pt][dt] = [[np.mean(G[pt][dt][aces][a]) if G[pt][dt][a] else 0 \
                    for a in range(len(ACTIONS))] for aces in range(2)]

    def policy(state: State):
        if state.total >= 21:
            return 1
        elif np.random.rand() < epsilon:
            return int(np.random.rand() < 0.5) if state.total < 21 else 1
        return np.argmax(Q[state.total][state.optotal][state.aces])

    def testing_policy(state: State):
        if state.total >= 21:
            return 1
        return np.argmax(Q[state.total][state.optotal][state.aces])


    if epsilon == 0:
        return testing_policy 

    return policy

def naive_mk \
(maxiter=40, deckcount=9, gamecount=10000) -> (callable, list[float]):

    deck = deck_init(deckcount)
    xp = []
    best_score = -np.inf
    best_policy = None
    scores = [] 
    for _ in range(maxiter):
        G = calculate_gains(xp, gamma=0.9)
        player_pi = create_policy(G)
        xp, score = gatherxp(deck, player_pi, gamecount)
        scores.append(score)
        if best_score < score:
            best_policy = create_policy(G, epsilon=0)
        
    return best_policy, scores

fig, ax = plt.subplots(2)
policy, scores = naive_mk(maxiter=10, gamecount=10000)
visualize_policy(policy, ax[0])
ax[1].plot(scores)
plt.show()
