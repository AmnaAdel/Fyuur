import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, jsonify,redirect, url_for,abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
from sqlalchemy import desc
from dateutil.tz import tzutc
import os

db = SQLAlchemy()


    
    

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(),nullable=False)
    
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String())
    
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website=db.Column(db.String(300))
    
    genres = db.Column(db.ARRAY(db.String()),nullable=False)
    
    seeking_talent = db.Column(db.Boolean,default=False,nullable=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show',backref='venue',lazy=True)
    
    def venue_to_dict(self):
      venue={}
      venue['id']=self.id
      venue['name']=self.name
      venue['city']=self.city
      venue['state']=self.state
      venue['address']=self.address
      venue['phone']=self.phone
      venue['image_link']=self.image_link
      venue['facebook_link']=self.facebook_link
      venue['website']=self.image_link
      venue['genres']=self.genres
      venue['seeking_talent']=self.seeking_talent
      venue['seeking_description']=self.seeking_description
      return venue

    def __repr__(self):
        return f'<Venue {self.id} {self.name} >'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(),nullable=False)
    
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String())
    
    genres = db.Column(db.ARRAY(db.String()),nullable=False)
    
    image_link = db.Column(db.String(500))
    website=db.Column(db.String(300))
    facebook_link = db.Column(db.String(120))
    
    seeking_venue = db.Column(db.Boolean,default=False,nullable=False)
    seeking_description = db.Column(db.String())
    
    available_from=db.Column(db.DateTime, nullable=False)
    available_to=db.Column(db.DateTime, nullable=False)
    shows = db.relationship('Show',backref='artist',lazy=True)
    
    def artist_to_dict(self):
      venue={}
      venue['id']=self.id
      venue['name']=self.name
      venue['city']=self.city
      venue['state']=self.state
      venue['address']=self.address
      venue['phone']=self.phone
      venue['image_link']=self.image_link
      venue['facebook_link']=self.facebook_link
      venue['website']=self.image_link
      venue['genres']=self.genres
      venue['seeking_venue']=self.seeking_venue
      venue['seeking_description']=self.seeking_description
      return venue
    
    
    def __repr__(self):
        return f'<Artist {self.id} {self.name} >'

class Show(db.Model):
  __tablename__ ='show'
  id = db.Column(db.Integer, primary_key=True)
  
  artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'),nullable=False)
  venue_id = db.Column(db.Integer,db.ForeignKey('venue.id'),nullable=False)
  
  date = db.Column(db.DateTime,default=datetime.datetime.today(), nullable=False)
  
  def show_venue(self):
      show={}
      show['date']=self.date
      show['venue_id']=self.venue.id
      show['venue_name']=self.venue.name
      show['venue_city']=self.venue.city
      show['venue_state']=self.venue.state
      show['venue_address']=self.venue.address
      show['venue_phone']=self.venue.phone
      show['venue_image_link']=self.venue.image_link
      return show
  
  def show_artist(self):
      show={}
      show['date']=self.date
      show['artist_id']=self.artist.id
      show['artist_name']=self.artist.name
      show['artist_city']=self.artist.city
      show['artist_state']=self.artist.state
      show['artist_address']=self.artist.address
      show['artist_phone']=self.artist.phone
      show['artist_image_link']=self.artist.image_link
      return show
  def __repr__(self):
      return f'<Show {self.id} {self.date} >'