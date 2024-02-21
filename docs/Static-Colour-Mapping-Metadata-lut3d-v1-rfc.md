# Static Colour Mapping Metadata (3D Look-Up-Table) Version 1 RFC
*This document describes a revised open metadata scheme by which MP4 (ISOBMFF) multimedia containers may accommodate colour tone mapping metadata (as production metadata) to map from an input R’G’B’ colour space to an output R’G’B’ colour space, including HDR to SDR video conversion. Comments are welcome by
filing an issue on GitHub.*

------------------------------------------------------

## Production Metadata in MP4 (ISOBMFF)
Production metadata is the information that may be used in a production process and is not required for playback or delivery.
The 3D Look-Up-Table (3D LUT) is a kind of production metadata that may be used in a production process to map between R’G’B’ colour spaces, including HDR to SDR video conversion.
Production metadata is stored in a new box, `prmd`, defined in this RFC, in
an MP4 (ISOBMFF) container. The metadata is applicable to individual video
tracks in the container. In order to allow the production metadata to be associated to a `VisualSampleEntry`,
the `prmr` box holds an identifier that is to be referred from the `VisualSampleEntry` to look up the
correspoding production metadata.

### Production Metadata Box (prmd)
#### Definition
BoxType:        	`prmd`  
Container:     	UserData Box (`udta`) of the corresponding Track Box (`trak`)  
Mandatory:   	No  
Quantity:        	Zero or more

Contains the production metadata which can be stored in an MP4 (ISOBMFF) container. The box is a child box of the track-level `UserDataBox` of the corresponding track.

Different types of production metadata can be defined in the `ProductionMetadataBox`. Two types of metadata (`lut3` and `l3ur`) are defined in the current version of this specification, specifically for the static tone mapping metadata (3D LUT). Such metadata types may be used for colour space conversion in a production process.


#### Syntax
```
aligned(8) class ProductionMetadataBox extends FullBox('prmd', 0, 0) {
  unsigned int(8) metadata_connection_uuid[16];
  unsigned int(32) production_metadata_type;
  if (production_metadata_type == 'lut3') {
    unsigned int(8) lut_size;
    unsigned int(8) output_colour_primaries;
    unsigned int(8) output_transfer_characteristics;
    unsigned int(16) lut_value[lut_size][lut_size][lut_size][3];
  } else if (production_metadata_type == 'l3ur') {
    utf8string lut3_uri;
  }
}
```

#### Semantics

