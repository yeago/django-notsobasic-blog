from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, TemplateDoesNotExist 
from django.http import Http404
from django.views.generic import date_based, list_detail
from notsobasic_blog.models import *

import datetime
import re

template_folder_list = ['blog']

def post_list(request,section=None,page=0):
	if not section:
		queryset = Post.objects.published()
		if request.user.is_superuser:
			queryset = Post.objects.all()
	else:
		section = get_object_or_404(Section,name=section)
		template_folder_list.append(section.slug)
		queryset = Post.objects.published().filter(section=section)
		if request.user.is_superuser:
			queryset = Post.objects.filter(section=section)

	template_folder_list.reverse()
	for template_folder in template_folder_list:
		try:
			return list_detail.object_list(
				request,
				template_name = '%s/post_list.html' % template_folder,
				queryset = queryset,
				paginate_by = 20,
				page = page,
				extra_context = {'section': section },
			)
		except TemplateDoesNotExist:
			continue	

post_list.__doc__ = list_detail.object_list.__doc__


def post_archive_year(request, year):
	return date_based.archive_year(
		 request,
		 year = year,
		 date_field = 'publish',
		 queryset = Post.objects.published(),
		 make_object_list = True,
	)
post_archive_year.__doc__ = date_based.archive_year.__doc__


def post_archive_month(request, year, month):
	return date_based.archive_month(
		 request,
		 year = year,
		 month = month,
		 date_field = 'publish',
		 queryset = Post.objects.published(),
	)
post_archive_month.__doc__ = date_based.archive_month.__doc__


def post_archive_day(request, year, month, day):
	return date_based.archive_day(
		 request,
		 year = year,
		 month = month,
		 day = day,
		 date_field = 'publish',
		 queryset = Post.objects.published(),
	)
post_archive_day.__doc__ = date_based.archive_day.__doc__

def post_detail_nodate(request,slug,section=None):
	return post_detail(request,slug,section=section)

def post_detail(request, slug, year=None, month=None, day=None, section=None):
	template_list = ["blog/post_detail.html"]
	if section:
		template_list = ["%s/post_detail.html" % (section.lower())] + template_list

	queryset = Post.objects.published()

	if request.user.has_perm('notsobasic_blog.change_post'):
		queryset = Post.objects.all()

	if year:
		for template_name in template_list:
			try:
				return date_based.object_detail(
					 request,
					 template_name = template_name,
					 year = year,
					 month = month,
					 day = day,
					 date_field = 'publish',
					 slug = slug,
					 queryset = queryset
				)
			except TemplateDoesNotExist:
				continue
	for template_name in template_list:
		try:
			return list_detail.object_detail(
				 request,
				 template_name = template_name,
				 slug = slug,
				 queryset = queryset
			)
		except TemplateDoesNotExist:
			continue

	get_template(template_list[0])

post_detail.__doc__ = date_based.object_detail.__doc__


def category_list(request,section=None):
	"""
	Category list

	Template: ``blog/category_list.html``
	Context:
		 object_list
				List of categories.
	"""
	queryset = Category.objects.all()
	if section:
		queryset = Category.objects.filter(section__slug=section)

	return list_detail.object_list(
		 request,
		 queryset = queryset,
		 template_name = 'blog/category_list.html',
	)

def category_detail(request, slug, section=None):
	template_folder_list = ['blog']
	"""
	Category detail

	Template: ``blog/category_detail.html``
	Context:
		 object_list
				List of posts specific to the given category.
		 category
				Given category.
	"""
	if section:
		section = get_object_or_404(Section,slug=section)
		template_folder_list.append(section.slug)
		category = get_object_or_404(Category, slug__iexact=slug,section=section)
	else:
		category = get_object_or_404(Category, slug__iexact=slug)

	template_folder_list.reverse()
	for template_folder in template_folder_list:
		try:
			return list_detail.object_list(
				 request,
				 queryset = category.post_set.published(),
				 extra_context = {'category': category, 'section': section},
				 template_name = '%s/category_detail.html' % template_folder,
			)
		except TemplateDoesNotExist:
			continue

