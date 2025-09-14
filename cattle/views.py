from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Cattle, HealthCheck, CalendarEvent
from .forms import CattleForm, HealthCheckForm, VaccinationForm, FeedingRationForm, CalendarEventInlineForm
from rest_framework import viewsets
from .serializers import CattleSerializer, HealthCheckSerializer
from django.db.models import Subquery, OuterRef
from django.contrib import messages
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime

# ---------------- Dashboard ----------------
def dashboard(request):
    total = Cattle.objects.count()
    latest_checks = HealthCheck.objects.filter(cattle=OuterRef('pk')).order_by('-check_date')

    sick_count = Cattle.objects.annotate(
        latest_status=Subquery(latest_checks.values('status')[:1])
    ).filter(latest_status='sick').count()

    for_sale_count = Cattle.objects.annotate(
        latest_status=Subquery(latest_checks.values('status')[:1])
    ).filter(latest_status='forsale').count()

    cattle_with_status = Cattle.objects.annotate(
        latest_status=Subquery(latest_checks.values('status')[:1])
    )

    events = CalendarEvent.objects.all()
    events_data = []
    for event in events:
        events_data.append({
            'title': f"{event.title}{f' ({event.cattle.tag_no})' if event.cattle else ''}",
            'start': event.start.isoformat(),
            'end': event.end.isoformat() if event.end else None,
            'url': reverse('cattle:update_calendar_event', args=[event.id])
        })

    context = {
        'total': total,
        'sick_count': sick_count,
        'for_sale_count': for_sale_count,
        'cattle_with_status': cattle_with_status,
        'events_data': events_data,
    }
    return render(request, 'dashboard.html', context)

def get_calendar_events(request):
    events = CalendarEvent.objects.all()
    event_list = []

    for event in events:
        if event.event_type == 'feeding':
            color = '#3788d8'
            event_type_name = 'ให้อาหาร'
        elif event.event_type == 'health':
            color = '#dc3545'
            event_type_name = 'ตรวจสุขภาพ'
        elif event.event_type == 'vaccine':
            color = '#ffc107'
            event_type_name = 'วัคซีน'
        elif event.event_type == 'breeding':
            color = '#fd7e14'
            event_type_name = 'ผสมพันธุ์'
        else:
            color = '#6c757d'
            event_type_name = 'อื่น ๆ'

        title = f"{event.title}"
        if event.cattle:
            title += f" ชื่อโค: ({event.cattle.name or event.cattle.tag_no})"
        title += f" [{event_type_name}]"

        event_list.append({
            'title': title,
            'start': event.start.isoformat(),
            'end': event.end.isoformat() if event.end else None,
            'color': color,
        })

    return JsonResponse(event_list, safe=False)

# ---------------- Cattle List ----------------
def cattle_list(request):
    # ดึง HealthCheck ล่าสุดของแต่ละโค
    latest_checks = HealthCheck.objects.filter(cattle=OuterRef('pk')).order_by('-check_date', '-id')
    
    cattle_qs = Cattle.objects.annotate(
        latest_status=Subquery(latest_checks.values('status')[:1])
    )

    # กรองตาม query params
    if request.GET.get('for_sale') == '1':
        cattle_qs = cattle_qs.filter(latest_status='forsale')
    elif request.GET.get('sick') == '1':
        cattle_qs = cattle_qs.filter(latest_status='sick')

    # ค้นหาตาม tag_no
    query = request.GET.get('q')
    if query:
        cattle_qs = cattle_qs.filter(tag_no__icontains=query)

    return render(request, 'cattle_list.html', {
        'cattle_list': cattle_qs,
        'query': query
    })

def cattle_delete(request, cattle_id):
    cattle = get_object_or_404(Cattle, pk=cattle_id)
    cattle.delete()
    messages.success(request, f'ลบโค {cattle.tag_no} เรียบร้อยแล้ว')
    return redirect('cattle:cattle_list')

# ---------------- Cattle Detail ----------------
def cattle_detail(request, cattle_id):
    cattle = get_object_or_404(Cattle, pk=cattle_id)
    checks = cattle.healthchecks.all()
    return render(request, 'cattle_detail.html', {'c': cattle, 'checks': checks})

# ---------------- Add/Edit Cattle ----------------
def add_cattle(request):
    if request.method == 'POST':
        form = CattleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cattle:cattle_list')
    else:
        form = CattleForm()
    return render(request, 'add_cattle.html', {'form': form})

# ------------------- CATTLE EDIT -------------------
def cattle_edit(request, cattle_id):
    cattle = get_object_or_404(Cattle, pk=cattle_id)
    if request.method == 'POST':
        form = CattleForm(request.POST, instance=cattle)
        if form.is_valid():
            form.save()
            messages.success(request, f'แก้ไขข้อมูลโค {cattle.name or cattle.tag_no} เรียบร้อยแล้ว')
            return redirect('cattle:cattle_list')
        else:
            messages.error(request, 'กรุณาตรวจสอบข้อมูล: มีข้อผิดพลาดในฟอร์ม')
    else:
        form = CattleForm(instance=cattle)
    return render(request, 'cattle_edit.html', {'form': form, 'cattle': cattle})

