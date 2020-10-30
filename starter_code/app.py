#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
#
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
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
db.app = app
migrate=Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
  if type(value) is datetime.datetime:
    date=value
  else:
    date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html',
  latestvenues=db.session.query(Venue).order_by(desc(Venue.id)).limit(10).all(),
  latestartists=db.session.query(Artist).order_by(desc(Artist.id)).limit(10).all())


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venuesdata=Venue.query.all()
  cities=db.session.query(Venue.city,Venue.state).distinct().all()
  data=[]
  for i in cities:
    dic={}
    dic['city']=i[0]
    dic['state']=i[1]
    l=[]
    for x in venuesdata:
      if x.city.lower()==i[0].lower() and x.state.lower()==i[1].lower():
        m={}
        m['id']=x.id
        m['name']=x.name
        r=0
        for show in x.shows:
          if show.date.replace(tzinfo=tzutc())>datetime.datetime.now(tzutc()):
            r+=1
        m['num_upcoming_shows']=r
        l.append(m)
    dic['venues']=l
    data.append(dic)  
    
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  searchword=request.form.get("search_term")
  response={}
  response["count"]=0
  response["data"]= []
  for i in Venue.query.all():
    dic={}
    if searchword.lower() in i.name.lower():  
      response["count"]+=1
      dic['id']=i.id
      dic['name']=i.name
      r=0
      for show in i.shows:
        if show.date.replace(tzinfo=tzutc())>datetime.datetime.now(tzutc()):
          r+=1
      dic["num_upcoming_shows"]=r 
      response["data"].append(dic)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue=Venue.query.get(venue_id)
  past_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.date<datetime.datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.date>datetime.datetime.now()).all()
  data=venue.venue_to_dict()
  data['past_shows'] = past_shows
  data['past_shows_count'] = len(past_shows)

  data['upcoming_shows'] = upcoming_shows
  data['upcoming_shows_count'] = len(upcoming_shows)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      venue=Venue()
      venue.name = request.form.get('name')
      venue.city = request.form.get('city')
      venue.state = request.form.get('state')
      venue.address = request.form.get('address')
      if '-' not in request.form.get('phone'):
        venue.phone = request.form.get('phone')[:3]+'-'+request.form.get('phone')[3:6]+'-'+request.form.get('phone')[6:]
      else:
        venue.phone=request.form.get('phone')
      venue.image_link = request.form.get('image_link')
      venue.facebook_link = request.form.get('facebook_link')
      venue.website= request.form.get('website')
      venue.genres=request.form.getlist('genres')         
      if request.form.get('seeking_talent'):
        venue.seeking_talent= True
      else:
        venue.seeking_talent= False
      venue.seeking_description= request.form.get('seeking_description')
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form.get('name')+ ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form.get('name')+ ' could not be listed.')
    finally:
      db.session.close()  
  else:
    message = []
    for field, errors in form.errors.items():
        message.append(field + ':, '.join(errors))
    flash(f'Errors: {message}')
  return redirect(url_for('index'))
