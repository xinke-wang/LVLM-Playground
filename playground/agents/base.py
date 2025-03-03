from abc import ABC, abstractmethod


class BaseAgent(ABC):

    def __init__(self, agent_cfg):
        self.agent_cfg = agent_cfg

    @abstractmethod
    def get_decision(self, screenshot_path: str, prompt: str):
        """
        Given the path to a screenshot of the current game state and a prompt,
        this method should return a decision on the next move or action.
        """
        raise NotImplementedError('The method not implemented')
