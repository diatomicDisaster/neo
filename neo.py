# Public Python Libraries
from os import path
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import argparse

# orBits Libraries
from rungekutta import make_step
from readinput import read_input

#-----------------------------------------------------------------------------
# First we ask the user for input and output files, and take various measures
# to ensure these are in fact valid files. Once the files have been opened we
# then call the function read_input which reads the input file and creates the
# bodies for the simulation.
#-----------------------------------------------------------------------------

parse = argparse.ArgumentParser(description=
            "I wonder what brought you here? Do it like this:"
        "\n\n  python orbits.py -i myinput.inp -o myoutput.out"
        "\n\nTo see what the input file should look like, head on over to the docs:",
        formatter_class=argparse.RawTextHelpFormatter)

parse.add_argument("-i", "--infile", default=None, type=str, help="Specify the input file, '.inp' suffix.")
parse.add_argument("-o", "--outfile", default=None, type=str, help=
          "Specify the output file, '.out' suffix."
        "\nIf not given, output can be written to console.")
args = parse.parse_args()

# Ask user for input file, check it is valid type and exists, then open.
inName = args.infile
if not inName:
    sys.exit("No input file given, use 'python orbits.py -h' for help.")
checkIn = inName.split(sep='.')
while (len(checkIn) < 2) or (checkIn[1] != "inp"):
    print("Not a valid input file type, must be *.inp!\n")
    inName = input("Specify the input file: ").strip()
    checkIn = inName.split(sep='.')
if not path.exists(inName):
    sys.exit("Could not find the input file, is it in the working directory?")
inFile = open(inName, 'r')

# Ask user for output file. If no file is given, we can output to the console
# but ask first, if the answer is no, ask for output file again. If an output
# file is specified that does not exist then we can create it.
termOut = False
while not termOut:
    outName = args.outfile
    if not outName:
        yn = None
        while yn not in ["Y", "y", "N", "n"]:
            yn = input("No output file given, write to console? [y/n] ").strip()
        if yn in ["Y", "y"]:
            outFile = sys.stdout
            break
        elif yn in ["N", "n"]:
            print("We need an output file :(", file=sys.stdout)
            sys.exit()
        
    else:
        checkOut = outName.split(sep='.')
        if (len(checkOut) < 2) or (checkOut[1] != "out"):
            print("Not a valid output file type, must be *.out!\n")
            continue
        elif not path.exists(outName):
            print("Could not find the output file... Created automatically.")
        outFile = open(outName, 'w+')
        break

# Read the input file and create the bodies
bods, timeStep, nSteps = read_input(inFile, outFile)

sci2 = '.2e'
print("\nPreparing the simulation for the following bodies:", file=outFile)
for bod in bods:
        print("\n - {1} with..."
              "\n   Mass = {2:{0}} Earth Masses"
              "\n   Initial Position (x, y) = ({3:{0}}, {4:{0}}) A.U."
              "\n   Initial Velocity (x, y) = ({5:{0}}, {6:{0}}) A.U. per day"
              .format(sci2, bod.name, bod.mass, *bod.pos, *bod.vel), file=outFile)
        
nBods = len(bods)
colours = [bod.c for bod in bods]

posSteps = np.zeros((nSteps, nBods, 2))
velSteps = np.zeros((nSteps, nBods, 2))
masses      = [bod.mass for bod in bods]
posSteps[0] = [bod.pos for bod in bods]
velSteps[0] = [bod.vel for bod in bods]

for step in range(1, nSteps):
    posSteps[step], velSteps[step] = make_step(timeStep, nBods, masses, 
                                               posSteps[step-1], 
                                               velSteps[step-1])

window = [[-2, 2], [-2, 2]]
fig  = plt.figure(figsize=[6, 6])
ax   = plt.axes(xlim=window[0], ylim=window[1])
dot, = ax.plot([], [], '.')

dots = []
for i in range(nBods):
    dObj = ax.plot([], [], marker='o', color=colours[i], ls='none')[0]
    dots.append(dObj)
    
def ani_init():
    for dot in dots:
        dot.set_data([], [])
    return dots

def animate(i):
    frame = posSteps[i]
    xPosits = [i[0] for i in frame]
    yPosits = [i[1] for i in frame]
    for dNum, dot in enumerate(dots):
        dot.set_data(xPosits[dNum], yPosits[dNum])
    return dots

anim = ani.FuncAnimation(fig, animate, init_func=ani_init, frames=nSteps, interval=10, blit=True)
anim.save('animated.mp4')
