import json
from datetime import datetime, timedelta
import flask
from core.types import Order, Session, Squad, SquadMember, OrderCleared
from werkzeug.routing import IntegerConverter as BaseIntegerConverter

app = flask.Flask(__name__)


class IntegerConverter(BaseIntegerConverter):
    regex = r'-?\d+'


app.url_map.converters['int'] = IntegerConverter


@app.route('/new_ready_to_battle/<int:chat_id>', methods=['GET'])
def new_ready_to_battle(chat_id):
    session = Session()
    try:
        order = Order()
        order.chat_id = chat_id
        order.confirmed_msg = 0
        order.text = 'К битве готовсь!'
        order.date = datetime.now()
        session.add(order)
        session.commit()
        order = session.query(Order).filter_by(chat_id=chat_id, date=order.date, text='К битве готовсь!').first()
        return flask.Response(status=200, mimetype="application/json", response=json.dumps({'order_id': order.id}))
    except:
        Session.rollback()
        return flask.Response(status=400)


@app.route('/ready_to_battle/<int:order_id>/<int:user_id>', methods=['GET'])
def new_order_click(order_id, user_id):
    try:
        session = Session()
        order = session.query(Order).filter_by(id=order_id).first()
        if order is not None:
            squad = session.query(Squad).filter_by(chat_id=order.chat_id).first()
            if squad is not None:
                squad_member = session.query(SquadMember).filter_by(squad_id=squad.chat_id,
                                                                    user_id=user_id)
                if squad_member is not None:
                    order_ok = session.query(OrderCleared).filter_by(order_id=order_id,
                                                                     user_id=user_id).first()
                    if order_ok is None and datetime.now() - order.date < timedelta(minutes=10):
                        order_ok = OrderCleared()
                        order_ok.order_id = order_id
                        order_ok.user_id = user_id
                        session.add(order_ok)
                        session.commit()
            else:
                order_ok = session.query(OrderCleared).filter_by(order_id=order_id,
                                                                 user_id=user_id).first()
                if order_ok is None and datetime.now() - order.date < timedelta(minutes=10):
                    order_ok = OrderCleared()
                    order_ok.order_id = order_id
                    order_ok.user_id = user_id
                    session.add(order_ok)
                    session.commit()
        return flask.Response(status=200)
    except:
        Session.rollback()
        return flask.Response(status=400)