# ---------------- Select Cattle before HealthCheck ----------------
def select_cattle_for_healthcheck(request):
    if request.method == 'POST' and 'add_cattle_submit' in request.POST:
        cattle_form = CattleForm(request.POST)
        if cattle_form.is_valid():
            cattle_form.save()
            return redirect('cattle:select_cattle_for_healthcheck')
    else:
        cattle_form = CattleForm()

    cattle_list = Cattle.objects.all()
    context = {
        'cattle_list': cattle_list,
        'cattle_form': cattle_form,
    }
    return render(request, 'select_cattle_healthcheck.html', context)

# ------------------- ADD HEALTHCHECK -------------------
def add_healthcheck(request, cattle_id):
    cattle = get_object_or_404(Cattle, pk=cattle_id)

    if request.method == 'POST':
        hc_form = HealthCheckForm(request.POST, prefix='hc')
        vax_form = VaccinationForm(request.POST, prefix='vax')
        ration_form = FeedingRationForm(request.POST, prefix='ration')
        cal_form = CalendarEventInlineForm(request.POST, prefix='cal')

        all_valid = hc_form.is_valid()
        if vax_form.has_changed():
            all_valid = all_valid and vax_form.is_valid()
        if ration_form.has_changed():
            all_valid = all_valid and ration_form.is_valid()
        if cal_form.has_changed():
            all_valid = all_valid and cal_form.is_valid()

        if all_valid:
            # Save HealthCheck
            hc = hc_form.save(commit=False)
            hc.cattle = cattle
            hc.save()

            # Save Vaccination ถ้ามี
            if vax_form.has_changed():
                v = vax_form.save(commit=False)
                v.cattle = cattle
                v.save()

            # Save FeedingRation ถ้ามี
            if ration_form.has_changed():
                r = ration_form.save(commit=False)
                r.cattle = cattle
                r.save()

            # Save CalendarEvent ถ้ามี
            if cal_form.has_changed():
                e = cal_form.save(commit=False)
                e.cattle = cattle
                e.save()

            messages.success(request, f'บันทึกข้อมูลสำหรับโค {cattle.name or cattle.tag_no} เรียบร้อยแล้ว')
            return redirect('cattle:cattle_detail', cattle_id=cattle.id)
        else:
            messages.error(request, 'กรุณาตรวจสอบข้อมูล: มีข้อผิดพลาดในบางฟอร์ม')

    else:
        # GET → set status ล่าสุด
        latest_hc = cattle.healthchecks.order_by('-check_date').first()
        initial_status = latest_hc.status if latest_hc else 'healthy'

        hc_form = HealthCheckForm(prefix='hc', initial={'status': initial_status})
        vax_form = VaccinationForm(prefix='vax')
        ration_form = FeedingRationForm(prefix='ration')
        cal_form = CalendarEventInlineForm(prefix='cal')

    context = {
        'hc_form': hc_form,
        'vax_form': vax_form,
        'ration_form': ration_form,
        'cal_form': cal_form,
        'cattle': cattle,
    }
    return render(request, 'add_healthcheck.html', context)

# ---------------- Farm Calendar ----------------
def farm_calendar(request):
    events = CalendarEvent.objects.all()
    return render(request, "farm_calendar.html", {"events": events})

def farm_calendar_events(request):
    events = CalendarEvent.objects.all()
    data = []
    for e in events:
        data.append({
            "id": e.id,
            "title": e.title,
            "start": e.start.isoformat(),
            "end": e.end.isoformat() if e.end else e.start.isoformat(),
        })
    return JsonResponse(data, safe=False)

def add_calendar_event(request):
    if request.method == "POST":
        cattle_id = request.POST.get("cattle")
        cattle = get_object_or_404(Cattle, id=cattle_id)
        title = request.POST.get("title")
        start = parse_datetime(request.POST.get("start"))
        end = parse_datetime(request.POST.get("end")) if request.POST.get("end") else start
        event_type = request.POST.get("event_type")
        notes = request.POST.get("notes")
        CalendarEvent.objects.create(
            cattle=cattle,
            title=title,
            start=start,
            end=end,
            event_type=event_type,
            notes=notes
        )
        return redirect('cattle:farm_calendar')
    cattles = Cattle.objects.all()
    return render(request, "add_calendar_event.html", {"cattles": cattles})

def update_calendar_event(request, event_id):
    event = get_object_or_404(CalendarEvent, id=event_id)
    if request.method == "POST":
        event.title = request.POST.get("title")
        event.start = parse_datetime(request.POST.get("start"))
        event.end = parse_datetime(request.POST.get("end")) if request.POST.get("end") else event.start
        event.event_type = request.POST.get("event_type")
        event.notes = request.POST.get("notes")
        event.save()
        return redirect('cattle:farm_calendar')
    cattles = Cattle.objects.all()
    return render(request, "update_calendar_event.html", {"event": event, "cattles": cattles})

def delete_calendar_event(request, event_id):
    event = get_object_or_404(CalendarEvent, id=event_id)
    event.delete()
    return redirect('cattle:farm_calendar')

# ---------------- DRF ViewSets ----------------
class CattleViewSet(viewsets.ModelViewSet):
    queryset = Cattle.objects.all()
    serializer_class = CattleSerializer

class HealthCheckViewSet(viewsets.ModelViewSet):
    queryset = HealthCheck.objects.all()
    serializer_class = HealthCheckSerializer
