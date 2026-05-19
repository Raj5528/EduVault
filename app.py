from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for,
    send_from_directory,
    flash,
    
)
import boto3
from werkzeug.security import (

    generate_password_hash,

    check_password_hash
)

from werkzeug.middleware.proxy_fix import ProxyFix
import json
from authlib.integrations.flask_client import OAuth

from dotenv import load_dotenv
import re
import os
import shutil

from datetime import datetime

from werkzeug.utils import secure_filename
load_dotenv()
app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
# ================= AWS S3 =================

from botocore.client import Config

s3 = boto3.client(

    "s3",

    region_name="ap-south-1",

    aws_access_key_id=os.getenv(
        "AWS_ACCESS_KEY"
    ),

    aws_secret_access_key=os.getenv(
        "AWS_SECRET_ACCESS_KEY"
    ),

    config=Config(

        signature_version="s3v4",

        s3={
            "addressing_style": "path"
        }
    )
)

S3_BUCKET = (

    "minor-project-eduvault-storage-571600834242-ap-south-1-an"
)
# ================= GOOGLE AUTH =================

oauth = OAuth(app)

google = oauth.register(

    name="google",

    client_id=os.getenv(
        "GOOGLE_CLIENT_ID"
     ),

    client_secret=os.getenv(
      "GOOGLE_CLIENT_SECRET"
     ),

    server_metadata_url=
    "https://accounts.google.com/.well-known/openid-configuration",

    client_kwargs={

        "scope": "openid email profile"
    }
)
# ================= ACTIVITY =================

activities = []




# ================= FILE TYPE =================

def get_file_type(filename):

    ext = filename.split(".")[-1].lower()

    if ext == "pdf":
        return "pdf"

    if ext in ["doc", "docx"]:
        return "docx"

    if ext in ["png", "jpg", "jpeg", "gif"]:
        return "image"

    if ext in ["ppt", "pptx"]:
        return "ppt"

    if ext in ["xls", "xlsx", "csv"]:
        return "excel"

    return "other"
# ================= SAFE EMAIL =================

def get_safe_email():

    return (

        session["user"]["email"]

        .replace("@", "_")

        .replace(".", "_")
    )
# ================= FAVORITES =================

def get_user_favorites_file():

    email = session["user"]["email"]

    os.makedirs(

        "favorites",

        exist_ok=True
    )

    return os.path.join(

        "favorites",

        f"{email}.json"
    )


def load_favorites():

    favorites_file = get_user_favorites_file()

    if not os.path.exists(
        favorites_file
    ):

        return []

    with open(

        favorites_file,

        "r"
    ) as f:

        return json.load(f)


def save_favorites(favorites):

    favorites_file = get_user_favorites_file()

    with open(

        favorites_file,

        "w"
    ) as f:

        json.dump(

            favorites,

            f,

            indent=4
        )

# ================= USERS =================

def load_users():

    if not os.path.exists(
        "users.json"
    ):

        return {}

    with open(

        "users.json",

        "r"
    ) as f:

        return json.load(f)


def save_users(users):

    with open(

        "users.json",

        "w"
    ) as f:

        json.dump(

            users,

            f,

            indent=4
        )
# ================= USER PROFILES =================

def load_profiles():

    if not os.path.exists(
        "user_profiles.json"
    ):

        return {}

    with open(

        "user_profiles.json",

        "r"
    ) as f:

        return json.load(f)


def save_profiles(profiles):

    with open(

        "user_profiles.json",

        "w"
    ) as f:

        json.dump(

            profiles,

            f,

            indent=4
        )
# ================= GET FILES =================

