from django.contrib import admin
from .models import Interest, Skill, StudentProfile, StudentSkill, Education


class StudentSkillInline(admin.TabularInline):
    model = StudentSkill
    extra = 1


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'grade_or_class', 'school_or_college', 'gender', 'created_at')
    search_fields = ('user__username', 'user__email', 'school_or_college')
    list_filter = ('gender', 'grade_or_class')
    inlines = [EducationInline, StudentSkillInline]


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('student_profile', 'institution_name', 'degree_or_level', 'start_year', 'end_year')
    search_fields = ('institution_name', 'student_profile__user__username')


@admin.register(StudentSkill)
class StudentSkillAdmin(admin.ModelAdmin):
    list_display = ('student_profile', 'skill', 'proficiency')
    list_filter = ('proficiency',)
