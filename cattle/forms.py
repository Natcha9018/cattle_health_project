from django import forms
from django.utils import timezone
from .models import Cattle, HealthCheck, CalendarEvent, Vaccination, FeedingRation

# สำหรับ HealthCheck status ภาษาไทย
STATUS_CHOICES = (
    ('healthy', 'ปกติ'),
    ('sick', 'ป่วย'),
    ('forsale', 'พร้อมขาย'),
)

# ------------------ CattleForm ------------------
class CattleForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('male', 'ตัวผู้'),
        ('female', 'ตัวเมีย'),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES, label='เพศ')
    status = forms.ChoiceField(choices=STATUS_CHOICES, label='สถานะ', required=False)

    # แก้พ่อแม่เป็น input พิมพ์ได้
    father = forms.CharField(label='พ่อโค', required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'หมายเลขหรือชื่อพ่อโค'}))
    mother = forms.CharField(label='แม่โค', required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'หมายเลขหรือชื่อแม่โค'}))

    class Meta:
        model = Cattle
        fields = ['tag_no', 'name', 'birth_date', 'gender', 'breed', 'category', 'housing', 'mother', 'father']
        widgets = {
            'tag_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'หมายเลขประจำตัว'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อโค'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'breed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'สายพันธุ์'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ประเภทโค'}),
            'housing': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'คอก/โรงเรือน'}),
        }

    def save(self, commit=True):
        cattle = super().save(commit=commit)

        # ถ้ามี status ถูกเลือก → บันทึกไปที่ HealthCheck ล่าสุด
        status = self.cleaned_data.get('status')
        if status:
            last_check = cattle.healthchecks.first()
            if last_check:
                last_check.status = status
                last_check.save()
            else:
                HealthCheck.objects.create(
                    cattle=cattle,
                    check_date=cattle.birth_date or timezone.now().date(),
                    status=status
                )

        return cattle
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ไม่บังคับทุกฟิลด์
        for field in self.fields.values():
            field.required = False

# ------------------ HealthCheckForm ------------------
class HealthCheckForm(forms.ModelForm):
    status = forms.ChoiceField(choices=STATUS_CHOICES, label='สถานะ')

    class Meta:
        model = HealthCheck
        fields = ['check_date', 'temperature', 'heart_rate', 'weight', 'status', 'notes']
        widgets = {
            'check_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'หมายเหตุเพิ่มเติม'}),
        }

# ------------------ VaccinationForm ------------------
class VaccinationForm(forms.ModelForm):
    class Meta:
        model = Vaccination
        fields = ['vaccine_name', 'vaccine_date', 'next_due_date', 'doctor_name']
        widgets = {
            'vaccine_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อวัคซีน'}),
            'vaccine_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'next_due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'doctor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อผู้ฉีด/หมอ'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False   # 👈 ทำให้ทุกฟิลด์ optional


class FeedingRationForm(forms.ModelForm):
    class Meta:
        model = FeedingRation
        fields = ['ration_id', 'feeding_time', 'fresh_weight', 'dry_weight', 'supplement']
        labels = {
            'ration_id': 'Ration Name',
            'feeding_time': 'เวลาการให้อาหาร',
            'fresh_weight': 'น้ำหนักอาหารสด (กก.)',
            'dry_weight': 'น้ำหนักอาหารแห้ง (กก.)',
            'supplement': 'อาหารเสริม / พรีมิกซ์',
        }
        
        widgets = {
            'ration_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อสูตรอาหาร'}),
            'feeding_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'เช่น 07:30, 16:30 / น้ำสะอาดตลอดวัน'}),
            'fresh_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.01}),
            'dry_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.01}),
            'supplement': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'เช่น พรีมิกซ์แร่ธาตุ 80 กรัม/วัน'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False   # 👈 optional หมด


class CalendarEventInlineForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ['title', 'start', 'end', 'event_type', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อกิจกรรม'}),
            'start': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'หมายเหตุเพิ่มเติม'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False   # 👈 optional
