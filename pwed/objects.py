# -*- coding: utf-8 -*-
#  **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (delarosatrevin@scilifelab.se) [1]
# *              Viktor E. G. Bengtsson (viktor.bengtsson@mmk.su.se)   [2]
# *
# * [1] SciLifeLab, Stockholm University
# * [2] MMK, Stockholm University
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

import pyworkflow.object as pwobj

import pwed
from .constants import NO_INDEX


class EdBaseObject(pwobj.OrderedObject):
    """ Simple base class from which all objects in this Domain will 
    inherit from.
    """
    pass


class EdBaseSet(pwobj.Set, EdBaseObject):
    """ Simple base Set class. """
    def _loadClassesDict(self):
        return pwed.Domain.getMapperDict()


class Detector(EdBaseObject):
    """ Store basic properties of detectors. """
    def __init__(self, **kwargs):
        EdBaseObject.__init__(self, **kwargs)
        # Detector type
        self._type = pwobj.String()
        self._serialNumber = pwobj.String()


class DiffractionImage(EdBaseObject):
    """Represents an EM Image object"""
    def __init__(self, location=None, **kwargs):
        """
         Params:
        :param location: Could be a valid location: (index, filename)
        or  filename
        """
        EdBaseObject.__init__(self, **kwargs)
        # Image location is composed by an index and a filename
        self._index = pwobj.Integer(0)
        self._filename = pwobj.String()

        # Detector distance of this image
        self._distance = pwobj.Float()

        # Where oscillation starts and its range
        self._oscStart = pwobj.Float()
        self._oscRange = pwobj.Float()

        # Beam center (in pixels)
        self._beamCenterX = pwobj.Float()
        self._beamCenterY = pwobj.Float()

        if location:
            self.setLocation(location)

    def getIndex(self):
        return self._index.get()

    def setIndex(self, index):
        self._index.set(index)

    def getFileName(self):
        """ Use the _objValue attribute to store filename. """
        return self._filename.get()

    def setFileName(self, filename):
        """ Use the _objValue attribute to store filename. """
        self._filename.set(filename)

    def getLocation(self):
        """ This function return the image index and filename.
        It will only differs from getFileName, when the image
        is contained in a stack and the index make sense.
        """
        return self.getIndex(), self.getFileName()

    def setLocation(self, *args):
        """ Set the image location, see getLocation.
        Params:
            First argument can be:
             1. a tuple with (index, filename)
             2. a index, this implies a second argument with filename
             3. a filename, this implies index=NO_INDEX
        """
        first = args[0]
        t = type(first)
        if t == tuple:
            index, filename = first
        elif t == int:
            index, filename = first, args[1]
        elif t == str:
            index, filename = NO_INDEX, first
        else:
            raise Exception('setLocation: unsupported type %s as input.' % t)

        self.setIndex(index)
        self.setFileName(filename)

    def getBaseName(self):
        return os.path.basename(self.getFileName())

    def getDistance(self):
        """ Return distance to the detector (in mm). """
        return self._distance.get()

    def setDistance(self, value):
        self._distance.set(value)

    def getOscillation(self):
        return self._oscStart.get(), self._oscRange.get()

    def setOscillation(self, start, range):
        self._oscStart.set(start)
        self._oscRange.set(range)

    def getBeamCenter(self):
        return self._beamCenterX.get(), self._beamCenterY.get()

    def setBeamCenter(self, x, y):
        self._beamCenterX.set(x)
        self._beamCenterY.set(y)

    def copyInfo(self, other):
        """ Copy basic information """
        self.copyAttributes(other, '_samplingRate')

    def copyLocation(self, other):
        """ Copy location index and filename from other image. """
        self.setIndex(other.getIndex())
        self.setFileName(other.getFileName())

    def getFiles(self):
        filePaths = set()
        filePaths.add(self.getFileName())
        return filePaths


class SetOfDiffractionImages(EdBaseSet):
    """ Represents a set of Images

    HEADER_BYTES=512;
DIM=2;
BYTE_ORDER=little_endian;
TYPE=unsigned_short;
SIZE1=516;
SIZE2=516;
PIXEL_SIZE=0.055;
BIN=1x1;
BIN_TYPE=HW;
ADC=fast;
CREV=1;
BEAMLINE=TimePix_SU;
DETECTOR_SN=901;
DATE=2019-05-03 12:10:21.302198;
TIME=0.3;
DISTANCE=532.2773;
TWOTHETA=0.0;
PHI=-33.9000;
OSC_START=-33.9000;
OSC_RANGE=0.3512;
WAVELENGTH=0.0251;
BEAM_CENTER_X=219.7000;
BEAM_CENTER_Y=226.6500;
DENZO_X_BEAM=12.4657;
DENZO_Y_BEAM=12.0835;

    """
    ITEM_TYPE = DiffractionImage

    def __init__(self, **kwargs):
        EdBaseSet.__init__(self, **kwargs)

        # Pixel size of the image (in millimeters)
        self._pixelSizeX = pwobj.Float()
        self._pixelSizeY = pwobj.Float()

        # Dimensions of images in this set (number of pixels)
        self._dimX = pwobj.Integer()
        self._dimY = pwobj.Integer()

        # Wavelength
        self._wavelength = pwobj.Float()

        # Detector type
        self._detector = Detector()

    def getPixelSize(self):
        """ Return the pixel size, assuming it is the same
        in both X and Y.
        """
        return self._pixelSizeX.get()

    def setPixelSize(self, value):
        """
        Set pixel size for both X and Y
        :param value: new pixel size value
        :return:
        """
        self._pixelSizeX.set(value)
        self._pixelSizeY.set(value)

    def getDim(self):
        return self._dimX.get()

    def setDim(self, value):
        self._dimX.set(value)
        self._dimY.set(value)

    def getDetector(self):
        return self._acquisition

    def setDetector(self, detector):
        self._detector = detector

    def copyInfo(self, other):
        """ Copy basic information (sampling rate and ctf)
        from other set of images to current one"""
        self.copyAttributes(other, '_pixelSizeX', '_pixelSizeY',
                            '_dimX', '_dimY', '_wavelength')
        # TODO: Implement copyInfo method in Detector class
        # self._detector.copyInfo(other._detector)

    def getFiles(self):
        filePaths = set()
        uniqueFiles = self.aggregate(['count'], '_filename', ['_filename'])

        for row in uniqueFiles:
            filePaths.add(row['_filename'])
        return filePaths

