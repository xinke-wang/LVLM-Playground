from lmdeploy import (ChatTemplateConfig, GenerationConfig,
                      TurbomindEngineConfig)

lmm_agent = dict(
    name='qwen7b',
    agent='lmdeploy_single',
    chat_template=ChatTemplateConfig('qwen-7b'),
    model='Qwen/Qwen2-VL-7B-Instruct',
    backend_config=TurbomindEngineConfig(session_len=8192),
    general_config=GenerationConfig(max_new_tokens=1024)
)
