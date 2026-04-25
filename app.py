from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"   # you can write anything here


# Change this to your own password
PASSWORD = "Suryansh"  # required to delete a donor

def get_db():
    return sqlite3.connect("blood_bank.db")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/add_donor", methods=["GET","POST"])
def add_donor():
    if request.method == "POST":
        name = request.form["name"].strip()
        age = request.form.get("age") or None
        gender = request.form.get("gender")
        blood_group = request.form.get("blood_group")
        phone = request.form.get("phone")
        city = request.form.get("city")
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO donor (name, age, gender, blood_group, phone, city) VALUES (?,?,?,?,?,?)",
            (name, age, gender, blood_group, phone, city)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("donors"))
    return render_template("add_donor.html")

@app.route("/donors")
def donors():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM donor")
    donors = cur.fetchall()
    conn.close()
    return render_template("donors.html", donors=donors)

@app.route("/confirm_delete/<int:id>")
def confirm_delete(id):
    # show password form
    return render_template("delete_confirm.html", donor_id=id)

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    password = request.form["password"]

    if password != PASSWORD:
        flash("Incorrect Password! Try again.", "error")
        return redirect(url_for("confirm_delete", id=id))

    conn = get_db()
    cur = conn.cursor()

    # Adjust stock before deleting
    cur.execute("SELECT blood_group FROM donor WHERE id=?", (id,))
    result = cur.fetchone()

    if result:
        blood_group = result[0]
        cur.execute("SELECT COUNT(*) FROM donation WHERE donor_id=?", (id,))
        donation_count = cur.fetchone()[0]
        cur.execute("UPDATE stock SET units = units - ? WHERE blood_group=?", (donation_count, blood_group))
        cur.execute("DELETE FROM donation WHERE donor_id=?", (id,))
        cur.execute("DELETE FROM donor WHERE id=?", (id,))
        conn.commit()

    conn.close()

    return redirect(url_for("donors"))



@app.route("/record_donation", methods=["GET","POST"])
def record_donation():
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        donor_id = request.form["donor_id"]
        date = datetime.now().strftime("%Y-%m-%d")
        cur.execute("INSERT INTO donation (donor_id, date) VALUES (?, ?)", (donor_id, date))
        # update stock +1 for donor's blood group
        cur.execute("SELECT blood_group FROM donor WHERE id=?", (donor_id,))
        row = cur.fetchone()
        if row:
            bg = row[0]
            cur.execute("UPDATE stock SET units = units + 1 WHERE blood_group=?", (bg,))
        conn.commit()
        conn.close()
        return redirect(url_for("view_stock"))
    cur.execute("SELECT id, name FROM donor")
    donors = cur.fetchall()
    conn.close()
    return render_template("record_donation.html", donors=donors)

@app.route("/view_stock")
def view_stock():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM stock")
    stock = cur.fetchall()
    conn.close()
    return render_template("view_stock.html", stock=stock)

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    password = request.form["password"]
    if password != PASSWORD:
        return "Incorrect Password. <a href='/donors'>Go Back</a>"

    conn = get_db()
    cur = conn.cursor()

    # Get donor’s blood group
    cur.execute("SELECT blood_group FROM donor WHERE id=?", (id,))
    result = cur.fetchone()

    if result:
        blood_group = result[0]

        # Adjust stock by number of donations
        cur.execute("SELECT COUNT(*) FROM donation WHERE donor_id=?", (id,))
        donation_count = cur.fetchone()[0]
        cur.execute("UPDATE stock SET units = units - ? WHERE blood_group=?", (donation_count, blood_group))

        # Delete donation history and donor
        cur.execute("DELETE FROM donation WHERE donor_id=?", (id,))
        cur.execute("DELETE FROM donor WHERE id=?", (id,))
        conn.commit()

        # 🚩 Reset AUTOINCREMENT if table is now empty
        cur.execute("SELECT COUNT(*) FROM donor")
        if cur.fetchone()[0] == 0:
            # Only works because table uses AUTOINCREMENT
            cur.execute("DELETE FROM sqlite_sequence WHERE name='donor'")
            conn.commit()

    conn.close()
    return redirect(url_for("donors"))
