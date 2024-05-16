#!/usr/bin/env python
from fastapi import FastAPI
from langchain_openai import  ChatOpenAI
from langserve import add_routes


#input libs
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
#parser libs
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
#prompt libs
from langchain_core.prompts import PromptTemplate

#init
model_name = 'gpt-4-turbo'
model = ChatOpenAI(model=model_name)

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)
#

#parser block
class candidate(BaseModel): 
    name: str = Field(description ='Name of the candidate')
    surname: str = Field(description = 'Surname of the candidate')
    gender: str = Field(description = 'Gender of the candidate. Possible values: ["Male", "Female", "Unknown"]')

    dateOfBirth: int = Field(description='Date of Birth of the candidate in unixtime')
    personalEmail: str = Field(description='Personal email of the candidate')
    phone: str = Field(description='Phone number of the candidate')
    education: str = Field(description='Education details of the candidate')
    experience: str = Field(description='Experience details of the candidate')
    softSkills: str = Field(description='List of soft skills of the candidate')
    hardSkills: str = Field(description='List of hard skills of the candidate')

    score: int = Field(description = 'On score 0-10 how good this candidate is suitable to this vacancy.')
    score_desciption: int = Field(description = 'Why did you decide this candidate is suitable or not.')

parser = JsonOutputParser(pydantic_object=candidate)
#

#prompt block
request = "Help me with this candidate please."
prompt = PromptTemplate(
    template ="You are a recruiter in IT Company. I will give you both - vacancy description and a candidate description. Candidate must know/be suitable for the most requierments in the vacancy description, if not - in most cases he is not suitable. You need to answer with a schema.\nVacancy: {vacancy}\nCandidate: {context}\n{format_instructions}",
    input_variables =["vacancy","context"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)
#
#github gitlab pdf doc googledoc
def pdfloader(obj):
    print('started pdfloader')
    print(obj)
    if obj['type']=='pdf':
        loader = PyPDFLoader(obj['fileUrl'])
    elif obj['type']=='docx':
        loader = Docx2txtLoader(obj['fileUrl'])
    pages = loader.load()
    print('end pdfloader')
    return { "context":pages[0], 'vacancy':obj['vacancyText'], 'fileUrl':obj['fileUrl'], "type":obj['type'] }

add_routes(
    app,
    pdfloader | prompt | model | parser,
    path="/openai",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)