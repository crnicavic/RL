from blackjack import *


def calculate_gains(xp):
    G = np.zeros((22, 12, len(ACTIONS), 0)).tolist()
    for ep in xp:
        for (state, a, g) in ep:
            G[state.total][state.optotal][a].append(g)
    
    return G


def update_action_values(pt, dt, Q, G, alpha):
    for a in range(len(ACTIONS)):
        #hack that will bite me later
        Q[pt][dt][a] = 0 if Q[pt][dt][a] == -np.inf else Q[pt][dt][a]
        for g in G[pt][dt][a]:
            Q[pt][dt][a] += alpha * (g - Q[pt][dt][a])


#bad bad bad bad
def init_Q():
    Q = [[[-np.inf, -np.inf] for dt in range(12)] for pt in range(22)]
    return Q


#i really wish for static to be a thing in python
def create_policy(Q, G, alpha=0.1):
    
    for pt in range(len(G)):
        for dt in range(len(G[pt])):
            #jesus...
            update_action_values(pt, dt, Q, G, alpha)
    
    def policy(state: State):
        if state.total >= 21:
            return 1
        if -np.inf in Q[state.total][state.optotal]:
            return int(np.random.rand() < 0.5) if state.total < 21 else 1
        return np.argmax(Q[state.total][state.optotal])

    return policy

deck = deck_init(20)
Q = init_Q()
xp = []
for _ in range(40):
    G = calculate_gains(xp)
    player_pi = create_policy(Q, G)
    xp, winrate, score = gatherxp(deck, player_pi, gamma=0.5, count=10000)
    print(score)
