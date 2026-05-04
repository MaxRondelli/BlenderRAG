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


def create_stackable_bin(
    width=0.35,
    depth=0.25,
    height=0.2,
    wall_thickness=0.015,
    bottom_thickness=0.01,
    lip_height=0.015,
    lip_inset=0.01,
    handle_cutout_width=0.12,
    handle_cutout_height=0.04,
    stacking_nub_radius=0.008,
    corner_radius=0.02,
    material_type="plastic",
    color=(0.3, 0.5, 0.7, 1.0)
):
    """
    Create a stackable modular storage bin
    
    Parameters:
    - width: width of the bin
    - depth: depth of the bin
    - height: height of the bin
    - wall_thickness: thickness of walls
    - bottom_thickness: thickness of bottom
    - lip_height: height of the stacking lip
    - lip_inset: how much the lip is inset for stacking
    - handle_cutout_width: width of handle cutout
    - handle_cutout_height: height of handle cutout
    - stacking_nub_radius: radius of corner nubs for stability
    - corner_radius: radius of rounded corners
    - material_type: material type
    - color: RGBA tuple for color
    """
    
    # Create collection
    bin_collection = bpy.data.collections.new("StackableBin")
    bpy.context.scene.collection.children.link(bin_collection)
    
    # Create material
    mat = create_bin_material(material_type, color)
    
    # 1. Create outer box
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
    
    # Add bevel for rounded corners
    outer_bevel = outer_box.modifiers.new(name="OuterBevel", type='BEVEL')
    outer_bevel.width = corner_radius
    outer_bevel.segments = 4
    outer_bevel.limit_method = 'ANGLE'
    
    # Move to collection
    for coll in outer_box.users_collection:
        coll.objects.unlink(outer_box)
    bin_collection.objects.link(outer_box)
    
    # 2. Create inner box for hollow interior
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
    
    # Add bevel for inner corners
    inner_bevel = inner_box.modifiers.new(name="InnerBevel", type='BEVEL')
    inner_bevel.width = corner_radius * 0.7
    inner_bevel.segments = 3
    inner_bevel.limit_method = 'ANGLE'
    
    # Move to collection
    for coll in inner_box.users_collection:
        coll.objects.unlink(inner_box)
    bin_collection.objects.link(inner_box)
    
    # 3. Boolean to hollow out
    bpy.context.view_layer.objects.active = outer_box
    hollow_bool = outer_box.modifiers.new(name="Hollow", type='BOOLEAN')
    hollow_bool.operation = 'DIFFERENCE'
    hollow_bool.object = inner_box
    
    # Apply modifiers
    bpy.ops.object.select_all(action='DESELECT')
    outer_box.select_set(True)
    bpy.context.view_layer.objects.active = outer_box
    bpy.ops.object.modifier_apply(modifier="OuterBevel")
    bpy.ops.object.modifier_apply(modifier="Hollow")
    
    # Delete inner box
    bpy.ops.object.select_all(action='DESELECT')
    inner_box.select_set(True)
    bpy.ops.object.delete()
    
    # Apply material
    if outer_box.data.materials:
        outer_box.data.materials[0] = mat
    else:
        outer_box.data.materials.append(mat)
    
    # 4. Create stacking lip (rim that goes inside when stacked)
    lip_width = width - 2 * lip_inset
    lip_depth = depth - 2 * lip_inset
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, height - lip_height/2)
    )
    lip = bpy.context.active_object
    lip.name = "Bin_StackingLip"
    lip.scale = (lip_width, lip_depth, lip_height)
    
    # Apply scale
    bpy.context.view_layer.objects.active = lip
    bpy.ops.object.transform_apply(scale=True)
    
    # Bevel the lip
    lip_bevel = lip.modifiers.new(name="LipBevel", type='BEVEL')
    lip_bevel.width = corner_radius * 0.5
    lip_bevel.segments = 2
    bpy.ops.object.modifier_apply(modifier="LipBevel")
    
    # Create hollow lip
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, height - lip_height/2)
    )
    lip_inner = bpy.context.active_object
    lip_inner.name = "Bin_LipInner"
    lip_inner.scale = (
        lip_width - 2*wall_thickness,
        lip_depth - 2*wall_thickness,
        lip_height + 0.02
    )
    
    # Apply scale
    bpy.context.view_layer.objects.active = lip_inner
    bpy.ops.object.transform_apply(scale=True)
    
    # Move to collection
    for coll in lip_inner.users_collection:
        coll.objects.unlink(lip_inner)
    bin_collection.objects.link(lip_inner)
    
    # Boolean for lip
    bpy.context.view_layer.objects.active = lip
    lip_bool = lip.modifiers.new(name="LipHollow", type='BOOLEAN')
    lip_bool.operation = 'DIFFERENCE'
    lip_bool.object = lip_inner
    
    bpy.ops.object.select_all(action='DESELECT')
    lip.select_set(True)
    bpy.context.view_layer.objects.active = lip
    bpy.ops.object.modifier_apply(modifier="LipHollow")
    
    # Delete lip inner
    bpy.ops.object.select_all(action='DESELECT')
    lip_inner.select_set(True)
    bpy.ops.object.delete()
    
    # Move to collection and apply material
    for coll in lip.users_collection:
        coll.objects.unlink(lip)
    bin_collection.objects.link(lip)
    
    if lip.data.materials:
        lip.data.materials[0] = mat
    else:
        lip.data.materials.append(mat)
    
    # 5. Create handle cutouts on short sides
    for i, y_mult in enumerate([-1, 1]):
        cutout_y = (depth/2 + wall_thickness/2 + 0.01) * y_mult
        cutout_z = height - handle_cutout_height - 0.05
        
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(0, cutout_y, cutout_z)
        )
        cutout = bpy.context.active_object
        cutout.name = f"Bin_HandleCutout_{i+1}"
        cutout.scale = (handle_cutout_width, wall_thickness + 0.02, handle_cutout_height)
        
        # Apply scale
        bpy.context.view_layer.objects.active = cutout
        bpy.ops.object.transform_apply(scale=True)
        
        # Round the cutout
        cutout_bevel = cutout.modifiers.new(name="CutoutBevel", type='BEVEL')
        cutout_bevel.width = 0.015
        cutout_bevel.segments = 3
        bpy.ops.object.modifier_apply(modifier="CutoutBevel")
        
        # Move to collection
        for coll in cutout.users_collection:
            coll.objects.unlink(cutout)
        bin_collection.objects.link(cutout)
        
        # Boolean to cut out handle
        bpy.context.view_layer.objects.active = outer_box
        handle_bool = outer_box.modifiers.new(name=f"HandleCut_{i+1}", type='BOOLEAN')
        handle_bool.operation = 'DIFFERENCE'
        handle_bool.object = cutout
    
    # Apply handle cutout booleans
    bpy.ops.object.select_all(action='DESELECT')
    outer_box.select_set(True)
    bpy.context.view_layer.objects.active = outer_box
    
    for i in range(2):
        bpy.ops.object.modifier_apply(modifier=f"HandleCut_{i+1}")
    
    # Delete cutout objects
    for obj in list(bin_collection.objects):
        if "HandleCutout" in obj.name:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.ops.object.delete()
    
    # 6. Create stacking nubs on bottom (4 corners)
    nub_offset_x = width/2 - lip_inset - wall_thickness
    nub_offset_y = depth/2 - lip_inset - wall_thickness
    
    for x_mult in [-1, 1]:
        for y_mult in [-1, 1]:
            nub_x = nub_offset_x * x_mult
            nub_y = nub_offset_y * y_mult
            
            bpy.ops.mesh.primitive_cylinder_add(
                radius=stacking_nub_radius,
                depth=0.01,
                vertices=12,
                location=(nub_x, nub_y, 0.005)
            )
            nub = bpy.context.active_object
            nub.name = f"Bin_StackingNub"
            
            # Move to collection and apply material
            for coll in nub.users_collection:
                coll.objects.unlink(nub)
            bin_collection.objects.link(nub)
            
            if nub.data.materials:
                nub.data.materials[0] = mat
            else:
                nub.data.materials.append(mat)
    
    # 7. Create label area (recessed panel on front)
    label_width = width * 0.6
    label_height = 0.08
    label_depth = 0.003
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, depth/2 - wall_thickness/2 - label_depth/2, height * 0.4)
    )
    label_area = bpy.context.active_object
    label_area.name = "Bin_LabelArea"
    label_area.scale = (label_width, label_depth, label_height)
    
    # Apply scale
    bpy.context.view_layer.objects.active = label_area
    bpy.ops.object.transform_apply(scale=True)
    
    # Bevel label area
    label_bevel = label_area.modifiers.new(name="LabelBevel", type='BEVEL')
    label_bevel.width = 0.008
    label_bevel.segments = 2
    bpy.ops.object.modifier_apply(modifier="LabelBevel")
    
    # Move to collection and apply darker material
    for coll in label_area.users_collection:
        coll.objects.unlink(label_area)
    bin_collection.objects.link(label_area)
    
    label_color = (color[0] * 0.7, color[1] * 0.7, color[2] * 0.7, color[3])
    label_mat = create_bin_material(material_type, label_color)
    
    if label_area.data.materials:
        label_area.data.materials[0] = label_mat
    else:
        label_area.data.materials.append(label_mat)
    
    # Smooth shading
    for obj in bin_collection.objects:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
    
    print(f"Stackable bin created with {material_type} material")
    return bin_collection


# Example 1: Blue stackable bin (default)
bin_stackable = create_stackable_bin(
    material_type="plastic",
    color=(0.3, 0.5, 0.7, 1.0)
)

# Example 2: Green storage bin
# bin_stackable_green = create_stackable_bin(
#     width=0.4,
#     depth=0.3,
#     height=0.25,
#     material_type="plastic",
#     color=(0.2, 0.6, 0.3, 1.0)
# )

# Example 3: Gray industrial bin
# bin_stackable_gray = create_stackable_bin(
#     width=0.45,
#     depth=0.35,
#     height=0.22,
#     material_type="plastic",
#     color=(0.4, 0.4, 0.42, 1.0)
# )

# Example 4: Small red organizer
# bin_stackable_red = create_stackable_bin(
#     width=0.28,
#     depth=0.2,
#     height=0.15,
#     material_type="plastic",
#     color=(0.75, 0.2, 0.2, 1.0)
# )