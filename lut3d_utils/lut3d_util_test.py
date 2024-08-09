import math
import tempfile
import unittest

from lut3d_utils import lut3d_util
from lut3d_utils import mpeg
from lut3d_utils.lut3d_util import Lut3d


def compute_lut_diff(lut1, lut2):
  rmse = 0
  max_abs_diff = 0

  for i in range(0, len(lut1.lut_value)):
    for j in range(0, 3):
      diff = lut1.lut_value[i][j] - lut2.lut_value[i][j]
      max_abs_diff = max(max_abs_diff, max(abs(diff), max_abs_diff))
      rmse += diff * diff

  return math.sqrt(diff / len(lut1.lut_value)), max_abs_diff


class TestLut3dUtil(unittest.TestCase):

  def testFailsOnMissingInput(self):
    self.assertFalse(
        lut3d_util.inject_lut3d_mpeg4(
            '/path/to/invalid/file', '/dev/null', None
        )
    )

  def testReadWriteCube(self):
    lut = Lut3d()
    with tempfile.NamedTemporaryFile(suffix='.cube') as f:
      self.assertTrue(
          lut.read_from_cube_file(
              'lut3d_utils/data/hlg_bt2020_to_bt709_33x33x33.cube'
          )
      )
      self.assertTrue(lut.write_to_cube_file(f.name))

      actual_lut = Lut3d()
      self.assertTrue(actual_lut.read_from_cube_file(f.name))
      self.assertEqual(actual_lut.lut_size, lut.lut_size)

      rmse, max_abs_diff = compute_lut_diff(lut, actual_lut)
      self.assertLess(rmse, 1e-6)
      self.assertLess(max_abs_diff, 1e-6)

  def testInsertMetadata(self):
    lut = Lut3d(
        output_colour_primaries=mpeg.constants.ColourPrimaries.COLOUR_PRIMARIES_BT709,
        output_colour_transfer_characteristics=mpeg.constants.ColourTransferCharacteristics.COLOUR_TRANSFER_CHARACTERISTICS_BT709,
    )
    self.assertTrue(
        lut.read_from_cube_file(
            'lut3d_utils/data/hlg_bt2020_to_bt709_33x33x33.cube'
        )
    )
    self.assertFalse(
        lut3d_util.parse_lut3d_mpeg4('lut3d_utils/data/testsrc_1920x1080.mp4')
    )

    with tempfile.NamedTemporaryFile(suffix='.mp4') as output_file:
      self.assertTrue(
          lut3d_util.inject_lut3d_mpeg4(
              'lut3d_utils/data/testsrc_1920x1080.mp4', output_file.name, lut
          )
      )

      actual_lut = lut3d_util.parse_lut3d_mpeg4(output_file.name)
      self.assertTrue(actual_lut != None)
      self.assertEqual(actual_lut.lut_size, lut.lut_size)

      rmse, max_abs_diff = compute_lut_diff(lut, actual_lut)
      self.assertLess(rmse, 1e-6)
      self.assertLess(max_abs_diff, 2e-5)


if __name__ == '__main__':
  unittest.main()
