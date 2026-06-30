import random

from django.contrib.auth.models import User
from django.db import models


class EmojiEvento(models.TextChoices):
    CARTAS = '🃏', 'Cartas'
    TABULEIRO = '♟️', 'Tabuleiro'
    RPG = '🐉', 'RPG'
    ESPORTES = '🏸', 'Esportes'
    MUSICA = '🎸', 'Música'


# Naipes de baralho usados como decoração das cartas de evento.
# Espadas/Paus = preto · Copas/Ouros = vermelho (regra padrão do baralho).
NAIPES_EVENTO = ['♠', '♣', '♥', '♦']
NAIPES_VERMELHOS = ('♥', '♦')


class StatusEvento(models.TextChoices):
    PLANNING = 'PLANNING', 'Planejamento'
    WAITING = 'WAITING', 'Aguardando Jogadores'
    ONGOING = 'ONGOING', 'Em Andamento'
    CLOSED = 'CLOSED', 'Encerrado'


class Evento(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='eventos_criados')
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(null=True, blank=True)
    emoji = models.CharField(
        max_length=10, choices=EmojiEvento.choices, default=EmojiEvento.CARTAS)
    status = models.CharField(
        max_length=20, choices=StatusEvento.choices, default=StatusEvento.PLANNING)
    min_participantes = models.PositiveIntegerField(default=2)

    # Tornados opcionais para permitir votação posterior (Democracia Deliberativa)
    data_evento = models.DateTimeField(null=True, blank=True)
    local = models.CharField(max_length=200, null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.emoji} {self.titulo} ({self.get_status_display()})"

    @property
    def naipe(self):
        """Naipe de baralho (♠ ♣ ♥ ♦) atribuído aleatoriamente ao evento.

        Usa o id do evento como seed: o resultado é aleatório (não segue
        nenhum padrão nem depende do emoji), mas estável — o mesmo evento
        sempre mostra o mesmo naipe, em vez de sortear um novo a cada
        carregamento de página.
        """
        if self.id is None:
            return NAIPES_EVENTO[0]
        return random.Random(self.id).choice(NAIPES_EVENTO)

    @property
    def cor_naipe(self):
        return 'red' if self.naipe in NAIPES_VERMELHOS else 'black'


class Participante(models.Model):
    ROLE_CHOICES = [
        ('ORGANIZER', 'Organizador'),
        ('PLAYER', 'Jogador'),
    ]
    STATUS_CHOICES = [
        ('INTERESTED', 'Interessado'),
        ('CONFIRMED', 'Confirmado'),
    ]
    evento = models.ForeignKey(
        Evento, on_delete=models.CASCADE, related_name='participantes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='PLAYER')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='INTERESTED')
    pontos_acumulados = models.IntegerField(
        default=0)  # Memória e histórico do jogador

    class Meta:
        unique_together = ('evento', 'user')

# Sistema de Votação/Enquetes para Data e Local


class OpcaoVotacao(models.Model):
    TIPO_CHOICES = [('LOCAL', 'Local'), ('DATA', 'Data/Hora')]
    evento = models.ForeignKey(
        Evento, on_delete=models.CASCADE, related_name='opcoes_voto')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    # Ex: "Bloco A, Sala 102" ou "2026-06-15 14:00"
    valor = models.CharField(max_length=200)

    def total_votos(self):
        return self.votos.count()


class Voto(models.Model):
    opcao = models.ForeignKey(
        OpcaoVotacao, on_delete=models.CASCADE, related_name='votos')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('opcao', 'user')

# Chat Simples para as etapas de Waiting e Ongoing


class MensagemChat(models.Model):
    evento = models.ForeignKey(
        Evento, on_delete=models.CASCADE, related_name='mensagens')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

# Histórico de Rodadas e Consenso de Placar


class StatusRodada(models.TextChoices):
    PONTUACAO = 'PONTUACAO', 'Aguardando Pontuação'
    VOTACAO = 'VOTACAO', 'Em Votação'
    CONTESTADA = 'CONTESTADA', 'Contestada'
    APROVADA = 'APROVADA', 'Aprovada'


class Rodada(models.Model):
    evento = models.ForeignKey(
        Evento, on_delete=models.CASCADE, related_name='rodadas')
    numero = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20, choices=StatusRodada.choices,
        default=StatusRodada.PONTUACAO)


class PropostaPontuacao(models.Model):
    rodada = models.ForeignKey(
        Rodada, on_delete=models.CASCADE, related_name='propostas')
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE)
    pontos_ganhos = models.IntegerField()
    # Quem registrou esta proposta: o organizador na 1ª pontuação da rodada,
    # ou quem contestou, ao repropor uma nova pontuação.
    proposto_por = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='propostas_feitas')

    class Meta:
        unique_together = ('rodada', 'participante')


class VotoRodada(models.Model):
    rodada = models.ForeignKey(
        Rodada, on_delete=models.CASCADE, related_name='votos_validacao')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    concorda = models.BooleanField(default=True)

    class Meta:
        unique_together = ('rodada', 'user')