from channels import Group
from channels.auth import channel_session_user_from_http, channel_session_user
from index.decorators import staff_required
from afdansen import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
import json
from django.contrib.auth.decorators import login_required

@channel_session_user_from_http
@login_required
def connectJury(message, pk):
    """
    Handles an incomming websocket connection when a jurymember opens a jurypage

    :param message:
    :param pk:
    :return:
    """
    #accept the handshake if the dance is found, otherwise reject
    try:
        dance = models.Dance.objects.get(pk=pk)
    except models.Dance.DoesNotExist:
        message.reply_channel.send({'close':True})
        return
    message.reply_channel.send({'accept': True})

    #select all grades already entered for this dance by this jury member and send them to the client to load in juryform
    grades = models.Grade.objects.filter(Q(Jury=message.user) & Q(Dance=dance)).distinct()
    gradespackage = {}
    for grade in grades:
        #set the grades in package
        if grade.Pair.LeadingRole == grade.Person:
            gradespackage['M{}_{}'.format(grade.Pair.id, grade.SubDance.id)] = float(grade.Grade)
        else:
            gradespackage['V{}_{}'.format(grade.Pair.id, grade.SubDance.id)] = float(grade.Grade)
    message.reply_channel.send({'text':json.dumps(gradespackage)})

@channel_session_user
@login_required
def receiveJury(message, pk):
    """
    Handles incomming message from jury page to save grade

    :param message:
    :param pk:
    :return:
    """
    #accept the handshake if the dance is found, otherwise reject
    try:
        dance = models.Dance.objects.get(pk=pk)
    except models.Dance.DoesNotExist:
        message.reply_channel.send({'close':True})
        return
    message.reply_channel.send({'accept': True})

    #check if this user has the correct jury rights, otherwise close channel
    if message.user not in dance.Jury.all():
        message.reply_channel.send({'text' : 'Not correct jury access rights!'})
        message.reply_channel.send({"close" : True})

    #try to parse the given message, simply return error but do not close channel if invalid format
    try:
        data = json.loads(message.content['text'])
    except:
        message.reply_channel.send({'text' : 'Invalid json format of message!'})
        return

    try:
        #retrieve the objects from database
        pair = get_object_or_404(models.Pair, pk=data['pair'])
        subdance = get_object_or_404(models.SubDance, pk=data['subdance'])
        if data['dance'] != int(pk):
            message.reply_channel.send({"close" : True})
            return
        if data['person'] == 'M':
            person = pair.LeadingRole
        elif data['person'] == 'V':
            person = pair.FollowingRole
        else:
            message.reply_channel.send({'close' : True})
            return
        #check if grade already exists if not create new object
        grade = models.Grade.objects.filter(Q(Pair=pair) & Q(Dance=dance) & Q(Person=person) & \
                                            Q(Jury=message.user) & Q(SubDance=subdance))
        if grade.count() == 0:
            grade = models.Grade(Pair=pair, Dance=dance, Person=person, Jury=message.user, SubDance=subdance \
                                 , Grade=0.0)
        else:
            grade = grade[0]

        #round the grade to half points using math trick
        #replace all possible delimters to a dot so that float understands it
        gradedata = data['grade'].replace(',', '.').replace(';', '.').replace('*', '.').replace('+', '.')
        try:
            g = float(gradedata)
        except:
            #float has failed so report this
            message.reply_channel.send({'text' : 'Unable to convert grade to a number, please check input'})
            return

        g = round(g * 2) / 2
        #refuse out of bounds grades
        if g < 5 or g > 10:
            message.reply_channel.send({'text' : 'Invalid grade (lower than 5 or higher than 10)'})
            return
        #if grade is updated, update it in the database
        if grade.Grade != g:
            grade.Grade = g
            grade.save()
            #send message to the livestream
            Group('livestream').send({'text' : ' pair <i>{}</i> dance <i>{}</i> person <i>{}</i> with grade <i>{}</i> from <i>{}</i>'\
                                        .format(str(pair), str(dance), str(person), grade.Grade, str(message.user.username))})
        #send always message back even if grade wasnt updated
        message.reply_channel.send({'text': 'Grade saved for pair {} dance {} person {} with grade {}' \
                                   .format(pair.id, dance.id, person.id, grade.Grade)})

    except Exception as e:
        #if generic error than send back and close channel
        message.reply_channel.send({'text':str(e)})
        message.reply_channel.send({'close' : True})


@channel_session_user_from_http
@staff_required
def connectLiveStream(message):
    """
    Handles incomming livestream request. simply adds the channel to the livestream group

    :param message:
    :return:
    """
    message.reply_channel.send({'accept': True})
    Group("livestream").add(message.reply_channel)
    Group("livestream").send({'text' : 'Connected'})