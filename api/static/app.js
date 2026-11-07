document.querySelectorAll("[data-copy]").forEach((button) => {
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(button.dataset.copy);
      const original = button.textContent;
      button.textContent = "Copiado!";
      window.setTimeout(() => { button.textContent = original; }, 1600);
    } catch {
      window.prompt("Copie a URL abaixo:", button.dataset.copy);
    }
  });
});
