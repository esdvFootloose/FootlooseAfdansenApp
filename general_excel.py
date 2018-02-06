from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from afdansen.models import Pair

def BacknumbersExcel():
    wb = Workbook()
    ws = wb.active
    ws.title = 'BackNumbers'

    header = ['Number', 'Leader', 'Follower', 'Dance']

    ws.append(header)
    last_leader = None
    for p in Pair.objects.all():
        row = [p.BackNumber, str(p.LeadingRole), str(p.FollowingRole), '&'.join([str(x) for x in list(p.Dances.all())])]
        if last_leader == p.LeadingRole:
            row[0] = ''
        else:
            last_leader = p.LeadingRole
        ws.append(row)

    return save_virtual_workbook(wb)
