from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import Usuario
from .database import db


bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("login.html")

@bp.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    senha = request.form.get("senha")

    usuario = Usuario.query.filter_by(email=email, senha=senha).first()

    if usuario:
        session.clear()
        
        session["usuario_id"] = usuario.id
        session['apelido'] = usuario.apelido 
        
        session.permanent = True 
        
        flash(f"Login realizado! Bem-vindo, {usuario.nome_completo}.", "success")
        
        # BP AQUI É MAIN
        return redirect(url_for("main.home"))
        
    else:
        flash("Email ou senha incorretos.", "danger")
        return redirect(url_for("main.index"))

@bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome_completo")
        apelido = request.form.get("apelido")
        email = request.form.get("email")
        senha = request.form.get("senha")
        conf_senha = request.form.get("conf_senha")

        if senha != conf_senha:
            flash("As senhas não coincidem.", "danger")
            return redirect(url_for("main.cadastro"))

        # checar se o email já existe
        if Usuario.query.filter_by(email=email).first():
            flash("Email já cadastrado.", "danger")
            return redirect(url_for("main.cadastro"))

        novo_usuario = Usuario(
            nome_completo=nome,
            apelido=apelido,
            email=email,
            senha=senha
        )
        db.session.add(novo_usuario)
        db.session.commit()

        flash("Cadastro realizado com sucesso!", "success")
        return redirect(url_for("main.index"))

    
    return render_template("cadastro.html")

@bp.route("/logout")
def logout():
    session.clear()  
    flash("Você saiu com sucesso.", "success")
    return redirect(url_for("main.index"))


@bp.route("/home")
def home():
    if "usuario_id" not in session:
        flash("Você precisa estar logado.", "danger")
        return redirect(url_for("main.index"))

    usuario_id = session.get("usuario_id")              # pega o ID da sessão
    usuario = Usuario.query.get(usuario_id)             # busca o usuário no banco

    return render_template("baseT.html", usuario=usuario)
