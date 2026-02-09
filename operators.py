import bpy
from bpy.types import Operator 
import sys

class RAG_OT_Generate(Operator):
    """Generate scene from prompt"""
    bl_idname = "rag.generate"
    bl_label = "Generate Scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        from .llm import LLM
        from .rag import get_rag_manager
        from .utils import process_response

        props = context.scene.rag_props
        
        addon_name = __name__.split('.')[0]
        addon_module = sys.modules.get(addon_name)
        
        if not addon_module or not getattr(addon_module, '_dependencies_ready', False):
            self.report({'ERROR'}, "Dependencies not ready. Please restart Blender.")
            return {'CANCELLED'}
        
        if not props.prompt:
            self.report({'WARNING'}, "Enter a prompt")
            return {'CANCELLED'}
        
        # init the llm client
        llm = LLM(props)
        if not llm.is_ready():
            self.report({'ERROR'}, llm.error)
            return {'CANCELLED'}
        
        # init vector db
        props.status = "Querying vector database..."
        rag = get_rag_manager()
        results, error = rag.query(
            prompt=props.prompt,
            k=props.top_k
        ) 
        
        if error:
            props.status = f"Error: {error}"
            self.report({'ERROR'}, error)
            return {'CANCELLED'}
        
        retrieved_objects = []
        if results:
            for idx in range(len(results)):
                obj_id = results[idx].metadata['id']
                code = results[idx].metadata['code']     
                retrieved_objects.append({
                    'obj_id': obj_id,
                    'code': code
                })

            self.report({'INFO'}, f"Found {len(retrieved_objects)} objects")
            print(f"Retrieved objects: {[obj['obj_id'] for obj in retrieved_objects]}")

        if props.history:
            props.history += f"\n\nUser: {props.prompt}"
        else:
            props.history = f"User: {props.prompt}"
        
        # generate the code
        props.status = "Generating response.."
        response, error = llm.generate(
            prompt = props.prompt,
            context = retrieved_objects
        )
        if error:
            props.status = f'Error: {error}'
            self.report({'Error'}, error)
            return {'CANCELLED'}
        
        # execute and save generate code
        props.status = "Processing generated code..."
        result = process_response(response)
        
        if result['filepath']:
            self.report({'INFO'}, f"Code saved to: {result['filepath']}")
            print(f"Generated code saved to: {result['filepath']}")
        
        if result['error']:
            props.status = f"Error: {result['error']}"
            props.history += f"\n\nAssistant: [Code generated but failed]\n{result['error']}"
            self.report({'ERROR'}, result['error'])
            return {'CANCELLED'}
        
        props.history += f"\n\nAssistant: {response}"
        props.prompt = ""
        props.status = "Ready"
        self.report({'INFO'}, "Generated!")
        return {'FINISHED'}

class RAG_OT_Clear(Operator):
    """Clear chat history"""
    bl_idname = "rag.clear"
    bl_label = "Clear"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        context.scene.rag_props.history = ""
        context.scene.rag_props.prompt = ""
        context.scene.rag_props.status = "Ready"
        return {'FINISHED'}
    