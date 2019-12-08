# Reference for discrete equations:
# http://physics.bu.edu/py502/lectures3/cmotion.pdf

from numpy import zeros_like, array
from numpy import sum as npsum

# Constants
G     = 6.67430e-11     # Netwon's gravitational constant in SI units
m2AU  = 6.684587122e-12 # Metre to astronomical units
kg2ME = 1.6744e-25      # Kilogram to Earth masses
s2dy  = 1.157407407e-5  # Second to days (ass. 24hr/day)

convG = G * m2AU**3 / (kg2ME * s2dy**2) # G in unit [au^3 ME^-1 dy^-2] 

def make_step(stepSize, numBodies, bodyMasses, currentPosits, currentVels):
    """Perform a forward step using the fourth-order Runge-Kutta method.
    
    This function takes the current positions and velocities of a number of
    bodies and performs a single forward time step of Netwon's gravitational
    equations of motion using the 4th order Runge-Kutta method for all bodies.
    
    Arguments:
    stepSize      -- the size of the time step in days.
    numBodies     -- the number of bodies equal to len(bodyMasses).
    bodyMasses    -- a list of masses for each body.
    currentPosits -- a NumPy ndarray of the current positions of all bodies,
                     each element of which has in turn two dimensions: [x, y].
    currentVels   -- a NumPy ndarray of the current velocities of all bodies,
                     each element of which has in turn two dimensions: [x, y].
    
    Returns:
    nextPosits  -- a NumPy ndarray of the next positions of all bodies, each
                   element of which has in turn two dimensions: [x, y].
    currentVels -- a NumPy ndarray of the next velocities of all bodies, each
                   element of which has in turn two dimensions: [x, y].
    
    Note, the order of the position and velocities vectors for each mass in the 
    arguments 'currentPosits' and 'currentVels' must be the same as the order 
    of masses in 'bodyMasses'. The return arrays also have the same ordering.
    """
    
    nextPosit = zeros_like(currentPosits)
    nextVel   = zeros_like(currentVels)
    
    for i in range(numBodies):
        
        iMass  = bodyMasses[i]
        iPosit = currentPosits[i]
        iVel   = currentVels[i]
        
        l1 = stepSize*iVel
        k1 = array([0., 0.])
        for j in range(numBodies):
            if i == j: continue
            
            jMass  = bodyMasses[j]
            jPosit = currentPosits[j]
            
            rVec   = jPosit - iPosit
            rSumSq = npsum(rVec**2)
            k1    += stepSize * convG * jMass * (rVec/rSumSq**1.5)
        
        
        l2 = stepSize * (iVel + k1/2)
        k2 = array([0., 0.])
        for j in range(numBodies):
            if i == j: continue
            
            jMass  = bodyMasses[j]
            jPosit = currentPosits[j]
            
            rVec   = jPosit - (iPosit + l1/2)
            rSumSq = npsum(rVec**2)
            k2    += stepSize * convG * jMass * (rVec/rSumSq**1.5)
       
        
        l3 = stepSize * (iVel + k2/2)
        k3 = array([0., 0.])
        for j in range(numBodies):
            if i == j: continue
            
            jMass  = bodyMasses[j]
            jPosit = currentPosits[j]
            
            rVec   = jPosit - (iPosit + l2/2)
            rSumSq = npsum(rVec**2)
            k3    += stepSize * convG * jMass * (rVec/rSumSq**1.5)
        
        
        l4 = stepSize * (iVel + k3)
        k4 = array([0., 0.])
        for j in range(numBodies):
            if i == j: continue
            
            jMass  = bodyMasses[j]
            jPosit = currentPosits[j]
            
            rVec   = jPosit - (iPosit + l3)
            rSumSq = npsum(rVec**2)
            k4    += stepSize * convG * jMass * (rVec/rSumSq**1.5)
       
        nextPosit[i] = iPosit + (l1 + 2*l2 + 2*l3 + l4)/6
        nextVel[i]   = iVel   + (k1 + 2*k2 + 2*k3 + k4)/6
    
    return nextPosit, nextVel
