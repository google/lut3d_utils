# Tone Map Metadata (3D Look-Up-Table) Injector

A tool for manipulating
[production metadata](../docs/Static-Colour-Mapping-Metadata-lut3d-rfc.md),
specifically tone map metadata (3D LUT), in MP4 and MOV files. It can be used to
inject 3D LUT metadata into a file or validate metadata in an existing file.

## Usage

[Python 3.11](https://www.python.org/downloads/) must be used to run the tool.
From within the directory above `lut3d_utils`:

#### Help

```
python lut3d_utils -h
```

Prints help and usage information.

#### Inject

```
python lut3d_utils -inject_lut3d -i ${input_file} -o ${output_file} -l ${lut3d_file} -p COLOUR_PRIMARIES_BT709 -t COLOUR_TRANSFER_CHARACTERISTICS_GAMMA22
```

Loads a tone mapping (3D LUT) metadata from `lut3d_file` and inject it to
`input_file`(.mov or .mp4). The specified `output_colour_primaries` and
`output_colour_transfer_characteristics` are injected too. It saves the result
to `output_file`. \
`input_file` and `output_file` must not be the same file.

#### Examine

```
python lut3d_utils -retrieve_lut3d -i ${input} -l ${lut3d_file}
```

Checks if `input_file` contains 3D LUT metadata. If so, parses the metadata and
prints it out. In addition, it saves the 3D LUT entries to `lut3d_file` as a
".cube" file.
