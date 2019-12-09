# **NEO V0.1**

NEO (**NE**wtonian **O**rbits) is a simulation of Newtonian gravity performed "on-the-fly" using the fourth-order Runge-Kutta time integration method. The bodies and simulation parameters are defined systematically in an '.inp' input file using a range of parameters, an example is [given below](#example-input).

## Getting Started
### Installing

1. To download the files directly, go to https://github.com/diatomicDisaster/neo, click the green button on the right hand side "Clone or Download" and select "Download ZIP".

2. To install using git:

```
git clone https://github.com/diatomicDisaster/neo.git
```
### Dependencies
3. Only the `numpy` library is required. Additional libraries are optionally required for full functionality: `matplotlib` if your input file contains the `VISUAL` flag for animating the simulation ([more info](#visualisation)) and `numba` if the program is called with the command line argument `-p`, which enables parallel computing. These libraries [can be installed using your chosen package manager](https://packaging.python.org/tutorials/installing-packages/).

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

The final command line argument is an optional flag `-p`. When used, the computation of gravitational interactions at each time step is performed in parallel using [Numba](http://numba.pydata.org/).

A collection of example input, output and step files are found in the `/examples` directory, including a simulation of analogs for the first six planets in the solar system, and a ficticious binary star system. 

#### Defining Bodies for the Simulation
The flag `BODY` is used to tell the program that the subsequent lines define a new body for the simulation, the end of the body is marked with the flag `END`. Parameters are specified using a keyword, followed by a colon. The following parameters are available (required ones indicated by an asterisk):

|`keyword`|Description|
|:---:|:---|
|*`name`|The name of the body, purely for the sanity of the user.| 
|*`mass`|The mass of the body, given as a value and units separated by a space. Currently the accepted units are: Earth masses `mE`, Solar masses `mS`, Kilograms `kg`. If no units are given `mE` is assumed.|
|*`position`|The initial position of the body, given as two values separated by a space that specify a vector quantity, followed by units. Currently allowed units for position are astronomical units`au`, kilometres `km` and metres `m`, default is `au`. Can be given in Cartesian (x, y) or polar form (r, ϕ) (see `polar` keyword below), and can also be defined relative to any other body (see `relative` keyword).|
|*`velocity`|The initial velocity of the body, given as two values separated by a space that specify a vector quantity, followed by units in the form `km/s`, where `km` and `s` can be replaced with any valid units for position and time respectively, default `au/dy`. Can be given in Cartesian (x, y) or polar form (r, ϕ) (see `polar` keyword below), and can also be defined relative to any other body (see `relative` keyword).|
|`polar`|Additional keyword required only when the position and velocity are defined in polar coordinates, note this keyword does not require a colon ":".|
|`relative`|An optional keyword used to define one body's initial position and velocity relative to another body in the simulation (useful for moons). If the keyword is not present the body is assumed to be defined relative to the origin. Note that the order in which the bodies are given in the input file is not important, moons can be specified before their host planets.|
|`colour`|An optional keyword that specifies the colour to use for this body in the visualisation, valid values are any html hex colour codes.|

An arbitrary number of bodies can be specified in any order, the order in which the parameters are given is also not important, however spaces between keywords and values *is important*. An example definition for an Earth analog defined relative to another body ("Sun") is given below:

```
BODY 
name: Earth
mass: 1 mE
position: 1 0 au
velocity: 0 2*pi/365 au/dy
polar
relative: Sun
colour: #0099ff
END
```
#### Defining the simulation
The flag `SIMULATION` is used to tell the program that subsequent lines define the paramters for the simulation, and the flag `END` is used to terminate the simulation section. There are three keyword arguments available to define the simulation, exactly two must be given, and the third is automatically inferred. If the time step `dt` and the `duration` of the simulation are given, then the number of steps to be iterated `duration`/`dt` is calculated. If the time step `dt` and the number of `steps` are given, then the duration of the simulation `dt` x `steps` is calculated. Lastly, if the `duration` and number of `steps` is given, then the time step `duration`/`steps` is calculated.

|`keyword`|Description|
|:---:|:---|
|`dt`|The time step for the simulation, specified with a value and units. Currently accepted units are: days (`days` or `dy`), years (`years` or `yr`), hours (`hours`, `hrs`, or `hr`) and seconds (`seconds`, `secs`, or `s`). The simulation is accurate to fourth order in time.
|`duration`|The duration of the simulation, specified with a value and units - as above.|
|`steps`| The number of time steps to perform the simulation for. |

An example simulation with a timestep of 12 hours and a duration of 182.5 days is shown below.

```
SIMULATION
dt: 0.5 day
duration: 0.5 year
END
```

### Output
The program provides updates and writes error messages to the [output file specified at runtime](#example-input). If no output file is provided, the program will ask before writing output to the console. If an output file is provided but it does not exist, the program will automatically create the output file.

```
python neo.py -i myinput.inp -o myoutput.out
```

In addition to the output file, the program creates a ".steps" file. This file contains the position and velocity of each body at every time step. The first column of each row in the file gives the time step number, the next four columns give the x, y, v<sub>x</sub>, v<sub>y</sub> values for the first body, and each four columns thereafter represent further bodies. The order of the bodies is given at the top of the ".steps" file for reference.

#### Visualisation
An ".mp4" animation can also be rendered using [`matplotlib.animation`](https://matplotlib.org/3.1.1/api/animation_api.html) if the input file contains the case `VISUAL`, ended with the usual `END` statement. A range of keyword arguments can be given to specify the animation.

|`keyword`|Description|
|:---:|:---|
|`size`|The size of the animation image in inches. The image is always square so only one number should be given. The default if no value is given is 6 inches.|
|`time`|The runtime of the final animation in seconds. The default is 30 seconds.|
|`FPS` |The framerate (per second) for the animation, alternatively the value `all` can be given, in which case every step calculated in the simulation is shown at the requisite framrate for the given value of `time`. The default `FPS` value is 25 frames per second.|
|`file`|The prefix of the file to which the animation should be saved. If none is given, the default is `animated`, such that the file has the name `animated.mp4`.|

When `FPS` is not `all` only every n<sup>th</sup> set of positions calculated in the simulation are displayed at a rate of `FPS` per second, where n is the nearest integer to the value `steps`/(`FPS`x`time`). If the combination of number of steps for the simulation, the frame rate for the animation and the runtime of the animation gives `steps`/(`FPS`x`time`) < 1, then n = 1, equivalent to `FPS: all`. The size of the body as displayed in the plot is currently given by the equation:

markersize = 5 log(\[M/M<sub>🜨</sub>\]<sup>1/5</sup>)
  
Which is appropriate for bodies with mass on the order of those found in the solar system (approx. 0.001 M<sub>🜨</sub> - 100,000 M<sub>🜨</sub>). A future implementation is planned to adjust this equation dynamically depending on the range of masses specified in the input file. To adjust it manually, go to the `calc_rad()` function of the `Body` class in `readinput.py`, broadly the prefactor in front of the log controls the absolute size of the markers while the order of the root controls the apparent difference in size between the smallest and largest objects.
