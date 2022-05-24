import warnings


warnings.filterwarnings(
	"ignore",
	"aliases are no longer used by BaseSettings to define which environment variables to read",
	FutureWarning,
)
