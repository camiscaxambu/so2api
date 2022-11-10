from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

class Pessoa(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  nome = db.Column(db.String(80), nullable=False)
  telefone = db.Column(db.String(14),unique=True, nullable=False)
  livro = db.relationship('Emprestimo')
  ativo = db.Column(db.Boolean, nullable=False, default=True)


  def __init__(self, nome, telefone):
    self.nome = nome
    self.telefone = telefone

class Livro(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  nome_livro = db.Column(db.String(80), unique=True, nullable=False)
  genero = db.Column(db.String(120), nullable=False)
  emprestado = db.Column(db.Boolean, nullable=False, default=False)
  emprestimo = db.relationship('Emprestimo')
  ativo = db.Column(db.Boolean, nullable=False, default=True)

  def __init__(self, nome_livro, genero, emprestado):
    self.nome_livro = nome_livro
    self.genero = genero
    self.emprestado = emprestado

class Emprestimo(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  livroid = db.Column(db.Integer, db.ForeignKey('livro.id'))
  pessoaid = db.Column(db.Integer, db.ForeignKey('pessoa.id'))
  devolvido = db.Column(db.Boolean, nullable=False, default=False)
  timestamp = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

# colocar campo finalizado, um datetime

  def __init__(self, livroid, pessoaid,devolvido,timestamp ):
    self.livroid = livroid
    self.pessoaid = pessoaid
    self.devolvido=devolvido
    self.timestamp=timestamp
