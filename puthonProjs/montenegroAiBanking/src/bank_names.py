"""
Mapiranje kodova banaka u njihove prave nazive.
Dodaj stvarne nazive banaka ovde.
"""

# Mapiranje: kod_banke -> puni_naziv_banke
BANK_NAMES = {
    # TODO: Dodaj stvarne nazive banaka ovde
    # Primer:
     'adr': 'Adriatic Banka',
     'ckb': 'Crnogorska Komercijalna Banka',
     'prv': 'Prva Banka Crne Gore',
     'hip': 'Hipotekarna Banka',
     'adk': 'Addiko Banka',
     'ers': 'Erste Banka',
     'lov': 'Lovćen Banka',
     'nlb': 'NLB Banka',
     'ucb': 'Universal Capital Banka',
     'zap': 'Zapad Banka',
     'zir': 'Ziraat Banka',
}

def get_bank_name(bank_code: str) -> str:
    """
    Vraća puni naziv banke za dati kod.
    Ako naziv ne postoji u mapiranju, vraća kod.
    
    Args:
        bank_code: Kod banke (npr. 'ckb', 'atl')
    
    Returns:
        Puni naziv banke ili kod ako naziv ne postoji
    """
    # Konvertujemo u lowercase za pretragu jer su ključevi u BANK_NAMES lowercase
    bank_code_lower = bank_code.lower()
    return BANK_NAMES.get(bank_code_lower, bank_code.upper())

def get_bank_code(bank_name: str) -> str:
    """
    Vraća kod banke za dati puni naziv.
    Ako kod ne postoji, vraća naziv.
    
    Args:
        bank_name: Puni naziv banke
    
    Returns:
        Kod banke ili naziv ako kod ne postoji
    """
    # Traži kod po nazivu
    for code, name in BANK_NAMES.items():
        if name == bank_name:
            return code
    return bank_name

def get_all_bank_names() -> dict:
    """
    Vraća sve mapiranje kodova u nazive.
    
    Returns:
        Dictionary sa mapiranjem kod -> naziv
    """
    return BANK_NAMES.copy()

