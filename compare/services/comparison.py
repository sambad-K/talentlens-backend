from pypdf import PdfReader

from .llm import evaluate_resume


def make_comparison(file, vacancy):
    reader = PdfReader(file)

    resume_text = "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )

    return evaluate_resume(
        resume_text=resume_text,
        vacancy=vacancy
    )