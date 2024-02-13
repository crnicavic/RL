from blackjack import *


def calculate_gains(xp):
    G = np.zeros((22, 12, len(ACTIONS), 0)).tolist()
    for ep in xp:
        for (state, a, g) in ep:
            G[state.total][state.optotal][a].append(g)
    
    return G


def create_policy(G):
    Q = np.zeros((22, 12, len(ACTIONS))).tolist()
    
    for pt in range(len(G)):
        for dt in range(len(G[pt])):
            Q[pt][dt] = [np.mean(G[pt][dt][a]) if G[pt][dt][a] else -np.inf \
                    for a in range(len(ACTIONS))]
    
    def policy(state: State):
        if state.total >= 21:
            return 1
        if -np.inf in Q[state.total][state.optotal]:
            return int(np.random.rand() < 0.5) if state.total < 21 else 1
        return np.argmax(Q[state.total][state.optotal])

    return policy

deck = deck_init(20)
xp = []
for _ in range(40):
    G = calculate_gains(xp)
    player_pi = create_policy(G)
    xp, winrate, score = gatherxp(deck, player_pi, gamma=0.5, count=10000)
    print(score)
