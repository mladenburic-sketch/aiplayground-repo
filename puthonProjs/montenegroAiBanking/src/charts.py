import plotly.graph_objects as go

def plot_income_pie(bank_row, mapping):
    """
    Crta pie chart za prihode banke.
    
    Args:
        bank_row: Red sa podacima banke
        mapping: MAPPING dictionary sa nazivima pozicija
    """
    # Kategorije prihoda
    income_categories = {
        'Prihodi od Kamata': mapping.get('prihodi_kamata'),
        'Prihodi od Naknada': mapping.get('prihodi_naknada'),
        'Ostali Prihodi': mapping.get('ostali_prihodi'),
        'Kursne Razlike': mapping.get('kursne_razlike')
    }
    
    labels = []
    values = []
    
    for label, col_name in income_categories.items():
        if col_name and col_name in bank_row:
            value = bank_row[col_name]
            if value > 0:  # Samo pozitivne vrednosti
                labels.append(label)
                values.append(value)
    
    if not values:
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>€ %{value:,.0f}',
        hovertemplate='<b>%{label}</b><br>€ %{value:,.0f}<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title="Struktura Prihoda (iznosi u hiljadama €)",
        height=700,
        margin=dict(t=100, b=100, l=100, r=100)
    )
    
    return fig

def plot_expense_pie(bank_row, mapping):
    """
    Crta pie chart za rashode banke.
    
    Args:
        bank_row: Red sa podacima banke
        mapping: MAPPING dictionary sa nazivima pozicija
    """
    # Kategorije rashoda
    expense_categories = {
        'Rashodi od Kamata': mapping.get('rashodi_kamata'),
        'Rashodi Naknada': mapping.get('rashodi_naknada'),
        'Troškovi Zaposlenih': mapping.get('troskovi_zaposlenih'),
        'Amortizacija': mapping.get('amortizacija'),
        'Admin Troškovi': mapping.get('admin_troskovi'),
        'Ostali Rashodi': mapping.get('ostali_rashodi'),
        'Rezervisanja': mapping.get('rezervisanja')
    }
    
    labels = []
    values = []
    
    for label, col_name in expense_categories.items():
        if col_name and col_name in bank_row:
            value = abs(bank_row[col_name])  # Apsolutna vrednost za rashode
            if value > 0:  # Samo pozitivne vrednosti
                labels.append(label)
                values.append(value)
    
    if not values:
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>€ %{value:,.0f}',
        hovertemplate='<b>%{label}</b><br>€ %{value:,.0f}<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title="Struktura Rashoda (iznosi u hiljadama €)",
        height=700,
        margin=dict(t=100, b=100, l=100, r=100)
    )
    
    return fig

def plot_profit_comparison(current_profit, new_profit):
    """
    Crta jednostavan bar chart sa dva bara: stvarni prihod i prihod nakon izmjena.
    
    Args:
        current_profit: Trenutna neto dobit
        new_profit: Neto dobit nakon izmjena
    """
    fig = go.Figure()
    
    # Dodajemo dva bara
    fig.add_trace(go.Bar(
        x=['Trenutna Neto Dobit', 'Nova Neto Dobit'],
        y=[current_profit, new_profit],
        marker_color=['#636EFA', '#00CC96'],
        text=[f"€ {current_profit:,.0f}", f"€ {new_profit:,.0f}"],
        textposition='outside',
        textfont=dict(size=12, color='black')
    ))
    
    # Ažuriranje layout-a
    fig.update_layout(
        title="Poređenje Neto Dobiti (iznosi u hiljadama €)",
        xaxis_title="",
        yaxis_title="Iznos (hiljade €)",
        yaxis=dict(tickformat=",.0f"),
        height=500,
        showlegend=False,
        margin=dict(t=60, b=60, l=60, r=60)
    )
    
    return fig

def plot_waterfall(start_value, changes_dict, final_value_name="Nova Dobit"):
    """
    Crta Waterfall grafik.
    start_value: Početna neto dobit.
    changes_dict: Dictionary sa promjenama {'Ušteda Admin': 500, 'Rast Naknada': 200...}
    """
    
    # Priprema podataka za Plotly
    labels = ["Trenutna Dobit"] + list(changes_dict.keys()) + [final_value_name]
    
    # Vrijednosti (početna, pa promjene...)
    values = [start_value] + list(changes_dict.values())
    
    # Za waterfall nam trebaju relativne promjene, ali zadnja kolona je total
    # Plotly traži da definišemo tip stuba (relative vs total)
    measure = ["relative"] * (len(values))
    measure[-1] = "total" # Zadnji stub je total
    
    # Moramo izračunati finalnu sumu za zadnji stub
    final_sum = start_value + sum(changes_dict.values())
    values.append(final_sum) # Dodajemo finalni iznos na kraj liste vrijednosti
    
    # Plotly Waterfall logika je malo specifična, on traži 'y' kao promjene
    # Za prvi stub (Trenutna) y je iznos. Za zadnji (Nova) y je 0 (jer je total computed).
    # Ali jednostavnije je ovako:
    
    x_data = labels
    y_data = [start_value] + list(changes_dict.values()) + [final_sum]
    measure_data = ["absolute"] + ["relative"] * len(changes_dict) + ["total"]

    fig = go.Figure(go.Waterfall(
        name = "Simulacija", orientation = "v",
        measure = measure_data,
        x = x_data,
        textposition = "outside",
        text = [f"{v/1000:.1f}m" if abs(v) > 1000 else f"{v:.0f}k" for v in y_data],
        y = y_data,
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
        decreasing = {"marker":{"color":"#EF553B"}},
        increasing = {"marker":{"color":"#00CC96"}},
        totals = {"marker":{"color":"#636EFA"}}
    ))

    fig.update_layout(
        title = "Efekat preporuka na Neto Dobit",
        waterfallgap = 0.3,
        height=450
    )
    
    return fig