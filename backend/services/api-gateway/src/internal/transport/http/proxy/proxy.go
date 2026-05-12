package proxy

import (
	"context"
	"net/http"
	"net/http/httputil"
	"net/url"
	"strconv"

	"github.com/artryry/commit/services/api-gateway/src/internal/common"
)

// contextUserIDHeader formats JWT user id from context for X-User-Id (chats, notifications).
func contextUserIDHeader(ctx context.Context) string {
	v := ctx.Value(common.UserIDKey)
	if v == nil {
		return ""
	}
	switch x := v.(type) {
	case int:
		return strconv.Itoa(x)
	case int64:
		return strconv.FormatInt(x, 10)
	case float64:
		return strconv.FormatInt(int64(x), 10)
	case string:
		return x
	default:
		return ""
	}
}

// corsHeaderNames are stripped from proxied responses so the API gateway remains the single source of CORS headers.
var corsHeaderNames = []string{
	"Access-Control-Allow-Origin",
	"Access-Control-Allow-Credentials",
	"Access-Control-Allow-Methods",
	"Access-Control-Allow-Headers",
	"Access-Control-Expose-Headers",
	"Access-Control-Max-Age",
}

func stripBackendCORS(resp *http.Response) error {
	for _, name := range corsHeaderNames {
		resp.Header.Del(name)
	}
	return nil
}

func New(target string) http.Handler {
	targetURL, _ := url.Parse(target)

	proxy := &httputil.ReverseProxy{}

	proxy.Rewrite = func(r *httputil.ProxyRequest) {
		r.SetURL(targetURL)
		r.Out.URL.Path = r.In.URL.Path

		r.Out.URL.RawQuery = r.In.URL.RawQuery
		r.Out.Host = targetURL.Host
	}

	proxy.ModifyResponse = stripBackendCORS

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

		if uid := contextUserIDHeader(r.In.Context()); uid != "" {
			r.Out.Header.Set("X-User-Id", uid)
		}
	}

	p.ModifyResponse = stripBackendCORS

	p.ErrorHandler = func(w http.ResponseWriter, r *http.Request, err error) {
		http.Error(w, "Bad Gateway", http.StatusBadGateway)
	}

	return p
}
