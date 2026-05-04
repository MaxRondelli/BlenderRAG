import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Wine glass dimensions (wider bowl, shorter stem for elegance)
bowl_bottom_radius = 0.018  # 1.8cm at bottom of bowl (wider)
bowl_top_radius = 0.035     # 3.5cm at rim (wider)
bowl_height = 0.12          # 12cm bowl height (shorter)
stem_radius = 0.003         # 3mm stem thickness (slightly thicker)
stem_height = 0.08          # 8cm stem height (shorter)
base_radius = 0.038         # 3.8cm base radius (larger)
base_thickness = 0.004      # 4mm base thickness (thicker)
glass_thickness = 0.0015    # 1.5mm glass wall thickness

# STEP 1: Create the hollow bowl walls using curves
curve_data = bpy.data.curves.new('bowl_profile', type='CURVE')
curve_data.dimensions = '3D'
curve_data.resolution_u = 32

# Create a spline for the bowl walls
spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(3)  # 4 points total

# Define the profile points (from bottom to top of bowl)
# Point 0: Bottom inside
spline.bezier_points[0].co = (bowl_bottom_radius - glass_thickness, 0, 0)
spline.bezier_points[0].handle_left_type = 'AUTO'
spline.bezier_points[0].handle_right_type = 'AUTO'

# Point 1: Bottom outside
spline.bezier_points[1].co = (bowl_bottom_radius, 0, 0)
spline.bezier_points[1].handle_left_type = 'AUTO'
spline.bezier_points[1].handle_right_type = 'AUTO'

# Point 2: Top outside
spline.bezier_points[2].co = (bowl_top_radius, 0, bowl_height)
spline.bezier_points[2].handle_left_type = 'AUTO'
spline.bezier_points[2].handle_right_type = 'AUTO'

# Point 3: Top inside
spline.bezier_points[3].co = (bowl_top_radius - glass_thickness, 0, bowl_height)
spline.bezier_points[3].handle_left_type = 'AUTO'
spline.bezier_points[3].handle_right_type = 'AUTO'

# Close the spline
spline.use_cyclic_u = True

# Create curve object
bowl_curve_obj = bpy.data.objects.new('bowl_curve', curve_data)
bpy.context.collection.objects.link(bowl_curve_obj)
bowl_curve_obj.location = (0, 0, stem_height)

# Add screw modifier
bpy.context.view_layer.objects.active = bowl_curve_obj
bowl_curve_obj.select_set(True)

screw_mod = bowl_curve_obj.modifiers.new(name="Screw", type='SCREW')
screw_mod.axis = 'Z'
screw_mod.steps = 64
screw_mod.render_steps = 64
screw_mod.angle = math.radians(360)
screw_mod.use_smooth_shade = True

# Convert to mesh
bpy.ops.object.convert(target='MESH')
bowl = bpy.context.active_object
bowl.name = "Bowl"

# STEP 2: Create the bottom cap (closed bottom)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=64,
    radius=bowl_bottom_radius - glass_thickness/2,
    depth=glass_thickness,
    location=(0, 0, stem_height + glass_thickness/2)
)
bottom_cap = bpy.context.active_object
bottom_cap.name = "Bottom_Cap"
bpy.ops.object.shade_smooth()

# STEP 3: Create stem as a simple uniform cylinder
stem_penetration = 0.002  # 2mm penetration into bowl
stem_actual_height = stem_height - base_thickness + stem_penetration
stem_center_z = base_thickness + stem_actual_height/2

bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=stem_radius,
    depth=stem_actual_height,
    location=(0, 0, stem_center_z)
)
stem = bpy.context.active_object
stem.name = "Stem"
bpy.ops.object.shade_smooth()

# STEP 4: Create base (flat disc)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=64,
    radius=base_radius,
    depth=base_thickness,
    location=(0, 0, base_thickness/2)
)
base = bpy.context.active_object
base.name = "Base"
bpy.ops.object.shade_smooth()

