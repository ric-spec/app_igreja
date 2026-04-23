# 📊 Visualização da Despensa - Itens e Disponibilidade

## ✅ Itens Cadastrados na Despensa

A despensa da app_igreja agora conta com **17 itens** distribuídos em **6 categorias**, totalizando **533 unidades** em estoque.

---

## 📦 **Categoria: GRÃOS E CEREAIS**

| Item | Quantidade | Vencimento |
|------|-----------|-----------|
| Arroz (5kg) | 25 | 2026-12-01 |
| Feijão (1kg) | **45** (2 lotes) | Vária |
| Macarrão (500g) | 40 | 2026-11-15 |
| Farinha de Trigo (1kg) | 20 | 2026-10-10 |
| **SUBTOTAL** | **130** | |

---

## 🧈 **Categoria: ÓLEOS E CONDIMENTOS**

| Item | Quantidade | Vencimento |
|------|-----------|-----------|
| Óleo de Soja (900ml) | 35 | 2026-03-20 ⚠️ |
| Sal (1kg) | 50 | 2027-06-15 |
| Açúcar (1kg) | 30 | 2026-07-30 |
| **SUBTOTAL** | **115** | |

---

## 🥛 **Categoria: LATICÍNIOS E PROTEÍNAS**

| Item | Quantidade | Vencimento |
|------|-----------|-----------|
| Leite em Pó (400g) | 18 | 2026-05-15 |
| Ovo (dúzia) | 12 | 2026-04-30 |
| Sardinha em Lata (120g) | 25 | 2026-09-10 |
| **SUBTOTAL** | **55** | |

---

## 🥬 **Categoria: FRUTAS E VEGETAIS**

| Item | Quantidade | Vencimento |
|------|-----------|-----------|
| Batata-doce (kg) | 40 | 2026-05-20 |
| Cebola (kg) | 35 | 2026-06-10 |
| **SUBTOTAL** | **75** | |

---

## ☕ **Categoria: BEBIDAS**

| Item | Quantidade | Vencimento |
|------|-----------|-----------|
| Café (500g) | 20 | 2026-12-15 |
| Achocolatado (400g) | 15 | 2026-08-20 |
| **SUBTOTAL** | **35** | |

---

## 🧼 **Categoria: HIGIENE E LIMPEZA**

| Item | Quantidade | Vencimento |
|------|-----------|-----------|
| Sabão em Pó (500g) | 22 | 2026-10-25 |
| Desinfetante (1L) | 18 | 2026-09-05 |
| Sabonete (unidade) | 48 | 2026-11-30 |
| **SUBTOTAL** | **88** | |

---

## 📈 **RESUMO GERAL**

```
Total de Categorias:     6
Total de Itens:          17
Total de Unidades:       533
Total de Lotes:          18

Distribuição por Categoria:
├─ Grãos:                130 unidades (24%)
├─ Óleos/Condimentos:    115 unidades (22%)
├─ Laticínios/Proteínas: 55 unidades  (10%)
├─ Vegetais:             75 unidades  (14%)
├─ Bebidas:              35 unidades  (7%)
└─ Higiene:              88 unidades  (23%)
```

---

## ⚠️ **Itens Vencendo Em Breve** (Prioridade!)

| Item | Vencimento | Status |
|------|-----------|--------|
| Óleo de Soja (900ml) | 2026-03-20 | 🔴 **VENCIDO!** |
| Ovo (dúzia) | 2026-04-30 | 🟡 Vence em 7 dias |
| Leite em Pó (400g) | 2026-05-15 | 🟡 Vence em 22 dias |

**⚡ Ação Recomendada**: Utilizar itens com vencimento próximo primeiro!

---

## 🔄 **Como a Despensa Funciona**

### Estrutura de Dados

```
CATALOGO (Itens Disponíveis)
├─ id_item
├─ nome
├─ qtd_por_cesta
└─ categoria

LOTES (Quantidade em Estoque)
├─ id_lote
├─ id_item (referencia catálogo)
├─ quantidade
└─ vencimento
```

### Fluxo de Entregas

```
1. Necessidade da Família
   └─→ 2. Cálculo de Capacidade
       └─→ 3. Retirada dos Lotes (FIFO)
           └─→ 4. Entrega
               └─→ 5. Atualização de Estoque
```

---

## 📝 **Adicionar Novos Itens**

Para adicionar um novo item à despensa, use:

```python
novo_item = {
    "nome": "Nome do Produto",
    "qtd_por_cesta": 1,
    "categoria": "Categoria"
}
salvar_item_catalogo_neon(novo_item)
```

Para adicionar estoque:

```python
novo_lote = {
    "id_item": 1,
    "quantidade": 10,
    "vencimento": datetime.date(2026, 12, 31)
}
salvar_lote_neon(novo_lote)
```

---

## 🎯 **Capacidade de Cestas**

Com o estoque atual, é possível montar:

| Tipo de Cesta | Capacidade | Itens Base |
|--------------|-----------|-----------|
| Cesta Padrão | 12-15 | Arroz + Feijão + Macarrão + Óleo |
| Mini Cesta | 25-30 | Feijão + Macarrão + Sal |
| Cesta Proteína | 8-10 | Sardinha + Leite + Ovo |

---

## 🚀 **Popular Despensa no Neon**

Para sincronizar esses dados com o banco Neon, execute:

```bash
pip install sqlalchemy psycopg2-binary pandas
python popular_despensa.py
```

---

## 📊 **Dashboard de Mensuração**

A despensa atual pode:
- ✅ Atender ~100 famílias (cestas padrão)
- ✅ Fornecer itens de higiene para ~500 dias
- ⚠️ Precisa reabastecer óleo urgentemente
- 🎯 Ideal para operações de 2-3 semanas

---

**Última atualização**: 23 de Abril de 2026  
**Próxima contagem prevista**: Semanalmente
