from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
import json
from .models import FormConfiguration, FormField, FormSubmission, FieldResponse

def formHome(request):
    return render(request, 'formCode.html')

@login_required
def create_form_view(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled Form')
        description = request.POST.get('description', '')
        custom_code = request.POST.get('custom_code', '').strip()
        fields_json = request.POST.get('fields_data', '[]')

        if custom_code and FormConfiguration.objects.filter(code=custom_code.upper()).exists():
            return HttpResponse("That custom code is already taken!", status=400)

        try:
            fields_data = json.loads(fields_json)
        except json.JSONDecodeError:
            return HttpResponse("Bad data payload.", status=400)

        new_form = FormConfiguration.objects.create(
            creator=request.user,
            title=title,
            description=description,
            code=custom_code
        )

        for index, field in enumerate(fields_data):
            FormField.objects.create(
                form=new_form,
                label=field['label'],
                field_type=field['type'],
                is_required=field.get('required', True),
                order=index
            )

        return render(request, 'form_created.html', {'form': new_form})

    return render(request, 'builder.html')

@login_required
def user_dashboard(request):
    forms = request.user.my_forms.all()
    return render(request, 'dashboard.html', {'forms': forms})

@login_required
def view_responses(request, code, secret_token):
    # Fixed query matching structure safely
    form_config = get_object_or_404(
        FormConfiguration,
        code=code.strip().upper(),
        creator=request.user,
        secret_token=secret_token.strip().upper()
    )

    fields = form_config.fields.all()
    submissions_data = []

    # Corrected clean query formatting structure
    for sub in form_config.submissions.all().order_by('-submitted_at'):
        answers = {resp.field_id: resp.answer for resp in sub.responses.all()}
        row = {
            'submitted_at': sub.submitted_at,
            'answers': [answers.get(field.id, '') for field in fields]
        }
        submissions_data.append(row)

    context = {
        'config': form_config,
        'fields': fields,
        'submissions': submissions_data
    }
    return render(request, 'responses.html', context)

def serve_dynamic_form(request, code):
    form_config = get_object_or_404(FormConfiguration, code=code.strip().upper())
    fields = form_config.fields.all()

    if request.method == 'POST':
        # Safely capture the submission event instance
        submission = FormSubmission.objects.create(form=form_config)

        for field in fields:
            input_name = f"field_{field.id}"

            # Match browser check box conditions perfectly
            if field.field_type == 'checkbox':
                answer = 'Yes' if request.POST.get(input_name) else 'No'
            else:
                answer = request.POST.get(input_name, '').strip()

            FieldResponse.objects.create(
                submission=submission,
                field=field,
                answer=answer
            )
        return render(request, 'success.html')

    return render(request, 'dynamic_form.html', {'config': form_config, 'fields': fields})