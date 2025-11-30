from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify, request
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

@bp_livro.route("/minhaestante")
def minhaestante():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Faça login para ver sua estante.", "warning")
        return redirect(url_for("main.index"))

    # 3. Busca itens usando a variável segura
    itens_estante = Estante.query.filter_by(usuario_id=usuario_id).all()

    livros_para_exibir = []
    for item in itens_estante:
        if item.livro:
            livro = item.livro
            nome_capa = livro.capa if livro.capa else 'capa-padrao.jpg'
            url_imagem = url_for('static', filename=f'images/{nome_capa}')

            livros_para_exibir.append({
                "id": livro.id,
                "estante_id": item.id,
                "title": livro.titulo,
                "author": livro.autor,
                "rating": float(livro.nota) if livro.nota else 0.0,
                "cover": url_imagem,
                "pages": livro.paginas,
                "synopsis": livro.descricao if livro.descricao else "Sem sinopse.",
                "status": item.status 
            })

    return render_template("minha-estante.html", books_data=livros_para_exibir)

@bp_livro.route("/remover_estante/<int:estante_id>", methods=['DELETE'])
def remover_estante(estante_id):
    # Retorna JSON 401 se não logado (não redirect, pois é AJAX)
    if "usuario_id" not in session:
        return jsonify({"ok": False, "mensagem": "Não autorizado"}), 401

    item = Estante.query.get(estante_id)

    if not item:
        return jsonify({"ok": False, "mensagem": "Item não encontrado"}), 404

    # Segurança: verifica se o item pertence ao dono da sessão
    if item.usuario_id != session["usuario_id"]:
        return jsonify({"ok": False, "mensagem": "Proibido"}), 403

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"ok": True, "mensagem": "Livro removido com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "mensagem": str(e)}), 500

@bp_livro.route("/atualizar_status/<int:estante_id>", methods=['PUT'])
def atualizar_status(estante_id):
    # 1. Verifica se o usuário está logado
    if "usuario_id" not in session:
        return jsonify({"ok": False, "mensagem": "Login necessário"}), 401

    # 2. Pega os dados enviados pelo JavaScript
    data = request.get_json()
    novo_status = data.get('status') 

    if not novo_status:
        return jsonify({"ok": False, "mensagem": "Status inválido"}), 400

    # 3. Busca o livro na estante
    item = Estante.query.get(estante_id)

    if not item:
        return jsonify({"ok": False, "mensagem": "Livro não encontrado na estante"}), 404
    
    if item.usuario_id != session["usuario_id"]:
        return jsonify({"ok": False, "mensagem": "Ação não autorizada"}), 403

    # 5. Atualiza o status e salva no banco
    try:
        item.status = novo_status
        db.session.commit()
        return jsonify({"ok": True, "mensagem": f"Status alterado para {novo_status}!"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar status: {e}") # Mostra o erro no terminal para debug
        return jsonify({"ok": False, "mensagem": "Erro interno ao atualizar status"}), 500

@bp_livro.route("/lidos")
def lidos():
     # 1. Proteção: Verifica se está logado
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Faça login para ver seus livros lidos.", "warning")
        return redirect(url_for("main.index"))

    # 2. Busca no banco APENAS os livros com status 'Lido'
    itens_estante = Estante.query.filter_by(
        usuario_id=usuario_id, 
        status="Lido"  # <--- O FILTRO IMPORTANTE
    ).all()

    # 3. Formata os dados para o JavaScript
    livros_para_exibir = []
    for item in itens_estante:
        if item.livro:
            livro = item.livro
            nome_capa = livro.capa if livro.capa else 'capa-padrao.jpg'
            url_imagem = url_for('static', filename=f'images/{nome_capa}')

            livros_para_exibir.append({
                "id": livro.id,
                "estante_id": item.id, # ID da relação (necessário para remover/alterar)
                "title": livro.titulo,
                "author": livro.autor,
                "rating": float(livro.nota) if livro.nota else 0.0,
                "cover": url_imagem,
                "pages": livro.paginas,
                "synopsis": livro.descricao or "Sem sinopse.",
                "status": item.status
            })

    # 4. Renderiza a página enviando os dados
    return render_template("livros-lidos.html", books_data=livros_para_exibir)

@bp_livro.route("/lendo")
def lendo():
     # 1. Proteção de Login
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Faça login para ver suas leituras atuais.", "warning")
        return redirect(url_for("main.index"))

    # 2. Busca APENAS os livros com status 'Lendo'
    itens_estante = Estante.query.filter_by(
        usuario_id=usuario_id, 
        status="Lendo"  # <--- FILTRO PRINCIPAL
    ).all()

    # 3. Formata os dados
    livros_para_exibir = []
    for item in itens_estante:
        if item.livro:
            livro = item.livro
            nome_capa = livro.capa if livro.capa else 'capa-padrao.jpg'
            url_imagem = url_for('static', filename=f'images/{nome_capa}')

            livros_para_exibir.append({
                "id": livro.id,
                "estante_id": item.id,
                "title": livro.titulo,
                "author": livro.autor,
                "rating": float(livro.nota) if livro.nota else 0.0,
                "cover": url_imagem,
                "pages": livro.paginas,
                "synopsis": livro.descricao or "Sem sinopse.",
                "status": item.status
            })

    return render_template("em-leitura.html", books_data=livros_para_exibir)


@bp_livro.route("/proximos")
def proximos():
    # 1. Proteção de Login
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Faça login para ver sua lista de desejos.", "warning")
        return redirect(url_for("main.index"))

    # 2. Busca APENAS os itens com status 'Quero Ler'
    itens_estante = Estante.query.filter_by(
        usuario_id=usuario_id, 
        status="Quero Ler"  # <--- FILTRO ESPECÍFICO DESTA PÁGINA
    ).all()

    # 3. Formata os dados
    livros_para_exibir = []
    for item in itens_estante:
        if item.livro:
            livro = item.livro
            nome_capa = livro.capa if livro.capa else 'capa-padrao.jpg'
            url_imagem = url_for('static', filename=f'images/{nome_capa}')

            livros_para_exibir.append({
                "id": livro.id,
                "estante_id": item.id,
                "title": livro.titulo,
                "author": livro.autor,
                "rating": float(livro.nota) if livro.nota else 0.0,
                "cover": url_imagem,
                "pages": livro.paginas,
                "synopsis": livro.descricao or "Sem sinopse.",
                "status": item.status
            })

    return render_template("proximos-livros.html", books_data=livros_para_exibir)


@bp_livro.route("/resenhas")
def resenhas():
    return render_template("minhas-resenhas.html")