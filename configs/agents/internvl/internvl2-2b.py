from lmdeploy import (ChatTemplateConfig, GenerationConfig,
                      TurbomindEngineConfig)

lmm_agent = dict(
    name='internvl2-2b',
    agent='lmdeploy_single',
    chat_template=ChatTemplateConfig('internvl-internlm2'),
    model='OpenGVLab/InternVL2-2B',
    backend_config=TurbomindEngineConfig(session_len=8192),
    general_config=GenerationConfig(max_new_tokens=1024, top_p=0.8),
)