# STEP 5: Create rim detail (golden ring)
bpy.ops.mesh.primitive_torus_add(
    major_radius=bowl_top_radius - glass_thickness/2,
    minor_radius=glass_thickness/2,
    location=(0, 0, stem_height + bowl_height)
)
rim_detail = bpy.context.active_object
rim_detail.name = "Rim_Detail"
bpy.ops.object.shade_smooth()

# Mark stem edges as sharp
bpy.context.view_layer.objects.active = stem
stem.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.mark_sharp()
bpy.ops.object.mode_set(mode='OBJECT')

# Join main glass parts
bpy.ops.object.select_all(action='DESELECT')
bowl.select_set(True)
bottom_cap.select_set(True)
stem.select_set(True)
base.select_set(True)
bpy.context.view_layer.objects.active = bowl
bpy.ops.object.join()

wine_glass = bpy.context.active_object
wine_glass.name = "Wine_Glass"

# Add modifiers
edge_split = wine_glass.modifiers.new(name="EdgeSplit", type='EDGE_SPLIT')
edge_split.use_edge_angle = False
edge_split.use_edge_sharp = True

subsurf = wine_glass.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 1
subsurf.render_levels = 2

bpy.ops.object.shade_smooth()

# STEP 6: Create amber glass material
mat_glass = bpy.data.materials.new(name="Amber_Glass_Material")
mat_glass.use_nodes = True
nodes = mat_glass.node_tree.nodes
nodes.clear()

# Glass BSDF
glass_bsdf = nodes.new(type='ShaderNodeBsdfGlass')
glass_bsdf.location = (0, 0)
glass_bsdf.inputs['IOR'].default_value = 1.52
glass_bsdf.inputs['Roughness'].default_value = 0.01
glass_bsdf.inputs['Color'].default_value = (0.95, 0.7, 0.4, 1.0)  # Amber tint

# Output
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (200, 0)

# Link nodes
links = mat_glass.node_tree.links
links.new(glass_bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign material to glass
if wine_glass.data.materials:
    wine_glass.data.materials[0] = mat_glass
else:
    wine_glass.data.materials.append(mat_glass)

mat_glass.blend_method = 'BLEND'

# STEP 7: Create golden rim material
mat_gold = bpy.data.materials.new(name="Gold_Rim_Material")
mat_gold.use_nodes = True
nodes_gold = mat_gold.node_tree.nodes
nodes_gold.clear()

# Principled BSDF for gold
gold_bsdf = nodes_gold.new(type='ShaderNodeBsdfPrincipled')
gold_bsdf.location = (0, 0)
gold_bsdf.inputs['Base Color'].default_value = (1.0, 0.8, 0.3, 1.0)
gold_bsdf.inputs['Metallic'].default_value = 1.0
gold_bsdf.inputs['Roughness'].default_value = 0.1

# Output
output_gold = nodes_gold.new(type='ShaderNodeOutputMaterial')
output_gold.location = (200, 0)

# Link nodes
links_gold = mat_gold.node_tree.links
links_gold.new(gold_bsdf.outputs['BSDF'], output_gold.inputs['Surface'])

# Assign material to rim
if rim_detail.data.materials:
    rim_detail.data.materials[0] = mat_gold
else:
    rim_detail.data.materials.append(mat_gold)

# STEP 8: Setup camera
bpy.ops.object.camera_add(location=(0.3, -0.3, 0.15))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(75), 0, math.radians(45))
bpy.context.scene.camera = camera

# STEP 9: Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.data.energy = 4.0

bpy.ops.object.light_add(type='AREA', location=(0, -0.4, 0.3))
area = bpy.context.active_object
area.data.energy = 80
area.data.size = 0.6

# STEP 10: Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.film_transparent = True

print("Elegant amber wine glass generated successfully!")
print(f"Dimensions:")
print(f"  - Bowl diameter (rim): {bowl_top_radius * 2 * 100:.1f}cm")
print(f"  - Bowl height: {bowl_height * 100:.1f}cm")
print(f"  - Stem height: {stem_height * 100:.1f}cm")
print(f"  - Base diameter: {base_radius * 2 * 100:.1f}cm")
print(f"  - Glass thickness: {glass_thickness * 1000:.2f}mm")
print(f"  - Total height: {(stem_height + bowl_height) * 100:.1f}cm")