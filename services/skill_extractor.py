from chains.skill_chain import extract_skills_from_resume_chain
from langchain_google_genai import GoogleGenerativeAI
llm = GoogleGenerativeAI('gemini-3.6-flash')
class SkillExtractor:
    def __init__(self,llm):
        self.llm = llm
    def extract(self,resume_text:str):
        chain = extract_skills_from_resume_chain(resume_text,self.llm)
        return chain.invoke({})
