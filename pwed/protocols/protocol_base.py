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

import pyworkflow as pw
import pyworkflow.protocol as pwprot
from pyworkflow.mapper import SqliteDb


from pwed.objects import DiffractionImage, SetOfDiffractionImages, DiffractionSpot, SetOfSpots, IndexedSpot, SetOfIndexedSpots, SetOfExportFiles


class EdBaseProtocol(pwprot.Protocol):
    """ Base class to all EM protocols.
    It will contains some common functionalities.
    """
    _base = True

    def __createSet(self, SetClass, template, suffix, **kwargs):
        """ Create a set and set the filename using the suffix.
        If the file exists, it will be deleted. """
        setFn = self._getPath(template % suffix)
        # Close the connection to the database if
        # it is open before deleting the file
        pw.utils.cleanPath(setFn)

        SqliteDb.closeConnection(setFn)
        setObj = SetClass(filename=setFn, **kwargs)
        return setObj

    def _createSetOfDiffractionImages(self, suffix=''):
        return self.__createSet(SetOfDiffractionImages,
                                'diffraction-images%s.sqlite', suffix)

    def _createSetOfSpots(self, suffix=''):
        return self.__createSet(SetOfSpots, 'diffraction-spots%s.sqlite', suffix)

    def _createSetOfIndexedSpots(self, suffix=''):
        return self.__createSet(SetOfIndexedSpots, 'indexed-spots%s.sqlite', suffix)

    def _createSetOfExportFiles(self, suffix=''):
        return self.__createSet(SetOfExportFiles, 'export-files%s.sqlite', suffix)


class EdProtFindSpots(EdBaseProtocol):
    """ Base protocol for implementations of finding diffraction spots.
    """
    pass


class EdProtIndexSpots(EdBaseProtocol):
    pass


class EdProtRefineSpots(EdBaseProtocol):
    pass


class EdProtIntegrateSpots(EdBaseProtocol):
    pass


class EdProtExport(EdBaseProtocol):
    pass
