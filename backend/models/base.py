from datetime import datetime
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from sqlalchemy import create_engine
import os

# plutôt que de l'instancier à chaque fois, nous le faisons ici et l'importons dans les modèles ORM
Base = declarative_base()


class BaseModelMixin:
	"""
	Les mixins sont une exception à l'héritage multiple : il s'agit d'un héritage partiel (et donc un peu multiple) qui va se mélanger (se mix in) avec l'autre classe héritée
	Mixin fournissant des méthodes pratiques pour les modèles ORM :
	- Classe Base déclarative
	- Accès dictionnaire via __getitem__ et __contains__ (assure la rétrocompatibilité
	  avec les templates Jinja utilisant movie['title'] ainsi que movie.title)
	- Méthode to_dict() pour sérialisation
	"""

	def __getitem__(self, item):
		if hasattr(self, item):
			return getattr(self, item)
		raise KeyError(f"L'objet '{self.__class__.__name__}' n'a pas l'attribut '{item}'")

	def to_dict(self):
		"""retourne les colonnes de l'objet sous forme de dictionnaire"""
		result = {}
		for col in self.__table__.columns:
			val = getattr(self, col.name)
			if isinstance(val, datetime):
				val = val.strftime("%Y-%m-%d %H:%M:%S")
			result[col.name] = val
		return result


def get_engine(db_uri=None):
	"""crée et retourne un moteur SQLAlchemy
	le chemin de la BDD db_uri est app/movies.db par défaut"""
	if db_uri is None:
		base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		db_path = os.path.join(base_dir, 'movies.db') # app/movies.db donc
		db_uri = f"sqlite:///{db_path}"
	return create_engine(db_uri, echo=False)

