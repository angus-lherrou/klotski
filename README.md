### Even a Broken Klotski... [0.1.2]

Script that plays [Klotski](https://en.wikipedia.com/wiki/Klotski) badly.  
Usually doesn't win.  
Maybe in version 0.2.

#### Dependencies

* [`termcolor`](https://pypi.org/project/termcolor/)

#### Manual

```
usage: klotski.py [-h] [--step STEP] [--json JSON] [--play] [--demo]

optional arguments:
  -h, --help   show this help message and exit
  --step STEP  Seconds between moves; default is 2
  --json JSON  Load your own game board! See original_board.json for format.
  --play       Play the game yourself!
  --demo       Watch a demo where the computer wins
```
Recommended commands:
* `python klotski.py --step 0`: watch the computer try to solve it in 10,000 random-ish moves
* `python klotski.py --play`: try to solve it yourself!
* `python klotski.py --demo --step 0.1`: watch the shortest(?) solution sequence