# import os
# import re
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from flask import Flask, render_template, request, redirect, url_for, flash, session
# from werkzeug.utils import secure_filename
# import pandas as pd
# from email_validator import validate_email, EmailNotValidError
# from markupsafe import Markup

# app = Flask(__name__)
# app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your-secret-key")
# app.config["UPLOAD_FOLDER"] = "uploads"
# app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload size
# app.config["ALLOWED_EXTENSIONS"] = {"csv"}

# # Email configuration
# app.config["SMTP_SERVER"] = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
# app.config["SMTP_PORT"] = int(os.environ.get("SMTP_PORT", 587))
# app.config["SMTP_USERNAME"] = os.environ.get("SMTP_USERNAME", "")
# app.config["SMTP_PASSWORD"] = os.environ.get("SMTP_PASSWORD", "")
# app.config["SENDER_EMAIL"] = os.environ.get("SENDER_EMAIL", "")
# app.config["SENDER_NAME"] = os.environ.get("SENDER_NAME", "Bulk Email Sender")


# def allowed_file(filename):
#     return (
#         "." in filename
#         and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
#     )


# def is_valid_email(email):
#     """Custom email validation function that's more permissive for common domains."""
#     # Basic pattern for email validation
#     pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
#     return re.match(pattern, email) is not None


# def validate_emails(emails):
#     valid_emails = []
#     invalid_emails = []

#     for email in emails:
#         if is_valid_email(email):
#             valid_emails.append(email)
#         else:
#             invalid_emails.append(email)

#     return valid_emails, invalid_emails


# def send_email(recipient, subject, content):
#     """Send an email to a single recipient."""
#     try:
#         # Create message
#         msg = MIMEMultipart()
#         msg["From"] = f"{app.config['SENDER_NAME']} <{app.config['SENDER_EMAIL']}>"
#         msg["To"] = f"{recipient['name']} <{recipient['email']}>"
#         msg["Subject"] = subject

#         # Attach HTML content
#         msg.attach(MIMEText(content, "html"))

#         # Connect to SMTP server
#         server = smtplib.SMTP(app.config["SMTP_SERVER"], app.config["SMTP_PORT"])
#         server.starttls()
#         server.login(app.config["SMTP_USERNAME"], app.config["SMTP_PASSWORD"])

#         # Send email
#         server.send_message(msg)
#         server.quit()

#         return True
#     except Exception as e:
#         print(f"Error sending email to {recipient['email']}: {str(e)}")
#         flash(f"Error sending email to {recipient['email']}: {str(e)}")
#         return False


# def send_bulk_emails(recipients, subject_template, content_template):
#     """Send emails to multiple recipients with personalized content."""
#     successful = 0
#     failed = 0

#     for recipient in recipients:
#         # Replace placeholders with recipient data
#         subject = subject_template.replace("{{name}}", recipient["name"]).replace(
#             "{{email}}", recipient["email"]
#         )
#         content = content_template.replace("{{name}}", recipient["name"]).replace(
#             "{{email}}", recipient["email"]
#         )

#         # Convert newlines to <br> tags for HTML
#         content_html = content.replace("\n", "<br>")

#         # Send the email
#         if send_email(recipient, subject, content_html):
#             successful += 1
#         else:
#             failed += 1

#     return successful, failed


# @app.route("/")
# def index():
#     return render_template("index.html")


# @app.route("/upload", methods=["POST"])
# def upload_file():
#     if "files" not in request.files:
#         flash("No file part")
#         return redirect(request.url)

#     files = request.files.getlist("files")

#     if not files or files[0].filename == "":
#         flash("No selected file")
#         return redirect(request.url)

#     all_data = []
#     invalid_entries = []

#     for file in files:
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
#             file.save(filepath)

#             try:
#                 # Read CSV file
#                 df = pd.read_csv(filepath)

#                 # Check if required columns exist
#                 if "emails" not in df.columns or "names" not in df.columns:
#                     flash(
#                         f"Error in {filename}: Missing required columns (emails, names)"
#                     )
#                     continue

