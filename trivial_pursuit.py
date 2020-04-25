import argparse
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter
from random import randrange


parser = argparse.ArgumentParser()
parser.add_argument('players_colors', type=str, nargs='+',
            help=('"_"-separated names of players and their associated colors,'
                 ' with each player_color pair separated by spaces'))
args = parser.parse_args()

assert all(len(name_color.split('_')) == 2
           for name_color in args.players_colors)
players = [{'name': name_color.split('_')[0].upper(),
            'color': name_color.split('_')[1],
            'wedges': set()}
           for name_color in args.players_colors]

# perimiter spaces
p_coords = [(6, i*(2*np.pi/42)) for i in range(42)]
p_coords.append((0, 0))
# will plot 'wedge' spaces a second time with larger markers
w_coords = [(6, i*(2*np.pi/42)) for i in range(42) if i % 7 == 0]

# 'spoke' spaces
s_coords = [(k, j*(2*np.pi/42)) for k in range(1, 6) for j in range(0, 42, 7)]

# coordinates for plotting
p_r, p_th = zip(*p_coords)
p_r = np.asarray(p_r)
p_th = np.asarray(p_th)

w_r, w_th = zip(*w_coords)
w_r = np.asarray(w_r)
w_th = np.asarray(w_th)

s_r, s_th = zip(*s_coords)
s_r = np.asarray(s_r)
s_th = np.asarray(s_th)

color_names = ['brown', 'green', 'magenta', 'yellow', 'orange', 'blue']
spoke_colors = []
# calculate colors of spoke spaces based on observed pattern and plotting order
for i in [4, 2, 1, 5, 0]:
    c_temp = color_names[i:]+color_names[:i]
    spoke_colors.extend(c_temp)

# calculate and keep track of locations/indices of perimiter spaces
d = {}
idxs = set()
order = [1, 10, 21, 32, 41]
for i, col in enumerate(color_names):
    d[col] = []
    places = order[i:] + order[:i]
    for val in places:
        idx = (val+(i*7))%42
        d[col].append(idx)
        idxs.add(idx)

# wedge coordinates
wedge_dict = {([p_th[idx] for idx in idxs if idx % 7 == 0][0], 6): col[:2]
              for col, idxs in d.items()}

# add 'roll again' spaces
d['darkgray'] = []
for val in range(42):
    if val not in idxs:
        d['darkgray'].append(val)
d['k'] = 42

# indices of just wedge spaces, for plotting with a larger markersize
wedge_d = {col: i for i, col in enumerate(color_names[3:] + color_names[:3])}

# indices of spaces on spokes
spoke_d = defaultdict(list)
for i, col in enumerate(spoke_colors):
    spoke_d[col].append(i)

thetas = np.concatenate([p_th, s_th])
rs = np.concatenate([p_r, s_r])
lines = []

for col, idxs in d.items():
    line = plt.polar(p_th[idxs], p_r[idxs], 'H', markeredgecolor='k', picker=5,
                     color=col, markersize=40, clip_on=False)[0]
    lines.append(list(zip(*line.get_data())))

for col, idxs in spoke_d.items():
    line = plt.polar(s_th[idxs], s_r[idxs], 'H', markeredgecolor='k', picker=5,
                     color=col, markersize=40)[0]
    lines.append(list(zip(*line.get_data())))

for col, idxs in wedge_d.items():
    line = plt.polar(w_th[idxs], w_r[idxs], 'H', markeredgecolor='k', picker=5,
                     color=col, markersize=45, clip_on=False)[0]

plt.axis('off')
plt.gcf().set_facecolor('lightgray')
plt.gca().set_title('Trivial Pursuit!')
plt.gca().title.set_weight('bold')
lines = np.asarray(sorted([v for l in lines for v in l]))

# drop the tokens on the board, mostly away from spaces
markers = [plt.polar([.6],[i], marker='X', color=d['color'], markersize=18,
                     lw=0, markeredgewidth=1.5, markeredgecolor='w',
                     label=d['name'])[0]
            for i, d in enumerate(players)]

# names/colors/current turn legend with wedge tracker
legend = plt.legend(loc='upper left', prop={'weight': 'bold', 'size':10},
                    bbox_to_anchor=(1, 1), markerscale=0, handlelength=0,
                    handletextpad=0, frameon=False)
