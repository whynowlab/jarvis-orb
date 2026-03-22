/**
 * LogPanel — click-to-toggle log display.
 */
export class LogPanel {
  constructor(element) {
    this.el = element;
    this.maxLines = 5;
    this.visible = false;
  }

  toggle() {
    this.visible = !this.visible;
    this.el.classList.toggle('visible', this.visible);
  }

  show() {
    this.visible = true;
    this.el.classList.add('visible');
  }

  hide() {
    this.visible = false;
    this.el.classList.remove('visible');
  }

  addLine(tag, text) {
    const line = document.createElement('div');
    line.className = 'log-line';
    line.innerHTML = `<span class="log-tag">[${tag}]</span> ${this._escapeHtml(text)}`;

    this.el.appendChild(line);

    // Remove old lines
    while (this.el.children.length > this.maxLines) {
      this.el.removeChild(this.el.firstChild);
    }

    // Animate entry
    line.style.opacity = '0';
    line.style.transform = 'translateY(8px)';
    requestAnimationFrame(() => {
      line.style.transition = 'all 0.3s ease-out';
      line.style.opacity = '1';
      line.style.transform = 'translateY(0)';
    });
  }

  _escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}
