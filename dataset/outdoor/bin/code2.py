import bpy
import math

def create_bin_material(material_type="plastic", color=(0.2, 0.3, 0.8, 1.0)):
    """
    Create a material for the bin
    
    Parameters:
    - material_type: "plastic", "metal", "rusty_metal", "wood"
    - color: RGBA tuple for base color
    """
    
    mat = bpy.data.materials.new(name=f"Bin_{material_type}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create output node
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (400, 0)
    
    if material_type == "plastic":
        # Create Principled BSDF for plastic
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Plastic settings
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = 0.0
        bsdf.inputs['Roughness'].default_value = 0.4
        bsdf.inputs['Specular IOR Level'].default_value = 0.5
        
        # Connect
        links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])
        
    elif material_type == "metal":
        # Create Principled BSDF for metal
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Metal settings
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = 1.0
        bsdf.inputs['Roughness'].default_value = 0.3
        
        # Connect
        links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])
        
    elif material_type == "rusty_metal":
        # Create Principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (200, 0)
        
        # Noise texture for rust
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-600, 0)
        noise.inputs['Scale'].default_value = 15.0
        noise.inputs['Detail'].default_value = 5.0
        
        # Color ramp for rust pattern
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-400, 0)
        color_ramp.color_ramp.elements[0].color = (0.3, 0.15, 0.05, 1.0)  # Dark rust
        color_ramp.color_ramp.elements[1].color = (0.6, 0.3, 0.1, 1.0)   # Light rust
        
        # Mix with metal color
        mix_rgb = nodes.new(type='ShaderNodeMix')
        mix_rgb.data_type = 'RGBA'
        mix_rgb.location = (-200, 100)
        mix_rgb.inputs[6].default_value = color  # Metal color
        
        # Roughness variation
        rough_ramp = nodes.new(type='ShaderNodeValToRGB')
        rough_ramp.location = (-200, -200)
        rough_ramp.color_ramp.elements[0].position = 0.3
        rough_ramp.color_ramp.elements[1].position = 0.8
        
        # Connections
        links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], mix_rgb.inputs[0])  # Factor
        links.new(color_ramp.outputs['Color'], mix_rgb.inputs[7])  # Color2
        links.new(mix_rgb.outputs[2], bsdf.inputs['Base Color'])
        
        links.new(noise.outputs['Fac'], rough_ramp.inputs['Fac'])
        links.new(rough_ramp.outputs['Color'], bsdf.inputs['Roughness'])
        
        bsdf.inputs['Metallic'].default_value = 0.8
        
        links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])
        
    elif material_type == "wood":
        # Create Principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (200, 0)
        
        # Wave texture for wood grain
        wave = nodes.new(type='ShaderNodeTexWave')
        wave.location = (-600, 0)
        wave.wave_type = 'BANDS'
        wave.inputs['Scale'].default_value = 5.0
        wave.inputs['Distortion'].default_value = 2.0
        
        # Color ramp for wood colors
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-400, 0)
        color_ramp.color_ramp.elements[0].color = (0.3, 0.15, 0.05, 1.0)  # Dark wood
        color_ramp.color_ramp.elements[1].color = (0.5, 0.3, 0.15, 1.0)  # Light wood
        
        # Connections
        links.new(wave.outputs['Color'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
        
        bsdf.inputs['Metallic'].default_value = 0.0
        bsdf.inputs['Roughness'].default_value = 0.6
        
        links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])
    
    return mat


