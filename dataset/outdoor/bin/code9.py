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


def create_flip_top_bin(
    radius=0.32,
    height=0.65,
    wall_thickness=0.02,
    bottom_thickness=0.02,
    lid_height=0.12,
    lid_flip_angle=75,  # degrees
    hinge_radius=0.008,
    hinge_width=0.15,
    liner_rim_height=0.03,
    liner_thickness=0.005,
    material_type="plastic",
    body_color=(0.85, 0.85, 0.87, 1.0),
    lid_color=(0.75, 0.75, 0.77, 1.0),
    liner_color=(0.15, 0.15, 0.15, 1.0)
):
    """
    Create a flip-top bin with removable liner
    
    Parameters:
    - radius: radius of the bin
    - height: height of the bin body
    - wall_thickness: thickness of walls
    - bottom_thickness: thickness of bottom
    - lid_height: height of the flip lid
    - lid_flip_angle: angle of lid when open (degrees)
    - hinge_radius: radius of hinge cylinder
    - hinge_width: width of hinge connection
    - liner_rim_height: height of liner rim
    - liner_thickness: thickness of liner walls
    - material_type: material type
    - body_color: color of main body
    - lid_color: color of flip lid
    - liner_color: color of inner liner
    """
    
    # Create collection
    bin_collection = bpy.data.collections.new("FlipTopBin")
    bpy.context.scene.collection.children.link(bin_collection)
    
    # Create materials
    body_mat = create_bin_material(material_type, body_color)
    lid_mat = create_bin_material(material_type, lid_color)
    liner_mat = create_bin_material(material_type, liner_color)
    
    # 1. Create main body (outer cylinder)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=height,
        vertices=32,
        location=(0, 0, height/2)
    )
    outer_body = bpy.context.active_object
    outer_body.name = "Bin_Body_Outer"
    
    # Move to collection
    for coll in outer_body.users_collection:
        coll.objects.unlink(outer_body)
    bin_collection.objects.link(outer_body)
    
    # 2. Create inner cylinder for hollowing
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius - wall_thickness,
        depth=height - bottom_thickness + 0.01,
        vertices=32,
        location=(0, 0, height/2 + bottom_thickness)
    )
    inner_body = bpy.context.active_object
    inner_body.name = "Bin_Body_Inner"
    
    # Move to collection
    for coll in inner_body.users_collection:
        coll.objects.unlink(inner_body)
    bin_collection.objects.link(inner_body)
    
    # Boolean to hollow
    bpy.context.view_layer.objects.active = outer_body
    hollow_bool = outer_body.modifiers.new(name="Hollow", type='BOOLEAN')
    hollow_bool.operation = 'DIFFERENCE'
    hollow_bool.object = inner_body
    
    # Apply modifier
    bpy.ops.object.select_all(action='DESELECT')
    outer_body.select_set(True)
    bpy.context.view_layer.objects.active = outer_body
    bpy.ops.object.modifier_apply(modifier="Hollow")
    
    # Delete inner body
    bpy.ops.object.select_all(action='DESELECT')
    inner_body.select_set(True)
    bpy.ops.object.delete()
    
    # Apply material to body
    if outer_body.data.materials:
        outer_body.data.materials[0] = body_mat
    else:
        outer_body.data.materials.append(body_mat)
    
    # 3. Create flip-top lid (semi-cylinder)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius + 0.015,
        depth=lid_height,
        vertices=32,
        location=(0, 0, height + lid_height/2)
    )
    lid = bpy.context.active_object
    lid.name = "Bin_FlipLid"
    
    # Cut the cylinder in half to make flip lid
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, radius + 0.02, height + lid_height/2)
    )
    lid_cutter = bpy.context.active_object
    lid_cutter.name = "Lid_Cutter"
    lid_cutter.scale = (radius * 3, radius * 2, lid_height + 0.1)
    
    # Apply scale
    bpy.context.view_layer.objects.active = lid_cutter
    bpy.ops.object.transform_apply(scale=True)
    
    # Move to collection
    for coll in lid_cutter.users_collection:
        coll.objects.unlink(lid_cutter)
    bin_collection.objects.link(lid_cutter)
    
    # Boolean to cut lid
    bpy.context.view_layer.objects.active = lid
    lid_bool = lid.modifiers.new(name="HalfCut", type='BOOLEAN')
    lid_bool.operation = 'DIFFERENCE'
    lid_bool.object = lid_cutter
    
    bpy.ops.object.select_all(action='DESELECT')
    lid.select_set(True)
    bpy.context.view_layer.objects.active = lid
    bpy.ops.object.modifier_apply(modifier="HalfCut")
    
    # Delete cutter
    bpy.ops.object.select_all(action='DESELECT')
    lid_cutter.select_set(True)
    bpy.ops.object.delete()
    
    # Rotate lid to flip position
    lid.rotation_euler = (math.radians(lid_flip_angle), 0, 0)
    
    # Set origin to hinge point
    bpy.context.view_layer.objects.active = lid
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    
    # Move to collection and apply material
    for coll in lid.users_collection:
        coll.objects.unlink(lid)
    bin_collection.objects.link(lid)
    
    if lid.data.materials:
        lid.data.materials[0] = lid_mat
    else:
        lid.data.materials.append(lid_mat)
    
    # 4. Create hinge
    hinge_y = -radius + 0.01
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=hinge_radius,
        depth=hinge_width,
        vertices=12,
        location=(0, hinge_y, height)
    )
    hinge = bpy.context.active_object
    hinge.name = "Bin_Hinge"
    hinge.rotation_euler = (0, math.pi/2, 0)
    
    # Move to collection and apply material
    for coll in hinge.users_collection:
        coll.objects.unlink(hinge)
    bin_collection.objects.link(hinge)
    
    if hinge.data.materials:
        hinge.data.materials[0] = body_mat
    else:
        hinge.data.materials.append(body_mat)
    
    # 5. Create removable liner (inner bucket)
    liner_radius = radius - wall_thickness - 0.01
    liner_height = height - bottom_thickness - 0.05
    
    # Liner outer
    bpy.ops.mesh.primitive_cylinder_add(
        radius=liner_radius,
        depth=liner_height,
        vertices=32,
        location=(0, 0, bottom_thickness + 0.025 + liner_height/2)
    )
    liner_outer = bpy.context.active_object
    liner_outer.name = "Liner_Outer"
    
    # Move to collection
    for coll in liner_outer.users_collection:
        coll.objects.unlink(liner_outer)
    bin_collection.objects.link(liner_outer)
    
    # Liner inner
    bpy.ops.mesh.primitive_cylinder_add(
        radius=liner_radius - liner_thickness,
        depth=liner_height - liner_thickness + 0.01,
        vertices=32,
        location=(0, 0, bottom_thickness + 0.025 + liner_height/2 + liner_thickness/2)
    )
    liner_inner = bpy.context.active_object
    liner_inner.name = "Liner_Inner"
    
    # Move to collection
    for coll in liner_inner.users_collection:
        coll.objects.unlink(liner_inner)
    bin_collection.objects.link(liner_inner)
    
    # Boolean to hollow liner
    bpy.context.view_layer.objects.active = liner_outer
    liner_bool = liner_outer.modifiers.new(name="LinerHollow", type='BOOLEAN')
    liner_bool.operation = 'DIFFERENCE'
    liner_bool.object = liner_inner
    
    bpy.ops.object.select_all(action='DESELECT')
    liner_outer.select_set(True)
    bpy.context.view_layer.objects.active = liner_outer
    bpy.ops.object.modifier_apply(modifier="LinerHollow")
    
    # Delete liner inner
    bpy.ops.object.select_all(action='DESELECT')
    liner_inner.select_set(True)
    bpy.ops.object.delete()
    
    # Apply material to liner
    if liner_outer.data.materials:
        liner_outer.data.materials[0] = liner_mat
    else:
        liner_outer.data.materials.append(liner_mat)
    
    # 6. Create liner rim (handle)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=liner_radius,
        minor_radius=liner_rim_height/2,
        major_segments=32,
        minor_segments=12,
        location=(0, 0, bottom_thickness + 0.025 + liner_height)
    )
    liner_rim = bpy.context.active_object
    liner_rim.name = "Liner_Rim"
    liner_rim.scale[2] = 1.2
    
    # Apply scale
    bpy.context.view_layer.objects.active = liner_rim
    bpy.ops.object.transform_apply(scale=True)
    
    # Move to collection and apply material
    for coll in liner_rim.users_collection:
        coll.objects.unlink(liner_rim)
    bin_collection.objects.link(liner_rim)
    
    if liner_rim.data.materials:
        liner_rim.data.materials[0] = liner_mat
    else:
        liner_rim.data.materials.append(liner_mat)
    
    # 7. Create lid handle/grip
    grip_z = height + lid_height * 0.7
    grip_y = radius * 0.3
    
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.05,
        minor_radius=0.01,
        major_segments=16,
        minor_segments=8,
        location=(0, grip_y, grip_z)
    )
    lid_grip = bpy.context.active_object
    lid_grip.name = "Lid_Grip"
    lid_grip.rotation_euler = (math.radians(90 + lid_flip_angle), 0, 0)
    
    # Move to collection and apply material
    for coll in lid_grip.users_collection:
        coll.objects.unlink(lid_grip)
    bin_collection.objects.link(lid_grip)
    
    if lid_grip.data.materials:
        lid_grip.data.materials[0] = lid_mat
    else:
        lid_grip.data.materials.append(lid_mat)
    
    # 8. Create top rim on body
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=0.02,
        major_segments=32,
        minor_segments=12,
        location=(0, 0, height)
    )
    top_rim = bpy.context.active_object
    top_rim.name = "Body_TopRim"
    
    # Move to collection and apply material
    for coll in top_rim.users_collection:
        coll.objects.unlink(top_rim)
    bin_collection.objects.link(top_rim)
    
    if top_rim.data.materials:
        top_rim.data.materials[0] = body_mat
    else:
        top_rim.data.materials.append(body_mat)
    
    # Smooth shading
    for obj in bin_collection.objects:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
    
    print(f"Flip-top bin with liner created with {material_type} material")
    return bin_collection


# Example 1: White/gray bathroom bin (default)
bin_flip = create_flip_top_bin(
    material_type="plastic",
    body_color=(0.85, 0.85, 0.87, 1.0),
    lid_color=(0.75, 0.75, 0.77, 1.0),
    liner_color=(0.15, 0.15, 0.15, 1.0)
)

# Example 2: Stainless steel kitchen bin
# bin_flip_steel = create_flip_top_bin(
#     radius=0.35,
#     height=0.7,
#     material_type="metal",
#     body_color=(0.8, 0.8, 0.85, 1.0),
#     lid_color=(0.75, 0.75, 0.8, 1.0),
#     liner_color=(0.2, 0.2, 0.2, 1.0),
#     lid_flip_angle=80
# )

# Example 3: Colored bathroom bin
# bin_flip_color = create_flip_top_bin(
#     radius=0.28,
#     height=0.55,
#     material_type="plastic",
#     body_color=(0.9, 0.7, 0.8, 1.0),  # Pink
#     lid_color=(0.85, 0.65, 0.75, 1.0),
#     liner_color=(0.1, 0.1, 0.1, 1.0)
# )