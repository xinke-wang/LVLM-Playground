from lmdeploy import (ChatTemplateConfig, GenerationConfig,
                      TurbomindEngineConfig)

lmm_agent = dict(
    name='llava1.6-vicuna7b',
    agent='lmdeploy_single',
    model='liuhaotian/llava-v1.6-vicuna-7b',
    hat_template=ChatTemplateConfig('llava-v1'),
    backend_config=TurbomindEngineConfig(session_len=8192),
    general_config=GenerationConfig(max_new_tokens=1024)
)
