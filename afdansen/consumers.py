from afdansen import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
import json
from asgiref.sync import async_to_sync

from channels.generic.websocket import WebsocketConsumer

class JuryConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.pk = self.scope['url_route']['kwargs']['pk']
        try:
            self.dance = models.Dance.objects.get(pk=self.pk)
        except models.Dance.DoesNotExist:
            return self.close()

        # check if this user has the correct jury rights, otherwise close channel
        if self.user not in self.dance.Jury.all():
            self.close()


        self.accept()

        # select all grades already entered for this dance by this jury member and send them to the client to load in juryform
        grades = models.Grade.objects.filter(Q(Jury=self.user) & Q(Dance=self.dance)).distinct()
        gradespackage = {}
        for grade in grades:
            # set the grades in package
            if grade.Pair.LeadingRole == grade.Person:
                gradespackage['M{}_{}'.format(grade.Pair.id, grade.SubDance.id)] = float(grade.Grade)
            else:
                gradespackage['V{}_{}'.format(grade.Pair.id, grade.SubDance.id)] = float(grade.Grade)

        self.send(text_data=json.dumps(gradespackage))

    def receive(self, text_data):
        #try to parse the given message, simply return error but do not close channel if invalid format
        try:
            data = json.loads(text_data)
        except:
            self.send(text_data='Invalid json format of message!')
            return

        try:
            #retrieve the objects from database
            pair = get_object_or_404(models.Pair, pk=data['pair'])
            subdance = get_object_or_404(models.SubDance, pk=data['subdance'])
            if data['dance'] != int(self.dance.pk):
                self.close()
                return
            if data['person'] == 'M':
                person = pair.LeadingRole
            elif data['person'] == 'V':
                person = pair.FollowingRole
            else:
                self.close()
                return
            #check if grade already exists if not create new object
            grade = models.Grade.objects.filter(Q(Pair=pair) & Q(Dance=self.dance) & Q(Person=person) & \
                                                Q(Jury=self.user) & Q(SubDance=subdance))
            if grade.count() == 0:
                grade = models.Grade(Pair=pair, Dance=self.dance, Person=person, Jury=self.user, SubDance=subdance \
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
                self.send(text_data='Unable to convert grade to a number, please check input')
                return

            g = round(g * 2) / 2
            #refuse out of bounds grades
            if g < 5 or g > 10:
                self.send(text_data='Invalid grade (lower than 5 or higher than 10)')
                return
            #if grade is updated, update it in the database
            if grade.Grade != g:
                grade.Grade = g
                grade.save()
                # #send message to the livestream
                # Group('livestream').send({'text' : ' pair <i>{}</i> dance <i>{}</i> person <i>{}</i> with grade <i>{}</i> from <i>{}</i>'\
                #                             .format(str(pair), str(dance), str(person), grade.Grade, str(message.user.username))})
                async_to_sync(self.channel_layer.group_send)(
                    'livestream', {
                    'type' : 'update',
                    'text' : 'pair <i>{}</i> dance <i>{}</i> person <i>{}</i> with grade <i>{}</i> from <i>{}</i>'\
                                             .format(str(pair), str(self.dance), str(person), grade.Grade, str(self.user.username))
                })
            #send always message back even if grade wasnt updated
            self.send(text_data='Grade saved for pair {} dance {} person {} with grade {}' \
                                       .format(pair.id, self.dance.pk, person.id, grade.Grade))

        except Exception as e:
            #if generic error than send back and close channel
            self.send(text_data=str(e))
            self.close()

class LiveStreamConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        if not self.user.is_staff:
            self.close()
        async_to_sync(self.channel_layer.group_add)(
            'livestream',
            self.channel_name
        )
        self.accept()

    def receive(self, text_data):
        pass

    def update(self, event):
        self.send(text_data=event["text"])

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            'livestream',
            self.channel_name
        )