def create_rectangular_bin(
    width=0.4,
    depth=0.3,
    height=0.6,
    corner_radius=0.05,
    wall_thickness=0.02,
    bottom_thickness=0.02,
    handle_width=0.08,
    handle_depth=0.03,
    handle_height=0.12,
    rim_height=0.03,
    segments=16,
    material_type="plastic",
    color=(0.7, 0.2, 0.2, 1.0)
):
    """
    Create a parametric rectangular bin with rounded corners
    
    Parameters:
    - width: width (X dimension) of the bin
    - depth: depth (Y dimension) of the bin
    - height: height of the bin
    - corner_radius: radius of rounded corners
    - wall_thickness: thickness of the walls
    - bottom_thickness: thickness of the bottom
    - handle_width: width of the handles
    - handle_depth: how far handles protrude
    - handle_height: vertical size of handles
    - rim_height: height of the top rim
    - segments: smoothness of rounded corners
    - material_type: "plastic", "metal", "rusty_metal", "wood"
    - color: RGBA tuple for base color
    """
    
    # Create collection for the bin
    bin_collection = bpy.data.collections.new("RectangularBin")
    bpy.context.scene.collection.children.link(bin_collection)
    
    # 1. Create outer rounded box
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, height/2)
    )
    outer_box = bpy.context.active_object
    outer_box.name = "Bin_Outer"
    outer_box.scale = (width, depth, height)
    
    # Apply scale
    bpy.context.view_layer.objects.active = outer_box
    bpy.ops.object.transform_apply(scale=True)
    
    # Add bevel modifier for rounded corners
    bevel_mod = outer_box.modifiers.new(name="RoundedCorners", type='BEVEL')
    bevel_mod.width = corner_radius
    bevel_mod.segments = segments
    bevel_mod.limit_method = 'ANGLE'
    
    # Move to collection
    for coll in outer_box.users_collection:
        coll.objects.unlink(outer_box)
    bin_collection.objects.link(outer_box)
    
    # 2. Create inner box (for hollow interior)
    inner_width = width - 2 * wall_thickness
    inner_depth = depth - 2 * wall_thickness
    inner_height = height - bottom_thickness + 0.01
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, height/2 + bottom_thickness)
    )
    inner_box = bpy.context.active_object
    inner_box.name = "Bin_Inner"
    inner_box.scale = (inner_width, inner_depth, inner_height)
    
    # Apply scale
    bpy.context.view_layer.objects.active = inner_box
    bpy.ops.object.transform_apply(scale=True)
    
    # Add bevel for inner rounded corners
    inner_bevel = inner_box.modifiers.new(name="InnerRounded", type='BEVEL')
    inner_bevel.width = corner_radius - wall_thickness if corner_radius > wall_thickness else corner_radius * 0.5
    inner_bevel.segments = segments
    inner_bevel.limit_method = 'ANGLE'
    
    # Move to collection
    for coll in inner_box.users_collection:
        coll.objects.unlink(inner_box)
    bin_collection.objects.link(inner_box)
    
    # 3. Boolean modifier to make it hollow
    bpy.context.view_layer.objects.active = outer_box
    bool_mod = outer_box.modifiers.new(name="Hollow", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = inner_box
    
    # Apply modifiers
    bpy.ops.object.select_all(action='DESELECT')
    outer_box.select_set(True)
    bpy.context.view_layer.objects.active = outer_box
    bpy.ops.object.modifier_apply(modifier="RoundedCorners")
    bpy.ops.object.modifier_apply(modifier="Hollow")
    
    # Delete inner box
    bpy.ops.object.select_all(action='DESELECT')
    inner_box.select_set(True)
    bpy.ops.object.delete()
    
    # 4. Create rim around the top
    rim_outer = width + 0.02
    rim_depth_outer = depth + 0.02
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, height - rim_height/2)
    )
    rim = bpy.context.active_object
    rim.name = "Bin_Rim"
    rim.scale = (rim_outer, rim_depth_outer, rim_height)
    
    # Apply scale
    bpy.context.view_layer.objects.active = rim
    bpy.ops.object.transform_apply(scale=True)
    
    # Bevel the rim
    rim_bevel = rim.modifiers.new(name="RimBevel", type='BEVEL')
    rim_bevel.width = corner_radius * 1.2
    rim_bevel.segments = segments
    
    bpy.ops.object.modifier_apply(modifier="RimBevel")
    
    # Move to collection
    for coll in rim.users_collection:
        coll.objects.unlink(rim)
    bin_collection.objects.link(rim)
    
    # 5. Create handles on the short sides (2 handles)
    for i, y_pos in enumerate([-depth/2 - handle_depth/2, depth/2 + handle_depth/2]):
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(0, y_pos, height - handle_height/2 - 0.05)
        )
        handle = bpy.context.active_object
        handle.name = f"Bin_Handle_{i+1}"
        handle.scale = (handle_width, handle_depth, handle_height)
        
        # Apply scale
        bpy.context.view_layer.objects.active = handle
        bpy.ops.object.transform_apply(scale=True)
        
        # Add bevel to handles
        handle_bevel = handle.modifiers.new(name="HandleBevel", type='BEVEL')
        handle_bevel.width = 0.01
        handle_bevel.segments = 4
        bpy.ops.object.modifier_apply(modifier="HandleBevel")
        
        # Move to collection
        for coll in handle.users_collection:
            coll.objects.unlink(handle)
        bin_collection.objects.link(handle)
    
    # 6. Join all parts
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bin_collection.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = outer_box
    bpy.ops.object.join()
    bin_obj = bpy.context.active_object
    bin_obj.name = "RectangularBin"
    
    # 7. Create and apply material
    mat = create_bin_material(material_type, color)
    
    if bin_obj.data.materials:
        bin_obj.data.materials[0] = mat
    else:
        bin_obj.data.materials.append(mat)
    
    # Smooth shading
    bpy.ops.object.shade_smooth()
    
    print(f"Rectangular bin created with {material_type} material")
    return bin_obj


# Clear existing objects (optional)
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete()

# Example 1: Red plastic rectangular bin
bin_rect_plastic = create_rectangular_bin(
    material_type="plastic",
    color=(0.7, 0.2, 0.2, 1.0)  # Red
)

# Example 2: Metal rectangular bin
# bin_rect_metal = create_rectangular_bin(
#     width=0.5,
#     depth=0.35,
#     height=0.7,
#     material_type="metal",
#     color=(0.8, 0.8, 0.85, 1.0)
# )

# Example 3: Green recycling bin
# bin_rect_recycle = create_rectangular_bin(
#     width=0.45,
#     depth=0.3,
#     height=0.65,
#     material_type="plastic",
#     color=(0.1, 0.7, 0.2, 1.0)  # Green
# )

# Example 4: Rusty metal bin
# bin_rect_rusty = create_rectangular_bin(
#     width=0.4,
#     depth=0.35,
#     height=0.6,
#     material_type="rusty_metal",
#     color=(0.5, 0.5, 0.55, 1.0)
# )