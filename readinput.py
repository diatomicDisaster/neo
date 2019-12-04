import sys
from numpy import pi, array, cos, sin

cases = ["BODY", "SIMULATION"]#, "VISUAL"]
checks = [False for i in cases]

# A dictionary of conversion factors.
convert = {
        "mE"  : 1.,
        "mS"  : 332946.,
        "kg"  : 5.972e24,
        "year": 365.,
        "yr"  : 365.,
        "day" : 1.,
        "dy"  : 1.,
        "hour": 1./24,
        "hrs" : 1./24,
        "hr"  : 1./24
        }

class Body:
    """An object to store information about each body."""
    def __init__(self):
        self.name  = 'Unnamed'
        self.mass  = 0.
        self.pos   = array([0., 0.])
        self.vel   = array([0., 0.])
        self.rel   = 'centre'
        self.polar = False
        self.c     = '#787878'
        
    def de_polar(self):
        self.vR, self.vPhi = self.vel
        self.r, self.phi   = self.pos
        self.pos = array([self.r*cos(self.phi), self.r*sin(self.phi)])
        self.vel = array([self.vR*cos(self.phi) - self.vPhi*sin(self.phi),
                         self.vR*sin(self.phi) + self.vPhi*cos(self.phi)])
        self.polar = False

def create_body(bodyLines, inFile, outFile):
    """Create a new body using a given set of parameters.
    
    This function takes a list of strings that contain the parameters
    required to define a new body in the simulation. The order of the strings
    is not important, for a full list of parameters that are required, please
    refer to the documentation.
    
    Argumnets:
    bodyLines -- a list of strings, the relevant lines from the input file.
    inFile    -- the global input file.
    outFile   -- the global output file.
    
    Returns:
    bod -- a Body object for the current body.
    """
    
    # Create body and begin reading the lines
    bod = Body()
    for line in bodyLines:
        # Polar coordinates is a one-line parameter, treat separately
        if line in ["Polar", "polar"]:
            bod.polar = True
        else:
            keyword = line.split(sep=':')[0].strip()
            line    = line.split(sep=':')[1].split()
            if keyword in ["Name", "name"]:
                bod.name = line[0]
            elif keyword in ["Mass", "mass"]:
                if len(line) == 1:
                    bod.mass = float(line[0]) * convert['mE']
                    print("Warning: No units found for mass of {}, assuming mE."
                          .format(bod.name), file = outFile)
                else:
                    bod.mass = float(line[0]) * convert[line[1]]
            elif keyword in ["Position", "position"]:
                bod.pos = array([eval(i) for i in line], dtype='float64')
            elif keyword in ["Velocity", "velocity"]:
                #if line[0] in ["Stable", "stable"]:
                    
                bod.vel = array([eval(i) for i in line], dtype='float')
            elif keyword in ["Relative", "relative"]:
                bod.rel = line[0]
            elif keyword in ["Colour", "colour", "Color", "color"]:
                bod.c = line[0]
            else:
                print("Error: Unrecognised keyword in body decleration. " 
                      "\n  Check your input file!", file = outFile)
                sys.exit()
    
    # If polar coordinates were declared then convert to Cartesian
    if bod.polar:
        bod.de_polar() 
    return bod

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
        if not line_:
            continue
        elif line_.upper() in cases:
            print("Error: encountered new case before end of last."
                  "\n  Have you forgotten an 'END'?", file=outFile)
            sys.exit()
        elif line_.upper() == "END":
            return bodyLines
        else:
            bodyLines.append(line_)

def read_input(inFile, outFile):
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
    
    print("\n---------------" 
          "\nReadInput: read_input()"
          "\n---------------"
          "\nReading input from '{}'"
            .format(inFile.name), file=outFile) 
    
    doVis = False
    bods = []
    for line in inFile:
        # Strip trailing, leading whitespace from line, skip if empty
        line = line.rstrip('\n').strip()
        if not line: 
            continue
        # Read a body if line begins body definition
        if line == "BODY":
            checks[cases.index(line)] = True
            bodLines = count_lines(inFile, outFile)
            bod = create_body(bodLines, inFile, outFile)
            bods.append(bod)
        elif line == "SIMULATION":
            checks[cases.index(line)] = True
            isSim = True
            simLines = count_lines(inFile, outFile)
            for line_ in simLines:
                keyword = line_.split(sep=':')[0].strip()
                val     = line_.split(sep=':')[1].split()
                if len(val) != 2:
                    print("Error: Not enough parameters."
                          "\n  Do time step and duration both have units?", 
                          file=outFile)
                    sys.exit()
                if keyword == "dt":
                    timeStep = float(val[0]) * convert[val[1]]
                elif keyword in ["Duration", "duration"]:
                    duration = float(val[0]) * convert[val[1]]
                    nSteps   = round(duration/timeStep)
        elif line == "VISUAL":
            checks[cases.index(line)] = True
            doVis = True
            continue
    
    missing = [i for i, x in enumerate(checks) if not x]
    if len(missing) > 0:
         print("Error: No {} case found."
               "\n  Is it in the input file?"
               .format([cases[i] for i in missing]), file=outFile)
         sys.exit()
    # Now globalise coordinates for bodies defined relative to one another.
    print("Globalising the coordinates for ", end='', file=outFile)
    none = True
    for bod in bods:
        while bod.rel != 'centre':
            none = False
            print(bod.name, end='... ', file=outFile)
            for relBod in bods:
                if relBod.name == bod.rel:
                    bod.pos += relBod.pos
                    bod.vel += relBod.vel
                    bod.rel  = relBod.rel
    if none:
        print("...None!", file=outFile)
    else:
        print()
                    
    return bods, timeStep, nSteps, doVis
