from service.query.app.data_retrieval.reranking import Reranking
from service.query.app.data_retrieval.reretrieval import Reretrieval

class RetrievalProcessor:
    def process(self, data):
        raise NotImplementedError("Subclasses should implement this!")

def get_retrieval_processor(processor_name):
    processors = {
        "reranking_processor": Reranking(),
        "service_now_processor": Reretrieval(),
        # 继续添加其他处理器
    }
    return processors.get(processor_name)
