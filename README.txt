GEOPHYSICS MAPPING PLUGIN – G&R DIVISION
OVERVIEW

The Geophysics Mapping plugin automates map generation for geophysical survey data within QGIS.
It creates standardized and editable map layouts from template files, automatically loads GeoTIFF rasters, applies consistent styling, extracts map metadata from filenames, and maintains layout modifications across sessions.

FEATURES
- Creates QGIS map layouts from template files (.qpt)
- Automatically loads and styles GeoTIFF raster files
- Extracts map titles, descriptions, and units from filenames
- Applies QML styles from the "templates" folder:
	- transparency_style.qml for most rasters
	- flightpath_style.qml for Flight Path rasters
- Manages layer visibility (keeps only relevant layers visible)
- Integrates legend images automatically
- Saves and reuses an active layout template (Geophysics_SurveyMaps_Active.qpt) so user-made layout modifications persist between map creations
- Opens each new layout automatically in a new Layout Designer window
- Allows setting the Client-Location directly from the plugin interface (ClientLocationLayoutTextEdit)
- First generated map automatically zooms to the GeoTIFF’s extent and location

WORKFLOW
1. Select a QGIS layout template (.qpt file)
2. Choose a GeoTIFF raster file
3. Optionally select a legend image
4. Enter the Client and Location text
5. Click "Create" to generate the map layout
6. The layout automatically opens in QGIS Layout Designer
7. Any manual edits you make (e.g., scalebar, text, symbols) are automatically preserved — the plugin saves them into Geophysics_SurveyMaps_Active.qpt for reuse in the next map

FILE NAMING CONVENTIONS
- The plugin recognizes keywords and patterns in filenames to populate map metadata automatically.

MAGNETIC SURVEYS
	TMI → Total Magnetic Intensity (nT)
	TMI_RTP → Reduced to Pole TMI (nT)
	TMI_AS → Analytical Signal (nT/m)
	TMI_RTP_HD_TDR → Horizontal Derivative of the Tilt (rad/m)
	TMI_RTP_RMI → Residual Magnetic Intensity (nT)
	TMI_RTP_TDR → Tilt Derivative (rad)
	TMI_RTP_THDR → Total Horizontal Gradient (nT/m)
	TMI_RTP_VD1 → First Vertical Derivative (nT/m)
	TMI_RTP_residual[depth]m → Residual Filtered - [depth] m (nT)
	TMI_RTP_regional[depth]m → Regional Filtered - [depth] m (nT)
	AGL → Sensor Altitude (m)
	DTM → Digital Terrain Model (m)

ELECTROMAGNETIC SURVEYS
	dBdtZch10 - dBdtZch45. → dB/dt z component (n ms after turnoff) (pV/(Am⁴))
	Conductivity [depth]m → Conductivity Depth Slice (mS/m)
	Susceptibility [depth]m → Susceptibility Depth Slice (SI)

RADIOMETRIC SURVEYS
	Th-K_Ratio → Thorium / Potassium Ratio (Th / K Ratio) 
	U-K_Ratio → Uranium / Potassium Ratio (U / K Ratio) 
	U-Th_Ratio → Uranium / Thorium Ratio (U / Th Ratio)
	Ternary → Radiometric Ternary Image
	Total_NASVD → Radiometric Total Count
	Th_NASVD → Thorium NASVD Processed
	U_NASVD → Uranium NASVD Processed
	K_NASVD → Potassium NASVD Processed

OTHER DATA
	FlightPath → Flight Path (no legend)

FILENAME EXAMPLES
	Survey_Area_TMI.tif → Title: Survey_Area, Map Description: Total Magnetic Intensity (nT)
	WGS84_Project Name_Conductivity50m.tif → Title: Project Name, Map Description: Conductivity Depth Slice 50 m (mS/m)
	NAD83_Project_dBdtZch15.tif → Title: Project, Type: dB/dt z component 0.045 ms after turnoff (pV/(Am⁴))

TECHNICAL NOTES
- Supports WGS84 and NAD83 filename prefixes
- Automatically searches for legend files in "LEGENDS" folder located beside the GeoTIFF
- Preserves visibility of essential base layers:
	- Esri World Imagery (Clarity) Beta
	- Google Satellite Hybrid
	- property AOI

Client-Location text is entered through the plugin UI
Default layout template: Geophysics_SurveyMaps.qpt
Active editable template: Geophysics_SurveyMaps_Active.qpt


REQUIREMENTS
- QGIS 3.34 or newer
- Template file (.qpt format)
- GeoTIFF raster files
- Optional legend images (.png, .jpg, .svg, .pdf)

RECENT UPDATES (v3.0.0)
- Added persistent layout saving via Geophysics_SurveyMaps_Active.qpt to preserve user modifications
- First map creation now automatically zooms to GeoTIFF extent
- Added conditional styling:
	- flightpath_style.qml → for Flight Path rasters
	- transparency_style.qml → for all other rasters

- Client-Location field now populated from the plugin UI instead of a constant (on script)
- Each new map automatically opens in a new Layout Designer window
- Fixed plugin icon path to correctly load from icon.png in the plugin directory


AUTHOR
------
Igor Macedo (imacedo@axiomex.com)
Axiom Exploration
Generated: August 22, 2025
Last Updated: October 29, 2025
