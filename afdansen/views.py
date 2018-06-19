from django.shortcuts import render
from django.shortcuts import redirect
from index.decorators import staff_required, superuser_required
from . import forms
from . import models
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from index.views import send_mail
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Max, Q, Sum, FloatField, F
from decimal import *
from itertools import chain
from django.http import HttpResponse
import json
from .utils import getSuggestedBackNumber
from general_excel import BacknumbersExcel
from django.http.response import HttpResponse

@login_required
def juryPageDance(request, danceid, heatid):
    """
    Serves the jury page on which jury member can put in grades.

    :param request:
    :param danceid: id of requested dance
    :param heatid: id of requested heat
    :return:
    """
    d = get_object_or_404(models.Dance, pk=danceid)
    h = get_object_or_404(models.Heat, pk=heatid)

    # check if the user is indeed a jury member of selected dance
    if request.user not in d.Jury.all():
        raise PermissionDenied("not a jury")

    return render(request, 'jury.html', {
        'pairs' : h.Persons.all().order_by('BackNumber'),
        'dance' : d,
        'subdances' : d.SubDances.order_by('dancesubdancerelation'),
        'heat' : h,
    })

@login_required
def juryPage(request):
    """
    Serves a menu for all heats current user has access to

    :param request:
    :return:
    """
    heats = []
    # iterate through all dances the current user has access too
    for dance in request.user.jury.all():
        for heat in models.Heat.objects.filter(Dance=dance):
            heats.append(heat)
    return render(request, 'jurydancechoice.html', {'heats' : heats})

@staff_required
def PersonList(request):
    """
    Serves list of all persons in databse

    :param request:
    :return:
    """
    return render(request, 'personlist.html', {'persons' : models.Person.objects.all()})

@staff_required
def PairList(request):
    """
    Serves list of all pairs in database

    :param request:
    :return:
    """
    return render(request, 'pairlist.html', {'pairs' : models.Pair.objects.all()})

@staff_required
def GradeList(request):
    """
    Serves a full list of all results that have been entered into the system

    :param request:
    :return:
    """
    return render(request, 'gradelist.html', {
        'grades' : models.Grade.objects.all()#.order_by('Dance', 'Pair', 'SubDance', 'Person')
    })

@staff_required
def ResultList(request):
    """
    Calculates the average result per person per dance and orders them in a python data structure to render in template

    :param request:
    :return:
    """

    grades = []
    for person in models.Person.objects.all():
        for dancepair in list(chain(person.pairs_following.all(), person.pairs_leading.all())):
            for dance in dancepair.Dances.all():
                info = {
                    'Person': str(person),
                    'Dance' : str(dance),
                    'Subdances' : []
                }
                for subdance in dance.SubDances.all():
                    #select the grades of the current selected combination in the loop
                    gradesdb = models.Grade.objects.filter(Q(Pair=dancepair) &
                                                 Q(Person=person) & Q(Dance=dance)
                                                 & Q(SubDance=subdance))
                    #iterate through person->dance->subdance
                    #use database aggregation to get average of grade of selected grades selected above
                    #this is fast because it is done in the database
                    aggr = gradesdb.aggregate(average=Sum(F('Grade'), output_field=FloatField()))['average']
                    if aggr is not None:
                        info['Subdances'].append({
                            'Name' : str(subdance),
                            'Grade' : float(aggr) / float(gradesdb.count()),
                        })
                grades.append(info)
    return render(request, 'resultlist.html', {
        'grades' : grades
    })

@staff_required
def CreatePair(request):
    """
    Serves form to create pair object

    :param request:
    :return:
    """
    if request.method == "POST":
        form = forms.PairForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'base.html', {"Message" : "Pair created"})
    else:
        form = forms.PairForm()
    return render(request, 'GenericForm.html', {
        'form'          : form,
        'buttontext'    : 'Create',
        'formtitle'     : 'Create new Pair',
    })

@staff_required
def EditPair(request, pk):
    """
    Serves form to edit given pair object

    :param request:
    :param pk:
    :return:
    """
    obj = get_object_or_404(models.Pair, pk=pk)
    if request.method == "POST":
        form = forms.PairForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return render(request, 'base.html', {
                "Message" : "Pair saved",
                'return': 'afdansen:pairlist',
            })
    else:
        form = forms.PairForm(instance=obj)
    return render(request, 'GenericForm.html', {
        'form'          : form,
        'buttontext'    : 'Save',
        'formtitle'     : 'Edit Pair',
    })

