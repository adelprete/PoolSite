from django.template import Library
from django.conf import settings

register = Library()


@register.inclusion_tag('oscars/top_three.html',takes_context=True)
def display_top_three(context):
    pool = context['pool']
    if pool.season.display_winners:

        picksheets = pool.bracket_set.all().order_by('-total_points')

        context['top_three_winners'] = picksheets
    else:
        context['top_three_winners'] = None

    return context
