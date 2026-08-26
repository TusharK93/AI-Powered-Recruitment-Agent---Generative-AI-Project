from chains.interview_chain import generate_question_chain
from langchain_google_genai import ChatGoogleGenerativeAI



class InterviewerAgent:
    def __init__(self, llm):
        self.llm = llm

    def run(self, name:str, role:str, skills, previous_questions=None):
        return generate_question_chain(
            name, role, skills, previous_questions or [], self.llm
        ).invoke({})
