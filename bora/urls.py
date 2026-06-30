from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',  views.tela_inicial),
    path('evento', views.lista_eventos, name='evento'),
    path('evento/criar-evento', views.criar_evento),
    path('evento/<int:evento_id>', views.detalhe_evento, name='detalhe_evento'),

    # Interações do Fluxo MVP
    path('evento/<int:evento_id>/interesse',
         views.demonstrar_interesse, name='demonstrar_interesse'),
    path('evento/<int:evento_id>/sugerir',
         views.sugerir_opcao, name='sugerir_opcao'),
    path('opcao/<int:opcao_id>/votar', views.votar_enquete, name='votar_enquete'),
    path('evento/<int:evento_id>/fechar-planejamento',
         views.fechar_planejamento, name='fechar_planejamento'),
    path('evento/<int:evento_id>/chat',
         views.enviar_mensagem, name='enviar_mensagem'),
    path('evento/<int:evento_id>/rodada',
         views.gerenciar_rodada, name='gerenciar_rodada'),
    path('rodada/<int:rodada_id>/validar',
         views.votar_placar_rodada, name='votar_placar_rodada'),
    path('evento/<int:evento_id>/encerrar',
         views.encerrar_evento, name='encerrar_evento'),
    path('evento/<int:evento_id>/excluir',
         views.excluir_evento, name='excluir_evento'),

    path('perfil', views.perfil_usuario, name='perfil'),
    path('entrar', views.login_view, name='login'),
    path('cadastro', views.cadastro_view, name='cadastro'),
    path('sair', views.logout_view, name='logout'),
]