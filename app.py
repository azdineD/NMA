from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="templates")

# Configuration de la base PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://nma_user:nmapassword@localhost/nma_transport'
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

# 📌 Routes pour afficher les pages HTML
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

# 📌 API pour récupérer et ajouter des trajets
@app.route('/api/trajets', methods=['GET'])
def get_trajets():
    trajets = Trajet.query.join(Conducteur, Trajet.conducteur_id == Conducteur.id)\
                          .join(Vehicule, Trajet.vehicule_id == Vehicule.id)\
                          .add_columns(
                              Trajet.id, Trajet.point_depart, Trajet.destination, Trajet.date_trajet,
                              Conducteur.nom.label("conducteur_nom"),
                              Vehicule.modele.label("vehicule_modele")
                          ).all()
    
    return jsonify([{
        "id": t.id,
        "point_depart": t.point_depart,
        "destination": t.destination,
        "date_trajet": str(t.date_trajet),
        "conducteur": t.conducteur_nom,
        "vehicule": t.vehicule_modele
    } for t in trajets])
@app.route('/api/trajets', methods=['POST'])
def add_trajet():
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

    try:
        db.session.add(nouveau_trajet)
        db.session.commit()
        return jsonify({"message": "Trajet ajouté"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur lors de l'ajout du trajet : {str(e)}"}), 500

@app.route('/api/trajets/<int:id>', methods=['DELETE'])
def delete_trajet(id):
    trajet = Trajet.query.get(id)
    if trajet:
        db.session.delete(trajet)
        db.session.commit()
        return jsonify({"message": "Trajet supprimé"}), 200
    else:
        return jsonify({"error": "Trajet non trouvé"}), 404
@app.route('/api/trajets/<int:id>', methods=['PUT'])
def update_trajet(id):
    trajet = Trajet.query.get(id)
    if trajet:
        data = request.get_json()
        trajet.point_depart = data['point_depart']
        trajet.destination = data['destination']
        trajet.date_trajet = data['date_trajet']
        trajet.conducteur_id = data['conducteur_id']
        trajet.vehicule_id = data['vehicule_id']
        db.session.commit()
        return jsonify({"message": "Trajet modifié"}), 200
    else:
        return jsonify({"error": "Trajet non trouvé"}), 404

# 📌 API pour récupérer et ajouter des véhicules
@app.route('/api/vehicules', methods=['GET'])
def get_vehicules():
    vehicules = Vehicule.query.all()
    return jsonify([{
        "id": v.id,
        "immatriculation": v.immatriculation,
        "modele": v.modele
    } for v in vehicules])

@app.route('/api/vehicules', methods=['POST'])
def add_vehicule():
    data = request.get_json()
    nouveau_vehicule = Vehicule(
        immatriculation=data['immatriculation'],
        modele=data['modele']
    )
    db.session.add(nouveau_vehicule)
    db.session.commit()
    return jsonify({"message": "Véhicule ajouté"}), 201

# 📌 API pour récupérer et ajouter des conducteurs
@app.route('/api/conducteurs', methods=['GET'])
def get_conducteurs():
    conducteurs = Conducteur.query.all()
    return jsonify([{
        "id": c.id,
        "nom": c.nom,
        "numero_permis": c.numero_permis
    } for c in conducteurs])

@app.route('/api/conducteurs', methods=['POST'])
def add_conducteur():
    data = request.get_json()
    nouveau_conducteur = Conducteur(
        nom=data['nom'],
        numero_permis=data['numero_permis']
    )
    db.session.add(nouveau_conducteur)
    db.session.commit()
    return jsonify({"message": "Conducteur ajouté"}), 201

# 📌 Démarrer Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
