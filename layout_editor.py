from qgis.core import (
    QgsPrintLayout,
    QgsLayoutItemMap,
    QgsLayoutItemLabel,
    QgsLayoutItemPicture,
    QgsProject,
    QgsReadWriteContext,
    QgsRasterLayer,
)
from qgis.PyQt.QtXml import QDomDocument
import re
import os


# Default client information
DEFAULT_CLIENT_LOCATION = "Axiom Exploration\nRio de Janeiro, Brazil"

# Layers that should never be hidden
EXCEPTION_LAYERS = {
    "Esri World Imagery (Clarity) Beta",
    "Google Satellite Hybrid",
    "property AOI",
}

# Description lookup dictionary for map types
DESCRIPTION_LOOKUP = {
    "AGL": (
        "Sensor Altitude",
        "Sensor Altitude (m)",
        "AGL.png",
    ),
    "dBdtZch10": (
        "dB/dt z component 0.014 ms after turnoff",
        "dB/dt z component: channel 10 (pV/(Am^4))",
        "dBdtZch10.png",
    ),
    "DTM": (
        "Digital Terrain Model",
        "Digital Terrain Model (m)",
        "DTM.png",
    ),
    "FlightPath": (
        "Flight Path",
        "",
        None,  # No legend
    ),
    "TMI": (
        "Total Magnetic Intensity",
        "Total Magnetic Intensity (nT)",
        "TMI.png",
    ),
    "TMI_RTP": (
        "TMI Reduced to Pole",
        "Total Magnetic Intensity Reduced to Pole (nT)",
        "TotalFieldMagneticsRTP.png",
    ),
    "TMI_RTP_AS": (
        "Analytical Signal",
        "Analytical Signal (nT/m)",
        "TMI_RTP_AS.png",
    ),
    "TMI_RTP_HD_TDR": (
        "Horizontal Derivative of the Tilt",
        "Tilt Horizontal Derivative : TMI Reduced to Pole (rad/m)",
        "TMI_RTP_HD_TDR.png",
    ),
    "TMI_RTP_RMI": (
        "Residual Magnetic Intensity",
        "IGRF corrected TMI (nT)",
        "TMI_RTP_RMI.png",
    ),
    "TMI_RTP_TDR": (
        "Tilt Derivative",
        "Tilt Derivative: TMI Reduced to Pole (rad)",
        "TMI_RTP_TDR.png",
    ),
    "TMI_RTP_THDR": (
        "Total Horizontal Gradient",
        "Total Horizontal Gradient: TMI Reduced to Pole (nT/m)",
        "TMI_RTP_THDR.png",
    ),
    "TMI_RTP_VD1": (
        "First Vertical Derivative",
        "First Vertical Derivative: TMI Reduced to Pole (nT/m)",
        "TMI_RTP_VD1.png",
    ),
    "Th-K_Ratio": (
        "Thorium / Potassium Ratio",
        "Th / K Ratio",
        "Th-K_Ratio",
    ),
    "U-K_Ratio": (
        "Uranium / Potassium Ratio",
        "U / K Ratio",
        "U-K_Ratio",
    ),
    "U-Th_Ratio": (
        "Uranium / Thorium Ratio",
        "U / Th Ratio",
        "U-Th_Ratio",
    ),
    "Ternary": (
        "Radiometric Ternary Image",
        "",
        "Ternary.png",
    ),
    "Total_NASVD": (
        "Radiometric Total Count",
        "Counts (cps)",
        "Total_NASVD.png",
    ),
    "Th_NASVD": (
        "Thorium NASVD Processed",
        "Thorium %",
        "Th_NASVD.png",
    ),
    "U_NASVD": (
        "Uranium NASVD Processed",
        "Uranium %",
        "U_NASVD.png",
    ),
    "K_NASVD": (
        "Potassium NASVD Processed",
        "Potassium %",
        "K_NASVD.png",
    ),
}


