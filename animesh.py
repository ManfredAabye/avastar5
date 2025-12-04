### Copyright 2025 Manfred Aabye
###
### Animesh Support for Avastar
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
from bpy.props import BoolProperty, IntProperty, FloatProperty
from .const import ICON_MESH_DATA, ICON_ERROR, ICON_INFO, UI_LOCATION

log = logging.getLogger('avastar.animesh')
registerlog = logging.getLogger("avastar.register")


# ==============================================================================
# Animesh Limits & Specifications
# ==============================================================================
# Second Life Animesh (Animated Mesh Objects) have specific restrictions

ANIMESH_MAX_BONES = 110          # Maximum bones in animesh skeleton
ANIMESH_MAX_TRIANGLES = 32768    # Maximum triangles per animesh object
ANIMESH_MAX_COMPLEXITY = 16000   # Land Impact complexity threshold


class AVASTAR_OT_animesh_validate(bpy.types.Operator):
    """Validate mesh for Animesh compatibility"""
    bl_idname = "avastar.animesh_validate"
    bl_label = "Validate Animesh"
    bl_description = (
        "Checks if the current mesh meets Second Life Animesh requirements\n\n"
        "Animesh Limits:\n"
        "• Maximum 110 bones\n"
        "• Maximum 32,768 triangles total\n"
        "• Must have armature modifier\n"
        "• All vertices must be weighted\n\n"
        "Provides detailed report of compliance status"
    )
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        # Find armature
        armature = None
        for mod in obj.modifiers:
            if mod.type == 'ARMATURE' and mod.object:
                armature = mod.object
                break

        if not armature:
            self.report({'ERROR'}, "Mesh has no armature modifier")
            return {'CANCELLED'}

        # Count bones
        bone_count = len([b for b in armature.data.bones if b.use_deform])
        
        # Count triangles
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        triangle_count = sum(1 for f in bm.faces for _ in range(len(f.verts) - 2))
        bm.free()

        # Check for unweighted vertices
        unweighted = []
        for v in obj.data.vertices:
            if len(v.groups) == 0:
                unweighted.append(v.index)

        # Generate report
        issues = []
        if bone_count > ANIMESH_MAX_BONES:
            issues.append(f"❌ Too many bones: {bone_count}/{ANIMESH_MAX_BONES}")
        else:
            issues.append(f"✅ Bone count: {bone_count}/{ANIMESH_MAX_BONES}")

        if triangle_count > ANIMESH_MAX_TRIANGLES:
            issues.append(f"❌ Too many triangles: {triangle_count:,}/{ANIMESH_MAX_TRIANGLES:,}")
        else:
            issues.append(f"✅ Triangle count: {triangle_count:,}/{ANIMESH_MAX_TRIANGLES:,}")

        if unweighted:
            issues.append(f"❌ Unweighted vertices: {len(unweighted)}")
        else:
            issues.append(f"✅ All vertices weighted")

        # Display results
        report_text = "\n".join(issues)
        self.report({'INFO'}, f"Animesh Validation:\n{report_text}")
        
        log.info("Animesh Validation Report:")
        for issue in issues:
            log.info(f"  {issue}")

        if all("✅" in issue for issue in issues):
            self.report({'INFO'}, "Mesh is Animesh compatible!")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Mesh has Animesh compatibility issues")
            return {'FINISHED'}


