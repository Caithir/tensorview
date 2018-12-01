from werkzeug.routing import BaseConverter
from db import Query


class QueryConverter(BaseConverter):

    def to_python(self, value):
        return [self.query_gen_with_string_comp(*query.split(">.<")) for query in value.split("|")]

    def to_url(self, values):
        return '|'.join(values)

    def query_gen_with_string_comp(self, param, comp, value):
        string_comps = ['contains', "startsWith", "endsWith", "exact"]
        if comp in string_comps:
            if comp == 'contains':
                value = f'\"%{value}%\" '
            if comp == 'startsWith':
                value = f'\"{value}%\"'
            if comp == 'endsWith':
                value = f'\"%{value}\"'
            comp = 'LIKE'
        return Query(param, comp, value)
