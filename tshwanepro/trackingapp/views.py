from django.shortcuts import render
from django.contrib import messages
from reportsapp.models import FaultReport


def track_report(request):
    """
    Track a report by tracking ID.
    """
    tracking_id = request.GET.get('tracking_id', '').strip().upper()
    
    if tracking_id:
        try:
            report = FaultReport.objects.get(tracking_id=tracking_id)
            context = {
                'report': report,
                'tracking_id': tracking_id,
                'found': True,
            }
        except FaultReport.DoesNotExist:
            context = {
                'tracking_id': tracking_id,
                'found': False,
            }
            messages.error(request, f'No report found with tracking ID: {tracking_id}')
    else:
        context = {
            'report': None,
            'tracking_id': '',
            'found': None,
        }
    
    return render(request, 'trackingapp/trackreports.html', context)
