from chains.ats_chain import analyze_resume_chain
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI( model="gemini-3.6-flash",
    temperature=0)
class ATSAgent:
    def __init__(self,llm):
        self.llm = llm
    def run(self,resume_text:str):
        return analyze_resume_chain(resume_text,self.llm).invoke({})
