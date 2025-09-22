from qgis.core import (
    QgsPrintLayout,
    QgsLayoutItemMap,
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
    "SensorAltitude": (
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
        "dBdtZch10.png",
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


class LayoutEditor:
    """Handles layout creation and manipulation"""

    def __init__(self, client_location=DEFAULT_CLIENT_LOCATION):
        self.client_location = client_location

    def set_client_location(self, client_location):
        """Update the client location text"""
        self.client_location = client_location

    def get_map_info(self, filename):
        """Extract map information from filename
        Returns: (title_text, map_desc, units_text, legend_file)"""
        basename_no_ext = os.path.splitext(os.path.basename(filename))[0]

        # Remove WGS84 / NAD83 prefix
        match_prefix = re.match(r"^(WGS84|NAD83)\s+", basename_no_ext, re.IGNORECASE)
        start_idx = match_prefix.end() if match_prefix else 0
        remaining_name = basename_no_ext[start_idx:].strip()

        matched_key = None
        for key in sorted(DESCRIPTION_LOOKUP.keys(), key=len, reverse=True):
            if remaining_name.endswith(key):
                matched_key = key
                break

        if matched_key:
            title_text = remaining_name[: -len(matched_key)].strip()
            map_desc, units_text, legend_file = DESCRIPTION_LOOKUP[matched_key]

            # Add newline for dBdtZch descriptions
            if matched_key.startswith("dBdtZch"):
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

            with open(template_path, "r", encoding="utf-8") as file:
                template_content = file.read()
            doc = QDomDocument()
            doc.setContent(template_content)

            project = QgsProject.instance()
            layout_manager = project.layoutManager()

            existing_layout = layout_manager.layoutByName(layout_name)
            if existing_layout:
                layout_manager.removeLayout(existing_layout)

            layout = QgsPrintLayout(project)
            layout.initializeDefaults()
            context = QgsReadWriteContext()

            if not layout.loadFromTemplate(doc, context):
                raise RuntimeError("Failed to load layout from template")

            layout.setName(layout_name)
            layout_manager.addLayout(layout)

            return layout

        except Exception as e:
            print(f"Error creating layout: {str(e)}")
            return None

    def duplicate_layout(self, source_layout, new_name):
        """Duplicates an existing layout (all variables preserved)"""
        try:
            project = QgsProject.instance()
            layout_manager = project.layoutManager()

            existing_layout = layout_manager.layoutByName(new_name)
            if existing_layout:
                layout_manager.removeLayout(existing_layout)

            new_layout = source_layout.clone()
            new_layout.setName(new_name)
            layout_manager.addLayout(new_layout)
            return new_layout

        except Exception as e:
            print(f"Error duplicating layout: {str(e)}")
            return None

    def update_map_item(self, layout, raster_layer):
        """Updates the map item with the raster layer"""
        try:
            map_item = layout.itemById("SatMap")
            if isinstance(map_item, QgsLayoutItemMap):
                map_item.setLayers([raster_layer])
                extent = raster_layer.extent()
                if not extent.isEmpty():
                    map_item.zoomToExtent(extent)
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
