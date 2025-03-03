_base_ = ['configs/agents/llava/llava1.6-vicuna7b.py']

lmm_agent = dict(
    name='llava1.6-yi34b',
    model='liuhaotian/llava-v1.6-34b',
)
