GEOPHYSICS MAPPING PLUGIN G&R DIVISION
=====================================

OVERVIEW
--------
This QGIS plugin automates the map making workflow for geophysical surveys. It creates standardized map layouts from templates using GeoTIFF raster files and automatically extracts map information from filenames.

FEATURES
--------
- Creates map layouts from QGIS template files (.qpt)
- Automatically loads and styles GeoTIFF raster files
- Extracts map titles, descriptions, and units from filenames
- Applies white background transparency to rasters
- Manages layer visibility (hides non-essential layers)
- Supports legend image integration
- Duplicates layouts for batch processing

WORKFLOW
--------
1. Select a QGIS layout template (.qpt file)
2. Choose a GeoTIFF raster file
3. Optionally select a legend image
4. Click "Create" to generate the map layout
5. The layout opens automatically in QGIS Layout Designer

FILE NAMING CONVENTIONS
-----------------------
The plugin recognizes specific filename patterns to automatically populate map information:

MAGNETIC SURVEYS:
- TotalFieldMagnetics → "Total Magnetic Intensity" (nT)
- TotalFieldMagneticsRTP → "TMI Reduced to Pole" (nT)
- TotalFieldMagneticsRTPAS → "Analytical Signal" (nT/m)
- TotalFieldMagneticsRTPHDTDR → "Horizontal Derivative of the Tilt" (rad/m)
- TotalFieldMagneticsRTPRMI → "Residual Magnetic Intensity" (nT)
- TotalFieldMagneticsRTPTDR → "Tilt Derivative" (rad)
- TotalFieldMagneticsRTPTHDR → "Total Horizontal Gradient" (nT/m)
- TotalFieldMagneticsRTPVD1 → "First Vertical Derivative" (nT/m)
- TotalFieldMagneticsRTPresidual[depth]m → "Residual Filtered - [depth] m" (nT)
- TotalFieldMagneticsRTPregional[depth]m → "Regional Filtered - [depth] m" (nT)

ELECTROMAGNETIC SURVEYS:
- dBdtZch10 → "dB/dt z component 0.014 ms after turnoff" (pV/(Am^4))
- ConductivityDepthSlice[depth]m → "Conductivity Depth Slice [depth] m" (S/m)
- SusceptibilityDepthSlice[depth]m → "Susceptibility Depth Slice [depth] m" (SI)

OTHER DATA:
- SensorAltitude → "Sensor Altitude" (m)
- DigitalTerrainModel → "Digital Terrain Model" (m)
- FlightPath → "Flight Path" (no legend)

FILENAME EXAMPLES:
- "Survey_Area_TotalFieldMagnetics.tif" → Title: "Survey_Area", Type: "Total Magnetic Intensity"
- "WGS84 Site_A_ConductivityDepthSlice50m.tif" → Title: "Site_A", Type: "Conductivity Depth Slice 50 m"
- "NAD83 Project_dBdtZch10.tif" → Title: "Project", Type: "dB/dt z component 0.014 ms after turnoff"

TECHNICAL NOTES
---------------
- Supports WGS84 and NAD83 coordinate system prefixes
- Automatically searches for legend files in "LEGENDS" folder
- Preserves essential layers (satellite imagery, property boundaries)
- Client location defaults to "Axiom Exploration, Rio de Janeiro, Brazil"
- Template must contain specific item IDs: "SatMap", "Title", "Client-Location", "Map Description", "Legend Unit", "Legend (Oasis)"

REQUIREMENTS
------------
- QGIS 3.x
- Template file (.qpt format)
- GeoTIFF raster files
- Optional legend images (PNG, JPG, SVG, PDF)

AUTHOR
------
Igor Macedo (imacedo@axiomex.com)
Axiom Exploration
Generated: August 22, 2025