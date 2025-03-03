_base_ = ['configs/agents/llava/llava1.6-vicuna7b.py']

lmm_agent = dict(
    name='llava1.6-mistral7b',
    model='liuhaotian/llava-v1.6-mistral-7b',
)
