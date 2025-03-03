from lmdeploy import (ChatTemplateConfig, GenerationConfig,
                      TurbomindEngineConfig)

lmm_agent = dict(
    name='phi3.5-vl',
    agent='lmdeploy_single',
    model='microsoft/Phi-3.5-vision-instruct',
    hat_template=ChatTemplateConfig('phi-3'),
    backend_config=TurbomindEngineConfig(session_len=8192),
    general_config=GenerationConfig(max_new_tokens=1024)
)