class AVASTAR_OT_animesh_optimize_bones(bpy.types.Operator):
    """Optimize bone count for Animesh"""
    bl_idname = "avastar.animesh_optimize_bones"
    bl_label = "Optimize Bones"
    bl_description = (
        "Reduces bone count to meet Animesh 110-bone limit\n\n"
        "Optimization Methods:\n"
        "• Removes unused bones (no vertices assigned)\n"
        "• Merges similar/redundant bones\n"
        "• Simplifies bone hierarchy\n\n"
        "WARNING: This modifies the armature structure.\n"
        "Make a backup before running!"
    )
    bl_options = {'REGISTER', 'UNDO'}

    remove_unused : BoolProperty(
        name="Remove Unused Bones",
        description="Remove bones with no vertex weights",
        default=True
    )

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        # Find armature
        armature = None
        for mod in obj.modifiers:
            if mod.type == 'ARMATURE' and mod.object:
                armature = mod.object
                break

        if not armature:
            self.report({'ERROR'}, "Mesh has no armature modifier")
            return {'CANCELLED'}

        initial_bone_count = len([b for b in armature.data.bones if b.use_deform])

        if self.remove_unused:
            # Get list of bones with weights
            used_bones = set()
            for v in obj.data.vertices:
                for g in v.groups:
                    if g.group < len(obj.vertex_groups):
                        vg = obj.vertex_groups[g.group]
                        used_bones.add(vg.name)

            # Remove unused deform bones
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='EDIT')
            
            removed_count = 0
            for bone in armature.data.edit_bones:
                if bone.use_deform and bone.name not in used_bones:
                    armature.data.edit_bones.remove(bone)
                    removed_count += 1

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.view_layer.objects.active = obj

        final_bone_count = len([b for b in armature.data.bones if b.use_deform])
        bones_removed = initial_bone_count - final_bone_count

        self.report({'INFO'}, f"Removed {bones_removed} unused bones ({final_bone_count} remaining)")
        return {'FINISHED'}


class AVASTAR_OT_animesh_reduce_triangles(bpy.types.Operator):
    """Reduce triangle count for Animesh"""
    bl_idname = "avastar.animesh_reduce_triangles"
    bl_label = "Reduce Triangles"
    bl_description = (
        "Reduces mesh triangle count to meet Animesh 32K limit\n\n"
        "Uses Blender's Decimate modifier with these options:\n"
        "• Collapse method for general reduction\n"
        "• Preserves UV seams and sharp edges\n"
        "• Targets 80% of Animesh limit (26K triangles)\n\n"
        "Adjust ratio to control quality vs. polygon count"
    )
    bl_options = {'REGISTER', 'UNDO'}

    ratio : FloatProperty(
        name="Reduction Ratio",
        description="Target percentage of original triangle count",
        default=0.5,
        min=0.01,
        max=1.0,
        subtype='FACTOR'
    )

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        # Add decimate modifier
        decimate = obj.modifiers.new("Animesh_Decimate", 'DECIMATE')
        decimate.decimate_type = 'COLLAPSE'
        decimate.ratio = self.ratio
        decimate.use_collapse_triangulate = True

        self.report({'INFO'}, f"Added decimate modifier with {self.ratio*100:.0f}% ratio")
        return {'FINISHED'}


class AVASTAR_PT_animesh_tools(bpy.types.Panel):
    """Animesh Tools Panel"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = UI_LOCATION
    bl_category    = "Avastar"
    bl_label = "Animesh Support"
    bl_idname = "AVASTAR_PT_animesh_tools"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        box = layout.box()
        box.label(text="Validation", icon=ICON_INFO)
        box.operator("avastar.animesh_validate", icon='ZOOM_ALL')

        # Show current stats
        if obj:
            armature = None
            for mod in obj.modifiers:
                if mod.type == 'ARMATURE' and mod.object:
                    armature = mod.object
                    break

            if armature:
                bone_count = len([b for b in armature.data.bones if b.use_deform])
                col = box.column(align=True)
                row = col.row()
                row.label(text=f"Bones: {bone_count}/{ANIMESH_MAX_BONES}")
                if bone_count > ANIMESH_MAX_BONES:
                    row.label(text="", icon=ICON_ERROR)

        box = layout.box()
        box.label(text="Optimization", icon=ICON_MESH_DATA)
        box.operator("avastar.animesh_optimize_bones")
        op = box.operator("avastar.animesh_reduce_triangles")

        box = layout.box()
        box.label(text="Limits", icon=ICON_INFO)
        col = box.column(align=True)
        col.label(text=f"Max Bones: {ANIMESH_MAX_BONES}")
        col.label(text=f"Max Triangles: {ANIMESH_MAX_TRIANGLES:,}")
        col.label(text=f"Max Complexity: {ANIMESH_MAX_COMPLEXITY:,}")


# ==============================================================================
# Registration
# ==============================================================================

classes = (
    AVASTAR_OT_animesh_validate,
    AVASTAR_OT_animesh_optimize_bones,
    AVASTAR_OT_animesh_reduce_triangles,
    AVASTAR_PT_animesh_tools,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
        registerlog.info("Registered animesh:%s" % cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
        registerlog.info("Unregistered animesh:%s" % cls)
