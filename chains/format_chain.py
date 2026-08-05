import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_core.messages import SystemMessage, HumanMessage
from prompts.prompt_reader import get_format_prompt
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI( model="gemini-2.5-flash",
    temperature=0)

def format_resume_chain(resume):
    system_prompt = get_format_prompt()
    resume_json = resume.model_dump_json(indent=2)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Generate the HTML resume for the following data:\n\n{resume_json}")

    ] 
    response = llm.invoke(messages,max_tokens=65000)
    html_output = response.content

    if not isinstance(html_output,str):
        html_output = str(html_output)
    if "<!DOCTYPE html>" in html_output:
        html_output = html_output[html_output.index("<!DOCTYPE html>"):]

    return html_output
