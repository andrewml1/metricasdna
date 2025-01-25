import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from baseDatos import conectarCredenciales, integrantesCorreo, listaProyectos, guardarMetricas, \
    obtenerIdIntegrantePorCorreo, obtenerIdProyecto
import datetime

app = Flask(__name__)


@app.route('/integrantes', methods=['GET'])
def correos():
    cred = conectarCredenciales('admin')
    paciente_data = integrantesCorreo(cred)
    return jsonify(paciente_data)

@app.route('/proyectos', methods=['GET'])
def proyectos():
    cred = conectarCredenciales('admin')
    paciente_data = listaProyectos(cred)
    return jsonify(paciente_data)

@app.route("/", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        # Procesar los datos del formulario
        correo = request.form["correo"]
        proyectos = request.form.getlist("proyecto[]")
        dedicacion = request.form.getlist("dedicacion[]")
        riesgo = request.form.getlist("riesgo[]")
        valor = request.form.getlist("valor[]")
        avance=request.form.getlist("avance[]")

        # Guardar la información
        cred = conectarCredenciales("admin")
        idIntegrante = obtenerIdIntegrantePorCorreo(cred, correo)

        for i, proyecto in enumerate(proyectos):
            if not (riesgo[i] == "" and valor[i] == ""):
                idProyecto = obtenerIdProyecto(cred, proyecto)
                guardarMetricas(cred, idIntegrante, idProyecto, dedicacion[i], riesgo[i], valor[i],avance,datetime.datetime.now())

        # Redirigir a la página de agradecimiento
        return redirect(url_for("gracias"))

    return render_template("formulario.html")


@app.route("/gracias")
def gracias():
    return render_template("gracias.html")


if __name__ == '__main__':
    # app.run()
    app.run(host="0.0.0.0", port=os.environ.get("PORT", 5000))
