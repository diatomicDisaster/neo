import sys
from numpy import pi, array, cos, sin, log10

cases = ["BODY", "SIMULATION", "VISUAL"]

# A dictionary of conversion factors.
convert = {
        "au"  : 1.,
        "AU"  : 1.,
        "m"   : 1/149597870700.,
        "km"  : 1/149597870.7,
        "mE"  : 1.,
        "mS"  : 332946.,
        "kg"  : 5.972e24,
        "year": 365.,
        "years" : 365.,
        "yr"  : 365.,
        "yrs" : 365.,
        "day" : 1.,
        "days": 1.,
        "dy"  : 1.,
        "dys" : 1.,
        "hour": 1./24,
        "hrs" : 1./24,
        "hr"  : 1./24,
        "second" : 1./(24*60*60),
        "seconds": 1./(24*60*60),
        "sec" : 1./(24*60*60),
        "secs": 1./(24*60*60),
        "s"   : 1./(24*60*60)
        }

class Body:
    """An object to store information about each body."""
    def __init__(self):
        self.name    = 'Unnamed'
        self.mass    = 0.
        self.pos     = array([0., 0.])
        self.vel     = array([0., 0.])
        self.rel     = 'centre'
        self.polar   = False
        self.c       = '#787878'
        self.ms      = 0.1
        self.posUnit = 'au'
        
    def de_polar(self):
        self.vR, self.vPhi = self.vel
        self.r, self.phi   = self.pos
        self.pos = array([self.r*cos(self.phi), self.r*sin(self.phi)])
        self.vel = array([self.vR*cos(self.phi) - self.vPhi*sin(self.phi),
                         self.vR*sin(self.phi) + self.vPhi*cos(self.phi)])
        self.polar = False
        
    def calc_rad(self):
         self.rad = self.mass**(1/3)
         self.ms  = 5*log10(self.rad**(1/2)+1.0)


def count_lines(inFile, outFile):
    """Counts the number of lines until the end of the current input section.
    
    This function counts the number of lines from the current position in the
    input file until the next END statement, then returns the lines in between
    and the line number of the END statement.
    
    Arguments:
    lineNum -- the current line in inFile, where this input section begins.
    inFile  -- the global input file.
    outFile -- the global output file.
    
    Returns:
    bodyLines -- a list of strings that are the lines in between lineNum and
                 the END statement.
    lineNum_  -- the line number of the END statement.
    """
    
    bodyLines = []
    # Begin iteratin lines, starting at line 'lineNum'
    for line_ in inFile:
        line_ = line_.rstrip('\n').strip()
        if (not line_) or (line_[0] == '!'):
            continue
        elif line_.upper() in cases:
            print("Error: encountered new case before end of last."
                  "\n  Have you forgotten an 'END'?", file=outFile)
            sys.exit()
        elif line_.upper() == "END":
            return bodyLines
        else:
            bodyLines.append(line_)

