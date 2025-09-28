from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
from datetime import timedelta
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'your_password'  
app.permanent_session_lifetime = timedelta(days=1)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@email.com'
app.config['MAIL_PASSWORD'] = 'mail_password'
app.config['MAIL_DEFAULT_SENDER'] = ('Schoint Finder', 'your_emial@email.com')

mail = Mail(app)

def get_db_connection():
    conn = sqlite3.connect('scholarships.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/about")
def about_us():
    return render_template("about_us.html")


from datetime import date

@app.route("/scholarships")
def scholarships():
    query = request.args.get("query", "").strip()
    today_str = date.today().isoformat()

    conn = get_db_connection()
    cur = conn.cursor()

    # Move expired scholarships to archive
    cur.execute("""
        INSERT INTO scholarships_archive
        SELECT * FROM scholarships WHERE deadline < ?
    """, (today_str,))
    cur.execute("DELETE FROM scholarships WHERE deadline < ?", (today_str,))
    conn.commit()

    if query:
        cur.execute("""
            SELECT * FROM scholarships
            WHERE approved = 1 AND (name LIKE ? OR eligibility LIKE ?)
            ORDER BY deadline
        """, ('%' + query + '%', '%' + query + '%'))
    else:
        cur.execute("SELECT * FROM scholarships WHERE approved = 1 ORDER BY deadline")

    scholarships = cur.fetchall()
    conn.close()
    return render_template("scholarships.html", scholarships=scholarships)


@app.route("/internships")
def internships():
    query = request.args.get("query", "").strip()
    today_str = date.today().isoformat()

    conn = get_db_connection()
    cur = conn.cursor()

    # Move expired internships to archive
    cur.execute("""
        INSERT INTO internships_archive
        SELECT * FROM internships WHERE deadline < ?
    """, (today_str,))
    cur.execute("DELETE FROM internships WHERE deadline < ?", (today_str,))
    conn.commit()

    if query:
        cur.execute("""
            SELECT * FROM internships
            WHERE approved = 1 AND (name LIKE ? OR eligibility LIKE ?)
            ORDER BY deadline
        """, ('%' + query + '%', '%' + query + '%'))
    else:
        cur.execute("SELECT * FROM internships WHERE approved = 1 ORDER BY deadline")

    internships = cur.fetchall()
    conn.close()
    return render_template("internships.html", internships=internships)

@app.route("/archives")
def archives():
    if not session.get("logged_in"):
        return "Unauthorized", 403

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM scholarships_archive ORDER BY deadline DESC")
    scholarships = cur.fetchall()
    cur.execute("SELECT * FROM internships_archive ORDER BY deadline DESC")
    internships = cur.fetchall()
    conn.close()

    return render_template("archives.html", scholarships=scholarships, internships=internships)

@app.route("/delete_archived_scholarship/<int:id>", methods=["POST"])
def delete_archived_scholarship(id):
    if not session.get("logged_in"):
        return "Unauthorized", 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM scholarships_archive WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("archives"))

@app.route("/delete_archived_internship/<int:id>", methods=["POST"])
def delete_archived_internship(id):
    if not session.get("logged_in"):
        return "Unauthorized", 403

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM internships_archive WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Archived internship deleted.", "danger")
    return redirect(url_for("archives"))


@app.route("/add", methods=["GET", "POST"])
def add_scholarship():
    # logic to render form and handle submission
    return render_template("submit.html") 


@app.route("/submit", methods=["GET", "POST"])
def submit_scholarship():
    if request.method == "POST":
        name = request.form["title"]
        provider = request.form["provider"]
        eligibility = request.form["eligibility"]
        amount = request.form["amount"]
        deadline = request.form["deadline"]
        link = request.form["link"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO scholarships (name, provider, eligibility, amount, deadline, link, approved)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (name, provider, eligibility, amount, deadline, link))

        # Fetch all newsletter subscribers
        cur.execute("SELECT email FROM subscribers")
        subscribers = cur.fetchall()

        conn.commit()
        conn.close()

        # Send email to each subscriber
        for subscriber in subscribers:
            try:
                msg = Message(
                    subject="🎓 New Scholarship Submitted!",
                    sender=app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[subscriber['email']],
                    body=f"A new scholarship '{name}' has been submitted. Visit the site to check it out!"
                )
                mail.send(msg)
            except Exception as e:
                print(f"Failed to send email to {subscriber['email']}: {e}")

        flash("Scholarship submitted and pending approval.", "success")
        return redirect(url_for("submit_scholarship"))

    return render_template("submit.html")


