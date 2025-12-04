import google.generativeai as genai

def _get_available_model(api_key):
    """Pronalazi prvi dostupan model koji podržava generateContent."""
    try:
        genai.configure(api_key=api_key)
        
        # Koristimo modele koji su stvarno dostupni za generateContent
        # Prema list_models() rezultatima, ovi modeli su dostupni
        model_names = [
            'gemini-2.5-flash',          # Najnoviji flash model
            'gemini-2.0-flash',          # Stabilan 2.0 flash
            'gemini-flash-latest',       # Latest verzija
            'gemini-2.0-flash-exp',      # Eksperimentalni
            'gemini-2.5-pro',            # Pro verzija
            'gemini-pro-latest'          # Latest pro verzija
        ]
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                return model
            except Exception:
                continue
        
        return None
    except Exception as e:
        return None

def get_gemini_analysis(api_key, bank_name, bank_row, market_avg_row):
    """Šalje podatke jedne banke AI-ju na analizu."""
    try:
        genai.configure(api_key=api_key)
        # Pronalazimo dostupan model
        model = _get_available_model(api_key)
        
        if model is None:
            return "Greška: Nije moguće pronaći dostupan Gemini model. Proveri API ključ i dostupnost modela."
        
        # Pretvaramo seriju (red) u tekst
        bank_stats = bank_row.to_string()
        market_stats = market_avg_row.to_string()
        
        prompt = f"""
        Analiziraj banku: {bank_name}.
        
        PODACI BANKE:
        {bank_stats}
        
        PROSJEK TRŽIŠTA (Benchmark):
        {market_stats}
        
        Zadatak:
        1. Identifikuj 2 ključna problema gdje banka najviše odstupa od prosjeka (lošiji CIR, manji prihodi...).
        2. Daj 2 konkretne preporuke (npr. "Smanjiti admin troškove", "Povećati naknade").
        3. Budi kratak i profesionalan.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Greška sa AI servisom: {str(e)}"