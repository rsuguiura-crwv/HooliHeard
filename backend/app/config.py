from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://hooli:hooli@localhost:5432/hooliheard"

    # Claude API
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"

    # Gong
    GONG_ACCESS_KEY: str = ""
    GONG_ACCESS_KEY_SECRET: str = ""

    # Salesforce
    SALESFORCE_USERNAME: str = ""
    SALESFORCE_PASSWORD: str = ""
    SALESFORCE_SECURITY_TOKEN: str = ""
    SALESFORCE_DOMAIN: str = "login"

    # Jira
    JIRA_BASE_URL: str = "https://coreweave.atlassian.net"
    JIRA_EMAIL: str = ""
    JIRA_API_TOKEN: str = ""

    # Slack
    SLACK_BOT_TOKEN: str = ""
    SLACK_CHANNELS: str = ""

    # Qualtrics
    QUALTRICS_API_TOKEN: str = ""
    QUALTRICS_DATACENTER: str = ""
    QUALTRICS_SURVEY_ID: str = ""

    # Limits
    MAX_SIGNALS_PER_SOURCE: int = 50

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
