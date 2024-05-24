# TRA370 scripts 

This repo contains the scripts used for our project

## Dependencies
Install the cf library at [crazyflie-lib-python](https://github.com/TRA370-Improve-TinyMPC/crazyflie-lib-python) in the github docs folder.

## Usage
### Clone
```bat
git clone https://github.com/TRA370-Improve-TinyMPC/scripts
```
### Requirements
```bat
pip install -r requirements.txt
```

### Polynomials
In `trajectories`there exist files that have the x,y,z,yaw coordinates for the trajectory.
To generate a polynomials from a coordinates file
```bat
  python3 polynomial/generatePolynomials.py [input_coordinates.py] [total_duration] [number_of_polynomials] [output_polynomials.csv]
```

### Execute trajectory
```bat
  python3 commander/autonomous_sequence.py [polynomials.csv]
```
Logs will be created at the end of the trajectory

### Plot logs
This does not have command line arguments, at the moment everything was hardcoded
```bat
  python3 plots/plots.py
```
Will generate plots for total trajectory, xy trajectory and motor thrusts along with reference comparing pid and tinympc

## License

The code is licensed under AGPL-3.0
