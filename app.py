import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="templates")

# Configuration de la base PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://nmauser:nmapassword@postgres:5432/nma_transport')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modèles de base de données
class Vehicule(db.Model):
    __tablename__ = 'vehicules'
    id = db.Column(db.Integer, primary_key=True)
    immatriculation = db.Column(db.String(20), unique=True, nullable=False)
    modele = db.Column(db.String(50), nullable=False)

class Conducteur(db.Model):
    __tablename__ = 'conducteurs'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    numero_permis = db.Column(db.String(20), unique=True, nullable=False)

class Trajet(db.Model):
    __tablename__ = 'trajets'
    id = db.Column(db.Integer, primary_key=True)
    point_depart = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    date_trajet = db.Column(db.Date, nullable=False)
    conducteur_id = db.Column(db.Integer, db.ForeignKey('conducteurs.id'), nullable=False)
    vehicule_id = db.Column(db.Integer, db.ForeignKey('vehicules.id'), nullable=False)

# Création automatique des tables au démarrage
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/trajets')
def trajets():
    return render_template('trajets.html')

@app.route('/vehicules')
def vehicules():
    return render_template('vehicules.html')

@app.route('/conducteurs')
def conducteurs():
    return render_template('conducteurs.html')

# API pour récupérer et ajouter des conducteurs
@app.route('/api/conducteurs', methods=['GET', 'POST'])
def manage_conducteurs():
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'nom' not in data or 'numero_permis' not in data:
            return jsonify({"error": "Données invalides"}), 400

        nouveau_conducteur = Conducteur(
            nom=data['nom'],
            numero_permis=data['numero_permis']
        )
        db.session.add(nouveau_conducteur)
        db.session.commit()
        return jsonify({"message": "Conducteur ajouté"}), 201
    
    conducteurs = Conducteur.query.all()
    return jsonify([{ "id": c.id, "nom": c.nom, "numero_permis": c.numero_permis } for c in conducteurs])

# API pour récupérer et ajouter des véhicules
@app.route('/api/vehicules', methods=['GET', 'POST'])
def manage_vehicules():
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'immatriculation' not in data or 'modele' not in data:
            return jsonify({"error": "Données invalides"}), 400

        nouveau_vehicule = Vehicule(
            immatriculation=data['immatriculation'],
            modele=data['modele']
        )
        db.session.add(nouveau_vehicule)
        db.session.commit()
        return jsonify({"message": "Véhicule ajouté"}), 201
    
    vehicules = Vehicule.query.all()
    return jsonify([{ "id": v.id, "immatriculation": v.immatriculation, "modele": v.modele } for v in vehicules])

# API pour récupérer et ajouter des trajets
@app.route('/api/trajets', methods=['GET', 'POST'])
def manage_trajets():
    if request.method == 'POST':
        data = request.get_json()
        if not data or not all(k in data for k in ("point_depart", "destination", "date_trajet", "conducteur_id", "vehicule_id")):
            return jsonify({"error": "Données invalides"}), 400

        nouveau_trajet = Trajet(
            point_depart=data['point_depart'],
            destination=data['destination'],
            date_trajet=data['date_trajet'],
            conducteur_id=int(data['conducteur_id']),
            vehicule_id=int(data['vehicule_id'])
        )
        db.session.add(nouveau_trajet)
        db.session.commit()
        return jsonify({"message": "Trajet ajouté"}), 201
    
    trajets = Trajet.query.all()
    return jsonify([{ "id": t.id, "point_depart": t.point_depart, "destination": t.destination, "date_trajet": str(t.date_trajet), "conducteur_id": t.conducteur_id, "vehicule_id": t.vehicule_id } for t in trajets])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