@app.route("/submit-internship", methods=["GET", "POST"])
def submit_internship():
    if request.method == "POST":
        name = request.form["title"]
        provider = request.form["company"]
        eligibility = request.form["eligibility"]
        amount = request.form["stipend"]
        deadline = request.form["deadline"]
        link = request.form["link"]
        duration = request.form["duration"]
        location = request.form["location"]


        conn = get_db_connection()
        cur = conn.cursor()

        # Save internship to database
        cur.execute(""" INSERT INTO internships 
        (name, provider, eligibility, amount, deadline, link, duration, location, approved)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (name, provider, eligibility, amount, deadline, link, duration, location))

        # Fetch all newsletter subscribers
        cur.execute("SELECT email FROM subscribers")
        subscribers = cur.fetchall()

        conn.commit()
        conn.close()

        # Send email to each subscriber
        for subscriber in subscribers:
            try:
                msg = Message(
                    subject="🚀 New Internship Submitted!",
                    sender=app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[subscriber['email']],
                    body=f"A new internship '{name}' has been submitted. Visit the site to check it out!"
                )
                mail.send(msg)
            except Exception as e:
                print(f"Failed to send email to {subscriber['email']}: {e}")

        flash("Internship submitted and pending approval.", "success")
        return redirect(url_for("submit_internship"))

    return render_template("submit_internship.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "your_password": 
            session.permanent = True           
            session["logged_in"] = True
            session["user_role"] = "admin"     
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/admin")
def admin():
   
    if not session.get("logged_in") or session.get("user_role") != "admin":
        flash("You must be an admin to access this page.", "danger")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch unapproved scholarships
    cur.execute("SELECT * FROM scholarships WHERE approved = 0 ORDER BY deadline")
    unapproved_scholarships = cur.fetchall()

    # Fetch unapproved internships
    cur.execute("SELECT * FROM internships WHERE approved = 0 ORDER BY deadline")
    unapproved_internships = cur.fetchall()

    conn.close()
    return render_template("admin.html", scholarships=unapproved_scholarships, internships=unapproved_internships)

@app.route('/approve_scholarship/<int:id>')
def approve_scholarship(id):
    if not session.get("logged_in"):
        return "Unauthorized", 403

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row 
    cur = conn.cursor()

    # Get scholarship details
    cur.execute("SELECT * FROM scholarships WHERE id = ?", (id,))
    scholarship = cur.fetchone()

    if scholarship:
        # Insert into archive
        cur.execute("""
            INSERT INTO scholarships_archive
            (name, provider, eligibility, amount, deadline, link, approved)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (
            scholarship["name"], scholarship["provider"], scholarship["eligibility"],
            scholarship["amount"], scholarship["deadline"], scholarship["link"]
        ))

        # Mark as approved instead of deleting
        cur.execute("UPDATE scholarships SET approved = 1 WHERE id = ?", (id,))

        conn.commit()

        # Get subscriber emails
        cur.execute("SELECT email FROM subscribers")
        subscribers = cur.fetchall()
        conn.close()

        # Send email to each subscriber
        for subscriber in subscribers:
            email = subscriber['email']
            message = Message(
                subject=f"🎓 New Scholarship: {scholarship['name']}",
                sender='your_email@email.com',
                recipients=[email],
                body=(
                    f"📢 A new scholarship has been approved and is now live!\n\n"
                    f"🔹 Title: {scholarship['name']}\n"
                    f"🏢 Provider: {scholarship['provider']}\n"
                    f"📌 Eligibility: {scholarship['eligibility']}\n"
                    f"🗓️ Deadline: {scholarship['deadline']}\n"
                    f"🔗 Link: {scholarship['link']}\n\n"
                    f"Visit our website to explore more opportunities!"
                )
            )
            try:
                mail.send(message)
            except Exception as e:
                print(f"Error sending to {email}: {e}")

        flash("Scholarship approved, archived, and email sent to subscribers.", "success")
    else:
        flash("Scholarship not found.", "danger")

    return redirect(url_for('admin'))