- `metadata_connection_uuid` is a Universally Unique Identifiers (UUID) that is used to match with the same UUID held in a referent (e.g., `SampleEntryProductionMetadataReferenceBox`).
A value of 0 for all elements of `metadata_connection_uuid` is valid but should be considered a placeholder and treated as absent. It shouldn't be used for look up from a referent. The value of 0 can be replaced with a non-zero UUID once known.
- `production_metadata_type` is the type of contained production metadata that indicates different production metadata structures. Two types are defined in the above syntax. Unrecognized values of `production_metadata_type` shall be treated as the `ProductionMetadataBox` is absent.
-  `lut_size` is the size of the 1st, 2nd, and 3rd dimension of the 3D LUT (defined by `lut_value`). The size shall not be zero.
- `output_colour_primaries` specifies the output colour primaries associated with the output R’G’B’ of the LUT specifying the CIE 1931 xy chromaticity coordinates of the white point and the red, green, and blue primaries. The `output_colour_primaries` uses the code points defined for ColourPrimaries from [ITU-T H.273](https://www.itu.int/rec/T-REC-H.273).
- `output_transfer_characteristics` specifies the output transfer characteristics associated with the output R’G’B’ of the LUT specifying the nonlinear transfer function characteristics used to translate between RGB colour space values and Y´CbCr values. The `output_transfer_characteristics` uses the code points defined for TransferCharacteristics from [ITU-T H.273](https://www.itu.int/rec/T-REC-H.273).
- `lut_value` contains the static 3D look-up-table (LUT) for colour mapping. The LUT maps an input R'G'B' colour to an output R′G′B′ colour (big-endian). For YCbCr input video, the input R'G'B' obtained by applying the MatrixCoefficients associated to the input video stream.
The `lut_value` shall contain the table entries for the LUT from the minimum to the maximum input values, with the third component index changing fastest (i.e. `lut_value[r_i][g_i][b_i][c_i] = data[(r_i * n * n + g_i * n + b_i) * 3 + c_i]`). The 3D LUT has dimensions lut_size-by-lut_size-by-lut_size-by-3.  
To look up an input RGB (a vector with 3 elements in [0, 1]), which must be in full range, a conversion step could be needed to convert from the coded video format to RGB, subsequently RGB will be mapped to `[0, lut_size - 1]` (simply by multiplying RGB values by `lut_size - 1`) to find the entries. Since the mapped RGB (which is assumed to be in full range) is not always on a lattice point, the output values shall be interpolated, preferably using tetrahedral interpolation, as detailed in [Specification S-2014-006 Common LUT Format (CLF)](https://community.acescentral.com/uploads/short-url/iHX8xsDczlEg7l7OtIbJrbPvm4C.pdf)- Appendix B. To generate a 3D LUT, one way is to follow Section 5.2 of [Rep. ITU-R BT.2446-1](https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-BT.2446-1-2021-PDF-E.pdf).  
The `lut_value` is a 1.15 fixed-point value (16-bit fixed point number, of which 15 rightmost bits are fractional) in the range [0, 2.0) (Note: this representation allows for the lut_value representation to have headroom above 1.0 to avoid potential 1-crossing interpolation distortion issues).
- `lut3_uri` is a Universal Resource Identifier (URI) that refers to a 3D LUT with the following representation (same as `lut3`) in a binary file:
```
       struct LUT3 {
          unsigned int(8) lut_size;
          unsigned int(8) output_colour_primaries;
          unsigned int(8) output_transfer_characteristics;
          unsigned int(16) lut_value[lut_size][lut_size][lut_size][3];
        }
```
### Production Metadata Reference Box (prmr)
#### Definition
BoxType:        	`prmr`  
Container:     VisualSampleEntry (e.g. `avc1`, `hev1`)  
Mandatory:   	No  
Quantity:        	Zero or more

The`ProductionMetadataBox` should be accessible from the `VisualSampleEntry`. The new box `ProductionMetadataReferenceBox` holds an identifier used to look up production metadata associated with the particular `VisualSampleEntry`. This indirection allows the `VisualSampleEntry` to avoid containing potentially large production metadata and also to reference the same production metadata among multiple sample entries of the track.  
The `connection_uuid` holds a UUID that matches production metadata found elsewhere in the `TrackBox`.The production metadata associated with the `connection_uuid` shall be unique and the search for the match can end once a matching production metadata item is found.
#### Syntax
```
aligned(8) class VisualSampleEntryProductionMetadataReferenceBox extends FullBox('prmr', 0, 0) {
  	unsigned int(8) connection_uuid[16];
}
```
#### Semantics
- `connection_uuid` is the Universally Unique Identifiers (UUID) that refers to production metadata associated with the `VisualSampleEntry`. This UUID is used to look up production metadata found elsewhere in the `TrackBox`. The production metadata associated with the `connection_uuid` shall be unique and the search for the match can end once a matching production metadata item is found. If the `connection_uuid` cannot be resolved to production metadata, the reference shall be treated as absent. The algorithm used for UUID generation shall be privacy preserving.
The value of 0 for all elements of `connection_uuid` is a placeholder and valid which shall be treated as absent. This placeholder value can be replaced once a non-zero UUID is known.

### Example

Here is an example box hierarchy for a file containing the PRMR/PRMD metadata:

```
[moov: Movie Box]
  [trak: Video Track Box]
    [mdia: Media Box]
      [minf: Media Information Box]
        [stbl: Sample Table Box]
          [stsd: Sample Table Sample Descriptor]
            [avc1: Advance Video Coding Box]
              [avcC: AVC Configuration Box]
                ...
              [prmr: Production Metadata Reference Box]
                connection_uuid = 0xe6a100fc94a140668d34dd98d671bae8
                ...
     ...
    [udta: User Data Box]
      ...
      [prmd: Production Metadata Box]
        metadata_connection_uuid = 0xe6a100fc94a140668d34dd98d671bae8
  	    production_metadata_type = 'lut3'
        lut_size = 33
        output_colour_primaries = 1
        output_transfer_characteristics = 1
        lut_value = ...
      ...
    ... 
```

The associated input video track will have MatrixCoefficients and TransferCharacteristics
associated to it (via metadata in the elementary stream or metadata in a color parameter
atom, `colr`). The input video signal should be transformed to R'G'B' space by applying
the input matrix coefficients as defined in [ITU-T H.273](https://www.itu.int/rec/T-REC-H.273).
The LUT data in the `prmd` box defines the transfomration of this R'G'B' data to an output
space defined by `output_colour_primaries` and `output_transfer_characteristics`.
