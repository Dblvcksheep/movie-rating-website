from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

url = "https://api.themoviedb.org/3/search/movie"


access_token = "Bearer Put-your-access-token-here"

headers ={
    "accept": "application/json",
    "Authorization": access_token
}

class EditForm(FlaskForm):
    rating = StringField('Rating', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ADDForm(FlaskForm):
    movie_field = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Submit')


class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] ="sqlite:///movie-collection.db"
db.init_app(app)

class new_movie(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer,unique=False, nullable=True)
    description: Mapped[str] = mapped_column(unique=False, nullable=True)
    rating: Mapped[int] = mapped_column(Integer, unique=False, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, unique=False, nullable=True)
    review: Mapped[str] = mapped_column( unique=False, nullable=True)
    image_url: Mapped[str] = mapped_column(unique=False, nullable=True)


with app.app_context():
    db.create_all()


app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)




@app.route("/")
def home():
    result = db.session.execute(db.select(new_movie).order_by(new_movie.rating.desc()))
    movies = result.scalars().all()
    for n in range (len(movies)):
        movies[n].ranking = n+1
    db.session.commit()
    return render_template("index.html", movies=movies)

@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = EditForm()

    if form.validate_on_submit():
        movie_id = request.args.get("id")
        movie_to_edit = db.get_or_404(new_movie,movie_id)
        movie_to_edit.rating = form.rating.data
        movie_to_edit.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("edit.html", form=form)

@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = db.get_or_404(new_movie, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()

    return redirect(url_for("home"))

@app.route("/add", methods=["GET", "POST"])
def add():
    form = ADDForm()

    if form.validate_on_submit():
        movie_name = form.movie_field.data
        params = {
            "query": movie_name,

        }

        response = requests.get(url, params, headers=headers)
        data = response.json()


        return render_template("select.html", movie_list=data["results"])

    movie_id = request.args.get("movie_id")

    if movie_id:
        find_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        response = requests.get(find_url, headers=headers)
        data = response.json()

        with app.app_context():
            new = new_movie(title=data["title"], year=data["release_date"],
                            description=data['overview'],
                            image_url=f"https://image.tmdb.org/t/p/w500/{data['poster_path']}")
            db.session.add(new)
            db.session.commit()
            return redirect(url_for("edit", id=new.id))
    return render_template("add.html", form=form)



if __name__ == '__main__':
    app.run(debug=True)
