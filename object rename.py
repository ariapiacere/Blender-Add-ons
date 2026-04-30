bl_info = {
    "name": "Rename Data to Object Name",
    "author": "ChatGPT",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Object",
    "description": "Rename object data to match object name",
    "category": "Object",
}

import bpy

class OBJECT_OT_rename_data_to_object(bpy.types.Operator):
    bl_idname = "object.rename_data_to_object"
    bl_label = "Rename Data to Object Name"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.data:
                obj.data.name = obj.name
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(OBJECT_OT_rename_data_to_object.bl_idname)


def register():
    bpy.utils.register_class(OBJECT_OT_rename_data_to_object)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_rename_data_to_object)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()