for i, l in enumerate(legend.get_texts()):
    l.set_color(players[i]['color'])
    l.set_text(f'{players[i]["name"]} -')
ax = plt.gca().add_artist(legend)
token_idx = -1

def refresh(legend_obj):
    '''Update a legend with each player's name and wedge tally'''
    for i, l in enumerate(legend_obj.get_texts()):
        l.set_text((f'{players[i]["name"]} - '
                    f'{"|".join(sorted(players[i]["wedges"]))}'))
    return

def get_closest(mx, my):
    ''''Find the closest space on the board to the location of given
    coordinates.'''

    # NOTE: if the click is close to theta=0 but below the line, i.e. slightly
    # less than 2pi, the wrong space will be chosen
    mouse = np.asarray([mx, my])
    dist_2 = np.sum((lines - mouse)**2, axis=1)
    idx = np.argmin(dist_2)
    return lines[idx]

def on_key(event):
    global ud
    global token_idx
    global legend
    global mk_idx
    global current_tag

    # only care about SPACE and 'w'
    if not event.key in ' w':
        return

    # remove annotation indicating starting location on a player's first roll
    # can be different error types
    try:
        current_tag.remove()
    except:
        pass

    # 'w' -- collect the wedge from this token's location
    if event.key == 'w':
        # coordinates of this wedge
        r, th = mk_idx.get_data()
        wedge_coords = (r[0], th[0])
        # disregard if the token wasn't on a wedge
        try:
            wedge_color = wedge_dict[wedge_coords]
        except KeyError:
            return
        # update this player as having collected this wedge
        players[token_idx]['wedges'].add(wedge_color)
        refresh(legend)
        event.canvas.draw_idle()
        return

    # SPACE -- start next player's turn
    # indicate end of previous player's turn in legend
    players[token_idx]['name'] = players[token_idx]['name'].lstrip('*')
    token_idx += 1
    if token_idx == len(players):
        token_idx = 0
    # indicate this player's turn in legend
    players[token_idx]['name'] = '***' + players[token_idx]['name']
    refresh(legend)
    print(f'Team {players[token_idx]["name"].lstrip("*")} to move')
    event.canvas.flush_events()
    x, y = markers[token_idx].get_xydata()[0]
    label = markers[token_idx].get_label()
    # indicate location of current token before first roll
    current_tag = plt.annotate(label, xy=(x, y), weight='bold', color='k',
                               fontsize=12, bbox=dict(boxstyle='round,pad=0.2',
                               fc='w', alpha=0.7))
    # alternate 'to move' indicator instead of using the main legend
    #legend2 = plt.legend(handles=[markers[token_idx]], loc='upper left',
                          #bbox_to_anchor=(0,1), labels=['TO MOVE'])
    event.canvas.draw()
    mk_idx = markers[token_idx]
    # dissociate movement with previous player
    plt.gcf().canvas.mpl_disconnect(ud)

    # activate this player's turn; clicking a location will move their token
    def update(event):
        try:
            current_tag.remove()
        except ValueError:
            pass
        if event.mouseevent.button != 1:
            return
        x, y = get_closest(event.mouseevent.xdata, event.mouseevent.ydata)
        if np.abs((np.pi*2) - x) < .01:
            x = 0
        mk_idx.set_data([x],[y])
        event.canvas.draw_idle()
    ud = plt.gcf().canvas.mpl_connect('pick_event', update)

def on_press(event):
    '''Right-click to roll the die, with a quick flash of red as feedback'''
    if event.button == 3:
        plt.text(0, 8, s='  ', fontsize=18, weight='bold',
                 bbox=dict(facecolor='r'))
        event.canvas.draw()
        plt.text(0, 8, s=randrange(1, 7), color='k', fontsize=18,
                 weight='bold', bbox=dict(facecolor='w'))
        event.canvas.draw_idle()
        return

def start_action(event):
    print(f'Press SPACE to begin {players[0]["name"]}\'s turn')

ud = plt.gcf().canvas.mpl_connect('pick_event', start_action)
die_roll = plt.gcf().canvas.mpl_connect('button_press_event', on_press)
token_key = plt.gcf().canvas.mpl_connect('key_press_event', on_key)

plt.show()
