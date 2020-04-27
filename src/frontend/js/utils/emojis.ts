import * as emojione from 'emojione';

export const renderEmojis = () => {
  // @ts-ignore
  emojione.imagePathPNG = '//cdn.jsdelivr.net/emojione/assets/svg/';
  // @ts-ignore
  emojione.fileExtension = '.svg';
  document.querySelectorAll('span.emoji').forEach((emojiElement) => {
    if (emojiElement.textContent) {
      emojiElement.innerHTML = emojione.toImage(emojiElement.textContent);
    }
  });
};
