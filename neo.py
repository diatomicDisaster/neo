# Public Python Libraries
from os import path
import sys
from numpy import array, absolute, amax, zeros, log, log10
import argparse

# orBits Libraries
from readinput import read_input

int8 = '8d'
sci2 = '.2e'
sci8 = '.8e'
ws6  = '      '
ws4  = '    '

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

parse.add_argument('-i', '--infile', default=None, type=str, help=
                   "Specify the input file, '.inp' suffix.")
parse.add_argument('-o', '--outfile', default=None, type=str, help=
                   "Specify the output file, '.out' suffix."
                   "\nIf not given, output can be written to console.")
parse.add_argument('-p', action='store_true', help=
                   "Perform computations in parallel (requires Numba).")

args = parse.parse_args()

# Ask user for input file, check it is valid type and exists, then open.
inName = args.infile
if not inName:
    sys.exit("No input file given, use 'python neo.py -h' for help.")
checkIn = inName.split(sep='.')
while (len(checkIn) < 2) or (checkIn[1] != "inp"):
    print("Not a valid input file type, must be *.inp!\n")
    inName = input("Specify the input file: ").strip()
    checkIn = inName.split(sep='.')
if not path.exists(inName):
    sys.exit("Could not find the input file, is it in the working directory?")
inFile = open(inName, 'r')
stepFile = open("{0}.steps".format(checkIn[0]), 'w+')


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
            print("We need an output file.", file=sys.stdout)
            sys.exit()
        
    else:
        checkOut = outName.split(sep='.')
        if (len(checkOut) < 2) or (checkOut[1] != "out"):
            print("Not a valid output file type, must be *.out!\n", file=sys.stdout)
            continue
        elif not path.exists(outName):
            print("Could not find the output file... Created automatically.", file=sys.stdout)
        outFile = open(outName, 'w+')
        break

print("\n"
    "\n                   @@@@@                                                    "
    "\n                 @@@@@@@@@                         #########                "
    "\n                 @@@@@@@@@                      OOOO         ######         "
    "\n          ######   @@@@@            EEEE      OO    OO             ###      "
    "\n       #####              NN     EEE          0O     OO               ##    "
    "\n     ###         NNNN      NN     EE  EEEE     0O     OO                ##  "
    "\n   ###            NN NNN    NN     EEE          0O     OO               ### "
    "\n  ###              NN   NNN  NN     EE   EEEE     0OOOO                 ### "
    "\n  ###               NN     NNNNN      EEE                             ####  "
    "\n   ####              NN                        @@@@@@@              #####   "
    "\n     #####                                   @@@@@@@@@@@        #######     "
    "\n         #####                              @@@@@@@@@@@@@   #######         "
    "\n              ############                  @@@@@@@@@@@@@                   "
    "\n                                             @@@@@@@@@@@                    "
    "\n                                               @@@@@@@                      "
    "\n"
    "\n                             Wilfrid Somogyi                                "
    "\n                     github.com/diatomicDisaster/neo                        "
    "\n",
    file=outFile)


if args.p:
    from rungekutta import make_step_par as make_step
    try:
        from numba import njit, prange
        print("Parallel execution enabled.", file=outFile)
    except:
        print("Error: Argument '-p' given, but cannot find numba.", file=outFile)
        sys.exit()
else:
    from rungekutta import make_step

# Read the input file and create the bodies
bods, timeStep, nSteps, doVis, figsize, scale = read_input(inFile, outFile)

print("\nPreparing the simulation for the following bodies:", file=outFile)
for bod in bods:
        print("\n - {1} with..."
              "\n   Mass = {2:{0}} Earth Masses"
              "\n   Initial Position (x, y) = ({3:{0}}, {4:{0}}) A.U."
              "\n   Initial Velocity (x, y) = ({5:{0}}, {6:{0}}) A.U. per day"
              .format(sci2, bod.name, bod.mass, *bod.pos, *bod.vel), file=outFile)
        
nBods = len(bods)

posSteps = zeros((nSteps, nBods, 2))
velSteps = zeros((nSteps, nBods, 2))
masses      = array([bod.mass for bod in bods])
posSteps[0] = array([bod.pos for bod in bods])
velSteps[0] = array([bod.vel for bod in bods])

print("\nBeginning forward time steps...", file=outFile)
print(*[bod.name for bod in bods], file=stepFile)
for step in range(1, nSteps):
    posSteps[step], velSteps[step] = make_step(timeStep, nBods, masses, 
                                               posSteps[step-1], 
                                               velSteps[step-1])
    for i, bodPos in enumerate(posSteps[step]):
        bodVel = velSteps[step][i]
        bodStr = "{2:{0}}{1}{3:{0}}{1}{4:{0}}{1}{5:{0}}".format(sci8, ws4, *bodPos, *bodVel)
        print(bodStr, end=ws6, file=stepFile)
    print('', file=stepFile)

stepFile.close()
    
print("Simulation complete, step file closed.", file=outFile)

if scale == 'log':
    posSteps = log10(posSteps)
elif scale == 'ln':
    posSteps = log(posSteps)

if doVis:
    print(  "Beginning animation, with:"
          "\n  Figure size = {0} inches".format(figsize), file=outFile)
    import matplotlib.pyplot as plt
    import matplotlib.animation as ani
    
    scale  = figsize/6
    marg   = 1.1
    s      = marg*amax(absolute(posSteps))
    window = [[-s, s], [-s, s]]
    
    fig  = plt.figure(figsize=(figsize,figsize))
    ax   = plt.axes(xlim=window[0], ylim=window[1])
    dot, = ax.plot([], [], '.')
    
    dots = []
    for i in range(nBods):
        dObj = ax.plot([], [], marker='o', markersize=scale*bods[i].ms, color=bods[i].c, ls='none')[0]
        dots.append(dObj)
        
    def ani_init():
        for dot in dots:
            dot.set_data([], [])
        return dots
    
    def animate(i, nSteps):
        xPosits = posSteps[i,:,0]
        yPosits = posSteps[i,:,1]
        for dNum, dot in enumerate(dots):
            dot.set_data(xPosits[dNum], yPosits[dNum])
        return dots
    
    anim = ani.FuncAnimation(fig, animate, init_func=ani_init, fargs=(nSteps,),
                            frames=nSteps, interval=10, blit=True)
    anim.save('animated.mp4')
    
    print("\nAnimation complete, closing files.", file=outFile)
    
outFile.close()
inFile.close()
