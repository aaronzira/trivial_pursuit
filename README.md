# Trivial Pursuit board

A convenient way of allowing other players to see the board while playing over video calls

# Requirements

- python >= 3.6
- matplotlib
- numpy

# Usage

- provide a string of space-separated pairs of \<TEAMNAME\>\_\<COLOR\>
	- named colors can be found in [matplotlib docs](https://matplotlib.org/3.1.0/gallery/color/named_colors.html)
	- hex color codes may be used

```
python trivial_pursuit.py TEAM1_r TEAM2_chartreuse team3_#c0b7ff
```

# Gameplay

Everything is controlled with the 'd' key, 'w' key, SPACE key, and LEFT MOUSE CLICK:

- **SPACE**: end the current team's turn, and move on to the next
- **'d'**: roll the 'die', displaying a number in [1, 6] to indicate number of moves to take
- **'w'**: collect the corresponding 'wedge' after correctly answering a question on an intersection space
	- NOTE: accidentally pressing 'q' will close the plot.
- **LEFT MOUSE CLICK**: choose the space to which the current team will move

Current turn is indicated with an asterisk to the left of the team's name in the legend, as are colors of collected wedges
