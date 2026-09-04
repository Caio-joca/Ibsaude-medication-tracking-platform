from email_validator import EmailNotValidError, validate_email


def somente_digitos(valor):
    return "".join(filter(str.isdigit, valor or ""))


def cpf_valido(cpf):
    cpf = somente_digitos(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10) % 11
        if digito == 10:
            digito = 0
        if digito != int(cpf[tamanho]):
            return False
    return True


def cnpj_valido(cnpj):
    cnpj = somente_digitos(cnpj)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    def calcular(parcial, pesos):
        resto = sum(int(n) * p for n, p in zip(parcial, pesos)) % 11
        return "0" if resto < 2 else str(11 - resto)

    primeiro = calcular(cnpj[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    segundo = calcular(cnpj[:12] + primeiro, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return cnpj[-2:] == primeiro + segundo


def email_valido(email):
    try:
        return validate_email(email or "", check_deliverability=False).normalized.lower()
    except EmailNotValidError:
        return None