#                 # Validate emails
#                 valid_emails = []
#                 file_invalid_entries = []

#                 for index, row in df.iterrows():
#                     email = str(row["emails"]).strip()
#                     name = str(row["names"]).strip()

#                     if is_valid_email(email):
#                         valid_emails.append({"email": email, "name": name})
#                     else:
#                         file_invalid_entries.append({"email": email, "name": name})

#                 all_data.extend(valid_emails)
#                 invalid_entries.extend(file_invalid_entries)

#             except Exception as e:
#                 flash(f"Error processing {filename}: {str(e)}")

#     # Remove duplicates (keeping only the first occurrence)
#     unique_emails = []
#     seen_emails = set()

#     for entry in all_data:
#         if entry["email"] not in seen_emails:
#             unique_emails.append(entry)
#             seen_emails.add(entry["email"])

#     # Store in session
#     session["recipients"] = unique_emails
#     session["invalid_entries"] = invalid_entries

#     return redirect(url_for("compose"))


# @app.route("/compose")
# def compose():
#     recipients = session.get("recipients", [])
#     invalid_entries = session.get("invalid_entries", [])

#     # Get a sample recipient for preview if available
#     sample_recipient = (
#         recipients[0]
#         if recipients
#         else {"name": "John Doe", "email": "john@example.com"}
#     )

#     return render_template(
#         "compose.html",
#         recipients=recipients,
#         invalid_entries=invalid_entries,
#         sample_recipient=sample_recipient,
#     )


# @app.route("/preview", methods=["POST"])
# def preview():
#     subject = request.form.get("subject", "")
#     content = request.form.get("content", "")
#     recipients = session.get("recipients", [])

#     # Get a sample recipient for preview
#     sample_recipient = (
#         recipients[0]
#         if recipients
#         else {"name": "John Doe", "email": "john@example.com"}
#     )

#     # Replace placeholders with sample data
#     preview_subject = subject.replace("{{name}}", sample_recipient["name"]).replace(
#         "{{email}}", sample_recipient["email"]
#     )
#     preview_content = content.replace("{{name}}", sample_recipient["name"]).replace(
#         "{{email}}", sample_recipient["email"]
#     )

#     # Convert newlines to <br> tags for HTML display
#     preview_content_html = Markup(preview_content.replace("\n", "<br>"))

#     return render_template(
#         "preview.html",
#         subject=subject,
#         content=content,
#         preview_subject=preview_subject,
#         preview_content=preview_content_html,
#         sample_recipient=sample_recipient,
#     )


# @app.route("/send", methods=["POST"])
# def send_emails():
#     subject = request.form.get("subject", "")
#     content = request.form.get("content", "")
#     recipients = session.get("recipients", [])

#     # Actually send emails instead of simulating
#     successful, failed = send_bulk_emails(recipients, subject, content)

#     # Clear session data after sending
#     session.pop("recipients", None)
#     session.pop("invalid_entries", None)

#     flash(f"Successfully sent {successful} emails. Failed: {failed}")
#     return redirect(url_for("index"))


# @app.route("/settings", methods=["GET", "POST"])
# def settings():
#     if request.method == "POST":
#         # Update email settings
#         app.config["SMTP_SERVER"] = request.form.get("smtp_server", "")
#         app.config["SMTP_PORT"] = int(request.form.get("smtp_port", 587))
#         app.config["SMTP_USERNAME"] = request.form.get("smtp_username", "")
#         app.config["SMTP_PASSWORD"] = request.form.get("smtp_password", "")
#         app.config["SENDER_EMAIL"] = request.form.get("sender_email", "")
#         app.config["SENDER_NAME"] = request.form.get("sender_name", "")

#         flash("Email settings updated successfully")
#         return redirect(url_for("index"))

