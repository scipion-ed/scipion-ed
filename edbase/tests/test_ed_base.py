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
from pyworkflow.tests import BaseTest, setupTestOutput, DataSet, setupTestProject
from pyworkflow.em import Domain, CTFModel

from edbase.objects import DiffractionImage, SetOfDiffractionImages
from edbase.protocols import ProtImportDiffractionImages


class TestEdBase(BaseTest):
    @classmethod
    def setUpClass(cls):
        setupTestOutput(cls)
        #cls.dataset = DataSet.getDataSet('relion_tutorial')
        #cls.getFile = cls.dataset.getFile

    def test_plugin(self):
        # Really stupid test to check that tomo plugin is defined
        edbase = Domain.getPlugin('edbase')

        self.assertFalse(edbase is None)
        self.assertTrue(hasattr(edbase, 'Plugin'))

        # Check that defined objects here are found
        objects = Domain.getObjects()

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


class TestEdBaseProtocols(BaseTest):
    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)
        cls.dataPath = os.environ.get('SCIPION_TEST_ED', '/data/work_software/scipion-ed/')

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

#
#
# class TestTomoImportTs(BaseTest):
#         @classmethod
#         def setUpClass(cls):
#             setupTestProject(cls)
#             cls.empiar10164 = os.environ.get('SCIPION_TOMO_EMPIAR10164', '')
#             cls.etomoTutorial = os.environ.get('SCIPION_TOMO_ETOMO_TUTORIAL', '')
#
#         def _runImportTiltSeriesM(self, filesPattern='{TS}_{TO}_{TA}.mrc'):
#             if not os.path.exists(self.empiar10164):
#                 raise Exception("Can not run tomo tests, "
#                                 "SCIPION_TOMO_EMPIAR10164 variable not defined. ")
#
#             protImport = self.newProtocol(
#                 tomo.protocols.ProtImportTiltSeries,
#                 importType=tomo.protocols.ProtImportTiltSeries.IMPORT_TYPE_MOVS,
#                 filesPath=os.path.join(self.empiar10164, 'data', 'frames'),
#                 filesPattern=filesPattern,
#                 voltage=300,
#                 magnification=105000,
#                 sphericalAberration=2.7,
#                 amplitudeContrast=0.1,
#                 samplingRate=1.35,
#                 doseInitial=0,
#                 dosePerFrame=0.3)
#             self.launchProtocol(protImport)
#             return protImport
#
#         def _runImportTiltSeries(self):
#             if not os.path.exists(self.etomoTutorial):
#                 raise Exception("Can not run tomo tests, "
#                                 "SCIPION_TOMO_ETOMO_TUTORIAL variable not defined. ")
#
#             protImport = self.newProtocol(
#                 tomo.protocols.ProtImportTiltSeries,
#                 importType=tomo.protocols.ProtImportTiltSeries.IMPORT_TYPE_MICS,
#                 filesPath=os.path.join(self.etomoTutorial),
#                 filesPattern='BB{TS}.st',
#                 voltage=300,
#                 magnification=105000,
#                 sphericalAberration=2.7,
#                 amplitudeContrast=0.1,
#                 samplingRate=1.35,
#                 doseInitial=0,
#                 dosePerFrame=0.3)
#             self.launchProtocol(protImport)
#             return protImport
#
#         def test_importTiltSeriesM(self):
#             protImport = self._runImportTiltSeriesM()
#             output = getattr(protImport, 'outputTiltSeriesM', None)
#             self.assertFalse(output is None)
#             self.assertEqual(output.getSize(), 3)
#
#             return protImport
#
#         def test_importTiltSeries(self):
#             protImport = self._runImportTiltSeries()
#             output = getattr(protImport, 'outputTiltSeries', None)
#             self.assertFalse(output is None)
#             self.assertEqual(output.getSize(), 2)
#
# # TODO: This test is based on https://www.ebi.ac.uk/pdbe/emdb/empiar/entry/10087/
# #  We need to refactor once we decide the final test infrastructures and the data sets to use
# # class TestTomoImportTomogramsProtocols(BaseTest):
# #     @classmethod
# #     def setUpClass(cls):
# #         setupTestProject(cls)
# #         cls.dataPath = os.environ.get('SCIPION_TOMO_EMPIAR10164', '')
# #
# #         if not os.path.exists(cls.dataPath):
# #             raise Exception("Can not run tomo tests, "
# #                             "SCIPION_TOMO_EMPIAR10164 variable not defined. ")
# #
# #     def _runImportTomograms(self):
# #         protImport = self.newProtocol(
# #             tomo.protocols.ProtImportTomograms,
# #             filesPath=os.path.join(self.dataPath, 'data', 'frames'),
# #             filesPattern='C2_tomo02.mrc',
# #             samplingRate=1.35)
# #         self.launchProtocol(protImport)
# #         return protImport
# #
# #     def test_importTomograms(self):
# #         protImport = self._runImportTomograms()
# #         output = getattr(protImport, 'outputTomogram', None)
# #         self.assertFalse(output is None)
# #
# #         return protImport
#
#
# class TestTomoPreprocessing(BaseTest):
#     @classmethod
#     def setUpClass(cls):
#         setupTestProject(cls)
#         cls.dataPath = os.environ.get('SCIPION_TOMO_EMPIAR10164', '')
#
#         if not os.path.exists(cls.dataPath):
#             raise Exception("Can not run tomo tests, "
#                             "SCIPION_TOMO_EMPIAR10164 variable not defined. ")
#
#     def _runImportTiltSeriesM(self, filesPattern='{TS}_{TO}_{TA}.mrc'):
#         protImport = self.newProtocol(
#             tomo.protocols.ProtImportTiltSeries,
#             importType=tomo.protocols.ProtImportTiltSeries.IMPORT_TYPE_MOVS,
#             filesPath=os.path.join(self.dataPath, 'data', 'frames'),
#             filesPattern=filesPattern,
#             voltage=300,
#             magnification=105000,
#             sphericalAberration=2.7,
#             amplitudeContrast=0.1,
#             samplingRate=1.35,
#             doseInitial=0,
#             dosePerFrame=0.3)
#         self.launchProtocol(protImport)
#         return protImport
#
#     def test_preprocess1(self):
#         """ Run the basic preprocessing pipeline for just one TS. """
#         protImport = self._runImportTiltSeriesM(
#             filesPattern='{TS}7_{TO}_{TA}.mrc')
#         output = getattr(protImport, 'outputTiltSeriesM', None)
#         self.assertFalse(output is None)
#         self.assertEqual(protImport.outputTiltSeriesM.getSize(), 1)
#
#         gpuList = os.environ.get('SCIPION_TEST_GPULIST', '0')
#         threads = len(gpuList.split()) + 1
#
#         protMc = self.newProtocol(
#             tomo.protocols.ProtTsMotionCorr,
#             inputTiltSeriesM=protImport.outputTiltSeriesM,
#             binFactor=2.0,
#             gpuList=gpuList,
#             numberOfThreads=threads
#         )
#
#         self.launchProtocol(protMc)
#
#         protGctf = self.newProtocol(
#             tomo.protocols.ProtTsGctf,
#             inputTiltSeries=protMc.outputTiltSeries,
#             gpuList=gpuList,
#             numberOfThreads=threads,
#         )
#         self.launchProtocol(protGctf)
#
#         protImodAuto = self.newProtocol(
#             tomo.protocols.ProtImodAuto3D,
#             inputTiltSeries=protGctf.outputTiltSeries,
#             excludeList=1,
#             zWidth=400,
#             useRaptor=True,
#             markersDiameter=20,
#             markersNumber=20
#         )
#         self.launchProtocol(protImodAuto)


if __name__ == 'main':
    pass