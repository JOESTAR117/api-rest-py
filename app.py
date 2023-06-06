from itertools import count
from typing import Optional
from flask import Flask, request, jsonify
from flask_pydantic_spec import (FlaskPydanticSpec, Response, Request)
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query

server = Flask(__name__)
spec = FlaskPydanticSpec('flask', title='Teste api')
spec.register(server)
database = TinyDB('database.json')
c = count()


class Pessoa(BaseModel):
    id: Optional[int] = Field(default_factory=lambda: next(c))
    name: str
    age: int


class Pessoas(BaseModel):
    pessoas: list[Pessoa]
    count: int


@server.get('/pessoas')
@spec.validate(resp=Response(HTTP_200=Pessoas))
def index():
    """Retorna todas as Pessoas"""
    return jsonify(
        Pessoas(
            pessoas=database.all(),
            count=len(database.all())
        ).dict()
    )


@server.post('/pessoas')
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_201=Pessoa))
def create():
    """Insere uma Pessoa no Banco de dados"""
    body = request.context.body.dict()
    database.insert(body)
    return body


@server.patch('/pessoas/<int:id>')
@spec.validate(
    body=Request(Pessoa), resp=Response(HTTP_204=Pessoa)
)
def update(id):
    """Atualiza dados de uma pessoa no banco de dados"""
    Pessoa = Query()
    body = request.context.body.dict()
    database.update(body, Pessoa.id == id)

    return jsonify(body)


@server.delete('/pessoas/<int:id>')
@spec.validate(resp=Response(HTTP_204=Pessoa))
def delete(id):
    """Apaga uma Pessoa no banco de dados"""
    Pessoa = Query()
    database.remove(Pessoa.id == id)
    return jsonify({})


server.run()
