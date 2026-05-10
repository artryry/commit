package proxy

import (
	"net/http"
	"net/http/httputil"
	"net/url"
	"strconv"

	"github.com/artryry/commit/services/api-gateway/src/internal/common"
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

// NewForwardingUserID proxies like New but sets X-User-Id from JWT middleware context (trusted caller identity).
func NewForwardingUserID(target string) http.Handler {
	targetURL, _ := url.Parse(target)

	p := &httputil.ReverseProxy{}

	p.Rewrite = func(r *httputil.ProxyRequest) {
		r.SetURL(targetURL)
		r.Out.URL.Path = r.In.URL.Path
		r.Out.URL.RawQuery = r.In.URL.RawQuery
		r.Out.Host = targetURL.Host

		if v := r.In.Context().Value(common.UserIDKey); v != nil {
			if uid, ok := v.(int); ok {
				r.Out.Header.Set("X-User-Id", strconv.Itoa(uid))
			}
		}
	}

	p.ErrorHandler = func(w http.ResponseWriter, r *http.Request, err error) {
		http.Error(w, "Bad Gateway", http.StatusBadGateway)
	}

	return p
}
