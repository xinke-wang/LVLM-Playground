import os
import pathlib

import anthropic
import google.generativeai as genai
import requests
from lmdeploy import pipeline
from lmdeploy.vl import load_image

from playground.agents import BaseAgent
from playground.registry import AGENT_REGISTRY
from playground.utils import encode_image


@AGENT_REGISTRY.register('openai_single')
class OpenAIAgentSingleStep(BaseAgent):

    def __init__(self, agent_cfg):
        super().__init__(agent_cfg)
        api_key = os.getenv('OPENAI_API_KEY')
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        self.base_payload = {
            'model': agent_cfg.lmm_agent.model,
            'max_tokens': agent_cfg.lmm_agent.max_tokens
        }
        self.input_sz = agent_cfg.lmm_agent.image_size

    def get_decision(self, screenshot_path: str, prompt: str):
        base64_image = encode_image(screenshot_path, self.input_sz)
        payload = self.base_payload.copy()
        payload['messages'] = [{
            'role':
            'user',
            'content': [{
                'type': 'text',
                'text': prompt
            }, {
                'type': 'image_url',
                'image_url': {
                    'url': f'data:image/jpeg;base64,{base64_image}'
                }
            }]
        }]
        outputs = requests.post('https://api.openai.com/v1/chat/completions',
                                headers=self.headers,
                                json=payload)
        outputs = outputs.json()
        return outputs['choices'][0]['message']['content']


@AGENT_REGISTRY.register('google_single')
class GoogleAIAgentSingleStep(BaseAgent):

    def __init__(self, agent_cfg):
        super().__init__(agent_cfg)
        self.api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name=agent_cfg.lmm_agent.model)

    def get_decision(self, screenshot_path: str, prompt: str):
        image = {
            'mime_type': 'image/png',
            'data': pathlib.Path(screenshot_path).read_bytes()
        }
        outputs = self.model.generate_content([prompt, image])
        return outputs.text


@AGENT_REGISTRY.register('anhthropic_single')
class AnthropicAgentSingleStep(BaseAgent):

    def __init__(self, agent_cfg):
        super().__init__(agent_cfg)
        self.base_payload = {
            'model': agent_cfg.lmm_agent.model,
            'max_tokens': agent_cfg.lmm_agent.max_tokens
        }
        self.input_sz = agent_cfg.lmm_agent.image_size
        self.model = anthropic.Anthropic()

    def get_decision(self, screenshot_path: str, prompt: str):
        base64_image = encode_image(screenshot_path, self.input_sz)
        payload = self.base_payload.copy()
        payload['messages'] = [{
            'role':
            'user',
            'content': [{
                'type': 'image',
                'source': {
                    'type': 'base64',
                    'media_type': 'image/png',
                    'data': base64_image
                }
            }, {
                'type': 'text',
                'text': prompt
            }]
        }]
        outputs = self.model.messages.create(**payload)
        return outputs.content[0].text


@AGENT_REGISTRY.register('lmdeploy_single')
class LMDeployAgentSingleStep(BaseAgent):

    def __init__(self, agent_cfg):
        super().__init__(agent_cfg)
        if agent_cfg.lmm_agent.name == 'deepseek-vl-7b':
            self.is_deepseek_vl = True
        else:
            self.is_deepseek_vl = False
        self.model = pipeline(
            agent_cfg.lmm_agent.model,
            backend_config=agent_cfg.lmm_agent.backend_config)
        self.gen_config = agent_cfg.lmm_agent.general_config

    def get_decision(self, screenshot_path: str, prompt: str):
        image = load_image(screenshot_path)
        if self.is_deepseek_vl:
            prompt = '<IMAGE_TOKEN>' + prompt
        outputs = self.model((prompt, image), gen_config=self.gen_config)
        return outputs.text
