from django.urls import path
from consoles.api import views



urlpatterns = [
    path("consoles/", views.ConsoleAV.as_view(), name='console-list'),
    path('consoles/<slug:slug>/', views.ConsoleDetailAV.as_view(), name='console-detail'),
    path('manufacturers/', views.ManufacturerAV.as_view(), name='manufacturer-list'),
    path('manufacturers/<slug:slug>/', views.ManufacturerDetailAV.as_view(), name='manufacturer-detail')

]