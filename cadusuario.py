from flask import Flask, render_template, request, redirect
import sqlite3
from init_db import conectar
#Quando puxamos uma função sequer de dentro de um arquivo n´so estamos puxando tudo que está acontecendo dentro daquele arquivo
app = Flask(__name__)


'''
Aqui nós estamos definindo uma rota no flask, senodo / a página inicial do sistema. Isso faz com que quando alguem acesse o endereço IP onde está hospedado o nosso site, ele vai chamar pelo " / ", sendo em busca de 127.0.0.1:5000/, e a rota / está cadastrada a função home. Onde nos leva a rota usuários. Cao depois queiramos fazer o retorno da página login como página incial, nós vamos ter que apenas alterar o que a função home retorna para ousuários, retornando o cmainho login, assim quebrando a pau tudo.
'''
@app.route("/")
def home():
    return redirect("/usuarios")

'''Aqui vamos ter a criação deo oque vai acontecer dentor do caminho de /usuarios, por meio de isso aqui a agente conseguie configurar oq ue que vmaos fazer uqando esta rota ser chamada, no caso é a rota incialque é chamda'''
# LISTAR
@app.route("/usuarios")
def usuarios():
    conn = conectar()
    cursor = conn.cursor()
    pesquisa = request.args.get("pesquisa")
    if pesquisa:
        cursor.execute("""
        SELECT * FROM usuarios WHERE nome LIKE ? OR cpf LIKE ? OR email LIKE ?
        ORDER BY nome """,   (f"%{pesquisa}%", f"%{pesquisa}%", f"%{pesquisa}%"))
    else:
        cursor.execute(""" SELECT * FROM usuarios ORDER BY nome """)
    usuarios = cursor.fetchall()
    conn.close()

    return render_template(
        "usuarios.html", 
        usuarios=usuarios
    )


# NOVO
@app.route("/usuarios/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO usuarios (nome, senha, cpf, email, perfil)
        VALUES (?, ?, ?, ?, ?) """,
        (request.form["nome"], request.form["senha"], request.form["cpf"],
            request.form["email"], request.form["perfil"]))
        conn.commit()
        conn.close()
        return redirect("/usuarios")
    return render_template("usuario_form.html", usuario=None)


# EDITAR
@app.route("/usuarios/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = conectar()
    cursor = conn.cursor()
    if request.method == "POST":
        cursor.execute(""" UPDATE usuarios SET nome=?, senha=?,cpf=?,
            email=?, perfil=? WHERE id_usuario=? """,
        (request.form["nome"], request.form["senha"], request.form["cpf"],
            request.form["email"], request.form["perfil"], id))
        conn.commit()
        conn.close()
        return redirect("/usuarios")

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario=?",(id,))
    usuario = cursor.fetchone()
    conn.close()
    return render_template("usuario_form.html", usuario=usuario)


# EXCLUIR
@app.route("/usuarios/excluir/<int:id>")
def excluir(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id_usuario=?",(id,))
    conn.commit()
    conn.close()
    return redirect("/usuarios")


if __name__ == "__main__":
    app.run(debug=True)