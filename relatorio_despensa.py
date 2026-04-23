# Relatório Visual de Disponibilidade da Despensa
# Exiba este conteúdo no Streamlit ou visualize no terminal

import pandas as pd
import datetime

# Dados do Catálogo
catalogo = [
    # Grãos
    {"id": 1, "nome": "Arroz (5kg)", "categoria": "🌾 Grãos", "cesta": 1},
    {"id": 2, "nome": "Feijão (1kg)", "categoria": "🌾 Grãos", "cesta": 2},
    {"id": 3, "nome": "Macarrão (500g)", "categoria": "🌾 Grãos", "cesta": 2},
    {"id": 4, "nome": "Farinha de Trigo (1kg)", "categoria": "🌾 Grãos", "cesta": 1},
    # Óleos
    {"id": 5, "nome": "Óleo de Soja (900ml)", "categoria": "🧈 Óleos", "cesta": 1},
    {"id": 6, "nome": "Sal (1kg)", "categoria": "🧂 Condimentos", "cesta": 1},
    {"id": 7, "nome": "Açúcar (1kg)", "categoria": "🍬 Condimentos", "cesta": 1},
    # Proteínas
    {"id": 8, "nome": "Leite em Pó (400g)", "categoria": "🥛 Laticínios", "cesta": 1},
    {"id": 9, "nome": "Ovo (dúzia)", "categoria": "🥚 Proteínas", "cesta": 1},
    {"id": 10, "nome": "Sardinha em Lata (120g)", "categoria": "🐟 Proteínas", "cesta": 1},
    # Vegetais
    {"id": 11, "nome": "Batata-doce (kg)", "categoria": "🥔 Vegetais", "cesta": 1},
    {"id": 12, "nome": "Cebola (kg)", "categoria": "🧅 Vegetais", "cesta": 1},
    # Bebidas
    {"id": 13, "nome": "Café (500g)", "categoria": "☕ Bebidas", "cesta": 1},
    {"id": 14, "nome": "Achocolatado (400g)", "categoria": "🍫 Bebidas", "cesta": 1},
    # Higiene
    {"id": 15, "nome": "Sabão em Pó (500g)", "categoria": "🧼 Higiene", "cesta": 1},
    {"id": 16, "nome": "Desinfetante (1L)", "categoria": "💨 Limpeza", "cesta": 1},
    {"id": 17, "nome": "Sabonete (unidade)", "categoria": "🧴 Higiene", "cesta": 1},
]

# Dados de Estoque
estoque = [
    {"id": 1, "item_id": 1, "qtd": 25, "venc": "2026-12-01"},
    {"id": 2, "item_id": 2, "qtd": 30, "venc": "2026-08-15"},
    {"id": 3, "item_id": 2, "qtd": 15, "venc": "2026-09-20"},
    {"id": 4, "item_id": 3, "qtd": 40, "venc": "2026-11-15"},
    {"id": 5, "item_id": 4, "qtd": 20, "venc": "2026-10-10"},
    {"id": 6, "item_id": 5, "qtd": 35, "venc": "2026-03-20"},
    {"id": 7, "item_id": 6, "qtd": 50, "venc": "2027-06-15"},
    {"id": 8, "item_id": 7, "qtd": 30, "venc": "2026-07-30"},
    {"id": 9, "item_id": 8, "qtd": 18, "venc": "2026-05-15"},
    {"id": 10, "item_id": 9, "qtd": 12, "venc": "2026-04-30"},
    {"id": 11, "item_id": 10, "qtd": 25, "venc": "2026-09-10"},
    {"id": 12, "item_id": 11, "qtd": 40, "venc": "2026-05-20"},
    {"id": 13, "item_id": 12, "qtd": 35, "venc": "2026-06-10"},
    {"id": 14, "item_id": 13, "qtd": 20, "venc": "2026-12-15"},
    {"id": 15, "item_id": 14, "qtd": 15, "venc": "2026-08-20"},
    {"id": 16, "item_id": 15, "qtd": 22, "venc": "2026-10-25"},
    {"id": 17, "item_id": 16, "qtd": 18, "venc": "2026-09-05"},
    {"id": 18, "item_id": 17, "qtd": 48, "venc": "2026-11-30"},
]

