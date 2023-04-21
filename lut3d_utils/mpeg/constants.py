#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2023 Google LLC All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""MPEG-4 constants."""

from enum import Enum


class ColourPrimaries(Enum):
  """

  """
  # Also ITU-R BT1361 / IEC 61966-2-4 / SMPTE RP177 Annex B.
  COLOUR_PRIMARIES_BT709 = 1
  COLOUR_PRIMARIES_UNSPECIFIED = 2
  COLOUR_PRIMARIES_BT470M = 4
  # Also ITU-R BT601-6 625 / ITU-R BT1358 625 / ITU-R BT1700 625 PAL & SECAM.
  COLOUR_PRIMARIES_BT470BG = 5
  # Also ITU-R BT601-6 525 / ITU-R BT1358 525 / ITU-R BT1700 NTSC.
  COLOUR_PRIMARIES_SMPTE170M = 6
  # Functionally identical to above.
  COLOUR_PRIMARIES_SMPTE240M = 7
  # Colour filters using Illuminant C.
  COLOUR_PRIMARIES_FILM = 8
  # ITU-R BT2020.
  COLOUR_PRIMARIES_BT2020 = 9
  # SMPTE ST428-1.
  COLOUR_PRIMARIES_SMPTEST428_1 = 10
  # SMPTE ST431-2
  COLOUR_PRIMARIES_SMPTE431 = 11
  # SMPTE ST432-1
  COLOUR_PRIMARIES_SMPTE432 = 12
  # JEDEC P22 phosphors
  COLOUR_PRIMARIES_JEDEC_P22 = 22


class ColourTransferCharacteristics(Enum):
  """

  """
  COLOUR_TRANSFER_CHARACTERISTICS_BT709 = 1
  COLOUR_TRANSFER_CHARACTERISTICS_UNSPECIFIED = 2
  # Also ITU-R BT470M / ITU-R BT1700 625 PAL & SECAM.
  COLOUR_TRANSFER_CHARACTERISTICS_GAMMA22 = 4
  # Also ITU-R BT470BG.
  COLOUR_TRANSFER_CHARACTERISTICS_GAMMA28 = 5
  # Also ITU-R BT601-6 525 or 625 / ITU-R BT1358 525 or 625 / ITU-R
  #   BT1700 NTSC.
  COLOUR_TRANSFER_CHARACTERISTICS_SMPTE170M = 6
  COLOUR_TRANSFER_CHARACTERISTICS_SMPTE240M = 7
  # Linear transfer characteristics.
  COLOUR_TRANSFER_CHARACTERISTICS_LINEAR = 8
  # Logarithmic transfer characteristic (100:1 range).
  COLOUR_TRANSFER_CHARACTERISTICS_LOG = 9
  # Logarithmic transfer characteristic (100 * Sqrt(10) : 1 range).
  COLOUR_TRANSFER_CHARACTERISTICS_LOG_SQRT = 10
  # IEC 61966-2-4.
  COLOUR_TRANSFER_CHARACTERISTICS_IEC61966_2_4 = 11
  # ITU-R BT1361 Extended Colour Gamut.
  COLOUR_TRANSFER_CHARACTERISTICS_BT1361_ECG = 12
  # IEC 61966-2-1 (sRGB or sYCC).
  COLOUR_TRANSFER_CHARACTERISTICS_IEC61966_2_1 = 13
  # ITU-R BT2020 for 10 bit system.
  COLOUR_TRANSFER_CHARACTERISTICS_BT2020_10 = 14
  # ITU-R BT2020 for 12 bit system.
  COLOUR_TRANSFER_CHARACTERISTICS_BT2020_12 = 15
  # SMPTE ST 2084 for 10, 12, 14 and 16 bit systems.
  COLOUR_TRANSFER_CHARACTERISTICS_SMPTEST2084 = 16
  # SMPTE ST 428-1.
  COLOUR_TRANSFER_CHARACTERISTICS_SMPTEST428_1 = 17
  # ARIB STD-B67, known as "Hybrid log-gamma".
  COLOUR_TRANSFER_CHARACTERISTICS_ARIB_STD_B67 = 18

TRAK_TYPE_VIDE = b"vide"

# Leaf types.
TAG_STCO = b"stco"
TAG_CO64 = b"co64"
TAG_FREE = b"free"
TAG_MDAT = b"mdat"
TAG_XML = b"xml "
TAG_HDLR = b"hdlr"
TAG_FTYP = b"ftyp"
TAG_ESDS = b"esds"
TAG_SOUN = b"soun"
TAG_SA3D = b"SA3D"
TAG_PRMD = b"prmd"
TAG_PRMR = b"prmr"

# Container types.
TAG_MOOV = b"moov"
TAG_UDTA = b"udta"
TAG_META = b"meta"
TAG_TRAK = b"trak"
TAG_MDIA = b"mdia"
TAG_MINF = b"minf"
TAG_STBL = b"stbl"
TAG_STSD = b"stsd"
TAG_UUID = b"uuid"
TAG_WAVE = b"wave"

# Visual sample entry types.
TAG_AVC1 = b"avc1"
TAG_MP4V = b"mp4v"
TAG_ENCV = b"encv"
TAG_S263 = b"s263"
TAG_VP09 = b"vp09"
TAG_AV01 = b"av01"
TAG_HEV1 = b"hev1"
TAG_DVH1 = b"dvh1"

# Sound sample descriptions.
TAG_NONE = b"NONE"
TAG_RAW_ = b"raw "
TAG_TWOS = b"twos"
TAG_SOWT = b"sowt"
TAG_FL32 = b"fl32"
TAG_FL64 = b"fl64"
TAG_IN24 = b"in24"
TAG_IN32 = b"in32"
TAG_ULAW = b"ulaw"
TAG_ALAW = b"alaw"
TAG_LPCM = b"lpcm"
TAG_MP4A = b"mp4a"
TAG_OPUS = b"Opus"

SOUND_SAMPLE_DESCRIPTIONS = frozenset([
    TAG_NONE,
    TAG_RAW_,
    TAG_TWOS,
    TAG_SOWT,
    TAG_FL32,
    TAG_FL64,
    TAG_IN24,
    TAG_IN32,
    TAG_ULAW,
    TAG_ALAW,
    TAG_LPCM,
    TAG_MP4A,
    TAG_OPUS,
    ])

VISUAL_SAMPLE_ENTRY_TYPES = frozenset([
    TAG_AVC1,
    TAG_MP4V,
    TAG_ENCV,
    TAG_S263,
    TAG_VP09,
    TAG_AV01,
    TAG_HEV1,
    TAG_DVH1
    ])

CONTAINERS_LIST = frozenset([
    TAG_MDIA,
    TAG_MINF,
    TAG_MOOV,
    TAG_STBL,
    TAG_STSD,
    TAG_TRAK,
    TAG_UDTA,
    TAG_WAVE,
    ]).union(SOUND_SAMPLE_DESCRIPTIONS).union(VISUAL_SAMPLE_ENTRY_TYPES)

