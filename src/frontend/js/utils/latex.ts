import katex from 'katex';

export const renderLatex = () => {
  document.querySelectorAll('[class^=ashley-latex]').forEach((math) => {
    if (math.textContent) {
      math.innerHTML = katex.renderToString(math.textContent, {
        displayMode: math.classList.contains('ashley-latex-display'),
      });
    }
  });
};
