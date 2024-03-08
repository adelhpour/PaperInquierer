import os
from llama_index.core import (SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage)
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI

class PaperInquirer:
    def __init__(self, pdf_dir, description_dir="", storage_dir=""):
        self.query_engine_tools = None
        self.load(pdf_dir, description_dir, storage_dir)

    def load(self, pdf_dir, description_dir="", storage_dir=""):
        pdf_dir = self._get_valid_dir(pdf_dir)
        if pdf_dir:
            query_indices_info = self._create_query_indices_info(pdf_dir, description_dir, storage_dir)
            query_engines_info = self._create_query_engines_info(query_indices_info)
            self.query_engine_tools = self._create_query_engine_tools(query_engines_info)

    def inquire(self, question):
        response = ""
        if self.query_engine_tools is not None:
            agent = self._get_agent(self.query_engine_tools)
            response = agent.chat(question)
        else:
            raise ValueError("No query engine tools loaded")
        return str(response)

    @staticmethod
    def _get_agent(query_engine_tools):
        llm = OpenAI(model="gpt-3.5-turbo-0613")
        agent = ReActAgent.from_tools(
            query_engine_tools,
            llm=llm
        )
        return agent

    def _create_query_indices_info(self, pdf_dir, description_dir, storage_dir):
        indices_list =[]
        for file in os.listdir(pdf_dir):
            if file.endswith(".pdf"):
                doc_index = self._load_index(storage_dir + file.split(".pdf")[0])
                if doc_index is None:
                    doc = SimpleDirectoryReader(
                        input_files=[pdf_dir + file]
                    ).load_data()
                    doc_index = VectorStoreIndex.from_documents(doc)
                    if storage_dir:
                        storage_dir = self._get_valid_dir(storage_dir)
                        doc_index.storage_context.persist(persist_dir=storage_dir + file.split(".pdf")[0])
                doc_index_info = {'name': self._remove_hyphen(file.split(".pdf")[0]), 'index': doc_index,
                                  'description': self._get_description_info(description_dir, file.split(".pdf")[0])}
                indices_list.append(doc_index_info)
        return indices_list

    @staticmethod
    def _load_index(file_name):
        try:
            storage_context = StorageContext.from_defaults(
                persist_dir=file_name
            )
            return load_index_from_storage(storage_context)
        except:
            return None

    @staticmethod
    def _create_query_engines_info(indices_info):
        engines_info_list = []
        for index_info in indices_info:
            engine = index_info['index'].as_query_engine(similarity_top_k=3)
            engine_info = {'name': index_info['name'], 'description': index_info['description'], 'engine': engine}
            engines_info_list.append(engine_info)
        return engines_info_list

    @staticmethod
    def _create_query_engine_tools(query_engines_info):
        tools_info_list = []
        for query_engine_info in query_engines_info:
            tools_info_list.append(
                QueryEngineTool(
                    query_engine=query_engine_info['engine'],
                    metadata=ToolMetadata(
                    name=query_engine_info['name'],
                    description=query_engine_info['description']
                    ),
                )
            )
        return tools_info_list

    def _get_description_info(self, description_dir, file):
        description_info = ""
        if description_dir:
            description_dir = self._get_valid_dir(description_dir)
            abstract_file = description_dir + file + ".txt"
            try:
                with open(abstract_file, 'r') as file_name:
                    return file_name.read()
            except:
                description_info = ""
        return description_info

    @staticmethod
    def _get_valid_dir(directory):
        if not os.path.isdir(directory):
            raise ValueError(f'{directory} is not a directory')
            return ""
        if not directory.endswith(os.path.sep):
            directory += os.path.sep
        return directory

    @staticmethod
    def _remove_hyphen(file_name):
        return file_name.replace("-", "_")
