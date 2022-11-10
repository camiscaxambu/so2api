from flask import Flask, request, jsonify
import json
from flask_sqlalchemy import SQLAlchemy
import os
import database
from database import *

application = Flask(__name__)

application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = database.db
db.init_app(application)

with application.app_context():
  db.create_all()


@application.route('/pessoa/<id>', methods=['GET','PUT'])
#get Pessoa por id
def get_pessoa(id):
    if request.method == "GET":
      pessoa = Pessoa.query.get(id)
      del pessoa.__dict__['_sa_instance_state']
      return jsonify(pessoa.__dict__)
    if request.method == "PUT":
        body = request.get_json()
        print(body, flush=True) 
        if len(body['nome']) > 3:
          db.session.query(Pessoa).filter_by(id=id).update(
          dict(nome=body['nome'], telefone=body['telefone'], ativo=body['ativo']))
          db.session.commit()
          teste = {"status":"success", "message":"usuario atualizado com sucesso"}
          return jsonify(teste) 


@application.route('/livro/<id>', methods=['GET','PUT'])
#get Livro por id
def get_livro(id):
  if request.method == "GET":
    livro = Livro.query.get(id)
    del livro.__dict__['_sa_instance_state']
    return jsonify(livro.__dict__) 
  if request.method == "PUT":
      body = request.get_json()
      db.session.query(Livro).filter_by(id=id).update(
        dict(nome_livro=body['nome_livro'], genero=body['genero']))
      db.session.commit()
      return "item updated"
 

  
@application.route('/emprestimos', methods=['GET'])
#get lista de emprestimos
def get_emprestimos():
  emprestimos = []
  for item in db.session.query(Emprestimo).all():
    del item.__dict__['_sa_instance_state']
    emprestimos.append(item.__dict__)
  return jsonify(emprestimos)

@application.route('/pessoa', methods=['GET'])
#get lista de PESSOAS 
def get_pessoas():
  pessoas = []
  for item in db.session.query(Pessoa).all():
    del item.__dict__['_sa_instance_state']
    pessoas.append(item.__dict__)
  return jsonify(pessoas)
  
@application.route('/livro', methods=['GET'])
#get lista de livros 
def get_livros():
  livros = []
  for item in db.session.query(Livro).all():
    del item.__dict__['_sa_instance_state']
    livros.append(item.__dict__)
  return jsonify(livros)  
  
@application.route('/pessoa', methods=['POST'])
#post pessoa
def create_pessoa():
  body = request.get_json()

  pessoaexiste = Pessoa.query.filter_by(nome = body['nome']).all()
  telefoneexiste = Pessoa.query.filter_by(telefone = body['telefone']).all()
  if len(pessoaexiste) > 0:
    dict = {"status":"failed", "message":"usuario ja existe"}
    return jsonify(dict)
  if len(telefoneexiste) > 0:
    dict = {"status":"failed", "message":"telefone ja existe"}
    return jsonify(dict) 
  if len(body['nome']) > 3:
    db.session.add(Pessoa(body['nome'], body['telefone']))
    db.session.commit()
    dict = {"status":"success", "message":"usuario criado com sucesso"}
    return jsonify(dict) 


#post livro
@application.route('/livro', methods=['POST'])
def create_livro():
  body = request.get_json()
  print(body['nome_livro'].isspace(), flush=True)
  livroexiste = Livro.query.filter_by(nome_livro = body['nome_livro']).all()
  if len(livroexiste) > 0 :
    dict = {"status":"failed", "message":"livro ja existe"}
    return jsonify(dict)
  if body['nome_livro'].isspace() == True or body['genero'].isspace() == True:
      dict = {"status":"failed", "message":"nome invalido"}
      return jsonify(dict)
  if len(body['nome_livro']) > 3:
      db.session.add(Livro(body['nome_livro'], body['genero'], body['emprestado']))
      db.session.commit()
      dict = {"status":"success", "message":"livro criado com sucesso"}
      return jsonify(dict)
  else:
      dict = {"status":"failed", "message":"nome invalido"}
      return jsonify(dict)



#post empretimo
@application.route('/emprestimo', methods=['POST'])
def create_emprestimo():
  body = request.get_json()
  sqlstring="SELECT id FROM Livro WHERE nome_livro='"+str(body['livro_name'])+"' and emprestado='0'"
  r=db.session.execute(sqlstring)
  livroid=r.fetchone()
  if not livroid:
    dict = {"status":"failed", "message":"livro não existente ou emprestado"}
    return jsonify(dict) 

  sqlstring="SELECT id FROM Pessoa WHERE nome='"+str(body['pessoa_name'])+"' AND ativo='1'"
  r=db.session.execute(sqlstring)
  pessoaid=r.fetchone()
  if not pessoaid:
    dict = {"status":"failed", "message":"pessoa inexistente ou inativa"}
    return jsonify(dict) 
  db.session.add(Emprestimo(livroid[0], pessoaid[0],devolvido=None,timestamp=None))
  #sqlstring = db.session.query(Livro).update({Livro.emprestado:1})
  sqlstring ="UPDATE Livro set emprestado ='1' where id="+str(livroid[0])
  db.session.execute(sqlstring)
  db.session.commit()
  dict = {"status":"success", "message":sqlstring}
  return jsonify(dict) 
 
@application.route('/emprestimo/<id>', methods=['DELETE'])
def delete_item(id):
  db.session.query(Emprestimo).filter_by(id=id).delete()
  db.session.commit()
  return "item deleted"

@application.route('/devolver', methods=['PUT'])
def devolver_emprestimo():
  body = request.get_json()
  sqlstring="SELECT id FROM Livro WHERE nome_livro='"+str(body['livro_name'])+"' and emprestado='1'"
  r=db.session.execute(sqlstring)
  livroid=r.fetchone()
  if not livroid:
    dict = {"status":"failed", "message":"livro não existente ou não emprestado"}
    return jsonify(dict) 

  sqlstring="SELECT id FROM Pessoa WHERE nome='"+str(body['pessoa_name'])+"'"
  r=db.session.execute(sqlstring)
  pessoaid=r.fetchone()
  if not pessoaid:
    dict = {"status":"failed", "message":"pessoa não existente ou cadastrada"}
    return jsonify(dict) 

  sqlstring="SELECT id FROM Emprestimo WHERE livroid="+str(livroid[0])+" and pessoaid ="+str(pessoaid[0])
  r=db.session.execute(sqlstring)
  Emprestimoidx=r.fetchone()
  if not Emprestimoidx:
    dict = {"status":"failed", "message":"Relação pessoa x emprestimo incorreta, talvez esteja devolvendo por outra pessoa"}
    return jsonify(dict) 

  #db.session.add(Emprestimo(livroid[0], pessoaid[0],devolvido=None,timestamp=None))
  sqlstring ="UPDATE Emprestimo set devolvido ='1' where id="+str(Emprestimoidx[0])
  db.session.execute(sqlstring)
  db.session.commit()
  sqlstring ="UPDATE Livro set emprestado ='0' where id="+str(livroid[0])
  db.session.execute(sqlstring)
  db.session.commit()
  dict = {"status":"success", "message":'sucess'}
  return jsonify(dict) 



if __name__ == '__main__':
    application.run(debug=True)