#     return render_template(
#         "settings.html",
#         smtp_server=app.config["SMTP_SERVER"],
#         smtp_port=app.config["SMTP_PORT"],
#         smtp_username=app.config["SMTP_USERNAME"],
#         sender_email=app.config["SENDER_EMAIL"],
#         sender_name=app.config["SENDER_NAME"],
#     )


# # Add a filter to convert newlines to <br> tags
# @app.template_filter("nl2br")
# def nl2br(value):
#     return Markup(value.replace("\n", "<br>"))


# if __name__ == "__main__":
#     os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)), debug=False)

import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import pandas as pd
from email_validator import validate_email, EmailNotValidError
from markupsafe import Markup

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your-secret-key")
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload size
app.config["ALLOWED_EXTENSIONS"] = {"csv"}

# Email configuration
app.config["SMTP_SERVER"] = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
app.config["SMTP_PORT"] = int(os.environ.get("SMTP_PORT", 587))
app.config["SMTP_USERNAME"] = os.environ.get("SMTP_USERNAME", "")
app.config["SMTP_PASSWORD"] = os.environ.get("SMTP_PASSWORD", "")
app.config["SENDER_EMAIL"] = os.environ.get("SENDER_EMAIL", "")
app.config["SENDER_NAME"] = os.environ.get("SENDER_NAME", "Bulk Email Sender")


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def is_valid_email(email):
    """Custom email validation function that's more permissive for common domains."""
    # Basic pattern for email validation
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def extract_name_from_email(email):
    """Extract the part before @ as a name if no name is provided."""
    if not email:
        return ""
    return email.split("@")[0]


def validate_emails(emails):
    valid_emails = []
    invalid_emails = []

    for email in emails:
        if is_valid_email(email):
            valid_emails.append(email)
        else:
            invalid_emails.append(email)

    return valid_emails, invalid_emails


def send_email(recipient, subject, content):
    """Send an email to a single recipient."""
    try:
        # Create message
        msg = MIMEMultipart()
        msg["From"] = f"{app.config['SENDER_NAME']} <{app.config['SENDER_EMAIL']}>"
        msg["To"] = f"{recipient['name']} <{recipient['email']}>"
        msg["Subject"] = subject

        # Attach HTML content
        msg.attach(MIMEText(content, "html"))

        # Connect to SMTP server
        server = smtplib.SMTP(app.config["SMTP_SERVER"], app.config["SMTP_PORT"])
        server.starttls()
        server.login(app.config["SMTP_USERNAME"], app.config["SMTP_PASSWORD"])

        # Send email
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        print(f"Error sending email to {recipient['email']}: {str(e)}")
        flash(f"Error sending email to {recipient['email']}: {str(e)}")
        return False


def send_bulk_emails(recipients, subject_template, content_template):
    """Send emails to multiple recipients with personalized content."""
    successful = 0
    failed = 0

    for recipient in recipients:
        # Replace placeholders with recipient data
        subject = subject_template.replace("{{name}}", recipient["name"]).replace(
            "{{email}}", recipient["email"]
        )
        content = content_template.replace("{{name}}", recipient["name"]).replace(
            "{{email}}", recipient["email"]
        )

        # Convert newlines to <br> tags for HTML
        content_html = content.replace("\n", "<br>")

        # Send the email
        if send_email(recipient, subject, content_html):
            successful += 1
        else:
            failed += 1

    return successful, failed


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "files" not in request.files:
        flash("No file part")
        return redirect(request.url)

    files = request.files.getlist("files")

    if not files or files[0].filename == "":
        flash("No selected file")
        return redirect(request.url)

    all_data = []
    invalid_entries = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            try:
                # Read CSV file
                df = pd.read_csv(filepath)

                # Check if required columns exist
                if "emails" not in df.columns:
                    flash(f"Error in {filename}: Missing required column (emails)")
                    continue

                # Validate emails
                valid_emails = []
                file_invalid_entries = []

                for index, row in df.iterrows():
                    email = str(row["emails"]).strip()

                    # Check if names column exists and has a value, otherwise extract from email
                    if (
                        "names" in df.columns
                        and not pd.isna(row["names"])
                        and str(row["names"]).strip()
                    ):
                        name = str(row["names"]).strip()
                    else:
                        name = extract_name_from_email(email)

                    if is_valid_email(email):
                        valid_emails.append({"email": email, "name": name})
                    else:
                        file_invalid_entries.append({"email": email, "name": name})

                all_data.extend(valid_emails)
                invalid_entries.extend(file_invalid_entries)

            except Exception as e:
                flash(f"Error processing {filename}: {str(e)}")

    # Remove duplicates (keeping only the first occurrence)
    unique_emails = []
    seen_emails = set()

    for entry in all_data:
        if entry["email"] not in seen_emails:
            unique_emails.append(entry)
            seen_emails.add(entry["email"])

    # Store in session
    session["recipients"] = unique_emails
    session["invalid_entries"] = invalid_entries

    return redirect(url_for("compose"))


