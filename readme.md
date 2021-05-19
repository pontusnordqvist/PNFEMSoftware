
# Welcome to PNFEMSoftware's documentation!
# =========================================
Pontus Nordqvist Finite Element Method Software (PNFEMSoftware) is a Software
to make you simulate plane stress in 2D for a wall bar. Additionally, can it
also be used to produce animations which can be viewed in Paraview.

Look how easy it is to use:
.. code-block::
    >>python main.py

and the graphical user interface will guide you through.

## Features
## --------

- Calculate displacements and stresses for a wall bar.
- Change the dimension, applied force and material parameters.
- Save or load data in json format.
- Save to .mat format to compare result in MATLAB.
- Export to .vtk files to make animations in Paraview.
- Perform parameter studies.

## Requirements
## ------------
- Python 3.7
- calfem-python 3.5.3
- tabulate 0.8.9
- gmsh 4.8.4

## Installation
## ------------

Install PNFEMSoftware by running
.. code-block::
    >>pip install -r requirements.txt
