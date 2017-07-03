from django import template
from django.contrib.auth.models import Group
from afdansen.models import *
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_user_agents.utils import get_user_agent

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_names):
    if user.is_superuser:
        return True
    for group_name in group_names.split(';'):
        group = Group.objects.get(name=group_name)
        if group in user.groups.all():
            return True

    return False

@register.simple_tag
def GetHash():
    try:
        with open("githash", "r") as stream:
            h = stream.readlines()[0].strip('\n')
        return h[:10]
    except:
        return "None"

@register.simple_tag
def getSubRelationObj(danceid, subdanceid):
    d = get_object_or_404(Dance, pk=danceid)
    subd = get_object_or_404(SubDance, pk=subdanceid)

    return DanceSubDanceRelation.objects.get(Q(d) & Q(subd))

@register.filter(name='is_ios')
def is_ios(request):
    user_agent = get_user_agent(request)
    if user_agent.os.family == 'iOS':
        return True
    else:
        return False
