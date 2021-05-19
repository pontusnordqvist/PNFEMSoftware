# -*- coding: utf-8 -*-
"""
Created on Sat May  2 13:57:35 2020

@author: Pontus Nordqvist
@email: p.nordq@gmail.com
"""

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QFont, QIcon

from dataTypes import InputData, OutputData
from solvers import Solver
from resultUtilities import Report, Visualization

import numpy as np

class MainWindow(QMainWindow):
    """
    MainWindow-class to hande GUI. It inherits from the QMainWindow class.
    """

    def __init__(self, app):
        """
        Constructor for the MainWindow GUI class. It initializes to deafualt
        values. Additional, it fixes the window to 1000x500. It also load from
        the 'mainwindow.ui' file.
        Returns
        -------
        None.

        """
        super(QMainWindow, self).__init__()

        self.app = app

        self.ui = loadUi('mainwindow.ui', self) #Loads the GUI files

        self.ui.setFixedSize(1000, 500)

        #--Connection of GUI elements to internal methods.
        self.ui.actionNew.triggered.connect(self.onActionNew)
        self.ui.actionOpen.triggered.connect(self.onActionOpen)
        self.ui.actionSave.triggered.connect(self.onActionSave)
        self.ui.actionSave_as.triggered.connect(self.onActionSaveAs)
        self.ui.actionExit.triggered.connect(self.onActionExit)
        self.ui.actionExecute.triggered.connect(self.onActionExecute)
        self.ui.showGeometryButton.clicked.connect(self.onShowGeometry)
        self.ui.showMeshButton.clicked.connect(self.onShowMesh)
        self.ui.showDisplacementsButton.clicked.connect(self.onShowDisplacement)
        self.ui.showElementValuesButton.clicked.connect(self.onShowElementValues)

        self.ui.maxElSizeSlide.valueChanged.connect(self.onShowElsize)

        self.ui.paramstudyButton.clicked.connect(self.onExecuteParamStudy)
        self.ui.executePushButton.clicked.connect(self.onActionExecute)
        self.ui.undisplacedBox.stateChanged.connect(self.onShowUndisplacedMesh)

        #Sets set shortcuts commandos
        self.ui.actionExecute.setShortcut("Ctrl+R")
        self.ui.actionExit.setShortcut("Alt+F4")
        self.ui.actionOpen.setShortcut("Ctrl+O")
        self.ui.actionSave.setShortcut("Ctrl+S")
        self.ui.actionSave_as.setShortcut("Ctrl+Shift+S")
        self.ui.actionNew.setShortcut("Ctrl+N")

        #Sets icons for shortcuts commandos
        self.ui.actionExecute.setIcon(QIcon("Icons/icons8-execute.png"))
        self.ui.actionExit.setIcon(QIcon("Icons/icons8-exit.png"))
        self.ui.actionOpen.setIcon(QIcon("Icons/icons8-open.png"))
        self.ui.actionSave.setIcon(QIcon("Icons/icons8-save.png"))
        self.ui.actionSave_as.setIcon(QIcon("Icons/icons8-save-as.png"))
        self.ui.actionNew.setIcon(QIcon("Icons/icons8-new-document.png"))

        self.ui.triButton.clicked.connect(self.onEltype2)
        self.ui.triButton.setChecked(True) #Sets triangles as default in GUI.
        self.ui.quadButton.clicked.connect(self.onEltype3)

        self.ui.bendButton.setChecked(True) #Set parameterstudy of b as default.

        #Sets font and size in the repport window.
        self.ui.reportEdit.setFont(QFont('Courier New',10))

        #--Sets the following windows to be read only.
        self.ui.reportEdit.setReadOnly(True)
        self.ui.maxElSizeEdit.setReadOnly(True)

        #--Shows the GUI
        self.ui.show()
        self.ui.raise_()

        #--Initialize the defult values for the plantmodel.
        self.initModel()
        self.updateControls()


    def onActionExecute(self):
        """
        Method to start an execution thread to call an solver on the input.

        Returns
        -------
        None.

        """
        self.updateModel() #Updates the model with new input.

        #Makes sure no fatal errors occurs in the input before execution.
        if not True in self.fatalErrors.values():

            self.ui.setEnabled(False) #Disables GUI during execution.

            self.solver = Solver(self.InputData, self.OutputData)

            #Moves over computation to a thread so the GUI won't freeze.
            self.solverThread = SolverThread(self.solver)
            self.solverThread.finished.connect(self.onSolverFinished)
            self.solverThread.start()



    def onSolverFinished(self):
        """
        Method to start when an execution thread has enden. Also print the
        report.

        Returns
        -------
        None.

        """
        #Boolean to make plot buttons diasbled before execution.
        self.calcDone = True
        self.updateButtons()
        self.Visual = Visualization(self.InputData, self.OutputData)
        self.ui.setEnabled(True) #Makes GUI interactible.

        # --- Generate the end repport.
        self.ui.reportEdit.clear() #Cleares previous text.
        self.report = Report(self.InputData, self.OutputData)
        np.set_printoptions(formatter={'float': '{: 0.3f}'.format})
        self.ui.reportEdit.setPlainText(str(self.report))

    def initModel(self):
        """
        Method to initiate the model with default parameters given from the
        plantmodel class. It also defaults visualisation, filename, buttons,
        solver and booleans for the calculation done and fatal error found.

        Returns
        -------
        None.

        """
        self.InputData = InputData()
        self.OutputData = OutputData()
        self.Visual = Visualization(self.InputData, self.OutputData)
        self.filename=""
        self.calcDone = False
        #Dict to detect fatal error for the differen key cases.
        self.fatalErrors = {
            'calc_inputs': False,
            'bend_input': False,
            'text_input': False
            }
        self.updateButtons()
        self.solver = Solver(self.InputData,self.OutputData)
        self.Visual.drawUndisplaced = False #Default to not show the org mesh.
        self.ui.undisplacedBox.setChecked(False) #Sets default to not checked.
        self.ui.undisplacedBox.setEnabled(False)

    def updateControls(self):
        """
        Method to update the GUI with the values from the plantmodel class.

        Returns
        -------
        None.

        """
        self.ui.wEdit.setText(str(self.InputData.w))
        self.ui.hEdit.setText(str(self.InputData.h))
        self.ui.aEdit.setText(str(self.InputData.a))
        self.ui.bEdit.setText(str(self.InputData.b))
        self.ui.tEdit.setText(str(self.InputData.t))
        self.ui.eEdit.setText(str(self.InputData.E))
        self.ui.vEdit.setText(str(self.InputData.v))
        self.ui.qEdit.setText(str(self.InputData.q))
        self.ui.maxElSizeEdit.setText(str(self.InputData.el_size_factor))
        self.ui.maxElSizeSlide.setValue((self.InputData.el_size_factor-0.99)/
                                        (-9.8e-3))
        self.ui.bendEdit.setText(str(self.InputData.bend))
        self.ui.qendEdit.setText(str(self.InputData.qend))
        self.ui.paramstudyBox.setValue(self.InputData.paramSteps)

    def updateModel(self):
        """
        Method to update the model given and input in the GUI. If an invalid
        input is given, an critical messagebox stating the error is triggered.

        Returns
        -------
        None.

        """
        try:
            self.InputData.w = float(self.ui.wEdit.text())
            self.InputData.h = float(self.ui.hEdit.text())
            self.InputData.a = float(self.ui.aEdit.text())
            self.InputData.b = float(self.ui.bEdit.text())
            self.InputData.t = float(self.ui.tEdit.text())
            self.InputData.E = float(self.ui.eEdit.text())
            self.InputData.v = float(self.ui.vEdit.text())
            self.InputData.q = float(self.ui.qEdit.text())
            self.InputData.el_size = float(self.ui.maxElSizeEdit.text())
            self.InputData.bend = float(self.ui.bendEdit.text())
            self.InputData.qend = float(self.ui.qendEdit.text())
            self.InputData.paramSteps = float(self.ui.paramstudyBox.text())
            self.fatalErrors['text_input'] = False #Won't flip if above fails.

        except ValueError as err: #Catches errors
            #Catches if the input is a string/char. Note: is a fatal error
            if 'could not convert string to float' in str(err):
                message = "The program can only handle numbers as input!"
                QMessageBox.critical(self, "Invalid input", message)
                del message
                self.fatalErrors['text_input'] = True

        self.__checkValidInput()


    def __checkValidInput(self):
        """
        Helpmethod to see if an input is valid. It checks if the given lengths
        are negative or zero. Also, it checks if the Poisson's ratio is in the
        valid intervall -1<v<0.5 and if b or bend >= h/2.

        Returns
        -------
        None.

        """
        #Dict with all input lengths, to ease iteration through them below.
        lengthDict = {
            'w': self.InputData.w,
            'h': self.InputData.h,
            'a': self.InputData.a,
            'b': self.InputData.b,
            't': self.InputData.t,
            'b, end': self.InputData.bend
            }
        bend_passed = True #Boolean to see if new inputs of bend is valid.
        lengths_passed = True

        #Iterates through the lengths to detec errors.
        for k,v in lengthDict.items():
            #Checks if lengths are negative.
            if lengthDict[k] < 0:
                message = (f"{k} is {v} m, which is negative and not possible"
                          " for a length!")
                QMessageBox.critical(self, "Invalid input", message)
                del message
                self.fatalErrors['calc_inputs'] = True
                lengths_passed = False

                #Special case for b, end to reset boolean.
                if k == 'b, end':
                    self.fatalErrors['bend_input'] = True
                    bend_passed = False

            #Checks if lengths are zeros.
            if lengthDict[k] == 0:
                message = f"{k} is {v} m, which is not a possible dimension!"
                QMessageBox.critical(self, "Invalid input", message)
                del message
                self.fatalErrors['calc_inputs'] = True
                lengths_passed = False

                #Special case for b, end to reset boolean.
                if k == 'b, end':
                    self.fatalErrors['bend_input'] = True
                    bend_passed = False

        #Checks valid range of v.
        if self.InputData.v < -1 or self.InputData.v > 0.5:
            message = ("The program works with isotropic, linearly elastic "
                      "materials , so  v is in the range of -1  to 0.5, you "
                      f"inputed v = {self.InputData.v }!")
            QMessageBox.critical(self, "Invalid input", message)
            del message
            self.fatalErrors['calc_inputs'] = True
            lengths_passed = False

        #Checks if b is greater than h.
        if self.InputData.b >= self.InputData.h/2:
            message = (f"The inputed b is  {self.InputData.b} m, which is "
                      "greater or eqaul to half the height h that is"
                      f"{self.InputData.h/2} m, this is an invalid geometry!" )
            QMessageBox.critical(self, "Invalid input", message)
            del message
            self.fatalErrors['calc_inputs'] = True
            lengths_passed = False

        #Checks if bend is greater than h.
        if self.InputData.bend >= self.InputData.h/2:
            message = (f"The inputed b, end is {self.InputData.bend} m, which"
                      f"is greater or eqaul to half the height h that is "
                      f"{self.InputData.h/2} m, this is an invalid geometry "
                      "for the model!")
            QMessageBox.critical(self, "Invalid input", message)
            del message
            self.fatalErrors['bend_input'] = True
            bend_passed = False

        if bend_passed:
            self.fatalErrors['bend_input'] = False

        if lengths_passed:
            self.fatalErrors['calc_inputs'] = False


    def onShowElsize(self):
        """
        Method to get the given value from the element size slider to the
        inputdata. Also, it updates the box showing the given value.

        Returns
        -------
        None.

        """
        #Empirically obtained conversion of slide input to CALFEM maxElSize.
        self.InputData.el_size_factor = round((-9.8e-3) *
                                        (self.maxElSizeSlide.value()) + 0.99, 4)
        self.ui.maxElSizeEdit.setText(str(self.InputData.el_size_factor))

    def onActionOpen(self):
        """
        Method to opean an input JSON file.

        Returns
        -------
        None.

        """
        self.filename, _ = QFileDialog.getOpenFileName(self.ui, "Open model",
                                        "", "Model files (*.json *.jpg *.bmp)")

        #Catches if no filname has been given.
        if self.filename !="":
            self.Visual.closeAll() #Closses all windows.
            self.InputData.load(self.filename)
            self.updateControls()
            self.calcDone = False
            self.updateButtons()
            self.ui.reportEdit.clear() #Cleares repport on new model.
            message = ("The model was succesfully succesfully loaded from the"
            f" file {self.filename}!")
            QMessageBox.information(self,'Message', message)
            del message

    def onActionSave(self):
        """
        Method to save the modell. Before it saves the model, it updates it with
        the given inpute i.e no prior execution is needed. It also checks for
        if there are any fatal errors and does not save if that is the case.
        It uses popups to communicate with the user.

        Returns
        -------
        None.

        """
        self.updateModel()
        #Outer shell to protect from fatal erros.
        if not True in self.fatalErrors.values():
            if self.filename == "":
                self.filename, _  = QFileDialog.getSaveFileName(self.ui,
                "Save model", "", "Model files (*.json)")

            #Catches if no filname has been given.
            if self.filename !="":
                self.updateModel()
                self.InputData.save(self.filename)
                message = f"The model was  saved in the file {self.filename}!"
                QMessageBox.information(self,'Message', message)
                del message
        else:
            message = ("You still have an invalid input, and therefore can't "
                      f"save! \n")
            QMessageBox.critical(self, "Invalid input", message)
            del message

    def onActionSaveAs(self):
        """
        Method to save the model as an new file. Before it saves the model,
        it updates it with the given input i.e no prior execution is needed.
        It also checks for if there are any fatal errors and does not save if
        that is the case. It uses popups to communicate with the user.

        Returns
        -------
        None.

        """
        self.updateModel()

        #Outer shell to protect from fatal erros.
        if not True in self.fatalErrors.values():
            newFilename, _  = QFileDialog.getSaveFileName(self.ui,
                "Save model", "", "Model files (*.json)")

            #Catches if no filname has been given.
            if newFilename !="":
                self.filename = newFilename
                self.updateModel()
                self.InputData.save(self.filename)

                message = f"The model was saved in the file {self.filename}!"
                QMessageBox.information(self,"Message", message)
                del message
        else:
            message = (f"You still have an invalid input, and therefore can't"
                      " save! \n")
            QMessageBox.critical(self, "Invalid input", message)
            del message

    def onActionNew(self):
        """
        Method to initiate a new model. The new model will have the default
        values.

        Returns
        -------
        None.

        """
        self.Visual.closeAll()
        self.initModel() #Load defaults.
        self.updateControls()
        self.ui.reportEdit.clear() #Cleares repport on new model.

    def onActionExit(self):
        """
        Method that is triggered when the user clicks on the exit button in the
        program (not the x in the window). Also, it closes all figure windows.
        Note: It might not terminate the kernel.

        Returns
        -------
        None.

        """
        self.Visual.closeAll()
        self.close()

    def updateButtons(self):
        """
        Method to update the button and the ticbox to be visable after an
        calulation is done.

        Returns
        -------
        None.

        """
        self.ui.showGeometryButton.setEnabled(self.calcDone)
        self.ui.showMeshButton.setEnabled(self.calcDone)
        self.ui.showDisplacementsButton.setEnabled(self.calcDone)
        self.ui.showElementValuesButton.setEnabled(self.calcDone)
        self.ui.undisplacedBox.setEnabled(True)

    def onShowGeometry(self):
        """
        Method that shows the geometry in the plantmodel class. It is triggered
        when the geomtery button in the GUI is pressed.

        Returns
        -------
        None.

        """
        self.Visual.showGeometry()
        self.Visual.wait() #Enables no further windows being triggered.

    def onShowMesh(self):
        """
        Method that shows the mesh in the plantmodel class. It is triggered
        when the mesh button in the GUI is pressed.

        Returns
        -------
        None.

        """
        self.Visual.showMesh()
        self.Visual.wait() #Enables no further windows being triggered.

    def onShowDisplacement(self):
        """
        Method that shows the calculated displacment in the plantmodel class.
        It is triggered when the displacement button in the GUI is pressed.

        Returns
        -------
        None.

        """
        self.Visual.showDisplacement()
        self.Visual.wait() #Enables no further windows being triggered.

    def onShowElementValues(self):
        """
        Method that shows the calculated effective stress for the elements
        in the plantmodel class. It is triggered when the displacement button
        in the GUI is pressed.

        Returns
        -------
        None.

        """
        self.Visual.showElementValues()
        self.Visual.wait() #Enables no further windows being triggered.


    def onShowUndisplacedMesh(self):
        """
        Method to show/unshow the undisplaced mesh in the displacement figure.

        Returns
        -------
        None.

        """
        self.Visual.drawUndisplaced = not self.Visual.drawUndisplaced
        self.Visual.wait() #Enables no further windows being triggered.

    def onExecuteParamStudy(self):
        """
        Method to that runs a paramter study using a solver thread. The input
        is taken from the GUI. Further, it also handles some invalid inputs.

        Returns
        -------
        None.

        """
        #--Booleans on what parameter study to preform.
        self.InputData.paramb = self.ui.bendButton.isChecked()
        self.InputData.paramq = self.ui.qendButton.isChecked()

        qend_typerror = False #Boolean to check if a qend typerror has occured.

        try:
            if self.InputData.paramb:
                self.InputData.bstart = float(self.ui.bEdit.text())
                self.InputData.bend = float(self.ui.bendEdit.text())
                self.__checkValidInput()
                filename = "paramStudy_01"
            elif self.InputData.paramq:
                self.InputData.qstart = float(self.ui.qEdit.text())
                self.InputData.qend = float(self.ui.qendEdit.text())
                filename = "paramStudy_02"

        #Catches invalid inputs.
        except ValueError as err:
             #Catches if input is string.
            if 'could not convert string to float' in str(err):
                message = "The program can only handle numbers as input!"
                QMessageBox.critical(self, "Invalid input", message)
                del message
                self.fatalErrors['bend_input'] = True
                qend_typerror = True                  #A qend typerror is found!

        #Flip backs the q_end typerror if it's corrected.
        if self.InputData.paramq and not qend_typerror:
            self.fatalErrors['bend_input'] = False
            qend_typerror = False

        #Outer shell to stop execution if there is an fatal error.
        if not self.fatalErrors['bend_input']:

            self.InputData.paramFilename = "paramStudy"
            self.InputData.paramSteps = int(self.ui.paramstudyBox.value())

            self.solverThread = SolverThread(self.solver, paramStudy = True)
            self.solverThread.finished.connect(self.onSolverFinished)
            self.solverThread.run()

            message = ("The paramater study was succesfull!\n It is saved in"
                      f"the .vtk which starts with {filename} !")
            QMessageBox.information(self,'Message', message)
            del message

    def onEltype2(self):
        """
        Method to change the element type to 2 (triangles). It is triggered
        by the corresponding radio button.

        Returns
        -------
        None.

        """
        self.InputData.el_type = 2

    def onEltype3(self):
        """
        Method to change the element type to 3 (quads). It is triggered
        by the corresponding radio button.

        Returns
        -------
        None.

        """
        self.InputData.el_type = 3

class SolverThread(QThread):
    """
    Class to handle execution threads i.e solverthreads.
    """

    def __init__(self, solver, paramStudy=False):
        """
        Constructor for the solver thread.

        Parameters
        ----------
        TYPE(solver): : plantmodel.Solver
            DESCRIPTION. An plantmodel solver object.
        TYPE(paramStudy): : bool, optional
            DESCRIPTION. Boolean to indicate if a parameter study should be
            performed. The default is False.

        Returns
        -------
        None.

        """
        QThread.__init__(self)
        self.solver = solver
        self.paramStudy = paramStudy

    def __del__(self):
        """
        Method to delete the thread.

        Returns
        -------
        None.

        """
        self.wait()

    def run(self):
        """
        Method to start the thread. The thread does an solver.execute()
        and a solver.executeParamStudy() if told to in the constructor.

        Returns
        -------
        None.

        """
        self.solver.execute()
        if self.paramStudy:
            self.solver.executeParamStudy()
