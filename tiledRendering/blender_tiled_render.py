import bpy, os, math

bl_info = {
    "name": "Tiling Renderer",
    "author": "SITN - sitn.ne.ch",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "location": "Render Properties > Tiling",
    "description": "Render the scene in tiles",
    "category": "Render",
}

ACTIVE_TILING_OPERATOR = None

def redraw_all():
    [area.tag_redraw() for area in bpy.context.screen.areas]
    bpy.ops.wm.redraw_timer(type='DRAW_WIN', iterations=1)
    
class TilingRenderProperties(bpy.types.PropertyGroup):
    tile_size_x: bpy.props.IntProperty(name="Tile Size X", default=1024, min=100)
    tile_size_y: bpy.props.IntProperty(name="Tile Size Y", default=1024, min=100)
    start_tile_id: bpy.props.IntProperty(name="Start Tile ID", default=0, min=0)
    end_tile_id: bpy.props.IntProperty(name="End Tile ID", default=-1, min=-1)
    overlap: bpy.props.IntProperty(name="Overlap", default=0, min=0)
    output_dir: bpy.props.StringProperty(name="Output Directory", subtype='DIR_PATH', default="C:/tmp")
    status_text: bpy.props.StringProperty(name="Status Text", default="Render")

class RENDER_OT_tiled_render_modal(bpy.types.Operator):
    bl_idname = "render.tiled_render_modal"
    bl_label = "Render Tiled"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global ACTIVE_TILING_OPERATOR
        ACTIVE_TILING_OPERATOR = self
        self.props = context.scene.tiling_render_props
        self.render = context.scene.render
        self.res_x, self.res_y = (self.render.resolution_x, self.render.resolution_y)
        self.tile_x, self.tile_y, self.overlap = self.props.tile_size_x, self.props.tile_size_y, self.props.overlap
        self.output_path = bpy.path.abspath(self.props.output_dir)
        self.tile_index = self.props.start_tile_id
        self.num_tiles = (math.ceil(self.res_x/self.tile_x), math.ceil(self.res_y/self.tile_y))
        self.total_tiles = self.num_tiles[0] * self.num_tiles[1]
        self.end_tile_id = self.props.end_tile_id if self.props.end_tile_id >= 0 and self.props.end_tile_id < self.total_tiles - 1 else self.total_tiles - 1
        self.tiles_done = 0
        self.timer = context.window_manager.event_timer_add(0.1, window=context.window)
        self.render.use_border = self.render.use_crop_to_border = True
        self.props.status_text = "Rendering ..."
        context.window_manager.modal_handler_add(self)
        os.makedirs(self.output_path, exist_ok=True)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        global ACTIVE_TILING_OPERATOR
        if event.type == 'TIMER':
            context.window_manager.event_timer_remove(self.timer)
            if self.tile_index > self.end_tile_id or not ACTIVE_TILING_OPERATOR:
                return self.finish(context)

            x = self.tile_index % self.num_tiles[0]
            y = self.tile_index // self.num_tiles[0]

            self.render.border_min_x = max((x       * self.tile_x - self.overlap) / self.res_x, 0) 
            self.render.border_max_x = min(((x + 1) * self.tile_x + self.overlap) / self.res_x, 1)
            self.render.border_min_y = max((y       * self.tile_y - self.overlap) / self.res_y, 0) 
            self.render.border_max_y = min(((y + 1) * self.tile_y + self.overlap) / self.res_y, 1) 
            self.render.filepath = os.path.join(self.output_path, f"tile_{self.tile_index}_{x}_{y}.png")
            bpy.ops.render.render(write_still=True, use_viewport=False)
            self.tiles_done += 1
            self.tile_index += 1
            self.props.status_text = f"Rendering... ({self.tiles_done}/{self.end_tile_id - self.props.start_tile_id + 1})"
            redraw_all()
            self.timer = context.window_manager.event_timer_add(0.1, window=context.window)
        return {'PASS_THROUGH'}

    def finish(self, context):
        global ACTIVE_TILING_OPERATOR
        self.render.use_border = self.render.use_crop_to_border = False
        self.render.filepath = "//"
        self.props.status_text = "Render"
        if ACTIVE_TILING_OPERATOR:
            ACTIVE_TILING_OPERATOR = None
            self.report({'INFO'}, "Tiled rendering complete")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Tiling render canceled")
            return {'CANCELLED'}

class CANCEL_OT_tiling_render_cancel(bpy.types.Operator):
    bl_idname = "render.tiled_render_cancel"
    bl_label = "Cancel Render"
    def execute(self, context):
        global ACTIVE_TILING_OPERATOR
        ACTIVE_TILING_OPERATOR = None
        return {'FINISHED'}

class RENDER_PT_tiling_panel(bpy.types.Panel):
    bl_label = "Tiling"
    bl_idname = "RENDER_PT_tiling_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    def draw(self, context):
        props = context.scene.tiling_render_props
        layout = self.layout
        for prop in ("tile_size_x", "tile_size_y", "start_tile_id", "end_tile_id", "overlap", "output_dir"):
            layout.prop(props, prop)
        layout.operator("render.tiled_render_modal", text=props.status_text, icon="RENDER_STILL")
        layout.operator("render.tiled_render_cancel", icon="CANCEL")

classes = (
    TilingRenderProperties,
    RENDER_OT_tiled_render_modal,
    CANCEL_OT_tiling_render_cancel,
    RENDER_PT_tiling_panel,
)

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.tiling_render_props = bpy.props.PointerProperty(type=TilingRenderProperties)

def unregister():
    for cls in reversed(classes): bpy.utils.unregister_class(cls)
    del bpy.types.Scene.tiling_render_props

if __name__ == "__main__":
    register()