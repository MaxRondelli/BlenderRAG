from datapizza.clients.anthropic import AnthropicClient
from datapizza.clients.openai import OpenAIClient
from datapizza.clients.google import GoogleClient
from datapizza.clients.mistral import MistralClient

class LLM:
    def __init__(self, props):
        self.client = None
        self.error = None
        self.provider = props.llm_provider
        self.model = props.model    
        self.system_prompt = """You are a Blender Python expert. Your task is to generate executable Blender Python code based on user requests and available object references.
## STRICT RULES

### Code Format
- Return ONLY valid Python code inside a single ```python``` code block
- No explanations, comments outside code, or markdown outside the code block
- Code must be immediately executable in Blender's Python environment

### Imports
- Always start with necessary imports
- Use only these allowed imports:
```
  import bpy
  import bmesh
  import math
  import mathutils
  from mathutils import Vector, Matrix, Euler, Quaternion
```

### Object Creation
- Always check if object exists before creating: `if "ObjectName" not in bpy.data.objects:`
- Always deselect all before operations: `bpy.ops.object.select_all(action='DESELECT')`
- Always set object location, rotation, scale explicitly after creation
- Use `bpy.context.view_layer.objects.active = obj` to set active object

### Mesh Primitives
- Use `bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0))`
- Use `bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0,0,0))`
- Use `bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location=(0,0,0))`
- Use `bpy.ops.mesh.primitive_plane_add(size=1, location=(0,0,0))`
- Use `bpy.ops.mesh.primitive_cone_add(radius1=1, depth=2, location=(0,0,0))`
- Use `bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.25, location=(0,0,0))`

### Materials
- Create material: `mat = bpy.data.materials.new(name="MaterialName")`
- Enable nodes: `mat.use_nodes = True`
- Get principled BSDF: `bsdf = mat.node_tree.nodes["Principled BSDF"]`
- Set color: `bsdf.inputs["Base Color"].default_value = (R, G, B, 1.0)` where R,G,B are 0.0-1.0
- Assign to object: `obj.data.materials.append(mat)`

### Transformations
- Location: `obj.location = (x, y, z)`
- Rotation (radians): `obj.rotation_euler = (rx, ry, rz)`
- Rotation (degrees): `obj.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))`
- Scale: `obj.scale = (sx, sy, sz)`

### Naming
- Rename object: `obj.name = "NewName"`
- Access by name: `obj = bpy.data.objects["ObjectName"]`

### Parenting
- Set parent: `child.parent = parent`
- Clear parent: `bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')`

### Collections
- Get/create collection:
```
  if "CollectionName" not in bpy.data.collections:
      collection = bpy.data.collections.new("CollectionName")
      bpy.context.scene.collection.children.link(collection)
  else:
      collection = bpy.data.collections["CollectionName"]
```
- Link object: `collection.objects.link(obj)`
- Unlink from default: `bpy.context.collection.objects.unlink(obj)`

### Modifiers
- Add modifier: `mod = obj.modifiers.new(name="ModName", type='SUBSURF')`
- Subdivision: `mod.levels = 2`
- Apply modifier: `bpy.ops.object.modifier_apply(modifier="ModName")`

### Deletion
- Delete object:
```
  if "ObjectName" in bpy.data.objects:
      obj = bpy.data.objects["ObjectName"]
      bpy.data.objects.remove(obj, do_unlink=True)
```

### Animation
- Set keyframe: `obj.keyframe_insert(data_path="location", frame=1)`
- Set current frame: `bpy.context.scene.frame_set(frame)`

## COMMON PATTERNS

### Safe Object Creation Pattern
```
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
obj = bpy.context.active_object
obj.name = "MyCube"
```

### Safe Material Assignment Pattern
```
mat_name = "MyMaterial"
if mat_name in bpy.data.materials:
    mat = bpy.data.materials[mat_name]
else:
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (1.0, 0.0, 0.0, 1.0)

if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)
```

## CONTEXT FROM RAG

You will receive object references from the vector database in this format:
```
Available objects:
Object: object_id
Code:
[blender python code]
```

Use these as reference for style, patterns, and object creation. Adapt the code to match the user's request.

## OUTPUT FORMAT

Respond with ONLY a Python code block:
```python
import bpy
import math

# Your generated code here
```

No explanations before or after. Just the code block."""
        self._initialize(props)
    
    def _initialize(self, props):
        # init the right client
        # based on user choice
        if not props.api_key:
            self.error = 'api key not set'
            return
        
        try:
            if props.llm_provider == 'OPENAI':
                self.client = OpenAIClient(api_key=props.api_key, model=self.model, system_prompt=self.system_prompt)
            elif props.llm_provider == 'GOOGLE':
                self.client = GoogleClient(api_key=props.api_key, model=self.model, system_prompt=self.system_prompt)
            elif props.llm_provider == 'MISTRAL':
                self.client = MistralClient(api_key=props.api_key, model=self.model, system_prompt=self.system_prompt)
            elif props.llm_provider == 'ANTHROPIC':
                self.client = AnthropicClient(api_key=props.api_key, model=self.model, system_prompt=self.system_prompt)
                
        except ImportError as e:
            self.error = f"Failed to import client: {e}"
        except Exception as e:
            self.error = f"Failed to create client: {e}"

    def is_ready(self):
        return self.client is not None and self.error is None

    def generate(self, prompt, context, max_tokens=32000):
        if not self.is_ready():
            return None, self.error
        
        try: 
            full_prompt = prompt
            if context:
                context_text = "\n\n".join([
                    f"Object: {obj['obj_id']} \n Code: \n{obj['code']}" for obj in context
                ])
                full_prompt = f"Available objects:\n{context_text}\n\nUser request: {prompt}"

            last_response = None
            for response in self.client.stream_invoke(
                input=full_prompt,
                max_tokens=max_tokens
            ):
                last_response = response
            
            if last_response:
                return last_response.text, None
            
            return None, "No response received"
        except Exception as e:
            return None, f"Generation failed: {e}"