def input_reader(inFile, outFile):
    """Control function for reading the input file, discriminates input cases.
    
    Calls the appropriate processing function for the input cases decribed in
    the documentation, namely: BODY and SIMULATION
    
    Arguments:
    inFile  -- the global input file.
    outFile -- the global output file.
    
    Returns:
    bods     -- a list of bodies.
    timeStep -- the time step of the simulation.
    nSteps   -- the number of steps to simulate.
    """
    
    print("\nReading input from '{}'".format(inFile.name), file=outFile) 
   
    # Checks for each case
    nBods = 0
    isBod = False
    isSum = False
    isVis = False
    
    # Default values for visualisation
    figsize = 6
    visTime = 30
    FPS     = 25
    visName = 'animated'
    
    bods = []
    for line in inFile:
        # Strip trailing, leading whitespace from line, skip if empty
        line = line.rstrip('\n').strip()
        if (not line) or (line[0] == '!'): 
            continue
        
        # Body case
        if line == "BODY":
            nBods += 1
            isBod = True
            bodLines = count_lines(inFile, outFile)
            # Create body and begin reading the lines
            bod = Body()
            for line in bodLines:
                # Polar coordinates is a one-line parameter, treat separately
                if line in ["Polar", "polar"]:
                    bod.polar = True
                else:
                    keyword = line.split(sep=':')[0].strip()
                    if keyword in ["Name", "name"]:
                        bod.name = line.split(sep=':')[1].strip()
                    else:
                        line    = line.split(sep=':')[1].split()
                        if keyword in ["Name", "name"]:
                            bod.name = line[0]
                        elif keyword in ["Mass", "mass"]:
                            bod.mass = float(line[0])
                            if len(line) == 1:
                                print("Warning: No units found for mass "
                                      "of body {0}, assuming mE."
                                      .format(nBods), file = outFile)
                            elif len(line) == 2:
                                bod.mass *= convert[line[1]]
                            else:
                                print("Error: Invalid number of arguments "
                                      "given for mass of body {0}."
                                      "\n  Check your input file!"
                                      .format(nBods), file=outFile)
                                sys.exit()
                        elif keyword in ["Position", "position"]:
                            bod.pos = array([eval(i) for i in line[:2]], 
                                            dtype='float64')
                            if len(line) == 2:
                                print("Warning: No units found for position "
                                      "of body {0}, assuming A.U."
                                      .format(nBods), file=outFile)
                            elif len(line) == 3:
                                bod.posUnit = line[2]
                            else:
                                print("Error: Invalid number of arguments "
                                      "given for position of body {0}."
                                      "\n  Check your input file!"
                                      .format(nBods), file=outFile)
                                sys.exit()
                        elif keyword in ["Velocity", "velocity"]:
                            bod.vel = array([eval(i) for i in line[:2]], 
                                            dtype='float64')
                            if len(line) == 2:
                                print("Warning: No units found for velocity "
                                      "of body {0}, assuming A.U/day."
                                      .format(nBods), file=outFile)
                            elif len(line) == 3:
                                units = line[2].split(sep='/')
                                bod.vel *= convert[units[0]]/convert[units[1]]
                            else:
                                print("Error: Invalid number of arguments "
                                      "given for velocity of body {0}."
                                      "\n  Check your input file!"
                                      .format(nBods), file=outFile)
                                sys.exit()
                        elif keyword in ["Relative", "relative"]:
                            if len(line) == 1:
                                bod.rel = line[0]
                            else:
                                print("Error: Invalid number of arguments "
                                      "given for colour of body {0}."
                                      "\n  Check your input file!"
                                      .format(nBods), file=outFile)
                                sys.exit()
                        elif keyword in ["Colour", "colour", "Color", "color"]:
                            if len(line) == 1:
                                bod.c = line[0]
                            else:
                                print("Error: Invalid number of arguments "
                                      "given for colour of body {0}."
                                      "\n  Check your input file!"
                                      .format(nBods), file=outFile)
                                sys.exit()
                        else:
                            print("Error: Unrecognised keyword in body decleration. " 
                                  "\n  Check your input file!", file = outFile)
                            sys.exit()
             
            # If polar coordinates were declared then convert to Cartesian.
            if bod.polar:
                bod.pos[0] = bod.pos[0]*convert[bod.posUnit] 
                bod.de_polar()
            else:
                bod.pos = bod.pos*convert[bod.posUnit]
            bods.append(bod)
            
            # Check mass of body is not zero.
            if bod.mass == 0.:
                print("Error: Mass of body {0} is equal to 0."
                      "\n  Check your input file!"
                      .format(bod.name), file=outFile)
                sys.exit()
        
        # Simulation case
        elif line == "SIMULATION":
            isSim      = True
            
            isSteps    = False
            isDuration = False
            isNSteps   = False
            
            simLines = count_lines(inFile, outFile)
            for line_ in simLines:
                keyword = line_.split(sep=':')[0].strip()
                val     = line_.split(sep=':')[1].split()
                if (keyword in ["dt", "Duration", "duration"]) \
                and (len(val) != 2):
                    print("Error: Not enough parameters for keyword in 'SIMULATION'."
                          "\n  Does {0} have units?"
                          .format(keyword), file=outFile)
                    sys.exit()
                if keyword == "dt":
                    timeStep = float(val[0]) * convert[val[1]]
                    isSteps  = True
                elif keyword in ["Duration", "duration"]:
                    duration   = float(val[0]) * convert[val[1]]
                    isDuration = True
                elif keyword in ["Steps", "steps"]:
                    nSteps = int(val[0])
                    isNSteps = True
                else:
                    print("Error: Unrecognised keyword in 'SIMULATION'."
                          "\n  Check your input file!", file=outFile)
                    sys.exit()
            
            # Some parameters conflict and are mutually exclusive
            if (isSteps and isDuration and isNSteps):
                print("Error: 'dt', 'duration' and 'steps' are all defined "
                      "for SIMULATION." 
                      "\n  Please choose only two.", file=outFile)
                sys.exit()
            elif (isDuration and isNSteps) and not isSteps:
                timeStep = duration/nSteps
            elif (isSteps and isDuration) and not isNSteps:
                nSteps = int(duration/timeStep)
            elif (isSteps and isNSteps) and not isDuration:
                pass
            else:
                print("Error: At least one keyword is missing from 'SIMULATION'."
                      "\n  Check your input file!", file=outFile)
                sys.exit()
                
        
        # Visual case
        elif line == "VISUAL":
            isVis = True
            visLines = count_lines(inFile, outFile)
            for line_ in visLines:
                keyword = line_.split(sep=':')[0].strip()
                val     = line_.split(sep=':')[1].strip()
                if keyword in ["Size", "size"]:
                    figsize = float(val)
                elif keyword in ["Time", "time"]:
                    visTime = int(val)
                elif keyword in ["FPS", "fps"]:
                    if val in ["All", "all"]:
                        FPS = 'all'
                    else:
                        FPS = int(val)
                elif keyword in ["File", "file"]:
                    visName = val
                else:
                    print("Error: Unrecognised keyword in visual decleration."
                         "\n  Check your input file!", file=outFile)
                    sys.exit()
        
        # If not valid case, raise error  
        else:
            print("Error: Unrecognised flag {0}."
                  "\n  Check your input file!".format(line), file=outFile)
            sys.exit()
    
    exit = False
    for i, case in enumerate([isBod, isSim]):
        if not case:
            print("Error: No {} case found, but is required."
                  "\n  Is it in the input file?"
                .format(cases[i]), file=outFile)
            exit = True 
    if exit: sys.exit()
    
    # Now globalise coordinates for bodies defined relative to one another.
    print("Globalising the coordinates for ", end='', file=outFile)
    none = True
    for bod in bods:
        # Also calculate the body's radius and marker size
        bod.calc_rad()
        while bod.rel != 'centre':
            none = False
            print(bod.name, end='... ', file=outFile)
            noBod = True
            for relBod in bods:
                if relBod.name == bod.rel:
                    noBod = False
                    bod.pos += relBod.pos
                    bod.vel += relBod.vel
                    bod.rel  = relBod.rel
            if noBod:
                print("Error: Could not globalise coordinates for {0}, "
                     "relative body {1} not found."
                     .format(bod.name, bod.rel), file=outFile)
    if none:
        print("...None!", file=outFile)
    else:
        print(file=outFile)
                    
    print("Finished reading input.", file=outFile)
    return bods, timeStep, nSteps, isVis, figsize, visTime, FPS, visName
