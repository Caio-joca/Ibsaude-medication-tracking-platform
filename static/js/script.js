document.querySelectorAll("form[data-confirm]").forEach((formulario) => {
    formulario.addEventListener("submit", (evento) => {
        if (!window.confirm(formulario.dataset.confirm)) {
            evento.preventDefault();
        }
    });
});