def get_files(folder_type):

    files = []

    email = get_safe_email()

    if folder_type == "uploads":

        prefix = f"{email}/"

    else:

        prefix = f"trash/{email}/"

    response = s3.list_objects_v2(

        Bucket=S3_BUCKET,

        Prefix=prefix
    )

    if "Contents" not in response:

        return []

    for obj in response["Contents"]:

        key = obj["Key"]

        filename = key.replace(

            prefix,

            ""
        )

        if filename == "":

            continue

        modified = obj[
            "LastModified"
        ]

        size_kb = round(

            obj["Size"] / 1024,

            2
        )

        files.append({

            "name": filename,

            "size":
                f"{size_kb} KB",

            "type":
                get_file_type(filename),

            "date":
                modified.strftime(
                    "%d %b %Y"
                ),

            "timestamp":
                modified.timestamp()

        })

    files.sort(

        key=lambda x: x["timestamp"],

        reverse=True
    )

    return files
# ================= USER ACTIVITY =================
def get_user_activity_file():

    email = session["user"]["email"]

    activity_file = os.path.join(

        "activities",

        f"{email}.json"
    )

    os.makedirs(

        "activities",

        exist_ok=True
    )

    return activity_file
# ================= USER STORAGE =================

def get_user_folder():

    email = session["user"]["email"]

    folder = os.path.join(

        UPLOAD_FOLDER,

        email
    )

    os.makedirs(

        folder,

        exist_ok=True
    )

    return folder


def get_user_trash_folder():

    email = session["user"]["email"]

    folder = os.path.join(

        TRASH_FOLDER,

        email
    )

    os.makedirs(

        folder,

        exist_ok=True
    )

    return folder

# ================= STORAGE =================

def get_storage_data():

    total_bytes = 0

    email = get_safe_email()

    prefix = f"{email}/"

    response = s3.list_objects_v2(

        Bucket=S3_BUCKET,

        Prefix=prefix
    )

    if "Contents" in response:

        for obj in response["Contents"]:

            total_bytes += obj["Size"]

    total_gb = round(

        total_bytes / (1024 * 1024 * 1024),

        4
    )

    max_storage = 1

    percent = min(

        int((total_gb / max_storage) * 100),

        100
    )

    stroke_offset = 440 - int(

        (440 * percent) / 100
    )

    total_mb = round(

        total_bytes / (1024 * 1024),

        2
    )

    return {

        "used_gb": total_gb,

        "used_mb": total_mb,

        "max_gb": max_storage,

        "percent": percent,

        "stroke_offset": stroke_offset,

        "file_count":

            len(
                response.get(
                    "Contents",
                    []
                )
            )
    }
# ================= ACTIVITY LOG =================

def add_activity(action, filename):

    activity_file = get_user_activity_file()

    activities = []

    if os.path.exists(activity_file):

        with open(

            activity_file,

            "r"
        ) as f:

            activities = json.load(f)

    activities.insert(0, {

        "action": action,

        "filename": filename
    })

    if len(activities) > 10:

        activities.pop()

    with open(

        activity_file,

        "w"
    ) as f:

        json.dump(

            activities,

            f,

            indent=4
        )
# ================= GET FILE URL =================

@app.route("/file-url/<path:filename>")

def get_file_url(filename):

    if "user" not in session:

        return "", 401

    source = request.args.get(

        "source",

        "uploads"
    )

    email = get_safe_email()

    if source == "trash":

        key = (

            f"trash/{email}/"

            +

            filename
        )

    else:

        key = (

            f"{email}/"

            +

            filename
        )

    url = s3.generate_presigned_url(

        "get_object",

        Params={

            "Bucket": S3_BUCKET,

            "Key": key
        },

        ExpiresIn=3600
    )

    return {

        "url": url
    }
# ================= CONFIG =================

app.secret_key = os.getenv(
    "SECRET_KEY"
)

UPLOAD_FOLDER = "uploads"
TRASH_FOLDER = "trash"
PROFILE_PICTURE_FOLDER = "profile_pictures"

os.makedirs(
    PROFILE_PICTURE_FOLDER,
    exist_ok=True
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRASH_FOLDER, exist_ok=True)



# ================= HOME =================

