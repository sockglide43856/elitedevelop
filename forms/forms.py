from django import forms
from datetime import date, timedelta

from django import forms
from datetime import date, timedelta
from .models import Reservation

from datetime import date, timedelta

def generate_available_slots():
    start_date = date(2026, 9, 1)
    end_date = date(2027, 4, 29)
    slots = []

    # 1. Fetch already booked dates (ensuring they match date objects or strings)
    booked_dates = set(Reservation.objects.values_list('booked_date', flat=True))

    # 2. Define 2026-2027 school breaks & holidays
    excluded_ranges = [
        # Labor Day
        (date(2026, 9, 7), date(2026, 9, 7)),
        # Fall Break
        (date(2026, 10, 15), date(2026, 10, 16)),
        # Thanksgiving Break
        (date(2026, 11, 25), date(2026, 11, 27)),
        # Winter Break
        (date(2026, 12, 21), date(2027, 1, 1)),
        # Martin Luther King Jr. Day
        (date(2027, 1, 18), date(2027, 1, 18)),
        # Washington & Presidents' Day
        (date(2027, 2, 15), date(2027, 2, 15)),
        # Spring Break
        (date(2027, 3, 29), date(2027, 4, 2))
    ]

    # 3. Flatten ranges into a set of unique restricted dates for fast O(1) lookup
    break_dates = set()
    for start_break, end_break in excluded_ranges:
        delta = end_break - start_break
        for i in range(delta.days + 1):
            break_dates.add(start_break + timedelta(days=i))

    # 4. Generate available slots
    current_date = start_date
    while current_date <= end_date:
        # Check weekday, reservation status, and school break schedule
        if (current_date.weekday() < 5
                and current_date not in booked_dates
                and current_date not in break_dates):

            date_value = current_date.isoformat()
            date_display = current_date.strftime('%A, %b %d, %Y (4:30 PM - 5:30 PM)')
            slots.append((date_value, date_display))

        current_date += timedelta(days=1)

    return slots



class TutoringReservationForm(forms.Form):
    # Parent Information
    parent_first_name = forms.CharField(max_length=100, label="Parent's First Name")
    parent_last_name = forms.CharField(max_length=100, label="Parent's Last Name")
    parent_email = forms.EmailField(label="Parent's Email Address")
    parent_phone = forms.CharField(max_length=20, label="Parent's Phone Number")

    # Child Information
    child_first_name = forms.CharField(max_length=100, label="Child's First Name")
    child_last_name = forms.CharField(max_length=100, label="Child's Last Name")
    child_grade = forms.CharField(max_length=50, label="Child's Grade Level", required=False)

    selected_slots = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        label="Select Tutoring Sessions ($15.00 each)",
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only load slots that are still available
        self.fields['selected_slots'].choices = generate_available_slots()