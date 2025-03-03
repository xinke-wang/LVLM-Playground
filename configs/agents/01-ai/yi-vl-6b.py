from lmdeploy import (ChatTemplateConfig, GenerationConfig,
                      TurbomindEngineConfig)

lmm_agent = dict(
    name='yi-vl-6b',
    agent='lmdeploy_single',
    chat_template=ChatTemplateConfig('yi-vl'),
    model='01-ai/Yi-VL-6B',
    backend_config=TurbomindEngineConfig(session_len=8192),
    general_config=GenerationConfig(max_new_tokens=1024)
)
