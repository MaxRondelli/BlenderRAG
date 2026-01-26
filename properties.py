import bpy
from bpy.props import StringProperty, EnumProperty, IntProperty, FloatProperty, BoolProperty, PointerProperty
from bpy.types import PropertyGroup

def get_model_items(self, context):
    """Return model choices based on selected provider"""
    models = {
        'OPENAI': [
            ('gpt-4o', "GPT-4o", ""),
            ('gpt-4o-mini', "GPT-4o Mini", ""),
            ('gpt-4-turbo', "GPT-4 Turbo", ""),
        ],
        'ANTHROPIC': [
            ('claude-sonnet-4-5-20250929', "Claude Sonnet 4.5", ""),
            ('claude-opus-4-5-20251101', "Claude Opus 4.5", ""),
            ('claude-haiku-4-5-20251001', "Claude Haiku 4.5", ""),
        ],
        'GOOGLE': [
            ('gemini-1.5-pro', "Gemini 1.5 Pro", ""),
            ('gemini-1.5-flash', "Gemini 1.5 Flash", ""),
        ],
        'MISTRAL': [
            ('mistral-large-latest', "Mistral Large", ""),
            ('mistral-medium-latest', "Mistral Medium", ""),
        ],
    }
    return models.get(self.llm_provider, [('', "None", "")])

class RAGProperties(PropertyGroup):
    """Settings for RAG Assistant"""
    
    # LLM Settings
    llm_provider: EnumProperty(
        name="Provider",
        items=[
            ('OPENAI', "OpenAI", ""),
            ('ANTHROPIC', "Anthropic", ""),
            ('GOOGLE', "Google", ""),
            ('MISTRAL', "Mistral", ""),
        ],
        default='ANTHROPIC'
    )
    
    api_key: StringProperty(
        name="API Key",
        default="",
        subtype='PASSWORD'
    )
    
    model: EnumProperty(
        name="Model",
        items=get_model_items  
    )
    
    # RAG Settings
    top_k: IntProperty(
        name="Top K",
        default=5,
        min=1,
        max=20
    )
    
    # Chat
    prompt: StringProperty(
        name="Prompt",
        default=""
    )
    
    history: StringProperty(
        name="History",
        default=""
    )
    
    status: StringProperty(
        name="Status",
        default="Ready"
    )