@app.route("/")
def home():

    return render_template("index.html")


# ================= FEATURES =================

@app.route("/features")
def features():

    return render_template("features.html")

# ================= GOOGLE LOGIN =================

@app.route("/login/google")

def google_login():

    redirect_uri = url_for(

        "authorize",

        _external=True
    )

    return google.authorize_redirect(
        redirect_uri
    )
@app.route("/callback")

def authorize():

    token = google.authorize_access_token()

    user_info = token.get("userinfo")

    session["user"] = {

        "name":
        user_info["name"],

        "email":
        user_info["email"],

        "picture":
        user_info["picture"]
    }
    profiles = load_profiles()

    email = user_info["email"]

    if email not in profiles:

     profiles[email] = {

        "display_name":
        user_info["name"],

        "custom_email":
        user_info["email"],

        "profile_picture":
        user_info["picture"],

        "theme": "light"
    }
    save_profiles(profiles)
    
    flash(

    f"Welcome back, {user_info['name']}!",

    "success"
)

    return redirect(
        url_for("dashboard")
    )
# ================= LOGIN =================

@app.route("/login", methods=["POST"])

def login():

    username = request.form.get(
        "username"
    )

    password = request.form.get(
        "password"
    )

    users = load_users()

    # ================= USER CHECK =================

    if username not in users:

        flash(

            "Invalid login credentials!",

            "delete"
        )

        return redirect(
            url_for("home") + "#login"
        )

    stored_password = users[username][
        "password"
    ]

    # ================= PASSWORD CHECK =================

    if not check_password_hash(

        stored_password,

        password
    ):

        flash(

            "Invalid login credentials!",

            "delete"
        )

        return redirect(
            url_for("home") + "#login"
        )

    # ================= SESSION =================

    session["user"] = {

        "name": username,

        "email": f"{username}@local",

        "picture": ""
    }

    flash(

        f"Welcome back, {username}!",

        "success"
    )

    return redirect(
        url_for("dashboard")
    )
# ================= PASSWORD VALIDATION =================

def is_strong_password(password):

    if len(password) < 8:

        return False

    if not re.search(r"[A-Z]", password):

        return False

    if not re.search(r"[a-z]", password):

        return False

    if not re.search(r"[0-9]", password):

        return False

    if not re.search(
        r"[!@#$%^&*(),.?\":{}|<>]",
        password
    ):

        return False

    return True
# ================= SIGNUP =================

@app.route("/signup", methods=["POST"])

def signup():

    username = request.form.get(
        "username"
    )

    password = request.form.get(
        "password"
    )

    users = load_users()

    # ================= DUPLICATE CHECK =================

    if username in users:

        flash(

            "Username already exists!",

            "delete"
        )

        return redirect(
            url_for("home") + "#signup"
        )
# ================= PASSWORD STRENGTH =================

    if not is_strong_password(password):

        flash(

        "Password must contain uppercase, lowercase, number, special character and be at least 8 characters long!",

        "delete"
        )

        return redirect(
        url_for("home") + "#signup"
        )
    # ================= PASSWORD HASH =================

    hashed_password = generate_password_hash(
        password
    )

    # ================= SAVE USER =================

    users[username] = {

        "password":
        hashed_password
    }

    save_users(users)
    
    profiles = load_profiles()

    profiles[f"{username}@local"] = {

    "display_name": username,

    "custom_email": "",

    "profile_picture": "",

    "theme": "light"
}

    save_profiles(profiles)
    
    session["user"] = {

    "name": username,

    "email": f"{username}@local",

    "picture": ""
}

    flash(

        "Account created successfully!",

        "success"
    )

    return redirect(
        url_for("dashboard")
    )
    
    
# ================= DASHBOARD =================

@app.route("/dashboard")

