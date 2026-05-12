package recommendations

import (
	"encoding/json"
	"testing"
)

func TestFiltersHTTPBodyUnmarshalJSON_CamelCaseAndStringAge(t *testing.T) {
	const payload = `{"ageTo":"100","partnerGender":"MALE"}`
	var b filtersHTTPBody
	if err := json.Unmarshal([]byte(payload), &b); err != nil {
		t.Fatal(err)
	}
	if b.AgeTo == nil || *b.AgeTo != 100 {
		t.Fatalf("ageTo: got %v want 100", b.AgeTo)
	}
	if b.PartnerGender == nil || *b.PartnerGender != "MALE" {
		t.Fatalf("partnerGender: got %v want MALE", b.PartnerGender)
	}
}

func TestFiltersHTTPBodyUnmarshalJSON_SnakeCase(t *testing.T) {
	const payload = `{"age_to":40,"partner_gender":"FEMALE","relationship_type":"FRIENDSHIP"}`
	var b filtersHTTPBody
	if err := json.Unmarshal([]byte(payload), &b); err != nil {
		t.Fatal(err)
	}
	if b.AgeTo == nil || *b.AgeTo != 40 {
		t.Fatalf("age_to: got %v", b.AgeTo)
	}
	if b.PartnerGender == nil || *b.PartnerGender != "FEMALE" {
		t.Fatalf("partner_gender: got %v", b.PartnerGender)
	}
	if b.RelationshipType == nil || *b.RelationshipType != "FRIENDSHIP" {
		t.Fatalf("relationship_type: got %v", b.RelationshipType)
	}
}
