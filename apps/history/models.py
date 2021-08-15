import datetime

from django.db import models


def get_year_choices():
    # Get all the years between now and 1997, when the society was founded.
    return [(r, r) for r in range(1997, datetime.date.today().year + 1)]


# This model represents an academic year. I
class AcademicYearEntry(models.Model):
    academic_year = models.IntegerField('Academic year starting in', choices=get_year_choices(),
                                        default=datetime.date.today().year)

    title = models.CharField(max_length=110, blank=True)

    history = models.TextField()

    def __str__(self):
        return 'Academic year {0}/{1}'.format(self.academic_year, self.academic_year + 1)

    class Meta:
        verbose_name_plural = 'Academic Year Entries'


# Unlike aniMango, exec entries are not linked to any particular account. This is because this model is now used for
# both exec who were exec after 2016 (when aniMango was made) and before 2016, therefore not all exec will have an
# account.
class ExecEntry(models.Model):
    related_academic_year = models.ForeignKey(AcademicYearEntry, null=False, blank=False,
                                              on_delete=models.CASCADE)
    exec_name = models.CharField(max_length=30)
    exec_role = models.CharField(max_length=30)

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.exec_name, self.exec_role, self.related_academic_year)
