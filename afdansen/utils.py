from .models import Pair
from django.db.models import Max, Q

## util functions
def getSuggestedBackNumber(pair, missingnumbers, greedy=False, cleaned_data=None):
    #if the object is new, the cleaned_data is inserted from modelform so use that
    if cleaned_data is not None:
        if Pair.objects.filter(LeadingRole=cleaned_data['LeadingRole']).exclude(id=pair.id).count() > 0:
            #backnumbers of some leader should be same so just take number of first one
            if Pair.objects.filter(LeadingRole=cleaned_data['LeadingRole'])[0].BackNumber != 0:
                return Pair.objects.filter(LeadingRole=cleaned_data['LeadingRole'])[0].BackNumber
    else:
        if Pair.objects.filter(LeadingRole=pair.LeadingRole).exclude(id=pair.id).count() > 0:
            #backnumbers of some leader should be same so just take number of first one
            if Pair.objects.filter(LeadingRole=pair.LeadingRole)[0].BackNumber != 0:
                return Pair.objects.filter(LeadingRole=pair.LeadingRole)[0].BackNumber
    #find a valid number by simply iterating, this is expensive.
    #greedy way is to do maxnumber + 1, this can be used when pairs are imported. than we know there are no gaps
    if greedy:
        m = Pair.objects.all().aggregate(Max('BackNumber'))['BackNumber__max']
        if m is None:
            m = 0
        while True:
            m += 1
            if m not in missingnumbers:
                return m
    else:
        numbers = [p.BackNumber for p in Pair.objects.all()]
        m = 0
        while True:
            m += 1
            if m not in missingnumbers and m not in numbers:
                return m
