from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.sql import func
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)
api = Api(app)

# Model to represent the messages in the database
class MessageModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=False)
    read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=func.now())

    def __repr__(self):
        return f'Message(recipient = {self.recipient}, message = {self.message})'

# Create the database    
with app.app_context():
    db.create_all()

# Helper to make sure recipient is non-empty
def non_empty_string(value):
    value = str(value).strip()
    if not value:
        raise ValueError("Field cannot be empty")
    return value

# Arguments to submit message
submit_message_args = reqparse.RequestParser()
submit_message_args.add_argument('recipient', type=non_empty_string, required=True, help='recipient cannot be blank')
submit_message_args.add_argument('message', type=str, required=True, help='message cannot be blank')

# Helper to parse int values from query strings, with default fallback
def parse_int_or_none(value, default=None):
    if value is None or str(value).strip() == "":
        return default
    return int(value)

# Arguments to fetch messages
fetch_messages_args = reqparse.RequestParser()
fetch_messages_args.add_argument('start', type=lambda v: parse_int_or_none(v, 0), required=False, location='args')
fetch_messages_args.add_argument('stop', type=lambda v: parse_int_or_none(v, None), required=False, location='args')
fetch_messages_args.add_argument('recipient', type=str, required=False, location='args')

# Arguments to delete messages
delete_messages_args = reqparse.RequestParser()
delete_messages_args.add_argument('ids', type=int, action='append', required=True, help='A list of IDs required')

# To represent the messages
messageFields = {
    'id':fields.Integer,
    'recipient':fields.String,
    'message':fields.String,
    'read':fields.Boolean,
    'timestamp':fields.DateTime
}

# Class for the /api/messages resource
class Messages(Resource):
    @marshal_with(messageFields)
    def get(self):
        args = fetch_messages_args.parse_args()

        recipient = args['recipient']
        start = args['start']
        stop = args['stop']

        if start < 0:
            abort(400, message="'start' and/or 'stop' cannot be negative")
        
        if stop is not None:
            if stop < 0:
                abort(400, message="'start' and/or 'stop' cannot be negative")
            if start>stop:
                abort(400, message="''start' cannot be greater than 'stop' input")

        query = MessageModel.query

        if recipient:
            query = query.filter_by(recipient=recipient)

        query = query.order_by(MessageModel.timestamp)

        if stop is not None:
            query = query.offset(start).limit(stop - start)
        else:
            query = query.offset(start)

        messages = query.all()

        for msg in messages:
            msg.read = True
        
        db.session.commit()

        return messages
    
    @marshal_with(messageFields)
    def post(self):
        args = submit_message_args.parse_args()
        message = MessageModel(recipient=args["recipient"], message=args["message"])
        db.session.add(message)
        db.session.commit()
        return message, 201
    
    @marshal_with(messageFields)
    def delete(self):
        args = delete_messages_args.parse_args()
        ids_to_delete = args['ids']
        messages = MessageModel.query.filter(MessageModel.id.in_(ids_to_delete)).all()

        if not messages:
            abort(404, message="No matching messages found")

        for msg in messages:
            db.session.delete(msg)
    
        db.session.commit()
        return '', 204

# Class for the /api/messages/<int:id> resource
class Message(Resource):
    @marshal_with(messageFields)
    def get(self, id):
        message = MessageModel.query.filter_by(id=id).first()
        if not message:
            abort(404, message="Message not found")
        message.read = True
        db.session.commit()
        return message
    
    @marshal_with(messageFields)
    def delete(self, id):
        message = MessageModel.query.filter_by(id=id).first()
        if not message:
            abort(404, message="Message not found")
        db.session.delete(message)
        db.session.commit()
        return '', 204
    
# Class for /api/messages/unread resource
class UnreadMessages(Resource):
    @marshal_with(messageFields)
    def get(self):
        unread_messages = MessageModel.query.filter_by(read=False).all()

        for msg in unread_messages:
            msg.read = True
        
        db.session.commit()

        return unread_messages
           
# Add resources
api.add_resource(Messages, '/api/messages/')
api.add_resource(Message, '/api/messages/<int:id>')
api.add_resource(UnreadMessages, '/api/messages/unread')

# Home resource
@app.route('/')
def home():
    return '<h1>OSTTRA test assignment</h1>'

# Run the app
if __name__ == '__main__':
    app.run(debug=True)