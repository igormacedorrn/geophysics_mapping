from qgis.core import (
    QgsPrintLayout,
    QgsLayoutItemMap,
    QgsLayoutItemScaleBar,
    QgsLayoutItemLabel,
    QgsLayoutItemPicture,
    QgsProject,
    QgsReadWriteContext,
)
from qgis.PyQt.QtXml import QDomDocument
import re
import os


# Default client information
DEFAULT_CLIENT_LOCATION = "Axiom Exploration\nRio de Janeiro, Brazil"

# Description lookup dictionary for map types
DESCRIPTION_LOOKUP = {
    "Sensor Altitude": (
        "Sensor Altitude",
        "Sensor Altitude (m)",
        "SensorAltitude.png",
    ),
    "ConductivityDepthSlice25m": (
        "Conductivity Depth Slice - 25m",
        "Conductivity (S/m)",
        "Conductivity 25m.png",
    ),
    "dBdtZch10": (
        "dB/dt z component 0.014 ms after turnoff",
        "dB/dt z component: channel 10 (pV/(Am^4))",
        "dBdt Z ch10.png",
    ),
    "dBdtZch15": (
        "dB/dt z component 0.045 ms after turnoff",
        "dB/dt z component: channel 15 (pV/(Am^4))",
        "dBdtZch15.png",
    ),
    "dBdtZch20": (
        "dB/dt z component 0.12 ms after turnoff",
        "dB/dt z component: channel 20 (pV/(Am^4))",
        "dBdtZch20.png",
    ),
    "dBdtZch25": (
        "dB/dt z component 0.26 ms after turnoff",
        "dB/dt z component: channel 25 (pV/(Am^4))",
        "dBdtZch25.png",
    ),
    "dBdtZch30": (
        "dB/dt z component 0.56 ms after turnoff",
        "dB/dt z component: channel 30 (pV/(Am^4))",
        "dBdtZch30.png",
    ),
    "dBdtZch35": (
        "dB/dt z component 1.16 ms after turnoff",
        "dB/dt z component: channel 35 (pV/(Am^4))",
        "dBdtZch35.png",
    ),
    "dBdtZch40": (
        "dB/dt z component 2.36 ms after turnoff",
        "dB/dt z component: channel 40 (pV/(Am^4))",
        "dBdtZch40.png",
    ),
    "dBdtZch45": (
        "dB/dt z component 4.74 ms after turnoff",
        "dB/dt z component: channel 45 (pV/(Am^4))",
        "dBdtZch45.png",
    ),
    "DigitalTerrainModel": (
        "Digital Terrain Model",
        "Digital Terrain Model (m)",
        "DigitalTerrainModel.png",
    ),
    "FlightPath": (
        "Flight Path",
        "",
        "",
    ),
    "SusceptibilityDepthSlice25m": (
        "Susceptibility Depth Slice - 25m",
        "Relative Susceptibility (SI)",
        "Susceptibility 25m.png",
    ),
    "TotalFieldMagnetics": (
        "Total Magnetic Intensity",
        "Total Magnetic Intensity (nT)",
        "Total Field Magnetics.png",
    ),
    "TotalFieldMagneticsRTP": (
        "TMI Reduced to Pole",
        "Total Magnetic Intensity Reduced to Pole (nT)",
        "Total Field Magnetics RTP.png",
    ),
    "TotalFieldMagneticsRTPAS": (
        "Analytical Signal",
        "Analytical Signal (nT/m)",
        "Total Field MagneticsRTPAS.png",
    ),
    "TotalFieldMagneticsRTPHDTDR": (
        "Horizontal Derivative of the Tilt",
        "Tilt Horizontal Derivative : TMI Reduced to Pole (rad/m)",
        "TotalFieldMagneticsRTPHDTDR.png",
    ),
    "TotalFieldMagneticsRTPregional1500m": (
        "Regional Filtered - 1500 m",
        "Regional Filtered: TMI Reduced to Pole (nT)",
        "TotalFieldMagneticsRTPRegional1500m.png",
    ),
    "TotalFieldMagneticsRTPRMI": (
        "Residual Magnetic Intensity",
        "IGRF corrected TMI (nT)",
        "TotalFieldMagneticsRTPRMI.png",
    ),
    "TotalFieldMagneticsRTPresidual1500m": (
        "Residual Filtered - 1500 m",
        "Residual Filtered: TMI Reduced to Pole (nT)",
        "TotalFieldMagneticsRTPresidual1500m.png",
    ),
    "TotalFieldMagneticsRTPTDR": (
        "Tilt Derivative",
        "Tilt Derivative: TMI Reduced to Pole (rad)",
        "Total Field Magnetics RTP TDR.png",
    ),
    "TotalFieldMagneticsRTPTHDR": (
        "Total Horizontal Gradient",
        "Total Horizontal Gradient: TMI Reduced to Pole (nT/m)",
        "Total Field Magnetics RTP THDR.png",
    ),
    "TotalFieldMagneticsRTPVD1": (
        "First Vertical Derivative",
        "First Vertical Derivative: TMI Reduced to Pole (nT/m)",
        "TotalFieldMagneticsRTPVD1.png",
    ),
}
import os


