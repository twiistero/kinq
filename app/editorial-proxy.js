const api = process.env.KINQ_API_URL || 'http://127.0.0.1:8000';

export async function editorialProxy(request) {
  const url = new URL(request.url);
  const headers = new Headers(request.headers);
  headers.delete('host');
  headers.delete('connection');
  headers.delete('content-length');
  try {
    const upstream = await fetch(`${api}${url.pathname}${url.search}`, {
      method: request.method,
      headers,
      body: ['GET', 'HEAD'].includes(request.method) ? undefined : request.body,
      duplex: 'half',
      redirect: 'manual',
      cache: 'no-store',
    });
    const responseHeaders = new Headers(upstream.headers);
    responseHeaders.delete('transfer-encoding');
    responseHeaders.delete('content-length');
    return new Response(upstream.body, {status: upstream.status, headers: responseHeaders});
  } catch {
    return new Response('API indisponible', {status: 502});
  }
}
