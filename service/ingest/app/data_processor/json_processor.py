from .base_processor import BaseProcessor
from datetime import datetime
from .mul_representation_indexing import MulReprenIndexing
import json
from langchain.schema import Document

class JsonProcessor(BaseProcessor):
    def process(self, data):
        #Chunking
        combined_data = []
        for item in data:
            if 'create_time' in item:
                item['create_time'] = self.convert_iso_to_custom_format(item['create_time']).strftime('%Y-%m-%d %H:%M:%S')
            content = json.dumps(item)
            # print("content: " + content)
            doc = Document(page_content=content, metadata={'timestamp': self.convert_iso_to_custom_format(item['create_time']).timestamp()})
            combined_data.append(doc)
        #Multi-representation Indexing
        # MulReprenIndexing()
        return combined_data

    def convert_iso_to_custom_format(self, iso_string):
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return dt
