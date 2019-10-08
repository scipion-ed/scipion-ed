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

import pyworkflow as pw
import pyworkflow.tests as pwtests

import pwed
from pwed.objects import DiffractionImage, SetOfDiffractionImages
from pwed.protocols import ProtImportDiffractionImages


pw.Config.setDomain(pwed)


class TestEdBase(pwtests.BaseTest):
    @classmethod
    def setUpClass(cls):
        pwtests.setupTestOutput(cls)

    def test_plugin(self):
        self.assertTrue(hasattr(pwed, 'Domain'))

        # Check that defined objects here are found
        objects = pwed.Domain.getObjects()

        expected = ['DiffractionImage', 'SetOfDiffractionImages']
        for e in expected:
            self.assertTrue(e in objects, "%s should be in Domain.getObjects" % e)

    def test_create_diffractionImages(self):
        setFn = self.getOutputPath('diffraction-images.sqlite')
        pw.utils.cleanPath(setFn)

        print("Creating set: %s" % os.path.abspath(setFn))
        testSet = SetOfDiffractionImages(filename=setFn)

        dImg = DiffractionImage()
        dImg.setDistance(1000)
        dImg.setOscillation(-33.90, 0.3512)
        pattern = '/data/experiment01/images/img%04d.img'
        N = 100

        for i in range(1, N+1):
            dImg.setFileName(pattern % i)
            dImg.setBeamCenter(i*100, i*200)
            dImg.setObjId(i)
            testSet.append(dImg)

        testSet.write()
        testSet.close()

        testSet2 = SetOfDiffractionImages(filename=setFn)
        self.assertEqual(testSet2.getSize(), N)
        for dImg2 in testSet2:
            self.assertEqual(dImg2.getDistance(), 1000)

        testSet2.close()


class TestEdBaseProtocols(pwtests.BaseTest):
    @classmethod
    def setUpClass(cls):
        pwtests.setupTestProject(cls, writeLocalConfig=True)
        cls.dataPath = os.environ.get('SCIPION_TEST_ED',
                                      '/data/work_software/scipion-ed/')

        if not os.path.exists(cls.dataPath):
            raise Exception("Can not run tomo tests, "
                            "SCIPION_TEST_ED variable not defined. ")

    def _runImportImages(self, filesPattern):
        protImport = self.newProtocol(
            ProtImportDiffractionImages,
            filesPath=os.path.join(self.dataPath),
            filesPattern=filesPattern)
        self.launchProtocol(protImport)
        return protImport

    def test_import(self):
        protImport = self._runImportImages('{TS}/RED/{TI}.mrc')
        output = getattr(protImport, 'outputDiffractionImages', None)
        self.assertFalse(output is None)

        protImport2 = self._runImportImages('{TS}/SMV/data/{TI}.img')
        output = getattr(protImport2, 'outputDiffractionImages', None)
        self.assertFalse(output is None)

