from django.shortcuts import render

from .models import AcademicYearEntry


def history(request):
    academic_years = AcademicYearEntry.objects.filter().order_by('academic_year')
    return render(request, 'history/history.html', context={'academic_years': academic_years})
