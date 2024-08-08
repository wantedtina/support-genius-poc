from confluence_processor import ConfluenceProcessor
from sn_processor import ServiceNowProcessor

class RetrievalProcessor:
    def process(self, data):
        raise NotImplementedError("Subclasses should implement this!")

def get_retrieval_processor(processor_name):
    processors = {
        "confluence_processor": ConfluenceProcessor(),
        "service_now_processor": ServiceNowProcessor(),
        # 继续添加其他处理器
    }
    return processors.get(processor_name)
