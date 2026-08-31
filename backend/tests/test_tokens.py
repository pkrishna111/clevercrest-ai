import unittest

from app.core.tokens import generate_token, hash_token


class TokenUtilitiesTests(unittest.TestCase):
    def test_generate_token_is_non_empty_and_unique(self) -> None:
        token_one = generate_token()
        token_two = generate_token()

        self.assertIsInstance(token_one, str)
        self.assertIsInstance(token_two, str)
        self.assertTrue(token_one)
        self.assertTrue(token_two)
        self.assertNotEqual(token_one, token_two)

    def test_hash_token_is_deterministic(self) -> None:
        token = generate_token()

        first_hash = hash_token(token)
        second_hash = hash_token(token)

        self.assertEqual(first_hash, second_hash)

    def test_hash_token_is_sha256_hex(self) -> None:
        token = "test-token"

        token_hash = hash_token(token)

        self.assertEqual(len(token_hash), 64)
        self.assertTrue(
            all(character in "0123456789abcdef" for character in token_hash)
        )


if __name__ == "__main__":
    unittest.main()