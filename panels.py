import sys
import bpy
from bpy.types import Panel

class RAG_PT_Main(Panel):
    bl_label = "BlenderRAG"
    bl_idname = "RAG_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlenderRAG'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.rag_props
        
        addon_name = __name__.split('.')[0]
        addon_module = sys.modules.get(addon_name)

        if not addon_module:
            layout.label(text="Error loading addon", icon='ERROR')
            # layout.label(text=f"Module '{addon_name}' not found")
            return
        ready = getattr(addon_module, '_dependencies_ready', None)
        error = getattr(addon_module, '_import_error', "")
        if ready is None:
            layout.label(text="Addon state unknown", icon='ERROR')
            return
        
        if not ready:
            box = layout.box()
            box.label(text="Dependencies Missing", icon='ERROR')
            box.separator()
            
            # button install dependecies
            col = box.column(align=True)
            col.scale_y = 2.0
            col.operator("rag.install_dependencies", 
                        text="Install Dependencies",
                        icon='IMPORT')
            
            box.separator()
            col = box.column(align=True)
            col.label(text="This will install required packages:")
            col.label(text="• torch")
            col.label(text="• sentence-transformers")
            col.label(text="• qdrant-client")
            col.label(text="• datapizza-ai")
            box.separator()
            col = box.column(align=True)
            col.label(text="Installation may some minutes.", icon='TIME')
            col.label(text="Please restart Blender afterwards.", icon='FILE_REFRESH')
           
            return
        
        # UI when dependencies are ready
        layout.label(text="Prompt:")
        layout.prop(props, "prompt", text="")
        
        layout.separator()
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("rag.generate", text="Generate", icon='PLAY')
        row.operator("rag.clear", text="Clear", icon='X')
        
        if props.status:
            layout.separator()
            box = layout.box()
            box.label(text=props.status, icon='INFO')
        
        if props.history:
            layout.separator()
            box = layout.box()
            box.label(text="History:", icon='TEXT')
            col = box.column(align=True)
            for line in props.history.split('\n')[:10]:
                if line.strip():
                    col.label(text=line[:60])

class RAG_PT_Settings(Panel):
    bl_label = "Settings"
    bl_idname = "RAG_PT_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Blender500'
    bl_parent_id = "RAG_PT_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.rag_props
        addon_name = __name__.split('.')[0]
        addon_module = sys.modules.get(addon_name)
        if not addon_module:
            layout.label(text="Addon module not found", icon='ERROR')
            return    
        ready = getattr(addon_module, '_dependencies_ready', False)   
        if not ready:
            layout.label(text="Dependencies not ready", icon='INFO')
            layout.label(text="Install dependencies first")
            return
        
        # LLM settings
        layout.label(text="LLM Settings:")
        layout.prop(props, "llm_provider", text="Provider")
        layout.prop(props, "model", text="Model")
        layout.prop(props, "api_key", text="API Key")
        
        layout.separator()
        
        # retrieval settings
        layout.label(text="Retrieval Settings:")
        layout.prop(props, "top_k", text="Number of Results")