import type { Handle } from '@sveltejs/kit';

import { env } from '$env/dynamic/public';
import { env as privateEnv } from '$env/dynamic/private';

const PUBLIC_FRONTEND_URL = env.PUBLIC_FRONTEND_URL;
const PUBLIC_CMS_URL = env.PUBLIC_CMS_URL;
const PRIVATE_OLLAMA_API = privateEnv.PRIVATE_OLLAMA_API;

interface RequestHeaders {
  [key: string]: string;
}

interface ProxyConfig {
  [key: string]: {
    target: string;
    token?: string;
    headers?: Record<string, string>;
  };
}

export function proxyHandle(
  proxyPaths: { [key: string]: Array<string> },
  options = { changeOrigin: true, debug: false }): Handle {
  
  // Logging .env variables for production mode
  console.log(`PUBLIC_FRONTEND_URL: ${PUBLIC_FRONTEND_URL}, 
               PUBLIC_CMS_URL: ${PUBLIC_CMS_URL}`);

  // Convert the simple array format to the more detailed config format
  const proxy: ProxyConfig = {};
  for (const path in proxyPaths) {
    proxy[path] = {
      target: proxyPaths[path][0],
      token: proxyPaths[path][1]
    };
    
    // Special handling for Ollama API
    if (path === '/ollama_proxy' && PRIVATE_OLLAMA_API) {
      proxy[path].headers = {
        'X-Api-Key': PRIVATE_OLLAMA_API
      };
    }
  }
  
  return async function ({ event, resolve }) {
    const { url, request } = event;

    for (const proxyParam in proxy) {
      const proxy_url = url.pathname.split(proxyParam)[1];
      if (proxy_url) {
        const proxyTarget = proxy[proxyParam].target;

        const requestHeaders: RequestHeaders = {
          "Accept": request.headers.get("accept") ?? "",
          "user-agent": request.headers.get("user-agent") ?? "",
          "accept-encoding": request.headers.get("accept-encoding") ?? "",
          "accept-language": request.headers.get("accept-language") ?? "",
          "Content-Type": request.headers.get("Content-Type") ?? "",
        };
        
        // Add Authorization header if token is provided
        if (proxy[proxyParam].token) {
          requestHeaders["Authorization"] = `Bearer ${proxy[proxyParam].token}`;
        } else if (event.cookies.get('access_token')) {
          requestHeaders["Authorization"] = `Bearer ${event.cookies.get('access_token')}`;
        }
        
        // Add any additional custom headers from the proxy config
        if (proxy[proxyParam].headers) {
          Object.entries(proxy[proxyParam].headers).forEach(([key, value]) => {
            requestHeaders[key] = value;
          });
        }

        if (options && !options.changeOrigin) {
          requestHeaders.host = request.headers.get("host") ?? "";
        }

        if (options && options.debug) {
          console.debug(`Headers: ${JSON.stringify(requestHeaders)}`);
          console.debug(`Proxy: ${proxyTarget}${proxy_url}${url.search}`);
          console.debug(`Request: ${JSON.stringify(request.method)}`);
        }

        if (options && options.debug) {
          const body = await request.clone().text();
          console.debug(`Request Body: ${body}`);
        }

        // TODO: consider sending the information in a header, so it does not need to be awaited
        // Handling the request body:
        let body;
        const contentType = request.headers.get('Content-Type'); 
        if (request.body) {
          if (contentType && contentType.startsWith('application/json')) {
            body = await request.json(); // Handle JSON data
          } else if (contentType && contentType.startsWith('text/')) {
            body = await request.text();  // Handle plain text
          } else {
            body = await request.arrayBuffer(); // Handle binary data (like PDFs, images, etc.)
          }
        }

        // Fetch data from the remote server
        const resp = await fetch(`${proxyTarget}${proxy_url}${url.search}`, {
          method: request.method,
          headers: requestHeaders,
          body: contentType?.startsWith('application/json') ? JSON.stringify(body) : body,
        });

        // Clean up response headers
        const responseHeaders = Object.fromEntries(resp.headers.entries());
        delete responseHeaders["content-encoding"]; // Remove content-encoding to avoid decompression issues

        if (options && options.debug) {
          console.debug(
            `Proxy response (${resp.status}) headers:`,
            responseHeaders
          );
        }

        // Determine the correct response type based on Content-Type
        const responseContentType = responseHeaders['content-type'] || ''; // Ensure responseContentType is available
        let bodyContent;

        // Ensure responseContentType is valid before checking with startsWith
        if (responseContentType && (responseContentType.startsWith('application/pdf') || responseContentType.startsWith('image/') || responseContentType.startsWith('application/octet-stream'))) {
          bodyContent = await resp.arrayBuffer(); // Handle binary data (PDFs, images, other files)
        } else {
          bodyContent = await resp.text(); // Handle text-based content
        }

        // Return response from the remote server
        return new Response(bodyContent, {
          status: resp.status,
          headers: responseHeaders,
        });
      }
    }
    return resolve(event);
  };
}

export default proxyHandle;
