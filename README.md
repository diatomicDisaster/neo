# **NEO V0.1**

NEO (**NE**wtonian **O**rbits) is a simulation of Newtonian gravity performed "on-the-fly" using the fourth-order Runge-Kutta time integration method. The bodies are defined systematically in an '.inp' input file using a range of dynamic parameters, an example is [given below](#example-input).


The parameters for the simulation are similarly defined in the input file:

```SIMULATION
dt: 0.5 day
duration: 0.5 year
END
```

## Getting Started
### Installing

1. Go to https://github.com/diatomicDisaster/Planets, click the green button on the right hand side "Clone or Download".
2. To download the files directly, click "Download ZIP", or to install using git:

```
git clone https://github.com/diatomicDisaster/Planets.git
```

3. The following Python libararies are required: `numpy`, `matplotlib` and `argparse`, and [can be installed using your chosen package manager](https://packaging.python.org/tutorials/installing-packages/).

### Example Input

The input is provided to the program via a plain text ".inp" file. In the file the bodies to be simulated can be specified using a range of parameters. An example is given below

```BODY 
name: Earth
mass: 1 mE
position: 1 0
velocity: 0 2*pi/365
polar
relative: Sun
colour: #0099ff
END
```

