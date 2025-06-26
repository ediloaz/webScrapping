def obtener_precio(string_precio):
    return float(string_precio.replace('₡', '').replace(',', ''))