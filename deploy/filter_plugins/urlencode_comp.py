from urllib.parse import quote


class FilterModule(object):
    '''
    custom jinja2 filters for working with collections
    '''

    def filters(self):
        return {
            'urlencode_comp': self.urlencode_comp
        }

    @staticmethod
    def urlencode_comp(comp):
        return quote(comp, safe='')
