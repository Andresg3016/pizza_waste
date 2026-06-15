from flask import Flask, render_template, request, redirect
from models.database import get_db_connection

app = Flask(__name__)

# =========================
# DASHBOARD
# =========================

@app.route('/')
def index():

    conn = get_db_connection()
    cursor = conn.cursor()

    # Total registros
    cursor.execute("SELECT COUNT(*) AS total FROM desperdicios")
    total_desperdicios = cursor.fetchone()['total']

    # Total pérdidas
    cursor.execute("""
        SELECT COALESCE(SUM(costo_perdido),0) AS total
        FROM desperdicios
    """)
    total_perdidas = cursor.fetchone()['total']

    # Ingrediente más desperdiciado
    cursor.execute("""
        SELECT ingrediente,
               SUM(cantidad) AS total
        FROM desperdicios
        GROUP BY ingrediente
        ORDER BY total DESC
        LIMIT 1
    """)

    ingrediente = cursor.fetchone()

    ingrediente_top = (
        ingrediente['ingrediente']
        if ingrediente
        else "Sin datos"
    )

    conn.close()

    return render_template(
        'index.html',
        total_desperdicios=total_desperdicios,
        total_perdidas=total_perdidas,
        ingrediente_top=ingrediente_top
    )

# =========================
# LISTAR
# =========================

@app.route('/historial')
def historial():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM desperdicios
        ORDER BY fecha DESC
    """)

    desperdicios = cursor.fetchall()

    conn.close()

    return render_template(
        'historial.html',
        desperdicios=desperdicios
    )

# =========================
# CREAR
# =========================

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():

    if request.method == 'POST':

        ingrediente = request.form['ingrediente']
        cantidad = request.form['cantidad']
        unidad = request.form['unidad']
        motivo = request.form['motivo']
        costo_perdido = request.form['costo_perdido']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO desperdicios
            (
                ingrediente,
                cantidad,
                unidad,
                motivo,
                costo_perdido
            )
            VALUES (%s,%s,%s,%s,%s)
        """, (
            ingrediente,
            cantidad,
            unidad,
            motivo,
            costo_perdido
        ))

        conn.commit()
        conn.close()

        return redirect('/historial')

    return render_template('registrar.html')

# =========================
# EDITAR
# =========================

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':

        ingrediente = request.form['ingrediente']
        cantidad = request.form['cantidad']
        unidad = request.form['unidad']
        motivo = request.form['motivo']
        costo_perdido = request.form['costo_perdido']

        cursor.execute("""
            UPDATE desperdicios
            SET
                ingrediente=%s,
                cantidad=%s,
                unidad=%s,
                motivo=%s,
                costo_perdido=%s
            WHERE id=%s
        """, (
            ingrediente,
            cantidad,
            unidad,
            motivo,
            costo_perdido,
            id
        ))

        conn.commit()
        conn.close()

        return redirect('/historial')

    cursor.execute("""
        SELECT *
        FROM desperdicios
        WHERE id=%s
    """, (id,))

    desperdicio = cursor.fetchone()

    conn.close()

    return render_template(
        'editar.html',
        desperdicio=desperdicio
    )

# =========================
# ELIMINAR
# =========================

@app.route('/eliminar/<int:id>')
def eliminar(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM desperdicios
        WHERE id=%s
    """, (id,))

    conn.commit()
    conn.close()

    return redirect('/historial')

# =========================

if __name__ == '__main__':
    app.run(debug=True)