# Stop Words courtesy of http://www.dcs.gla.ac.uk/idom/ir_resources/linguistic_utils/stop_words
STOP_WORDS = r"""\b(a|about|above|across|after|afterwards|again|against|all|almost|alone|along|already|also|
although|always|am|among|amongst|amoungst|amount|an|and|another|any|anyhow|anyone|anything|anyway|anywhere|are|
around|as|at|back|be|became|because|become|becomes|becoming|been|before|beforehand|behind|being|below|beside|
besides|between|beyond|bill|both|bottom|but|by|call|can|cannot|cant|co|computer|con|could|couldnt|cry|de|describe|
detail|do|done|down|due|during|each|eg|eight|either|eleven|else|elsewhere|empty|enough|etc|even|ever|every|everyone|
everything|everywhere|except|few|fifteen|fify|fill|find|fire|first|five|for|former|formerly|forty|found|four|from|
front|full|further|get|give|go|had|has|hasnt|have|he|hence|her|here|hereafter|hereby|herein|hereupon|hers|herself|
him|himself|his|how|however|hundred|i|ie|if|in|inc|indeed|interest|into|is|it|its|itself|keep|last|latter|latterly|
least|less|ltd|made|many|may|me|meanwhile|might|mill|mine|more|moreover|most|mostly|move|much|must|my|myself|name|
namely|neither|never|nevertheless|next|nine|no|nobody|none|noone|nor|not|nothing|now|nowhere|of|off|often|on|once|
one|only|onto|or|other|others|otherwise|our|ours|ourselves|out|over|own|part|per|perhaps|please|put|rather|re|same|
see|seem|seemed|seeming|seems|serious|several|she|should|show|side|since|sincere|six|sixty|so|some|somehow|someone|
something|sometime|sometimes|somewhere|still|such|system|take|ten|than|that|the|their|them|themselves|then|thence|
there|thereafter|thereby|therefore|therein|thereupon|these|they|thick|thin|third|this|those|though|three|through|
throughout|thru|thus|to|together|too|top|toward|towards|twelve|twenty|two|un|under|until|up|upon|us|very|via|was|
we|well|were|what|whatever|when|whence|whenever|where|whereafter|whereas|whereby|wherein|whereupon|wherever|whether|
which|while|whither|who|whoever|whole|whom|whose|why|will|with|within|without|would|yet|you|your|yours|yourself|
yourselves)\b"""


def search(request):
	"""
	Search for blog posts.

	This template will allow you to setup a simple search form that will try to return results based on
	given search strings. The queries will be put through a stop words filter to remove words like
	'the', 'a', or 'have' to help imporve the result set.

	Template: ``blog/post_search.html``
	Context:
		 object_list
				List of blog posts that match given search term(s).
		 search_term
				Given search term.
	"""
	if request.GET:
		 stop_word_list = re.compile(STOP_WORDS, re.IGNORECASE)
		 search_term = '%s' % request.GET['q']
		 cleaned_search_term = stop_word_list.sub('', search_term)
		 cleaned_search_term = cleaned_search_term.strip()
		 if len(cleaned_search_term) != 0:
			post_list = Post.objects.filter(body__icontains=cleaned_search_term, status__gte=2, publish__lte=datetime.datetime.now())
			context = {'object_list': post_list, 'search_term':search_term}
			return render_to_response('blog/post_search.html', context, context_instance=RequestContext(request))
		 else:
			message = 'Search term was too vague. Please try again.'
			context = {'message':message}
			return render_to_response('blog/post_search.html', context, context_instance=RequestContext(request))
	else:
		 return render_to_response('blog/post_search.html', {}, context_instance=RequestContext(request))
