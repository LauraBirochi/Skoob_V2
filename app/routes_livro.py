from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify
from .models import Livro, Estante
from .database import db

bp_livro = Blueprint("livro", __name__, url_prefix="/livros")

@bp_livro.route("/")
def listar_livros():
    livros = Livro.query.all()
    return f"Total de livros cadastrados: {len(livros)}"

# Rota normal (redireciona para /home)
@bp_livro.route("/adicionar_estante/<int:livro_id>")
def adicionar_estante(livro_id):
    if "usuario_id" not in session:
        flash("Você precisa estar logado para adicionar livros à estante.", "danger")
        return redirect(url_for("main.index"))

    usuario_id = session["usuario_id"]

    existe = Estante.query.filter_by(usuario_id=usuario_id, livro_id=livro_id).first()
    if existe:
        flash("Livro já está na sua estante.", "info")
        return redirect(url_for("main.home"))

    estante = Estante(usuario_id=usuario_id, livro_id=livro_id, status="Quero Ler")
    db.session.add(estante)
    db.session.commit()

    flash("Livro adicionado à estante!", "success")
    return redirect(url_for("main.home"))

# 🔹 Rota AJAX para disparar toast sem recarregar
@bp_livro.route("/add_ajax/<int:livro_id>")
def adicionar_estante_ajax(livro_id):
    if "usuario_id" not in session:
        return jsonify({"ok": False, "mensagem": "Você precisa estar logado"}), 401

    usuario_id = session["usuario_id"]

    existe = Estante.query.filter_by(usuario_id=usuario_id, livro_id=livro_id).first()
    if existe:
        return jsonify({"ok": False, "mensagem": "Livro já está na estante"}), 200

    estante = Estante(usuario_id=usuario_id, livro_id=livro_id, status="Quero Ler")
    db.session.add(estante)
    db.session.commit()

    return jsonify({"ok": True, "mensagem": "Livro adicionado à estante!"}), 200

@bp_livro.route("/livraria")
def livraria():
    livros_db = Livro.query.all()

    if "usuario_id" not in session:
        flash("Você precisa estar logado.", "danger")
        return redirect(url_for("main.index"))

    usuario = {
        'apelido': session.get('apelido'),
        'id': session.get('user_id')
    }

    lista_livros_js = []
    
    for livro in livros_db:
        nome_capa = livro.capa if livro.capa else 'capa-padrao.jpg'
        
        url_imagem = url_for('static', filename=f'images/{nome_capa}')
        
        cat = livro.categoria if livro.categoria else "Indefinido"
        
        #Dicionário JavaScript
        item = {
            "id": livro.id,
            "title": livro.titulo,
            "author": livro.autor,
            "category": cat,  
            "cover": url_imagem,
            "pages": livro.paginas,
            "rating": float(livro.nota) if livro.nota else 0.0,
            "synopsis": livro.descricao if livro.descricao else "Sinopse indisponível."
        }
        lista_livros_js.append(item)

    return render_template("livraria.html", dados_livros=lista_livros_js, usuario=usuario)

@bp_livro.route('/logout')
def logout():
    session.clear()
    
    return redirect(url_for('main.home'))
