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
"""Tone Map Metadata (3D Look-Up-Table) Injector.

Tool for examining and injecting tone mapping metadata in MP4/MOV files.
"""

import argparse
import os
import sys

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, "..")
sys.path.insert(0, path)

from lut3d_utils import lut3d_util
from lut3d_utils import mpeg


def main():
  """Main function for printing and injecting the tone mapping metadata (3D LUT)."""

  parser = argparse.ArgumentParser(
      usage=(
          "%(prog)s [options] \n\nIf inject_lut3d option is set, this tool"
          " loads a tone mapping (3D LUT) metadata from the lut3d file(.cube"
          " file) and inject to the input file (.mov or .mp4) if. The tool also"
          " takes the output colour primaries and the output colour transfer"
          " characteristics using the specified options. It finally saves the"
          " result to the output file. If retrieve_lut3d is set, this tool will"
          " parse the 3D LUT metadata from the input file and write it to the"
          " lut3d file(.cube file). \n\n Typical usage example to inject the"
          " lut3d:\n   python lut3d_utils -inject_lut3d -i ${input_file} -o"
          " ${output_file} -l ${lut3d_file} -p COLOUR_PRIMARIES_BT709 -t"
          " COLOUR_TRANSFER_CHARACTERISTICS_GAMMA22\n\n The following command"
          " parses and prints lut3d from input_file and writes its entries to"
          " lut3d_file:\n   python lut3d_utils -retrieve_lut3d -i ${input_file}"
          " -l ${lut3d_file}"
      )
  )
  parser.add_argument(
      "-inject_lut3d",
      "--inject_lut3d",
      action="store_true",
      help="Inject the tone mapping metadata (3D LUT) file if it's true.",
  )
  parser.add_argument(
      "-retrieve_lut3d",
      "--retrieve_lut3d",
      action="store_true",
      help=(
          "Retrieve the tone mapping metadata (3D LUT) from the input file if"
          " it's true."
      ),
  )
  parser.add_argument(
      "-l",
      "--lut3d_file",
      nargs="?",
      help="The tone mapping metadata (3D LUT) file",
  )
  parser.add_argument(
      "-i", "--input_file", nargs="?", required=True, help="The input file"
  )
  parser.add_argument("-o", "--output_file", nargs="?", help="The output file")
  parser.add_argument(
      "-p",
      "--output_colour_primaries",
      nargs="?",
      default="COLOUR_PRIMARIES_BT709",
      help="The output colour primaries",
  )
  parser.add_argument(
      "-t",
      "--output_colour_transfer_characteristics",
      nargs="?",
      default="COLOUR_TRANSFER_CHARACTERISTICS_BT709",
      help="The output colour transfer characteristics function",
  )

  args = parser.parse_args()
  if (
      args.inject_lut3d is not None
      and args.inject_lut3d
      and args.retrieve_lut3d is not None
      and args.retrieve_lut3d
  ):
    print("Error: either inject_lut3d or retrieve_lut3d must be set.")
    return

  if args.retrieve_lut3d is not None and args.retrieve_lut3d:
    lut3d = lut3d_util.parse_lut3d_mpeg4(args.input_file)
    if not lut3d:
      print("Not found lut3d metadata in file: " + args.input_file)
      return
    print(f"{args.input_file} contains a valid lut3d:")
    lut3d.print()
    if args.lut3d_file:
      lut3d.write_to_cube_file(args.lut3d_file)
    return
  if args.inject_lut3d is None or not args.inject_lut3d:
    print("Error: either inject_lut3d or retrieve_lut3d must be set.")
    return

  if args.output_file is None:
    print("No output file to save the result!")
    return
  lut3d = lut3d_util.Lut3d(
      output_colour_primaries=mpeg.constants.ColourPrimaries[
          args.output_colour_primaries
      ],
      output_colour_transfer_characteristics=mpeg.constants.ColourTransferCharacteristics[
          args.output_colour_transfer_characteristics
      ],
  )
  if not lut3d.read_from_cube_file(args.lut3d_file):
    print("Unable to read lut3d from the file.")
    return
  if not lut3d_util.inject_lut3d_mpeg4(
      args.input_file, args.output_file, lut3d
  ):
    print("Failed to inject the lut3d!")
    return

  return


if __name__ == "__main__":
  main()
