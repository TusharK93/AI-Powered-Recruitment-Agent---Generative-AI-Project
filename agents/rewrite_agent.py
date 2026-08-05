from chains.rewrite_chain import rewrite_resume_chain

class RewriteAgent:
    def __init__(self, llm):
        self.llm = llm

    def run(self, resume, ats, skills, job_role:str, job_description:str):
        return rewrite_resume_chain(
            resume, ats, skills, job_role, job_description, self.llm
        ).invoke({})

