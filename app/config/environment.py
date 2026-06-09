from enum import Enum


class AppEnv(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"
