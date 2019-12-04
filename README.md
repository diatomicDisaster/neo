# **NEO V0.1**

NEO (**NE**wtonian **O**rbits) is a simulation of Newtonian gravity performed "on-the-fly" using the fourth-order Runge-Kutta time integration method. The bodies and simulation parameters are defined systematically in an '.inp' input file using a range of parameters, an example is [given below](#example-input).

## Getting Started
### Installing

1. Go to https://github.com/diatomicDisaster/Planets, click the green button on the right hand side "Clone or Download".
2. To download the files directly, click "Download ZIP", or to install using git:

```
git clone https://github.com/diatomicDisaster/Planets.git
```

3. The Python libararies `numpy` and `argparse` are required and optionally `matplotlib` if your input file contains the `VISUAL` flag ([more info](#visualisation)), these libraries [can be installed using your chosen package manager](https://packaging.python.org/tutorials/installing-packages/).

### Example Input

Input is provided to the program via a plain text ".inp" file, which is used to define the bodies to be simulated as well as the paramters for the simulation itself. The input file is specified through the command line when the program is run.

```
python neo.py -i myinput.inp
```

An output ".out" file can also be specified, using the following syntax.

```
python neo.py -i myinput.inp -o myoutput.out
```
If the output file does not exist the program will create it automatically, if no output file is specified then the option will be available to write output to the console. In addition to the output file where messages are written, the program also creates a ".steps" file, which contains the position and velocity of each body at each time step.

#### Defining Bodies for the Simulation
The flag `BODY` is used to tell the program that the subsequent lines define a new body for the simulation, the end of the body is marked with the flag `END`. Parameters are specified using a keyword, followed by a colon. The following parameters are available (required ones indicated by an asterisk):

|`keyword`|Description|
|:---:|:---|
|*`name`|The name of the body, purely for the sanity of the user.| 
|*`mass`|The mass of the body, given as a value and units separated by a space. Currently the accepted units are: Earth masses `mE`, Solar masses `mS`, Kilograms `kg`. If no units are given `mE` is assumed.|
|*`position`|The initial position of the body, given as two values separated by a space that specify a vector quantity. Can be given in Cartesian (x, y) or polar form (r, ϕ) (see `polar` keyword below), and can also be defined relative to any other body (see `relative` keyword).|
|*`velocity`|The initial velocity of the body, given as two values separated by a space that specify a vector quantity. Can be given in Cartesian (x, y) or polar form (r, ϕ) (see `polar` keyword below), and can also be defined relative to any other body (see `relative` keyword).|
|`polar`|Additional keyword required only when the position and velocity are defined in polar coordinates, note this keyword does not require a colon ":".|
|`relative`|An optional keyword used to define one body's initial position and velocity relative to another body in the simulation (useful for moons). If the keyword is not present the body is assumed to be defined relative to the origin. Note that the order in which the bodies are given in the input file is not important, moons can be specified before their host planets.|
|`colour`|An optional keyword that specifies the colour to use for this body in the visualisation, valid values are any [`matplotlib` colour](https://matplotlib.org/2.0.2/api/colors_api.html).|

An arbitrary number of bodies can be specified in any order, the order in which the parameters are given is also not important, however spaces between keywords and values *is important*. An example definition for an Earth analog defined relative to another body ("Sun") is given below:

```
BODY 
name: Earth
mass: 1 mE
position: 1 0
velocity: 0 2*pi/365
polar
relative: Sun
colour: #0099ff
END
```
#### Defining the simulation
The flag `SIMULATION` is used to tell the program that subsequent lines define the paramters for the simulation, and the flag `END` is used to terminate the simulation section. There are two parameters required, both have units:

|`keyword`|Description|
|:---:|:---|
|`dt`|The time step for the simulation, specified with a value and units. Currently accepted units are: days (`days` or `dy`), years (`years` or `yr`) and hours (`hours`, `hrs`, or `hr`). The simulation is accurate to fourth order in time.
|`duration`|The duration of the simulation, specified with a value and units - as above.|

An example simulation with a timestep of 12 hours and a duration of 182.5 days is shown below.

```
SIMULATION
dt: 0.5 day
duration: 0.5 year
END
```

### Output
The program provides updates and writes error messages to the [output file specified when the program is run](#example-input).

```
python neo.py -i myinput.inp -o myoutput.out
```

In addition to the output file, the program creates a ".steps" file. This file contains the position and velocity of each body at every time step. The first column of each row in the file gives the time step number, the next four columns give the x, y, v_x, v_y values for the first body, and each four columns thereafter represent further bodies. The order of the bodies is given at the top of the ".steps" file for reference.

#### Visualisation
An ".mp4" animation can also be rendered using [`matplotlib.animation`](https://matplotlib.org/3.1.1/api/animation_api.html) if the input file contains the single line flag `VISUAL`, this is poorly implemented at present and this is not advised for simulations with > 1000 time steps.
