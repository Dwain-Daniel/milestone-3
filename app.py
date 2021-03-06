import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    recipes = list(mongo.db.recipes.find().sort("category", 1))
    return render_template("recipes.html", recipes=recipes)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    return render_template("recipes.html", recipes=recipes)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username is already in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            if check_password_hash(existing_user["password"], 
            request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))
        else:
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    if session["user"]:
        return render_template("profile.html", username=username)
    return redirect(url_for("login"))
       

@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.clear()
    return redirect(url_for("login"))


@app.route("/submit_recipe", methods=["GET", "POST"])
def submit_recipe():
    if session.get("user"):
        if request.method == "POST":
            recipe = {
                "category": request.form.get("category"),
                "recipe_name": request.form.get("recipe_name"),
                "description": request.form.get("description"),
                "serving_size": request.form.get("serving_size"),
                "preparation_time": request.form.get("preparation_time"),
                "cooking_time": request.form.get("cooking_time"),
                "ingredients": request.form.get("ingredients"),
                "instructions": request.form.get("instructions"),
                "username": session["user"]
            }
            mongo.db.recipes.insert_one(recipe)
            flash("Recipe Successfully Submitted!")
            return redirect(url_for("get_recipes"))

        categories = mongo.db.categories.find()
        return render_template("submit_recipe.html", categories=categories)
    flash("You are not logged in so cannot add recipe, please log in.")
    return redirect(url_for("login"))


@app.route("/edit_recipe<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    if session.get("user"):
        if request.method == "POST":
            submit = {
                "category": request.form.get("category"),
                "recipe_name": request.form.get("recipe_name"),
                "description": request.form.get("description"),
                "serving_size": request.form.get("serving_size"),
                "preparation_time": request.form.get("preparation_time"),
                "cooking_time": request.form.get("cooking_time"),
                "ingredients": request.form.get("ingredients"),
                "instructions": request.form.get("instructions"),
                "username": session["user"]
            }
            mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, submit)
            flash("Recipe Successfully Updated!")

        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
        categories = mongo.db.categories.find()
        return render_template("edit_recipe.html", recipe=recipe, categories=categories)
    flash("You are not logged in so cannot add recipe, please log in.")
    return redirect(url_for("login"))
    

@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    if session.get("user"):
        mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
        flash("Recipe Deleted")
        return redirect(url_for("get_recipes"))
    flash("You are not logged in so cannot delete recipes, please log in.")
    return redirect(url_for("login"))


@app.route("/contact")
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
