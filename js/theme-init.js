(function () {
    const saved = localStorage.getItem('theme');
    const systemLikesLight = window.matchMedia('(prefers-color-scheme: light)').matches;
    if (saved === 'light' || (!saved && systemLikesLight)) {
        document.documentElement.setAttribute('data-theme', 'light');
    } else {
        document.documentElement.removeAttribute('data-theme');
    }
})();
