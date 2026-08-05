from pydantic import BaseModel
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from prompts.prompt_reader import get_ats_prompt

class ATSResponse(BaseModel):
    ats_score: int
    strengths: List[str]
    weaknesses: List[str]
    missing_keywords: List[str]
    improvements: List[str]
    summary: str


def analyze_resume_chain(resume_text: str, llm):
    prompt = ChatPromptTemplate.from_messages([
        ("human",
         f"System: {get_ats_prompt()}\nResume:\n{resume_text}")
    ])

    structured_llm = llm.with_structured_output(ATSResponse)
    return prompt | structured_llm