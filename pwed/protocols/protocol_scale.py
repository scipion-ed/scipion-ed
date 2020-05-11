# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (delarosatrevin@scilifelab.se) [1]
# *              V. E.G. Bengtsson (viktor.bengtsson@mmk.su.se) [2]
# *
# * [1] SciLifeLab, Stockholm University
# * [2] Department of Materials and Environmental Chemistry, Stockholm University
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import os
import re
import pathlib
from glob import glob

import pyworkflow as pw
import pyworkflow.protocol as pwprot

from pwed.objects import ExportFile, SetOfExportFiles
from .protocol_base import EdBaseProtocol


class ProtScale(EdBaseProtocol):
    _label = 'scale'

    # -------------------------- DEFINE param functions -----------------------

    def _defineParams(self, form):
        form.addSection(label='Input')

        form.addParam('inputSet', pwprot.MultiPointerParam,
                      pointerClass='SetOfExportFiles',
                      label="Exported files to scale",
                      minNumObjects=1,
                      help="")

        form.addParam('outputName', pwprot.StringParam,
                      label='Name of output file',
                      default='MERGED.HKL',
                      help="",
                      )

        form.addParam('unitCell', pwprot.StringParam,
                      label='Unit cell parameters',
                      allowsNull=True,
                      default=None,
                      help="",
                      )

        form.addParam('spaceGroupNumber', pwprot.IntParam,
                      label='Space group (number)',
                      default=None,
                      allowsNull=True,
                      help="",
                      )

        form.addParam('dMin', pwprot.FloatParam,
                      default=None,
                      allowsNull=True,
                      label="High resolution limit",
                      help="The maximum resolution limit")

        form.addParam('dMax', pwprot.FloatParam,
                      default=None,
                      allowsNull=True,
                      label="Low resolution limit",
                      help="The minimum resolution limit")

        form.addParam('saveCorrImg', pwprot.BooleanParam,
                      label='Save correction images?',
                      default=False,
                      help="",
                      expertLevel=pwprot.LEVEL_ADVANCED,
                      )

   # -------------------------- INSERT functions ------------------------------

    def _insertAllSteps(self):
        self._insertFunctionStep('convertInputStep')
        self._insertFunctionStep('scaleStep')
        self._insertFunctionStep('createOutputStep')

    # -------------------------- STEPS functions -------------------------------
    def convertInputStep(self):
        self._prepInputFile()

    def scaleStep(self):
        program = 'xscale'
        arguments = self._prepCommandLine()
        try:
            self.runJob(program, arguments)
        except:
            self.info(self.getError())

    def createOutputStep(self):
        outputSet = self._createSetOfExportFiles()
        eFile = ExportFile()
        eFile.setFilePath(self.getOutputFilePath())
        eFile.setFileType("XDS_ASCII")
        outputSet.append(eFile)
        outputSet.write()
        self._defineOutputs(exportedFileSet=outputSet)

    # -------------------------- INFO functions -------------------------------
    def _validate(self):
        errors = []
        return errors

    # -------------------------- UTILS functions ------------------------------
    def getFileNames(self):
        fileNames = []
        for exportSet in self._iterExportSets():
            for expFile in exportSet:
                if expFile.getFileType() is "XDS_ASCII":
                    fileNames.append(expFile.getFilePath())
        return fileNames

    def getOutputDirectory(self):
        return self._getExtraPath()

    def getOutputFile(self):
        return self.outputName.get()

    def getOutputFilePath(self):
        path = "/".join([self.getOutputDirectory(), self.getOutputFile()])
        return path

    def getInputFilePath(self):
        path = "/".join([self.getOutputDirectory(), "XSCALE.INP"])
        return path

    def getUnitCell(self):
        try:
            uc = self.unit_cell.get()
            return uc
        except AttributeError as e:
            self.info(e)
            return None

    def getSpaceGroup(self):
        try:
            sg = self.space_group_number.get()
            return sg
        except AttributeError as e:
            self.info(e)
            return None

    def getCorr(self):
        return self.saveCorrImg.get()

    def _getRes(self):
        d_min = self.dMin.get()
        d_max = self.dMax.get()
        try:
            if d_min and d_max:
                assert(d_min < d_max)
                return d_min, d_max
            else:
                return None
        except AssertionError as e:
            self.info("Bad choice of resolution:\n{}".format(e))
            return None

    def getDMin(self):
        if self._getRes():
            return self._getRes()[0]
        else:
            return None

    def getDMax(self):
        if self._getRes():
            return self._getRes()[1]
        else:
            return None

    def _iterExportSets(self):
        """ Iterate over all the input SetOfExportFile. """
        for pointer in self.inputSet:
            item = pointer.get()
            if item is None:
                break
            yield item

    def _prepInputFile(self):
        self.info(self.getFileNames())
        self._writeXscaleInp(input_fns=self.getFileNames(),
                             unit_cell=self.getUnitCell(),
                             space_group_number=self.getSpaceGroup(),
                             output_fn=self.getOutputFile(),
                             path=self.getOutputDirectory(),
                             save_correction_images=self.getCorr(),
                             d_min=self.getDMin(),
                             d_max=self.getDMax(),
                             )

    def _prepCommandLine(self):
        return self.getInputFilePath()

    def _writeXscaleInp(self,
                        input_fns,
                        unit_cell=None,
                        space_group_number=None,
                        output_fn="MERGED.HKL",
                        path=None,
                        save_correction_images=False,
                        d_min=None,
                        d_max=None,
                        ):
        if path:
            inpFile = "XSCALE.INP"
        else:
            inpFile = "/".join([path, "XSCALE.INP"])

        self.info("xscale input file: {}".format(inpFile))

        if save_correction_images:
            saveCorr = "TRUE"
        else:
            saveCorr = "FALSE"

        with open(inpFile, "w") as f:
            # prevent local directory being littered with .cbf files
            print("SAVE_CORRECTION_IMAGES= {}".format(saveCorr), file=f)
            if space_group_number:
                print("SPACE_GROUP_NUMBER= {}".format(
                    space_group_number), file=f)
            if unit_cell:
                print("UNIT_CELL_CONSTANTS= {}".format(unit_cell), file=f)

            print(file=f)
            print("OUTPUT_FILE= {}".format(output_fn), file=f)
            print(file=f)

            for fn in input_fns:
                self.info("Filefn)
                print(f"    INPUT_FILE= {fn}", file=f)
                if d_min and d_max:
                    print("    INCLUDE_RESOLUTION_RANGE= {} {}".format(
                        d_max, d_min), file=f)
                print(file=f)
