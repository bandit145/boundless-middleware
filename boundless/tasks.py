from celery import Celery, shared_task, Task
import importlib
import boundless.utility as util
import re
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
    # black formatting error
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


def check_subversive_comments(text_blob):
    pass


# write a test for this as a place to start
@shared_task(base=DatabasesTask)
def analyze_message(msg):
    es = analyze_message.es
    db = analyze_message.db
    query = {"match": {"hash": msg["hash"]}}
    result = es.con.search(es.get_active_index(INDEX_NAME), body=query)
    user = db.query(mainway.Poi).filter(
        getattr(mainway.Poi, f'{msg["server_type"]}_id') == msg["user_id"]
    )
    srv = db.query(mainway.Server).filter(mainway.Server.server_id == msg["server_id"])
    bad_words = [
        x.word
        for x in db.query(mainway.SubversiveWord)
        .filter(SubversiveWord.server_id == srv.id)
        .all()
    ]
    # TODO: use https://stackoverflow.com/questions/20199462/sqlalchemy-postgresql-pg-regex
    # to check if word exists
    for word in actual_msg.words():
        if word.lower in bad_words:
            if actual_msg.sentiment[0] > 0.50:
                user.neg_comments += 1
                break
            elif actual_msg.sentiment[0] < 0.50:
                user.pos_comments += 1
                break
    db.commit()
