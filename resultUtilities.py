# -*- coding: utf-8 -*-
"""
Created on Mon Apr 1 15:42:47 2020

@author: Pontus Nordqvist
@email: p.nordq@gmail.com
"""
import calfem.vis_mpl as cfv
import tabulate as tbl
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np

class Report():
    """
    Class to present input and output in report form.
    """

    def __init__(self, input_data, output_data):
        """
        Constructor for the report. Initializes to an empty report.

        Parameters
        ----------
        TYPE(input_data): : plantmodel.InputData
            DESCRIPTION. An InputData object to load input data from.
        TYPE(output_data): : plantmodel.OutputData
            DESCRIPTION. An OutputData object to save output data to.

        Returns
        -------
        None.

        """
        self.input_data = input_data
        self.output_data = output_data
        self.report = ""

    def clear(self):
        """
        Method to clear the repport i.e set it to an empty string.

        Returns
        -------
        None.

        """
        self.report = ""

    def add_text(self, text=""):
        """
        Method to add text to existing repport.

        Parameters
        ----------
        TYPE(text): : str, optional
            DESCRIPTION. Text to add to the report. The default is "".

        Returns
        -------
        None.

        """
        self.report+=str(text)

    def __str__(self):
        """
        Returns a printable string object of the report. Uses a 'psql'
        np.tabulate format to do nice printing of certain data.

        Returns
        -------
        TYPE(self.report): : str
            DESCRIPTION. A report as an string.

        """
        self.clear()
        self.add_text()
        self.add_text("-------------- Model input --------------------------\n")
        self.add_text("t = " + str(self.input_data.t) + " m\n")
        self.add_text("E = " + str(self.input_data.E) + " Pa\n")
        self.add_text("v = " + str(self.input_data.v) + "\n")
        self.add_text("-------------- Results ------------------------------\n")
        self.add_text("Coordinates:\n")
        self.add_text(tbl.tabulate(self.output_data.coords,headers = ["x","y"],
                                   numalign="right", floatfmt=".3f",
                                   tablefmt="psql"))
        self.add_text("\n")
        self.add_text("Coordinate dofs:\n")
        self.add_text(tbl.tabulate(self.output_data.dofs.astype(int),
                                   headers = ["x","y"],numalign="right",
                                   floatfmt=".3f",tablefmt="psql"))
        self.add_text("\n")
        self.add_text("Topology:\n")
        self.add_text(tbl.tabulate(self.output_data.edof.astype(int),
                                   numalign="right",floatfmt=".3f",
                                   tablefmt="psql"))
        self.add_text("\n")
        self.add_text("Element coordinates x:\n")
        self.add_text(tbl.tabulate(self.output_data.ex,numalign="right",
                                   floatfmt=".3f",tablefmt="psql"))
        self.add_text("\n")
        self.add_text("Element coordinates y:\n")
        self.add_text(tbl.tabulate(self.output_data.ey,numalign="right",
                                   floatfmt=".3f",tablefmt="psql"))
        self.add_text("\n")
        self.add_text("Displacements (magnified by 1000):\n")
        self.add_text(tbl.tabulate(self.output_data.ed*1000,numalign="right",
                                   floatfmt=".3f", tablefmt="psql"))
        self.add_text("\n")
        self.add_text("Reactions:\n")
        self.add_text(tbl.tabulate(self.output_data.r,numalign="right",
                                   floatfmt=".3f",tablefmt="psql"))
        self.add_text("\n")
        self.add_text("Nodal displacements (magnified by 1000):\n")
        self.add_text(tbl.tabulate(self.output_data.a*1000,numalign="right",
                                   floatfmt=".3f",tablefmt="psql"))

        return self.report

class Visualization():
    """
    A class to handle the visualization of the input and output data.
    """
    def __init__(self, input_data, output_data):
        """
        Constructor for the visualization class. Loads default data from the
        parameters. Furthermore, it sets marker booleans for open windows to
        None type. Additional, it initializes a boolean as False that controll
        if the undisplaced mesh should be shown for the displacement figure.

        Parameters
        ----------
        TYPE(input_data): : plantmodel.InputData
            DESCRIPTION. An InputData object to load input data from.
        TYPE(output_data): : plantmodel.OutputData
            DESCRIPTION. An OutputData object to save output data to.

        Returns
        -------
        None.

        """
        self.input_data = input_data
        self.output_data = output_data

        # --- Variables referencing opean figures.
        self.geomFig = None
        self.meshFig = None
        self.elValueFig = None
        self.displacementFig = None
        #Boolean to controll if an undisplaced mesh should be shown.
        self.drawUndisplaced = False

    def showGeometry(self):
        """
        Method to show the geometry of the output data.

        Returns
        -------
        None.

        """
        geometry = self.output_data.geometry

        self.geomFig = cfv.figure(self.geomFig)
        cfv.clf()
        cfv.draw_geometry(geometry, title="Geometry (m)")
        self.geomFig = True

    def showMesh(self):
        """
        Method to show the mesh of the output data.

        Returns
        -------
        None.

        """
        coords = self.output_data.coords
        edof = self.output_data.edof
        dofs_per_node = self.output_data.dofsPerNode

        self.meshFig = cfv.figure(self.meshFig)
        cfv.clf()
        cfv.draw_mesh(coords, edof, dofs_per_node, el_type=2, filled=True,
                      title="Mesh (m)")
        self.meshFig = True

    def showElementValues(self):
        """
        Method to show the element effective stresses.

        Returns
        -------
        None.

        """
        eseff = self.output_data.eseff
        coords = self.output_data.coords
        edof = self.output_data.edof
        dofs_per_node = self.output_data.dofsPerNode
        el_type = self.output_data.elType

        self.elValueFig = cfv.figure(self.elValueFig)
        cfv.clf()
        cfv.draw_element_values(values=eseff, coords=coords, edof=edof,
                                dofs_per_node=dofs_per_node, el_type=el_type,
                                title="Element effective stresses (Pa)")
        colormap = cm.viridis
        normalize = mcolors.Normalize(vmin=np.min(eseff), vmax=np.max(eseff))
        s_map = cm.ScalarMappable(norm=normalize, cmap=colormap)
        self.elValueFig.colorbar(s_map)
        self.elValueFig = True

    def showDisplacement(self):
        """
        Method to show the displacements. Can also be triggered to show the
        undisplaced mesh in the same figure.

        Returns
        -------
        None.

        """
        a = self.output_data.a
        coords = self.output_data.coords
        edof = self.output_data.edof
        dofs_per_node = self.output_data.dofsPerNode
        el_type = self.output_data.elType

        self.displacementFig = cfv.figure(self.displacementFig)
        cfv.clf()
        cfv.draw_displacements(a=a, coords=coords, edof=edof,
                               dofs_per_node=dofs_per_node, el_type=el_type,
                               color=(30,144,255),
                               draw_undisplaced_mesh=self.drawUndisplaced,
                               magnfac=1e3,
                               title="Element displacements, magnified by " +
                                     "1000 (m)")
        self.displacementFig = True

    def closeAll(self):
        """
        Method to close all windows and default the trigger booleans.

        Returns
        -------
        None.

        """
        self.geomFig = None
        self.meshFig = None
        self.elValueFig = None
        self.nodeValueFig = None
        self.drawUndisplaced  = False
        cfv.closeAll()

    def wait(self):
        """
        Method to make sure that the windows gets updated. It will return when
        the windows closes.

        Returns
        -------
        None.

        """
        cfv.show_and_wait()
