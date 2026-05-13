package s3

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"

	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"

	"github.com/artryry/commit/backend/services/profiles/src/internal/config"
)

type Storage struct {
	client *minio.Client
	bucket string
}

func NewImageStorage(cfg *config.Config) (*Storage, error) {
	client, err := minio.New(
		cfg.Storage.Endpoint,
		&minio.Options{
			Creds: credentials.NewStaticV4(
				cfg.Storage.AccessKey,
				cfg.Storage.SecretKey,
				"",
			),
			Secure: cfg.Storage.UseSSL,
		},
	)
	if err != nil {
		return nil, err
	}

	exists, err := client.BucketExists(
		context.Background(),
		cfg.Storage.Bucket,
	)
	if err != nil {
		return nil, err
	}

	if !exists {
		err = client.MakeBucket(
			context.Background(),
			cfg.Storage.Bucket,
			minio.MakeBucketOptions{},
		)
		if err != nil {
			return nil, err
		}
	}

	if cfg.Storage.AnonymousRead {
		if err := setAnonymousGetObjectPolicy(context.Background(), client, cfg.Storage.Bucket); err != nil {
			return nil, err
		}
	}

	return &Storage{
		client: client,
		bucket: cfg.Storage.Bucket,
	}, nil
}

// setAnonymousGetObjectPolicy allows browser GETs on https://minio-host/bucket/object paths without signing.
func setAnonymousGetObjectPolicy(ctx context.Context, client *minio.Client, bucket string) error {
	policy := struct {
		Version   string `json:"Version"`
		Statement []any  `json:"Statement"`
	}{
		Version: "2012-10-17",
		Statement: []any{
			map[string]any{
				"Effect": "Allow",
				"Principal": map[string]any{
					"AWS": []string{"*"},
				},
				"Action":   []string{"s3:GetObject"},
				"Resource": []string{fmt.Sprintf("arn:aws:s3:::%s/*", bucket)},
			},
		},
	}
	raw, err := json.Marshal(policy)
	if err != nil {
		return err
	}
	return client.SetBucketPolicy(ctx, bucket, string(raw))
}

func (s *Storage) Upload(
	ctx context.Context,
	storageKey string,
	data []byte,
) error {

	_, err := s.client.PutObject(
		ctx,
		s.bucket,
		storageKey,
		bytes.NewReader(data),
		int64(len(data)),
		minio.PutObjectOptions{},
	)

	return err
}

func (s *Storage) Delete(
	ctx context.Context,
	storageKey string,
) error {

	err := s.client.RemoveObject(
		ctx,
		s.bucket,
		storageKey,
		minio.RemoveObjectOptions{},
	)
	if err != nil {
		resp := minio.ToErrorResponse(err)
		if resp.Code == "NoSuchKey" {
			return nil
		}
		return err
	}
	return nil
}
