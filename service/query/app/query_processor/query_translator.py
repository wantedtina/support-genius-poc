from langchain_core.runnables import RunnableLambda

from .base_processor import BaseProcessor
# from langchain.prompts import ChatPromptTemplate
from ..prompt_template.template_loader import TemplateLoader
from ..utils.config_loader import load_config
from service.query.config import Config
from openai import OpenAI
from langchain.load import dumps, loads
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
from langchain import hub, LLMChain
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate


class QueryTranslator(BaseProcessor):

    def process(self, data):
        pass

    def __init__(self, channel, multi_query=False, rag_fusion=False, decomposition=False, answer_recursively=False,
                 answer_individually=False, step_back=False, hyde=False):
        # self.llm = ChatOpenAI(temperature=0)
        self.llm = OpenAI(
            base_url=Config.OPENAI_BASE_URL,
            api_key=Config.OPENAI_API_KEY
        )
        self.channel = channel
        config = load_config('config/channel_config.yaml')
        channel_config = config['channels'].get(channel)
        normal_template = TemplateLoader.load_template(channel_config['prompt_template_translator'],
                                                       'normal_template')
        self.prompt_normal = ChatPromptTemplate.from_template(normal_template)
        if rag_fusion:
            rag_fusion_template = TemplateLoader.load_template(channel_config['prompt_template_translator'],
                                                               'rag_fusion_template')
            self.prompt_rag_fusion = ChatPromptTemplate.from_template(rag_fusion_template)
        if multi_query:
            multi_query_template = TemplateLoader.load_template(channel_config['prompt_template_translator'],
                                                                'multi_query_template')
            self.prompt_multi_query = ChatPromptTemplate.from_template(multi_query_template)
        if decomposition:
            decomposition_template = TemplateLoader.load_template(channel_config['prompt_template_translator'],
                                                                  'decomposition_template')
            self.prompt_decomposition = ChatPromptTemplate.from_template(decomposition_template)
        if answer_recursively:
            answer_recursively_template = TemplateLoader.load_template(channel_config['prompt_template_translator'],
                                                                       'answer_recursively_template')
            self.prompt_answer_recursively = ChatPromptTemplate.from_template(answer_recursively_template)
        if answer_individually:
            answer_individually_template = TemplateLoader.load_template(
                channel_config['prompt_template_translator'], 'answer_individually_template')
            self.prompt_answer_individually = ChatPromptTemplate.from_template(answer_individually_template)
        if step_back:
            step_back_request_template = TemplateLoader.load_template(channel_config['prompt_template_translator'],
                                                                      'step_back_request_template')
            examples = [
                {
                    "input": "Could the members of The Police perform lawful arrests?",
                    "output": "what can the members of The Police do?",
                },
                {
                    "input": "Jan Sindel’s was born in what country?",
                    "output": "what is Jan Sindel’s personal history?",
                },
            ]
            example_prompt = ChatPromptTemplate.from_messages(
                [
                    ("human", "{input}"),
                    ("ai", "{output}"),
                ]
            )
            few_shot_prompt = FewShotChatMessagePromptTemplate(example_prompt=example_prompt, examples=examples)

            self.prompt_step_back_request = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        step_back_request_template,
                    ),
                    # Few shot examples
                    few_shot_prompt,
                    # New question
                    ("user", "{question}"),
                ]
            )

            step_back_response_template = TemplateLoader.load_template(
                channel_config['prompt_template_translator'], 'step_back_response_template')
            self.prompt_step_back_response = ChatPromptTemplate.from_template(step_back_response_template)
        if hyde:
            hyde_template = TemplateLoader.load_template(channel_config['prompt_template_translator'],
                                                         'hyde_template')
            self.prompt_hyde = ChatPromptTemplate.from_template(hyde_template)

    def get_unique_union(self, documents: list[list]):
        """ Unique union of retrieved docs """
        # Flatten list of lists, and convert each Document to string
        flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
        # Get unique documents
        unique_docs = list(set(flattened_docs))
        # Return
        return [loads(doc) for doc in unique_docs]

    def multi_query(self, question, retriever):
        generate_queries = (
                self.prompt_multi_query
                | self.llm
                | StrOutputParser()
                | (lambda x: x.split("\n"))
        )
        # retrieval_chain = generate_queries | retriever.map() | self.get_unique_union
        retrieval_chain = LLMChain(generate_queries, retriever.map(), self.get_unique_union, output_key="multi_query")
        return retrieval_chain
        # final_rag_chain = (
        #         {"context": retrieval_chain,
        #          "question": itemgetter("question")}
        #         | self.prompt_normal
        #         | self.llm
        #         | StrOutputParser()
        # )
        # return final_rag_chain.invoke({"question": question})

    def reciprocal_rank_fusion(self, results: list[list], k=60):
        """ Reciprocal_rank_fusion that takes multiple lists of ranked documents
            and an optional parameter k used in the RRF formula """

        # Initialize a dictionary to hold fused scores for each unique document
        fused_scores = {}

        # Iterate through each list of ranked documents
        for docs in results:
            # Iterate through each document in the list, with its rank (position in the list)
            for rank, doc in enumerate(docs):
                # Convert the document to a string format to use as a key (assumes documents can be serialized to JSON)
                doc_str = dumps(doc)
                # If the document is not yet in the fused_scores dictionary, add it with an initial score of 0
                if doc_str not in fused_scores:
                    fused_scores[doc_str] = 0
                # Retrieve the current score of the document, if any
                previous_score = fused_scores[doc_str]
                # Update the score of the document using the RRF formula: 1 / (rank + k)
                fused_scores[doc_str] += 1 / (rank + k)

        # Sort the documents based on their fused scores in descending order to get the final reranked results
        reranked_results = [
            (loads(doc), score)
            for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        ]

        # Return the reranked results as a list of tuples, each containing the document and its fused score
        return reranked_results

    def rag_fusion(self, retriever, question):
        generate_queries = (
                self.prompt_rag_fusion
                | ChatOpenAI(temperature=0)
                | StrOutputParser()
                | (lambda x: x.split("\n"))
        )
        retrieval_chain_rag_fusion = generate_queries | retriever.map() | self.reciprocal_rank_fusion
        # docs = retrieval_chain_rag_fusion.invoke({"question": question})
        final_rag_chain = (
                {"context": retrieval_chain_rag_fusion,
                 "question": itemgetter("question")}
                | self.prompt_normal
                | self.llm
                | StrOutputParser()
        )
        return final_rag_chain.invoke({"question": question})

    def decomposition(self, question):
        # Chain
        generate_queries_decomposition = (
                self.prompt_decomposition | self.llm | StrOutputParser() | (lambda x: x.split("\n")))
        # questions = generate_queries_decomposition.invoke({"question": question})
        decomposition_chain = LLMChain({"question": question}, generate_queries_decomposition, self.llm,
                                       StrOutputParser(),
                                       output_key="decomposition")
        return decomposition_chain

    def format_qa_pair(self, question, answer):
        """Format Q and A pair"""
        formatted_string = ""
        formatted_string += f"Question: {question}\nAnswer: {answer}\n\n"
        return formatted_string.strip()

    def get_q_a_pairs(self, questions, retriever, prompt_answer_recursively):
        q_a_pairs = ""
        for q in questions:
            rag_chain = (
                    {"context": itemgetter("question") | retriever,
                     "question": itemgetter("question"),
                     "q_a_pairs": itemgetter("q_a_pairs")}
                    | prompt_answer_recursively
                    | self.llm
                    | StrOutputParser())

            answer = rag_chain.invoke({"question": q, "q_a_pairs": q_a_pairs})
            q_a_pair = self.format_qa_pair(q, answer)
            q_a_pairs = q_a_pairs + "\n---\n" + q_a_pair
        return q_a_pairs

    def answer_recursively(self, retriever, question):
        questions = self.decomposition(question)
        return self.get_q_a_pairs(questions, retriever, self.prompt_answer_recursively)

    def retrieve_and_rag(self, retriever, question):
        """RAG on each sub-question"""
        # RAG prompt
        prompt_rag = hub.pull("rlm/rag-prompt")
        # Use our decomposition /
        sub_questions = self.decomposition(question)

        # Initialize a list to hold RAG chain results
        rag_results = []

        for sub_question in sub_questions:
            # Retrieve documents for each sub-question
            retrieved_docs = retriever.get_relevant_documents(sub_question)
            # Use retrieved documents and sub-question in RAG chain
            answer = (prompt_rag | self.llm | StrOutputParser()).invoke({"context": retrieved_docs,
                                                                         "question": sub_question})
            rag_results.append(answer)
        return rag_results, sub_questions

    def format_qa_pairs(self, questions, answers):
        """Format Q and A pairs"""
        formatted_string = ""
        for i, (question, answer) in enumerate(zip(questions, answers), start=1):
            formatted_string += f"Question {i}: {question}\nAnswer {i}: {answer}\n\n"
        return formatted_string.strip()

    def answer_individually(self, retriever, question):
        answers, questions = self.retrieve_and_rag(retriever, question)
        context = self.format_qa_pairs(questions, answers)
        final_rag_chain = (self.prompt_answer_individually | self.llm | StrOutputParser())
        return final_rag_chain.invoke({"context": context, "question": question})

    def step_back(self, retriever, question):
        generate_queries_step_back = self.prompt_step_back_request | ChatOpenAI(temperature=0) | StrOutputParser()
        chain = (
                {
                    # Retrieve context using the normal question
                    "normal_context": RunnableLambda(lambda x: x["question"]) | retriever,
                    # Retrieve context using the step-back question
                    "step_back_context": generate_queries_step_back | retriever,
                    # Pass on the question
                    "question": lambda x: x["question"],
                }
                | self.prompt_step_back_response
                | ChatOpenAI(temperature=0)
                | StrOutputParser()
        )
        return chain.invoke({"question": question})

    def hyde(self, retriever, question):
        generate_docs_for_retrieval = (self.prompt_hyde | ChatOpenAI(temperature=0) | StrOutputParser())
        # Retrieve
        retrieval_chain = generate_docs_for_retrieval | retriever
        retrieved_docs = retrieval_chain.invoke({"question": question})
        final_rag_chain = (self.prompt_normal | self.llm | StrOutputParser())

        return final_rag_chain.invoke({"context": retrieved_docs, "question": question})
