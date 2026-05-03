DELETE FROM profiles_tags pt
USING tags t
WHERE pt.tag_id = t.id
  AND pt.user_id = $1
  AND t.name = ANY($2);
