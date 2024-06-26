import os
from llama_index.core import (SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage)
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI

class PaperInquirer:
    def __init__(self, resource_dirs, storage_dir=""):
        self._agent = None
        self.query_engine_tools = None
        self.file_list = []
        self.load(resource_dirs, storage_dir)

    def load(self, resource_dirs, storage_dir=""):
        if not isinstance(resource_dirs, list):
            resource_dirs = [resource_dirs]
        query_indices_info = self._create_query_indices_info(resource_dirs, storage_dir)
        query_engines_info = self._create_query_engines_info(query_indices_info)
        self.query_engine_tools = self._create_query_engine_tools(query_engines_info)

    def inquire(self, question):
        response = ""
        if self.query_engine_tools is not None:
            agent = self._get_agent(self.query_engine_tools)
            response = agent.chat(self._embellish_question(question))
        else:
            raise ValueError("No query engine tools loaded")
        return str(response)

    def _get_agent(self, query_engine_tools):
        if self._agent is None:
            llm = OpenAI(model="gpt-3.5-turbo-0613")
            self._agent = ReActAgent.from_tools(
                query_engine_tools,
                llm=llm,
                verbose=True
            )

        return self._agent

    def _create_query_indices_info(self, resource_dirs, storage_dir):
        indices_list = []
        for resource_dir in resource_dirs:
            resource_dir = self._get_valid_dir(resource_dir)
            for file in os.listdir(resource_dir):
                suffix = file.split(".")[-1]
                if self.is_valid_suffix(suffix):
                    self.file_list.append(file)
                    doc_index = self._load_index(storage_dir + file.split("." + suffix)[0])
                    if doc_index is None:
                        doc = SimpleDirectoryReader(
                            input_files=[resource_dir + file]
                        ).load_data()
                        doc_index = VectorStoreIndex.from_documents(doc)
                        if storage_dir:
                            storage_dir = self._get_valid_dir(storage_dir)
                            doc_index.storage_context.persist(persist_dir=storage_dir + file.split("." + suffix)[0])
                    doc_index_info = {'name': self.remove_space(self._remove_hyphen(file.split("." + suffix)[0])),
                                      'index': doc_index}
                    indices_list.append(doc_index_info)

        return indices_list

    def _embellish_question(self, question):
        embellished_question = ""
        if len(self.file_list):
            embellished_question += "You have to use "
            for file_index in range(len(self.file_list)):
                embellished_question += self.file_list[file_index].split(".")[0]
                if file_index < len(self.file_list) - 1:
                    if file_index == len(self.file_list) - 2:
                        embellished_question += " and "
                    else:
                        embellished_question += ", "
            embellished_question += " resources to answer the following question: " + question
        else:
            embellished_question = question

        return embellished_question + " Think step by step."

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
            engine_info = {'name': index_info['name'], 'engine': engine}
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
                    description=query_engine_info['name']
                    ),
                )
            )
        return tools_info_list

    @staticmethod
    def _get_valid_dir(directory):
        if not os.path.isdir(directory):
            raise ValueError(f'{directory} is not a directory')
            return ""
        if not directory.endswith(os.path.sep):
            directory += os.path.sep
        return directory

    @staticmethod
    def is_valid_suffix(suffix):
        return suffix in ["pdf", "txt", "sbml"]

    @staticmethod
    def _remove_hyphen(file_name):
        return file_name.replace("-", "_")

    @staticmethod
    def remove_space(file_name):
        return file_name.replace(" ", "_")
