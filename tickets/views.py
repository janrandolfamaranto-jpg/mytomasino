from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Ticket, TicketHistory
from .forms import TicketForm

@login_required
def ticket_list(request):
    tickets = Ticket.objects.filter(created_by=request.user).order_by('-created_at')

    open_tickets = tickets.filter(status='open')
    in_progress_tickets = tickets.filter(status='in_progress')
    completed_tickets = tickets.filter(status='completed')
    context = {
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'completed_tickets': completed_tickets,
    }

    return render(request, 'tickets/ticket_overview.html', context)

@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, created_by=request.user)
    history = TicketHistory.objects.filter(ticket=ticket).order_by('-timestamp')
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket, 'history': history})

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user  
            ticket.save()
            TicketHistory.objects.create(ticket=ticket, action="Ticket created by user")
            return redirect('tickets:ticket_overview')  
    else:
        form = TicketForm()
    
    return render(request, 'tickets/create_ticket.html', {'form': form})

@login_required
def delete_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, created_by=request.user)

    TicketHistory.objects.create(
        ticket=None,  
        ticket_title=ticket.title,
        action="Ticket deleted by user"
    )

    ticket.delete()
    return redirect('tickets:ticket_overview')


@login_required
def update_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, created_by=request.user)

    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            updated_ticket = form.save()
            TicketHistory.objects.create(
                ticket=updated_ticket,
                action="Ticket updated by user"
            )
            return redirect('tickets:ticket_detail', pk=ticket.pk)
    else:
        # This line is crucial — pre-fills the form with ticket data
        form = TicketForm(instance=ticket)

    # Render the correct template with context
    return render(request, 'tickets/update_ticket.html', {'form': form, 'ticket': ticket})

   