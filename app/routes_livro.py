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
    livros = Livro.query.all()
    return render_template("livraria.html", livros=livros)