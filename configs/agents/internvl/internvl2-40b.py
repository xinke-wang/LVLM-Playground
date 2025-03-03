_base_ = ['configs/agents/internvl/internvl2-2b.py']

from lmdeploy import ChatTemplateConfig

lmm_agent = dict(
    name='internvl2-40b',
    model='OpenGVLab/InternVL2-40B',
    chat_template=ChatTemplateConfig('internvl-zh-hermes2'),
)