@staff_required
def DeletePair(request, pk):
    """
    Serves confirmation form to delete given id of pair

    :param request:
    :param pk:
    :return:
    """
    obj = get_object_or_404(models.Pair, pk=pk)
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            obj.delete()
            return render(request, 'base.html', {
                'Message' : 'Pair deleted!',
                'return' : 'afdansen:pairlist',
            })
    else:
        form = forms.ConfirmForm()

    return render(request, 'GenericForm.html', {
        'form' : form,
        'formtitle' : 'Confirm deletion of {}'.format(obj),
        'buttontext' : 'Delete'
    })

@staff_required
def CreatePerson(request):
    """
    Serves form to create new person object

    :param request:
    :return:
    """
    if request.method == "POST":
        form = forms.PersonForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'base.html', {"Message" : "Person created"})
    else:
        form = forms.PersonForm()
    return render(request, 'GenericForm.html', {
        'form'          : form,
        'buttontext'    : 'Create',
        'formtitle'     : 'Create new Person',
    })

@staff_required
def EditPerson(request, pk):
    """
    Serves form to edit given person object

    :param request:
    :param pk:
    :return:
    """
    obj = get_object_or_404(models.Person, pk=pk)
    if request.method == "POST":
        form = forms.PersonForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return render(request, 'base.html', {"Message" : "Person saved"})
    else:
        form = forms.PersonForm(instance=obj)
    return render(request, 'GenericForm.html', {
        'form'          : form,
        'buttontext'    : 'Save',
        'formtitle'     : 'Edit Person',
    })

@staff_required
def DeletePerson(request, pk):
    """
    Serves confirmation form to delete given personobject

    :param request:
    :param pk:
    :return:
    """
    obj = get_object_or_404(models.Person, pk=pk)
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            obj.delete()
            return render(request, 'base.html', {
                'Message' : 'Person deleted!',
                'return' : 'afdansen:personlist',
            })
    else:
        form = forms.ConfirmForm()

    return render(request, 'GenericForm.html', {
        'form' : form,
        'formtitle' : 'Confirm deletion of {}'.format(obj),
        'buttontext' : 'Delete'
    })

