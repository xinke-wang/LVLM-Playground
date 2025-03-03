
class BaseQuestionAnswering:

    def __init__(self, general_prompt, shot=3):
        self.general_prompt = general_prompt
        self.question_pool = []
        self.shot = shot

    def get_qa_pair(self, game_state):
        raise NotImplementedError('Subclasses should implement this method.')

    def get_qa_pairs(self, game_state):
        qa_pairs = set()
        while len(qa_pairs) < self.shot + 1:
            question, answer = self.get_qa_pair(game_state)
            qa_pair = (question, answer)
            if qa_pair not in qa_pairs:
                qa_pairs.add(qa_pair)

        return list(qa_pairs)

    def get_answer(self, game_state, question):
        raise NotImplementedError('Subclasses should implement this method.')
