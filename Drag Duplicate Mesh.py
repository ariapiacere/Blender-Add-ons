bl_info = {
    "name": "Drag Duplicate Mesh",
    "author": "ChatGPT",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D",
    "description": "Duplicate mesh by dragging middle mouse up/down",
    "category": "Object",
}

import bpy

class OBJECT_OT_drag_duplicate(bpy.types.Operator):
    bl_idname = "object.drag_duplicate"
    bl_label = "Drag Duplicate Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            delta = event.mouse_y - self.start_mouse_y
            new_count = max(1, int(delta / 20))  # sensitivity

            if new_count != self.count:
                self.count = new_count
                self.update_duplicates(context)

        elif event.type == 'MIDDLEMOUSE' and event.value == 'RELEASE':
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cleanup(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def update_duplicates(self, context):
        # ลบของเก่า
        for obj in self.duplicates:
            bpy.data.objects.remove(obj, do_unlink=True)
        self.duplicates.clear()

        # สร้างใหม่
        for i in range(self.count):
            dup = self.original.copy()
            dup.data = self.original.data.copy()
            dup.location.x += (i + 1) * 2
            context.collection.objects.link(dup)
            self.duplicates.append(dup)

    def cleanup(self, context):
        for obj in self.duplicates:
            bpy.data.objects.remove(obj, do_unlink=True)

    def invoke(self, context, event):
        if context.object is None:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}

        self.original = context.object
        self.start_mouse_y = event.mouse_y
        self.count = 1
        self.duplicates = []

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


def menu_func(self, context):
    self.layout.operator(OBJECT_OT_drag_duplicate.bl_idname)


def register():
    bpy.utils.register_class(OBJECT_OT_drag_duplicate)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_drag_duplicate)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()