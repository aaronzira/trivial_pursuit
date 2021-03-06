import argparse
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.image import BboxImage
from matplotlib.transforms import Bbox, TransformedBbox
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
players = [{'name': name_color.split('_')[0][:17].upper(),
            'color': name_color.split('_')[1],
            'wedges': set()}
           for name_color in args.players_colors]

# rectangular axes for legend, die rolls, and key to topics
fig, ax = plt.subplots(1, 1, figsize=(11, 9))
plt.subplots_adjust(left=-.15)
ax.set_axis_off()

# images for rolling die
dice = {i: plt.imread(f'images/{i}.png') for i in range(7)}
bb = Bbox.from_bounds(.84, .46, .065, .1)
bb2 = TransformedBbox(bb, ax.transData)
bbox_image = BboxImage(bb2)

# perimiter spaces
p_coords = [(6, i * (2 * np.pi / 42)) for i in range(42)]
p_coords.append((0, 0))
# will plot 'wedge' spaces a second time with larger markers
w_coords = [(6, i * (2 * np.pi / 42)) for i in range(42) if i % 7 == 0]

# 'spoke' spaces
s_coords = [(k, j * (2 * np.pi / 42)) for k in range(1, 6) for j in range(0, 42, 7)]

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

# colors and categories for most editions
color_names = [('saddlebrown', 'SCIENCE & NATURE'), ('green', 'SPORTS & LEISURE'),
               ('magenta', 'ARTS & ENTERTAINMENT'), ('yellow', 'HISTORY'),
               ('orange', 'WILD CARD'), ('blue', 'PEOPLE & PLACES')]
# alternate color/category scheme
#color_names = [('orange', 'SPORTS & LEISURE'), ('green', 'SCIENCE & TECHNOLOGY'),
#               ('magenta', 'ENTERTAINMENT'), ('yellow', 'HISTORY'),
#               ('purple', 'ARTS & LITERATURE'), ('blue', 'GEOGRAPHY')]

spoke_colors = []
# calculate colors of spoke spaces based on observed pattern and plotting order
for i in [4, 2, 1, 5, 0]:
    c_temp = color_names[i:] + color_names[:i]
    spoke_colors.extend(col for col, _ in c_temp)

# calculate and keep track of locations/indices of perimiter spaces
d = {}
idxs = set()
order = [1, 10, 21, 32, 41]
for i, (col, _) in enumerate(color_names):
    d[col] = []
    places = order[i:] + order[:i]
    for val in places:
        idx = (val + (i * 7)) % 42
        d[col].append(idx)
        idxs.add(idx)

# wedge coordinates
wedge_dict = {([p_th[idx] for idx in idxs if idx % 7 == 0][0], 6): col
              for col, idxs in d.items()}

# add 'roll again' spaces
d['darkgray'] = []
for val in range(42):
    if val not in idxs:
        d['darkgray'].append(val)
d['k'] = 42

# indices of just wedge spaces, for plotting with a larger markersize
wedge_d = {col: i for i, (col, _) in enumerate(color_names[3:] + color_names[:3])}

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
markers = [plt.polar([.6], [i], marker='X', color=d['color'], markersize=18,
                     lw=0, markeredgewidth=1.5, markeredgecolor='w',
                     label=d['name'])[0]
            for i, d in enumerate(players)]

# explanatory table
table = mpatches.Rectangle((.795, -.01), .245, .245, fill=True, color='darkgray')
table.set_clip_on(False)
ax.add_patch(table)
for i, (col, topic) in enumerate(color_names):
    ax.text(.8, .2 - (i / 25), topic, color=col, weight='bold', fontsize=14)

# names/colors/current turn legend with wedge tracker
longest_name = max(len(p['name']) for p in players)
offset = (longest_name - 4) / 100
for idx, player in enumerate(players):
    ax.text(.8, .994 - (idx + 1) / 22, player['name'],
                 color=player['color'],
                 fontname='PT Mono',
                 fontsize=14)
    # collected wedge placeholders
    for i in range(6):
        blank = mpatches.Rectangle(((.846 + offset + i * .015),
                                   .992 - (idx + 1) / 22),
                                   .015, .025,
                                   fill=False,
                                   color='k')
        blank.set_clip_on(False)
        ax.add_patch(blank)