def gerar_relatorio_texto():
    """Gera relatório em formato texto para exibição"""
    
    df_cat = pd.DataFrame(catalogo)
    df_est = pd.DataFrame(estoque)
    
    # Agrupa estoque por item
    disponibilidade = df_est.groupby('item_id')['qtd'].sum().reset_index()
    disponibilidade.columns = ['id', 'total']
    
    # Junta com catálogo
    resultado = pd.merge(df_cat, disponibilidade, on='id')
    
    texto = "\n"
    texto += "╔" + "═" * 78 + "╗\n"
    texto += "║" + " " * 78 + "║\n"
    texto += "║" + "  📦 RELATÓRIO DE DISPONIBILIDADE DA DESPENSA".center(78) + "║\n"
    texto += "║" + f"  App Igreja - {datetime.date.today().strftime('%d/%m/%Y')}".center(78) + "║\n"
    texto += "║" + " " * 78 + "║\n"
    texto += "╚" + "═" * 78 + "╝\n\n"
    
    # Por categoria
    categorias = resultado['categoria'].unique()
    total_itens = 0
    total_unidades = 0
    
    for categoria in sorted(categorias):
        items = resultado[resultado['categoria'] == categoria].sort_values('nome')
        texto += f"\n{categoria}\n"
        texto += "─" * 80 + "\n"
        
        for _, item in items.iterrows():
            status = ""
            if item['total'] < 5:
                status = "🔴 CRÍTICO"
            elif item['total'] < 15:
                status = "🟡 BAIXO"
            else:
                status = "🟢 OK"
            
            texto += f"  {item['nome']:<45} {item['total']:>4} unid.  {status}\n"
            total_itens += 1
            total_unidades += item['total']
    
    # Resumo
    texto += "\n" + "=" * 80 + "\n"
    texto += "📊 RESUMO GERAL\n"
    texto += "=" * 80 + "\n"
    texto += f"  Total de Itens Únicos:        {total_itens}\n"
    texto += f"  Total de Unidades em Estoque: {total_unidades}\n"
    texto += f"  Total de Lotes:              {len(df_est)}\n"
    texto += "\n"
    
    # Capacidade
    texto += "🎁 CAPACIDADE DE ENTREGAS\n"
    texto += "-" * 80 + "\n"
    
    # Cesta 1: Arroz + Feijão + Macarrão + Óleo
    cesta_padrão = min(
        int(resultado[resultado['id'] == 1]['total'].values[0] / 1),
        int(resultado[resultado['id'] == 2]['total'].values[0] / 2),
        int(resultado[resultado['id'] == 3]['total'].values[0] / 2),
        int(resultado[resultado['id'] == 5]['total'].values[0] / 1),
    )
    texto += f"  Cesta Padrão (Arroz+Feijão+Macarrão+Óleo):  {cesta_padrão} cestas possíveis\n"
    
    # Cesta 2: Feijão + Macarrão + Sal
    cesta_mini = min(
        int(resultado[resultado['id'] == 2]['total'].values[0] / 2),
        int(resultado[resultado['id'] == 3]['total'].values[0] / 2),
        int(resultado[resultado['id'] == 6]['total'].values[0] / 1),
    )
    texto += f"  Mini Cesta (Feijão+Macarrão+Sal):          {cesta_mini} cestas possíveis\n"
    
    texto += "\n"
    
    # Vencimentos
    texto += "⏰ PRODUTOS COM VENCIMENTO PRÓXIMO\n"
    texto += "-" * 80 + "\n"
    
    hoje = datetime.date.today()
    df_est['venc_date'] = pd.to_datetime(df_est['venc']).dt.date
    df_est_ord = df_est.sort_values('venc_date')
    
    items_vencimento = []
    for _, lote in df_est_ord.iterrows():
        dias = (lote['venc_date'] - hoje).days
        if dias < 30:
            item = resultado[resultado['id'] == lote['item_id']]['nome'].values[0]
            items_vencimento.append((item, lote['venc_date'], dias, lote['qtd']))
    
    if items_vencimento:
        for item, venc, dias, qtd in items_vencimento:
            if dias < 0:
                emoji = "🔴"
                status = "VENCIDO"
            elif dias < 7:
                emoji = "🔴"
                status = "URGENTE"
            else:
                emoji = "🟡"
                status = "EM BREVE"
            texto += f"  {emoji} {item:<40} {venc} ({dias} dias) - {qtd} unid. ({status})\n"
    else:
        texto += "  ✅ Todos os produtos com vencimento OK!\n"
    
    texto += "\n" + "=" * 80 + "\n"
    
    return texto

def exibir_no_streamlit():
    """Função para exibir no Streamlit (se necessário)"""
    import streamlit as st
    
    relatorio = gerar_relatorio_texto()
    st.text(relatorio)

if __name__ == "__main__":
    relatorio = gerar_relatorio_texto()
    print(relatorio)
    
    # Também salva em arquivo
    with open('relatorio_despensa_atual.txt', 'w', encoding='utf-8') as f:
        f.write(relatorio)
    print("✅ Relatório salvo em: relatorio_despensa_atual.txt")
