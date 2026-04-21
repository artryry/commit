package proxy

import (
	"net/http"
	"net/http/httputil"
	"net/url"
)

func New(target string) http.Handler {
	targetURL, _ := url.Parse(target)

	proxy := &httputil.ReverseProxy{}

	proxy.Rewrite = func(r *httputil.ProxyRequest) {
		r.SetURL(targetURL)
		r.Out.URL.Path = r.In.URL.Path

		r.Out.URL.RawQuery = r.In.URL.RawQuery
		r.Out.Host = targetURL.Host
	}

	proxy.ErrorHandler = func(w http.ResponseWriter, r *http.Request, err error) {
		http.Error(w, "Bad Gateway", http.StatusBadGateway)
	}

	return proxy
}
