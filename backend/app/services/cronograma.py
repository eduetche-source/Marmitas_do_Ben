from datetime import datetime, timedelta
import pytz

# Configura o fuso horário oficial para evitar problemas em servidores na nuvem
BR_TIMEZONE = pytz.timezone("America/Sao_Paulo")

def obter_data_atual_br() -> datetime:
    """Retorna o datetime atual com o fuso horário de Brasília."""
    return datetime.now(BR_TIMEZONE)

def obter_ciclo_cardapio_atual() -> int:
    """
    Descobre qual cardápio mostrar (1 ou 2):
    - Se hoje for Segunda, Terça, Quarta ou Quinta: mostra o ciclo da semana ATUAL.
    - Se hoje for Sexta, Sábado ou Domingo: já mostra o ciclo da PRÓXIMA semana.
    """
    agora = obter_data_atual_br()
    
    # weekday(): Segunda = 0, Terça = 1, Quarta = 2, Quinta = 3, Sexta = 4, Sábado = 5, Domingo = 6
    dia_da_semana = agora.weekday()
    
    # Pegamos o número da semana no ano (de 1 a 53) para alternar de forma contínua
    semana_do_ano = agora.isocalendar()[1]
    
    # REGRA DE OURO: Se passou de Quinta-feira (dia 3), avança mentalmente para a próxima semana
    if dia_da_semana > 3:
        semana_do_ano += 1
        
    # Se a semana calculada for ímpar, retorna Ciclo 1. Se for par, retorna Ciclo 2.
    return 1 if semana_do_ano % 2 != 0 else 2

def calcular_data_entrega_pedido() -> datetime:
    """
    Calcula a data da entrega (Segunda-feira) com base na regra:
    - Pedidos de Segunda a Quinta -> Entrega na Segunda-feira da semana QUE VEM.
    - Pedidos de Sexta a Domingo -> Entrega na Segunda-feira da OUTRA semana.
    """
    agora = obter_data_atual_br()
    dia_da_semana = agora.weekday()
    
    if dia_da_semana <= 3:
        # Se for de Segunda a Quinta, entrega na segunda da próxima semana
        dias_ate_entrega = 7 - dia_da_semana
    else:
        # Se for de Sexta a Domingo, pula uma segunda e entrega na outra
        dias_ate_entrega = (7 - dia_da_semana) + 7
        
    data_entrega = agora + timedelta(days=dias_ate_entrega)
    
    # Retorna apenas o dia (zerando hora, minuto e segundo)
    return data_entrega.replace(hour=0, minute=0, second=0, microsecond=0)
