# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 15:42:47 2020

@author: Pontus Nordqvist
@email: p.nordq@gmail.com
"""
import json
import calfem.geometry as cfg

class InputData():
    """
    Class to define input data for our model.
    """

    def __init__(self):
        """
        Cunstructor with initialize with default values.

        Returns
        -------
        None.

        """
        self.version = 1

        #--Geometry dimension, se report for graphic representation.
        self.h = 0.1
        self.w = 0.3
        self.a = 0.05
        self.b = 0.025

        self.el_size_factor = 0.5 #Gives the area of the elements.

        #--Default forces and material properties.
        self.E = 2.08e10
        self.v = 0.2
        self.q = 100e3      #If positive, it is dragging the object out.

        self.t = 0.15       #Thickness

        #--Booleans to control parameter study.
        self.paramb = False
        self.paramq = False

        self.bstart = self.b
        self.bend = 0.0001
        self.qstart = self.q
        self.qend = -1.0*self.q

        self.paramFileName = "paramStudy"
        self.paramSteps = 10

        self.el_type = 2 #Element typ, 2: triangles, 3: quads.


    def geometry(self):
        """
        Method which defines a geometry to be used by the GMSH mesh generator.

        Returns
        -------
        TYPE(g): : calfem.geometry.Geometry
            DESCRIPTION. The created geometry for GMSH.

        """

        g = cfg.Geometry()

        h = self.h
        w = self.w
        a = self.a
        b = self.b

        #Define the boundarys node points.
        g.point([0,0])
        g.point([(w-a)/2,0])
        g.point([(w-a)/2,b])
        g.point([(w+a)/2,b])
        g.point([(w+a)/2,0])
        g.point([w,0])
        g.point([w,h])
        g.point([(w+a)/2,h])
        g.point([(w+a)/2,h-b])
        g.point([(w-a)/2,h-b])
        g.point([(w-a)/2,h])
        g.point([0,h])

        #Makes the borders
        for i in range(11):
            if i==5:
                g.spline([i,i+1],marker=6) #Most right border where q is.
            else:
                g.spline([i,i+1])

        g.spline([0,11], marker=12) #Moste left border where wall is.

        g.surface([0,1,2,3,4,5,6,7,8,9,10,11])

        return g

    def save(self, filename):
        """
        Method to save the indata to a JSON file.

        Parameters
        ----------
        TYPE(filename) : str
            DESCRIPTION. The name of the file where you save the input data.

        Returns
        -------
        None.

        """
        #Dict to put the data to ease the conversion to JSON format.
        input_data = {}
        input_data["version"] = self.version
        input_data["h"] = self.h
        input_data["a"] = self.a
        input_data["b"] = self.b
        input_data["w"] = self.w
        input_data["el_size_factor"] = self.el_size_factor
        input_data["t"] = self.t
        input_data["E"] = self.E
        input_data["v"] = self.v
        input_data["q"] = self.q
        input_data["bend"] = self.bend
        input_data["qend"] = self.qend
        input_data["paramSteps"] = self.paramSteps
        input_data["el_type"] = self.el_type

        with open(filename, "w") as ofile:
            json.dump(input_data, ofile, sort_keys = True, indent = 4)

    def load(self, filename):
        """
        Method to load indata from a JSON file.

        Parameters
        ----------
        TYPE(filename): : str
            DESCRIPTION. The name of the JSON file you want to load the input
            data from.

        Returns
        -------
        None.

        """
        with open(filename, "r") as ifile:
            input_data = json.load(ifile)

        self.version = input_data["version"]
        self.h = input_data["h"]
        self.a = input_data["a"]
        self.b = input_data["b"]
        self.w = input_data["w"]
        self.el_size_factor = input_data["el_size_factor"]
        self.t = input_data["t"]
        self.E = input_data["E"]
        self.v = input_data["v"]
        self.q = input_data["q"]
        self.bend = input_data["bend"]
        self.qend = input_data["qend"]
        self.paramSteps = input_data["paramSteps"]
        self.el_type = input_data["el_type"]

class OutputData():
    """
    Class to store results from calculation.
    """

    def __init__(self):
        """
        Constructor for the output data. Initiates all to None type.

        Returns
        -------
        None.

        """
        self.a = None
        self.r = None
        self.ed = None
        self.qs = None
        self.qt = None
        self.ex = None
        self.ey = None
        self.coords = None
        self.edof = None
        self.geometry = None
        self.dofsPerNode = None
        self.elType = None
        self.eseff = None
        self.maxEssef = None
        self.eseffnod = None
        self.dofs = None
        self.topo = None
        self.mises = None
        self.stress1 = None
        self.stress2 = None