class LayoutStateManager:
    """Manages layout state and persistence across multiple layout creations"""

    def __init__(self):
        self.initialized = False
        # Main map settings (SatMap)
        self.map_settings = {"scale": None, "extent": None, "rotation": None}
        # Inset map settings
        self.inset_map_settings = {"scale": None, "extent": None, "rotation": None}
        # Main scalebar settings
        self.scalebar_settings = {
            "style": None,
            "units": None,
            "segments": None,
            "height": None,
            "unit_label": None,
            "position": None,
            "alignment": None,
            "box_content_space": None,
            "units_per_segment": None,
            "fixed_width": None,
            "fixed_bar_width": None,
            "num_map_units_per_bar_unit": None,
        }
        # Inset scalebar settings
        self.inset_scalebar_settings = {
            "style": None,
            "units": None,
            "segments": None,
            "height": None,
            "unit_label": None,
            "position": None,
            "alignment": None,
            "box_content_space": None,
            "units_per_segment": None,
            "fixed_width": None,
            "fixed_bar_width": None,
            "num_map_units_per_bar_unit": None,
        }

    def capture_layout_state(self, layout):
        """Captures the current state of important layout items"""
        try:
            # Capture main map settings
            map_item = layout.itemById("SatMap")
            if isinstance(map_item, QgsLayoutItemMap):
                self.map_settings.update(
                    {
                        "scale": map_item.scale(),
                        "extent": map_item.extent(),
                        "rotation": map_item.mapRotation(),
                    }
                )
                print("Captured SatMap settings")

            # Capture inset map settings
            inset_map = layout.itemById("InsetMap")
            if isinstance(inset_map, QgsLayoutItemMap):
                self.inset_map_settings.update(
                    {
                        "scale": inset_map.scale(),
                        "extent": inset_map.extent(),
                        "rotation": inset_map.mapRotation(),
                    }
                )
                print("Captured InsetMap settings")

            # Capture main scalebar settings
            scalebar = layout.itemById("Scalebar")
            if isinstance(scalebar, QgsLayoutItemScaleBar):
                self.scalebar_settings.update(
                    {
                        "style": scalebar.style(),
                        "units": scalebar.units(),
                        "segments": scalebar.numberOfSegments(),
                        "height": scalebar.height(),
                        "unit_label": scalebar.unitLabel(),
                        "position": scalebar.positionWithUnits(),
                        "alignment": scalebar.alignment(),
                        "box_content_space": scalebar.boxContentSpace(),
                        "units_per_segment": scalebar.numUnitsPerSegment(),
                        "fixed_width": scalebar.fixedWidth(),
                        "fixed_bar_width": scalebar.fixedBarWidth(),
                        "num_map_units_per_bar_unit": scalebar.numMapUnitsPerScaleBarUnit(),
                    }
                )
                print("Captured Scalebar settings")

            # Capture inset scalebar settings
            inset_scalebar = layout.itemById("InsetScaleBar")
            if isinstance(inset_scalebar, QgsLayoutItemScaleBar):
                self.inset_scalebar_settings.update(
                    {
                        "style": inset_scalebar.style(),
                        "units": inset_scalebar.units(),
                        "segments": inset_scalebar.numberOfSegments(),
                        "height": inset_scalebar.height(),
                        "unit_label": inset_scalebar.unitLabel(),
                        "position": inset_scalebar.positionWithUnits(),
                        "alignment": inset_scalebar.alignment(),
                        "box_content_space": inset_scalebar.boxContentSpace(),
                        "units_per_segment": inset_scalebar.numUnitsPerSegment(),
                        "fixed_width": inset_scalebar.fixedWidth(),
                        "fixed_bar_width": inset_scalebar.fixedBarWidth(),
                        "num_map_units_per_bar_unit": inset_scalebar.numMapUnitsPerScaleBarUnit(),
                    }
                )
                print("Captured InsetScaleBar settings")

            self.initialized = True
            return True

        except Exception as e:
            print(f"Error capturing layout state: {str(e)}")
            return False

    def apply_layout_state(self, layout):
        """Applies the saved state to a new layout"""
        try:
            if not self.initialized:
                return False

            # Apply main map settings
            map_item = layout.itemById("SatMap")
            if isinstance(map_item, QgsLayoutItemMap):
                if self.map_settings["extent"]:
                    map_item.setExtent(self.map_settings["extent"])
                if self.map_settings["scale"]:
                    map_item.setScale(self.map_settings["scale"])
                if self.map_settings["rotation"] is not None:
                    map_item.setMapRotation(self.map_settings["rotation"])
                map_item.refresh()
                print("Applied SatMap settings")

            # Apply inset map settings
            inset_map = layout.itemById("InsetMap")
            if isinstance(inset_map, QgsLayoutItemMap):
                if self.inset_map_settings["extent"]:
                    inset_map.setExtent(self.inset_map_settings["extent"])
                if self.inset_map_settings["scale"]:
                    inset_map.setScale(self.inset_map_settings["scale"])
                if self.inset_map_settings["rotation"] is not None:
                    inset_map.setMapRotation(self.inset_map_settings["rotation"])
                inset_map.refresh()
                print("Applied InsetMap settings")

            # Apply main scalebar settings
            scalebar = layout.itemById("Scalebar")
            if isinstance(scalebar, QgsLayoutItemScaleBar) and all(
                v is not None for v in self.scalebar_settings.values()
            ):
                scalebar.setStyle(self.scalebar_settings["style"])
                scalebar.setUnits(self.scalebar_settings["units"])
                scalebar.setNumberOfSegments(self.scalebar_settings["segments"])
                scalebar.setHeight(self.scalebar_settings["height"])
                scalebar.setUnitLabel(self.scalebar_settings["unit_label"])
                scalebar.setPositionWithUnits(self.scalebar_settings["position"])
                scalebar.setAlignment(self.scalebar_settings["alignment"])
                scalebar.setBoxContentSpace(self.scalebar_settings["box_content_space"])
                scalebar.setNumUnitsPerSegment(
                    self.scalebar_settings["units_per_segment"]
                )
                scalebar.setNumMapUnitsPerScaleBarUnit(
                    self.scalebar_settings["num_map_units_per_bar_unit"]
                )
                if self.scalebar_settings["fixed_width"]:
                    scalebar.setFixedWidth(self.scalebar_settings["fixed_width"])
                if self.scalebar_settings["fixed_bar_width"]:
                    scalebar.setFixedBarWidth(self.scalebar_settings["fixed_bar_width"])
                scalebar.refresh()
                print("Applied Scalebar settings")

            # Apply inset scalebar settings
            inset_scalebar = layout.itemById("InsetScaleBar")
            if isinstance(inset_scalebar, QgsLayoutItemScaleBar) and all(
                v is not None for v in self.inset_scalebar_settings.values()
            ):
                inset_scalebar.setStyle(self.inset_scalebar_settings["style"])
                inset_scalebar.setUnits(self.inset_scalebar_settings["units"])
                inset_scalebar.setNumberOfSegments(
                    self.inset_scalebar_settings["segments"]
                )
                inset_scalebar.setHeight(self.inset_scalebar_settings["height"])
                inset_scalebar.setUnitLabel(self.inset_scalebar_settings["unit_label"])
                inset_scalebar.setPositionWithUnits(
                    self.inset_scalebar_settings["position"]
                )
                inset_scalebar.setAlignment(self.inset_scalebar_settings["alignment"])
                inset_scalebar.setBoxContentSpace(
                    self.inset_scalebar_settings["box_content_space"]
                )
                inset_scalebar.setNumUnitsPerSegment(
                    self.inset_scalebar_settings["units_per_segment"]
                )
                inset_scalebar.setNumMapUnitsPerScaleBarUnit(
                    self.inset_scalebar_settings["num_map_units_per_bar_unit"]
                )
                if self.inset_scalebar_settings["fixed_width"]:
                    inset_scalebar.setFixedWidth(
                        self.inset_scalebar_settings["fixed_width"]
                    )
                if self.inset_scalebar_settings["fixed_bar_width"]:
                    inset_scalebar.setFixedBarWidth(
                        self.inset_scalebar_settings["fixed_bar_width"]
                    )
                inset_scalebar.refresh()
                print("Applied InsetScaleBar settings")

            return True
        except Exception as e:
            print(f"Error applying layout state: {str(e)}")
            return False


