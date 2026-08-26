import os


PROMPT_DIR = os.path.dirname(os.path.abspath(__file__))


def read_prompt(filename: str) -> str:
    path = os.path.join(PROMPT_DIR, filename)

    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def get_ats_prompt():
    return read_prompt("ats_prompt.md")


def get_skills_prompt():
    return read_prompt("skills_prompt.md")


def get_interview_prompt():
    return read_prompt("interview_prompt.md")


def get_evaluation_prompt():
    return read_prompt("evaluation_prompt.md")


def get_rewrite_prompt():
    return read_prompt("rewrite_prompt.md")


def get_format_prompt():
    return read_prompt("format_prompt.md")