def dashboard():

    if "user" not in session:

        return redirect(
            url_for("home")
        )

    files = get_files(
        "uploads"
    )

    trash_files = get_files(
        "trash"
    )

    storage_data = get_storage_data()
    favorites = load_favorites()

    favorite_files = [

        file for file in files

        if file["name"] in favorites
    ]

    # ================= USER ACTIVITIES =================

    activity_file = get_user_activity_file()

    activities = []

    if os.path.exists(activity_file):

        with open(

            activity_file,

            "r"
        ) as f:

            activities = json.load(f)
    profiles = load_profiles()

    email = session["user"]["email"]

    profile = profiles.get(email)

    if not profile:

     profile = {

        "display_name":
        session["user"]["name"],

        "custom_email":
        session["user"]["email"],

        "profile_picture":
        session["user"]["picture"],

        "theme": "light"
    }

    profiles[email] = profile

    save_profiles(profiles)

    return render_template(

        "dashboard.html",

        files=files,

        trash_files=trash_files,

        storage_data=storage_data,

        activities=activities,

        favorites=favorites,

        favorite_files=favorite_files,
        
        profile=profile
    )
# ================= UPLOAD =================

@app.route("/upload", methods=["POST"])

def upload():

    if "user" not in session:

        return redirect(url_for("home"))

    uploaded_files = request.files.getlist("file")

    uploaded_count = 0

    for file in uploaded_files:

        if file and file.filename != "":

            filename = secure_filename(file.filename)

            s3.upload_fileobj(

                file,

                S3_BUCKET,

                f"{get_safe_email()}/{filename}",

                ExtraArgs={

                    "ContentType":
                    file.content_type
                }
            )

            add_activity(
                "uploaded",
                file.filename
            )

            uploaded_count += 1

    flash(
        f"{uploaded_count} file(s) uploaded successfully!",
        "success"
    )

    return redirect(url_for("dashboard"))

# ================= PREVIEW =================

@app.route("/uploads/<filename>")

def download_file(filename):

    if "user" not in session:

        return redirect(
            url_for("home")
        )

    key = (

        f"{get_safe_email()}/"

        +

        filename
    )

    url = s3.generate_presigned_url(

        "get_object",

        Params={

            "Bucket": S3_BUCKET,

            "Key": key
        },

        ExpiresIn=3600
    )

    return redirect(url)
# ================= TRASH-PREVIEW =================

@app.route("/trash/<filename>")

def trash_file(filename):

    if "user" not in session:

        return redirect(
            url_for("home")
        )

    trash_folder = get_user_trash_folder()

    return send_from_directory(

        trash_folder,

        filename,

        as_attachment=False
    )
# ================= REAL DOWNLOAD =================

@app.route("/download/<filename>")

def real_download(filename):

    if "user" not in session:

        return redirect(
            url_for("home")
        )

    key = (

        f"{get_safe_email()}/"

        +

        filename
    )

    url = s3.generate_presigned_url(

        "get_object",

        Params={

            "Bucket": S3_BUCKET,

            "Key": key
        },

        ExpiresIn=3600
    )

    return redirect(url)

# ================= SHARE FILE =================

@app.route("/share/<filename>")

def share_file(filename):

    if "user" not in session:

        return "", 401

    key = (

        f"{get_safe_email()}/"

        +

        filename
    )

    url = s3.generate_presigned_url(

        "get_object",

        Params={

            "Bucket": S3_BUCKET,

            "Key": key
        },

        ExpiresIn=86400
    )

    return {

        "url": url
    }
# ================= DELETE =================

@app.route("/delete/<filename>")

def delete(filename):

    if "user" not in session:

        return redirect(
            url_for("home")
        )

    email = get_safe_email()

    source_key = (

        f"{email}/"

        +

        filename
    )

    trash_key = (

        f"trash/{email}/"

        +

        filename
    )

    # COPY TO TRASH

    s3.copy_object(

        Bucket=S3_BUCKET,

        CopySource={

            "Bucket": S3_BUCKET,

            "Key": source_key
        },

        Key=trash_key
    )

    # DELETE ORIGINAL

    s3.delete_object(

        Bucket=S3_BUCKET,

        Key=source_key
    )

    add_activity(

        "deleted",

        filename
    )

    return "", 204                              
