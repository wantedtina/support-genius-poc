class DataProcessor:
    def process(self, data):
        raise NotImplementedError("Subclasses should implement this!")

class ConfluenceProcessor(DataProcessor):
    def process(self, data):
        # Confluence数据处理逻辑
        pass

class ServiceNowProcessor(DataProcessor):
    def process(self, data):
        # Service Now数据处理逻辑
        pass

def get_data_processor(processor_name):
    processors = {
        "confluence_processor": ConfluenceProcessor(),
        "service_now_processor": ServiceNowProcessor(),
        # 继续添加其他处理器
    }
    return processors.get(processor_name)
