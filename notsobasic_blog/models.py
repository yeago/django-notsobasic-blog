from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.db.models import permalink
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch

from tagging.fields import TagField

from notsobasic_blog.managers import PublicManager
from notsobasic_blog.helpers.fix_unicode import fix_unicode

import tagging

class Section(models.Model):
	name = models.CharField(max_length=30)
	date_based = models.BooleanField(default=True)
        slug = models.SlugField(_('slug'), unique=True)
	class Meta:
		verbose_name = _('section')
		verbose_name_plural = _('sections')
		db_table = 'blog_sections'
		ordering = ('name',)
	def __unicode__(self):
		return u'%s' % self.name

class Category(models.Model):
    """Category model."""
    title       = models.CharField(_('title'), max_length=100)
    description = models.TextField(null=True,blank=True)
    slug        = models.SlugField(_('slug'), unique=True)
    section	    = models.ManyToManyField(Section,null=True,blank=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        db_table = 'blog_categories'
        ordering = ('title',)

    def __unicode__(self):
        return u'%s' % self.title

    @permalink
    def get_absolute_url(self):
        return ('blog_category_detail', None, {'slug': self.slug})


class Post(models.Model):
    """Post model."""
    STATUS_CHOICES = (
        (1, _('Draft')),
        (2, _('Public')),
        (3, _('Removed')),
    )
    title           = models.CharField(_('title'), max_length=100)
    slug            = models.SlugField(_('slug'), unique_for_date='publish',max_length=200)
    author          = models.ForeignKey(User, blank=True, null=True)
    body            = models.TextField(_('body'),help_text="Special non-web characters (like &#8222; &#8216; &#8225; etc) will be stripped. <a target='_new' href='http://home.earthlink.net/~awinkelried/keyboard_shortcuts.html'>Use HTML number codes instead (click here)</a>")
    tease           = models.TextField(_('tease'), blank=True)
    image           = models.CharField(max_length=200,null=True,blank=True)
    status          = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=2)
    allow_comments  = models.BooleanField(_('allow comments'), default=True)
    publish         = models.DateTimeField(_('publish'))
    created         = models.DateTimeField(_('created'), auto_now_add=True)
    modified        = models.DateTimeField(_('modified'), auto_now=True)
    categories      = models.ManyToManyField(Category, blank=True)
    section	    = models.ManyToManyField(Section, blank=True)
    followup_to     = models.ForeignKey('Post',null=True,blank=True,related_name="followup_set",help_text="If this is in a series of posts and you want to link them, select the previous post in the series here")
    tags            = TagField()
    objects         = PublicManager()

    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')
        db_table  = 'blog_posts'
        ordering  = ('-publish',)
        get_latest_by = 'publish'

    class Admin:
        list_display  = ('title', 'publish', 'status')
        list_filter   = ('publish', 'categories', 'status')
        search_fields = ('title', 'body')

    def save(self,*args,**kwargs):
	 super(Post,self).save(*args,**kwargs)

    def image_tag(self):
         if self.image:
               return mark_safe('<img src="%s%s" />' % (settings.MEDIA_URL,self.image))
         return False

    def __unicode__(self):
        return u'%s' % self.title

    @permalink
    def get_absolute_url(self):
	section = None
	try:
		section = self.section.all()[0]
		if section.date_based:
			return ('blog_detail', None, {
			    'section' : section.name.lower(),
			    'year': self.publish.year,
			    'month': self.publish.strftime('%b').lower(),
			    'day': self.publish.day,
			    'slug': self.slug
			})
		return ('blog_detail_nodate', None, {
		    'section' : section.name.lower(),
		    'slug': self.slug
		})

	except:
		return ('blog_detail_nodate',None,{'slug': self.slug})
		#kwargs = {'year': self.publish.year,
		#    'month': self.publish.strftime('%b').lower(),
		#    'day': self.publish.day,
		#    'slug': self.slug,  }
		#return reverse('blog_detail',kwargs=kwargs)

    
    def get_previous_post(self):
        return self.get_previous_by_publish(status__gte=2)
    
    def get_next_post(self):
        return self.get_next_by_publish(status__gte=2)
