from blackjack import *


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


#might be considered hacky, but i think it's elegant
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


def update_action_values(pt, dt, Q, G, alpha):
    for a in range(len(ACTIONS)):
        #hack that will bite me later
        Q[pt][dt][a] = 0 if Q[pt][dt][a] == -np.inf else Q[pt][dt][a]
        for g in G[pt][dt][a]:
            Q[pt][dt][a] += alpha * (g - Q[pt][dt][a])



#i really wish for static to be a thing in python
def update_policy(Q, G, alpha=0.1, epsilon=0.05):
    
    for pt in range(len(G)):
        for dt in range(len(G[pt])):
            #jesus... pt and dt define state
            update_action_values(pt, dt, Q, G, alpha)
    
    def policy(state: State):
        if state.total >= 21:
            return 1
        elif np.random.rand() < epsilon:
            return int(np.random.rand() < 0.5) if state.total < 21 else 1
        return np.argmax(Q[state.total][state.optotal])

    return policy


def create_testing_policy(Q):
    def policy(state: State):
        if state.total >= 21:
            return 1
        return np.argmax(Q[state.total][state.optotal])
    return policy


def inc_mk(maxiter=40, deckcount=9, gamecount=10000):
    deck = deck_init(deckcount)
    Q = np.zeros((22, 12, len(ACTIONS))).tolist()
    xp = []
    scores = []
    for _ in range(maxiter):
        G = calculate_gains(xp, gamma=0.9)
        player_pi = update_policy(Q, G)
        xp, score = gatherxp(deck, player_pi, gamecount)
        scores.append(score)
    return create_testing_policy(Q), scores

fig, ax = plt.subplots(2)
policy, scores = inc_mk(maxiter=10)
visualize_policy(policy, ax[0])
ax[1].plot(scores)
plt.show()
