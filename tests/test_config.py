import unittest

from config import Settings


class SettingsTests(unittest.TestCase):
    def test_database_url_escapes_credentials(self) -> None:
        settings = Settings(
            bot_token="test-token",
            tg_url="https://t.me/example",
            github_url="https://github.com/example/repository",
            db_host="db",
            db_port=5432,
            db_user="pizza@user",
            db_password="p@ss:word",
            db_name="pizza_db",
            _env_file=None,
        )

        self.assertIn("pizza%40user", settings.database_url)
        self.assertIn("p%40ss%3Aword", settings.database_url)


if __name__ == "__main__":
    unittest.main()
