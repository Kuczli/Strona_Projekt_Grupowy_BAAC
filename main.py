from flask import Flask, render_template, request,Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils.functions import database_exists, create_database
from flask_mail import Mail,Message
from prometheus_client import Histogram, generate_latest, CollectorRegistry
from prometheus_client import multiprocess
import ast
import time

import os

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor


app = Flask("foto_service")
app.secret_key = "dsfSDF8SD76FD6SF76SDA8F6SDA8DF69A"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='vassilli.zaitsev@gmail.com',
    MAIL_PASSWORD='qplzxmdxmzakrwei'
)
db = SQLAlchemy(app)

mail = Mail(app)



class customer(db.Model):
    id= db.Column(db.Integer,primary_key =True)
    name = db.Column(db.String(120),nullable=False)
    email = db.Column(db.String(120),nullable=False)
    checkopt1 = db.Column(db.Boolean,nullable = True,default=False)
    checkopt2 = db.Column(db.Boolean,nullable = True,default=False)
    checkopt3 = db.Column(db.Boolean,nullable = True,default=False)
    message = db.Column(db.String,nullable = False)
    
    
def get_tracer(service_name, jaeger_host):
    trace.set_tracer_provider(
        TracerProvider(resource=Resource.create({SERVICE_NAME: service_name}))
    )
    tracer = trace.get_tracer(service_name)

    # create a JaegerExporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=jaeger_host,
        agent_port=6831,
    )

    # Create a BatchSpanProcessor and add the exporter to it
    span_processor = BatchSpanProcessor(jaeger_exporter)

    # add to the tracer, for debugging if needed
    #
    #
    # from opentelemetry.sdk.trace.export import (SimpleSpanProcessor, ConsoleSpanExporter)
    #
    # SimpleSpanProcessor(ConsoleSpanExporter())
    trace.get_tracer_provider().add_span_processor(span_processor)
    return 

class MetricCollector:
    def observe_myself(self, path, method, status_code, duration):
        self._me.labels(path=path, method=method, status_code=status_code).observe(
            duration
        )
    def observe_db(self, status_code, sql_state, duration):
        self._db.labels(status_code=status_code, sql_state=sql_state).observe(duration)

    def observe_external(self, status_code, duration):
        self._external.labels(status_code=status_code).observe(duration)

    def get_latest(self):
        return generate_latest()

    @staticmethod
    def newCollector(service_name):
        prefix = service_name.replace("-", "_")
        STATUS_CODE = "status_code"
        PATH = "path"
        HTTP_METHOD = "method"

        about_me = Histogram(
            prefix + "_duration_seconds",
            service_name + " latency request distribution",
            [PATH, HTTP_METHOD, STATUS_CODE],
            buckets=(0.1, 0.25, 0.5, 0.75, 0.90, 1.0, 2.5),
        )

        about_db = Histogram(
            prefix + "_database_duration_seconds",
            "database latency request distribution",
            [STATUS_CODE, "sql_state"],
            buckets=(0.1, 0.25, 0.5, 0.75, 0.90, 1.0, 2.5),
        )

        about_her = Histogram(
            prefix + "_audit_duration_seconds",
            "audit service latency request distribution",
            [STATUS_CODE],
            buckets=(0.1, 0.25, 0.5, 0.75, 0.90, 1.0, 2.5),
        )

        mc = MetricCollector()
        mc._me = about_me
        mc._db = about_db
        mc._external = about_her
        return mc


def get_collector(name):
    return MetricCollector.newCollector(name)

def add_routes(app, collector,tracer):
    @app.route("/",methods=['GET', 'POST'])
    def home():
        if request.method == 'POST':
            name = request.form.get('inlineFormInputName2')
            email = request.form.get('inlineFormInputGroupUsername2')
            emailtoSend = name+ "@"+email
            checkopt1 = False
            checkopt2 = False
            checkopt3 = False
            if request.form.get('checkopt1') != None:
                checkopt1 =True
            if request.form.get('checkopt1') != None:
                checkopt2 =True
            if request.form.get('checkopt1') != None:
                checkopt3 = True
            message = request.form['comment']
            
            cu = customer(name = name,email = email,checkopt1 = checkopt1,checkopt2=checkopt2,checkopt3=checkopt3,message=message)
            try:
                work_with_db(db,cu,collector,tracer)
            except RuntimeError as re:
                r = Response("{0}".format(re), mimetype="text/plain")
                r.status_code = 503
                return r
                

            subject = 'Kurs fotografii'
            name = name
            message = message
            recipients = ['vassilli.zaitsev@gmail.com']
            mesage_to_admin = Message(subject=subject,
                                  sender=app.config.get("MAIL_USERNAME"),
                                  recipients=recipients,  # replace with your email for testing
                                  body="Message from: " + name + "\n" + "email: " + email + "\n" + "Message:" + message)
            message_to_sender = Message(subject="Dziękuje za wysłanie wiadomośći",
                                    sender=app.config.get("MAIL_USERNAME"),
                                    recipients=list(emailtoSend.split(" ")), # replace with your email for testing
                                    body="Dziękuję za wiadomość, wkrótce odpiszę")
            mail.send(mesage_to_admin)
            mail.send(message_to_sender)

        return render_template('home.html')
        
def work_with_db(db,customer_data,collector,tracer):
    with tracer.start_as_current_span("db_query"):
    	if not database_exists('sqlite:///customers'):
    		create_database('sqlite:///customers')
    	start_time = time.time()

    	db_sleep = float(request.args.get("db_sleep", 0))
    	is_db_error = ast.literal_eval(request.args.get("is_db_error", "False"))

    	try:
        	call_db(db,customer_data,db_sleep, is_db_error)
        	latency = time.time() - start_time
        	collector.observe_db("0", "0", latency)
    	except RuntimeError as re:
        	"""
        	"""
        	latency = time.time() - start_time
        	collector.observe_db("1001", "HY000", latency)
        	raise re


def call_db(db,customer_data,db_sleep, is_error):
    db.session.add(customer_data)
    db.session.commit()


def instrument_requests(app, collector):
    import time

    def before():
        request.start_time = time.time()

    def after(response):
        if request.path != "/metrics":
            request_latency = time.time() - request.start_time
            collector.observe_myself(
                request.path, request.method, response.status_code, request_latency
            )
        return response

    app.before_request(before)
    app.after_request(after)

 
def add_metrics_route(app, collector):
    @app.route("/metrics", strict_slashes=False, methods=["GET"])
    def metrics_rotue():
        # txt = generate_latest()
        txt = get_latest_when_running_with_gunicorn()
        return Response(txt, mimetype="text/plain")

def get_latest_when_running_with_gunicorn():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return generate_latest(registry)

def get_app():
    c = get_collector("foto-mgmt")
    tracer = get_tracer("foto_service", 'localhost')
    add_routes(app, c,tracer)
    add_metrics_route(app, c)
    instrument_requests(app, c)
    mail = Mail(app)
    FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()
    return app

if __name__ == '__main__':
    app = get_app()
    app.run(host="0.0.0.0", port=8081)
    


