from django.db.models import Manager
import datetime


class PublicManager(Manager):
    """Returns published posts that are not in the future."""
    def __init__(self, *args, **kwargs):
        self.filter_dict = dict(status__gte=2)
        super(PublicManager, self).__init__(*args, **kwargs)
    
    def published(self):
        return self.get_query_set().filter(**self.filter_dict).exclude(publish__gt=datetime.datetime.now())
