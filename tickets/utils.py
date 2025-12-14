from user.models import Office, StaffProfile

def assign_office_and_staff(ticket):
    category_map = {
        'academic': 'Registrar’s Office',
        'technical': 'ETC',
        'facilities': 'Physical Plant and Facilities Management Office',
        'lostfound': 'Principal Office', 'Office of Student Services'
        'welfare': 'Guidance Office',
    }

    office_name = category_map.get(ticket.category)
    if office_name:
        try:
            office = Office.objects.get(name=office_name)
            staff = StaffProfile.objects.filter(office=office).first()
            ticket.assigned_to = staff.user if staff else None
            ticket.save()
        except Office.DoesNotExist:
            ticket.assigned_to = None
