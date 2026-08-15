def calculate(parameter):
    import re
    # Mapping Spanish words to numbers and operators
    mapping = {
        'cero': '0', 'uno': '1', 'una': '1', 'dos': '2', 'tres': '3',
        'cuatro': '4', 'cinco': '5', 'seis': '6', 'siete': '7',
        'ocho': '8', 'nueve': '9', 'diez': '10',
        'mas': '+', 'más': '+', 'menos': '-', 'por': '*',
        'entre': '/', 'dividido': '/', 'dividida': '/'
    }
    expr = parameter.lower()
    # Replace words with their corresponding symbols
    for word, sym in mapping.items():
        expr = re.sub(r'\b' + word + r'\b', sym, expr)
    # Keep only numbers, operators, parentheses, and spaces
    expr = re.sub(r'[^0-9\+\-\*/\.\(\) ]', '', expr)
    try:
        return eval(expr)
    except Exception:
        return None