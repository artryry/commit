ALTER TABLE profiles
ADD CONSTRAINT fk_profiles_avatar
FOREIGN KEY (avatar_image_id)
REFERENCES images(id)
ON DELETE SET NULL;