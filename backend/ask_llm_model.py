from config_loader import AppConfig
from langchain_openai import OpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain, RetrievalQA
from langchain.chains.summarize import load_summarize_chain
from langchain_community.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
#from langchain_community.embeddings import HuggingFaceInstructEmbeddings
import json
config=AppConfig()
class LanguageProcessing:
    def __init__(self, openai_api_key=config.openai_api_key, temperature=0.2):
        self.llm = OpenAI(openai_api_key=openai_api_key, temperature=temperature, verbose=True)
        self.temperature = temperature

    def predict_task_type(self, filetype, query):
        generic_template = '''
        Consider yourself as a chatbot. A user has provided a {filetype} file and asked to perform a task. Below, I have mentioned the task description and provided different options. You need to predict which type of task this is from the below options only. Task Description: `{task_desc}` The options are below:

    1. Question Answering
    2. Summarization
    3. Classification
    4. Sentiment_Analysis
    5. Named_Entity_Recognition
    6. Translation
    7. Text_Generation
    8. Content_Enhancement
    9. Keyword_Extraction
    10. Other (Please specify if the task involves content creation or processing beyond text, such as generating images or visual content from text descriptions.)

    You can select "Other" if the first 9 options do not accurately describe the task type. Select from the first 9 options only if you are 100 percent sure. If selecting "Other," please provide a brief explanation.

    Please give the output in a JSON format where the key is "task_type" and the value is the chosen option. If "Other" is selected, include an "explanation" key with a brief description of the task.
        '''  # Your existing template string here
        prompt = PromptTemplate(input_variables=['filetype', 'task_desc'], template=generic_template)
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        result = llm_chain.run({'filetype': filetype, 'task_desc': query})
        print(type(result))
        parsed_json = json.loads(result)
        task_type = parsed_json['task_type']
        return task_type

    def do_embedding(self, info_text):
       # instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")
        openai_embedding=OpenAIEmbeddings()
        vectordb = FAISS.from_documents(documents=info_text, embedding=openai_embedding)
        return vectordb

    def summarize_text(self, info_chunk, query_value):
        chunks_prompt = ''' 
        {query}
        Speech:`{text}'
        Summary:
        '''
        map_prompt_template = PromptTemplate(input_variables=['text'], template=chunks_prompt.format(query=query_value, text="{text}"))
        summary_chain = load_summarize_chain(llm=self.llm, chain_type='map_reduce', map_prompt=map_prompt_template, verbose=False)
        output = summary_chain.run(info_chunk)
        return output

    def question_answering(self, vector_db, query_value):
        retriever = vector_db.as_retriever(score_threshold=0.7)
        prompt_template = ''' 
        Given the following context and a question, generate an answer based on this context only.
        In the answer try to provide as much text as possible from "response" section in the source document context without making much changes.
        If the answer is not found in the context, kindly state "I don't know." Don't try to make up an answer.

         CONTEXT: {context}

         QUESTION: {question}
         '''
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=retriever, input_key="query", return_source_documents=True, chain_type_kwargs={"prompt": PROMPT})
        json_result = chain(query_value)
        result=json_result['result']

        return result

