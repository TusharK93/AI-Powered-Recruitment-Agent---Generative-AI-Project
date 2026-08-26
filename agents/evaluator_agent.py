from chains.evaluation_chain import evaluate_answer_chain


class EvaluatorAgent:

    def __init__(self, llm):
        self.llm = llm

    def run(self, question: str, answer: str, difficulty: str):
        return evaluate_answer_chain(
            question,
            answer,
            difficulty,
            self.llm
        ).invoke({})