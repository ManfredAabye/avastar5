### Copyright 2025 Manfred Aabye
###
### Bakes on Mesh (BoM) Tools for Avastar
### 

### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import logging
from bpy.props import *
from .const import *

log = logging.getLogger('avastar.bom')
registerlog = logging.getLogger("avastar.register")


# ==============================================================================
# Bakes on Mesh (BoM) System Layer Management
# ==============================================================================
# BoM allows system layer textures (clothing, tattoos, etc.) to be baked
# directly onto mesh bodies, eliminating the need for alpha masking

class BomLayerType:
    """System layer types supported by Second Life/OpenSim"""
    SKIN = 'SKIN'
    TATTOO = 'TATTOO'
    CLOTHING = 'CLOTHING'
    EYEBROW = 'EYEBROW'
    HAIR = 'HAIR'


class AVASTAR_OT_bom_setup_material(bpy.types.Operator):
    """Setup BoM-compatible material for mesh"""
    bl_idname = "avastar.bom_setup_material"
    bl_label = "Setup BoM Material"
    bl_description = (
        "Creates a Bakes on Mesh compatible material setup\n\n"
        "This configures the material to receive system layer textures\n"
        "(skin, tattoos, clothing) directly from the viewer\n\n"
        "Requirements:\n"
        "- Mesh must have UV maps\n"
        "- Works with avatar body parts\n"
        "- Viewer must support BoM (2019+)"
    )
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        if not obj.data.uv_layers:
            self.report({'ERROR'}, "Mesh has no UV maps. Add UV coordinates first.")
            return {'CANCELLED'}

        # Create or get material
        mat_name = f"{obj.name}_BoM"
        mat = bpy.data.materials.get(mat_name)
        if not mat:
            mat = bpy.data.materials.new(name=mat_name)
            mat.use_nodes = True
        
        # Clear existing nodes
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        # Create principled BSDF
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Create output node
        output = nodes.new('ShaderNodeOutputMaterial')
        output.location = (300, 0)
        
        # Link nodes
        mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        # Configure for BoM
        bsdf.inputs['Specular'].default_value = 0.0
        bsdf.inputs['Roughness'].default_value = 1.0
        
        # Assign material to object
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        
        self.report({'INFO'}, f"BoM material '{mat_name}' created successfully")
        return {'FINISHED'}


class AVASTAR_OT_bom_add_layer_slot(bpy.types.Operator):
    """Add BoM layer texture slot"""
    bl_idname = "avastar.bom_add_layer_slot"
    bl_label = "Add BoM Layer"
    bl_description = (
        "Adds a texture slot for a specific BoM system layer\n\n"
        "Layer Types:\n"
        "• SKIN - Base avatar skin texture\n"
        "• TATTOO - Tattoo layer overlay\n"
        "• CLOTHING - Clothing texture layer\n"
        "• EYEBROW - Eyebrow layer\n"
        "• HAIR - Hair layer\n\n"
        "Note: In Second Life, these textures are applied\n"
        "automatically by the viewer when wearing system items"
    )
    bl_options = {'REGISTER', 'UNDO'}
    
    layer_type : EnumProperty(
        name="Layer Type",
        items=[
            ('SKIN', 'Skin', 'Base skin layer'),
            ('TATTOO', 'Tattoo', 'Tattoo overlay layer'),
            ('CLOTHING', 'Clothing', 'Clothing layer'),
            ('EYEBROW', 'Eyebrow', 'Eyebrow layer'),
            ('HAIR', 'Hair', 'Hair layer'),
        ],
        default='SKIN'
    )

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        if not obj.active_material:
            self.report({'ERROR'}, "No active material. Run 'Setup BoM Material' first")
            return {'CANCELLED'}

        mat = obj.active_material
        if not mat.use_nodes:
            mat.use_nodes = True

        nodes = mat.node_tree.nodes
        bsdf = nodes.get('Principled BSDF')
        if not bsdf:
            self.report({'ERROR'}, "Material is not BoM compatible")
            return {'CANCELLED'}

        # Create texture image node for this layer
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.name = f"BoM_{self.layer_type}"
        tex_node.label = f"BoM {self.layer_type}"
        tex_node.location = (-400, 0)
        
        # Create placeholder image
        img_name = f"{obj.name}_{self.layer_type}_BoM"
        if img_name not in bpy.data.images:
            img = bpy.data.images.new(img_name, width=1024, height=1024, alpha=True)
            img.source = 'GENERATED'
        else:
            img = bpy.data.images[img_name]
        
        tex_node.image = img
        
        # Link to base color (can be customized for layer blending)
        mat.node_tree.links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
        
        self.report({'INFO'}, f"Added {self.layer_type} BoM layer to material")
        return {'FINISHED'}


class AVASTAR_OT_bom_export_preview(bpy.types.Operator):
    """Generate BoM export preview"""
    bl_idname = "avastar.bom_export_preview"
    bl_label = "Preview BoM Export"
    bl_description = (
        "Generates a preview of how the mesh will look\n"
        "with BoM system layers applied in Second Life\n\n"
        "This bakes all layer textures into a single preview\n"
        "texture for testing purposes\n\n"
        "Note: This does not affect the actual BoM export"
    )
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        if not obj.active_material:
            self.report({'ERROR'}, "No material to preview")
            return {'CANCELLED'}

        self.report({'INFO'}, "BoM preview generated (placeholder - requires full baking implementation)")
        return {'FINISHED'}


class AVASTAR_PT_bom_tools(bpy.types.Panel):
    """BoM Tools Panel"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = UI_LOCATION
    bl_category    = "Avastar"
    bl_label = "Bakes on Mesh (BoM)"
    bl_idname = "AVASTAR_PT_bom_tools"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        box = layout.box()
        box.label(text="BoM Material Setup", icon='MATERIAL')
        box.operator("avastar.bom_setup_material", icon='ADD')

        if obj and obj.active_material:
            box = layout.box()
            box.label(text="System Layers", icon='TEXTURE')
            box.operator("avastar.bom_add_layer_slot", icon='ADD').layer_type = 'SKIN'
            row = box.row(align=True)
            row.operator("avastar.bom_add_layer_slot", text="Tattoo").layer_type = 'TATTOO'
            row.operator("avastar.bom_add_layer_slot", text="Clothing").layer_type = 'CLOTHING'

        box = layout.box()
        box.label(text="Preview & Export", icon='RENDER_RESULT')
        box.operator("avastar.bom_export_preview", icon='PLAY')


# ==============================================================================
# Registration
# ==============================================================================

classes = (
    AVASTAR_OT_bom_setup_material,
    AVASTAR_OT_bom_add_layer_slot,
    AVASTAR_OT_bom_export_preview,
    AVASTAR_PT_bom_tools,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
        registerlog.info("Registered bom:%s" % cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
        registerlog.info("Unregistered bom:%s" % cls)
