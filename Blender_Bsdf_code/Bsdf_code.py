# Blender Python script to create materials and lights for GLB files
# This script creates a BRDF material and a Translucent BSDF material,
# adds operators to apply these materials, and places lights around the selected object.
# This script is made to be run in Blender's scripting environment.
# It assumes that the GLB file has vertex colors named "Color" for the materials to work correctly.
# this script is designed to be run in Blender 3.0 or later.


# Pay attention each time you run this script, it will clear the scene of lights, materials, and operators.
# But the buttons will remain in the UI until you manually remove them or run the cleanup function.

import bpy
from mathutils import Vector

# Create a BRDF material using vertex color input
def make_brdf_material():
    mat = bpy.data.materials.new(name="Custom_BRDF")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    color_input = nodes.new(type="ShaderNodeVertexColor")
    color_input.layer_name = "Color"  # Must match GLB vertex color name

    shader = nodes.get("Principled BSDF")
    mat.node_tree.links.new(color_input.outputs[0], shader.inputs['Base Color'])

    shader.inputs['Metallic'].default_value = 0.5 # Adjust metallic value as needed feel free to change
    shader.inputs['Roughness'].default_value = 0.1 # Adjust roughness value as needed feel free to change

    return mat

# Create a material using Translucent BSDF with vertex color
def make_translucent_material():
    mat = bpy.data.materials.new(name="Custom_Translucent") 
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    color_input = nodes.new(type="ShaderNodeVertexColor")
    color_input.layer_name = "Color"

    translucent_node = nodes.new(type="ShaderNodeBsdfTranslucent")
    mat.node_tree.links.new(color_input.outputs[0], translucent_node.inputs['Color'])

    output = nodes.get("Material Output")
    mat.node_tree.links.new(translucent_node.outputs[0], output.inputs[0])

    mat.blend_method = 'BLEND'  # Needed for Eevee rendering

    return mat

# Add lights around the selected object
def place_lights(x, y, z):
    obj = bpy.context.active_object
    if obj:
        base = obj.location
        light_positions = [
            base + Vector((x, y, z)),
        ]

        for i, pos in enumerate(light_positions):
            bpy.ops.object.light_add(type='POINT', location=pos)
            light = bpy.context.object
            light.name = f"Custom_Light_{i+1}"
            light.data.energy = 1000  # Adjust energy as needed

# Clear scene: remove lights, materials, operators
def cleanup_scene():
    for obj in bpy.context.scene.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)

    for cls in [ApplyBRDFOperator, ApplyTranslucentOperator, AddCustomLights]:
        if hasattr(bpy.types, cls.__name__):
            bpy.utils.unregister_class(cls)

    if "draw_ui" in locals():
        bpy.types.VIEW3D_PT_view3d_properties.remove(draw_ui)

# Operator to assign BRDF material
class ApplyBRDFOperator(bpy.types.Operator):
    bl_idname = "object.assign_brdf"
    bl_label = "Assign BRDF Material"

    def execute(self, context):
        obj = bpy.context.active_object
        if obj and obj.type == 'MESH':
            obj.data.materials.clear()
            mat = make_brdf_material()
            obj.data.materials.append(mat)
        return {'FINISHED'}

# Operator to assign Translucent BSDF material 
class ApplyTranslucentOperator(bpy.types.Operator):
    bl_idname = "object.assign_translucent"
    bl_label = "Assign Translucent Material"

    def execute(self, context):
        obj = bpy.context.active_object
        if obj and obj.type == 'MESH':
            obj.data.materials.clear()
            mat = make_translucent_material()
            obj.data.materials.append(mat)
        return {'FINISHED'}

# Operator to place lights
class AddCustomLights(bpy.types.Operator):
    bl_idname = "object.place_custom_lights"
    bl_label = "Place Lights Around"

    def execute(self, context):
        place_lights(4.07, 1.00, 5.90) #Base position for lights in blender feel free to change
        return {'FINISHED'}

# Add custom buttons to the UI panel 
def draw_ui(self, context):
    layout = self.layout
    layout.operator("object.assign_brdf", text="Apply BRDF")
    layout.operator("object.assign_translucent", text="Apply Translucent")
    layout.operator("object.place_custom_lights", text="Place Lights")

# Register everything
def register():
    cleanup_scene()
    bpy.utils.register_class(ApplyBRDFOperator)
    bpy.utils.register_class(ApplyTranslucentOperator)
    bpy.utils.register_class(AddCustomLights)
    bpy.types.VIEW3D_PT_view3d_properties.append(draw_ui)

def unregister():
    bpy.utils.unregister_class(ApplyBRDFOperator)
    bpy.utils.unregister_class(ApplyTranslucentOperator)
    bpy.utils.unregister_class(AddCustomLights)
    bpy.types.VIEW3D_PT_view3d_properties.remove(draw_ui)

if __name__ == "__main__":
    register()
