from django.urls import path
from . import views

urlpatterns = [
    path('reservar/<int:veiculo_id>/', views.reservar_veiculo, name='reservar_veiculo'),
    path('listar/', views.listar_reservas, name='listar_reservas'),
    path('registrar_devolucao/<int:reserva_id>/', views.registrar_devolucao_veiculo, name='registrar_devolucao_veiculo'),
    path('registrar_retirada/<int:reserva_id>/', views.registrar_retirada, name='registrar_retirada'),
    path('historico/', views.historico_reservas_cliente, name='historico_reservas_cliente'),
    path('editar/<int:reserva_id>/', views.editar_reserva, name='editar_reserva'),
    path('excluir/<int:reserva_id>/', views.excluir_reserva, name='excluir_reserva'),


]

