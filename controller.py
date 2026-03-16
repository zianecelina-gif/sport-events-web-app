from flask import Flask, render_template, request, redirect, url_for, session, flash
from model import DB
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = b'c1dcc1cc06d7cb4e0fd4a03b45a4f33135b9346736edf2f2'
app.template_folder = 'view'


# ─── Helpers ─────────────────────────────────────────────────────────

def convert_json_to_string(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return [f"{item['nom_voie']}, {item['nom_commune']}, {item['code_postal']}" for item in data]


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id' not in session:
            flash("Veuillez vous connecter pour accéder à cette ressource", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ─── Public Routes ───────────────────────────────────────────────────

@app.route('/')
def home():
    stats = {
        'users': DB.count_users(),
        'events': DB.count_events(),
        'participations': DB.count_total_participations()
    }
    return render_template('homePage.html', stats=stats)


@app.get('/login')
def login():
    return render_template('logInPage.html')


@app.post('/login')
def do_login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    if not username or not password:
        flash("Veuillez remplir tous les champs", "error")
        return redirect(url_for('login'))
    user_id = DB.login(username, password)
    if user_id != -1:
        user = DB.get_user_by_id(user_id)
        session['id'] = user_id
        session['username'] = username
        session['firstName'] = user['first_name']
        flash(f"Bienvenue, {user['first_name']} !", "success")
        return redirect(url_for('home'))
    else:
        flash("Identifiants incorrects, veuillez réessayer", "error")
        return redirect(url_for('login'))


@app.get('/signup')
def signup():
    return render_template('signUpPage.html')


@app.post('/signup')
def do_signup():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    confirmation = request.form.get('confirmationPassword', '')
    first_name = request.form.get('firstName', '').strip()
    family_name = request.form.get('familyName', '').strip()
    age = request.form.get('age', '')
    gender = request.form.get('gender', '')
    bio = request.form.get('bio', '').strip()

    if not all([username, password, confirmation, first_name, family_name, age, gender]):
        flash("Veuillez remplir tous les champs obligatoires", "error")
        return redirect(url_for('signup'))

    if not DB.verify_username_available(username):
        flash("Ce nom d'utilisateur est déjà pris", "error")
        return redirect(url_for('signup'))

    if password != confirmation:
        flash("Les mots de passe ne correspondent pas", "error")
        return redirect(url_for('signup'))

    user_id = DB.signup(username, password, first_name, family_name, age, gender, bio)
    session['id'] = user_id
    session['username'] = username
    session['firstName'] = first_name
    flash(f"Bienvenue sur Kalos, {first_name} !", "success")
    return redirect(url_for('home'))


@app.post('/logout')
def logout():
    session.clear()
    flash("Vous avez été déconnecté", "success")
    return redirect(url_for('home'))


# ─── Event Routes ────────────────────────────────────────────────────

@app.get('/events')
@login_required
def list_events():
    events = DB.list_events()
    # Attach participation count to each event
    for event in events:
        event['current_count'] = DB.count_participations_by_event(event['id'])
    return render_template('eventPage.html', events=events)


@app.get('/filteredEvents')
@login_required
def filter_events():
    activity = request.args.get('activite', '/')
    if activity == '/':
        events = DB.list_events()
    else:
        events = DB.list_events_by_activity(activity)
    for event in events:
        event['current_count'] = DB.count_participations_by_event(event['id'])
    return render_template('eventPage.html', events=events)


@app.get('/eventCreation')
@login_required
def create_event_page():
    locations = convert_json_to_string('adresses.json')
    return render_template('createEventPage.html', locations=locations)


@app.post('/createEvent')
@login_required
def do_create_event():
    name = request.form.get('event-name', '').strip()
    description = request.form.get('event-description', '').strip()
    date = request.form.get('event-date', '')
    activity = request.form.get('event-activity', '')
    location = request.form.get('event-location', '').strip()
    headcount = request.form.get('event-headcount', '')

    if not all([name, description, date, activity, location, headcount]):
        flash("Veuillez remplir tous les champs", "error")
        return redirect(url_for('create_event_page'))

    activity_id = DB.get_activity_id(activity)
    if activity_id is None:
        flash("Activité invalide", "error")
        return redirect(url_for('create_event_page'))

    owner_id = session['id']
    event_id = DB.create_event(name, description, date, location, headcount, activity, activity_id, owner_id)
    DB.register_user_to_event(session['id'], event_id)
    flash(f"Événement « {name} » créé avec succès !", "success")
    return redirect(url_for('list_events'))


@app.get('/eventDetails/<int:event_id>')
@login_required
def event_details(event_id):
    event = DB.get_event_by_id(event_id)
    if not event:
        flash("Événement introuvable", "error")
        return redirect(url_for('list_events'))
    user_is_registered = DB.is_user_registered(session['id'], event_id)
    current_headcount = DB.count_participations_by_event(event_id)
    participations = DB.list_participations_by_event(event_id)
    members = [DB.get_user_by_id(p['user_id']) for p in participations]
    user_is_owner = session['id'] == event['owner_id']
    return render_template('read.html',
                           event=event,
                           user_is_registered=user_is_registered,
                           current_headcount=current_headcount,
                           members=members,
                           user_is_owner=user_is_owner)


@app.post('/eventDetails/<int:event_id>')
@login_required
def participate(event_id):
    headcount = DB.get_event_headcount(event_id)
    current = DB.count_participations_by_event(event_id)
    if current >= headcount:
        flash("L'événement est complet", "warning")
    else:
        DB.register_user_to_event(session['id'], event_id)
        flash("Vous êtes inscrit !", "success")
    return redirect(url_for('event_details', event_id=event_id))


@app.post('/eventDetails/<int:event_id>/unregister')
@login_required
def unregister(event_id):
    DB.cancel_user_registration(session['id'], event_id)
    flash("Participation annulée", "success")
    return redirect(url_for('event_details', event_id=event_id))


@app.get('/profile/<int:user_id>')
@login_required
def show_profile(user_id):
    user_id = session['id']
    user = DB.get_user_by_id(user_id)
    if not user:
        flash("Utilisateur introuvable", "error")
        return redirect(url_for('home'))
    participations = DB.list_participations_by_user(user_id)
    events = [DB.get_event_by_id(p['event_id']) for p in participations]
    events = [e for e in events if e is not None]
    events_count = len(events)
    participation_count = DB.count_participations_by_user(user_id)
    return render_template('profilePage.html',
                           user=user,
                           events=events,
                           events_count=events_count,
                           participation_count=participation_count)


@app.post('/eventDetails/<int:event_id>/delete')
@login_required
def delete_event(event_id):
    event = DB.get_event_by_id(event_id)
    if event and event['owner_id'] == session['id']:
        DB.delete_event(event_id)
        flash("Événement supprimé", "success")
    else:
        flash("Vous n'êtes pas autorisé à supprimer cet événement", "error")
    return redirect(url_for('show_profile', user_id=session['id']))


# ─── Error Handlers ──────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template('homePage.html', stats={
        'users': DB.count_users(),
        'events': DB.count_events(),
        'participations': DB.count_total_participations()
    }), 404


# ─── Run ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(port=5000, debug=True)
