import os
import re
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

# -----------------------------
# Map description lookup
# -----------------------------
DESCRIPTION_LOOKUP = {
    "AGL": ("Sensor Altitude", "Sensor Altitude (m)", "AGL.png"),
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
    "DTM": ("Digital Terrain Model", "Digital Terrain Model (m)", "DTM.png"),
    "FlightPath": ("Flight Path", "", None),
    "TMI": ("Total Magnetic Intensity", "Total Magnetic Intensity (nT)", "TMI.png"),
    "TMI_RTP": (
        "Reduced to Pole TMI",
        "Total Magnetic Intensity : Reduced to Pole (nT)",
        "TMI_RTP.png",
    ),
    "TMI_AS": ("Analytical Signal", "Analytical Signal (nT/m)", "TMI_AS.png"),
    "TMI_RTP_HD_TDR": (
        "Horizontal Derivative of the Tilt",
        "Tilt Horizontal Derivative : Reduced to Pole TMI (rad/m)",
        "TMI_RTP_HD_TDR.png",
    ),
    "TMI_RTP_RMI": (
        "Residual Magnetic Intensity",
        "IGRF corrected TMI (nT)",
        "TMI_RTP_RMI.png",
    ),
    "TMI_RTP_TDR": (
        "Tilt Derivative",
        "Tilt Derivative: Reduced to Pole TMI (rad)",
        "TMI_RTP_TDR.png",
    ),
    "TMI_RTP_THDR": (
        "Total Horizontal Gradient",
        "Total Horizontal Gradient: Reduced to Pole TMI (nT/m)",
        "TMI_RTP_THDR.png",
    ),
    "TMI_RTP_VD1": (
        "First Vertical Derivative",
        "First Vertical Derivative: Reduced to Pole TMI (nT/m)",
        "TMI_RTP_VD1.png",
    ),
    "Th-K_Ratio": ("Thorium / Potassium Ratio", "Th / K Ratio", "Th-K_Ratio"),
    "U-K_Ratio": ("Uranium / Potassium Ratio", "U / K Ratio", "U-K_Ratio"),
    "U-Th_Ratio": ("Uranium / Thorium Ratio", "U / Th Ratio", "U-Th_Ratio"),
    "Ternary": ("Radiometric Ternary Image", None, "Ternary.png"),
    "Total_NASVD": ("Radiometric Total Count", "Counts (cps)", "Total_NASVD.png"),
    "Th_NASVD": ("Thorium NASVD Processed", "Thorium (ppm)", "Th_NASVD.png"),
    "U_NASVD": ("Uranium NASVD Processed", "Uranium (ppm)", "U_NASVD.png"),
    "K_NASVD": ("Potassium NASVD Processed", "Potassium (%)", "K_NASVD.png"),
}


