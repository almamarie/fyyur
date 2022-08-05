
from app import db

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    def __repr__(self):
        return f'<Venue {self.id} {self.city}  {self.state}>'

    # my tables
    genres = db.Column(db.String())
    website_link = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())

    artists = db.relationship(
        'Artist', secondary='show', backref=db.backref('artist', lazy=True))


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # my tables
    website_link = db.Column(db.String())
    seeking_venue = db.Column(db.String())
    seeking_description = db.Column(db.String())


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
