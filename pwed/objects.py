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

        # Exposure time (in seconds)
        self._exposureTime = pwobj.Float()

        # TwoTheta
        self._twoTheta = pwobj.Float()

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

        # Experiment time
        self._collectionTime = pwobj.String()

        # Add parameter to state if the image should be ignored in processing
        self._ignore = pwobj.Boolean()

        # Add information about goniometer rotation axis relative to image
        self._rotX=pwobj.Float()
        self._rotY=pwobj.Float()
        self._rotZ=pwobj.Float()

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

    def getDirName(self):
        return os.path.dirname(self.getFileName())

    def getExtension(self):
        _, extension = os.path.splitext(self.getBaseName())
        return extension

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
    
    def getBeamCenterMm(self):
        x = self._beamCenterX.get() * self._pixelSizeX.get()
        y = self._beamCenterY.get() * self._pixelSizeY.get()
        return x,y

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

    def getExposureTime(self):
        return self._exposureTime.get()

    def setExposureTime(self, value):
        self._exposureTime.set(value)

    def getTwoTheta(self):
        return self._twoTheta.get()

    def setTwoTheta(self, value):
        self._twoTheta.set(value)

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
        return self._dimX.get(), self._dimY.get()

    def setDim(self, value):
        self._dimX.set(value)
        self._dimY.set(value)

    def getDetector(self):
        return self._acquisition.get()

    def setDetector(self, detector):
        self._detector = detector

    def getWavelength(self):
        return self._wavelength.get()

    def setWavelength(self, value):
        self._wavelength.set(value)

    def getCollectionTime(self):
        return self._collectionTime.get()

    def setCollectionTime(self, value):
        self._collectionTime.set(value)

    def setRotationAxis(self,rotAxis):
        self._rotX.set(rotAxis[0])
        self._rotY.set(rotAxis[1])
        self._rotZ.set(rotAxis[2])
    
    def getRotationAxis(self):
        return self._rotX.get(),self._rotY.get(),self._rotZ.get()

    def setIgnore(self, true_or_false=False):
        self._ignore.set(true_or_false)
    
    def getIgnore(self):
        return self._ignore.get()


class SetOfDiffractionImages(EdBaseSet):
    """ Represents a set of Images
    """
    ITEM_TYPE = DiffractionImage

    def __init__(self, **kwargs):
        EdBaseSet.__init__(self, **kwargs)

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