class LayoutEditor:
    """Handles layout creation, duplication, styling, and map item management."""

    def __init__(self, exception_layers=None):
        """
        Initialize LayoutEditor.

        Args:
            exception_layers (set[str], optional): Layers that should never be hidden.
        """
        self.client_location = ""
        self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.exception_layers = exception_layers or {
            "Esri World Imagery (Clarity) Beta",
            "Google Satellite Hybrid",
            "property AOI",
        }

    # -----------------------------
    # Exception Layers Management
    # -----------------------------
    def set_exception_layers(self, layers_set):
        """Override the layers that are never hidden."""
        self.exception_layers = set(layers_set)
        print(f"Updated exception layers: {self.exception_layers}")

    # -----------------------------
    # Client Info
    # -----------------------------
    def set_client_location(self, client_location):
        """Store the client location text (normalize newlines)."""
        if client_location:
            self.client_location = client_location.replace("\r\n", "\n")
        else:
            self.client_location = ""

    # -----------------------------
    # Raster Styling
    # -----------------------------
    def apply_style_qml(self, raster_layer: QgsRasterLayer, qml_file):
        """Apply a QML style file to a raster layer."""
        try:
            if not isinstance(raster_layer, QgsRasterLayer):
                print("Not a raster layer")
                return False
            if not os.path.exists(qml_file):
                print(f"Style QML not found: {qml_file}")
                return False
            success, error_message = raster_layer.loadNamedStyle(qml_file)
            if not success:
                print(f"Failed to apply QML style: {error_message}")
                return False
            raster_layer.triggerRepaint()
            print(f"Applied QML style: {os.path.basename(qml_file)}")
            return True
        except Exception as e:
            print(f"Error applying QML style: {e}")
            return False

    def apply_transparency_style(self, raster_layer: QgsRasterLayer):
        """Apply default transparency QML style (backward-compatible)."""
        qml = os.path.join(self.templates_dir, "transparency_style.qml")
        return self.apply_style_qml(raster_layer, qml)

    # -----------------------------
    # Layout Creation / Duplication
    # -----------------------------
    def create_layout(self, template_path, layout_name):
        """Create a new layout from a QPT template."""
        try:
            project = QgsProject.instance()
            layout_manager = project.layoutManager()
            if layout_manager.layoutByName(layout_name):
                raise RuntimeError(f'Map layout "{layout_name}" already exists.')
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
            print(f"Created layout from template: {os.path.basename(template_path)}")
            return layout
        except Exception as e:
            print(f"Error creating layout: {e}")
            return None

    def duplicate_layout(self, source_layout, new_name):
        """Duplicate an existing layout with all settings preserved."""
        try:
            project = QgsProject.instance()
            layout_manager = project.layoutManager()
            if layout_manager.layoutByName(new_name):
                raise RuntimeError(f'Map layout "{new_name}" already exists.')
            new_layout = source_layout.clone()
            new_layout.setName(new_name)
            layout_manager.addLayout(new_layout)
            return new_layout
        except Exception as e:
            print(f"Error duplicating layout: {e}")
            return None

    # -----------------------------
    # Map Item Updates
    # -----------------------------
    def update_map_item(self, layout, raster_layer, zoom_to_extent=False):
        """Update map item with raster layer and optional zoom to raster extent."""
        try:
            if (
                not isinstance(raster_layer, QgsRasterLayer)
                or not raster_layer.isValid()
            ):
                print("Raster layer invalid or not found")
                return False
            map_item = layout.itemById("SatMap")
            if isinstance(map_item, QgsLayoutItemMap):
                map_item.setLayers([raster_layer])
                if zoom_to_extent:
                    map_item.zoomToExtent(raster_layer.extent())
                map_item.refresh()
                return True
        except Exception as e:
            print(f"Error updating map item: {e}")
        return False

    def update_text_item(self, layout, item_id, text):
        """Update a text label item in the layout."""
        try:
            item = layout.itemById(item_id)
            if isinstance(item, QgsLayoutItemLabel) and text:
                item.setText(text)
                return True
        except Exception as e:
            print(f"Error updating text item: {e}")
        return False

    def update_picture_item(self, layout, item_id, picture_path):
        """Update a picture (legend) item in the layout."""
        try:
            if not picture_path or not os.path.exists(picture_path):
                print("Legend/picture not found")
                return False
            item = layout.itemById(item_id)
            if isinstance(item, QgsLayoutItemPicture):
                item.setPicturePath(picture_path)
                item.refresh()
                return True
        except Exception as e:
            print(f"Error updating picture item: {e}")
        return False

    def get_item_by_id(self, layout, item_id):
        """Retrieve a layout item by its ID."""
        try:
            return layout.itemById(item_id)
        except Exception as e:
            print(f"Error getting item by ID: {e}")
            return None

    # -----------------------------
    # Layer Visibility Management
    # -----------------------------
    def hide_other_layers(self, keep_layer: QgsRasterLayer):
        """Hide all layers except keep_layer and exception layers."""
        project = QgsProject.instance()
        layer_tree = project.layerTreeRoot()
        for child in layer_tree.children():
            layer = child.layer()
            if layer and (layer == keep_layer or layer.name() in self.exception_layers):
                child.setItemVisibilityChecked(True)
            elif layer:
                child.setItemVisibilityChecked(False)
        kept_name = keep_layer.name() if keep_layer else "None"
        print(
            f"Applied hide-other-layers. Kept {kept_name} and exceptions: {self.exception_layers}"
        )

    # -----------------------------
    # Map Info Extraction
    # -----------------------------
    def get_map_info(self, filename):
        """Extract map info: title, description, units, and legend from filename."""
        basename_no_ext = os.path.splitext(os.path.basename(filename))[0]
        match_prefix = re.match(r"^(WGS84|NAD83)\s+", basename_no_ext, re.IGNORECASE)
        remaining_name = basename_no_ext[
            (match_prefix.end() if match_prefix else 0) :
        ].strip()

        # Depth slice / residual / regional matches
        depth_patterns = [
            (
                r"Conductivity\s*(\d+m)$",
                "Conductivity Depth Slice",
                "Conductivity (mS/m)",
                "Conductivity.png",
            ),
            (
                r"Susceptibility\s*(\d+m)$",
                "Susceptibility Depth Slice",
                "Susceptibility (SI)",
                "Susceptibility.png",
            ),
            (
                r"TMI_RTP_residual\s*(\d+m)$",
                "Residual Filtered",
                "Residual Filtered: Reduced to Pole TMI (nT)",
                "TMI_RTP_residual.png",
            ),
            (
                r"TMI_RTP_regional\s*(\d+m)$",
                "Regional Filtered",
                "Regional Filtered: Reduced to Pole TMI (nT)",
                "TMI_RTP_regional.png",
            ),
        ]
        for pattern, desc, units, legend in depth_patterns:
            match = re.search(pattern, remaining_name, re.IGNORECASE)
            if match:
                depth = match.group(1)
                title = remaining_name.replace(match.group(0), "").strip()
                map_desc = f"{desc}\n{depth.replace('m',' m')}"
                return title, map_desc, units, legend

        # Standard lookup
        matched_key = next(
            (
                k
                for k in sorted(DESCRIPTION_LOOKUP.keys(), key=len, reverse=True)
                if remaining_name.endswith(k)
            ),
            None,
        )
        if matched_key:
            title = remaining_name[: -len(matched_key)].strip()
            map_desc, units, legend = DESCRIPTION_LOOKUP[matched_key]
            if matched_key.startswith("dBdtZch"):
                parts = map_desc.split(" after ")
                if len(parts) == 2:
                    map_desc = parts[0] + "\n" + "after " + parts[1]
            return title, map_desc, units, legend

        return remaining_name, "", "", ""
