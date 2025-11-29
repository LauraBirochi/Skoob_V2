from .database import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(120), nullable=False)
    apelido = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)

    # Relacionamento com estante
    estantes = db.relationship("Estante", backref="usuario", lazy=True)

    def __repr__(self):
        return f"<Usuario {self.nome}>"

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    autor = db.Column(db.String(100), nullable=True)
    isbn = db.Column(db.String(50), nullable=True)
    descricao = db.Column(db.Text, nullable=True)
    paginas = db.Column(db.Integer, nullable=True)
    capa = db.Column(db.String(255), nullable=True)
    nota = db.Column(db.Float, nullable=True)
    categoria = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<Livro {self.titulo}>"

class Estante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Relacionamento com usuário
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    
    # Relacionamento com livro
    livro_id = db.Column(db.Integer, db.ForeignKey("livro.id"), nullable=False)
    livro = db.relationship("Livro", backref=db.backref("estantes", lazy=True))
    
    # Status da leitura
    status = db.Column(db.String(50), nullable=False)  # ex: "Lendo", "Quero Ler", "Lido"

    def __repr__(self):
        return f"<Estante User:{self.usuario_id} Livro:{self.livro_id}>"
