# envguard

> CLI tool to validate and diff .env files across environments

---

## Installation

```bash
pip install envguard
```

Or with pipx:

```bash
pipx install envguard
```

---

## Usage

Validate that all keys in a base `.env` file are present in another environment file:

```bash
envguard validate --base .env.example --check .env.production
```

Diff two environment files to see missing or extra keys:

```bash
envguard diff .env.staging .env.production
```

Example output:

```
[✔] Keys in common: 12
[✘] Missing in .env.production: DB_HOST, REDIS_URL
[!] Extra in .env.production: NEW_RELIC_KEY
```

### Available Commands

| Command | Description |
|---|---|
| `validate` | Check that all required keys exist in target env file |
| `diff` | Show key differences between two env files |
| `list` | List all keys in an env file |

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

---

## License

[MIT](LICENSE)