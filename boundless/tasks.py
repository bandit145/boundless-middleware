from celery import Celery, shared_task, Task
import textblob
import importlib
import boundless.utility as util
from boundless.databases import ElasticsearchConnector, INDEX_NAME
import boundless.mainway_objects as mainway
import os
import sys


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config["celery_result_backend"],
        backend=app.config["celery_broker_url"],
    )
    celery.conf.update(app.config["celery_config"])
    #black formatting error
    # class ContextTask(Task):
    #    	def __call__(self, *args, **kwargs):
    #        	with app.app_context():
    #            	return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery


class DatabasesTask(Task):
    _db = None
    _es = None
    _es_config = None
    _db_config = None

    def read_confg(self):
        location = os.getenv("BOUNDLESS_CONF")
        sys.path.append(location)
        conf = importlib.import_module(location.split("/")[-1])
        self._es_config = conf["elasticsearch_connection"]
        self._db_config = conf["sql_connection_string"]

    @property
    def db(self):
        if not self._db:
            self._db = util.load_db_session(self._db_config)
        return self._db

    @property
    def es(self):
        if not self._es:
            self._es = ElasticsearchConnector(**self._es_config)
        return self._es


# write a test for this as a place to start
@shared_task(base=DatabasesTask)
def analyze_message(msg):
    es = analyze_message.es
    query = {"match": {"hash": msg["hash"]}}
    result = es.con.search(es.get_active_index(INDEX_NAME), body=query)
