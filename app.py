from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta

import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS drinks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    drink TEXT,
    sugar TEXT,
    price INTEGER
)
""")

conn.commit()
conn.close()

app = Flask(__name__)

# -----------------------------
# Create Database Automatically
# -----------------------------
def init_db():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drinks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    drink TEXT,
    sugar TEXT,
    price INTEGER
    )
    """)

    conn.commit()
    conn.close()

# Create database when app starts
init_db()

# -----------------------------
# Home Page
# -----------------------------
@app.route('/')
def home():
    return render_template("index.html")

# -----------------------------
# Add Drink Record
# -----------------------------
@app.route('/add', methods=['POST'])
def add_drink():

    date = request.form['date']
    drink = request.form['drink']
    sugar = request.form['sugar']
    price = request.form['price']

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO drinks
    (date, drink, sugar, price)

    VALUES (?, ?, ?, ?)
    """,
    (date, drink, sugar, price))

    conn.commit()
    conn.close()

    return """
    <h2>Drink Saved Successfully!</h2>
    <a href="/">Go Back</a>
    """

@app.route('/records')
def records():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM drinks")

    data = cursor.fetchall()

    conn.close()

    return str(data)

@app.route('/dashboard')
def dashboard():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    period = request.args.get("period", "all")

    today = datetime.today()

    if period == "7":

        start_date = (
            today - timedelta(days=7)
        ).strftime("%Y-%m-%d")

    elif period == "30":

        start_date = (
            today - timedelta(days=30)
        ).strftime("%Y-%m-%d")

    else:

        start_date = None
    
    filter_clause = ""
    filter_params = ()

    if start_date:
        filter_clause = "WHERE date >= ?"
        filter_params = (start_date,)

    if start_date:

        cursor.execute("""
        SELECT COUNT(*)
        FROM drinks
        WHERE date >= ?
        """, (start_date,))

    else:

        cursor.execute("""
        SELECT COUNT(*)
        FROM drinks
        """)

    total_drinks = cursor.fetchone()[0]

    if total_drinks == 0:

        conn.close()

        return """
        <div style="
            max-width:600px;
            margin:50px auto;
            padding:30px;
            background:white;
            border-radius:15px;
            text-align:center;
            box-shadow:0 4px 12px rgba(0,0,0,0.08);
        ">
            <h2>No Records Available</h2>

            <p>
                Please add at least one beverage record before viewing the dashboard.
            </p>

            <a href="/">Return to Input Page</a>
        </div>
        """

    cursor.execute(
        f"""
        SELECT SUM(price)
        FROM drinks
        {filter_clause}
        """,
        filter_params
    )

    total_spending = cursor.fetchone()[0]

    if total_spending is None:
        total_spending = 0

    # Average cost
    cursor.execute(
        f"""
        SELECT AVG(price)
        FROM drinks
        {filter_clause}
        """,
        filter_params
    )
    average_cost = cursor.fetchone()[0]

    if average_cost is None:
        average_cost = 0

    # Full sugar drinks

    if start_date:

        cursor.execute("""
        SELECT COUNT(*)
        FROM drinks
        WHERE sugar='全糖'
        AND date >= ?
        """, (start_date,))

    else:

        cursor.execute("""
        SELECT COUNT(*)
        FROM drinks
        WHERE sugar='全糖'
        """)

    full_sugar_count = cursor.fetchone()[0]

    cursor.execute(
        f"""
        SELECT sugar
        FROM drinks
        {filter_clause}
        """,
        filter_params
    )

    sugar_records = cursor.fetchall()

    sugar_score_map = {
    "全糖": 100,
    "少糖": 75,
    "半糖": 50,
    "微糖": 25,
    "無糖": 0
    }

    total_sugar_score = 0

    for row in sugar_records:
        total_sugar_score += sugar_score_map.get(row[0], 0)

    if len(sugar_records) > 0:
        average_sugar_score = round(
            total_sugar_score / len(sugar_records),
            1
        )
    else:
        average_sugar_score = 0

    if average_sugar_score >= 70:
        sugar_risk = "High Risk"

    elif average_sugar_score >= 40:
        sugar_risk = "Moderate Risk"

    else:
        sugar_risk = "Low Risk"

    if average_sugar_score >= 87:
        sugar_level_text = "全糖"

    elif average_sugar_score >= 62:
        sugar_level_text = "少糖"

    elif average_sugar_score >= 37:
        sugar_level_text = "半糖"

    elif average_sugar_score >= 12:
        sugar_level_text = "微糖"

    else:
        sugar_level_text = "無糖"

    # Recent records
    cursor.execute("""
    SELECT id, date, drink, sugar, price
    FROM drinks
    ORDER BY id DESC
    LIMIT 20
    """)

    recent_records = cursor.fetchall()
    # ---------------------
    # Pie Chart Data
    # ---------------------

    cursor.execute(
        f"""
        SELECT drink, COUNT(*)
        FROM drinks
        {filter_clause}
        GROUP BY drink
        """,
        filter_params
    )

    drink_counts = cursor.fetchall()

    favorite_drink = "None"

    if len(drink_counts) > 0:

        highest_count = 0

        for row in drink_counts:

            if row[1] > highest_count:

                highest_count = row[1]

                favorite_drink = row[0]

        pie_labels = [row[0] for row in drink_counts]
        pie_values = [row[1] for row in drink_counts]


    # ---------------------
    # Bar Chart Data
    # ---------------------

    cursor.execute(
        f"""
        SELECT drink, SUM(price)
        FROM drinks
        {filter_clause}
        GROUP BY drink
        """,
        filter_params
    )

    drink_spending = cursor.fetchall()

    bar_labels = [row[0] for row in drink_spending]
    bar_values = [row[1] for row in drink_spending]


    # ---------------------
    # Line Chart Data
    # ---------------------

    cursor.execute(
        f"""
        SELECT date, SUM(price)
        FROM drinks
        {filter_clause}
        GROUP BY date
        ORDER BY date
        """,
        filter_params
    )

    daily_spending = cursor.fetchall()

    line_labels = [row[0] for row in daily_spending]
    line_values = [row[1] for row in daily_spending]

    conn.close()

    drink_penalty = total_drinks * 5

    sugar_penalty = average_sugar_score * 0.4

    spending_penalty = total_spending * 0.05

    consumption_score = round(
        100
        - drink_penalty
        - sugar_penalty
        - spending_penalty
    )

    if consumption_score < 0:
        consumption_score = 0

    if consumption_score >= 80:
        consumption_rating = "Excellent"

    elif consumption_score >= 60:
        consumption_rating = "Good"

    elif consumption_score >= 40:
        consumption_rating = "Fair"

    else:
        consumption_rating = "Needs Improvement"

    # ====================
    # Improvement Plan
    # ====================

    # Recommended drink frequency

    if total_drinks > 5:
        recommended_drinks = max(1, round(total_drinks * 0.5))
    else:
        recommended_drinks = total_drinks

    # Recommended spending

    recommended_spending = round(total_spending * 0.7)

    estimated_savings = total_spending - recommended_spending

    # Recommended sugar level

    if full_sugar_count >= 3:
        recommended_sugar = "半糖"

    elif full_sugar_count >= 1:
        recommended_sugar = "微糖"

    else:
        recommended_sugar = "維持目前糖度"

    recommended_score = consumption_score

    if recommended_drinks < total_drinks:
        recommended_score += 15

    if recommended_sugar != "維持目前糖度":
        recommended_score += 10

    if recommended_spending < total_spending:
        recommended_score += 10

    if recommended_score > 100:
        recommended_score = 100

    # ----------------------
    # Recommendation
    # ----------------------

    recommendation = []

    if total_drinks > 5:
        recommendation.append(
            f"Reduce weekly beverage purchases from {total_drinks} to about {recommended_drinks} drinks."
        )

    if average_sugar_score > 50 and recommended_sugar != "維持目前糖度":
        recommendation.append(
            f"Choose {recommended_sugar} options more often to reduce sugar intake."
        )

    if total_spending > 300:
        recommendation.append(
            f"Limit weekly beverage spending to around NT${recommended_spending}."
        )

    if len(recommendation) == 0:
        recommendation.append(
            "Great job! Keep maintaining healthy habits."
        )

    monthly_spending = total_spending * 4

    return render_template(

    "dashboard.html",

    total_drinks=total_drinks,
    total_spending=total_spending,
    average_cost=round(average_cost, 2),
    full_sugar_count=full_sugar_count,

    consumption_score=consumption_score,
    consumption_rating=consumption_rating,

    recommendation=recommendation,

    recent_records=recent_records,

    pie_labels=pie_labels,
    pie_values=pie_values,

    bar_labels=bar_labels,
    bar_values=bar_values,

    line_labels=line_labels,
    line_values=line_values,

    recommended_drinks=recommended_drinks,
    recommended_spending=recommended_spending,
    estimated_savings=estimated_savings,
    recommended_sugar=recommended_sugar,
    recommended_score=recommended_score,

    average_sugar_score=average_sugar_score,
    sugar_level_text=sugar_level_text,
    sugar_risk=sugar_risk,

    monthly_spending=monthly_spending,

    period=period
)

@app.route('/delete/<int:id>')
def delete_record(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM drinks WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# -----------------------------
# Run Flask
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)