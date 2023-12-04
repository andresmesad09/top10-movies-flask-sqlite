from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from dotenv import load_dotenv
import os

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# app config
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
Bootstrap5(app)
# initialize the app with the extension
db.init_app(app)

MOVIE_API_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DETAILS_URL = "https://api.themoviedb.org/3/movie/"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
load_dotenv(override=True)


def get_movies(movie_title):
    try:
        # print(f"Bearer {os.environ.get('MOVIE_API_TOKEN')}")
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {os.environ.get('MOVIE_API_TOKEN')}"
        }
        response = requests.get(
            url=MOVIE_API_URL,
            params={
                "query": movie_title,
                "page": 1,
                "language": "en-US",
                "include_adult": "false"
            },
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        movies_detail = result["results"]
        return movies_detail
    except Exception as e:
        print(e)
        # TODO: Notify users about error during search
        return render_template(url_for('home'))


def get_movie_details(movie_id):
    try:
        # print(f"Bearer {os.environ.get('MOVIE_API_TOKEN')}")
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {os.environ.get('MOVIE_API_TOKEN')}"
        }
        response = requests.get(
            url=f"{MOVIE_DETAILS_URL}/{movie_id}",
            params={
                "language": "en-US",
            },
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        return result
    except Exception as e:
        print(e)
        # TODO: Notify users about error during search
        return render_template(url_for('home'))


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), unique=True, nullable=True)
    img_url = db.Column(db.String(250), unique=True, nullable=False)

    def __repr__(self):
        return f'<Movie {self.title}>'


class UpdateForm(FlaskForm):
    rating = StringField(label="Your rating out of 10", validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField("Update")


class AddForm(FlaskForm):
    title = StringField(label="Movie title", validators=[DataRequired()])
    add_movie = SubmitField("Add movie")


# Create table schema in the database after defining the models
with app.app_context():
    db.create_all()


@app.route("/home")
@app.route("/")
def home():
    all_movies = (db
                  .session.execute(db.Select(Movies).order_by(Movies.ranking.desc()))
                  .scalars()
                  .fetchall()
                  )
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/update/<int:movie_id>", methods=['GET', 'POST'])
def update(movie_id):
    form = UpdateForm()
    movie_to_update = db.get_or_404(Movies, movie_id)
    if request.method == "POST":
        movie_to_update.rating = form.rating.data
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form, movie=movie_to_update)


@app.route("/delete/<int:movie_id>")
def delete(movie_id):
    movie_to_delete = db.get_or_404(Movies, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=['GET', 'POST'])
def add_movie():
    form = AddForm()
    if request.method == 'POST':
        title = form.title.data
        result_movies = get_movies(movie_title=title)
        return render_template('select.html', movies=result_movies)
    return render_template("add.html", form=form)


@app.route("/insert_movie/<int:movie_id>")
def insert_movie(movie_id):
    movie_details = get_movie_details(movie_id=movie_id)
    new_movie = Movies(
        title=movie_details["title"],
        year=movie_details["release_date"].split("-")[0],
        img_url=f"{MOVIE_DB_IMAGE_URL}{movie_details['poster_path']}",
        description=movie_details["overview"]
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('update', movie_id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
