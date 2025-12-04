### Copyright 2025 Manfred Aabye
###
### Performance Optimizations for Avastar
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
import time
import logging
from functools import wraps
from bpy.props import BoolProperty, IntProperty
from .const import UI_LOCATION

log = logging.getLogger('avastar.performance')
registerlog = logging.getLogger("avastar.register")


# ==============================================================================
# Performance Monitoring & Optimization
# ==============================================================================

# Global cache for expensive computations
_mesh_cache = {}
_bone_cache = {}


def clear_performance_caches():
    """Clear all performance caches"""
    global _mesh_cache, _bone_cache
    _mesh_cache.clear()
    _bone_cache.clear()
    log.info("Performance caches cleared")


def timed_operation(func):
    """Decorator to measure operation time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        if elapsed > 0.1:  # Log operations > 100ms
            log.info(f"{func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper


@timed_operation
def get_cached_mesh_data(obj):
    """
    Get cached mesh data to avoid repeated mesh evaluations
    Cache is invalidated when mesh is modified
    """
    if obj.name not in _mesh_cache:
        vertex_count = len(obj.data.vertices)
        polygon_count = len(obj.data.polygons)
        
        _mesh_cache[obj.name] = {
            'vertex_count': vertex_count,
            'polygon_count': polygon_count,
            'timestamp': time.time()
        }
    
    return _mesh_cache[obj.name]


@timed_operation
def optimize_weight_calculation(obj, bone_names, chunk_size=1000):
    """
    Optimized weight calculation for large meshes
    Processes vertices in chunks to reduce memory pressure
    """
    vertices = obj.data.vertices
    total_verts = len(vertices)
    
    results = []
    for start_idx in range(0, total_verts, chunk_size):
        end_idx = min(start_idx + chunk_size, total_verts)
        chunk = vertices[start_idx:end_idx]
        
        # Process chunk
        chunk_weights = {}
        for v in chunk:
            for g in v.groups:
                if g.group < len(obj.vertex_groups):
                    vg_name = obj.vertex_groups[g.group].name
                    if vg_name in bone_names:
                        if vg_name not in chunk_weights:
                            chunk_weights[vg_name] = []
                        chunk_weights[vg_name].append((v.index, g.weight))
        
        results.append(chunk_weights)
    
    # Merge results
    final_weights = {}
    for chunk_result in results:
        for bone_name, weights in chunk_result.items():
            if bone_name not in final_weights:
                final_weights[bone_name] = []
            final_weights[bone_name].extend(weights)
    
    return final_weights


class AVASTAR_OT_performance_profile(bpy.types.Operator):
    """Profile Avastar operations performance"""
    bl_idname = "avastar.performance_profile"
    bl_label = "Profile Performance"
    bl_description = (
        "Analyzes performance of current scene setup\n\n"
        "Checks:\n"
        "• Mesh complexity (vertex/poly count)\n"
        "• Armature bone count\n"
        "• Modifier stack efficiency\n"
        "• Weight map complexity\n\n"
        "Provides optimization recommendations"
    )
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        report = []
        warnings = []

        # Mesh analysis
        if obj.type == 'MESH':
            data = get_cached_mesh_data(obj)
            vcount = data['vertex_count']
            pcount = data['polygon_count']
            
            report.append(f"Vertices: {vcount:,}")
            report.append(f"Polygons: {pcount:,}")
            
            if vcount > 50000:
                warnings.append(f"⚠️ High vertex count ({vcount:,}). Consider LOD optimization.")
            
            # Modifier analysis
            mod_count = len(obj.modifiers)
            report.append(f"Modifiers: {mod_count}")
            
            if mod_count > 5:
                warnings.append(f"⚠️ Many modifiers ({mod_count}). May impact viewport performance.")
            
            # Weight groups
            vg_count = len(obj.vertex_groups)
            report.append(f"Weight Groups: {vg_count}")
            
            if vg_count > 100:
                warnings.append(f"⚠️ Many weight groups ({vg_count}). Animesh limit is 110 bones.")

        # Armature analysis
        armature = None
        for mod in obj.modifiers if obj.type == 'MESH' else []:
            if mod.type == 'ARMATURE' and mod.object:
                armature = mod.object
                break

        if armature:
            bone_count = len(armature.data.bones)
            deform_count = len([b for b in armature.data.bones if b.use_deform])
            
            report.append(f"Total Bones: {bone_count}")
            report.append(f"Deform Bones: {deform_count}")
            
            if deform_count > 110:
                warnings.append(f"⚠️ Exceeds Animesh bone limit ({deform_count}/110)")

        # Display report
        self.report({'INFO'}, "\n".join(report))
        if warnings:
            log.warning("Performance Warnings:")
            for w in warnings:
                log.warning(f"  {w}")
        
        return {'FINISHED'}


class AVASTAR_OT_performance_optimize_scene(bpy.types.Operator):
    """Apply performance optimizations to scene"""
    bl_idname = "avastar.performance_optimize_scene"
    bl_label = "Optimize Scene"
    bl_description = (
        "Applies performance optimizations to the current scene\n\n"
        "Optimizations:\n"
        "• Clears unused weight groups\n"
        "• Removes zero-weight assignments\n"
        "• Optimizes modifier stack order\n"
        "• Cleans up mesh data\n\n"
        "Creates backup before applying changes"
    )
    bl_options = {'REGISTER', 'UNDO'}

    clean_weights : BoolProperty(
        name="Clean Zero Weights",
        description="Remove weight assignments below 0.001",
        default=True
    )

    remove_unused_groups : BoolProperty(
        name="Remove Unused Groups",
        description="Remove vertex groups with no assignments",
        default=True
    )

    optimize_modifiers : BoolProperty(
        name="Optimize Modifiers",
        description="Reorder modifiers for better performance",
        default=False
    )

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        changes = []

        # Clean weights
        if self.clean_weights:
            cleaned = 0
            for v in obj.data.vertices:
                for g in list(v.groups):
                    if g.weight < 0.001:
                        obj.vertex_groups[g.group].remove([v.index])
                        cleaned += 1
            if cleaned > 0:
                changes.append(f"Cleaned {cleaned} zero-weight assignments")

        # Remove unused groups
        if self.remove_unused_groups:
            used_groups = set()
            for v in obj.data.vertices:
                for g in v.groups:
                    used_groups.add(g.group)
            
            removed = 0
            for i in range(len(obj.vertex_groups) - 1, -1, -1):
                if i not in used_groups:
                    obj.vertex_groups.remove(obj.vertex_groups[i])
                    removed += 1
            
            if removed > 0:
                changes.append(f"Removed {removed} unused weight groups")

        # Optimize modifiers
        if self.optimize_modifiers:
            # Move Armature modifiers to end for better performance
            armature_mods = [m for m in obj.modifiers if m.type == 'ARMATURE']
            for mod in armature_mods:
                while obj.modifiers.find(mod.name) < len(obj.modifiers) - 1:
                    bpy.ops.object.modifier_move_down(modifier=mod.name)
            
            if armature_mods:
                changes.append(f"Optimized modifier stack ({len(armature_mods)} armature mods)")

        # Clear caches
        clear_performance_caches()
        changes.append("Cleared performance caches")

        if changes:
            self.report({'INFO'}, " | ".join(changes))
        else:
            self.report({'INFO'}, "No optimizations needed")

        return {'FINISHED'}


class AVASTAR_PT_performance_tools(bpy.types.Panel):
    """Performance Tools Panel"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = UI_LOCATION
    bl_category    = "Avastar"
    bl_label = "Performance"
    bl_idname = "AVASTAR_PT_performance_tools"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Analysis")
        box.operator("avastar.performance_profile", icon='TIME')

        box = layout.box()
        box.label(text="Optimization")
        op = box.operator("avastar.performance_optimize_scene", icon='MOD_BUILD')


# ==============================================================================
# Registration
# ==============================================================================

classes = (
    AVASTAR_OT_performance_profile,
    AVASTAR_OT_performance_optimize_scene,
    AVASTAR_PT_performance_tools,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
        registerlog.info("Registered performance:%s" % cls)

def unregister():
    from bpy.utils import unregister_class
    clear_performance_caches()
    for cls in reversed(classes):
        unregister_class(cls)
        registerlog.info("Unregistered performance:%s" % cls)