class LayoutEditor:
    """Handles layout creation and manipulation"""

    def __init__(self, client_location=DEFAULT_CLIENT_LOCATION):
        self.client_location = client_location

        # Path to transparency style QML inside plugin folder
        self.transparency_qml = os.path.join(
            os.path.dirname(__file__), "transparency_style.qml"
        )

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

        # 🔹 Conductivity depth slices
        match_conductivity = re.search(
            r"ConductivityDepthSlice\s*(\d+m)$", remaining_name
        )
        if match_conductivity:
            depth_value = match_conductivity.group(1)
            title_text = remaining_name.replace(match_conductivity.group(0), "").strip()
            map_desc = f"Conductivity Depth Slice\n{depth_value.replace('m',' m')}"
            units_text = "Conductivity (S/m)"
            legend_file = "Conductivity.png"
            return title_text, map_desc, units_text, legend_file

        # 🔹 Susceptibility depth slices
        match_susceptibility = re.search(
            r"SusceptibilityDepthSlice\s*(\d+m)$", remaining_name
        )
        if match_susceptibility:
            depth_value = match_susceptibility.group(1)
            title_text = remaining_name.replace(
                match_susceptibility.group(0), ""
            ).strip()
            map_desc = f"Susceptibility Depth Slice\n{depth_value.replace('m',' m')}"
            units_text = "Relative Susceptibility (SI)"
            legend_file = "Susceptibility.png"
            return title_text, map_desc, units_text, legend_file

        # 🔹 Residual Filtered variable depths
        match_residual = re.search(
            r"TotalFieldMagneticsRTPresidual\s*(\d+m)$", remaining_name, re.IGNORECASE
        )
        if match_residual:
            depth_value = match_residual.group(1)
            title_text = remaining_name.replace(match_residual.group(0), "").strip()
            map_desc = f"Residual Filtered - {depth_value.replace('m',' m')}"
            units_text = "Residual Filtered: TMI Reduced to Pole (nT)"
            legend_file = "TotalFieldMagneticsRTPResidual.png"
            return title_text, map_desc, units_text, legend_file

        # 🔹 Regional Filtered variable depths
        match_regional = re.search(
            r"TotalFieldMagneticsRTPregional\s*(\d+m)$", remaining_name, re.IGNORECASE
        )
        if match_regional:
            depth_value = match_regional.group(1)
            title_text = remaining_name.replace(match_regional.group(0), "").strip()
            map_desc = f"Regional Filtered - {depth_value.replace('m',' m')}"
            units_text = "Regional Filtered: TMI Reduced to Pole (nT)"
            legend_file = "TotalFieldMagneticsRTPRegional.png"
            return title_text, map_desc, units_text, legend_file

        # 🔹 Regular lookup fallback
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
            project = QgsProject.instance()
            layout_manager = project.layoutManager()

            if layout_manager.layoutByName(layout_name):
                raise RuntimeError(
                    f'Map layout "{layout_name}" already exists. Choose a different name.'
                )

            if not os.path.exists(template_path):
                raise FileNotFoundError("Template file not found")

            with open(template_path, "r", encoding="utf-8") as file:
                template_content = file.read()
            doc = QDomDocument()
            doc.setContent(template_content)

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

            if layout_manager.layoutByName(new_name):
                raise RuntimeError(
                    f'Map layout "{new_name}" already exists. Choose a different name.'
                )

            new_layout = source_layout.clone()
            new_layout.setName(new_name)
            layout_manager.addLayout(new_layout)
            return new_layout

        except Exception as e:
            print(f"Error duplicating layout: {str(e)}")
            return None

    def update_map_item(self, layout, raster_layer):
        """Updates the map item with the raster layer,
        preserving scale and extent from duplication"""
        try:
            if (
                not isinstance(raster_layer, QgsRasterLayer)
                or not raster_layer.isValid()
            ):
                print("geotiff search was not found")
                return False

            map_item = layout.itemById("SatMap")
            if isinstance(map_item, QgsLayoutItemMap):
                map_item.setLayers([raster_layer])
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
                if text:
                    item.setText(text)
                return True
        except Exception as e:
            print(f"Error updating text item: {str(e)}")
        return False

    def update_picture_item(self, layout, item_id, picture_path):
        """Updates a picture item in the layout"""
        try:
            if not picture_path:
                return True  # Skip if no legend is required (e.g., FlightPath)

            if not os.path.exists(picture_path):
                print("geotiff legend not found")
                return False

            item = layout.itemById(item_id)
            if isinstance(item, QgsLayoutItemPicture):
                item.setPicturePath(picture_path)
                item.refresh()
                return True
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

    # 🔹 Apply QML style for transparency
    def apply_transparency_style(self, raster_layer: QgsRasterLayer):
        """Apply predefined QML style (transparency) to raster"""
        try:
            if not isinstance(raster_layer, QgsRasterLayer):
                print("Not a raster layer")
                return False

            if not os.path.exists(self.transparency_qml):
                print(f"Transparency QML not found: {self.transparency_qml}")
                return False

            success, error_message = raster_layer.loadNamedStyle(self.transparency_qml)
            if not success:
                print(f"Failed to apply transparency QML: {error_message}")
                return False

            raster_layer.triggerRepaint()
            print(f"Applied QML transparency style to: {raster_layer.name()}")
            return True
        except Exception as e:
            print(f"Error applying transparency style: {str(e)}")
            return False

    # 🔹 Hide all other layers except exceptions
    def hide_other_layers(self, keep_layer: QgsRasterLayer):
        """Hide all layers except exceptions and the keep_layer"""
        project = QgsProject.instance()
        layer_tree = project.layerTreeRoot()

        for child in layer_tree.children():
            layer = child.layer()
            if layer is None:
                continue

            if layer == keep_layer or layer.name() in EXCEPTION_LAYERS:
                child.setItemVisibilityChecked(True)
            else:
                child.setItemVisibilityChecked(False)

        print(
            f"Applied hide-other-layers. Kept {keep_layer.name()} and exceptions: {EXCEPTION_LAYERS}"
        )
