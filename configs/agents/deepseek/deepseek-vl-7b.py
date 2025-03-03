from lmdeploy import (ChatTemplateConfig, GenerationConfig,
                      TurbomindEngineConfig)

lmm_agent = dict(
    name='deepseek-vl-7b',
    agent='lmdeploy_single',
    chat_template=ChatTemplateConfig('deepseek-chat'),
    model='deepseek-ai/deepseek-vl-7b-chat',
    backend_config=TurbomindEngineConfig(session_len=8192),
    general_config=GenerationConfig(max_new_tokens=1024)
)
