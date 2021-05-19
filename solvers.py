# -*- coding: utf-8 -*-
"""
Created on Mon Apr 1 15:42:47 2020

@author: Pontus Nordqvist
@email: p.nordq@gmail.com
"""
import numpy as np
import calfem.core as cfc
import calfem.mesh as cfm
import calfem.utils as cfu
import pyvtk as vtk
import math
import scipy.io as scio

class Solver():
    """
    Class to handle solution to our computational model.
    """

    def __init__(self, input_data, output_data, mat_save=False):
        """
        Constructor for the solver. Loads data from a InputData object and
        assign it to a OutputData object.

        Parameters
        ----------
        TYPE(input_data) : plantmodel.InputData
            DESCRIPTION. An InputData object to load input data from.
        TYPE(output_data) : plantmodel.OutputData
            DESCRIPTION. An OutputData object to save output data to.
        TYPE(mat_save) : bool
            DESCRIPTION. Boolean to controll if the solvers save result to
                         MALTAB data. Default to False (No saving).
        Returns
        -------
        None.

        """
        self.input_data = input_data
        self.output_data = output_data
        self.ex = None
        self.ey = None
        self.mat_save = mat_save

    def execute(self):
        """
        Method to execute the calculations. The performed calulations are:
        node displacement obtaining, node/element stress and strain obtaining,
        von Misses stress and principal stresses. Also saves the geometry and
        some calculated values to MATLAB files for comparison.

        Returns
        -------
        None.

        """
        E = self.input_data.E
        v = self.input_data.v
        ep = [1, self.input_data.t]
        q = self.input_data.q
        el_size_factor = self.input_data.el_size_factor

        #Construct the geometry
        geometry = self.input_data.geometry()

        el_type = self.input_data.el_type
        #Defrees of freedom for node, b.c this is plane strees => 2.
        dofs_per_node = 2

        #--Makes the mesh using a GMSH mesh generator.
        mesh = cfm.GmshMeshGenerator(geometry)
        mesh.el_size_factor = el_size_factor
        mesh.el_type = el_type
        mesh.dofs_per_node = dofs_per_node
        mesh.return_boundary_elements = True

        coords, edof, dofs, bdofs, elementmarkers, boundaryElements = mesh.create()

        #Initialization and prelocation for variabls to perform the calculations
        D = cfc.hooke(1,E,v)

        ndof = np.size(dofs)
        K = np.zeros((ndof,ndof)) # Stiffness matrix
        f = np.zeros((ndof,1))      #Force matrix
        cfu.applyforcetotal(bdofs,f,6,value=q,dimension=1) #Apply q force

        bc = np.array([],int)
        bcVal = np.array([],float)
        bc, bcVal = cfu.applybc(bdofs,bc,bcVal,12,value=0.0,dimension=0)

        # x coordinates and y coordinates for elements
        ex, ey = cfc.coordxtr(edof, coords, dofs)

        #--Loop to create the stiffness matrix
        for elx, ely, eltopo in zip(ex, ey, edof):
            if el_type == 2:                     #Case if elements are triangles
                Ke = cfc.plante(elx, ely, ep, D)
            elif el_type == 3:                   #Case if elements are quads
                Ke = cfc.planqe(elx, ely, ep, D)

            # Assemble element stiffness matrices to global stiffness matrix
            cfc.assem(eltopo, K, Ke)

        #-Solves the equation system.
        a, r = cfc.solveq(K,f, bc, bcVal) #a displacements, #r reactions forces

        ed = cfc.extractEldisp(edof, a) #element displacements

        #--Computes stresses and strains.
        if el_type == 2: #Traingle elements
            es, et = cfc.plants(ex, ey, ep, D, ed) #Stress and strains

        elif el_type == 3: #Quds elements
            es = np.zeros((edof.shape[0],3))

            for i in range(edof.shape[0]):
                es[i,:], et = cfc.planqs(ex[i,:], ey[i,:], ep, D, ed[i,:])

        mises = []      #List of von Misses stress
        stress1 = []    #List for pricipal stress 1
        stress2 = []    #List for pricipal stress 2

        #--Loop to make the vonMisses and principal stresses.
        for i in range(edof.shape[0]):

            mises.append(np.sqrt(math.pow(es[i,0],2) - es[i,0]*es[i,1] +
                        math.pow(es[i,1],2) + 3*es[i,2]))

            theta = np.arctan2(2*es[i,2], es[i,0]-es[i,1])*0.5

            sigma1 = 0.5 * (es[i,0] + es[i,1]) + np.sqrt(np.power(0.5 *
                    (es[i,0] - es[i,1]), 2) + np.power(es[i,2], 2))
            sigma2 = 0.5 * (es[i,0] + es[i,1]) + np.sqrt(np.power( 0.5 *
                    (es[i,0] - es[i,1]), 2) + np.power(es[i,2], 2))

            s1v = [sigma1*np.cos(theta), sigma1*np.sin(theta), 0.0]
            s2v = [sigma2*np.cos(theta+0.5*np.pi),
                   sigma2*np.sin(theta+0.5*np.pi), 0.0]

            stress1.append(s1v)
            stress2.append(s2v)

        #List for displacments to be used in Paraview.
        displ = [[np.asscalar(a[i]), np.asscalar(a[i+1]),0.0] for i in range(0,
                len(a),2)]

        eseff = cfc.effmises(es,1) #Makes vonMisses stress using CALFEM.

        eseffnod = cfc.stress2nodal(eseff, edof) #Extracts nodal stresses.

        #--Save variables to MATLAB files.
        if self.mat_save:
            scio.savemat('MATLABSaves/geometry.mat', dict(geometry=geometry))
            scio.savemat('MATLABSaves/coords.mat', dict(coords=coords))
            scio.savemat('MATLABSaves/dofs.mat', dict(dofs=dofs))
            scio.savemat('MATLABSaves/edof.mat', dict(edof=edof))
            scio.savemat('MATLABSaves/bc.mat', dict(bc=bc))
            scio.savemat('MATLABSaves/a_python.mat', dict(a_python=a))
            scio.savemat('MATLABSaves/r_python.mat', dict(r_python=r))
            scio.savemat('MATLABSaves/ed_python.mat', dict(ed_python=ed))
            scio.savemat('MATLABSaves/es_python.mat', dict(es_python=es))


        #--Transfer model variables to local variables
        self.output_data.a = a
        self.output_data.r = r
        self.output_data.ed = ed
        self.output_data.es = es
        self.output_data.et = et
        self.output_data.ex = ex
        self.output_data.ey = ey
        self.output_data.coords = coords
        self.output_data.edof = edof
        self.output_data.dofs = dofs
        self.output_data.geometry = geometry
        self.output_data.dofsPerNode = dofs_per_node
        self.output_data.elType = el_type
        self.output_data.eseff = eseff
        self.output_data.maxEssef = np.amax(eseff)
        self.output_data.eseffnod = eseffnod
        self.output_data.topo = mesh.topo
        self.output_data.mises = mises
        self.output_data.stress1 = stress1
        self.output_data.stress2 = stress2
        self.output_data.displ = displ

    def executeParamStudy(self):
        """
        Method to perform a parameter study.

        Returns
        -------
        None.

        """
        old_b = self.input_data.b
        old_q = self.input_data.q

        #Trigger if the user want a parameter study on b.
        if self.input_data.paramb:
            # --- Makes a range of b to do calulations on.
            bRange = np.linspace(self.input_data.bstart, self.input_data.bend,
                                 self.input_data.paramSteps)

            # --- Starts the parameter study of b.
            #counter to make resonable file names.
            for counter, b in enumerate(bRange):
                self.input_data.b = b
                self.execute()

                # --- Exports to vtk-file
                #Special case if <10 or have 0 infront.
                if counter < 9:
                    self.exportVtk(f"vtks/bParam/paramStudy_01_0{counter+1}.vtk")
                else:
                    self.exportVtk(f"vtks/bParam/paramStudy_01_{counter+1}.vtk")

        #Trigger if the user want a parameter study on b.
        elif self.input_data.paramq:
            # --- Makes a range of q to do calulations on.
            qRange = np.linspace(self.input_data.qstart, self.input_data.qend,
                                 self.input_data.paramSteps)

            # --- Starts the parameter study of q.
            for counter,q in enumerate(qRange):

                self.input_data.q = q
                self.execute()

                # --- Exports to vtk-file
                #Special case if <10 or have 0 infront.
                if counter < 9:
                    self.exportVtk(f"vtks/qParam/paramStudy_02_0{counter+1}.vtk")
                else:
                    self.exportVtk(f"vtks/qParam/paramStudy_02_{counter+1}.vtk")

        # --- Restores parameters to pre parameter study.
        self.input_data.b = old_b
        self.input_data.q = old_q

    def exportVtk(self, filename):
        """
        Method to export the parameter study to a .vtk file.

        Parameters
        ----------
        TYPE(filename): : str
            DESCRIPTION. Name of the .vtk file to export.

        Returns
        -------
        None.

        """
        #Convert displacement to vtk point data.
        point_data = vtk.PointData(vtk.Vectors(self.output_data.displ,
                                               name="displacements"))

        # --- Makes points, polygons, celldata and structure for the .vtk format
        points = self.output_data.coords.tolist()
        polygons = (self.output_data.topo-1).tolist()
        cellData = vtk.CellData(vtk.Scalars(self.output_data.mises,
                                            name="mises"),
                                vtk.Vectors(self.output_data.stress1,
                                            "principal stress 1"),
                                vtk.Vectors(self.output_data.stress2,
                                            "principal stress 2"))
        structure = vtk.PolyData(points = points, polygons = polygons)

        #Makes the above for a .vtk data.
        vtkData = vtk.VtkData(structure, cellData, point_data)

        vtkData.tofile(filename, "ascii")#Saves the file using vtkDatas function
