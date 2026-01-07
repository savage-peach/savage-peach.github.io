class SPGoogleAnalytics extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        // ID provided by the user
        const measurementId = 'G-2H24VV9DR6';

        // Avoid adding multiple times
        if (document.getElementById('ga-script')) return;

        // <!-- Google tag (gtag.js) -->
        const script1 = document.createElement('script');
        script1.id = 'ga-script';
        script1.async = true;
        script1.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
        document.head.appendChild(script1);

        const script2 = document.createElement('script');
        script2.innerHTML = `
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${measurementId}');
        `;
        document.head.appendChild(script2);
    }
}

customElements.define('sp-google-analytics', SPGoogleAnalytics);
