from django import template
from django.utils.safestring import mark_safe
import markdown
import bleach

register = template.Library()

@register.filter(name='markdown')
def markdown_format(text):
    if not text:
        return ""
    
    # Extensions for better coding experience
    extensions = [
        'markdown.extensions.fenced_code',
        'markdown.extensions.tables',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
    ]
    
    html = markdown.markdown(text, extensions=extensions)
    
    # Allowed tags/attributes for bleach (safe HTML)
    allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + [
        'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
        'pre', 'code', 'br', 'hr', 
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'img', 'span', 'div', 'blockquote', 'ul', 'ol', 'li', 'strong', 'em', 'del'
    ]
    
    allowed_attributes = {
        '*': ['class', 'id', 'style'],
        'img': ['src', 'alt', 'title'],
        'a': ['href', 'title', 'target'],
        'code': ['class'],
        'pre': ['class'],
    }
    
    # cleaned_html = bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes)
    # return mark_safe(cleaned_html)
    return mark_safe(html)
