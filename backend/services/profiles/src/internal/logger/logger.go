package logger

import (
	"log/slog"
	"os"
)

var Log *slog.Logger

func Init(env string) {

	var level slog.Level

	switch env {
	case "Debug":
		level = slog.LevelDebug

	default:
		level = slog.LevelInfo
	}

	opts := &slog.HandlerOptions{
		Level: level,
	}

	handler := slog.NewJSONHandler(
		os.Stdout,
		opts,
	)

	Log = slog.New(handler)
}

func Info(msg string, args ...any) {
	Log.Info(msg, args...)
}

func Debug(msg string, args ...any) {
	Log.Debug(msg, args...)
}

func Warn(msg string, args ...any) {
	Log.Warn(msg, args...)
}

func Error(msg string, args ...any) {
	Log.Error(msg, args...)
}
