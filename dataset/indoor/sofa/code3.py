import bpy
import bmesh
import math
from mathutils import Vector

def clear_scene():
    """Clear all mesh objects from the scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_couch_base(width, depth, height, location):
    """Create the base/frame of the couch"""
    bpy.ops.mesh.primitive_cube_add(location=location)
    base = bpy.context.active_object
    base.name = "Couch_Base"
    base.scale = (width/2, depth/2, height/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Add subdivision and bevel for smooth edges
    bevel = base.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.03
    bevel.segments = 4
    
    subsurf = base.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3
    
    return base

def create_armrest(width, depth, height, location, name):
    """Create a padded armrest"""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # Create armrest shape
    bmesh.ops.create_cube(bm, size=1.0)
    
    # Scale to armrest dimensions
    bmesh.ops.scale(bm, vec=(width, depth, height), verts=bm.verts)
    
    # More pronounced bevel edges for luxury look
    edges_to_bevel = [e for e in bm.edges]
    bmesh.ops.bevel(bm, geom=edges_to_bevel, offset=0.12, segments=5, 
                    profile=0.6, affect='EDGES')
    
    bm.to_mesh(mesh)
    bm.free()
    
    obj.location = location
    
    # Add subdivision for smoothness
    subsurf = obj.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 3
    subsurf.render_levels = 4
    
    return obj

def create_seat_cushion(width, depth, height, location, name):
    """Create a comfortable seat cushion"""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(width, depth, height), verts=bm.verts)
    
    # More pronounced bevel for luxury cushion softness
    edges_to_bevel = [e for e in bm.edges]
    bmesh.ops.bevel(bm, geom=edges_to_bevel, offset=0.09, segments=5, 
                    profile=0.6, affect='EDGES')
    
    bm.to_mesh(mesh)
    bm.free()
    
    obj.location = location
    
    # Add subdivision
    subsurf = obj.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 3
    subsurf.render_levels = 4
    
    return obj

def create_back_cushion(width, depth, height, location, name, angle=0):
    """Create a back cushion with optional angle"""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(width, depth, height), verts=bm.verts)
    
    # Enhanced bevel for luxury cushion softness
    edges_to_bevel = [e for e in bm.edges]
    bmesh.ops.bevel(bm, geom=edges_to_bevel, offset=0.08, segments=5, 
                    profile=0.65, affect='EDGES')
    
    bm.to_mesh(mesh)
    bm.free()
    
    obj.location = location
    obj.rotation_euler = (math.radians(angle), 0, 0)
    
    # Add subdivision
    subsurf = obj.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 3
    subsurf.render_levels = 4
    
    return obj

def create_couch_section(width, depth, base_height, back_height, location, section_name, num_cushions=3):
    """Create a section of the couch with cushions"""
    
    armrest_width = 0.3
    armrest_height = 0.65
    seat_height = 0.18  # Slightly thicker cushions
    back_cushion_thickness = 0.24  # Thicker back cushions
    
    # Create base/frame
    base = create_couch_base(
        width, 
        depth, 
        base_height,
        Vector((location[0], location[1], base_height/2))
    )
    base.name = f"{section_name}_Base"
    
    # Create left armrest
    left_arm = create_armrest(
        armrest_width,
        depth * 0.9,
        armrest_height,
        Vector((location[0] - width/2 + armrest_width/2, location[1], base_height + armrest_height/2)),
        f"{section_name}_Armrest_Left"
    )
    
    # Create right armrest
    right_arm = create_armrest(
        armrest_width,
        depth * 0.9,
        armrest_height,
        Vector((location[0] + width/2 - armrest_width/2, location[1], base_height + armrest_height/2)),
        f"{section_name}_Armrest_Right"
    )
    
    # Calculate cushion dimensions
    cushion_area_width = width - 2 * armrest_width
    cushion_width = cushion_area_width / num_cushions
    cushion_depth = depth * 0.83
    
    seat_z = base_height + seat_height/2
    
    # Create seat cushions - touching each other
    for i in range(num_cushions):
        cushion_x = location[0] - cushion_area_width/2 + cushion_width/2 + i * cushion_width
        cushion = create_seat_cushion(
            cushion_width,
            cushion_depth,
            seat_height,
            Vector((cushion_x, location[1] + 0.05, seat_z)),
            f"{section_name}_SeatCushion_{i+1}"
        )
    
    # Create back cushions - touching each other
    back_cushion_width = cushion_width
    back_cushion_height = back_height - base_height + 0.15
    back_z = base_height + back_cushion_height/2 - 0.1
    back_y = location[1] - depth/2 + back_cushion_thickness/2 + 0.15
    
    for i in range(num_cushions):
        cushion_x = location[0] - cushion_area_width/2 + back_cushion_width/2 + i * back_cushion_width
        cushion = create_back_cushion(
            back_cushion_width,
            back_cushion_thickness,
            back_cushion_height,
            Vector((cushion_x, back_y, back_z)),
            f"{section_name}_BackCushion_{i+1}",
            angle=-5
        )

def create_realistic_couch():
    """Generate a realistic couch similar to the reference"""
    
    # Main couch dimensions (scaled appropriately)
    main_width = 5.0
    main_depth = 1.8
    base_height = 0.45
    back_height = 1.7
    
    # Create main couch section
    create_couch_section(
        main_width,
        main_depth,
        base_height,
        back_height,
        (0, 0, 0),
        "MainCouch",
        num_cushions=3
    )
    
    # Create materials
    create_couch_materials()
    apply_materials()
    
    print("Realistic leather couch generated successfully!")

def create_couch_materials():
    """Create realistic leather materials for the couch"""
    
    # Main leather material - rich dark brown
    main_leather = bpy.data.materials.new(name="Couch_Leather_Main")
    main_leather.use_nodes = True
    nodes = main_leather.node_tree.nodes
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    
    # Add noise texture for leather grain
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-300, 0)
    noise.inputs['Scale'].default_value = 25.0
    noise.inputs['Detail'].default_value = 10.0
    noise.inputs['Roughness'].default_value = 0.7
    
    # Add ColorRamp for contrast
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.location = (-100, 0)
    ramp.color_ramp.elements[0].position = 0.4
    ramp.color_ramp.elements[0].color = (0.12, 0.08, 0.05, 1.0)  # Dark brown
    ramp.color_ramp.elements[1].position = 0.6
    ramp.color_ramp.elements[1].color = (0.25, 0.18, 0.12, 1.0)  # Medium brown
    
    # Mix node for blending
    mix = nodes.new(type='ShaderNodeMix')
    mix.location = (100, 0)
    mix.data_type = 'RGBA'
    mix.inputs[0].default_value = 0.3
    
    # Rich dark brown leather color
    bsdf.inputs['Base Color'].default_value = (0.18, 0.12, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.4
    bsdf.inputs['IOR'].default_value = 1.5
    bsdf.inputs['Metallic'].default_value = 0.0
    
    # Connect nodes
    links = main_leather.node_tree.links
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], mix.inputs[6])
    mix.inputs[7].default_value = (0.18, 0.12, 0.08, 1.0)
    links.new(mix.outputs['Result'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Cushion leather material - slightly lighter brown
    cushion_leather = bpy.data.materials.new(name="Couch_Leather_Cushion")
    cushion_leather.use_nodes = True
    nodes = cushion_leather.node_tree.nodes
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Medium brown leather for cushions
    bsdf.inputs['Base Color'].default_value = (0.22, 0.16, 0.11, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.35
    bsdf.inputs['IOR'].default_value = 1.5
    bsdf.inputs['Metallic'].default_value = 0.0
    
    cushion_leather.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

def apply_materials():
    """Apply materials to couch components"""
    main_leather = bpy.data.materials.get("Couch_Leather_Main")
    cushion_leather = bpy.data.materials.get("Couch_Leather_Cushion")
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if "Cushion" in obj.name:
                if len(obj.data.materials) == 0:
                    obj.data.materials.append(cushion_leather)
                else:
                    obj.data.materials[0] = cushion_leather
            elif "Couch" in obj.name or "Armrest" in obj.name or "Base" in obj.name:
                if len(obj.data.materials) == 0:
                    obj.data.materials.append(main_leather)
                else:
                    obj.data.materials[0] = main_leather

def setup_scene():
    """Setup camera and lighting for better visualization"""
    
    # Add camera
    bpy.ops.object.camera_add(location=(7, -7, 4.5))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(60), 0, math.radians(45))
    bpy.context.scene.camera = camera
    
    # Add key light
    bpy.ops.object.light_add(type='AREA', location=(5, -5, 6))
    key_light = bpy.context.active_object
    key_light.data.energy = 400
    key_light.data.size = 4
    
    # Add fill light
    bpy.ops.object.light_add(type='AREA', location=(-4, -3, 4))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 200
    fill_light.data.size = 3
    
    # Set render settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128

# Main execution
if __name__ == "__main__":
    clear_scene()
    create_realistic_couch()
    setup_scene()
    
    # Set viewport shading to material preview
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
    
    print("Leather couch generation complete! Adjust camera angle as needed.")