@staff_required
def CreateSubDanceRelation(request):
    """
    Serves a form to create a new subdance in a dance.
    Creates a subdancerelation object which links dance and subdance together, this is needed to manipulate
       the order of the subdances in the dance

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = forms.DanceSubDanceCreateForm(request.POST)
        if form.is_valid():
            subd, created = models.SubDance.objects.get_or_create(Name=form.cleaned_data['SubDance'])
            d = form.cleaned_data['Dance']
            #find the highest order for new subdancerelaiton. if not exists start at 1
            try:
                o = models.DanceSubDanceRelation.objects.filter(Dance=d).aggregate(Max('Order'))['Order__max'] + 1
            except:
                o = 1
            models.DanceSubDanceRelation.objects.create(Dance=d, SubDance=subd, Order=o).save()
            return render(request, 'base.html', {
                "Message" : "SubDance {} attached to Dance {} with order {}".format(subd, d, o),
                "return" : "afdansen:createsubdancerelation",
            })
    else:
        form = forms.DanceSubDanceCreateForm()

    return render(request, 'GenericForm.html', {
        'form' : form,
        'buttontext' : 'Create',
        'formtitle' : 'Assign SubDance to Dance',
    })

@staff_required
def SubDanceOrderUp(request, danceid, subdanceid):
    """
    Move up the selected subdance in the selected dance, swap if necessary

    :param request:
    :param danceid:
    :param subdanceid:
    :return:
    """
    d = get_object_or_404(models.Dance, pk=danceid)
    subd = get_object_or_404(models.SubDance, pk=subdanceid)
    obj = models.DanceSubDanceRelation.objects.get(Q(Dance=d) & Q(SubDance=subd))

    #if the order is equal to the number of subdancerelations existing than it is already at max order
    if obj.Order == models.DanceSubDanceRelation.objects.filter(Dance=d).count():
        return render(request, 'base.html', {'Message' : 'Already at max order'})
    obj2 = models.DanceSubDanceRelation.objects.get(Q(Dance=d) & Q(Order=obj.Order + 1))
    obj2.Order -= 1
    obj.Order += 1
    obj2.save()
    obj.save()

    return redirect('afdansen:dancelist')

@staff_required
def SubDanceOrderDown(request, danceid, subdanceid):
    """
    Move down selected subdance in selected dance, swap if necessary

    :param request:
    :param danceid:
    :param subdanceid:
    :return:
    """
    d = get_object_or_404(models.Dance, pk=danceid)
    subd = get_object_or_404(models.SubDance, pk=subdanceid)
    obj = models.DanceSubDanceRelation.objects.get(Q(Dance=d) & Q(SubDance=subd))
    # 1 is the minimum order number
    if obj.Order == 1:
        return render(request, 'base.html', {'Message' : 'Already at min order'})
    obj2 = models.DanceSubDanceRelation.objects.get(Q(Dance=d) & Q(Order = obj.Order - 1))
    obj.Order -= 1
    obj.save()
    obj2.Order += 1
    obj2.save()

    return redirect('afdansen:dancelist')

@staff_required
def SubDanceRelationDelete(request, danceid, subdanceid):
    """
    Delete given subdancerelation, no confirmation form

    :param request:
    :param danceid:
    :param subdanceid:
    :return:
    """
    d = get_object_or_404(models.Dance, pk=danceid)
    subd = get_object_or_404(models.SubDance, pk=subdanceid)
    obj = models.DanceSubDanceRelation.objects.get(Q(Dance=d) & Q(SubDance=subd))

    obj.delete()

    for relation in models.DanceSubDanceRelation.objects.filter(Order__gt=obj.Order):
        relation.Order -= 1
        relation.save()

    return redirect('afdansen:dancelist')

@staff_required
def DanceList(request):
    """
    Serves list of all dances in database

    :param request:
    :return:
    """
    return render(request, 'DanceList.html', {'dances' : models.Dance.objects.all()})

@staff_required
def RecalcBackNumbers(request):
    """
    Recalculates all backnumbers of pairs
    Will iterate through all pairs and give the lowest dancenumber available to the pair
    This will be either the maxnumber + 1 or the number of the pair with the same leader

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            #first reset all backnumbers to 0 and than call the util function in greedy mode,
            # just as with importing

            for p in models.Pair.objects.all():
                p.BackNumber = 0
                p.save()
            missingbacknumbers = [m.Number for m in models.MissingBackNumber.objects.all()]
            for p in models.Pair.objects.all():
                p.BackNumber = getSuggestedBackNumber(p, missingbacknumbers)
                p.save()

            return render(request, 'base.html', {
                'Message' : 'BackNumbes recalculated!',
                'return' : 'afdansen:pairlist',
            })
    else:
        form = forms.ConfirmForm()

    return render(request, 'GenericForm.html', {
        'form' : form,
        'formtitle' : 'Confirm recalculating backnumbers',
        'buttontext' : 'Go'
    })

@staff_required
def ExportBackNumbers(request):
    response = HttpResponse(content=BacknumbersExcel())
    response['Content-Disposition'] = 'attachment; filename=backnumbers.xlsx'
    return response

