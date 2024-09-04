from .base_processor import BaseProcessor
from ..utils.config_loader import load_config
from ..prompt_template.template_loader import TemplateLoader
from service.query.config import Config
import datetime
from typing import Literal, Optional, Tuple
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain import LLMChain
from langchain_core.pydantic_v1 import BaseModel, Field
from openai import OpenAI


class QueryConstructorVector(BaseProcessor):
    def process(self, data):
        pass

    def construct(self, template, knowledge, question):
        return template.format(knowledge=knowledge, question=question)

    def __init__(self, channel):
        # self.llm = ChatOpenAI(temperature=0)
        self.llm = OpenAI(
            base_url=Config.OPENAI_BASE_URL,
            api_key=Config.OPENAI_API_KEY
        )
        self.channel = channel
        config = load_config('config/channel_config.yaml')
        channel_config = config['channels'].get(channel)
        self.self_query_retriever_template = TemplateLoader.load_template(channel_config['prompt_template_constructor'],
                                                              'self_query_retriever_template')

    def construction(self, question):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.self_query_retriever_template),
                ("human", "{question}"),
            ]
        )
        structured_llm = self.llm.with_structured_output(ServiceNowSearch)
        # query_analyzer = prompt | structured_llm
        # query_analyzer.invoke({"question": question}).pretty_print()
        construction_chain = LLMChain(prompt, structured_llm, output_key="construction")
        return construction_chain


class ServiceNowSearch:
    content_search: str = Field(
        ...,
        description="Similarity search query applied to issue description.",
    )
    title_search: str = Field(
        ...,
        description=(
            "Alternate version of the content search query to apply to issue titles. "
            "Should be succinct and only include key words that could be in a issue title."
        ),
    )
    create_time_search: Optional[datetime.date] = Field(
        None,
        description="create time filter, inclusive. Only use if explicitly specified.",
    )
    state_search: str = Field(
        None,
        description="state filter, inclusive.",
    )
    solution_search: str = Field(
        ...,
        description="Similarity search query applied to issue solution or comments.",
    )

    def pretty_print(self) -> None:
        for field in self.__fields__:
            if getattr(self, field) is not None and getattr(self, field) != getattr(
                    self.__fields__[field], "default", None
            ):
                print(f"{field}: {getattr(self, field)}")



