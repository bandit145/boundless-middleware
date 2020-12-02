from flask import Flask, request
from flask_restx import Api, Resource, fields
from boundless.databases import ElasticsearchConnector, Mainway
from marshmellow.exceptions import ValidationError 
import boundless.schema as schema, metadata
import boundless.mainway_objects as db_objs  
import sqlalchemy
import actions
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
api = Api(app)

def load_db_session(config):
	engine = sqlalchemy.create_engine(config['sql_connection_string'])
	db_objs.Base.metadata.create_all(engine)
	return sessionmaker(bind=engine)()

app.config.from_envvar('BOUNDLESS_SETTINGS')
app.es = ElasticsearchConnector(**app.config['elasticsearch_connection'])
app.mainway = load_db_session(app.config)


message = api.model('Message', {
	'hash': fields.String(description='Unique sha256 hash of the message'),
	'body': fields.String(description='Contents of the message'),
	'metadata': fields.Dict(readonly=True, description='relevent metadata with message')
	})


#more to come
report = api.model('Report', {
	'service': fields.String(description='service to search by id'),
	'id': fields.String(description='id to search by'),
	'incidents': fields.Dict(description='incidents user has been in')
	})

message_job = api.model('MessageJob', {
	'id': fields.String(description='job id of running job')
	})


@api.route('/message')
class Message(Resource):
	#this will return a job id to lookup later
	@api.doc('kick off a message/message search job and respond with job id')
	@api.marshal_with(message_job)
	def post(self):
		try:
			msg = schema.MessageRequest(**api.payload)
			return actions.search_messages(msg), 200
		except ValidationError as error:
			return {'error': error.message}, 400

	@api.doc('get results of message search job')
	@api.marshal_with_list(message)
	def get(self):
		job_id = request.args.get('id')

@api.route('/report')
class Report(Resource):
	@api.doc('generate mainway report on a user')
	@api.marshal_with(report)
	def post(self):
		try:
			msg = schema.ReportRequest(**api.payload)
			actions.generate_report(msg)
			
		except ValidationError as error:
			return {'error': error.message}, 400


