from django.template import Library

register = Library()

OPT_SEP = ', '

@register.inclusion_tag('oscars/piechart.html')
def render_piechart():
    """
    formatted_options = {
        'div_id': options.get('div_id'),
        'title': options.get('title', ''),
        'chart_options': options.get('chart_options', [{'height': 300, 'width': 750}]),
        'header_labels': options.get('header_labels', ''),
        'series_options': options.get('series_options', []),
        'data_type': options.get('data_type','\'\''),
        'data': options.get('data', ['No Data',100])
    }
    """
    formatted_options = {
        'data': "{y: 392, sliced: 1, name: 'Responded'}, {y: 1952, sliced: 1, name: 'Did not respond'}"
    }

    return formatted_options

@register.inclusion_tag('oscars/top_three.html',takes_context=True)
def display_top_three(context):
    pool = context['pool']
    if pool.can_display_winners:
        if pool.how_to_win == 'points':
            ballots = pool.ballot_set.all().order_by('-total_points','-total_correct','last_save_date')
        else:
            ballots = pool.ballot_set.all().order_by('-total_correct','last_save_date')[:3]

        context['top_three_winners'] = ballots
    else:
        context['top_three_winners'] = None

    return context

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def remove_underscores(value):
    value = value.replace("_"," ")
    return value

@register.assignment_tag
def get_attr(item, attribute):
    try:
        if hasattr(item,attribute):
            return getattr(item,attribute)
    except:
        return None

@register.assignment_tag
def get_attr_verbose_name(item, attribute):
    try:
        if getattr(item,attribute):
            return item._meta.get_field_by_name(attribute)[0].verbose_name
    except:
        return None

@register.assignment_tag
def get_winner(dictionary,key):
    return dictionary.get(key)

@register.assignment_tag
def subtract(value, arg):
    return value - arg
