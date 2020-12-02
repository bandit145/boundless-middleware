from boundless.databases import ElasticsearchConnector
from elasticsearch7 import Elasticsearch
import atexit
import os


def remove_all_indices():
    es = Elasticsearch(nodes=["localhost"], use_ssl=False)
    [es.indices.delete(x) for x in es.indices.get("*").keys()]


if not os.getenv("CLEANUP"):
    atexit.register(remove_all_indices)


def test_get_active_index_creation():
    elastic = ElasticsearchConnector(nodes=["localhost"], use_ssl=False)
    elastic.create_index("wiretap")
    elastic.create_index("wiretap")
    elastic.create_index("wiretap")
    assert elastic.get_active_index("wiretap") == "wiretap_3"


def test_index_rotation():
    es = Elasticsearch(["localhost"])
    elastic = ElasticsearchConnector(nodes=["localhost"], use_ssl=False)
    elastic.create_index("test_rotate")
    elastic.rotate_index("test_rotate")
    assert elastic.get_active_index("test_rotate") == "test_rotate_2"
    assert es.indices.get("test_rotate_1")["test_rotate_1"]["settings"]["index"][
        "blocks"
    ]["write"]


def test_message_insert():
    elastic = ElasticsearchConnector(nodes=["localhost"], use_ssl=False)
    index = elastic.get_active_index("wiretap")
