from django.contrib import admin
from rental.models import Student, Play, Game, Sanction, Image, Notice, Material, OwedMaterial

# Register your models here.
admin.site.register(Student)
admin.site.register(Play)
admin.site.register(Game)
admin.site.register(Sanction)
admin.site.register(Image)
admin.site.register(Notice)
admin.site.register(Material)
admin.site.register(OwedMaterial)
