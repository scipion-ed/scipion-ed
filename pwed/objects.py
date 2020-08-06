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
import numpy

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
        self._rotX = pwobj.Float()
        self._rotY = pwobj.Float()
        self._rotZ = pwobj.Float()

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
        return x, y

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
        return self._detector.get()

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

    def setRotationAxis(self, rotAxis):
        self._rotX.set(rotAxis[0])
        self._rotY.set(rotAxis[1])
        self._rotZ.set(rotAxis[2])

    def getRotationAxis(self):
        return self._rotX.get(), self._rotY.get(), self._rotZ.get()

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
        self._skipImages = pwobj.Integer()
        self._dialsModelPath = pwobj.String()
        self._dialsReflPath = pwobj.String()

    def setSkipImages(self, skip):
        self._skipImages.set(skip)

    def getSkipImages(self):
        return self._skipImages.get()

    def setDialsModel(self, path):
        self._dialsModelPath.set(path)

    def getDialsModel(self):
        return self._dialsModelPath.get()

    def setDialsRefl(self, path):
        self._dialsReflPath.set(path)

    def getDialsRefl(self):
        return self._dialsReflPath.get()

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


class DiffractionSpot(EdBaseObject):
    ''' Represents an individual diffraction spot. '''

    def __init__(self, **kwargs):
        EdBaseObject.__init__(self, **kwargs)
        self._spotId = pwobj.Integer()
        self._bbox = pwobj.CsvList()
        self._flag = pwobj.Integer()
        self._intensitySumValue = pwobj.Float()
        self._intensitySumVariance = pwobj.Float()
        self._nSignal = pwobj.Integer()
        self._panel = pwobj.Integer()
        self._shoebox = None
        self._xyzobsPxValue = pwobj.CsvList()
        self._xyzobsPxVariance = pwobj.CsvList()

    def setSpotId(self, value):
        self._spotId.set(value)

    def getSpotId(self):
        return self._spotId.get()

    def setBbox(self, value):
        if type(value) is numpy.ndarray:
            self._bbox.set(list(value))
        elif type(value) is list:
            self._bbox.set(value)
        else:
            raise TypeError

    def getBbox(self):
        return self._bbox.get()

    def setFlag(self, value):
        self._flag.set(value)

    def getFlag(self):
        return self._flag.get()

    def setIntensitySumValue(self, value):
        self._intensitySumValue.set(value)

    def getIntensitySumValue(self):
        return self._intensitySumValue.get()

    def setIntensitySumVariance(self, value):
        self._intensitySumVariance.set(value)

    def getIntensitySumVariance(self):
        return self._intensitySumVariance.get()

    def setNSignal(self, value):
        self._nSignal.set(value)

    def getNSignal(self):
        return self._nSignal.get()

    def setPanel(self, value):
        self._panel.set(value)

    def getPanel(self):
        return self._panel.get()

    def setShoebox(self, value):
        self._shoebox.set(value)

    def getShoebox(self):
        return self._shoebox.get()

    def setXyzobsPxValue(self, value):
        if type(value) is numpy.ndarray:
            self._xyzobsPxValue.set(list(value))
        elif type(value) is list:
            self._xyzobsPxValue.set(value)
        else:
            raise TypeError

    def getXyzobsPxValue(self):
        return self._xyzobsPxValue.get()

    def setXyzobsPxVariance(self, value):
        if type(value) is numpy.ndarray:
            self._xyzobsPxVariance.set(list(value))
        elif type(value) is list:
            self._xyzobsPxVariance.set(value)
        else:
            raise TypeError

    def getXyzobsPxVariance(self):
        return self._xyzobsPxVariance.get()


class SetOfSpots(EdBaseSet):
    ''' Represents a set of diffraction spots, e.g. all spots in a diffraction experiment. '''

    ITEM_TYPE = DiffractionSpot

    def __init__(self, **kwargs):
        EdBaseSet.__init__(self, **kwargs)
        self._numberOfSpots = pwobj.Integer(0)
        self._skipImages = pwobj.Integer()
        self._dialsModelPath = pwobj.String()
        self._dialsReflPath = pwobj.String()

    def setSkipImages(self, skip):
        self._skipImages.set(skip)

    def getSkipImages(self):
        return self._skipImages.get()

    def setDialsModel(self, path):
        self._dialsModelPath.set(path)

    def getDialsModel(self):
        return self._dialsModelPath.get()

    def setDialsRefl(self, path):
        self._dialsReflPath.set(path)

    def getDialsRefl(self):
        return self._dialsReflPath.get()

    def setSpots(self, spots):
        self._numberOfSpots.set(spots)

    def getSpots(self):
        return self._numberOfSpots.get()


class IndexedSpot(DiffractionSpot):
    # TODO: Add HKL-indexing
    def __init__(self, **kwargs):
        DiffractionSpot.__init__(self, **kwargs)


class SetOfIndexedSpots(SetOfSpots, SetOfDiffractionImages):
    # TODO: Add space group
    # TODO: Add unit cell parameters
    ITEM_TYPE = IndexedSpot

    def __init__(self, **kwargs):
        SetOfSpots.__init__(self, **kwargs)
        SetOfDiffractionImages.__init__(self, **kwargs)
        self._dialsHtmlPath = pwobj.String()

    def setDialsHtml(self, path):
        self._dialsHtmlPath.set(path)

    def getDialsHtml(self):
        return self._dialsHtmlPath.get()


class ExportFile(EdBaseObject):
    def __init__(self, **kwargs):
        EdBaseObject.__init__(self, **kwargs)
        self._dialsExportedPath = pwobj.String()
        self._fileType = pwobj.String()

    def setFilePath(self, path):
        self._dialsExportedPath.set(path)

    def getFilePath(self):
        return self._dialsExportedPath.get()

    def setFileType(self, file_type):
        self._fileType.set(file_type)

    def getFileType(self):
        return self._fileType.get()


class SetOfExportFiles(EdBaseSet):
    ''' Represents a set of exported files. '''

    ITEM_TYPE = ExportFile

    def __init__(self, **kwargs):
        EdBaseSet.__init__(self, **kwargs)