# ================= RECOVER =================

@app.route("/recover/<filename>")

def recover(filename):

    if "user" not in session:

        return redirect(
            url_for("home")
        )

    email = get_safe_email()

    trash_key = (

        f"trash/{email}/"

        +

        filename
    )

    upload_key = (

        f"{email}/"

        +

        filename
    )

    # COPY BACK

    s3.copy_object(

        Bucket=S3_BUCKET,

        CopySource={

            "Bucket": S3_BUCKET,

            "Key": trash_key
        },

        Key=upload_key
    )

    # DELETE FROM TRASH

    s3.delete_object(

        Bucket=S3_BUCKET,

        Key=trash_key
    )

    add_activity(

        "recovered",

        filename
    )

    return "", 204
# ================= RECOVER ALL =================

@app.route("/recover-all")

def recover_all():

    if "user" not in session:

        return redirect(
            url_for("home")
        )

    email = get_safe_email()

    prefix = f"trash/{email}/"

    response = s3.list_objects_v2(

        Bucket=S3_BUCKET,

        Prefix=prefix
    )

    if "Contents" in response:

        for obj in response["Contents"]:

            trash_key = obj["Key"]

            filename = trash_key.replace(

                prefix,

                ""
            )

            upload_key = (

                f"{email}/"

                +

                filename
            )

            # COPY BACK

            s3.copy_object(

                Bucket=S3_BUCKET,

                CopySource={

                    "Bucket": S3_BUCKET,

                    "Key": trash_key
                },

                Key=upload_key
            )

            # DELETE FROM TRASH

            s3.delete_object(

                Bucket=S3_BUCKET,

                Key=trash_key
            )

            add_activity(

                "recovered",

                filename
            )

    return redirect(
        url_for("dashboard")
    )
# ================= DELETE ALL =================

@app.route("/delete-all")

def delete_all():

    if "user" not in session:

        return redirect(
            url_for("home")
        )

    email = get_safe_email()

    prefix = f"trash/{email}/"

    response = s3.list_objects_v2(

        Bucket=S3_BUCKET,

        Prefix=prefix
    )

    if "Contents" in response:

        for obj in response["Contents"]:

            key = obj["Key"]

            filename = key.replace(

                prefix,

                ""
            )

            s3.delete_object(

                Bucket=S3_BUCKET,

                Key=key
            )
            favorites = load_favorites()

            if filename in favorites:

                favorites.remove(
        filename
    )

                save_favorites(
    favorites
)

            add_activity(

                "deleted forever",

                filename
            )

    return redirect(
        url_for("dashboard")
    )
@app.route("/test-s3")

def test_s3():

    obj = s3.get_object(

        Bucket=S3_BUCKET,

        Key="DemonSlayer_local/sample_pdf.pdf"
    )

    return str(obj["ContentLength"])

# ================= DELETE FOREVER =================

@app.route("/permanent-delete/<filename>")

def permanent_delete(filename):

    if "user" not in session:

        return redirect(
            url_for("home")
        )

    email = get_safe_email()

    trash_key = (

        f"trash/{email}/"

        +

        filename
    )

    s3.delete_object(

        Bucket=S3_BUCKET,

        Key=trash_key
    )
    favorites = load_favorites()

    if filename in favorites:

      favorites.remove(
        filename
    )

      save_favorites(
        favorites
    )

    add_activity(

        "deleted forever",

        filename
    )

    return "", 204
# ================= FAVORITES =================

@app.route("/favorite/<filename>")

def toggle_favorite(filename):

    if "user" not in session:

        return redirect(
            url_for("home")
        )

    favorites = load_favorites()

    if filename in favorites:

        favorites.remove(filename)

    else:

        favorites.append(filename)

    save_favorites(favorites)

    return "", 204
