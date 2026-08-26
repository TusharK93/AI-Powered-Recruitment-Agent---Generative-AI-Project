from chains.ats_chain import analyze_resume_chain


class ATSAgent:

    def __init__(self, llm):
        self.llm = llm

    def run(self, resume_text: str):
        return analyze_resume_chain(
            resume_text,
            self.llm
        ).invoke({})