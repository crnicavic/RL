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
    wins = 0
    score = 0
    for _ in range(count):
        result, plog, dlog = episode(deck, policy)
        xp.append(logs2xp(plog, result)) 
        wins += int(result == 1)
        score += result
    winrate = wins / count * 100      
    score /= count
    return xp, winrate, score


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


def inc_mk():
    deck = deck_init(20)
    Q = init_Q()
    xp = []
    best_score = -np.inf
    best_policy = None
    for _ in range(40):
        G = calculate_gains(xp, gamma=0.9)
        player_pi = create_policy(Q, G)
        xp, winrate, score = gatherxp(deck, player_pi, count=10000)
        if best_score < score:
            best_policy = player_pi
        print(score)
