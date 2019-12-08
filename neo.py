# NEO is an expansible, general code for simulating Newtonian motion of


# Public Python Libraries
from os import path
import sys
from numpy import array, absolute, amax, zeros, log, log10
import argparse

# orBits Libraries
from readinput import input_reader

int8 = '8d'
sci2 = '.2e'
sci8 = '.8e'
ws6  = '      '
ws4  = '    '
ws2  = '  '

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

print("\n------------"
      "\nBegin output"
      "\n------------", file=outFile)

if args.p:
    try:
        from numba import njit, prange
        from rkpar import make_step
        print("Argument '-p' given, using numba parallelised Runge-Kutta.", file=outFile)
    except:
        print("Error: Argument '-p' given, but cannot find numba.", file=outFile)
        sys.exit()
else:
    from rknopar import make_step
    print("Argument '-p' not given, will no compute in parallel.", file=outFile)
    
# Read the input file and create the bodies
bods, timeStep, nSteps, doVis, figSize, visTime, FPS, visName \
    = input_reader(inFile, outFile)

print("\nPreparing the simulation for the following bodies:", file=outFile)
for bod in bods:
        print(  " - {1} with..."
              "\n   Mass = {2:{0}} Earth Masses"
              "\n   Initial Position (x, y) = ({3:{0}}, {4:{0}}) A.U."
              "\n   Initial Velocity (x, y) = ({5:{0}}, {6:{0}}) A.U. per day\n"
              .format(sci2, bod.name, bod.mass, *bod.pos, *bod.vel), file=outFile)

# Initialise bodies
print("Setting initial conditions.", file=outFile)
nBods = len(bods)
posSteps = zeros((nSteps+1, nBods, 2))
velSteps = zeros((nSteps+1, nBods, 2))
posSteps[0] = array([bod.pos for bod in bods])
velSteps[0] = array([bod.vel for bod in bods])
masses      = array([bod.mass for bod in bods])

print(*[bod.name for bod in bods], file=stepFile)
print("Beginning forward time steps...", file=outFile)
for step in range(1, nSteps+1):
    posSteps[step], velSteps[step] = make_step(timeStep, nBods, masses, 
                                               posSteps[step-1], 
                                               velSteps[step-1])
    for i, bodPos in enumerate(posSteps[step]):
        bodVel = velSteps[step][i]
        bodStr = "{2:{0}}{1}{3:{0}}{1}{4:{0}}{1}{5:{0}}".format(sci8, ws2, *bodPos, *bodVel)
        print(bodStr, end=ws6, file=stepFile)
    print('', file=stepFile)

stepFile.close()    
print("Simulation complete, step file closed.", file=outFile)

if doVis:
    import matplotlib.animation as ani
    import matplotlib.pyplot as plt

    print("\nSetting animation parameters.", file=outFile)
    if FPS == 'all':
        frameStep = 1
        FPS = nSteps/visTime
    else:
        frameStep = round(nSteps/(FPS*visTime))
        if (frameStep == 0):
            frameStep = 1
            
    nFrames = int(nSteps/frameStep)    
    scale  = figSize/6
    marg   = 1.1
    s      = marg*amax(absolute(posSteps))
    window = [[-s, s], [-s, s]]
    
    print("Beginning animation, with:"
          "\n  Figure size = {0} x {0} inches"
          "\n  Window in the range x, y = [-{1}, {1}] A.U"
          "\n  Frame rate = {2} FPS"
          "\n  Interval = {3} ms"
          "\n  Duration = {4} s"
          "\n  {5} frames"
          "\nThis might take a while...".format(figSize, s, FPS, 1e3/FPS, visTime, nFrames), file=outFile)
    
    fig  = plt.figure(figsize=(figSize,figSize))
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
    
    def animate(i, frameStep):
        xPosits = posSteps[i*frameStep,:,0]
        yPosits = posSteps[i*frameStep,:,1]
        for dNum, dot in enumerate(dots):
            dot.set_data(xPosits[dNum], yPosits[dNum])
        return dots
    
    anim = ani.FuncAnimation(fig, animate, init_func=ani_init, fargs=(frameStep,),
                            frames=nFrames, interval=1e3/FPS, blit=True)
    anim.save("{0}.mp4".format(visName))
    
    print("Animation complete.", file=outFile)

print("Done!", file=sys.stdout)
