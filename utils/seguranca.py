from functools import wraps

from flask import flash, g, redirect, request, session, url_for


def login_obrigatorio(funcao):
    @wraps(funcao)
    def protegida(*args, **kwargs):
        if g.get("usuario") is None:
            flash("Faça login para acessar esta página.", "warning")
            return redirect(url_for("auth.login", proximo=request.path))
        return funcao(*args, **kwargs)

    return protegida


def perfis_permitidos(*perfis):
    def decorador(funcao):
        @wraps(funcao)
        def protegida(*args, **kwargs):
            if g.get("usuario") is None:
                return redirect(url_for("auth.login", proximo=request.path))
            if g.usuario.perfil not in perfis:
                flash("Seu perfil não tem permissão para esta operação.", "danger")
                return redirect(url_for("principal.painel"))
            return funcao(*args, **kwargs)

        return protegida

    return decorador
