from confluence_source import ConfluenceSource
from sn_source import ServiceNowSource

class DataSource:
    def process(self, data):
        raise NotImplementedError("Subclasses should implement this!")

def get_data_source(processor_name):
    processors = {
        "confluence_processor": ConfluenceSource(),
        "service_now_processor": ServiceNowSource(),
        # 继续添加其他处理器
    }
    return processors.get(processor_name)
