from lmdeploy import ChatTemplateConfig, PytorchEngineConfig

_base_ = ['configs/agents/internvl/internvl2-2b.py']

lmm_agent = dict(
    name='internvl2-4b',
    chat_template=ChatTemplateConfig('internvl-phi3'),
    model='OpenGVLab/InternVL2-4B',
    backend_config=PytorchEngineConfig(session_len=8192)
)
