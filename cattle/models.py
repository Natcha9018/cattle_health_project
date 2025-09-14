from django.db import models


STATUS_CHOICES = [
    ('healthy', 'ปกติ'),
    ('sick', 'ป่วย'),
    ('forsale', 'พร้อมขาย'),
]

class Cattle(models.Model):
    tag_no = models.CharField(max_length=50, unique=True)  # AnimalID
    name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'ตัวผู้'), ('female', 'ตัวเมีย')]
    )
    breed = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)  # ประเภท (โคนม, โคสาว, โคขุน)
    housing = models.CharField(max_length=100, blank=True, null=True)   # คอก/โรงเรือน

    birth_date = models.DateField(blank=True, null=True)
    mother = models.CharField(max_length=50, blank=True, null=True)
    father = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.tag_no} - {self.name or 'Unnamed'}"


class FeedingRation(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name="rations")
    ration_id = models.CharField(max_length=50)  # เช่น FTMR-1, FTMR-2
    feeding_time = models.CharField(max_length=100)  # เช่น "07:30, 16:30 / น้ำสะอาดตลอดวัน"
    fresh_weight = models.DecimalField(max_digits=5, decimal_places=2)  # ปริมาณอาหารสด (กก.)
    dry_weight = models.DecimalField(max_digits=5, decimal_places=2)    # ปริมาณอาหารแห้ง (กก.)
    supplement = models.TextField(blank=True, null=True)  # เช่น "พรีมิกซ์แร่ธาตุ-วิตามิน 80 กรัม/วัน"

    def __str__(self):
        return f"{self.ration_id} for {self.cattle.tag_no}"
    
class HealthCheck(models.Model):  
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='healthchecks')
    check_date = models.DateField()
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    # 👇 เพิ่มตรงนี้
    status = models.CharField(
        max_length=20,
        choices=[('healthy', 'ปกติ'), ('sick', 'ป่วย'), ('forsale', 'พร้อมขาย')],
        default='healthy'
    )

    class Meta:
        ordering = ['-check_date']

    def __str__(self):
        return f"Health {self.cattle.tag_no} on {self.check_date}"
    
class Treatment(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='treatments')
    diagnosis = models.CharField(max_length=255)
    treatment_date = models.DateField()
    medication = models.CharField(max_length=255, blank=True, null=True)
    doctor_name = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Treatment {self.cattle.tag_no} on {self.treatment_date}"


class Vaccination(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='vaccinations')
    vaccine_name = models.CharField(max_length=100)
    vaccine_date = models.DateField()
    next_due_date = models.DateField(blank=True, null=True)
    doctor_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Vaccine {self.vaccine_name} for {self.cattle.tag_no}"


class Notification(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(
        max_length=50,
        choices=[
            ('vaccine', 'Vaccine'),
            ('checkup', 'Checkup'),
            ('weight', 'Weight'),
            ('other', 'Other'),
        ]
    )
    message = models.TextField()
    notify_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('done', 'Done')],
        default='pending'
    )

    def __str__(self):
        return f"Notification {self.type} for {self.cattle.tag_no}"


class Report(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='reports')
    report_date = models.DateField(auto_now_add=True)
    content = models.TextField()

    def __str__(self):
        return f"Report {self.cattle.tag_no} - {self.report_date}"

class CalendarEvent(models.Model):
    EVENT_TYPES = [
        ('feeding', 'การให้อาหาร'),
        ('health', 'การรักษา'),
        ('breeding', 'ผสมพันธุ์'),
        ('other', 'อื่นๆ'),
    ]

    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.cattle.tag_no})"
    
