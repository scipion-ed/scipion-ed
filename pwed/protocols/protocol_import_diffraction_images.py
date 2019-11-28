# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (delarosatrevin@scilifelab.se) [1]
# *
# * [1] SciLifeLab, Stockholm University
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
from glob import glob

import pyworkflow as pw
import pyworkflow.protocol as pwprot

from pwed.objects import DiffractionImage, SetOfDiffractionImages
from .protocol_base import EdBaseProtocol


class ProtImportDiffractionImages(EdBaseProtocol):
    """ Base class for other Import protocols.
    All imports protocols will have:
    1) Several options to import from (_getImportOptions function)
    2) First option will always be "from files". (for this option
      files with a given pattern will be retrieved  and the ### will
      be used to mark an ID part from the filename.
      - For each file a function to process it will be called
        (_importFile(fileName, fileId))
    """
    IMPORT_FROM_FILES = 0

    # How to handle the input files into the project
    IMPORT_COPY_FILES = 0
    IMPORT_LINK_ABS = 1
    IMPORT_LINK_REL = 2

    IMPORT_TYPE_MICS = 0
    IMPORT_TYPE_MOVS = 1

    ANGLES_FROM_FILES = 0
    ANGLES_FROM_HEADER = 1
    ANGLES_FROM_MDOC = 2

    _label = 'import diffraction images'

    # -------------------------- DEFINE param functions -----------------------
    def _defineParams(self, form):
        form.addSection(label='Import')

        form.addParam('filesPath', pwprot.PathParam,
                      label="Files directory",
                      help="Root directory of the tilt-series (or movies).")
        form.addParam('filesPattern', pwprot.StringParam,
                      label='Pattern',
                      help="Pattern of the tilt series\n\n"
                           "The pattern can contain standard wildcards such as\n"
                           "*, ?, etc.\n\n"
                           "It should also contains the following special tags:"
                           "   {TS}: tilt series identifier "
                           "         (can be any UNIQUE part of the path).\n"
                           "   {TI}: image identifier "
                           "         (an integer value, unique within a tilt-series).\n"
                           "Examples:\n"
                           "")
        form.addParam('importAction', pwprot.EnumParam,
                      default=self.IMPORT_LINK_REL,
                      choices=['Copy files',
                               'Absolute symlink',
                               'Relative symlink'],
                      display=pwprot.EnumParam.DISPLAY_HLIST,
                      expertLevel=pwprot.LEVEL_ADVANCED,
                      label="Import action on files",
                      help="By default ...")

        form.addParam('skipImages', pwprot.IntParam, default=0,
                      label="Skip images",
                      help="Images to skip during processing.\n"
                           "Required for data collected with defocusing to "
                           "track images back to the aperture or beam.\n"
                           "A value of 10 will skip every 10th frame.")

    # -------------------------- INSERT functions ------------------------------
    def _insertAllSteps(self):
        self.loadPatterns()
        self._insertFunctionStep('importStep', self._pattern)

    # -------------------------- STEPS functions -------------------------------
    def importStep(self, pattern):
        self.loadPatterns()
        self.info("Using glob pattern: '%s'" % self._globPattern)
        self.info("Using regex pattern: '%s'" % self._regexPattern)

        outputSet = self._createSetOfDiffractionImages()

        # f, _, _ = self.getMatchingFiles()[0]
        # h = self.readSmvHeader(f)

        dImg = DiffractionImage()

        for f, ts, ti in self.getMatchingFiles():
            dImg.setFileName(f)
            dImg.setObjId(int(ti))
            try:
                if f.endswith('.img'):
                    h = self.readSmvHeader(f)
                    dImg.setPixelSize(float(h.get('PIXEL_SIZE')))
                    dImg.setDim(int(h.get('SIZE1')))
                    dImg.setWavelength(float(h.get('WAVELENGTH')))
                    dImg.setDistance(float(h.get('DISTANCE')))
                    dImg.setOscillation(float(h.get('OSC_START')),
                                        float(h.get('OSC_RANGE')))
                    dImg.setBeamCenter(float(h.get('BEAM_CENTER_X')),
                                       float(h.get('BEAM_CENTER_Y')))
                    dImg.setExposureTime(float(h.get('TIME')))
                    dImg.setTwoTheta(float(h.get('TWOTHETA')))
            except Exception as e:
                print(e)

            outputSet.append(dImg)

        outputSet.write()

        self._defineOutputs(outputDiffractionImages=outputSet)

    # -------------------------- INFO functions -------------------------------
    def _validate(self):
        errors = []
        return errors

    # -------------------------- BASE methods to be overridden -----------------
    def _getImportChoices(self):
        """ Return a list of possible choices
        from which the import can be done.
        (usually packages form such as: xmipp3, eman2, relion...etc.
        """
        return ['files']

    # -------------------------- UTILS functions ------------------------------
    def loadPatterns(self):
        """ Expand the pattern using environ vars or username
        and also replacing special character # by digit matching.
        """
        self._pattern = os.path.join(self.filesPath.get('').strip(),
                                     self.filesPattern.get('').strip())

        def _replace(p, ts, ti):
            p = p.replace('{TS}', ts)
            p = p.replace('{TI}', ti)
            return p

        self._regexPattern = _replace(self._pattern.replace('*', '(.*)'),
                                      '(?P<TS>.*)', r'(?P<TI>\d+)')
        self._regex = re.compile(self._regexPattern)
        self._globPattern = _replace(self._pattern, '*', '*')

    def getMatchingFiles(self):
        """ Return a sorted list with the paths of files that
        matched the pattern.
        """
        self.loadPatterns()

        filePaths = glob(self._globPattern)
        filePaths.sort()

        matchingFiles = []
        for f in filePaths:
            m = self._regex.match(f)
            if m is not None:
                matchingFiles.append((f, m.group('TS'), int(m.group('TI'))))

        return matchingFiles

    def getCopyOrLink(self):
        # Set a function to copyFile or createLink
        # depending in the user selected option
        if self.copyFiles:
            return pw.utils.copyFile
        else:
            return pw.utils.createAbsLink

    def readSmvHeader(self, image_file):
        # Reimplemented from get_smv_header in
        # https://github.com/dials/dxtbx/blob/master/format/FormatSMV.py
        with open(image_file, "rb") as fh:
            header_info = fh.read(45).decode("ascii", "ignore")
            header_size = int(
                header_info.split("\n")[1].split(
                    "=")[1].replace(";", "").strip()
            )
            header_text = fh.read(header_size).decode("ascii", "ignore")
        header_dictionary = {}

        # Check that we have the whole header, contained within { }.  Stop
        # extracting data once a record solely composed of a closing curly
        # brace is seen.  If there is no such character in header_text
        # either HEADER_BYTES caused a short read of the header or the
        # header is malformed.
        for record in header_text.split("\n"):
            if record == "}":
                break
            if "=" not in record:
                continue

            key, value = record.replace(";", "").split("=")

            header_dictionary[key.strip()] = value.strip()

        return header_dictionary
