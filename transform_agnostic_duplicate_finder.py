bl_info = {
    "name": "Transform Agnostic Duplicate Finder",
    "author": "ChatGPT",
    "version": (1, 3),
    "blender": (3, 0, 0),
    "category": "Object",
}

import bpy
import hashlib
from collections import defaultdict
from mathutils import Vector


# -----------------------------
# 🔧 Normalize Geometry (ignore transform)
# -----------------------------
def normalized_geo_hash(obj, depsgraph):
    eval_obj = obj.evaluated_get(depsgraph)
    me = eval_obj.to_mesh()

    if not me or len(me.vertices) == 0:
        return None

    coords = [v.co.copy() for v in me.vertices]

    # 🔹 Center (remove location)
    center = sum(coords, Vector()) / len(coords)
    coords = [v - center for v in coords]

    # 🔹 Normalize scale
    max_len = max(v.length for v in coords)
    if max_len > 0:
        coords = [v / max_len for v in coords]

    # 🔹 Sort → ignore vertex order
    coords_sorted = sorted(
        [(round(v.x, 4), round(v.y, 4), round(v.z, 4)) for v in coords]
    )

    h = hashlib.md5(str(coords_sorted).encode()).hexdigest()

    eval_obj.to_mesh_clear()
    return h


# -----------------------------
# 🔍 Signature
# -----------------------------
def mesh_signature(obj, depsgraph, use_geo=False):
    me = obj.data
    if not me:
        return None

    verts = len(me.vertices)
    edges = len(me.edges)
    faces = len(me.polygons)

    mats = tuple(sorted([
        slot.material.name if slot.material else "None"
        for slot in obj.material_slots
    ]))

    if use_geo:
        ghash = normalized_geo_hash(obj, depsgraph)
    else:
        ghash = None

    return (verts, edges, faces, mats, ghash)


# -----------------------------
# 🔎 Find
# -----------------------------
class OBJECT_OT_find_duplicates(bpy.types.Operator):
    bl_idname = "object.transform_find_duplicates"
    bl_label = "Find Duplicate Meshes (Transform Safe)"

    use_geo: bpy.props.BoolProperty(
        name="Strict (Geometry)",
        default=True
    )

    def execute(self, context):
        depsgraph = context.evaluated_depsgraph_get()
        groups = defaultdict(list)

        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                sig = mesh_signature(obj, depsgraph, self.use_geo)
                if sig:
                    groups[sig].append(obj)

        bpy.ops.object.select_all(action='DESELECT')

        valid = [g for g in groups.values() if len(g) > 1]

        for g in valid:
            for obj in g:
                obj.select_set(True)

        self.report({'INFO'}, f"{len(valid)} groups found")
        return {'FINISHED'}


# -----------------------------
# 🔗 Link
# -----------------------------
class OBJECT_OT_link_duplicates(bpy.types.Operator):
    bl_idname = "object.transform_link_duplicates"
    bl_label = "Link Duplicate Mesh Data (Transform Safe)"

    use_geo: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        depsgraph = context.evaluated_depsgraph_get()
        groups = defaultdict(list)

        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                sig = mesh_signature(obj, depsgraph, self.use_geo)
                if sig:
                    groups[sig].append(obj)

        linked = 0

        for g in groups.values():
            if len(g) > 1:
                master = g[0]
                for obj in g[1:]:
                    obj.data = master.data
                    linked += 1

        self.report({'INFO'}, f"Linked {linked} objects")
        return {'FINISHED'}


# -----------------------------
# 🧹 Cleanup
# -----------------------------
class OBJECT_OT_cleanup(bpy.types.Operator):
    bl_idname = "object.transform_cleanup"
    bl_label = "Clean Orphan Data"

    def execute(self, context):
        bpy.ops.outliner.orphans_purge(do_recursive=True)
        return {'FINISHED'}


# -----------------------------
# UI
# -----------------------------
class VIEW3D_PT_transform_duplicate(bpy.types.Panel):
    bl_label = "Transform Duplicate Finder"
    bl_idname = "VIEW3D_PT_transform_duplicate"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout

        layout.label(text="Find:")
        op = layout.operator("object.transform_find_duplicates")
        op.use_geo = True

        op = layout.operator("object.transform_find_duplicates", text="Find Fast")
        op.use_geo = False

        layout.separator()

        layout.label(text="Link:")
        op = layout.operator("object.transform_link_duplicates")
        op.use_geo = True

        op = layout.operator("object.transform_link_duplicates", text="Link Fast")
        op.use_geo = False

        layout.separator()
        layout.operator("object.transform_cleanup")


# -----------------------------
# Register
# -----------------------------
classes = (
    OBJECT_OT_find_duplicates,
    OBJECT_OT_link_duplicates,
    OBJECT_OT_cleanup,
    VIEW3D_PT_transform_duplicate,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()