@superuser_required
def ImportPairs(request):
    """
    Import pairs from csv. This will first delete all existing pairs and than parse the pairs from csv

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = forms.CsvUpload(request.POST, request.FILES)
        if form.is_valid():
            missingbacknumbers = [m.Number for m in models.MissingBackNumber.objects.all()]
            models.Person.objects.all().delete()
            lines = request.FILES['csvfile'].readlines()
            del lines[0] #delete first line to get rid of headers
            for l in lines:
                parts = l.decode("utf-8", "ignore").strip('\n').strip('\r').lower().split(',')
                try:
                    int(parts[0].strip('"'))
                except:
                    continue
                p = models.Pair()
                #extract the leader and followername
                leadername = parts[2].strip('"').split(' ')
                followername = parts[3].strip('"').split(' ')
                #check if the leader already has a personobject if not create it
                if len(leadername) == 1:#check existance of prefix in name, if so chop it away
                    leaderobj = models.Person.objects.filter(FirstName=leadername[0])
                else:
                    leaderobj = models.Person.objects.filter(Q(FirstName=leadername[0]) & Q(LastName=leadername[-1]))
                if leaderobj.count() == 0:
                    leaderobj = models.Person()
                    leaderobj.FirstName = leadername.pop(0)
                    if len(leadername) == 0:
                        leaderobj.LastName = ''
                    else:
                        leaderobj.LastName = leadername.pop(-1)
                        leaderobj.Prefix = ' '.join(leadername)
                    leaderobj.save()
                else:
                    leaderobj = leaderobj[0]
                # check if the follower already has a personobject if not create it
                if len(followername) == 1:#check existance of prefix in name, if so chop it away
                    followerobj = models.Person.objects.filter(FirstName=followername[0])
                else:
                    followerobj = models.Person.objects.filter(Q(FirstName=followername[0]) & Q(LastName=followername[-1]))
                if followerobj.count() == 0:
                    followerobj = models.Person()
                    followerobj.FirstName = followername.pop(0)
                    if len(followername) == 0:
                        followerobj.LastName = ''
                    else:
                        followerobj.LastName = followername.pop(-1)
                        followerobj.Prefix = ' '.join(followername)
                    followerobj.save()
                else:
                    followerobj = followerobj[0]
                #create the pair object
                p.LeadingRole = leaderobj
                p.FollowingRole = followerobj
                p.BackNumber = getSuggestedBackNumber(p, missingbacknumbers, greedy=True)
                p.save()
                #add dances that this pair dances
                #take special care for ballroom and latin to translate to english names
                if 'stijldansen' in parts[4].strip('"'):
                    graad = parts[4].strip('"').split(' ')[1]
                    p.Dances.add(models.Dance.objects.get(Name="latin_{}".format(graad)))
                    p.Dances.add(models.Dance.objects.get(Name="ballroom_{}".format(graad)))
                else:
                    p.Dances.add(models.Dance.objects.get(Name=parts[4].strip('"').replace(' ', '_')))

                p.save()
            return render(request, 'base.html', {
                'Message' : 'Pairs imported!',
                'return'  : 'afdansen:pairlist',
            })
    else:
        form = forms.CsvUpload()

    return render(request, 'GenericForm.html', {
        'formtitle' : 'Import From Site, THIS WILL DELETE THE CURRENT PAIRS!',
        'form' : form,
    })


@superuser_required
def CreateJury(request):
    """
    Serve form to register new jury member

    :param request:
    :return:
    """
    if request.method == "POST":
        form = forms.RegisterJuryForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['Email'].lower()
            username = form.cleaned_data['FirstName'].lower()[0] + form.cleaned_data['LastName'].lower()
            if User.objects.filter(username=username).exists():
                return render(request, "base.html", {
                    "Message" : "User with username {} already exists!".format(username),
                    })
            if User.objects.filter(email=email).exists():
                return render(request, "base.html", {"Message":"User with email {} already exists!".format(email)})
            NewUser = User.objects.create_user(username, email, None)
            NewUser.first_name = form.cleaned_data['FirstName']
            NewUser.last_name = form.cleaned_data['LastName']
            NewUser.save()

            for dance in form.cleaned_data['Dances']:
                dance.Jury.add(NewUser)
                dance.save()

            # current_site = get_current_site(request)
            # domain = current_site.domain
            # context = {
            #     'domain' : domain,
            #     'uid'    : urlsafe_base64_encode(force_bytes(NewUser.pk)),
            #     'user'   : NewUser,
            #     'token'  : default_token_generator.make_token(NewUser),
            # }
            #
            # send_mail("email/password_newuser_set_email_subject.txt", "email/password_newuser_set_email.html", context,
            #           "no-reply@afdansen.edsvfootloose.nl", NewUser.email, html_email_template_name="email/password_newuser_set_email.html")

            return render(request, "base.html", { "Message" : "Jury {} created".format(username)})
    else:
        form = forms.RegisterJuryForm()
    return render(request, "GenericForm.html", {"form":form, "buttontext":"Save", "formtitle" : "Register new Jury"})

@superuser_required
def EditJury(request):
    """
    Serve form to give accounts access to being a jury

    :param request:
    :return:
    """
    if request.method == "POST":
        form = forms.EditJuryForm(request.POST)
        if form.is_valid():
            form.save()
            form = forms.EditJuryForm()
            return render(request, 'EditJuryForm.html', {
                'form': form,
                'formtitle': 'Edit Jury',
                'buttontext': 'Save',
                'saved' : True
            })
    else:
        form = forms.EditJuryForm

    return render(request, 'EditJuryForm.html', {
        'form' : form,
        'formtitle' : 'Edit Jury',
        'buttontext' : 'Save',
    })

@staff_required
def CreateHeat(request):
    """
    Serve form to create new heat

    :param request:
    :return:
    """
    if request.method == "POST":
        form = forms.HeatModelForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'base.html', {
                'Message' : 'Heat Created! Go to Heats->Edit to assign people.'
            })

    else:
        form = forms.HeatModelForm()

    return render(request, 'GenericForm.html', {
        'form' : form,
        'formtitle' : 'Create Heat',
    })

@staff_required
def EditHeatList(request):
    """
    Serves menu of list of all heats to choose from and edit in the modelform way

    :param request:
    :return:
    """
    return  render(request, 'chooseheat.html', {
        'heats' : models.Heat.objects.all(),
    })

@staff_required
def EditHeat(request, pk):
    """
    Serves menu of list of all dances to edit heats in the drag and drop way

    :param request:
    :param pk:
    :return:
    """
    obj = get_object_or_404(models.Heat, pk=pk)
    if request.method == "POST":
        form = forms.HeatModelForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            form = forms.HeatModelForm(instance=obj)
            return render(request, 'GenericForm.html', {
                'form': form,
                'formtitle': 'Edit Heat',
                'returnlink' : 'afdansen:editheatlist',
                'saved' : True,
            })
    else:
        form = forms.HeatModelForm(instance=obj)

    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Edit Heat',
        'returnlink': 'afdansen:editheatlist',
    })

@staff_required
def HeatEditListDance(request, pk):
    """
    Serves page to edit heat in drag and drop way

    :param request:
    :param pk:
    :return:
    """
    dance = get_object_or_404(models.Dance, pk=pk)
    if request.method == "POST":
        #have received a ajax call to save the heat data
        jsondata = request.POST.get('jsondata', None)
        if jsondata is None:
            return HttpResponse('{"type":"error","txt":"Invalid POST data"}')
        data = json.loads(jsondata)
        if 'unbounded' not in data:
            return HttpResponse('{"type":"error","txt":"Invalid POST data"}')
        heats = dance.heats.all()
        #data is saved in hashtable with heatid as key and list of pair ids as value
        #iterate through it
        for key, value in data.items():
            try:
                heatid = int(key)
            except:
                continue
            #find the heat object, if id is not found in this dance skip it
            try:
                h = dance.heats.get(pk=heatid)
            except models.Heat.DoesNotExist:
                continue
            #iterate the payload
            for p_id in value:
                #check if this pair exists
                pair = get_object_or_404(models.Pair, pk=p_id)
                #check if it was in one of the other heats, if so remove it
                for hts in heats:
                    if pair in hts.Persons.all():
                        hts.Persons.remove(pair)
                        break
                #add it to the correct heat
                h.Persons.add(pair)
        for p_id in data['unbounded']:
            pair = get_object_or_404(models.Pair, pk=p_id)
            for hts in heats:
                if pair in hts.Persons.all():
                    hts.Persons.remove(pair)
                    break
        #save all heats, django will figure out if heat has changed and needs saving
        for hts in heats:
            hts.save()
        return HttpResponse('{"type":"success","txt":"success"}')
    else:
        try:
            boundedpersons = dance.heats.all()[0].Persons.all()

            for h in dance.heats.all()[1:]:
                boundedpersons = boundedpersons | h.Persons.all()
        except:
            boundedpersons=[]

        return render(request, "HeatListEdit.html", {
            'heats' : models.Heat.objects.filter(Dance=dance).order_by('Number'),
            'unboundpairs' : dance.pairs.exclude(pk__in=boundedpersons).distinct().order_by('BackNumber'),
            'dance' : dance,
        })

@staff_required
def HeatDanceChooseList(request):
    """
    Serves menu to choose a dance to edit the heats off

    :param request:
    :return:
    """
    return render(request, "choosedance.html", {
        "dances" : models.Dance.objects.all(),
    })

def HeatListAll(request):
    """


    :param request:
    :return:
    """
    return render(request, "HeatListAll.html", {
        "dances" : models.Dance.objects.all()
    })

@staff_required
def LiveStream(request):
    """
    Serves the page for livestreamer

    :param request:
    :return:
    """
    return render(request, "livestreamer.html")

@staff_required
def PrintHeatList(request):
    """
    Serves a page with all heats without the menu, for printing purpose

    :param request:
    :return:
    """
    return render(request, "HeatListPrint.html", {
        "dances" : models.Dance.objects.all()
    })

@staff_required
def PrintJuryForm(request, danceid, heatid):
    """
    Serves a page with a jurypage of selected dance and heat

    :param request:
    :param danceid:
    :param heatid:
    :return:
    """
    d = get_object_or_404(models.Dance, pk=danceid)
    h = get_object_or_404(models.Heat, pk=heatid)

    return render(request, 'JuryFormPrint.html', {
        'pairs': h.Persons.all().order_by('BackNumber'),
        'dance': d,
        'subdances': d.SubDances.order_by('dancesubdancerelation'),
        'heat': h,
    })
