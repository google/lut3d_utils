#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2023 Google LLC All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utilities for examining/injecting the tone mapping metadata (3D LUT) in MP4/MOV files."""

import binascii
import io
import os
import struct
import uuid

from lut3d_utils import mpeg

MPEG_FILE_EXTENSIONS = [".mp4", ".mov"]
FIXED_POINT_FRACTIONAL_BITS = 15


class Lut3d(object):
  """A class for storing/parsing the tone mapping metadata (3D LUT).

  Attributes:
    output_colour_primaries: the output colour primaries associated with the
      output RGB of the LUT specifying the CIE 1931 xy chromaticity coordinates
      of the white point and the red, green, and blue primaries.
    output_colour_transfer_characteristics: output transfer function associated
      with the output RGB of the LUT specifying the nonlinear transfer function
      coefficients used to translate between RGB colour space values and YCbCr
      values.
    connection_uuid: the UUID that is used to match with the same UUID held in a
      referent
    lut_size: the size of the 1st, 2nd, and 3rd dimension of the 3D LUT (defined
      by lut_value).
    lut_value: the static 3D look-up-table (LUT) for colour mapping. The LUT
      maps an input RGB colour to an output R′G′B′ colour (big-endian). The
      lut_value is the table entries for the LUT from the minimum to the maximum
      input values, with the third component index changing fastest (i.e.
      lut_value[(r_i * n * n + g_i * n + b_i) * 3 + c_i]). The 3D LUT has
      dimensions lut_size-by-lut_size-by-lut_size-by-3.
  """

  def __init__(
      self,
      output_colour_primaries: mpeg.constants.ColourPrimaries = mpeg.constants.ColourPrimaries.COLOUR_PRIMARIES_UNSPECIFIED,
      output_colour_transfer_characteristics: mpeg.constants.ColourTransferCharacteristics = mpeg.constants.ColourTransferCharacteristics.COLOUR_TRANSFER_CHARACTERISTICS_UNSPECIFIED,
      connection_uuid: str = uuid.uuid4().bytes,
  ):
    self.output_colour_primaries = output_colour_primaries
    self.output_colour_transfer_characteristics = (
        output_colour_transfer_characteristics
    )
    self.connection_uuid = connection_uuid
    self.lut_size = 0
    self.lut_value = None


  def to_3d_index(self, i):
    """Convert the index into a 3d tuple with last dimension changing fastest."""
    return (
        (i // self.lut_size // self.lut_size),
        (i // self.lut_size) % self.lut_size,
        i % self.lut_size
    )


  def shuffle_indices(self, i):
    """
    Convert the 3d index i from last dimension changing fastest to first dimension
    changing fastest (or vice versa).
    """
    inds = self.to_3d_index(i)
    return (inds[2] * self.lut_size + inds[1]) * self.lut_size + inds[0]


  def read_from_cube_file(self, src):
    """Reads the lut_value from a lut3d file(.cube).

    Args:
      src: the source file to read lut3d values.

    Returns:
      True if succeeds. Otherwise False will be returned.
    """

    infile = os.path.abspath(src)
    try:
      in_fc = open(infile, "r")
    except ValueError:
      print(
          f"Error: {infile} does not exist or we do not have permission:"
          f" {ValueError.message}"
      )
      return False
    lines = in_fc.readlines()
    if lines is None or not lines:
      print("Error: The file has no data to read!")
      return False

    title = None
    domain_min = None
    domain_max = None
    lut3d_size = -1
    data = []
    # Parse keywords
    for line in lines:
      line = line.strip()
      if not line or line.startswith("#"):
        continue

      elements = line.split()
      if len(elements) != 3 and data:
        print(
            "Error: all keywords shall appear before any table  or the data"
            f" vector size shall be 3! Line: {line}"
        )
        return False
      if len(elements) != 3:
        if elements[0] == "TITLE" and title is None:
          title = " ".join(elements[1:])[1:-1]
        elif elements[0] == "DOMAIN_MIN" and domain_min is None:
          domain_min = [float(x) for x in elements[1:]]
        elif elements[0] == "DOMAIN_MAX" and domain_max is None:
          domain_max = [float(x) for x in elements[1:]]
        elif elements[0] == "LUT_1D_SIZE":
          print("Error: 1D LUT is not supported!")
          return False
        elif elements[0] == "LUT_3D_SIZE" and lut3d_size < 0:
          if len(elements) != 2:
            print(f"Error: LUT_3D_SIZE shall have only one param! Line: {line}")
            return False
          lut3d_size = int(elements[1])
          if lut3d_size < 2 or lut3d_size > 256:
            print(
                "Error: LUT_3D_SIZE shall be an integer in the range of"
                f" [2,256]. Size: {lut3d_size}"
            )
            return False
        else:
          print(f"Error: Unknow keyword or repeated keyword! Line: {line}")
          return False
      else:
        data.append([float(x) for x in elements])

    if lut3d_size < 0:
      print("Error: There is no LUT_3D_SIZE in the file.")
      return False
    if (domain_min and len(domain_min) != 3) or (
        domain_max and len(domain_max) != 3
    ):
      print(
          "Error: domain_min/domain_max shall be vector with 3 elements."
          f" domain_min: {domain_min}, domain_max: {domain_max}"
      )
      return False
    if len(data) != lut3d_size**3:
      print(
          f"Error: The data size is not as expected. Expected: {lut3d_size}^3 ="
          f" {lut3d_size**3}, Actual: {len(data)}"
      )
      return False
    self.lut_size = lut3d_size
    self.lut_value = [data[self.shuffle_indices(i)]
                      for i in range(self.lut_size**3)]
    in_fc.close()
    return True

  def create_prmd_contents(self):
    """Creats a Production Metadata (PRMD) box's contents (binary) from the self attributes.

    Returns:
      A binary message.
    """
    msg = io.BytesIO()
    msg.write(struct.pack(">I", 0))  # version and flags = (0, 0)
    msg.write(self.connection_uuid)  # metadata_connection_uuid
    msg.write(b"lut3")  # production_metadata_type
    msg.write(struct.pack(">B", self.lut_size))
    msg.write(struct.pack(">B", self.output_colour_primaries.value))
    msg.write(
        struct.pack(">B", self.output_colour_transfer_characteristics.value)
    )
    mul = 1 << FIXED_POINT_FRACTIONAL_BITS
    lut_value_fixed_point = [
        int(max(min(x, 1.9999), 0) * mul + 0.5)
        for rgb in self.lut_value
        for x in rgb
    ]
    msg.write(
        struct.pack(
            ">{}H".format(len(lut_value_fixed_point)), *lut_value_fixed_point
        )
    )
    return msg

  def read_from_prmd_contents(self, src):
    """Reads the atributes from a Production Metadata (PRMD) box's contents (binary).

    Args:
      src: a binary stream or message.

    Returns:
      True if succeeds. Otherwise False will be returned.
    """
    src_size = len(src)
    if src_size < 20:
      print("Not sufficient data to read!")
      return False
    msg = io.BytesIO(src)
    version_and_flags = struct.unpack(">I", msg.read(4))
    if version_and_flags[0] != 0:
      print(f"Invalid version and flags ({version_and_flags}), should be 0")
      return False
    self.connection_uuid = msg.read(16)
    metadata_type = msg.read(4)
    if metadata_type != b"lut3":
      print(f"Incorrect metadata type: {metadata_type}, unable to parse it!")
      return False
    if src_size - msg.tell() < 3:
      print("Not sufficient data to read!")
      return False
    self.lut_size = struct.unpack("B", msg.read(1))[0]
    self.output_colour_primaries = mpeg.constants.ColourPrimaries(
        struct.unpack("B", msg.read(1))[0]
    )
    self.output_colour_transfer_characteristics = (
        mpeg.constants.ColourTransferCharacteristics(
            struct.unpack("B", msg.read(1))[0]
        )
    )
    if src_size - msg.tell() < 3 * pow(self.lut_size, 3) * 2:
      print("Not sufficient data to read!")
      return False
    self.lut_value = [[]] * pow(self.lut_size, 3)
    denum = 1 << FIXED_POINT_FRACTIONAL_BITS
    for k in range(pow(self.lut_size, 3)):
      self.lut_value[k] = [
          float(struct.unpack(">H", msg.read(2))[0]) / denum for c in range(0, 3)]
    return True

  def print(self):
    """Prints the attributes."""
    print("Tone Map Metadata (3D LUT) {")
    print(
        "    metadata_connection_uuid (hex): "
        + binascii.hexlify(self.connection_uuid).decode("utf-8")
    )
    print(f"    lut_size: {self.lut_size}")
    print(
        f"    output_colour_primaries: {self.output_colour_primaries.__str__()}"
    )
    print(
        "    output_transfer_function:"
        f" {self.output_colour_transfer_characteristics.__str__()}"
    )
    print("}")

  def write_to_cube_file(self, dst):
    """Writes lut_value to a file.

    Args:
      dst: a text file path (.cube).

    Returns:
      True if succeeds. Otherwise False will be returned.
    """

    outfile = os.path.abspath(dst)
    try:
      out_fc = open(outfile, "w")
    except ValueError:
      print(
          f"Error: failed to open {outfile}\n Error message:"
          f" {ValueError.message}"
      )
      return False

    out_fc.write(f"LUT_3D_SIZE {self.lut_size}\n")
    for b_major_index in range(0, len(self.lut_value)):
      i = self.shuffle_indices(b_major_index)
      out_fc.write(
          "{0:.7f} {1:.7f} {2:.7f}\n".format(
              self.lut_value[i][0],
              self.lut_value[i][1],
              self.lut_value[i][2],
          )
      )
    out_fc.close()
    print(f"lut3d saved in file: {outfile}")
    return True


def prmr_box(connection_uuid):
  """Creates a Production Metadata Reference (prmr) box.

  Args:
    connection_uuid: it is used to look up for production metadata found
      elsewhere in the TrackBox.

  Returns:
    A mpeg Box for Production Metadata Reference
  """

  assert len(connection_uuid) == 16
  prmr_leaf = mpeg.Box()
  prmr_leaf.name = mpeg.constants.TAG_PRMR
  prmr_leaf.header_size = 8
  prmr_leaf.contents = struct.pack(">I", 0) + connection_uuid
  prmr_leaf.content_size = len(prmr_leaf.contents)
  return prmr_leaf


def prmd_box(lut3d):
  """Creates a Production Metadata (prmd) box.

  Args:
    lut3d: a Lut3d object.

  Returns:
    an mpeg box containing Production Metadata (containing lut3d).
  """

  prmd_leaf = mpeg.Box()
  prmd_leaf.name = mpeg.constants.TAG_PRMD
  prmd_leaf.header_size = 8
  prmd_leaf.contents = lut3d.create_prmd_contents().getvalue()
  prmd_leaf.content_size = len(prmd_leaf.contents)
  return prmd_leaf


def udta_box(lut3d):
  """Constructs a user data box container which contains a production metadata box (prmd).

  Args:
    lut3d: a Lut3d object to be added to the user data.

  Returns:
    an mpeg box containing user data (lut3d).
  """
  udta_container = mpeg.Container()
  udta_container.name = mpeg.constants.TAG_UDTA
  udta_container.header_size = 8
  udta_container.add(prmd_box(lut3d))
  udta_container.content_size = len(udta_container.contents)

  return udta_container


def mpeg4_add_lut3d(mpeg4_file, in_fh, lut3d):
  """Adds a lut3d metadata to an mpeg4 file for all video tracks.

  For every video track, creates and adds a Production Metadata box (pmrd)
  containing the lut3d metadata the user data box (udta) of the track. It also
  crates and adds a corresponding Production Metadata Reference box (prmr) to
  the visual sample entry box.

  Args:
    mpeg4_file: mpeg4 file structure to add lut3d.
    in_fh: file handle to read uncached file contents.
    lut3d: a Lut3d object to be added to the mpeg4 file.

  Returns:
    True if succeeds. Otherwise False will be returned.
  """
  injected = False
  for element in mpeg4_file.moov_box.contents:
    if element.name == mpeg.constants.TAG_TRAK:
      added = False
      for sub_element in element.contents:
        if sub_element.name != mpeg.constants.TAG_MDIA:
          continue
        for mdia_sub_element in sub_element.contents:
          if mdia_sub_element.name != mpeg.constants.TAG_HDLR:
            continue
          position = mdia_sub_element.content_start() + 8
          in_fh.seek(position)
          if in_fh.read(4) == mpeg.constants.TRAK_TYPE_VIDE:
            added = True
            break
        if added:
          for mdia_sub_element in sub_element.contents:
            if mdia_sub_element.name != mpeg.constants.TAG_MINF:
              continue
            for minf_sub_element in mdia_sub_element.contents:
              if minf_sub_element.name != mpeg.constants.TAG_STBL:
                continue
              for stbl_sub_element in minf_sub_element.contents:
                if stbl_sub_element.name != mpeg.constants.TAG_STSD:
                  continue
                for stsd_sub_element in stbl_sub_element.contents:
                  if (
                      stsd_sub_element.name
                      in mpeg.constants.VISUAL_SAMPLE_ENTRY_TYPES
                  ):
                    stsd_sub_element.remove(mpeg.constants.TAG_PRMR)
                    stsd_sub_element.add(prmr_box(lut3d.connection_uuid))
                    print("Successfully added prmr box to Visual Sample Entry.")

      if added:
        add_udta = True
        for sub_element in element.contents:
          if sub_element.name == mpeg.constants.TAG_UDTA:
            add_udta = False
            sub_element.remove(mpeg.constants.TAG_PRMD)
            sub_element.add(prmd_box(lut3d))
            print("Successfully added lut3d to prmd box.")
        if add_udta:
          element.add(udta_box(lut3d))
          print("Successfully added udta box.")
        injected = True

  mpeg4_file.resize()
  return injected


def inject_lut3d_mpeg4(input_file, output_file, lut3d):
  """Injects a lut3d metadata to an mpeg4 file.

  Args:
    input_file: the path of the mpeg4 file to add lut3d
    output_file: the file path to save the input mpeg4 file with lut3d added.
    lut3d: a Lut3d object.

  Returns:
    True if succeeds. Otherwise False will be returned.
  """

  infile = os.path.abspath(input_file)
  outfile = os.path.abspath(output_file)

  if infile == outfile:
    print("Error: Input and output cannot be the same")
    return False

  try:
    in_fh = open(infile, "rb")
  except IOError:
    print(f"Error: {infile} does not exist or we do not have permission.")
    return False

  print(f"Processing: {infile}")

  extension = os.path.splitext(infile)[1].lower()

  if extension not in MPEG_FILE_EXTENSIONS:
    print("Error: Unknown file type")
    return False
  with open(infile, "rb") as in_fh:
    mpeg4_file = mpeg.load(in_fh)
    if mpeg4_file is None:
      print("Error: file could not be opened.")
      return False

    if not mpeg4_add_lut3d(mpeg4_file, in_fh, lut3d):
      print("Error failed to insert lut3d data")
      return False

    with open(outfile, "wb") as out_fh:
      mpeg4_file.save(in_fh, out_fh)
    print(f"Injected the lut3d to file: {outfile}")
    return True

  return inject_lut3d_mpeg4(infile, outfile, lut3d)


def parse_lut3d_mpeg4(input_file):
  """Parses a lut3d metadata from an mpeg4 file.

    It looks for a Production Metadata box (pmrd) in video tracks, parses the
    lut3d in the one found first and return the lut3d.

  Args:
    input_file: the path of the mpeg4 file from which to parse lut3d.

  Returns:
    the parsed lut3d in a Lut3d object or None if not found.
  """

  infile = os.path.abspath(input_file)
  try:
    in_fh = open(infile, "rb")
    in_fh.close()
  except IOError:
    print(
        f"Error: {infile} does not exist or we do not have permission. Error:"
        f" {Error.mro()}"
    )
    return None

  print(f"Parsing: {infile}")

  extension = os.path.splitext(infile)[1].lower()

  if extension not in MPEG_FILE_EXTENSIONS:
    print("Error: Unknown file type")
    return None
  with open(input_file, "rb") as in_fh:
    mpeg4_file = mpeg.load(in_fh)
    if mpeg4_file is None:
      print("Error: file could not be opened.")
      return None
    ref_uuid = []
    for element in mpeg4_file.moov_box.contents:
      if element.name == mpeg.constants.TAG_TRAK:
        parse = False
        for sub_element in element.contents:
          if sub_element.name != mpeg.constants.TAG_MDIA:
            continue
          for mdia_sub_element in sub_element.contents:
            if mdia_sub_element.name != mpeg.constants.TAG_HDLR:
              continue
            position = mdia_sub_element.content_start() + 8
            in_fh.seek(position)
            if in_fh.read(4) == mpeg.constants.TRAK_TYPE_VIDE:
              parse = True
              break
          if parse:
            for mdia_sub_element in sub_element.contents:
              if mdia_sub_element.name != mpeg.constants.TAG_MINF:
                continue
              for minf_sub_element in mdia_sub_element.contents:
                if minf_sub_element.name != mpeg.constants.TAG_STBL:
                  continue
                for stbl_sub_element in minf_sub_element.contents:
                  if stbl_sub_element.name != mpeg.constants.TAG_STSD:
                    continue
                  for stsd_sub_element in stbl_sub_element.contents:
                    if (
                        stsd_sub_element.name
                        in mpeg.constants.VISUAL_SAMPLE_ENTRY_TYPES
                    ):
                      for vse_sub_element in stsd_sub_element.contents:
                        if vse_sub_element.name == mpeg.constants.TAG_PRMR:
                          position = vse_sub_element.content_start()
                          if vse_sub_element.content_size != 20:
                            print(f"prmr box is incorrect size {vse_sub_element.content_size} != 20")
                          else:
                            in_fh.seek(position + 4)  # Seek past version and flags
                            ref_uuid.append(
                                in_fh.read(vse_sub_element.content_size - 4)
                            )
        if parse:
          for sub_element in element.contents:
            if sub_element.name == mpeg.constants.TAG_UDTA:
              for udta_sub_element in sub_element.contents:
                if udta_sub_element.name == mpeg.constants.TAG_PRMD:
                  lut3d = Lut3d()
                  position = udta_sub_element.content_start()
                  in_fh.seek(position)
                  if not lut3d.read_from_prmd_contents(
                      in_fh.read(udta_sub_element.content_size)
                  ):
                    return None
                  if lut3d.connection_uuid not in ref_uuid:
                    print(
                        "Warning: No ref UUID was matched for the parsed lut3d!"
                    )
                  return lut3d
  return None