@app.route("/compose")
def compose():
    recipients = session.get("recipients", [])
    invalid_entries = session.get("invalid_entries", [])

    # Get a sample recipient for preview if available
    sample_recipient = (
        recipients[0]
        if recipients
        else {"name": "John Doe", "email": "john@example.com"}
    )

    return render_template(
        "compose.html",
        recipients=recipients,
        invalid_entries=invalid_entries,
        sample_recipient=sample_recipient,
    )


@app.route("/preview", methods=["POST"])
def preview():
    subject = request.form.get("subject", "")
    content = request.form.get("content", "")
    recipients = session.get("recipients", [])

    # Get a sample recipient for preview
    sample_recipient = (
        recipients[0]
        if recipients
        else {"name": "John Doe", "email": "john@example.com"}
    )

    # Replace placeholders with sample data
    preview_subject = subject.replace("{{name}}", sample_recipient["name"]).replace(
        "{{email}}", sample_recipient["email"]
    )
    preview_content = content.replace("{{name}}", sample_recipient["name"]).replace(
        "{{email}}", sample_recipient["email"]
    )

    # Convert newlines to <br> tags for HTML display
    preview_content_html = Markup(preview_content.replace("\n", "<br>"))

    return render_template(
        "preview.html",
        subject=subject,
        content=content,
        preview_subject=preview_subject,
        preview_content=preview_content_html,
        sample_recipient=sample_recipient,
    )


@app.route("/send", methods=["POST"])
def send_emails():
    subject = request.form.get("subject", "")
    content = request.form.get("content", "")
    recipients = session.get("recipients", [])

    # Actually send emails instead of simulating
    successful, failed = send_bulk_emails(recipients, subject, content)

    # Clear session data after sending
    session.pop("recipients", None)
    session.pop("invalid_entries", None)

    flash(f"Successfully sent {successful} emails. Failed: {failed}")
    return redirect(url_for("index"))


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        # Update email settings
        app.config["SMTP_SERVER"] = request.form.get("smtp_server", "")
        app.config["SMTP_PORT"] = int(request.form.get("smtp_port", 587))
        app.config["SMTP_USERNAME"] = request.form.get("smtp_username", "")
        app.config["SMTP_PASSWORD"] = request.form.get("smtp_password", "")
        app.config["SENDER_EMAIL"] = request.form.get("sender_email", "")
        app.config["SENDER_NAME"] = request.form.get("sender_name", "")

        flash("Email settings updated successfully")
        return redirect(url_for("index"))

    return render_template(
        "settings.html",
        smtp_server=app.config["SMTP_SERVER"],
        smtp_port=app.config["SMTP_PORT"],
        smtp_username=app.config["SMTP_USERNAME"],
        sender_email=app.config["SENDER_EMAIL"],
        sender_name=app.config["SENDER_NAME"],
    )


# Add a filter to convert newlines to <br> tags
@app.template_filter("nl2br")
def nl2br(value):
    return Markup(value.replace("\n", "<br>"))


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)), debug=False)
