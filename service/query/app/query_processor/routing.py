from .base_processor import BaseProcessor
from ..utils.config_loader import load_config
from ..prompt_template.template_loader import TemplateLoader
from ..knowledge_indexer import KnowledgeIndexer
from service.query.config import Config
from service.query.tools.prompt_loader import PromptLoader

from typing import Literal
from openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain import LLMChain

knowledge_indexer_confluence = KnowledgeIndexer('data', 'faiss_index/confluence', 'pdf')
knowledge_indexer_sn = KnowledgeIndexer('data', 'faiss_index/serviceNow', 'json')

# Load prompt template from yaml file
prompt_template_confluence = PromptLoader(Config.PROMPT_PATH).load_prompt("prompt_confluence", "extract_query")
prompt_template_sn = PromptLoader(Config.PROMPT_PATH).load_prompt("prompt_sn", "extract_query")


# llm = OpenAI(
#     base_url=Config.OPENAI_BASE_URL,
#     api_key=Config.OPENAI_API_KEY
# )

class Routing(BaseProcessor):

    def process(self, data):
        pass

    def __init__(self, channel):
        # self.llm = ChatOpenAI(temperature=0)
        self.llm = OpenAI(
            base_url=Config.OPENAI_BASE_URL,
            api_key=Config.OPENAI_API_KEY
        )
        self.channel = channel
        self.prompt_template = ''
        self.knowledge_text = ''
        config = load_config('config/channel_config.yaml')
        channel_config = config['channels'].get(channel)
        logic_routing_template = TemplateLoader.load_template(channel_config['prompt_template_routing'],
                                                              'logic_routing_template')
        self.prompt_logic_routing = ChatPromptTemplate.from_messages(
            [
                ("system", logic_routing_template),
                ("human", "{question}"),
            ]
        )

    def route(self, question):
        router = self.prompt_logic_routing | self.llm.with_structured_output(RouteQuery)
        result = router.invoke({"question": question})
        return result.datasource

    def choose_route(self, question):
        if "confluence" in self.route(question).lower():
            print("chain for confluence_docs")
            relevant_docs = knowledge_indexer_confluence.search2("confluence", question)
            self.prompt_template = prompt_template_confluence
            self.knowledge_text = "\n".join(relevant_docs)
        elif "serviceNow" in self.route(question).lower():
            print("chain for serviceNow_docs")
            relevant_docs = knowledge_indexer_sn.search2("serviceNow", question)
            self.prompt_template = prompt_template_sn
            for doc in relevant_docs:
                self.knowledge_text += doc.page_content + "\n"

        print("knowledge_text: " + self.knowledge_text)
        # prompt_route = ChatPromptTemplate.from_template(prompt_template)
        prompt_route = self.prompt_template.format(knowledge=self.knowledge_text, question=question)

        # route = (prompt_route | self.llm | StrOutputParser())
        # route_prompt = prompt_template.format(knowledge=knowledge_text, question=question)
        # route_chain = ({"knowledge": knowledge_text, "question": question} | route | self.llm | StrOutputParser())
        route_chain = LLMChain({"knowledge": self.knowledge_text, "question": question}, prompt_route, self.llm,
                               StrOutputParser(),
                               output_key="route")

        return route_chain


class RouteQuery:
    datasource: Literal["confluence", "serviceNow"] = Field(
        ...,
        description="Given a user question choose which datasource would be most relevant for answering their question",
    )
