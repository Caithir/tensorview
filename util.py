from werkzeug.routing import BaseConverter
from db import Query
from urllib.parse import unquote
class QueryConverter(BaseConverter):

    def to_python(self, value):
        return [Query(*query.split(">.<")) for query in value.split("|")]

    def to_url(self, values):
        return '|'.join(values)