class LayoutEditor:
    """Handles layout creation and manipulation"""

    def __init__(self, client_location=DEFAULT_CLIENT_LOCATION):
        self.state_manager = LayoutStateManager()
        self.client_location = client_location

    def set_client_location(self, client_location):
        """Update the client location text"""
        self.client_location = client_location

    def get_map_info(self, filename):
        """Extract map information from filename
        Returns: (title_text, map_desc, units_text, legend_file)"""
        # Remove file extension
        basename_no_ext = os.path.splitext(os.path.basename(filename))[0]

        # Remove WGS84 / NAD83 prefix
        match_prefix = re.match(r"^(WGS84|NAD83)\s+", basename_no_ext, re.IGNORECASE)
        start_idx = match_prefix.end() if match_prefix else 0
        remaining_name = basename_no_ext[start_idx:].strip()

        # Find matching key in lookup dictionary
        matched_key = None
        for key in sorted(DESCRIPTION_LOOKUP.keys(), key=len, reverse=True):
            if remaining_name.endswith(key):
                matched_key = key
                break

        if matched_key:
            title_text = remaining_name[: -len(matched_key)].strip()
            map_desc, units_text, legend_file = DESCRIPTION_LOOKUP[matched_key]

            # Add newline for dBdtZch descriptions
            if matched_key and matched_key.startswith("dBdtZch"):
                parts = map_desc.split(" after ")
                if len(parts) == 2:
                    map_desc = parts[0] + "\n" + "after " + parts[1]

            return title_text, map_desc, units_text, legend_file
        else:
            return remaining_name, "", "", ""

    def create_layout(self, template_path, layout_name):
        """Creates a new layout from template"""
        try:
            if not os.path.exists(template_path):
                raise FileNotFoundError("Template file not found")

            # Load template
            with open(template_path, "r", encoding="utf-8") as file:
                template_content = file.read()
            doc = QDomDocument()
            doc.setContent(template_content)

            # Set up layout
            project = QgsProject.instance()
            layout_manager = project.layoutManager()

            # Remove existing layout if it exists
            existing_layout = layout_manager.layoutByName(layout_name)
            if existing_layout:
                layout_manager.removeLayout(existing_layout)

            # Create new layout
            layout = QgsPrintLayout(project)
            layout.initializeDefaults()
            context = QgsReadWriteContext()

            if not layout.loadFromTemplate(doc, context):
                raise RuntimeError("Failed to load layout from template")

            layout.setName(layout_name)
            layout_manager.addLayout(layout)

            # If this is a subsequent layout, apply saved state
            if self.state_manager.initialized:
                self.state_manager.apply_layout_state(layout)

            return layout

        except Exception as e:
            print(f"Error creating layout: {str(e)}")
            return None

    def update_map_item(self, layout, raster_layer):
        """Updates the map item with the raster layer"""
        try:
            map_item = layout.itemById("SatMap")
            if isinstance(map_item, QgsLayoutItemMap):
                map_item.setLayers([raster_layer])
                extent = raster_layer.extent()
                if not extent.isEmpty():
                    # For first map, zoom to extent and capture state
                    if not self.state_manager.initialized:
                        map_item.zoomToExtent(extent)
                        map_item.setScale(round(map_item.scale(), -3))
                        # Capture initial state after first map is set up
                        self.state_manager.capture_layout_state(layout)
                    else:
                        # For subsequent maps, preserve scale but center on new extent
                        current_scale = map_item.scale()
                        map_item.zoomToExtent(extent)
                        map_item.setScale(current_scale)

                    map_item.refresh()
                return True
        except Exception as e:
            print(f"Error updating map item: {str(e)}")
        return False

    def update_text_item(self, layout, item_id, text):
        """Updates a text item in the layout"""
        try:
            item = layout.itemById(item_id)
            if isinstance(item, QgsLayoutItemLabel):
                item.setText(text)
                return True
        except Exception as e:
            print(f"Error updating text item: {str(e)}")
        return False

    def update_picture_item(self, layout, item_id, picture_path):
        """Updates a picture item in the layout"""
        try:
            item = layout.itemById(item_id)
            if isinstance(item, QgsLayoutItemPicture):
                if os.path.exists(picture_path):
                    item.setPicturePath(picture_path)
                    item.refresh()
                    return True
                else:
                    print(f"Picture file not found: {picture_path}")
        except Exception as e:
            print(f"Error updating picture item: {str(e)}")
        return False

    def get_item_by_id(self, layout, item_id):
        """Retrieves a layout item by its ID"""
        try:
            return layout.itemById(item_id)
        except Exception as e:
            print(f"Error getting item by ID: {str(e)}")
            return None
