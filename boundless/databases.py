from elasticsearch7 import Elasticsearch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import textblob

INDEX_NAME = "boundless"


class ElasticsearchConnector:
    def __init__(self, **kwargs):
        if "use_ssl" not in kwargs.keys():
            use_ssl = True
        else:
            use_ssl = kwargs["use_ssl"]
        if "verify_tls" not in kwargs.keys():
            verify_tls = True
        else:
            verify_tls = kwargs["verify_tls"]
        if "ca_certs" not in kwargs.keys():
            ca_certs = None
        else:
            ca_certs = kwargs["ca_certs"]
        self.con = Elasticsearch(
            kwargs["nodes"], use_ssl=use_ssl, verify_tls=verify_tls, ca_certs=ca_certs
        )

    def create_index(self, index_name):
        indices = self.es.indices.get(index=f"{index_name}_*")
        self.con.indices.create(index=f"{index_name}_{len(indices) + 1}")

    def rotate_index(self, index_name):
        active = self.get_active_index(index_name)
        self.create_index(index_name)
        self.con.indices.add_block(active, "write")

    def get_indices(self, name=None):
        return [x for x in self.con.indices.get(index=name).keys()]

    def get_active_index(self, index_name):
        indices = self.con.indices.get(index=f"{index_name}_*")
        index_list = list(indices.keys())
        return index_list[len(index_list) - 1]

    def insert_message(self, message, index_name):
        index = self.get_active_index(index_name)
        self.con.index(index=index_name, body=message)
