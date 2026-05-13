"""Module for anonymizing F1 team and driver data with Brazilian cultural references."""

ANON_TEAM_MAPPING = {
    "Red Bull Racing": "Recife Racing",
    "McLaren": "BEAT Scuderia",
    "Williams": "Porto Digital",
    "Ferrari": "Capibaribe Scuderia",
    "Mercedes": "Boa Viagem Motors",
    "Aston Martin": "Olinda Martin",
    "Racing Bulls": "Rio Doce Rats",
    "Haas F1 Team": "Ibura Scuderia",
    "Alpine": "Janga Rats",
    "Kick Sauber": "Abreu e Sauber",
}

ANON_TEAM_PALETTE = {
    "Recife Racing": "#CC0000",
    "BEAT Scuderia": "#FF8700",
    "Porto Digital": "#005AFF",
    "Capibaribe Scuderia": "#2DA84E",
    "Boa Viagem Motors": "#9467BD",
    "Olinda Martin": "#ffffff",
    "Rio Doce Rats": "#E377C2",
    "Ibura Scuderia": "#7F7F7F",
    "Janga Rats": "#BCBD22",
    "Abreu e Sauber": "#17BECF",
}

ANON_DRIVER_MAPPING = {
    # Red Bull
    "VER": "Rafael Camara",
    "TSU": "Mestre Vitalino",
    # McLaren
    "NOR": "Chico Science",
    "PIA": "Rivaldo",
    # Ferrari
    "LEC": "Alceu Valença",
    "HAM": "Reginaldo Rossi",
    # Williams
    "SAI": "Paulo Freire",
    "ALB": "João Cabral",
    # Mercedes
    "RUS": "Capiba",
    "ANT": "Lampião",
    # Aston Martin
    "ALO": "Ariano Suassuna",
    "STR": "Francisco Brennand",
    # RB
    "LAW": "Manuel Bandeira",
    "HAD": "Luiz Gonzaga",
    # Haas
    "BEA": "Lenine",
    "OCO": "Antônio Carlos",
    # Alpine
    "GAS": "Lia",
    "COL": "Abelardo da Hora",
    # Kick Sauber
    "HUL": "Duarte Coelho",
    "BOR": "Frei Caneca",
}

ANON_DRIVER_TO_ABBR = {
    name: name.split()[-1][:3].upper() for _, name in ANON_DRIVER_MAPPING.items()
}
