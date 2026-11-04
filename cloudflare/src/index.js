// Liefert die GitHub-Pages-Seite unter der eigenen Subdomain aus.
// Die Seite selbst bleibt im Repo (site/); hier wird nur durchgereicht, damit jede Änderung
// an der Website ohne neues Deployment auch unter dieser Adresse erscheint.
const ORIGIN = "https://lb2002.github.io/openstitch";

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method not allowed", { status: 405, headers: { Allow: "GET, HEAD" } });
    }
    const upstream = await fetch(ORIGIN + url.pathname + url.search, {
      method: request.method,
      headers: { "Accept": request.headers.get("Accept") || "*/*" },
      cf: { cacheTtl: 300, cacheEverything: true },
    });
    const headers = new Headers(upstream.headers);
    // Weiterleitungen von GitHub zeigen auf github.io: auf die eigene Adresse umschreiben
    const location = headers.get("Location");
    if (location && location.startsWith(ORIGIN)) {
      headers.set("Location", location.slice(ORIGIN.length) || "/");
    }
    return new Response(upstream.body, { status: upstream.status, headers });
  },
};
