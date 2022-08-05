from flask import Blueprint, render_template

from collections import defaultdict
import enum
from hashlib import new
import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import or_
from forms import *
from flask_migrate import Migrate
from datetime import datetime

from app import *


shows = Blueprint("shows", __name__,
                  static_folder="/static", template_folder="/templates")


class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)


#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows

    response = []
    allShows = Show.query.all()
    # print("All Shows", allShows)

    for show in allShows:
        artist = Artist.query.with_entities(
            Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).first()
        venue = Venue.query.with_entities(Venue.name).filter(
            Venue.id == show.venue_id).first()
        tmp = {
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        }
        response.append(tmp)
    return render_template('pages/shows.html', shows=response)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form

    is_successful = True

    try:
        # print('Date   ', format_datetime(request.form['start_time']))
        newShow = Show(
            venue_id=request.form['venue_id'],
            artist_id=request.form['artist_id'],
            start_time=request.form['start_time'])
        db.session.add(newShow)
        db.session.commit()

    except:
        db.session.rollback()
        print(sys.exc_info())
        is_successful = False
    finally:
        db.session.close()

    # on successful db insert, flash success
    if is_successful:
        flash('Show was successfully listed!')
    else:
        flash('An error occurred. Show could not be listed.')
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')