token_idx = -1

def get_closest(mx, my):
    ''''Find the closest space on the board to the location of given
    coordinates.'''

    # NOTE: if the click is close to theta=0 but below the line, i.e. slightly
    # less than 2pi, the wrong space will be chosen
    mouse = np.asarray([mx, my])
    dist_2 = np.sum((lines - mouse) ** 2, axis=1)
    idx = np.argmin(dist_2)
    return lines[idx]

def on_key(event):
    global ud
    global token_idx
    global mk_idx
    global current_tag
    global marker

    # only care about SPACE, 'd', and 'w'
    if not event.key in ' wd':
        return

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
        if wedge_color in players[token_idx]['wedges']:
            return
        # adjust the first argument to account for long or short names
        wedge = mpatches.Rectangle((.846 + offset + (len(players[token_idx]['wedges']) * .015),
                                   .992 - (token_idx + 1) / 22),
                                   .015, .025,
                                   fill=True,
                                   color=wedge_color)
        wedge.set_clip_on(False)
        ax.add_patch(wedge)
        players[token_idx]['wedges'].add(wedge_color)
        print(f'Collected {wedge_color} wedge')
        event.canvas.draw()
        return

    # 'd' -- roll the die
    if event.key == 'd':
        # dice rolling indicator
        bbox_image.set_data(dice[0])
        ax.add_artist(bbox_image)
        plt.pause(.5)
        # new roll
        roll = randrange(1, 7)
        print(f'Rolled a {roll}')
        bbox_image.set_data(dice[roll])
        ax.add_artist(bbox_image)
        event.canvas.draw()
        return

    # SPACE -- start next player's turn
    # indicate end of previous player's turn in legend
    try:
        marker.remove()
    except NameError:
        pass
    # remove location tag for previous player
    # probably don't need legend marker as long as this is updated
    try:
        current_tag.remove()
    except:
        pass
    token_idx += 1
    if token_idx == len(players):
        token_idx = 0
    # indicate this player's turn in legend
    #marker = ax.text(.78, .984 - (token_idx + 1) / 22, '*',
    marker = ax.text(.78, .992 - (token_idx + 1) / 22, '\u261e',
                          #color=players[token_idx]['color'],
                          color='k',
                          fontsize=18)
    print(f'Team {players[token_idx]["name"]} to move')
    x, y = markers[token_idx].get_xydata()[0]
    label = markers[token_idx].get_label()
    # indicate location of current player's token
    current_tag = plt.annotate(label, xy=(x, y), weight='bold', color='k',
                               fontsize=12, bbox=dict(boxstyle='round,pad=0.2',
                               fc='w', alpha=0.7))
    event.canvas.draw()
    mk_idx = markers[token_idx]
    # dissociate movement with previous player
    plt.gcf().canvas.mpl_disconnect(ud)

    # activate this player's turn; clicking a location will move their token
    def update(event):
        # maintain location tag for current player
        global current_tag
        try:
            current_tag.remove()
        except ValueError:
            pass
        if event.mouseevent.button != 1:
            return
        x, y = get_closest(event.mouseevent.xdata, event.mouseevent.ydata)
        if np.abs((np.pi * 2) - x) < .01:
            x = 0
        mk_idx.set_data([x], [y])
        current_tag = plt.annotate(label, xy=(x, y), weight='bold', color='k',
                               fontsize=12, bbox=dict(boxstyle='round,pad=0.2',
                               fc='w', alpha=0.7))
        event.canvas.draw()
    ud = plt.gcf().canvas.mpl_connect('pick_event', update)
    return

def start_action(event):
    print(f'Press SPACE to begin {players[0]["name"]}\'s turn')

ud = plt.gcf().canvas.mpl_connect('pick_event', start_action)
token_key = plt.gcf().canvas.mpl_connect('key_press_event', on_key)

plt.show()
