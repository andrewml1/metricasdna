from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Recibe los datos del formulario
        nombre_proyecto = request.form["nombre_proyecto"]
        dedicacion = request.form["dedicacion"]
        riesgo = request.form["riesgo"]
        valor = request.form["valor"]

        # Procesa o guarda los datos
        print(f"Nombre del Proyecto: {nombre_proyecto}")
        print(f"Dedicación: {dedicacion}%")
        print(f"Riesgo: {riesgo}")
        print(f"Valor: {valor}")

        # Redirige o confirma el envío
        return redirect(url_for("index"))
    return render_template("formulario.html")


if __name__ == "__main__":
    app.run(debug=True)
