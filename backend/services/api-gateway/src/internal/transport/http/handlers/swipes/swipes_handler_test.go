package swipes

import (
	"encoding/json"
	"testing"
)

func TestSwipeBodyUnmarshalJSON_stringLikedAndStringTarget(t *testing.T) {
	const payload = `{"target_user_id":"1","liked":"true"}`
	var b swipeBody
	if err := json.Unmarshal([]byte(payload), &b); err != nil {
		t.Fatal(err)
	}
	if b.TargetUserID != 1 || !b.Liked {
		t.Fatalf("got %+v", b)
	}
}

func TestSwipeBodyUnmarshalJSON_numeric(t *testing.T) {
	const payload = `{"target_user_id":99,"liked":false}`
	var b swipeBody
	if err := json.Unmarshal([]byte(payload), &b); err != nil {
		t.Fatal(err)
	}
	if b.TargetUserID != 99 || b.Liked {
		t.Fatalf("got %+v", b)
	}
}
