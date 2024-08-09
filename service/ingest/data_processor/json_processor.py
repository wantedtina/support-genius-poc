from base_processor import BaseProcessor
from datetime import datetime
from mul_representation_indexing import MulReprenIndexing
import json

class JsonProcessor(BaseProcessor):
    def process(self, data):
        #Chunking
        processed_data = []
        for item in data:
            if 'create_time' in item:
                item['create_time'] = self.convert_iso_to_custom_format(item['create_time']).strftime('%Y-%m-%d %H:%M:%S')
            content = json.dumps(item)
            processed_data.append(content)
        #Multi-representation Indexing
        MulReprenIndexing()
        return processed_data

    def convert_iso_to_custom_format(self, iso_string):
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return dt
