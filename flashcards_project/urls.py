from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from cards import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.practice, name='practice'),
    path('learn/', views.learn, name='learn'),  # новая страница заучивания
    path('next_learn_card/', views.next_learn_card, name='next_learn_card'),
    path('get_group1_cards/', views.get_group1_cards, name='get_group1_cards'),
    path('check/', views.check_answer, name='check_answer'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)