@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue deleted successfully.') 
  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be deleted.')
  finally:
    db.session.close()    
  return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  searchword=request.form.get("search_term")
  response={}
  response["count"]=0
  response["data"]= []
  for i in Artist.query.all():
    dic={}
    if searchword.lower() in i.name.lower():  
      response["count"]+=1
      dic['id']=i.id
      dic['name']=i.name
      r=0
      for show in i.shows:
        if show.date.replace(tzinfo=tzutc())>datetime.datetime.now(tzutc()):
          r+=1
      dic["num_upcoming_shows"]=r 
      response["data"].append(dic)    

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist=Artist.query.get(artist_id)
  past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.date<datetime.datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.date>datetime.datetime.now()).all()
  
  data=artist.artist_to_dict()
  
  data['past_shows'] = past_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows'] = upcoming_shows
  data['upcoming_shows_count'] = len(upcoming_shows)
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist=Artist.query.get(artist_id)
    artist.available_from=datetime.datetime.strptime(request.form.get('available_from'),'%Y-%m-%d %H:%M:%S')
    artist.available_to=datetime.datetime.strptime(request.form.get('available_to'),'%Y-%m-%d %H:%M:%S')
    artist.genres=request.form.getlist('genres')
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    if '-' not in request.form.get('phone'):
      artist.phone = request.form.get('phone')[:3]+'-'+request.form.get('phone')[3:6]+'-'+request.form.get('phone')[6:]
    else:
      artist.phone=request.form.get('phone')
    artist.image_link = request.form.get('image_link')
    artist.facebook_link = request.form.get('facebook_link')
    artist.website= request.form.get('website')
    artist.seeking_description= request.form.get('seeking_description')
    if request.form.get('seeking_venue'):
      artist.seeking_venue= True
    else:
      artist.seeking_venue= False
    db.session.commit()
    flash('Artist  was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist  could not be edited.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue=Venue.query.get(venue_id)
  form = VenueForm()
  # TODO: populate f
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue=Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    if '-' not in request.form.get('phone'):
      venue.phone = request.form.get('phone')[:3]+'-'+request.form.get('phone')[3:6]+'-'+request.form.get('phone')[6:]
    else:
      venue.phone=request.form.get('phone')
    venue.image_link = request.form.get('image_link')
    venue.facebook_link = request.form.get('facebook_link')
    venue.website= request.form.get('website')
    venue.genres=request.form.getlist('genres')         
    if request.form.get('seeking_talent'):
      venue.seeking_talent= True
    else:
      venue.seeking_talent= False
    venue.seeking_description= request.form.get('seeking_description')
    db.session.commit()
    flash('Venue  was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue  could not be edited.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    artist=Artist()
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.address=request.form.get('address')
    if '-' not in request.form.get('phone'):
      artist.phone = request.form.get('phone')[:3]+'-'+request.form.get('phone')[3:6]+'-'+request.form.get('phone')[6:]
    else:
      artist.phone=request.form.get('phone')
    artist.image_link = request.form.get('image_link')
    artist.facebook_link = request.form.get('facebook_link')
    artist.website= request.form.get('website')
    artist.genres=request.form.getlist('genres')
    if request.form.get('seeking_venue'):
      artist.seeking_venue = True
    else:
      venue.seeking_venuet= False
    artist.seeking_description= request.form.get('seeking_description')
    artist.available_from=request.form.get('available_from')
    artist.available_to=request.form.get('available_to')
    req=(request.form.get('address'),request.form.get('city'),request.form.get('state'))
    if  req in db.session.query(Artist.address,Artist.city,Artist.state).distinct().all():
     flash('This Artist already existed.')
     return render_template('forms/new_artist.html', form= ArtistForm())
    else: 
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form.get('name')+ ' was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form.get('name')+ ' could not be listed.')
  finally:
    db.session.close()

  return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():     
  return render_template('pages/shows.html', shows=Show.query.all())

@app.route('/shows/create',methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error=False
  artist=Artist.query.get(request.form.get('artist_id'))
  time=datetime.datetime.strptime(request.form.get('start_time'),'%Y-%m-%d %H:%M:%S')
  if  artist.available_to <time or time < artist.available_from:
    flash("The artist you specefied isn't available during this time.")
    return render_template('forms/new_show.html', form=ShowForm())
  else:
    try:
      dat=request.form.get('start_time')
      show=Show(date=dat,artist_id=request.form.get('artist_id'),venue_id=request.form.get('venue_id'))
      db.session.add(show)
      db.session.commit()
      flash('Show successfully listed.')
    except:
      error=True
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()  
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(405)
def invalid_method(error):
  return render_template('errors/405.html'), 405

@app.errorhandler(400)
def bad_request(error):
  return render_template('errors/400.html'), 400

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#


# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