@app.route("/approve-internship/<int:id>")
def approve_internship(id):
    if not session.get("logged_in"):
        return "Unauthorized", 403

    conn = get_db_connection()
    cur = conn.cursor()

    # fetch internship
    internship = cur.execute("SELECT * FROM internships WHERE id = ?", (id,)).fetchone()
    if internship:
        # insert into archive
        cur.execute("""
            INSERT INTO internships_archive
            (name, provider, eligibility, amount, deadline, link, duration, location, approved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (internship["name"], internship["provider"], internship["eligibility"],
              internship["amount"], internship["deadline"], internship["link"],
              internship["duration"], internship["location"]))

           
        cur.execute("UPDATE internships SET approved = 1 WHERE id = ?", (id,))

        conn.commit()

    conn.close()
    return redirect(url_for("admin"))


@app.route('/delete_scholarship/<int:id>')
def delete_scholarship(id):
    if not session.get("logged_in") or session.get("user_role"):
        flash("You do not have permission to perform this action.", "danger")
        return redirect(url_for('home'))

    conn = get_db_connection()
    cur = conn.cursor()

    
    cur.execute("DELETE FROM scholarships WHERE id = ?", (id,))
    cur.execute("DELETE FROM scholarships_archive WHERE id = ?", (id,))

    conn.commit()
    conn.close()
    flash("Scholarship deleted.", "danger")
    return redirect(url_for('admin'))

@app.route('/delete_scholarship_main/<int:id>', methods=["POST"])
def delete_scholarship_main(id):
    if not session.get("logged_in") or session.get("user_role") != "admin":
        flash("You do not have permission to perform this action.", "danger")
        return redirect(url_for('scholarships'))

    conn = get_db_connection()
    cur = conn.cursor()

   
    cur.execute("DELETE FROM scholarships WHERE id = ?", (id,))

    conn.commit()
    conn.close()
    flash("Scholarship deleted.", "danger")
    return redirect(url_for('scholarships'))

@app.route("/delete-internship/<int:id>")
def delete_internship(id):
    if not session.get("logged_in") or session.get("user_role") != "admin":
        flash("You do not have permission to perform this action.", "danger")
        return redirect(url_for('home'))

    conn = get_db_connection()
    cur = conn.cursor()


    cur.execute("DELETE FROM internships WHERE id = ?", (id,))
    cur.execute("DELETE FROM internships_archive WHERE id = ?", (id,))

    conn.commit()
    conn.close()
    flash("Internship deleted.", "danger")
    return redirect(url_for("admin"))

@app.route("/delete_internship_main/<int:id>", methods=["POST"])
def delete_internship_main(id):
    if not session.get("logged_in") or session.get("user_role") != "admin":
        flash("You do not have permission to perform this action.", "danger")
        return redirect(url_for('home'))

    conn = get_db_connection()
    cur = conn.cursor()

    
    cur.execute("DELETE FROM internships WHERE id = ?", (id,))
    cur.execute("DELETE FROM internships_archive WHERE id = ?", (id,))

    conn.commit()
    conn.close()
    flash("Internship deleted.", "danger")
    return redirect(url_for("internships"))

@app.route("/logout")
def logout():
    session.clear()  
    flash("You have been logged out.", "info")
    session.pop("logged_in", None)
    return redirect(url_for("login"))


@app.route("/")
def home():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM scholarships WHERE approved = 1")
    scholarship_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM internships WHERE approved = 1")
    internship_count = cur.fetchone()[0]

    conn.close()
    return render_template("home.html", scholarship_count=scholarship_count, internship_count=internship_count)

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in") or session.get("user_role") != "admin":
        flash("You must be an admin to access the dashboard.", "danger")
        return redirect(url_for("login"))

    conn = get_db_connection()
    c = conn.cursor()

    # Count approved items
    c.execute("SELECT COUNT(*) FROM scholarships WHERE approved = 1")
    approved_scholarships = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM internships WHERE approved = 1")
    approved_internships = c.fetchone()[0]

    # Count pending items
    c.execute("SELECT COUNT(*) FROM scholarships WHERE approved = 0")
    pending_scholarships = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM internships WHERE approved = 0")
    pending_internships = c.fetchone()[0]

    # Combine pending items
    pending_count = pending_scholarships + pending_internships

    c.execute("SELECT COUNT(*) FROM scholarships")
    total_scholarships = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM internships")
    total_internships = c.fetchone()[0]

    conn.close()

    return render_template("dashboard.html",
                           pending_count=pending_count,
                           total_count=total_scholarships,
                           internship_count=total_internships)

@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form["email"].strip()

    if not email:
        flash("Email is required.")
        return redirect(request.referrer)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO subscribers (email) VALUES (?)", (email,))
        conn.commit()

        # Send confirmation email
        msg = Message(
            "Thanks for Subscribing 🎉",
            sender="your_email@email.com",
            recipients=[email]
        )
        msg.body = "You've successfully subscribed to Schoint Finder. We'll notify you about new opportunities!"
        mail.send(msg)

        flash("Subscribed successfully! ✅ Check your email.")
    except sqlite3.IntegrityError:
        flash("You're already subscribed.")
    finally:
        conn.close()

    return redirect(request.referrer)

def notify_subscribers(name, provider, eligibility, amount, deadline, link):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT email FROM subscribers")
    subscribers = cur.fetchall()
    conn.close()

    subject = "🎓 New Scholarship Opportunity!"
    body = f"""
A new scholarship has been added:

🏷️ Name: {name}
🏢 Provider: {provider}
🎯 Eligibility: {eligibility}
💰 Amount: {amount}
⏰ Deadline: {deadline}
🔗 Apply Here: {link}

Visit the Scholarship Finder site for more details.
    """

    for sub in subscribers:
        msg = Message(subject, sender="aditya.prabhu0910@gmail.com", recipients=[sub["email"]])
        msg.body = body
        mail.send(msg)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message_body = request.form["message"]

        try:
            # Create the email message
            msg = Message(
                subject=f"Contact Form Message from {name}",
                recipients=["your_email@email.com"],  
                body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message_body}"
            )

            # Send the email
            mail.send(msg)

            return render_template("contact.html", success=True)
        except Exception as e:
            print("Email failed:", e)
            return render_template("contact.html", error=True)

    return render_template("contact.html")



if __name__ == "__main__":
    app.run(debug=True)