# ================= FAVORITES PARTIAL =================

@app.route(
    "/favorites-partial"
)

def favorites_partial():

    if "user" not in session:

        return "", 401

    files = get_files(
        "uploads"
    )

    favorites = load_favorites()

    favorite_files = [

        file for file in files

        if file["name"] in favorites
    ]

    return render_template(

        "partials/favorites_partial.html",

        favorite_files=favorite_files
    )
    
# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect(url_for("home"))

# ================= CHANGE DISPLAY NAME =================

@app.route(
    "/change-display-name",
    methods=["POST"]
)

def change_display_name():

    if "user" not in session:

        return redirect(
            url_for("home")
        )

    display_name = request.form.get(
        "display_name"
    ).strip()

    profiles = load_profiles()

    email = session["user"]["email"]

    if not display_name:

        flash(

            "Display name cannot be empty!",

            "delete"
        )

        return redirect(
            url_for("dashboard")
        )

    for user_email, profile in profiles.items():

        if (

            profile.get(
                "display_name",
                ""
            ).lower()

            ==

            display_name.lower()

            and

            user_email != email
        ):

            flash(

                "Display name already taken!",

                "delete"
            )

            return redirect(
                url_for("dashboard")
            )

    profiles[email][
        "display_name"
    ] = display_name

    save_profiles(profiles)

    flash(

        "Display name updated!",

        "success"
    )

    return redirect(
        url_for("dashboard")
    )

# ================= CHANGE EMAIL =================

@app.route(
    "/change-email",
    methods=["POST"]
)

def change_email():

    if "user" not in session:

        return redirect(
            url_for("home")
        )

    custom_email = request.form.get(
        "custom_email"
    ).strip()

    profiles = load_profiles()

    email = session["user"]["email"]

    profiles[email][
        "custom_email"
    ] = custom_email

    save_profiles(profiles)

    flash(

        "Email updated successfully!",

        "success"
    )

    return redirect(
        url_for("dashboard")
    )   

# ================= PROFILE PICTURES =================

@app.route(
    "/profile_pictures/<filename>"
)

def profile_picture(filename):

    return send_from_directory(

        PROFILE_PICTURE_FOLDER,

        filename
    )
# ================= CHANGE PROFILE PICTURE =================

@app.route(
    "/change-profile-picture",
    methods=["POST"]
)

def change_profile_picture():

    if "user" not in session:

        return redirect(
            url_for("home")
        )

    file = request.files.get(
        "profile_picture"
    )

    if not file or file.filename == "":

        flash(

            "No image selected!",

            "delete"
        )

        return redirect(
            url_for("dashboard")
        )

    filename = secure_filename(
        file.filename
    )

    email = session["user"]["email"]

    extension = filename.split(".")[-1]

    new_filename = (

        email.replace("@", "_")

        +

        "."

        +

        extension
    )

    filepath = os.path.join(

        PROFILE_PICTURE_FOLDER,

        new_filename
    )

    file.save(filepath)

    profiles = load_profiles()

    profiles[email][
        "profile_picture"
    ] = "/" + filepath.replace(
        "\\",
        "/"
    )

    save_profiles(profiles)

    flash(

        "Profile picture updated!",

        "success"
    )

    return redirect(
        url_for("dashboard")
    )

# ================= TOGGLE THEME =================

@app.route(
    "/toggle-theme",
    methods=["POST"]
)

def toggle_theme():

    if "user" not in session:

        return "", 401

    data = request.get_json()

    theme = data.get(
        "theme",
        "light"
    )

    profiles = load_profiles()

    email = session["user"]["email"]

    profiles[email][
        "theme"
    ] = theme

    save_profiles(profiles)

    return "", 204
# ================= RUN =================

if __name__ == "__main__":

    app.run(debug=True)

