from blackjack import *
import visualize

def gatherxp(deck, policy, count=10):
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


def calculate_gains(xp, gamma=1):
    G = np.zeros((22, 12, len(ACTIONS), 0)).tolist()
    for ep in xp:
        g = 0
        for (state, a, r) in reversed(ep):
            #r is 0 if not terminal
            g += r 
            G[state.total][state.optotal][a].append(g)
            g *= gamma
    return G


def create_policy(G, epsilon=0.05):
    Q = np.zeros((22, 12, len(ACTIONS))).tolist()
    
    for pt in range(len(G)):
        for dt in range(len(G[pt])):
            Q[pt][dt] = [np.mean(G[pt][dt][a]) if G[pt][dt][a] else 0 \
                    for a in range(len(ACTIONS))]
    
    def policy(state: State):
        if state.total >= 21:
            return 1
        if np.random.rand() < epsilon:
            return int(np.random.rand() < 0.5) if state.total < 21 else 1
        return np.argmax(Q[state.total][state.optotal])

    return policy

def naive_mk(maxiter=40, deckcount=9, gamecount=10000):
    deck = deck_init(deckcount)
    xp = []
    best_score = -np.inf
    best_policy = None
    scores = [] 
    for _ in range(maxiter):
        G = calculate_gains(xp)
        player_pi = create_policy(G)
        xp, score = gatherxp(deck, player_pi, gamecount)
        scores.append(score)
        if best_score < score:
            best_policy = player_pi
        
    return best_policy, scores

fig, ax = plt.subplots(2)
policy, scores = naive_mk(maxiter=10)
visualize_policy(policy, ax[0])
ax[1].plot(scores)
plt.show()
