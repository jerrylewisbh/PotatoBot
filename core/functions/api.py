import json
from datetime import datetime, timedelta

import flask
from core.texts import *
from core.types import Order, OrderCleared, Session, Squad, SquadMember
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.routing import IntegerConverter as BaseIntegerConverter

app = flask.Flask(__name__)

Session()

class IntegerConverter(BaseIntegerConverter):
    regex = r'-?\d+'


app.url_map.converters['int'] = IntegerConverter


@app.route('/new_ready_to_battle/<int:chat_id>', methods=['GET'])
def new_ready_to_battle(chat_id):
    try:
        order = Order()
        order.chat_id = chat_id
        order.confirmed_msg = 0
        order.text = MSG_MAIN_READY_TO_BATTLE
        order.date = datetime.now()
        Session.add(order)
        Session.commit()
        order = Session.query(Order).filter_by(chat_id=chat_id,
                                               date=order.date,
                                               text=MSG_MAIN_READY_TO_BATTLE).first()

        return flask.Response(status=200,
                              mimetype="application/json",
                              response=json.dumps({'order_id': order.id}))
    except SQLAlchemyError:
        Session.rollback()
        return flask.Response(status=400)


@app.route('/ready_to_battle/<int:order_id>/<int:user_id>', methods=['GET'])
def new_order_click(order_id, user_id):
    try:
        order = Session.query(Order).filter_by(id=order_id).first()
        if order is not None:
            squad = Session.query(Squad).filter_by(chat_id=order.chat_id).first()
            if squad is not None:
                squad_member = Session.query(SquadMember).filter_by(squad_id=squad.chat_id,
                                                                    user_id=user_id,
                                                                    approved=True)

                if squad_member is not None:
                    order_ok = Session.query(OrderCleared).filter_by(order_id=order_id,
                                                                     user_id=user_id).first()

                    if order_ok is None and datetime.now() - order.date < timedelta(minutes=10):
                        order_ok = OrderCleared()
                        order_ok.order_id = order_id
                        order_ok.user_id = user_id
                        Session.add(order_ok)
                        Session.commit()

            else:
                order_ok = Session.query(OrderCleared).filter_by(order_id=order_id,
                                                                 user_id=user_id).first()

                if order_ok is None and datetime.now() - order.date < timedelta(minutes=10):
                    order_ok = OrderCleared()
                    order_ok.order_id = order_id
                    order_ok.user_id = user_id
                    Session.add(order_ok)
                    Session.commit()

        return flask.Response(status=200)

    except SQLAlchemyError:
        Session.rollback()
        return flask.Response(status=400)


@app.route('/ready_to_battle_status/<int:order_id>', methods=['GET'])
def order_status(order_id):
    try:
        order = Session.query(Order).filter_by(id=order_id).first()
        if order is not None:
            users = []
            for order_ok in order.cleared:
                users.append({'username': order_ok.user.username,
                              'id': order_ok.user.id,
                              'attack': order_ok.user.character.attack if order_ok.user.character else 0,
                              'defence': order_ok.user.character.defence if order_ok.user.character else 0})

            return flask.Response(status=200,
                                  mimetype="application/json",
                                  response=json.dumps({'users': users}))

    except SQLAlchemyError:
        Session.rollback()
        return flask.Response(status=400)
